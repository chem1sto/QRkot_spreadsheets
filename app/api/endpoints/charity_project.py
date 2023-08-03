from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_charity_project_name_duplicate,
    check_charity_project_exist,
    check_project_invest_amount_is_empty,
    check_project_is_close,
    check_full_amount_no_less_than_invested_amount,
)
from app.core import get_async_session, current_superuser
from app.crud import charity_project_crud, donation_crud
from app.services import investing_process
from app.schemas import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)


router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_new_charity_project(
    charity_project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.
    Создаёт благотворительный проект.
    """
    await check_charity_project_name_duplicate(
        charity_project_name=charity_project.name,
        session=session
    )
    new_charity_project = await charity_project_crud.create(
        obj_in=charity_project,
        session=session,
        commit=False
    )
    session.add_all(
        investing_process(
            target=new_charity_project,
            sources=await donation_crud.get_not_fully_invested(session),
        )
    )
    await session.commit()
    await session.refresh(new_charity_project)
    return new_charity_project


@router.get(
    '/',
    response_model_exclude_none=True,
    response_model=List[CharityProjectDB]
)
async def get_all_charity_projects(
        session: AsyncSession = Depends(get_async_session),
):
    """Возвращает список всех проектов."""
    all_charity_projects = await charity_project_crud.get_multi(
        session=session
    )
    return all_charity_projects


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def partially_update_charity_project(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.
    Закрытый проект нельзя редактировать;
    нельзя установить требуемую сумму меньше вложенной.
    """
    charity_project = await check_charity_project_exist(
        charity_project_id=project_id,
        session=session
    )
    check_project_is_close(charity_project_obj=charity_project)
    if obj_in.name is not None:
        await check_charity_project_name_duplicate(
            charity_project_name=obj_in.name,
            session=session
        )
    if obj_in.full_amount is not None:
        check_full_amount_no_less_than_invested_amount(
            invested_amount=charity_project.invested_amount,
            new_full_amount=obj_in.full_amount,
        )
    charity_project = await charity_project_crud.update(
        db_obj=charity_project,
        obj_in=obj_in,
        session=session,
    )
    return charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def remove_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.
    Удаляет проект. Нельзя удалить проект, в который уже были инвестированы
    средства, его можно только закрыть.
    """
    charity_project = await check_charity_project_exist(
        charity_project_id=project_id,
        session=session
    )
    check_project_invest_amount_is_empty(charity_project_obj=charity_project)
    check_project_is_close(charity_project_obj=charity_project)
    charity_project = await charity_project_crud.remove(
        db_obj=charity_project,
        session=session
    )
    return charity_project
