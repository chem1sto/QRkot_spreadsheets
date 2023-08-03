from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import current_superuser, current_user, get_async_session
from app.crud import charity_project_crud, donation_crud
from app.services import investing_process
from app.models import User
from app.schemas import DonationDB, DonationCreate

router = APIRouter()


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude={
        'user_id',
        'invested_amount',
        'fully_invested',
        'close_date'
    },
    response_model_exclude_none=True,
)
async def create_donation(
        donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    """Сделать пожертвование."""
    new_donation = await donation_crud.create(
        obj_in=donation,
        session=session,
        user=user,
        commit=False
    )
    session.add_all(
        investing_process(
            target=new_donation,
            sources=await charity_project_crud.get_not_fully_invested(session),
        )
    )
    await session.commit()
    await session.refresh(new_donation)
    return new_donation


@router.get(
    '/',
    response_model=List[DonationDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.
    Возвращает список всех пожертвований.
    """
    all_donations = await donation_crud.get_multi(
        session=session
    )
    return all_donations


@router.get(
    '/my',
    response_model_exclude_none=True,
    response_model_exclude={
        'user_id',
        'invested_amount',
        'fully_invested',
        'close_date'
    },
    response_model=List[DonationDB]
)
async def get_user_donations(
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    """Возвращает список пожертвований пользователя, выполняющего запрос."""
    user_donations = await donation_crud.get_by_user(
        user=user,
        session=session
    )
    return user_donations
