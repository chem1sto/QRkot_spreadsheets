from datetime import datetime as dt

from aiogoogle import Aiogoogle
from app.core import settings
from app.constants import COLUMN_COUNT, ROW_COUNT

DATE_TIME_FORMAT = '%Y/%m/%d %H:%M:%S'
FIRST_TABLE_CELL = 'R1C1'
GOOGLE_TABLE_BODY = dict(
        properties=dict(
            title='Отчет от {now_date_time}',
            locale='ru_RU',
        ),
        sheets=[dict(properties=dict(
            sheetType='GRID',
            sheetId=0,
            title='Лист1',
            gridProperties=dict(
                rowCount=ROW_COUNT,
                columnCount=COLUMN_COUNT,
            )
        ))]
    )
TABLE_HEADER = [
    ['Отчет от', '{now_date_time}'],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]
ROW_COUNT_ERROR_MESSAGE = (
    'В созданной таблице строк или столбцов меньше, чем требуется!'
)


async def spreadsheets_create(
        wrapper_services: Aiogoogle,
        date_time_now: str = None,
        spreadsheet_body=None
) -> str:
    """Создание новой google-таблицы."""
    if date_time_now is None:
        date_time_now = dt.now().strftime(DATE_TIME_FORMAT)
    if spreadsheet_body is None:
        spreadsheet_body = GOOGLE_TABLE_BODY.copy()
        spreadsheet_body['properties']['title'] = (
            GOOGLE_TABLE_BODY['properties']['title'].format(
                now_date_time=date_time_now
            ))
    service = await wrapper_services.discover('sheets', 'v4')
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    return response['spreadsheetId']


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    """
    Предоставление прав доступа google-аккаунту
    для созданной google-таблицы.
    """
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        closed_projects: list,
        wrapper_services: Aiogoogle,
        date_time_now: str = None
) -> None:
    """Запись данных, полученных из БД, в google-таблицу."""
    if date_time_now is None:
        date_time_now = dt.now().strftime(DATE_TIME_FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    table_header = TABLE_HEADER.copy()
    table_header[0][1] = TABLE_HEADER[0][1].format(
            now_date_time=date_time_now
        )
    table_values = [
        *table_header,
        *[list(map(
            str,
            [project['name'],
             project['close_date'] - project['create_date'],
             project['description']]
        )) for project in closed_projects]
    ]
    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    table_rows = len(table_header) + len(closed_projects)
    table_columns = max(len(row) for row in table_header)
    if table_rows > ROW_COUNT or table_columns > COLUMN_COUNT:
        raise ValueError(ROW_COUNT_ERROR_MESSAGE)
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=(
                f'{FIRST_TABLE_CELL}:R{table_rows}C{table_columns}'
            ),
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
