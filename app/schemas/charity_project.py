from datetime import datetime as dt
from typing import Optional

from pydantic import (
    BaseModel, Field, Extra, PositiveInt, root_validator, validator
)

from app.constants import (
    DEFAULT_FULL_AMOUNT, DEFAULT_INVESTED_AMOUNT, MAX_LENGTH_PROJECT_NAME,
    MIN_LENGTH_PROJECT_NAME, MIN_LENGTH_PROJECT_DESCRIPTION
)

DESCRIPTION = 'Описание проекта'
DESCRIPTION_SPECIFY_FOR_PROJECT = 'Укажите описание к проекту'
EMPTY_FIELD_ERROR_MESSAGE = 'Поля не могут быть нулевыми или пустыми!'
FULL_AMOUNT = 'Требуемая сумма'
FULL_AMOUNT_DESCRIPTION = 'Укажите, какая сумма нужна'
INVESTED_AMOUNT = 'Вложенная сумма в проект'
NAME = 'Название проекта'
NAME_DESCRIPTION = 'Укажите название благотворительного фонда'
NAME_VALUE_ERROR_MESSAGE = (
    'Название не должно превышать 100 символов или быть пустым!'
)
NAME_VALUE_NOT_A_NUMBER_ERROR_MESSAGE = 'Название не может быть числом!'


class CharityProjectBase(BaseModel):
    """Базовая схема для проекта пожертвований."""
    name: Optional[str] = Field(
        default=None,
        min_length=MIN_LENGTH_PROJECT_NAME,
        max_length=MAX_LENGTH_PROJECT_NAME,
        title=NAME,
        description=NAME_DESCRIPTION
    )
    description: Optional[str] = Field(
        default=None,
        min_length=MIN_LENGTH_PROJECT_DESCRIPTION,
        title=DESCRIPTION,
        description=DESCRIPTION_SPECIFY_FOR_PROJECT
    )
    full_amount: Optional[PositiveInt] = Field(
        default=DEFAULT_FULL_AMOUNT,
        title=FULL_AMOUNT,
        description=FULL_AMOUNT_DESCRIPTION
    )

    class Config:
        extra = Extra.forbid


class CharityProjectUpdate(CharityProjectBase):
    """Схема для обновления проекта пожертвований."""
    @validator('name')
    def check_name_value_and_max_length(cls, value: str):
        if value == '' or value is None:
            raise ValueError(EMPTY_FIELD_ERROR_MESSAGE)
        if len(value) > MAX_LENGTH_PROJECT_NAME or len(value) == 0:
            raise ValueError(NAME_VALUE_ERROR_MESSAGE)
        if value.isnumeric():
            raise ValueError(NAME_VALUE_NOT_A_NUMBER_ERROR_MESSAGE)
        return value

    @root_validator(skip_on_failure=True)
    def check_empty_values(cls, values):
        if values is None:
            raise ValueError(EMPTY_FIELD_ERROR_MESSAGE)
        return values


class CharityProjectCreate(CharityProjectUpdate):
    """Схема для создания проекта пожертвований."""
    name: str = Field(
        ...,
        min_length=MIN_LENGTH_PROJECT_NAME,
        max_length=MAX_LENGTH_PROJECT_NAME,
        title=NAME,
        description=NAME_DESCRIPTION
    )
    description: str = Field(
        ...,
        min_length=MIN_LENGTH_PROJECT_DESCRIPTION,
        title=DESCRIPTION,
        description=DESCRIPTION_SPECIFY_FOR_PROJECT
    )
    full_amount: PositiveInt = Field(
        ...,
        title=FULL_AMOUNT,
        description=FULL_AMOUNT_DESCRIPTION
    )
    invested_amount: PositiveInt = Field(
        default=DEFAULT_INVESTED_AMOUNT,
        title=INVESTED_AMOUNT,
    )


class CharityProjectDB(CharityProjectBase):
    """Схема для описания объекта проекта пожертвований, полученного из БД."""
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: dt
    close_date: Optional[dt]

    class Config:
        orm_mode = True
