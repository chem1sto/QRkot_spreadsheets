from sqlalchemy import Column, Integer, Text, ForeignKey

from app.models.base import InvestingBaseModel


class Donation(InvestingBaseModel):
    """Модель для пожертвований пользователей."""
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)

    def __repr__(self):
        return (
            f'Пожертвование пользователя с id{self.user_id}. '
            f'{super().__repr__()} '
        )
