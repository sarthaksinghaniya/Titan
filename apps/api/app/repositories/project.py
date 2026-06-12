"""Project repository combining all associated agent operations."""
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.session import (
    Project, Agent, Debate, Vote, Simulation, FinalReport
)
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self):
        super().__init__(Project)

    async def get_with_relations(self, db: AsyncSession, project_id: UUID | str) -> Optional[Project]:
        """Fetch a project with all its nested relationships eagerly loaded."""
        if isinstance(project_id, str):
            project_id = UUID(project_id)
        
        stmt = (
            select(Project)
            .options(
                selectinload(Project.agents),
                selectinload(Project.debates),
                selectinload(Project.votes),
                selectinload(Project.simulations),
                selectinload(Project.final_report)
            )
            .where(Project.id == project_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi_paginated(
        self, db: AsyncSession, *, page: int = 1, page_size: int = 20
    ) -> Tuple[list[Project], int]:
        """Get paginated projects ordered by created_at desc."""
        offset = (page - 1) * page_size
        
        # Count query
        count_stmt = select(func.count(Project.id))
        total = await db.scalar(count_stmt) or 0
        
        # Items query
        stmt = select(Project).order_by(Project.created_at.desc()).offset(offset).limit(page_size)
        result = await db.execute(stmt)
        items = list(result.scalars().all())
        
        return items, total

    # Factory methods for sub-models that bypass BaseRepository for bulk/special logic
    async def save_agents(self, db: AsyncSession, agents: list[Agent]) -> None:
        db.add_all(agents)
        await db.commit()

    async def save_debates(self, db: AsyncSession, debates: list[Debate]) -> None:
        db.add_all(debates)
        await db.commit()

    async def save_votes(self, db: AsyncSession, votes: list[Vote]) -> None:
        db.add_all(votes)
        await db.commit()

    async def save_simulations(self, db: AsyncSession, simulations: list[Simulation]) -> None:
        db.add_all(simulations)
        await db.commit()

    async def save_final_report(self, db: AsyncSession, report: FinalReport) -> None:
        db.add(report)
        await db.commit()

project_repo = ProjectRepository()
