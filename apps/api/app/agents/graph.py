"""
LangGraph Governance Agent Graph
8-node multi-agent system: 6 Ministers → Debate → Vote → Simulate → Prime Minister
"""
import asyncio
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import GovernanceState
from app.agents.prompts import (
    MINISTER_SYSTEM_PROMPTS,
    DEBATE_PROMPT_TEMPLATE,
    VOTING_PROMPT_TEMPLATE,
    SIMULATION_PROMPT_TEMPLATE,
)
from app.core.config import settings
from app.services.event_bus import EventBus
from app.models.session import (
    MinisterAnalysis, DebateRound, Vote, SimulationResult, FinalPolicy,
    SessionStatus, MinisterRole, RiskLevel,
)

logger = structlog.get_logger(__name__)

MINISTER_ROLES = [
    "economic_minister",
    "technology_minister",
    "infrastructure_minister",
    "citizen_minister",
    "environment_minister",
    "opposition_minister",
]

MINISTER_TITLES = {
    "economic_minister": "Economic Minister",
    "technology_minister": "Technology Minister",
    "infrastructure_minister": "Infrastructure Minister",
    "citizen_minister": "Citizen Minister",
    "environment_minister": "Environment Minister",
    "opposition_minister": "Opposition Minister",
    "prime_minister": "Prime Minister",
    "simulation_agent": "Simulation Agent",
}

MINISTER_FOCUS = {
    "economic_minister": "GDP, employment, and fiscal sustainability",
    "technology_minister": "digital innovation and tech infrastructure",
    "infrastructure_minister": "physical infrastructure and implementation feasibility",
    "citizen_minister": "social equity and citizen welfare",
    "environment_minister": "environmental sustainability and climate impact",
    "opposition_minister": "critical risks and alternative perspectives",
}


def get_flash_llm() -> ChatGoogleGenerativeAI:
    """Gemini Flash — fast, for minister analyses and debates."""
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_FLASH_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=settings.GEMINI_TEMPERATURE,
        max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
    )


def get_pro_llm() -> ChatGoogleGenerativeAI:
    """Gemini Pro — high quality, for Prime Minister synthesis."""
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_PRO_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.5,  # Lower temp for more consistent final policy
        max_output_tokens=8192,
    )


def parse_json_from_response(text: str) -> Dict[str, Any]:
    """Extract and parse JSON from LLM response text."""
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON block
    json_match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    return {}


def extract_policy_options_from_analyses(analyses: List[Dict[str, Any]]) -> List[str]:
    """Extract distinct policy option names from minister analyses."""
    options = set()
    for analysis in analyses:
        proposed = analysis.get("proposed_solutions", [])
        for sol in proposed[:2]:  # Take top 2 from each minister
            if isinstance(sol, str) and len(sol) > 10:
                # Clean up to a short option name
                short = sol[:80].split(".")[0].strip()
                options.add(short)

    result = list(options)[: settings.MAX_SIMULATION_OPTIONS]
    if not result:
        result = ["Integrated Multi-Ministry Approach", "Technology-Led Reform", "Community-Centered Initiative"]
    return result


def parse_analysis_text(text: str, role: str) -> Dict[str, Any]:
    """Parse a minister's analysis text into structured data."""
    lines = text.split("\n")
    key_points = []
    proposed_solutions = []
    concerns = []

    current_section = None
    for line in lines:
        line = line.strip()
        if not line:
            continue

        line_lower = line.lower()
        if any(kw in line_lower for kw in ["key", "impact", "opportunity", "concern"]):
            current_section = "key_points"
        elif any(kw in line_lower for kw in ["proposed", "solution", "recommend", "option"]):
            current_section = "solutions"
        elif any(kw in line_lower for kw in ["concern", "risk", "challenge", "flaw"]):
            current_section = "concerns"

        if line.startswith(("-", "•", "*", "◦")) or (len(line) > 2 and line[1] == "."):
            content = line.lstrip("-•* ").lstrip("0123456789.").strip()
            if content:
                if current_section == "key_points":
                    key_points.append(content)
                elif current_section == "solutions":
                    proposed_solutions.append(content)
                elif current_section == "concerns":
                    concerns.append(content)
                else:
                    key_points.append(content)

    return {
        "analysis_text": text,
        "key_points": key_points[:5] or ["Analysis complete — see full text"],
        "proposed_solutions": proposed_solutions[:3] or ["See detailed analysis"],
        "concerns": concerns[:3] or ["See full analysis for concerns"],
    }


