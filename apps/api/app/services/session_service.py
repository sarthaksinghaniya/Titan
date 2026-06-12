"""
Session Service — orchestrates project lifecycle and agent graph execution.
Uses the new GovernanceState schema (project_id, not session_id).
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.session import (
    Project, ProjectStatus, AgentRole, RiskLevel,
    Agent, Debate, Vote, Simulation, FinalReport
)
from app.services.event_bus import EventBus
from app.agents.graph import create_governance_graph
from app.agents.state import make_initial_state, GovernanceState

logger = structlog.get_logger(__name__)


class SessionService:
    def __init__(self, db: AsyncSession, event_bus: EventBus) -> None:
        self.db = db
        self.event_bus = event_bus

    async def create_project(self, problem: str, context: Optional[str] = None) -> Project:
        """Create a new project record in the database."""
        # Auto-generate a short title from the problem
        title = problem[:80].rstrip() + ("…" if len(problem) > 80 else "")

        project = Project(
            id=uuid.uuid4(),
            title=title,
            problem=problem,
            context=context,
            status=ProjectStatus.PENDING,
            metadata_={},
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        logger.info("Project created", project_id=str(project.id))
        return project

    # Backwards-compatible alias
    async def create_session(self, problem: str, context: Optional[str] = None):
        return await self.create_project(problem, context)

    async def run_agent_graph(self, project_id: str) -> None:
        """
        Run the full LangGraph governance pipeline for a project.
        Uses a fresh DB session (background task context).
        Publishes SSE events at each phase transition.
        """
        async with AsyncSessionLocal() as db:
            try:
                await self._update_status(db, project_id, ProjectStatus.ANALYZING)
                await self.event_bus.publish(project_id, "session_started", {"project_id": project_id})

                # Fetch problem from DB
                result = await db.execute(select(Project).where(Project.id == uuid.UUID(project_id)))
                project = result.scalar_one()

                # Build initial state
                initial_state = make_initial_state(
                    project_id=project_id,
                    problem=project.problem,
                    context=project.context or "",
                )

                # Compile and run the graph
                graph = create_governance_graph()
                final_state = await graph.ainvoke(initial_state)

                if final_state.get("error") or final_state.get("current_phase") == "failed":
                    error_msg = final_state.get("error", "Unknown failure")
                    await self._update_status(db, project_id, ProjectStatus.FAILED, error=error_msg)
                    await self.event_bus.publish(project_id, "error", {"message": error_msg})
                else:
                    await self._persist_state(db, project_id, final_state)
                    await self._update_status(db, project_id, ProjectStatus.COMPLETED, completed=True)
                    await self.event_bus.publish(project_id, "session_complete", {
                        "project_id": project_id,
                        "final_report": final_state.get("final_report"),
                    })

            except Exception as e:
                logger.error("Agent graph failed", project_id=project_id, error=str(e))
                await self._update_status(db, project_id, ProjectStatus.FAILED, error=str(e))
                await self.event_bus.publish(project_id, "error", {"message": str(e)})
            finally:
                await self.event_bus.close_session(project_id)

    async def _update_status(
        self,
        db: AsyncSession,
        project_id: str,
        status: ProjectStatus,
        error: Optional[str] = None,
        completed: bool = False,
    ) -> None:
        result = await db.execute(select(Project).where(Project.id == uuid.UUID(project_id)))
        project = result.scalar_one()
        project.status = status
        if error:
            project.error_message = error
        if completed:
            project.completed_at = datetime.now(tz=timezone.utc)
        await db.commit()

    async def _persist_state(self, db: AsyncSession, project_id: str, state: GovernanceState) -> None:
        """Persist all graph outputs to the database."""
        pid = uuid.UUID(project_id)
        
        # 1. Agents (Analyses)
        db_agents = {}
        for a in state.get("analyses", []):
            role = AgentRole(a["agent_role"])
            agent = Agent(
                id=uuid.uuid4(), project_id=pid, role=role,
                model_used="gemini-1.5-flash", analysis=a.get("situation_assessment", ""),
                key_points=a.get("key_findings", []), proposed_solutions=a.get("proposed_solutions", []),
                concerns=a.get("red_lines", []), tokens_used=0, processing_ms=a.get("_elapsed_ms", 0)
            )
            db.add(agent)
            db_agents[role.value] = agent
        await db.flush()

        # 2. Debates (Presentations, Arguments, Attacks, Rebuttals)
        all_debates = (
            state.get("debate_arguments", []) +
            state.get("opposition_attacks", []) +
            state.get("rebuttals", [])
        )
        for d in all_debates:
            role_str = d.get("agent_role")
            if role_str not in db_agents:
                continue
            debate = Debate(
                id=uuid.uuid4(), project_id=pid, agent_id=db_agents[role_str].id,
                round_number=d.get("round_number", 1), phase=d.get("phase", "debate"),
                argument=d.get("argument", ""), supporting_agents=d.get("defending_positions", []),
                opposing_agents=d.get("attacking_roles", []), word_count=d.get("word_count", 0)
            )
            db.add(debate)

        # 3. Votes
        for v in state.get("votes", []):
            role_str = v.get("agent_role")
            if role_str not in db_agents:
                continue
            vote = Vote(
                id=uuid.uuid4(), project_id=pid, agent_id=db_agents[role_str].id,
                voted_option=v.get("voted_option", ""), confidence_score=v.get("confidence_score", 0.0),
                justification=v.get("justification", "")
            )
            db.add(vote)

        # 4. Final Report
        fr = state.get("final_report")
        if fr:
            report = FinalReport(
                id=uuid.uuid4(), project_id=pid, chosen_option=fr.get("chosen_option", ""),
                executive_summary=fr.get("executive_summary", ""), overall_rationale=fr.get("rationale", ""),
                implementation_steps=fr.get("implementation_steps", []), success_metrics=fr.get("success_metrics", []),
                risks_and_mitigations=fr.get("risks_and_mitigations", {}), expected_outcomes=fr.get("expected_outcomes", []),
                review_timeline=fr.get("review_timeline", ""), total_votes=fr.get("vote_breakdown", {}).get("total_votes", 0),
                winning_votes=0, vote_percentage=0.0, consensus_level=fr.get("consensus_level", "moderate"),
                model_used="gemini-1.5-pro"
            )
            db.add(report)

        await db.commit()
