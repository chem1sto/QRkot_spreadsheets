from sqlalchemy import Column, String, Text

from app.constants import MAX_LENGTH_PROJECT_NAME
from app.models import InvestingBaseModel


class CharityProject(InvestingBaseModel):
    """Модель проектов для пожертвований."""
    name = Column(
        String(MAX_LENGTH_PROJECT_NAME),
        unique=True,
        nullable=False
    )
    description = Column(Text, nullable=False)

    def __repr__(self):
        return (
            f'Название проекта: {self.name}. '
            f'{super().__repr__()}'
        )
