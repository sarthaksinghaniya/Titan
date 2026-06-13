"""
TITAN LangGraph Node Functions
==============================
Each function is a LangGraph node — takes GovernanceState, returns a
partial state dict (merged by the graph runtime).

Flow:
  input_validation
      │
      ├─ [Send × 6] ──► minister_analysis  (parallel fan-out)
      │
      ▼
  aggregate_analyses
      │
      ▼
  debate_round           (all 6 ministers sequentially — context-aware)
      │
      ▼
  opposition_attack      (OppositionMinister dedicated attack node)
      │
      ▼
  rebuttal_round         (5 ministers defend against the attack)
      │
      ▼
  extract_options        (derive policy options from debate corpus)
      │
      ├─ [Send × N] ──► minister_vote     (parallel fan-out)
      │
      ▼
  tally_votes
      │
      ▼
  prime_minister_synthesis
      │
      ▼
  END
"""
from __future__ import annotations

import asyncio
import json
import uuid
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import Send

from app.agents.state import GovernanceState, MinisterOutput, DebateArgument, VoteRecord
from app.agents.ministers import CABINET, PRIME_MINISTER, MINISTER_REGISTRY, SIMULATION_AGENT, OppositionMinister
from app.core.config import settings
from app.services.event_bus import EventBus

logger = structlog.get_logger(__name__)


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def _ts() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _build_llm_pro() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_PRO_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.4,
        max_output_tokens=8192,
    )


# ══════════════════════════════════════════════════════════════
# NODE 1 — INPUT VALIDATION
# Entry point: validates problem, initialises metadata
# ══════════════════════════════════════════════════════════════

async def node_input_validation(state: GovernanceState) -> Dict[str, Any]:
    """
    Validates the incoming problem and seeds metadata.
    Returns a partial-state update dict.
    """
    problem = (state.get("problem") or "").strip()
    if not problem or len(problem) < 20:
        return {"error": "Problem statement too short (minimum 20 characters)", "current_phase": "failed"}

    logger.info("Input validated", project_id=state["project_id"], length=len(problem))
    return {
        "current_phase": "analyzing",
        "metadata": {
            "started_at": _ts(),
            "problem_length": len(problem),
            "cabinet_size": len(CABINET),
        },
    }


# ══════════════════════════════════════════════════════════════
# NODE 2 — MINISTER ANALYSIS  (fan-out target)
# Called once per minister via Send()
# ══════════════════════════════════════════════════════════════

