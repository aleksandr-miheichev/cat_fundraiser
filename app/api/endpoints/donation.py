from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import DonationCreate, DonationDB, DonationAdminDB
from app.services.investment import run_investment_process

MAKE_DONATION = 'Сделать пожертвование.'
LIST_OF_DONATIONS_FOR_SUPERVISORS = (
    'Только для суперюзеров.<br/><br/>Получает список всех пожертвований.'
)
LIST_MY_DONATIONS = 'Получить список моих пожертвований.'

router = APIRouter()


@router.get(
    '/',
    response_model=list[DonationAdminDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
    description=LIST_OF_DONATIONS_FOR_SUPERVISORS,
)
async def get_all_donations(
        session: AsyncSession = Depends(get_async_session),
):
    """
    Получить все пожертвования. Эта конечная точка предназначена только для
    суперпользователей.

    Атрибуты:
        - session (AsyncSession): сессия SQLAlchemy, которую нужно использовать
          для операций с базой данных.

    Возвращает:
        list[DonationAdminDB]: список всех пожертвований.
    """
    all_donations = await donation_crud.get_multi(
        session=session
    )
    return all_donations


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True,
    description=MAKE_DONATION,
)
async def create_donation(
        donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    """
    Создать новое пожертвование и обработать его.

    Атрибуты:
        - donation (DonationCreate): информация о пожертвовании, которое нужно
          создать.
        - session (AsyncSession): сессия SQLAlchemy, которую нужно использовать
          для операций с базой данных.
        - user (User): пользователь, делающий пожертвование.

    Возвращает:
        DonationDB: созданное пожертвование после обработки.
    """
    donation = await donation_crud.create(
        session=session,
        obj_in=donation,
        user=user,
        commit=False,
    )
    session.add_all(
        run_investment_process(
            target=donation,
            sources=await charity_project_crud.get_uninvested(session=session)
        )
    )
    await session.commit()
    await session.refresh(donation)
    return donation


@router.get(
    '/my',
    response_model_exclude_none=True,
    response_model=list[DonationDB],
    description=LIST_MY_DONATIONS,
)
async def get_user_donations(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """
    Получить все пожертвования, сделанные текущим пользователем.

    Атрибуты:
        - user (Пользователь): пользователь, чьи пожертвования нужно получить.
        - session (AsyncSession): сессия SQLAlchemy, которую нужно использовать
          для операций с базой данных.

    Возвращает:
        list[DonationDB]: список пожертвований пользователя.
    """
    user_donations = await donation_crud.get_by_user(
        user=user,
        session=session
    )
    return user_donations
