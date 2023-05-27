from datetime import datetime
from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import not_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class CRUDBase:
    """Базовый класс для операций CRUD."""

    def __init__(self, model):
        """
        Инициализация CRUDBase с моделью.

        Аргументы:
            - model: модель, с которой будет работать этот класс CRUD-операций.
        """
        self.model = model

    async def get_multi(self, session: AsyncSession):
        """
        Получить несколько экземпляров модели из базы данных.

        Аргументы:
            - session (AsyncSession): сессия SQLAlchemy, которую нужно
              использовать для операций с базой данных.

        Возвращает:
            Список экземпляров модели.
        """
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
            self,
            session: AsyncSession,
            obj_in,
            user: Optional[User] = None,
            commit: bool = True
    ):
        """
        Создать новый экземпляр модели в базе данных.

        Аргументы:
            - session (AsyncSession): сессия SQLAlchemy, которую нужно
              использовать для операций с базой данных.
            - obj_in: данные, которые нужно использовать для создания нового
              экземпляра.
            - user (User, не обязательный): необязательный экземпляр
              пользователя, который будет связан с новым экземпляром.
            - commit (bool, по умолчанию = True): флаг, контролирующий, следует
              ли вызвать метод commit после добавления объекта в сессию.

        Возвращает:
            Вновь созданный экземпляр модели.
        """
        obj_in_data = obj_in.dict()
        if user is not None:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        if commit:
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

    async def update(
            self,
            session: AsyncSession,
            db_obj,
            obj_in,
    ):
        """
        Обновляет данный объект благотворительного проекта.

        Атрибуты:
            - session (AsyncSession): сессия SQLAlchemy.
            - db_obj: объект, который нужно обновить.
            - obj_in: новые данные, которыми нужно обновить объект.

        Возвращает:
            Обновленный объект.
        """
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)
        if (
                'full_amount' in update_data and
                update_data['full_amount'] == db_obj.invested_amount
        ):
            update_data['fully_invested'] = True
            update_data['close_data'] = datetime.now()
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(
            self,
            session: AsyncSession,
            db_obj,
    ):
        """
        Удаляет данный объект благотворительного проекта.

        Атрибуты:
            - session (AsyncSession): сессия SQLAlchemy.
            - db_obj: объект, который нужно удалить.

        Возвращает:
            Удаленный объект.
        """
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    async def get_unfunded_projects(self, session: AsyncSession):
        """
        Получить все проекты из базы данных, которые не полностью
        профинансированы.

        Аргументы:
            - session (AsyncSession): сессия SQLAlchemy, которую нужно
              использовать для операций с базой данных.

        Возвращает:
            Список проектов, которые не полностью профинансированы.
        """
        return (await session.execute(select(self.model).where(
            not_(self.model.fully_invested)
        ).order_by(self.model.create_date))).scalars().all()

    async def get_charity_project_obj_by_id(
            self,
            charity_project_id: int,
            session: AsyncSession,
    ):
        """
        Получает объект благотворительного проекта по его ID.

        Атрибуты:
            - charity_project_id (int): ID благотворительного проекта.
            - session (AsyncSession): сессия SQLAlchemy.

        Возвращает:
            Объект благотворительного проекта, или None, если подходящий
            проект не найден.
        """
        return (await session.execute(select(self.model).where(
            self.model.id == charity_project_id
        ))).scalars().first()

    async def get_uninvested(self, session: AsyncSession):
        """
        Собирает все экземпляры модели, в которых объект не закрыт
        (fully_invested == False).

        Атрибуты:
            - session (AsyncSession): SQLAlchemy сессия.

        Возвращает:
            Список экземпляров модели, для которых значение fully_invested =
            False.
        """
        result = await session.execute(select(self.model).where(
            self.model.fully_invested == False  # noqa
        ))
        return result.scalars().all()

    async def get_fully_invested(self, session: AsyncSession):
        """
        Собирает все экземпляры модели, в которых объект проинвестирован
        (fully_invested == True).

        Атрибуты:
          - session (AsyncSession): SQLAlchemy сессия.

        Возвращает:
            Список экземпляров модели, для которых значение
            fully_invested = True.
        """
        return (await session.execute(select(self.model).where(
            self.model.fully_invested == True  # noqa
        ))).scalars().all()