async def node_minister_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invoked by Send() for each minister.
    payload = {"project_id":..., "problem":..., "context":..., "role":...}
    Returns partial state with one analysis appended.
    """
    role    = payload["role"]
    problem = payload["problem"]
    context = payload.get("context", "")

    minister = MINISTER_REGISTRY.get(role)
    if not minister:
        logger.error("Unknown minister role", role=role)
        return {"analyses": []}

    logger.info("Minister analyzing", role=role)
    result = await minister.analyze(problem, context)
    result["_timestamp"] = _ts()
    
    # Also record this as a 'presentation' phase debate argument for the history
    presentation = {
        "agent_role": role,
        "round_number": 0,
        "phase": "presentation",
        "argument": f"Situation Assessment: {result.get('situation_assessment', '')}\n\nKey Findings: {', '.join(result.get('key_findings', []))}\n\nProposed Solutions: {', '.join(result.get('proposed_solutions', []))}",
        "attacking_roles": [],
        "defending_positions": [],
        "concessions": [],
        "new_evidence": [],
        "word_count": len(result.get("situation_assessment", "").split()),
        "_timestamp": result["_timestamp"]
    }

    logger.info("Minister analysis done", role=role, confidence=result.get("confidence"))
    return {
        "analyses": [result],
        "debate_arguments": [presentation]
    }


# ══════════════════════════════════════════════════════════════
# ROUTER — fan-out to all 6 ministers
# ══════════════════════════════════════════════════════════════

def route_to_ministers(state: GovernanceState) -> List[Send]:
    """
    Emits one Send per cabinet minister — runs all 6 in parallel.
    """
    return [
        Send("minister_analysis", {
            "project_id": state["project_id"],
            "problem":    state["problem"],
            "context":    state.get("context", ""),
            "role":       minister.role,
        })
        for minister in CABINET
    ]


# ══════════════════════════════════════════════════════════════
# NODE 3 — AGGREGATE ANALYSES
# Collects parallel fan-out results, extracts policy options
# ══════════════════════════════════════════════════════════════

async def node_aggregate_analyses(state: GovernanceState) -> Dict[str, Any]:
    """
    After all 6 parallel analysis nodes complete, aggregate and
    extract candidate policy options from proposed_solutions.
    """
    analyses = state.get("analyses", [])
    logger.info("Aggregating analyses", count=len(analyses))

    # Derive policy options from minister proposals
    seen: set[str] = set()
    options: List[str] = []
    for a in analyses:
        for sol in a.get("proposed_solutions", [])[:2]:
            short = str(sol)[:100].split(".")[0].strip()
            if short and short not in seen and len(short) > 15:
                seen.add(short)
                options.append(short)

    options = options[: settings.MAX_SIMULATION_OPTIONS] or [
        "Integrated Multi-Ministry Reform",
        "Technology-Led Transformation",
        "Community-Centered Development",
    ]

    logger.info("Policy options extracted", count=len(options), options=options)
    return {
        "current_phase": "debating",
        "policy_options": options,
    }


# ══════════════════════════════════════════════════════════════
# NODE 4 — DEBATE ROUND (Round 1)
# All 6 ministers debate sequentially so each can see prior args
# ══════════════════════════════════════════════════════════════

async def node_debate_round(state: GovernanceState) -> Dict[str, Any]:
    """
    Round 1 debate — each minister argues based on all analyses.
    Sequential so later speakers can reference earlier arguments.
    """
    logger.info("Debate round 1 starting")
    analyses  = state.get("analyses", [])
    problem   = state["problem"]
    arguments: List[DebateArgument] = []

    for minister in CABINET:
        if isinstance(minister, OppositionMinister):
            continue    # Opposition Minister gets dedicated attack node

        result = await minister.debate(
            problem=problem,
            all_analyses=analyses,
            round_number=1,
            phase="debate",
            prior_arguments=arguments,
        )
        result["_timestamp"] = _ts()
        arguments.append(result)
        logger.info("Debate argument recorded", role=minister.role, words=result.get("word_count", 0))

    return {"debate_arguments": arguments}


# ══════════════════════════════════════════════════════════════
# NODE 5 — OPPOSITION ATTACK
# OppositionMinister dedicates full output to attacking proposals
# ══════════════════════════════════════════════════════════════

async def node_opposition_attack(state: GovernanceState) -> Dict[str, Any]:
    """
    Dedicated Opposition Minister attack node.
    Targets the strongest proposals from the debate and analyses.
    """
    logger.info("Opposition attack phase starting")
    problem         = state["problem"]
    analyses        = state.get("analyses", [])
    debate_args     = state.get("debate_arguments", [])

    opposition = MINISTER_REGISTRY["opposition_minister"]
    result = await opposition.debate(
        problem=problem,
        all_analyses=analyses,
        round_number=1,
        phase="opposition_attack",
        prior_arguments=debate_args,
    )
    result["_timestamp"] = _ts()

    logger.info("Opposition attack complete", words=result.get("word_count", 0))
    return {"opposition_attacks": [result]}


# ══════════════════════════════════════════════════════════════
# NODE 6 — REBUTTAL ROUND (Round 2)
# 5 ministers respond to the Opposition attack
# ══════════════════════════════════════════════════════════════

async def node_rebuttal_round(state: GovernanceState) -> Dict[str, Any]:
    """
    Round 2 rebuttals — each minister defends their position
    against the Opposition's attack. Parallel since they don't
    depend on each other's rebuttals.
    """
    logger.info("Rebuttal round starting")
    problem          = state["problem"]
    analyses         = state.get("analyses", [])
    prior_arguments  = (
        state.get("debate_arguments", [])
        + state.get("opposition_attacks", [])
    )

    async def rebuttal(minister) -> DebateArgument:
        if isinstance(minister, OppositionMinister):
            return None                     # Opposition doesn't rebut itself
        result = await minister.debate(
            problem=problem,
            all_analyses=analyses,
            round_number=2,
            phase="rebuttal",
            prior_arguments=prior_arguments,
        )
        result["_timestamp"] = _ts()
        return result

    results = await asyncio.gather(
        *[rebuttal(m) for m in CABINET],
        return_exceptions=False,
    )
    rebuttals = [r for r in results if r is not None]

    logger.info("Rebuttals complete", count=len(rebuttals))
    return {"rebuttals": rebuttals, "current_phase": "voting"}


# ══════════════════════════════════════════════════════════════
# NODE 7 — MINISTER VOTE  (fan-out target)
# Called once per minister via Send()
# ══════════════════════════════════════════════════════════════

async def node_minister_vote(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Invoked by Send() for each minister.
    payload = {"project_id":..., "problem":..., "policy_options":...,
               "analyses":..., "all_debates":..., "role":...}
    """
    role           = payload["role"]
    problem        = payload["problem"]
    policy_options = payload["policy_options"]
    analyses       = payload["analyses"]
    all_debates    = payload["all_debates"]

    minister = MINISTER_REGISTRY.get(role)
    if not minister:
        return {"votes": []}

    logger.info("Minister voting", role=role)
    result = await minister.vote(
        problem=problem,
        policy_options=policy_options,
        all_analyses=analyses,
        all_debates=all_debates,
    )
    result["_timestamp"] = _ts()

    logger.info("Vote cast", role=role, option=result.get("voted_option"), confidence=result.get("confidence_score"))
    return {"votes": [result]}              # Annotated reducer appends


