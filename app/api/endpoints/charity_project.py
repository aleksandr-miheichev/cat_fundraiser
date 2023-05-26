from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_charity_project_exist,
    check_charity_project_name_duplicate,
    ensure_full_amount_greater_than_invested,
    ensure_project_has_no_investment,
    ensure_project_is_not_closed,
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate
)
from app.services.investment import run_investment_process

LIST_ALL_PROJECTS = 'Получает список всех проектов.'
CREATE_PROJECT_FOR_SUPERUSERS = (
    'Только для суперюзеров.<br/><br/>Создает благотворительный проект.'
)
DELETE_PROJECT_FOR_SUPERUSERS = (
    'Только для суперюзеров.<br/><br/>Удаляет проект. Нельзя удалить проект, '
    'в который уже были инвестированы средства, его можно только закрыть.'
)
UPDATE_PROJECT_FOR_SUPERUSERS = (
    'Только для суперюзеров.<br/><br/>Закрытый проект нельзя редактировать, '
    'также нельзя установить требуемую сумму меньше уже вложенной.'
)

router = APIRouter()


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
    description=LIST_ALL_PROJECTS,
)
async def get_all_charity_projects(
        session: AsyncSession = Depends(get_async_session),
):
    """
    Извлекает из базы данных список всех благотворительных проектов.

    Аргументы:
        - session (AsyncSession): сессия SQLAlchemy.

    Возвращает:
        list[CharityProjectDB]: список всех благотворительных проектов.
    """
    all_charity_projects = await charity_project_crud.get_multi(
        session=session
    )
    return all_charity_projects


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
    description=CREATE_PROJECT_FOR_SUPERUSERS
)
async def create_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session)
):
    """
    Создает новый благотворительный проект. Эта функция доступна только
    суперпользователям.

    Аргументы:
        - charity_project (CharityProjectCreate): объект, содержащий данные
          для создаваемого благотворительного проекта.
        - session (AsyncSession): сессия SQLAlchemy.

    Возвращает:
        CharityProjectDB: созданный благотворительный проект.
    """
    await check_charity_project_name_duplicate(
        project_name=charity_project.name,
        session=session
    )
    new_charity_project = await charity_project_crud.create(
        obj_in=charity_project,
        session=session,
        commit=False,
    )
    session.add_all(
        run_investment_process(
            target=new_charity_project,
            sources=await donation_crud.get_uninvested(session=session)
        )
    )
    await session.commit()
    await session.refresh(new_charity_project)
    return new_charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
    description=DELETE_PROJECT_FOR_SUPERUSERS
)
async def delete_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Удаляет благотворительный проект по его id. Эта функция доступна только
    суперпользователям.

    Аргументы:
        - project_id (int): id удаляемого благотворительного проекта.
        - session (AsyncSession, необязательно): сессия SQLAlchemy.

    Возвращает:
        CharityProjectDB: удалённый благотворительный проект.
    """
    charity_project = await check_charity_project_exist(
        project_id=project_id,
        session=session
    )
    ensure_project_has_no_investment(charity_project_obj=charity_project)
    ensure_project_is_not_closed(charity_project_obj=charity_project)
    charity_project = await charity_project_crud.delete(
        db_obj=charity_project,
        session=session
    )
    return charity_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
    description=UPDATE_PROJECT_FOR_SUPERUSERS
)
async def update_charity_project(
        project_id: int,
        project_update: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Обновляет благотворительный проект по его id. Эта функция доступна только
    суперпользователям.

    Аргументы:
        - project_id (int): id благотворительного проекта, который нужно
          обновить.
        - project_update (CharityProjectUpdate): Объект, содержащий новые
          данные для благотворительного проекта.
        - session (AsyncSession): сессия SQLAlchemy.

    Возвращает:
        CharityProjectDB: обновленный благотворительный проект.
    """
    charity_project = await check_charity_project_exist(
        project_id=project_id,
        session=session
    )
    ensure_project_is_not_closed(charity_project_obj=charity_project)
    if project_update.name is not None:
        await check_charity_project_name_duplicate(
            project_name=project_update.name,
            session=session
        )
    if project_update.full_amount is not None:
        ensure_full_amount_greater_than_invested(
            invested_amount=charity_project.invested_amount,
            new_full_amount=project_update.full_amount
        )
    charity_project = await charity_project_crud.update(
        db_obj=charity_project,
        obj_in=project_update,
        session=session,
    )
    return charity_project
