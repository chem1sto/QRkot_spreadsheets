import copy
from datetime import datetime as dt

from aiogoogle import Aiogoogle
from app.core import settings
from app.constants import COLUMN_COUNT, ROW_COUNT


FORMAT = '%Y/%m/%d %H:%M:%S'
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
    'В созданной таблице слишком мало строк! '
    f'Создано: {ROW_COUNT}. '
    'Требуемое количество: {rows}.'
)
COLUMN_COUNT_ERROR_MESSAGE = (
    'В созданной таблице слишком мало столбцов! '
    f'Создано: {COLUMN_COUNT}. '
    'Требуемое количество: {columns}.'
)


async def spreadsheets_create(
        wrapper_services: Aiogoogle,
        spreadsheet_body=None
) -> str:
    """Создание новой google-таблицы."""
    now_date_time = dt.now().strftime(FORMAT)
    if spreadsheet_body is None:
        spreadsheet_body = copy.deepcopy(GOOGLE_TABLE_BODY)
        spreadsheet_body['properties']['title'] = (
            GOOGLE_TABLE_BODY['properties']['title'].format(
                now_date_time=now_date_time
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
    table_header = copy.deepcopy(TABLE_HEADER)
    table_header[0][1] = TABLE_HEADER[0][1].format(
        now_date_time=dt.now().strftime(FORMAT)
    )
    service = await wrapper_services.discover('sheets', 'v4')
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
    table_rows = len(table_values)
    table_columns = max(map(len, table_values))
    if table_rows > ROW_COUNT:
        raise ValueError(ROW_COUNT_ERROR_MESSAGE.format(
            rows=table_rows))
    if table_columns > COLUMN_COUNT:
        raise ValueError(COLUMN_COUNT_ERROR_MESSAGE.format(
            columns=table_columns)
        )
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{table_rows}C{table_columns}',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
