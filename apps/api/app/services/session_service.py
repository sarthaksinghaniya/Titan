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
                
                # Use astream to run the graph and publish events in real-time
                final_state = initial_state.copy()
                async for event in graph.astream(initial_state):
                    for node_name, node_output in event.items():
                        if not node_output or not isinstance(node_output, dict):
                            continue
                        # Update the final_state dictionary, merging list reducers
                        for key, val in node_output.items():
                            if val is None:
                                continue
                            if key in ("analyses", "debate_arguments", "opposition_attacks", "rebuttals", "votes"):
                                if not final_state.get(key):
                                    final_state[key] = []
                                # Avoid duplicating items already in the list
                                for item in val:
                                    if item not in final_state[key]:
                                        final_state[key].append(item)
                            elif key == "metadata" and "metadata" in final_state and isinstance(final_state["metadata"], dict):
                                final_state["metadata"] = {**final_state["metadata"], **val}
                            else:
                                final_state[key] = val

                        # Publish specific intermediate events to event_bus
                        if "current_phase" in node_output:
                            await self.event_bus.publish(project_id, "phase_changed", {
                                "project_id": project_id,
                                "new_phase": node_output["current_phase"]
                            })

                        if node_name == "minister_analysis":
                            analyses = node_output.get("analyses", [])
                            for a in analyses:
                                await self.event_bus.publish(project_id, "minister_analysis", {
                                    "project_id": project_id,
                                    "analysis": a
                                })
                        elif node_name == "debate_round":
                            args = node_output.get("debate_arguments", [])
                            for arg in args:
                                await self.event_bus.publish(project_id, "debate_argument", {
                                    "project_id": project_id,
                                    "argument": arg
                                })
                        elif node_name == "opposition_attack":
                            attacks = node_output.get("opposition_attacks", [])
                            for attack in attacks:
                                await self.event_bus.publish(project_id, "opposition_attack", {
                                    "project_id": project_id,
                                    "argument": attack
                                })
                        elif node_name == "rebuttal_round":
                            rebuttals = node_output.get("rebuttals", [])
                            for rebuttal in rebuttals:
                                await self.event_bus.publish(project_id, "rebuttal", {
                                    "project_id": project_id,
                                    "argument": rebuttal
                                })
                        elif node_name == "minister_vote":
                            votes = node_output.get("votes", [])
                            for vote in votes:
                                await self.event_bus.publish(project_id, "minister_vote", {
                                    "project_id": project_id,
                                    "vote": vote
                                })
                        elif node_name == "simulation_phase":
                            sims = node_output.get("simulation_results", [])
                            if sims:
                                await self.event_bus.publish(project_id, "simulation_complete", {
                                    "project_id": project_id,
                                    "results": sims
                                })

                if final_state.get("error") or final_state.get("current_phase") == "failed":
                    error_msg = final_state.get("error", "Unknown failure")
                    await self._update_status(db, project_id, ProjectStatus.FAILED, error=error_msg)
                    await self.event_bus.publish(project_id, "error", {"message": error_msg})
                else:
                    await self._persist_state(db, project_id, final_state)
                    await self._update_status(db, project_id, ProjectStatus.COMPLETED, completed=True)
                    final_report_payload = final_state.get("final_report", {})
                    bs_results = final_state.get("black_swan_results", {})
                    if bs_results:
                        final_report_payload.update(bs_results)

                    await self.event_bus.publish(project_id, "session_complete", {
                        "project_id": project_id,
                        "final_report": final_report_payload,
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

        # 4. Simulations
        for s in state.get("simulation_results", []):
            risk_val = s.get("risk_level", "medium").lower()
            try:
                risk_enum = RiskLevel(risk_val)
            except ValueError:
                risk_enum = RiskLevel.MEDIUM

            sim = Simulation(
                id=uuid.uuid4(), project_id=pid, option_name=s.get("option_name", ""),
                option_description=s.get("future_name", ""), # using description field for future designation
                economic_score=float(s.get("economic_score", 50.0)),
                social_score=float(s.get("social_score", 50.0)),
                environmental_score=float(s.get("environment_score", 50.0)),
                feasibility_score=float(s.get("feasibility_score", 50.0)),
                composite_score=float(s.get("composite_score", 50.0)),
                risk_level=risk_enum,
                time_to_implement_months=int(s.get("time_to_implement_months", 12)),
                cost_estimate_usd_millions=float(s.get("cost_estimate_usd_millions", 0.0)),
                projected_population_impact=float(s.get("projected_population_impact", 0.0)),
                key_risks=s.get("key_risks", []),
                key_benefits=s.get("key_benefits", []),
                scenario_data=s.get("scenario_data", {})
            )
            db.add(sim)

        # 5. Final Report & Black Swan
        fr = state.get("final_report")
        bs = state.get("black_swan_results", {})
        
        if fr:
            report = FinalReport(
                id=uuid.uuid4(), project_id=pid, chosen_option=fr.get("chosen_option", ""),
                executive_summary=fr.get("executive_summary", ""), overall_rationale=fr.get("rationale", ""),
                confidence_score=float(fr.get("confidence_score", 0.0)),
                implementation_steps=fr.get("implementation_steps", []), success_metrics=fr.get("success_metrics", []),
                risks_and_mitigations=fr.get("risks_and_mitigations", {}), expected_outcomes=fr.get("expected_outcomes", []),
                review_timeline=fr.get("review_timeline", ""), total_votes=fr.get("vote_breakdown", {}).get("total_votes", 0),
                winning_votes=0, vote_percentage=0.0, consensus_level=fr.get("consensus_level", "moderate"),
                black_swan_crisis=bs.get("black_swan_crisis"),
                black_swan_impact=bs.get("black_swan_impact"),
                resilience_score=bs.get("resilience_score"),
                model_used="gemini-1.5-pro"
            )
            db.add(report)

        await db.commit()
