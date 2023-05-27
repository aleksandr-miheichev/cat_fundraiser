from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.services.google_api import (
    set_user_permissions,
    spreadsheets_create,
    spreadsheets_update_value
)

GOOGLE_TABLES_URL = 'https://docs.google.com/spreadsheets/d/{}'
UPDATE_ERROR_MSG = 'Ошибка обновления электронной таблицы: {}'

router = APIRouter()


@router.post(
    '/',
    dependencies=[Depends(current_superuser)],
)
async def get_charity_projects_report(
        session: AsyncSession = Depends(get_async_session),
        google_client: Aiogoogle = Depends(get_service)

):
    """
    Генерирует отчет Google Spreadsheet для благотворительных проектов,
    отсортированных по времени, которое потребовалось для закрытия проекта.

    Параметры:
      - session (AsyncSession): сессия SQLAlchemy.
      - google_client (Aiogoogle): экземпляр Aiogoogle для взаимодействия с
        API Google.

    Возвращает:
        str: URL созданной электронной таблицы Google.
    """
    projects = await charity_project_crud.get_fully_invested(session)
    google_spreadsheet_id = await spreadsheets_create(google_client)
    await set_user_permissions(google_spreadsheet_id, google_client)
    try:
        await spreadsheets_update_value(
            google_spreadsheet_id,
            projects,
            google_client
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=UPDATE_ERROR_MSG.format(e))
    return GOOGLE_TABLES_URL.format(google_spreadsheet_id)
