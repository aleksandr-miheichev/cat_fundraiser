from copy import deepcopy
from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings
from app.models import CharityProject

OVER_NUMBER_OF_ROWS = (
    'В таблице слишком много строк: {number_lines}. Максимально допустимое '
    'значение - {max_number_rows}'
)
EXCEED_NUMBER_OF_COLUMNS = (
    'В таблице слишком много столбцов: {number_columns}. Максимально '
    'допустимое значение - {max_number_columns}'
)
FORMAT = "%Y/%m/%d %H:%M:%S"
ID_LIST = 0
COLUMN_COUNT = 11
ROW_COUNT = 100
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


async def spreadsheets_create(google_services_wrapper: Aiogoogle) -> str:
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
    spreadsheet_body = deepcopy(SPREADSHEET_TEMPLATE)
    spreadsheet_body['properties']['title'] = (
        spreadsheet_body['properties']['title'].format(
            date=datetime.now().strftime(FORMAT)
        )
    )
    service = await google_services_wrapper.discover('sheets', 'v4')
    response = await google_services_wrapper.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    return response['spreadsheetId']


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
    service = await google_services_wrapper.discover('sheets', 'v4')
    header = deepcopy(HEADER)
    header[0][1] = header[0][1].format(date=datetime.now().strftime(FORMAT))
    charity_projects = sorted(
        charity_projects,
        key=lambda project: project.close_date - project.create_date
    )
    table_values = [
        *header,
        *[list(map(str, [
            project['name'],
            project['close_date'] - project['create_date'],
            project['description']
        ])) for project in charity_projects]]
    max_rows = len(table_values)
    if max_rows > ROW_COUNT:
        raise ValueError(OVER_NUMBER_OF_ROWS.format(
            number_lines=len(table_values),
            max_number_rows=ROW_COUNT
        ))
    max_columns = max(map(len, table_values))
    if max_columns > COLUMN_COUNT:
        raise ValueError(EXCEED_NUMBER_OF_COLUMNS.format(
            number_columns=max_columns,
            max_number_columns=COLUMN_COUNT
        ))
    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    await google_services_wrapper.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{max_rows}C{max_columns}',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
    return spreadsheet_id
