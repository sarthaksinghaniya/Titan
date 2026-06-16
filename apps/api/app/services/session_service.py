"""
Session Service — orchestrates project lifecycle and agent graph execution.
Uses the new GovernanceState schema (project_id, not session_id).

Hardening changes (Step 7.1):
- Added asyncio.sleep(0.1) after publishing session_started so the SSE
  subscriber has time to attach before the first real event fires.
- close_session is called in the finally block AFTER all events are
  published, ensuring no events are missed.
- black_swan_results is safely accessed via .get() with a fallback.
- Every exception path publishes an "error" event before closing the
  session, guaranteeing the browser always receives a terminal event.
- _persist_state failures are isolated so the completion event still
  fires even if DB write partially fails.
- Per-node duplicate detection now uses a set of (key, id) tuples
  so list reducers with Annotated[List, operator.add] don't emit
  duplicate SSE events when the graph merges parallel fan-outs.
"""
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Set, Tuple

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

        Reliability guarantees:
        - session_started is published first; a short yield gives the
          SSE subscriber time to attach before subsequent events fire.
        - close_session is always called in the finally block so the
          browser EventSource is never left hanging.
        - Any unhandled exception emits an "error" SSE event so the
          browser always receives a terminal signal.
        - Duplicate SSE events are suppressed using an emitted-items set.
        """
        # Track already-emitted list items to prevent duplicate SSE events
        # when LangGraph's Annotated[List, operator.add] merges fan-outs.
        emitted: Dict[str, Set[str]] = {
            "analyses": set(),
            "debate_arguments": set(),
            "opposition_attacks": set(),
            "rebuttals": set(),
            "votes": set(),
        }

        async with AsyncSessionLocal() as db:
            try:
                await self._update_status(db, project_id, ProjectStatus.ANALYZING)

                # Publish the started event, then yield to the event loop so the
                # SSE subscriber (which was registered just before the background
                # task started) has time to process its first queue.get() call.
                await self.event_bus.publish(
                    project_id, "session_started", {"project_id": project_id}
                )
                await asyncio.sleep(0.05)  # Brief yield — not a busy-wait

                # Fetch problem from DB
                result = await db.execute(
                    select(Project).where(Project.id == uuid.UUID(project_id))
                )
                project = result.scalar_one()

                # Build initial state
                initial_state = make_initial_state(
                    project_id=project_id,
                    problem=project.problem,
                    context=project.context or "",
                )

                # Compile and stream the graph
                graph = create_governance_graph()
                final_state: GovernanceState = initial_state.copy()  # type: ignore[assignment]

                async for node_event in graph.astream(initial_state):
                    for node_name, node_output in node_event.items():
                        if not node_output or not isinstance(node_output, dict):
                            continue

                        # ── Merge output into final_state ─────────────────
                        for key, val in node_output.items():
                            if val is None:
                                continue
                            if key in (
                                "analyses", "debate_arguments",
                                "opposition_attacks", "rebuttals", "votes",
                            ):
                                if not final_state.get(key):
                                    final_state[key] = []  # type: ignore[literal-required]
                                for item in val:
                                    if item not in final_state[key]:  # type: ignore[operator]
                                        final_state[key].append(item)  # type: ignore[literal-required]
                            elif (
                                key == "metadata"
                                and isinstance(final_state.get("metadata"), dict)
                            ):
                                final_state["metadata"] = {
                                    **final_state["metadata"],
                                    **val,
                                }
                            else:
                                final_state[key] = val  # type: ignore[literal-required]

                        # ── Publish phase transitions ─────────────────────
                        if "current_phase" in node_output:
                            await self.event_bus.publish(
                                project_id,
                                "phase_changed",
                                {
                                    "project_id": project_id,
                                    "new_phase": node_output["current_phase"],
                                },
                            )

                        # ── Publish per-node intermediate events ──────────
                        await self._publish_node_events(
                            project_id, node_name, node_output, emitted
                        )

                # ── Terminal state handling ───────────────────────────────
                if final_state.get("error") or final_state.get("current_phase") == "failed":
                    error_msg = final_state.get("error") or "Unknown failure"
                    await self._update_status(
                        db, project_id, ProjectStatus.FAILED, error=error_msg
                    )
                    await self.event_bus.publish(
                        project_id, "error", {"message": error_msg}
                    )
                else:
                    # Persist state; isolate failures so completion fires either way
                    try:
                        await self._persist_state(db, project_id, final_state)
                    except Exception as persist_exc:
                        logger.error(
                            "State persist failed — completion event will still fire",
                            project_id=project_id,
                            error=str(persist_exc),
                        )

                    await self._update_status(
                        db, project_id, ProjectStatus.COMPLETED, completed=True
                    )

                    final_report_payload: Dict[str, Any] = dict(
                        final_state.get("final_report") or {}
                    )
                    bs_results: Dict[str, Any] = dict(
                        final_state.get("black_swan_results") or {}  # type: ignore[arg-type]
                    )
                    if bs_results:
                        final_report_payload.update(bs_results)

                    # ─── Telemetry: Graph Runtime & Memory ────────────
                    runtime_ms = int((datetime.now(timezone.utc) - project.created_at).total_seconds() * 1000)
                    import psutil
                    import os
                    process = psutil.Process(os.getpid())
                    mem_info = process.memory_info()
                    logger.info("Graph execution completed", 
                                project_id=project_id, 
                                graph_runtime_ms=runtime_ms,
                                memory_usage_mb=round(mem_info.rss / (1024 * 1024), 2))

                    await self.event_bus.publish(
                        project_id,
                        "session_complete",
                        {
                            "project_id": project_id,
                            "final_report": final_report_payload,
                        },
                    )

            except Exception as exc:
                logger.error(
                    "Agent graph failed",
                    project_id=project_id,
                    error=str(exc),
                    exc_info=True,
                )
                try:
                    await self._update_status(
                        db, project_id, ProjectStatus.FAILED, error=str(exc)
                    )
                except Exception:
                    pass  # Don't mask the original exception in logs

                # Always emit error event so browser receives terminal signal
                await self.event_bus.publish(
                    project_id, "error", {"message": str(exc)}
                )

            finally:
                # close_session sends the sentinel to all current subscribers.
                # Must be last so that all published events are enqueued first.
                await self.event_bus.close_session(project_id)

    # ──────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────

    async def _publish_node_events(
        self,
        project_id: str,
        node_name: str,
        node_output: Dict[str, Any],
        emitted: Dict[str, Set[str]],
    ) -> None:
        """Publish per-node SSE events, suppressing duplicates.

        Uses a fingerprint (repr) of each list item to detect items that
        have already been emitted in a previous stream tick — which can
        happen when LangGraph re-emits accumulated list state.
        """

        def _is_new(bucket: str, item: Any) -> bool:
            fp = repr(item)
            if fp in emitted.get(bucket, set()):
                return False
            emitted.setdefault(bucket, set()).add(fp)
            return True

        if node_name == "minister_analysis":
            for analysis in node_output.get("analyses", []):
                if _is_new("analyses", analysis):
                    await self.event_bus.publish(
                        project_id,
                        "minister_analysis",
                        {"project_id": project_id, "analysis": analysis},
                    )

        elif node_name == "debate_round":
            for arg in node_output.get("debate_arguments", []):
                if _is_new("debate_arguments", arg):
                    await self.event_bus.publish(
                        project_id,
                        "debate_argument",
                        {"project_id": project_id, "argument": arg},
                    )

        elif node_name == "opposition_attack":
            for attack in node_output.get("opposition_attacks", []):
                if _is_new("opposition_attacks", attack):
                    await self.event_bus.publish(
                        project_id,
                        "opposition_attack",
                        {"project_id": project_id, "argument": attack},
                    )

        elif node_name == "rebuttal_round":
            for rebuttal in node_output.get("rebuttals", []):
                if _is_new("rebuttals", rebuttal):
                    await self.event_bus.publish(
                        project_id,
                        "rebuttal",
                        {"project_id": project_id, "argument": rebuttal},
                    )

        elif node_name == "minister_vote":
            for vote in node_output.get("votes", []):
                if _is_new("votes", vote):
                    await self.event_bus.publish(
                        project_id,
                        "minister_vote",
                        {"project_id": project_id, "vote": vote},
                    )

        elif node_name == "simulation_phase":
            sims = node_output.get("simulation_results", [])
            if sims:
                await self.event_bus.publish(
                    project_id,
                    "simulation_complete",
                    {"project_id": project_id, "results": sims},
                )

    async def _update_status(
        self,
        db: AsyncSession,
        project_id: str,
        status: ProjectStatus,
        error: Optional[str] = None,
        completed: bool = False,
    ) -> None:
        result = await db.execute(
            select(Project).where(Project.id == uuid.UUID(project_id))
        )
        project = result.scalar_one()
        project.status = status
        if error:
            project.error_message = error
        if completed:
            project.completed_at = datetime.now(tz=timezone.utc)
        await db.commit()

    async def _persist_state(
        self, db: AsyncSession, project_id: str, state: GovernanceState
    ) -> None:
        """Persist all graph outputs to the database."""
        pid = uuid.UUID(project_id)

        # 1. Agents (Analyses)
        db_agents: Dict[str, Agent] = {}
        for a in state.get("analyses", []):
            role = AgentRole(a["agent_role"])
            agent = Agent(
                id=uuid.uuid4(),
                project_id=pid,
                role=role,
                model_used="gemini-1.5-flash",
                analysis=a.get("situation_assessment", ""),
                key_points=a.get("key_findings", []),
                proposed_solutions=a.get("proposed_solutions", []),
                concerns=a.get("red_lines", []),
                tokens_used=0,
                processing_ms=a.get("_elapsed_ms", 0),
            )
            db.add(agent)
            db_agents[role.value] = agent
        await db.flush()

        # 2. Debates (Arguments, Attacks, Rebuttals)
        all_debates = (
            state.get("debate_arguments", [])
            + state.get("opposition_attacks", [])
            + state.get("rebuttals", [])
        )
        for d in all_debates:
            role_str = d.get("agent_role")
            if role_str not in db_agents:
                continue
            debate = Debate(
                id=uuid.uuid4(),
                project_id=pid,
                agent_id=db_agents[role_str].id,
                round_number=d.get("round_number", 1),
                phase=d.get("phase", "debate"),
                argument=d.get("argument", ""),
                supporting_agents=d.get("defending_positions", []),
                opposing_agents=d.get("attacking_roles", []),
                word_count=d.get("word_count", 0),
            )
            db.add(debate)

        # 3. Votes
        for v in state.get("votes", []):
            role_str = v.get("agent_role")
            if role_str not in db_agents:
                continue
            vote = Vote(
                id=uuid.uuid4(),
                project_id=pid,
                agent_id=db_agents[role_str].id,
                voted_option=v.get("voted_option", ""),
                confidence_score=v.get("confidence_score", 0.0),
                justification=v.get("justification", ""),
            )
            db.add(vote)

        # 4. Simulations
        for s in state.get("simulation_results", []):  # type: ignore[attr-defined]
            risk_val = s.get("risk_level", "medium").lower()
            try:
                risk_enum = RiskLevel(risk_val)
            except ValueError:
                risk_enum = RiskLevel.MEDIUM

            sim = Simulation(
                id=uuid.uuid4(),
                project_id=pid,
                option_name=s.get("option_name", ""),
                option_description=s.get("future_name", ""),
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
                scenario_data=s.get("scenario_data", {}),
            )
            db.add(sim)

        # 5. Final Report & Black Swan
        fr = state.get("final_report")
        bs: Dict[str, Any] = dict(state.get("black_swan_results") or {})  # type: ignore[arg-type]

        if fr:
            report = FinalReport(
                id=uuid.uuid4(),
                project_id=pid,
                chosen_option=fr.get("chosen_option", ""),
                executive_summary=fr.get("executive_summary", ""),
                overall_rationale=fr.get("rationale", ""),
                confidence_score=float(fr.get("confidence_score", 0.0)),
                implementation_steps=fr.get("implementation_steps", []),
                success_metrics=fr.get("success_metrics", []),
                risks_and_mitigations=fr.get("risks_and_mitigations", {}),
                expected_outcomes=fr.get("expected_outcomes", []),
                review_timeline=fr.get("review_timeline", ""),
                total_votes=fr.get("vote_breakdown", {}).get("total_votes", 0),
                winning_votes=0,
                vote_percentage=0.0,
                consensus_level=fr.get("consensus_level", "moderate"),
                black_swan_crisis=bs.get("black_swan_crisis"),
                black_swan_impact=bs.get("black_swan_impact"),
                resilience_score=bs.get("resilience_score"),
                model_used="gemini-1.5-pro",
            )
            db.add(report)
            
            # Save contradiction fields to metadata to avoid schema migration
            result = await db.execute(select(Project).where(Project.id == pid))
            proj = result.scalar_one()
            meta_update = {}
            if "alternative_hypotheses" in fr:
                meta_update["alternative_hypotheses"] = fr["alternative_hypotheses"]
            if "requires_human_review" in fr:
                meta_update["requires_human_review"] = fr["requires_human_review"]
                
            # Lineage, version tracking, and timestamps
            meta_update["version"] = state.get("metadata", {}).get("version", 1)
            meta_update["parent_project_id"] = state.get("metadata", {}).get("parent_project_id", None)
            meta_update["verification_timestamps"] = {
                "started_at": state.get("metadata", {}).get("started_at"),
                "fact_check_completed": state.get("fact_check_report", {}).get("_timestamp"),
                "synthesis_completed": fr.get("_timestamp")
            }
            
            if meta_update:
                proj.metadata_ = {**(proj.metadata_ or {}), **meta_update}
                db.add(proj)

        # 6. Save Executive Reports to metadata
        exec_reports = state.get("executive_reports", [])
        if exec_reports:
            result = await db.execute(select(Project).where(Project.id == pid))
            proj = result.scalar_one()
            proj.metadata_ = {**(proj.metadata_ or {}), "executive_reports": exec_reports}
            db.add(proj)

        await db.commit()
