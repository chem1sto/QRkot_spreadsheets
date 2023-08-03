from datetime import datetime as dt

from typing import List
from app.models import InvestingBaseModel


def investing_process(
    target: InvestingBaseModel,
    sources: List[InvestingBaseModel]
) -> List[InvestingBaseModel]:
    """Функция для реализации процесса «инвестирования»."""
    modified = []
    for source in sources:
        investing_amount = min(
            target.full_amount - target.invested_amount,
            source.full_amount - source.invested_amount
        )
        if investing_amount == 0:
            break
        for invest in target, source:
            invest.invested_amount += investing_amount
            if invest.full_amount == invest.invested_amount:
                invest.fully_invested = True
                invest.close_date = dt.now()
        modified.append(source)
    return modified
