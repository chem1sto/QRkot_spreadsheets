from datetime import datetime as dt

from aiogoogle import Aiogoogle
from aiogoogle.excs import AiogoogleError, AuthError
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import GOOGLE_TABLE_LINK
from app.core import current_superuser, get_async_session, get_service
from app.crud import charity_project_crud
from app.services.google_api import (
    spreadsheets_create, set_user_permissions, spreadsheets_update_value
)

AIOGOOGLE_ERROR_MESSAGE = 'Возникла ошибка: {error}'
AUTH_GOOGLE_ERROR_MESSAGE = 'Возникла ошибка авторизации {auth_error}'
DATE_TIME_FORMAT = '%Y/%m/%d %H:%M:%S'
router = APIRouter()


@router.get(
    '/',
    response_model=str,
    dependencies=[Depends(current_superuser)]
)
async def get_report(
        session: AsyncSession = Depends(get_async_session),
        wrapper_services: Aiogoogle = Depends(get_service)
):
    """
    Только для суперюзеров.
    Формирование отчета в google-таблицы
    с сортировкой по скорости сбора средств.
    """
    projects = await charity_project_crud.get_projects_by_completion_rate(
        session
    )
    try:
        date_time_now = dt.now().strftime(DATE_TIME_FORMAT)
        spreadsheet_id = await spreadsheets_create(
            wrapper_services,
            date_time_now
        )
        await set_user_permissions(spreadsheet_id, wrapper_services)
        await spreadsheets_update_value(
            spreadsheet_id,
            projects,
            wrapper_services,
            date_time_now
        )
        return GOOGLE_TABLE_LINK.format(spreadsheet_id=spreadsheet_id)
    except AuthError as auth_error:
        raise Exception(
            AUTH_GOOGLE_ERROR_MESSAGE.format(auth_error=auth_error)
        )
    except AiogoogleError as error:
        raise Exception(AIOGOOGLE_ERROR_MESSAGE.format(error=error))
