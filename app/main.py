from fastapi import FastAPI

from app.api.routers import main_router
from app.core.config import settings
from app.core.init_db import create_first_superuser

app = FastAPI(
    title=settings.app_title,
    description=settings.description
)


@app.on_event('startup')
async def startup():
    """
    Асинхронный менеджер контекста, который создает первого суперпользователя
    при запуске приложения.
    """
    await create_first_superuser()


app.include_router(main_router)

# SQLAlchemy 2.0
# from contextlib import asynccontextmanager
#
# from fastapi import FastAPI
#
# from app.api.routers import main_router
# from app.core.config import settings
# from app.core.init_db import create_first_superuser
#
#
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """
#     Асинхронный менеджер контекста, который создает первого суперпользователя
#     при запуске приложения.
#     """
#     await create_first_superuser()
#     yield
#
#
# app = FastAPI(
#     title=settings.app_title,
#     description=settings.description,
#     lifespan=lifespan
# )
#
# app.include_router(main_router)
