from datetime import datetime as dt

from sqlalchemy import Column, Integer, Boolean, DateTime, CheckConstraint

from app.constants import DEFAULT_INVESTED_AMOUNT
from app.core import Base


class InvestingBaseModel(Base):
    """Базовый абстрактный класс для проектов и пожертвований."""
    __abstract__ = True
    __table_args__ = (
        CheckConstraint('full_amount > 0'),
        CheckConstraint('invested_amount >= 0'),
        CheckConstraint('invested_amount <= full_amount'),
    )
    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(
        Integer,
        nullable=False,
        default=DEFAULT_INVESTED_AMOUNT
    )
    fully_invested = Column(Boolean, default=False)
    create_date = Column(
        DateTime,
        nullable=False,
        default=dt.now
    )
    close_date = Column(DateTime)

    def __repr__(self):
        return (
            f'Объект №{self.id}. '
            f'Статус закрытия: {self.fully_invested}. '
            f'Нужно для закрытия {self.full_amount} условных единиц. '
            f'Вложено {self.invested_amount} условных единиц. '
            f'Дата создания: {self.create_date}. '
            f'Дата закрытия: {self.close_date}.'
        )