# ══════════════════════════════════════════════════════════════
# ROUTER — fan-out to all ministers for voting
# ══════════════════════════════════════════════════════════════

def route_to_voting(state: GovernanceState) -> List[Send]:
    """Emits one Send per minister — all vote in parallel."""
    all_debates = (
        state.get("debate_arguments", [])
        + state.get("opposition_attacks", [])
        + state.get("rebuttals", [])
    )
    return [
        Send("minister_vote", {
            "project_id":    state["project_id"],
            "problem":       state["problem"],
            "policy_options": state["policy_options"],
            "analyses":      state.get("analyses", []),
            "all_debates":   all_debates,
            "role":          minister.role,
        })
        for minister in CABINET
    ]


# ══════════════════════════════════════════════════════════════
# NODE 8 — TALLY VOTES
# Counts votes and determines winning option
# ══════════════════════════════════════════════════════════════

async def node_tally_votes(state: GovernanceState) -> Dict[str, Any]:
    """Count votes and determine the cabinet's democratic choice."""
    votes      = state.get("votes", [])
    options    = state.get("policy_options", [])

    tally: Dict[str, int] = Counter(v.get("voted_option", "") for v in votes)
    winner = max(tally, key=tally.get) if tally else (options[0] if options else "Option 1")
    total  = len(votes)
    winning_count = tally.get(winner, 0)
    pct    = round((winning_count / total * 100) if total else 0, 1)

    consensus = "high" if pct >= 80 else "moderate" if pct >= 50 else "low"

    logger.info("Votes tallied", winner=winner, percentage=pct, consensus=consensus)
    return {
        "vote_tally": dict(tally),
        "current_phase": "simulating",
        "metadata": {
            **state.get("metadata", {}),
            "winning_option": winner,
            "vote_percentage": pct,
            "consensus_level": consensus,
            "total_votes": total,
        },
    }


# ══════════════════════════════════════════════════════════════
# NODE 8.5 — SIMULATION ENGINE
# Simulates the winning option across 4 distinct futures
# ══════════════════════════════════════════════════════════════

async def node_simulation_phase(state: GovernanceState) -> Dict[str, Any]:
    """
    Runs the future simulation engine on the winning policy option.
    Generates Future A, B, C, D.
    """
    logger.info("Simulation phase starting")
    
    problem = state["problem"]
    winning_option = state.get("metadata", {}).get("winning_option")
    if not winning_option:
        options = state.get("policy_options", [])
        winning_option = options[0] if options else "Option 1"

    futures = ["Future A (Optimistic)", "Future B (Pessimistic)", "Future C (Tech-Driven)", "Future D (Resource-Constrained)"]
    
    async def run_sim(future_name: str):
        result = await SIMULATION_AGENT.simulate(problem, winning_option, future_name)
        result["_timestamp"] = _ts()
        return result

    # Run the 4 futures in parallel
    results = await asyncio.gather(*[run_sim(f) for f in futures], return_exceptions=False)
    sim_results = list(results)

    logger.info("Simulations complete", futures_simulated=len(sim_results))
    return {
        "simulation_results": sim_results,
        "current_phase": "synthesizing",
    }


# ══════════════════════════════════════════════════════════════
# NODE 9 — PRIME MINISTER SYNTHESIS
# Final binding policy from Gemini Pro
# ══════════════════════════════════════════════════════════════

