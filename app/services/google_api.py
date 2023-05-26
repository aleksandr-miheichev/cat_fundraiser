from copy import deepcopy
from datetime import datetime

from aiogoogle import Aiogoogle

from app.api.validators import ensure_spreadsheet_data_fits
from app.core.config import settings
from app.core.google_client import COLUMN_COUNT, ROW_COUNT
from app.models import CharityProject

FORMAT = "%Y/%m/%d %H:%M:%S"
ID_LIST = 0
SPREADSHEET_TEMPLATE = dict(
    properties=dict(
        title='Отчет от {date}',
        locale='ru_RU',
    ),
    sheets=[dict(properties=dict(
        sheetType='GRID',
        sheetId=ID_LIST,
        title='Лист1',
        gridProperties=dict(
            rowCount=ROW_COUNT,
            columnCount=COLUMN_COUNT
        )
    ))]
)
HEADER = [
    ['Отчет от', '{date}'],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]


async def spreadsheets_create(
        google_services_wrapper: Aiogoogle,
        spreadsheet_template=SPREADSHEET_TEMPLATE
) -> str:
    """
    Создает новую электронную таблицу Google с определенными свойствами и
    настройками.

    Параметры:
      - google_services_wrapper (Aiogoogle): экземпляр Aiogoogle для
        взаимодействия с API Google Sheets.
      - spreadsheet_template (dict, необязательно): шаблон для структуры и
        свойств создаваемой электронной таблицы.

    Возвращает:
        str: ID созданной электронной таблицы Google.
    """
    now_date_time = datetime.now().strftime(FORMAT)
    spreadsheet_body = deepcopy(spreadsheet_template)
    spreadsheet_body['properties']['title'] = (
        spreadsheet_body['properties']['title'].format(date=now_date_time)
    )
    service = await google_services_wrapper.discover('sheets', 'v4')
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
    header = deepcopy(HEADER)
    header[0][1] = header[0][1].format(date=now_date_time)
    table_values = [
        *header,
        *[list(map(str, [
            project['name'],
            project['close_date'] - project['create_date'],
            project['description']
        ])) for project in charity_projects]]
    ensure_spreadsheet_data_fits(table_values)
    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    max_columns = max(len(row) for row in HEADER)
    await google_services_wrapper.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{len(table_values)}C{max_columns}',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
    return spreadsheet_id


def get_projects_by_completion_rate(projects):
    """
    Сортирует список проектов на основе времени, затраченного на их завершение.

    Аргументы:
      - projects (list): список экземпляров проектов.

    Возвращает:
        list: список проектов, отсортированный по времени, затраченному на
        завершение, от самого короткого до самого длинного.
    """
    return sorted(
        projects,
        key=lambda project: project.close_date - project.create_date
    )
