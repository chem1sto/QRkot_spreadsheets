import copy
from datetime import datetime as dt

from aiogoogle import Aiogoogle
from app.core import settings
from app.constants import COLUMN_COUNT, ROW_COUNT


DATE_TIME_NOW = dt.now().strftime('%Y/%m/%d %H:%M:%S')
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
    ['Отчет от', DATE_TIME_NOW],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]
ROW_COUNT_ERROR_MESSAGE = (
    'В созданной таблице слишком мало строк! '
    'Создано: {created_rows} строки. Требуемое количество: {rows} строк.'
)
COLUMN_COUNT_ERROR_MESSAGE = (
    'В созданной таблице слишком мало столбцов! '
    'Создано: {created_columns} столбца. '
    'Требуемое количество: {columns} столбцов.'
)


async def spreadsheets_create(
        wrapper_services: Aiogoogle,
        spreadsheet_body=None
) -> str:
    """Создание новой google-таблицы."""
    if spreadsheet_body is None:
        spreadsheet_body = copy.deepcopy(GOOGLE_TABLE_BODY)
        spreadsheet_body['properties']['title'] = (
            GOOGLE_TABLE_BODY['properties']['title'].format(
                now_date_time=DATE_TIME_NOW
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
) -> None:
    """Запись данных, полученных из БД, в google-таблицу."""
    service = await wrapper_services.discover('sheets', 'v4')
    table_values = [
        *TABLE_HEADER,
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
    table_rows = len(table_values)
    table_columns = max(map(len, table_values))
    if table_rows > ROW_COUNT:
        raise ValueError(ROW_COUNT_ERROR_MESSAGE.format(
            created_rows=ROW_COUNT, rows=table_rows))
    if table_columns > COLUMN_COUNT:
        raise ValueError(COLUMN_COUNT_ERROR_MESSAGE.format(
            created_columns=COLUMN_COUNT, columns=table_columns)
        )
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{table_rows}C{table_columns}',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
