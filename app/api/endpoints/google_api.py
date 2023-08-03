from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import current_superuser, get_async_session, get_service
from app.crud import charity_project_crud
from app.services.google_api import (
    spreadsheets_create, set_user_permissions, spreadsheets_update_value
)

router = APIRouter()


@router.post(
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
    spreadsheetid = await spreadsheets_create(wrapper_services)
    await set_user_permissions(spreadsheetid, wrapper_services)
    await spreadsheets_update_value(
        spreadsheetid, projects, wrapper_services
    )
    return f'https://docs.google.com/spreadsheets/d/{spreadsheetid}'
