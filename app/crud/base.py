from typing import Optional
from datetime import datetime as dt

from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class CRUDBase:
    def __init__(self, model):
        self.model = model

    async def get(
            self,
            obj_id: int,
            session: AsyncSession,
    ):
        """Получение объекта по его id."""
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalars().first()

    async def get_multi(self, session: AsyncSession):
        """Получение из БД всех объектов."""
        db_objs = await session.execute(select(self.model))
        db_objs = db_objs.scalars().all()
        return db_objs

    async def create(
            self,
            obj_in,
            session: AsyncSession,
            commit: bool = True,
            user: Optional[User] = None,
    ):
        """Создание нового объекта и сохранение его в БД."""
        obj_in_data = obj_in.dict()
        if user is not None:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        if commit:
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

    async def get_not_fully_invested(
            self,
            session: AsyncSession
    ):
        """Получение из БД всех незакрытых объектов с сортировкой по дате."""
        not_fully_invested_objs = await session.scalars(
            select(self.model).where(
                self.model.fully_invested.is_(False)
            ).order_by(asc('create_date'))
        )
        return not_fully_invested_objs.all()

    @staticmethod
    async def update(
            db_obj,
            obj_in,
            session: AsyncSession,
    ):
        """Обновление объекта."""
        update_data = obj_in.dict(exclude_unset=True)
        if (
            'full_amount' in update_data and
            update_data['full_amount'] == db_obj.invested_amount
        ):
            update_data['fully_invested'] = True
            update_data['close_data'] = dt.now()
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    @staticmethod
    async def remove(
            db_obj,
            session: AsyncSession
    ):
        """Удаление объекта."""
        await session.delete(db_obj)
        await session.commit()
        return db_obj
