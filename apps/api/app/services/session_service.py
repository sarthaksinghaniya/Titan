"""
Session Service — orchestrates session lifecycle and agent graph execution.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.session import (
    Session, MinisterAnalysis, DebateRound, Vote, SimulationResult, FinalPolicy,
    SessionStatus, MinisterRole,
)
from app.services.event_bus import EventBus
from app.agents.graph import create_governance_graph
from app.schemas.session import (
    MinisterAnalysisSchema, DebateRoundSchema, VoteSchema,
    SimulationResultSchema, FinalPolicySchema,
)

logger = structlog.get_logger(__name__)


class SessionService:
    def __init__(self, db: AsyncSession, event_bus: EventBus) -> None:
        self.db = db
        self.event_bus = event_bus

    async def create_session(self, problem: str, context: Optional[str] = None) -> Session:
        """Create a new session record in the database."""
        session = Session(
            id=uuid.uuid4(),
            problem=problem,
            context=context,
            status=SessionStatus.PENDING,
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def run_agent_graph(self, session_id: str) -> None:
        """
        Run the full LangGraph agent pipeline for a session.
        Uses a fresh DB session (background task context).
        """
        async with AsyncSessionLocal() as db:
            try:
                await self._update_status(db, session_id, SessionStatus.ANALYZING)
                await self.event_bus.publish(session_id, "session_started", {"session_id": session_id})

                graph = create_governance_graph(db, self.event_bus, session_id)
                session_result = await db.execute(select(Session).where(Session.id == uuid.UUID(session_id)))
                session = session_result.scalar_one()

                final_state = await graph.ainvoke({
                    "session_id": session_id,
                    "problem": session.problem,
                    "context": session.context or "",
                    "analyses": [],
                    "debate_rounds": [],
                    "votes": [],
                    "simulation_results": [],
                    "final_policy": None,
                    "current_phase": "analyzing",
                    "error": None,
                })

                if final_state.get("error"):
                    await self._update_status(db, session_id, SessionStatus.FAILED, error=final_state["error"])
                    await self.event_bus.publish(session_id, "error", {"message": final_state["error"]})
                else:
                    await self._update_status(db, session_id, SessionStatus.COMPLETED, completed=True)
                    await self.event_bus.publish(session_id, "session_complete", {"session_id": session_id})

            except Exception as e:
                logger.error("Agent graph failed", session_id=session_id, error=str(e))
                await self._update_status(db, session_id, SessionStatus.FAILED, error=str(e))
                await self.event_bus.publish(session_id, "error", {"message": str(e)})
            finally:
                await self.event_bus.close_session(session_id)

    async def _update_status(
        self,
        db: AsyncSession,
        session_id: str,
        status: SessionStatus,
        error: Optional[str] = None,
        completed: bool = False,
    ) -> None:
        result = await db.execute(select(Session).where(Session.id == uuid.UUID(session_id)))
        session = result.scalar_one()
        session.status = status
        if error:
            session.error_message = error
        if completed:
            session.completed_at = datetime.now(tz=timezone.utc)
        await db.commit()
