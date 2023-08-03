from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models import CharityProject

DUPLICATE_PROJECT_NAME_ERROR_MESSAGE = 'Проект с таким именем уже существует!'
PROJECT_NOT_FOUND_ERROR_MESSAGE = 'Проект не найден!'
NO_DELETION_FOR_INVESTED_PROJECT_ERROR_MESSAGE = (
    'В проект были внесены средства, не подлежит удалению!'
)
NO_UPDATING_FOR_CLOSED_PROJECT = 'Закрытый проект нельзя редактировать!'
FULL_AMOUNT_NO_LESS_THAN_INVESTED_AMOUNT_ERROR_MESSAGE = (
    'Новая требуемая сумма должна быть не меньше старой!'
)


def check_charity_project_fields_not_empty_or_null(
        charity_project: CharityProject,
        session: AsyncSession,
):
    if value == '' or value is None:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Обязательные поля не могут быть пустыми!',
        )
    return value


async def check_charity_project_name_duplicate(
        charity_project_name: str,
        session: AsyncSession,
) -> None:
    """Проверка названия проекта на дублирование."""
    charity_project_id = await charity_project_crud.get_project_id_by_name(
        charity_project_name=charity_project_name,
        session=session
    )
    if charity_project_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=DUPLICATE_PROJECT_NAME_ERROR_MESSAGE
        )


async def check_charity_project_exist(
        charity_project_id: int,
        session: AsyncSession,
) -> CharityProject:
    """Проверка на наличие проекта в БД."""
    charity_project = await charity_project_crud.get(
        obj_id=charity_project_id,
        session=session
    )
    if charity_project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=PROJECT_NOT_FOUND_ERROR_MESSAGE
        )
    return charity_project


def check_project_invest_amount_is_empty(
        charity_project_obj: CharityProject
) -> None:
    """Проверка проекта на наличие внесённых средств."""
    if charity_project_obj.invested_amount != 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=NO_DELETION_FOR_INVESTED_PROJECT_ERROR_MESSAGE
        )


def check_project_is_close(charity_project_obj: CharityProject) -> None:
    """Проверка проекта на закрытие по дате."""
    if charity_project_obj.close_date is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=NO_UPDATING_FOR_CLOSED_PROJECT
        )


def check_full_amount_no_less_than_invested_amount(
        invested_amount: int,
        new_full_amount: int,
) -> None:
    """Проверка новой требуемой суммы для проекта."""
    if new_full_amount < invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=FULL_AMOUNT_NO_LESS_THAN_INVESTED_AMOUNT_ERROR_MESSAGE
        )