class GovernanceGraph:
    """The core LangGraph multi-agent governance system."""

    def __init__(self, db: AsyncSession, event_bus: EventBus, session_id: str) -> None:
        self.db = db
        self.event_bus = event_bus
        self.session_id = session_id

    async def _publish(self, event: str, data: Any) -> None:
        await self.event_bus.publish(self.session_id, event, data)

    async def _save_analysis(self, role: str, parsed: Dict[str, Any]) -> MinisterAnalysis:
        analysis = MinisterAnalysis(
            id=uuid.uuid4(),
            session_id=uuid.UUID(self.session_id),
            minister_role=MinisterRole(role),
            analysis_text=parsed["analysis_text"],
            key_points=parsed["key_points"],
            proposed_solutions=parsed["proposed_solutions"],
            concerns=parsed["concerns"],
        )
        self.db.add(analysis)
        await self.db.commit()
        await self.db.refresh(analysis)
        return analysis

    async def _save_debate_round(
        self, round_num: int, role: str, text: str
    ) -> DebateRound:
        debate = DebateRound(
            id=uuid.uuid4(),
            session_id=uuid.UUID(self.session_id),
            round_number=round_num,
            minister_role=MinisterRole(role),
            argument_text=text,
            supporting_ministers=[],
            opposing_ministers=[],
        )
        self.db.add(debate)
        await self.db.commit()
        return debate

    async def _save_vote(self, role: str, data: Dict[str, Any]) -> Vote:
        vote = Vote(
            id=uuid.uuid4(),
            session_id=uuid.UUID(self.session_id),
            minister_role=MinisterRole(role),
            voted_option=data.get("voted_option", "Integrated Approach"),
            confidence_score=float(data.get("confidence_score", 70)),
            justification=data.get("justification", "Based on ministerial assessment"),
        )
        self.db.add(vote)
        await self.db.commit()
        return vote

    async def _save_simulation(self, option_name: str, data: Dict[str, Any]) -> SimulationResult:
        risk_str = data.get("risk_level", "medium").lower()
        risk = RiskLevel(risk_str) if risk_str in [r.value for r in RiskLevel] else RiskLevel.MEDIUM
        sim = SimulationResult(
            id=uuid.uuid4(),
            session_id=uuid.UUID(self.session_id),
            option_name=option_name,
            economic_score=float(data.get("economic_score", 65)),
            social_score=float(data.get("social_score", 65)),
            environmental_score=float(data.get("environmental_score", 60)),
            feasibility_score=float(data.get("feasibility_score", 60)),
            risk_level=risk,
            time_to_implement_months=int(data.get("time_to_implement_months", 24)),
            cost_estimate_usd_millions=float(data.get("cost_estimate_usd_millions", 1000)),
            projected_population_impact=float(data.get("projected_population_impact", 10)),
            key_risks=data.get("key_risks", []),
            key_benefits=data.get("key_benefits", []),
        )
        self.db.add(sim)
        await self.db.commit()
        return sim

    async def _save_final_policy(self, data: Dict[str, Any]) -> FinalPolicy:
        policy = FinalPolicy(
            id=uuid.uuid4(),
            session_id=uuid.UUID(self.session_id),
            chosen_option=data.get("chosen_option", "Integrated Approach"),
            overall_rationale=data.get("overall_rationale", ""),
            implementation_steps=data.get("implementation_steps", []),
            success_metrics=data.get("success_metrics", []),
            risks_and_mitigations=data.get("risks_and_mitigations", {}),
            expected_outcomes=data.get("expected_outcomes", []),
            review_timeline=data.get("review_timeline", "Annual review"),
        )
        self.db.add(policy)
        await self.db.commit()
        return policy

    # ─── Phase Nodes ──────────────────────────────────────────

    async def analysis_phase(self, state: GovernanceState) -> GovernanceState:
        """Parallel analysis by all 6 ministers using Gemini Flash."""
        logger.info("Analysis phase starting", session_id=self.session_id)
        await self._publish("analysis_started", {"ministers": MINISTER_ROLES})

        llm = get_flash_llm()
        analyses = []

        async def analyze_minister(role: str) -> Dict[str, Any]:
            system_prompt = MINISTER_SYSTEM_PROMPTS[role]
            user_prompt = f"""Analyze the following societal problem from your ministerial perspective:

PROBLEM: {state['problem']}

{f'ADDITIONAL CONTEXT: {state["context"]}' if state.get('context') else ''}

Provide a comprehensive ministerial analysis following your designated format."""

            try:
                await self._publish("analysis_started", {"minister_role": role})
                response = await llm.ainvoke([
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ])
                text = response.content
                parsed = parse_analysis_text(str(text), role)

                db_analysis = await self._save_analysis(role, parsed)
                analysis_dict = {
                    "id": str(db_analysis.id),
                    "minister_role": role,
                    **parsed,
                    "created_at": db_analysis.created_at.isoformat(),
                }

                await self._publish("analysis_complete", {
                    "minister_role": role,
                    "is_complete": True,
                    "analysis": analysis_dict,
                })

                return analysis_dict
            except Exception as e:
                logger.error("Minister analysis failed", role=role, error=str(e))
                await self._publish("analysis_complete", {
                    "minister_role": role,
                    "is_complete": True,
                    "analysis": {"minister_role": role, "analysis_text": f"Analysis error: {e}", "key_points": [], "proposed_solutions": [], "concerns": []},
                })
                return {"minister_role": role, "analysis_text": str(e), "key_points": [], "proposed_solutions": [], "concerns": []}

        # Run all ministers in parallel
        tasks = [analyze_minister(role) for role in MINISTER_ROLES]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        analyses = list(results)

        state["analyses"] = analyses
        state["current_phase"] = "debating"
        return state

    async def debate_phase(self, state: GovernanceState) -> GovernanceState:
        """2 rounds of ministerial debate."""
        logger.info("Debate phase starting", session_id=self.session_id)
        await self._publish("debate_started", {"rounds": settings.DEBATE_ROUNDS})

        llm = get_flash_llm()
        all_debate_rounds = []

        analyses_summary = "\n\n".join([
            f"**{MINISTER_TITLES.get(a['minister_role'], a['minister_role'])}**: "
            f"{'; '.join(a.get('key_points', [])[:3])}"
            for a in state["analyses"]
        ])

        for round_num in range(1, settings.DEBATE_ROUNDS + 1):
            round_debates = []
            state["debate_round_number"] = round_num

            previous_context = ""
            if all_debate_rounds:
                previous_context = "Previous round arguments:\n" + "\n".join([
                    f"- {MINISTER_TITLES.get(d['minister_role'], '')} (Round {d['round_number']}): "
                    f"{d['argument_text'][:150]}..."
                    for d in all_debate_rounds[-6:]
                ])

            for role in MINISTER_ROLES:
                prompt = DEBATE_PROMPT_TEMPLATE.format(
                    minister_title=MINISTER_TITLES[role],
                    round_number=round_num,
                    problem=state["problem"],
                    analyses_summary=analyses_summary,
                    previous_debate_context=previous_context,
                    focus_area=MINISTER_FOCUS.get(role, "your area of expertise"),
                )

                try:
                    response = await llm.ainvoke([
                        SystemMessage(content=MINISTER_SYSTEM_PROMPTS[role]),
                        HumanMessage(content=prompt),
                    ])
                    argument_text = str(response.content)

                    db_round = await self._save_debate_round(round_num, role, argument_text)
                    debate_dict = {
                        "id": str(db_round.id),
                        "session_id": self.session_id,
                        "round_number": round_num,
                        "minister_role": role,
                        "argument_text": argument_text,
                        "supporting_ministers": [],
                        "opposing_ministers": [],
                        "created_at": db_round.created_at.isoformat() if db_round.created_at else "",
                    }

                    round_debates.append(debate_dict)
                    await self._publish("debate_argument", {
                        "round_number": round_num,
                        "minister_role": role,
                        "chunk": argument_text,
                        "is_complete": True,
                        "debate_round": debate_dict,
                    })

                except Exception as e:
                    logger.error("Debate round failed", role=role, round=round_num, error=str(e))

            all_debate_rounds.extend(round_debates)

        state["debate_rounds"] = all_debate_rounds
        state["policy_options"] = extract_policy_options_from_analyses(state["analyses"])
        state["current_phase"] = "voting"
        await self._publish("debate_complete", {"total_rounds": settings.DEBATE_ROUNDS})
        return state

    async def voting_phase(self, state: GovernanceState) -> GovernanceState:
        """Each minister casts a vote for the best policy option."""
        logger.info("Voting phase starting", session_id=self.session_id)
        await self._publish("voting_started", {"options": state["policy_options"]})

        llm = get_flash_llm()
        votes = []

        policy_options_text = "\n".join(
            f"{i+1}. {opt}" for i, opt in enumerate(state["policy_options"])
        )
        debate_summary = "\n".join([
            f"- Round {d['round_number']}, {MINISTER_TITLES.get(d['minister_role'], d['minister_role'])}: "
            f"{d['argument_text'][:100]}..."
            for d in state["debate_rounds"][-12:]
        ])

        for role in MINISTER_ROLES:
            prompt = VOTING_PROMPT_TEMPLATE.format(
                minister_title=MINISTER_TITLES[role],
                problem=state["problem"],
                policy_options=policy_options_text,
                debate_summary=debate_summary,
            )

            try:
                response = await llm.ainvoke([
                    SystemMessage(content=MINISTER_SYSTEM_PROMPTS[role]),
                    HumanMessage(content=prompt),
                ])
                parsed = parse_json_from_response(str(response.content))

                if not parsed:
                    parsed = {
                        "voted_option": state["policy_options"][0] if state["policy_options"] else "Integrated Approach",
                        "confidence_score": 65,
                        "justification": str(response.content)[:200],
                    }

                db_vote = await self._save_vote(role, parsed)
                vote_dict = {
                    "id": str(db_vote.id),
                    "session_id": self.session_id,
                    "minister_role": role,
                    "voted_option": db_vote.voted_option,
                    "confidence_score": db_vote.confidence_score,
                    "justification": db_vote.justification,
                    "created_at": db_vote.created_at.isoformat() if db_vote.created_at else "",
                }

                votes.append(vote_dict)
                await self._publish("vote_cast", {"minister_role": role, "vote": vote_dict})

            except Exception as e:
                logger.error("Vote failed", role=role, error=str(e))

        state["votes"] = votes
        state["current_phase"] = "simulating"
        await self._publish("voting_complete", {"vote_count": len(votes)})
        return state

    async def simulation_phase(self, state: GovernanceState) -> GovernanceState:
        """Simulate each policy option with Gemini Flash."""
        logger.info("Simulation phase starting", session_id=self.session_id)
        await self._publish("simulation_started", {"options": state["policy_options"]})

        llm = get_flash_llm()
        sim_results = []

        for option in state["policy_options"]:
            prompt = SIMULATION_PROMPT_TEMPLATE.format(
                problem=state["problem"],
                option_name=option,
                option_description=option,
            )

            try:
                response = await llm.ainvoke([
                    SystemMessage(content="You are the Simulation Agent. You run synthetic policy simulations and output structured JSON."),
                    HumanMessage(content=prompt),
                ])
                parsed = parse_json_from_response(str(response.content))

                db_sim = await self._save_simulation(option, parsed)
                sim_dict = {
                    "id": str(db_sim.id),
                    "session_id": self.session_id,
                    "option_name": option,
                    "economic_score": db_sim.economic_score,
                    "social_score": db_sim.social_score,
                    "environmental_score": db_sim.environmental_score,
                    "feasibility_score": db_sim.feasibility_score,
                    "risk_level": db_sim.risk_level.value,
                    "time_to_implement_months": db_sim.time_to_implement_months,
                    "cost_estimate_usd_millions": db_sim.cost_estimate_usd_millions,
                    "projected_population_impact": db_sim.projected_population_impact,
                    "key_risks": db_sim.key_risks,
                    "key_benefits": db_sim.key_benefits,
                    "created_at": db_sim.created_at.isoformat() if db_sim.created_at else "",
                }

                sim_results.append(sim_dict)
                await self._publish("simulation_result", {"option_name": option, "result": sim_dict})

            except Exception as e:
                logger.error("Simulation failed", option=option, error=str(e))

        state["simulation_results"] = sim_results
        state["current_phase"] = "synthesizing"
        await self._publish("simulation_complete", {"simulations_run": len(sim_results)})
        return state

    async def synthesis_phase(self, state: GovernanceState) -> GovernanceState:
        """Prime Minister synthesizes everything into final policy."""
        logger.info("Synthesis phase starting", session_id=self.session_id)
        await self._publish("synthesis_started", {})

        llm = get_pro_llm()

        # Build comprehensive context for PM
        analyses_summary = "\n\n".join([
            f"### {MINISTER_TITLES.get(a['minister_role'], a['minister_role'])}\n"
            f"Key points: {'; '.join(a.get('key_points', [])[:3])}\n"
            f"Proposed solutions: {'; '.join(a.get('proposed_solutions', [])[:2])}\n"
            f"Concerns: {'; '.join(a.get('concerns', [])[:2])}"
            for a in state["analyses"]
        ])

        votes_summary = "\n".join([
            f"- {MINISTER_TITLES.get(v['minister_role'], v['minister_role'])}: "
            f"Voted for '{v['voted_option']}' (confidence: {v['confidence_score']:.0f}%)"
            for v in state["votes"]
        ])

        sim_summary = "\n".join([
            f"- {s['option_name']}: Economic={s['economic_score']:.0f}, "
            f"Social={s['social_score']:.0f}, Environmental={s['environmental_score']:.0f}, "
            f"Feasibility={s['feasibility_score']:.0f}, Risk={s['risk_level']}"
            for s in state["simulation_results"]
        ])

        pm_prompt = f"""You are the Prime Minister making the final governance decision.

PROBLEM: {state['problem']}

MINISTERIAL ANALYSES:
{analyses_summary}

VOTING RESULTS:
{votes_summary}

SIMULATION RESULTS:
{sim_summary}

As Prime Minister, deliver the final policy decision. Be specific, actionable, and comprehensive.
Your response must be structured as JSON:
{{
  "chosen_option": "Name of the chosen policy option",
  "overall_rationale": "3-4 sentence explanation of why this option was chosen",
  "implementation_steps": [
    {{
      "phase": "Phase 1: Foundation (Months 1-6)",
      "duration": "6 months",
      "actions": ["Action 1", "Action 2", "Action 3"],
      "responsible_ministry": "Economic Ministry",
      "budget_allocation_percent": 25
    }}
  ],
  "success_metrics": ["Metric 1", "Metric 2", "Metric 3"],
  "risks_and_mitigations": {{
    "Risk 1": "Mitigation strategy 1",
    "Risk 2": "Mitigation strategy 2"
  }},
  "expected_outcomes": ["Outcome 1", "Outcome 2", "Outcome 3"],
  "review_timeline": "Quarterly reviews for 2 years, then annual"
}}"""

        try:
            response = await llm.ainvoke([
                SystemMessage(content=MINISTER_SYSTEM_PROMPTS["prime_minister"]),
                HumanMessage(content=pm_prompt),
            ])
            text = str(response.content)
            parsed = parse_json_from_response(text)

            if not parsed:
                parsed = {
                    "chosen_option": state["policy_options"][0] if state["policy_options"] else "Integrated Approach",
                    "overall_rationale": text[:500],
                    "implementation_steps": [],
                    "success_metrics": [],
                    "risks_and_mitigations": {},
                    "expected_outcomes": [],
                    "review_timeline": "Annual review",
                }

            db_policy = await self._save_final_policy(parsed)
            policy_dict = {
                "id": str(db_policy.id),
                "session_id": self.session_id,
                **parsed,
                "created_at": db_policy.created_at.isoformat() if db_policy.created_at else "",
            }

            state["final_policy"] = policy_dict
            state["current_phase"] = "completed"

            await self._publish("synthesis_complete", {"policy": policy_dict})

        except Exception as e:
            logger.error("Synthesis failed", error=str(e))
            state["error"] = str(e)

        return state


def create_governance_graph(
    db: AsyncSession, event_bus: EventBus, session_id: str
) -> Any:
    """Build and compile the LangGraph governance StateGraph."""
    gov = GovernanceGraph(db, event_bus, session_id)

    graph = StateGraph(GovernanceState)

    # Add all phase nodes
    graph.add_node("analysis", gov.analysis_phase)
    graph.add_node("debate", gov.debate_phase)
    graph.add_node("voting", gov.voting_phase)
    graph.add_node("simulation", gov.simulation_phase)
    graph.add_node("synthesis", gov.synthesis_phase)

    # Linear flow: analysis → debate → voting → simulation → synthesis → END
    graph.set_entry_point("analysis")
    graph.add_edge("analysis", "debate")
    graph.add_edge("debate", "voting")
    graph.add_edge("voting", "simulation")
    graph.add_edge("simulation", "synthesis")
    graph.add_edge("synthesis", END)

    return graph.compile()
