from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, Extra, PositiveInt
from app.constants import DEFAULT_INVESTED_AMOUNT

DONATION_INVESTED_AMOUNT = 'Вложенная сумма пожертвования'


class DonationCreate(BaseModel):
    comment: Optional[str]
    full_amount: PositiveInt
    invested_amount: Optional[PositiveInt] = Field(
        DEFAULT_INVESTED_AMOUNT,
        title=DONATION_INVESTED_AMOUNT,
    )

    class Config:
        extra = Extra.forbid


class DonationDB(DonationCreate):
    id: int
    user_id: Optional[int]
    invested_amount: Optional[int]
    fully_invested: Optional[bool]
    create_date: Optional[datetime]
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
