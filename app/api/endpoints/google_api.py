from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from http import HTTPStatus

from app.constants import GOOGLE_TABLE_LINK
from app.core import current_superuser, get_async_session, get_service
from app.crud import charity_project_crud
from app.services.google_api import (
    spreadsheets_create, set_user_permissions, spreadsheets_update_value
)

ERROR_MESSAGE = 'Возникла ошибка: {error}'
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

    spreadsheet_id, now_date_time = await spreadsheets_create(
        wrapper_services
    )
    await set_user_permissions(spreadsheet_id, wrapper_services)
    try:
        await spreadsheets_update_value(
            spreadsheet_id,
            projects,
            wrapper_services,
            now_date_time
        )
    except ValueError as error:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=ERROR_MESSAGE.format(error=error)
        )
    return GOOGLE_TABLE_LINK.format(spreadsheet_id=spreadsheet_id)
