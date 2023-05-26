from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings
from app.models import CharityProject

FORMAT = "%Y/%m/%d %H:%M:%S"
ROW_COUNT = 100
COLUMN_COUNT = 11
ID_LIST = 0


async def spreadsheets_create(google_services_wrapper: Aiogoogle) -> str:
    """
    Создает новую электронную таблицу Google с определенными свойствами и
    настройками.

    Параметры:
      - google_services_wrapper (Aiogoogle): экземпляр Aiogoogle для
      взаимодействия с API Google Sheets.

    Возвращает:
        str: ID созданной электронной таблицы Google.
    """
    now_date_time = datetime.now().strftime(FORMAT)
    service = await google_services_wrapper.discover('sheets', 'v4')
    spreadsheet_body = {
        'properties': {
            'title': f'Отчет на {now_date_time}',
            'locale': 'ru_RU'
        },
        'sheets': [{'properties': {
            'sheetType': 'GRID',
            'sheetId': ID_LIST,
            'title': 'Лист1',
            'gridProperties': {
                'rowCount': ROW_COUNT,
                'columnCount': COLUMN_COUNT
            }
        }}]
    }
    response = await google_services_wrapper.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id


async def set_user_permissions(
        spreadsheet_id: str,
        google_services_wrapper: Aiogoogle
) -> None:
    """
    Предоставляет права доступа вашему личному аккаунту для указанной
    электронной таблицы Google.

    Параметры:
      - spreadsheet_id (str): ID электронной таблицы Google, для которой нужно
        установить права доступа.
      - google_services_wrapper (Aiogoogle): экземпляр Aiogoogle для
        взаимодействия с API Google Drive.
    """
    permissions_body = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': settings.email
    }
    service = await google_services_wrapper.discover('drive', 'v3')
    await google_services_wrapper.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        charity_projects: list[CharityProject],
        google_services_wrapper: Aiogoogle
) -> str:
    """
    Обновить указанную таблицу Google данными из предоставленных
    благотворительных проектов.

    Параметры:
      - spreadsheet_id (str): ID электронной таблицы Google, которую нужно
        обновить.
      - charity_projects (list[CharityProject]): список объектов CharityProject
        для включения в электронную таблицу.
      - google_services_wrapper (Aiogoogle): экземпляр Aiogoogle для
        взаимодействия с API Google Sheets.

    Возвращает:
        str: ID обновленной электронной таблицы Google.
    """
    now_date_time = datetime.now().strftime(FORMAT)
    service = await google_services_wrapper.discover('sheets', 'v4')
    table_values = [
        ['Отчет от', now_date_time],
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание']
    ]
    for project in charity_projects:
        new_row = [
            str(project['name']),
            str(project['close_date'] - project['create_date']),
            str(project['description'])
        ]
        table_values.append(new_row)
    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    await google_services_wrapper.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'A1:C{len(table_values)}',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
    return spreadsheet_id
