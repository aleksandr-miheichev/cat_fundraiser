from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject


class CRUDCharityProject(CRUDBase):
    """
    Класс для обработки CRUD-операций, связанных с моделью CharityProject.
    """

    async def get_charity_project_id_by_name(
            self,
            charity_project_name: str,
            session: AsyncSession,
    ) -> Optional[int]:
        """
        Получает идентификатор благотворительного проекта по его названию.

        Атрибуты:
            - charity_project_name (str): название благотворительного проекта.
            - session (AsyncSession): сессия SQLAlchemy.

        Возвращает:
            ID благотворительного проекта, или None, если подходящий проект не
            найден.
        """
        charity_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == charity_project_name
            )
        )
        charity_project_id = charity_project_id.scalars().first()
        return charity_project_id

    async def get_projects_by_completion_rate(
            self,
            db_session: AsyncSession,
    ) -> list[CharityProject]:
        """
        Получает список всех закрытых проектов, отсортированный по времени,
        которое потребовалось для закрытия проекта — от тех, что закрылись
        быстрее всего, до тех, что долго собирали нужную сумму.

        Атрибуты:
            - session (AsyncSession): сессия SQLAlchemy.

        Возвращает:
            Список проектов, отсортированный по времени, которое потребовалось
            для закрытия проекта.
        """
        result = await db_session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested == True  # noqa
            )
        )
        return sorted(
            result.scalars().all(),
            key=lambda project: project.close_date - project.create_date
        )


charity_project_crud = CRUDCharityProject(CharityProject)
