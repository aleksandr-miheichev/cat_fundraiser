from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, declared_attr, sessionmaker

from app.core.config import settings


class PreBase:
    """
    Базовый класс для моделей SQLAlchemy с общим столбцом 'id' и атрибутом
    '__tablename__'.

    Атрибуты:
        - id (int): Общий атрибут для всех производных классов, служащий
          колонкой первичного ключа в базе данных.
    """

    @declared_attr
    def __tablename__(cls):
        """
        Возвращает имя класса в нижнем регистре, которое будет использоваться
        в качестве имени таблицы.
        """
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=PreBase)

engine = create_async_engine(settings.database_url)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


# SQLAlchemy 2.0
# AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_async_session():
    """Асинхронный менеджер контекста для сессий SQLAlchemy."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