async def node_prime_minister_synthesis(state: GovernanceState) -> Dict[str, Any]:
    """
    Prime Minister synthesizes all debate outputs, vote results,
    and metadata into a final structured JSON policy report.
    """
    logger.info("Prime Minister synthesis starting")

    problem   = state["problem"]
    analyses  = state.get("analyses", [])
    debates   = (
        state.get("debate_arguments", [])
        + state.get("opposition_attacks", [])
        + state.get("rebuttals", [])
    )
    simulations = state.get("simulation_results", [])
    votes     = state.get("votes", [])
    tally     = state.get("vote_tally", {})
    options   = state.get("policy_options", [])
    meta      = state.get("metadata", {})

    # ── Build synthesis context ────────────────────────────────
    analyses_block = "\n\n".join(
        f"[{a.get('role_title', a.get('agent_role','?'))}]\n"
        f"Assessment: {a.get('situation_assessment','')}\n"
        f"Goal: {a.get('primary_goal','')}\n"
        f"Findings: {'; '.join(a.get('key_findings',[])[:3])}\n"
        f"Solutions: {'; '.join(a.get('proposed_solutions',[])[:2])}\n"
        f"Red Lines: {'; '.join(a.get('red_lines',[])[:2])}"
        for a in analyses
    )

    debate_block = "\n".join(
        f"[{d.get('agent_role','')} | {d.get('phase','')} | Round {d.get('round_number',0)}]: "
        f"{d.get('argument','')[:200]}..."
        for d in debates
    )
    
    simulations_block = "\n".join(
        f"[{s.get('future_name', 'Future')}]: Option '{s.get('option_name','')}' "
        f"scored {s.get('composite_score',0)}/100 (Econ: {s.get('economic_score',0)}, Env: {s.get('environment_score',0)}, Social: {s.get('social_score',0)}, Feasibility: {s.get('feasibility_score',0)}). "
        f"Risk Level: {s.get('risk_level','')}"
        for s in simulations
    )

    vote_block = "\n".join(
        f"- {v.get('agent_role','?')}: '{v.get('voted_option','')}' "
        f"(confidence {v.get('confidence_score',0):.0f}%) — {v.get('justification','')[:100]}"
        for v in votes
    )

    tally_block = " | ".join(f"{k}: {v} votes" for k, v in tally.items())

    pm_schema = """{
  "executive_summary": "<2-3 sentence plain-language summary of the final decision>",
  "chosen_option": "<exact option name>",
  "rationale": "<your detailed reasoning for selecting this strategy, citing debate and simulation results>",
  "confidence_score": <1-100 float representing your confidence in this decision>,
  "implementation_steps": [
    {
      "phase": "Phase 1 — Foundation",
      "duration": "Months 1-6",
      "actions": ["Action 1", "Action 2", "Action 3"],
      "responsible_ministry": "Ministry Name",
      "budget_allocation_percent": 30,
      "kpis": ["KPI 1", "KPI 2"]
    }
  ],
  "success_metrics": [
    {"metric": "Unemployment rate", "target": "Below 8%", "deadline": "24 months"},
    {"metric": "CO2 reduction", "target": "15% vs baseline", "deadline": "36 months"}
  ],
  "risks_and_mitigations": {
    "Risk 1 description": "Mitigation strategy",
    "Risk 2 description": "Mitigation strategy",
    "Risk 3 description": "Mitigation strategy"
  },
  "expected_outcomes": ["Outcome 1", "Outcome 2", "Outcome 3"],
  "review_timeline": "Quarterly for 2 years, then annual",
  "dissenting_views_acknowledged": [
    {"from": "opposition_minister", "concern": "...", "response": "..."}
  ],
  "consensus_level": "<low|moderate|high>",
  "vote_breakdown": {}
}"""

    user_msg = f"""You are making the final governance decision as Prime Minister.

PROBLEM: {problem}

MINISTERIAL ANALYSES:
{analyses_block}

DEBATE TRANSCRIPT:
{debate_block}

SIMULATION RESULTS:
{simulations_block}

VOTE RESULTS:
{vote_block}
TALLY: {tally_block}
WINNING OPTION: {meta.get('winning_option','?')} ({meta.get('vote_percentage',0)}% — {meta.get('consensus_level','?')} consensus)

Synthesise all of the above into a final binding policy (the selected strategy). Be specific, realistic, and politically defensible.
You must generate:
1. Reasoning (rationale)
2. Risk analysis (risks_and_mitigations)
3. Expected impact (expected_outcomes)
4. Confidence score (confidence_score)

Return ONLY this JSON (no markdown fences, no text outside the JSON):
{pm_schema}"""

    # Use PM's dedicated synthesis
    from app.agents.ministers.base import extract_json
    from langchain_core.messages import HumanMessage, SystemMessage

    llm = _build_llm_pro()
    try:
        resp = await llm.ainvoke([
            SystemMessage(content=PRIME_MINISTER.system_prompt),
            HumanMessage(content=user_msg),
        ])
        final = extract_json(str(resp.content))
        if not final:
            raise ValueError("Empty JSON from PM synthesis")
        final.setdefault("chosen_option", meta.get("winning_option", options[0] if options else ""))
        final.setdefault("consensus_level", meta.get("consensus_level", "moderate"))
        final.setdefault("vote_breakdown", tally)
        final["_timestamp"] = _ts()

        logger.info("Prime Minister synthesis complete", option=final.get("chosen_option"))
        return {
            "final_report": final,
            "metadata": {**meta, "completed_at": _ts()},
        }

    except Exception as exc:
        logger.error("PM synthesis failed", error=str(exc))
        return {
            "error": str(exc),
            "current_phase": "failed",
        }


