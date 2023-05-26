from http.client import METHOD_NOT_ALLOWED

from fastapi import APIRouter, HTTPException

from app.core.user import auth_backend, fastapi_users
from app.schemas.user import UserCreate, UserRead, UserUpdate

DEACTIVATE_USERS = 'Не используйте удаление, деактивируйте пользователей.'
DELETE_USERS_FORBIDDEN = 'Удаление пользователей запрещено!'

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=['auth'],
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix='/users',
    tags=['users'],
)


@router.delete(
    '/users/{id}',
    tags=['users'],
    deprecated=True,
    description=DEACTIVATE_USERS,
)
def delete_user(id: str):
    """
    Запрещает удаление пользователей. Вместо этого пользователи должны быть
    деактивированы.

    Атрибуты:
        - id (str): ID пользователя, которого нужно удалить.

    Вызывает:
        HTTPException: всегда вызывает исключение 405 HTTP, указывающее на то,
        что удаление пользователя запрещено.
    """
    raise HTTPException(
        status_code=METHOD_NOT_ALLOWED,
        detail=DELETE_USERS_FORBIDDEN
    )
