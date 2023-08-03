from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import CRUDBase
from app.models import CharityProject


class CRUDCharityProject(CRUDBase):
    """Класс для CRUD-операций с проектом пожертвований."""
    @staticmethod
    async def get_project_id_by_name(
            charity_project_name: str,
            session: AsyncSession,
    ) -> Optional[int]:
        """Получение проекта пожертвований по его названию."""
        charity_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == charity_project_name
            )
        )
        charity_project_id = charity_project_id.scalars().first()
        return charity_project_id

    @staticmethod
    async def get_projects_by_completion_rate(
            session: AsyncSession
    ) -> List[CharityProject]:
        """
        Получение завершенных проектов,
        отсортированных по скорости сбора.
        """
        closed_projects = await session.execute(
            select(
                CharityProject.name,
                CharityProject.description,
                CharityProject.create_date,
                CharityProject.close_date
            ).where(
                CharityProject.fully_invested.is_(True)
            ).order_by(
                CharityProject.close_date - CharityProject.create_date
            )
        )
        return closed_projects.all()


charity_project_crud = CRUDCharityProject(CharityProject)