# ══════════════════════════════════════════════════════════════
# 10. BLACK SWAN RESILIENCE ENGINE
# ══════════════════════════════════════════════════════════════

async def node_black_swan_engine(state: GovernanceState) -> Dict[str, Any]:
    """
    Stress-tests the finalized strategy against a random catastrophic Black Swan event.
    """
    pid = state.get("project_id", "")
    from app.services.session_service import SessionService
    await SessionService.update_phase(pid, "black_swan")

    report = state.get("final_report", {})
    if not report:
        return {}

    # 1. Randomly select a crisis
    import random
    crises = [
        "Global Economic Recession (-15% GDP)",
        "Global Pandemic (Lockdowns, 30% workforce impact)",
        "Catastrophic 500-Year Flood (Infrastructure destroyed)",
        "Severe Supply Chain Shortage (Critical materials unavailable)",
        "Massive Political Unrest (Riots, 40% drop in approval)"
    ]
    selected_crisis = random.choice(crises)

    schema = """{
  "black_swan_crisis": "<the selected crisis>",
  "black_swan_impact": "<detailed 3-sentence analysis of how the strategy holds up or fails>",
  "resilience_score": <1-100 float estimating strategy survivability>
}"""

    prompt = f"""You are the TITAN Black Swan Resilience Engine.
A finalized governance strategy has been passed to you.

STRATEGY CHOSEN: {report.get('chosen_option', 'Unknown')}
RATIONALE: {report.get('rationale', '')}
RISK MITIGATIONS: {json.dumps(report.get('risks_and_mitigations', {}))}

A BLACK SWAN EVENT HAS JUST OCCURRED:
{selected_crisis}

Analyze how the strategy survives this unpredictable, massive shock. Generate a resilience score.
Return ONLY valid JSON matching this schema:
{schema}"""

    from langchain_core.messages import HumanMessage
    from app.agents.base import _build_llm_flash
    llm = _build_llm_flash()
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    content = response.content.strip()

    try:
        from app.agents.ministers.base import extract_json
        results = extract_json(content)
        if not results:
            raise ValueError("Empty JSON")
    except Exception:
        results = {
            "black_swan_crisis": selected_crisis,
            "black_swan_impact": "Failed to generate structured impact analysis.",
            "resilience_score": 0.0
        }
        
    return {
        "black_swan_results": results,
        "current_phase": "completed"
    }


# ══════════════════════════════════════════════════════════════
# NODE 11 — ERROR HANDLER
# ══════════════════════════════════════════════════════════════

async def node_error_handler(state: GovernanceState) -> Dict[str, Any]:
    """Terminal error node — logs and finalises failed state."""
    error = state.get("error", "Unknown error")
    logger.error("Governance graph failed", error=error, project_id=state["project_id"])
    return {
        "current_phase": "failed",
        "metadata": {
            **state.get("metadata", {}),
            "failed_at": _ts(),
            "error": error,
        },
    }


# ══════════════════════════════════════════════════════════════
# CONDITIONAL EDGES
# ══════════════════════════════════════════════════════════════

def route_after_validation(state: GovernanceState) -> str | List[Send]:
    """After validation: proceed to parallel analysis or fail."""
    if state.get("error") or state.get("current_phase") == "failed":
        return "error_handler"
    return route_to_ministers(state)


def route_after_synthesis(state: GovernanceState) -> str:
    """After PM synthesis: done or failed."""
    return "failed" if state.get("error") else "__end__"
