from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Donation, User


class CRUDDonation(CRUDBase):
    """Класс для обработки CRUD-операций, связанных с моделью Donation."""

    async def get_by_user(
            self,
            user: User,
            session: AsyncSession,
    ):
        """
        Возвращает все пожертвования, сделанные конкретным пользователем.

        Атрибуты:
            - user (User): пользователь, чьи пожертвования должны быть
              получены.
            - session (AsyncSession): сессия SQLAlchemy.

        Возвращает:
            Список объектов пожертвований, связанных с указанным пользователем.
        """
        donations = await session.execute(
            select(Donation).where(
                Donation.user_id == user.id
            )
        )
        return donations.scalars().all()


donation_crud = CRUDDonation(Donation)
