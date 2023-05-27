from http.client import BAD_REQUEST, NOT_FOUND, UNPROCESSABLE_ENTITY

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject

PROJECT_EXISTS = 'Проект с таким именем уже существует!'
PROJECT_NOT_FOUND = 'Проект не найден!'
PROJECT_NOT_DELETE = 'В проект были внесены средства, не подлежит удалению!'
CLOSED_PROJECT_NOT_EDITED = 'Закрытый проект нельзя редактировать!'
REQUIRED_AMOUNT_NOT_LESS_THAN_INVESTED = (
    'Требуемая сумма не должна быть меньше уже вложенной!'
)
ERROR_EXCEED_MAXIMUM_COLUMNS = (
    'Данные превышают максимальное количество столбцов в электронной таблице!'
)
ERROR_EXCEED_MAXIMUM_ROWS = (
    'Данные превышают максимальное количество строк в электронной таблице!'
)


async def check_charity_project_name_duplicate(
        project_name: str,
        session: AsyncSession,
) -> None:
    """
    Проверяет, существует ли уже благотворительный проект с заданным именем.

    Аргументы:
        - project_name (str): название проекта.
        - session (AsyncSession): SQLAlchemy сессия для взаимодействия с базой
          данных.

    Вызывает:
        HTTPException: если проект с заданным именем уже существует.
    """
    project_id = (
        await charity_project_crud.get_charity_project_id_by_name(
            charity_project_name=project_name,
            session=session
        )
    )
    if project_id is not None:
        raise HTTPException(
            status_code=BAD_REQUEST,
            detail=PROJECT_EXISTS,
        )


async def check_charity_project_exist(
        project_id: int,
        session: AsyncSession,
) -> CharityProject:
    """
    Проверяет, существует ли благотворительный проект с заданным id.

    Аргументы:
        - project_id (int): ID проекта.
        - session (AsyncSession): SQLAlchemy сессия для взаимодействия с базой
          данных.

    Возвращает:
        CharityProject: проект с заданным идентификатором.

    Вызывает:
        HTTPException: если проект с заданным id не существует.
    """
    charity_project = await charity_project_crud.get_charity_project_obj_by_id(
        charity_project_id=project_id,
        session=session
    )
    if charity_project is None:
        raise HTTPException(
            status_code=NOT_FOUND,
            detail=PROJECT_NOT_FOUND,
        )
    return charity_project


def ensure_project_has_no_investment(
        charity_project_obj: CharityProject
) -> None:
    """
    Проверяет, есть ли у данного благотворительного проекта инвестиции.

    Аргументы:
        - charity_project_obj (CharityProject): благотворительный проект,
          который нужно проверить.

    Вызывает:
        HTTPException: если у проекта есть какие-либо инвестиции.
    """
    project_invested_amount = charity_project_obj.invested_amount
    if project_invested_amount != 0:
        raise HTTPException(
            status_code=BAD_REQUEST,
            detail=PROJECT_NOT_DELETE
        )


def ensure_project_is_not_closed(
        charity_project_obj: CharityProject,
) -> None:
    """
    Проверяет, закрыт ли данный благотворительный проект.

    Аргументы:
        - charity_project_obj (CharityProject): благотворительный проект,
          который нужно проверить.

    Вызывает:
        HTTPException: если проект закрыт.
    """
    if charity_project_obj.close_date is not None:
        raise HTTPException(
            status_code=BAD_REQUEST,
            detail=CLOSED_PROJECT_NOT_EDITED
        )


def ensure_full_amount_greater_than_invested(
        invested_amount: int,
        new_full_amount: int,
) -> None:
    """
    Проверяет, больше ли новая требуемая сумма, чем уже вложенная.

    Аргументы:
        - invested_amount (int): сумма, которая была инвестирована.
        - new_full_amount (int): новая требуемая сумма.

    Вызывает:
        HTTPException: если новая полная сумма не больше инвестированной суммы.
    """
    if new_full_amount < invested_amount:
        raise HTTPException(
            status_code=UNPROCESSABLE_ENTITY,
            detail=REQUIRED_AMOUNT_NOT_LESS_THAN_INVESTED
        )
