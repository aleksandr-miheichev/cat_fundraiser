from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser

from app.crud.charity_project import charity_project_crud
from app.services.google_api import (
    set_user_permissions, spreadsheets_create, spreadsheets_update_value
)

URL_GOOGLE_TABLES = 'https://docs.google.com/spreadsheets/d/'
router = APIRouter()


@router.post(
    '/',
    dependencies=[Depends(current_superuser)],
)
async def get_charity_projects_report(
        session: AsyncSession = Depends(get_async_session),
        google_services: Aiogoogle = Depends(get_service)

):
    """
    Генерирует отчет Google Spreadsheet для благотворительных проектов,
    отсортированных по времени, которое потребовалось для закрытия проекта.

    Параметры:
      - session (AsyncSession): сессия SQLAlchemy.
      - google_services (Aiogoogle): экземпляр Aiogoogle для взаимодействия с
        API Google.

    Возвращает:
        str: URL созданной электронной таблицы Google.
    """
    projects = await charity_project_crud.get_projects_by_completion_rate(
        session)
    google_spreadsheet_id = await spreadsheets_create(google_services)
    await set_user_permissions(google_spreadsheet_id, google_services)
    await spreadsheets_update_value(google_spreadsheet_id, projects,
                                    google_services)
    return URL_GOOGLE_TABLES + google_spreadsheet_id
