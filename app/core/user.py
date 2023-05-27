from typing import Optional, Union

from fastapi import Depends, Request
from fastapi_users import (BaseUserManager, FastAPIUsers, IntegerIDMixin,
                           InvalidPasswordException)
from fastapi_users.authentication import (AuthenticationBackend,
                                          BearerTransport, JWTStrategy)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_async_session
from app.models.user import User
from app.schemas.user import UserCreate

CONDITION_PASSWORD_LENGTH = 'Password should be at least 3 characters'
PASSWORD_NO_E_MAIL = 'Password should not contain e-mail'
USER_REGISTERED = 'Пользователь {email} зарегистрирован.'


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """
    Асинхронный менеджер контекста, который возвращает экземпляр
    SQLAlchemyUserDatabase.

    Аргументы:
        - session (AsyncSession): асинхронная сессия SQLAlchemy. По умолчанию
          используется сессия, предоставленная get_async_session.

    Выдаёт:
        - SQLAlchemyUserDatabase: экземпляр базы данных пользователей для
          взаимодействия с моделями User.
    """
    yield SQLAlchemyUserDatabase(session, User)


bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')


def get_jwt_strategy() -> JWTStrategy:
    """
    Создает экземпляр JWTStrategy для обработки аутентификации JWT.
    """
    return JWTStrategy(secret=settings.secret, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """
    Настраиваемый менеджер пользователей, который расширяет BaseUserManager с
    использованием кастомной валидации пароля и действий после регистрации.
    """

    async def validate_password(
            self,
            password: str,
            user: Union[UserCreate, User],
    ) -> None:
        """
        Проверяет пароль на основе настроенных правил.

        Аргументы:
            - password (str): пароль, который нужно проверить.
            - user (Union[UserCreate, User]): экземпляр пользователя,
              связанный с паролем.

        Вызывает:
            - InvalidPasswordException: если пароль состоит менее чем из 3
              символов или содержит электронную почту пользователя.
        """
        if len(password) < 3:
            raise InvalidPasswordException(reason=CONDITION_PASSWORD_LENGTH)
        if user.email in password:
            raise InvalidPasswordException(reason=PASSWORD_NO_E_MAIL)

    async def on_after_register(
            self,
            user: User,
            request: Optional[Request] = None
    ):
        """
        Печатает сообщение после регистрации пользователя.

        Аргументы:
            - user (User): экземпляр пользователя, который был зарегистрирован.
            - request (Request, необязательно, по умолчанию = None): экземпляр
              запроса, связанный с регистрацией.
        """
        print(USER_REGISTERED.format(email=user.email))


async def get_user_manager(user_db=Depends(get_user_db)):
    """
    Асинхронный менеджер контекста, который выдает экземпляр UserManager.

    Аргументы:
        - user_db: экземпляр базы данных пользователей. По умолчанию
          используется экземпляр SQLAlchemyUserDatabase, предоставленный
          get_user_db.

    Выдаёт:
        - UserManager: экземпляр менеджера пользователей для обработки
          операций, связанных с пользователями.
    """
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend], )

current_user = fastapi_users.current_user(active=True)

current_superuser = fastapi_users.current_user(active=True, superuser=True)
