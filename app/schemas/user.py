from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    """Схема для чтения данных пользователя."""
    pass


class UserCreate(schemas.BaseUserCreate):
    """Схема для создания нового пользователя."""
    pass


class UserUpdate(schemas.BaseUserUpdate):
    """Схема для обновления существующего пользователя."""
    pass
