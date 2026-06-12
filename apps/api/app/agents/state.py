"""
TITAN Governance State
======================
Typed state flowing through every LangGraph node.
Uses Annotated reducers for list fields so parallel
Send-based fan-outs merge correctly.
"""
from __future__ import annotations

import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict


# ──────────────────────────────────────────────────────────────
# Per-phase output schemas (stored as dicts in state)
# ──────────────────────────────────────────────────────────────

class MinisterOutput(TypedDict):
    """Structured JSON output from each minister's analysis node."""
    agent_role: str
    role_title: str
    # core deliverables
    situation_assessment: str
    primary_goal: str
    key_findings: List[str]          # 3-5 findings
    proposed_solutions: List[str]    # 2-3 concrete options
    constraints_applied: List[str]   # what limits their recommendations
    red_lines: List[str]             # conditions they will never accept
    priority_score: float            # 0-100, how urgent this minister sees the issue
    confidence: float                # 0-100, certainty in their analysis


class DebateArgument(TypedDict):
    """Structured JSON output from a debate node."""
    agent_role: str
    round_number: int                # 1 = initial debate, 2 = rebuttal
    phase: str                       # "debate" | "opposition_attack" | "rebuttal"
    argument: str
    attacking_roles: List[str]       # roles this argument targets
    defending_positions: List[str]   # positions being defended
    concessions: List[str]           # points conceded to others
    new_evidence: List[str]          # new data points introduced
    word_count: int


class VoteRecord(TypedDict):
    """Structured JSON output from a voting node."""
    agent_role: str
    voted_option: str
    confidence_score: float          # 0-100
    justification: str
    second_choice: str               # fallback preference
    veto_options: List[str]          # options this minister will block


class GovernanceState(TypedDict):
    """
    Master state object shared across all LangGraph nodes.

    Annotated[List, operator.add] means each node's output
    is appended (not replaced) — critical for parallel fan-outs.
    """
    # ── Session identity ────────────────────────────────────────
    project_id: str
    problem: str
    context: str

    # ── Phase 1 : Parallel minister analyses ───────────────────
    analyses: Annotated[List[MinisterOutput], operator.add]

    # ── Phase 2 : Structured debate arguments ──────────────────
    debate_arguments: Annotated[List[DebateArgument], operator.add]

    # ── Phase 3 : Opposition attack outputs ────────────────────
    opposition_attacks: Annotated[List[DebateArgument], operator.add]

    # ── Phase 4 : Rebuttal outputs ─────────────────────────────
    rebuttals: Annotated[List[DebateArgument], operator.add]

    # ── Phase 5 : Votes ─────────────────────────────────────────
    votes: Annotated[List[VoteRecord], operator.add]

    # ── Derived ─────────────────────────────────────────────────
    policy_options: List[str]        # extracted from debate
    vote_tally: Dict[str, int]       # option -> count

    # ── Phase 6 : Prime Minister synthesis ─────────────────────
    final_report: Optional[Dict[str, Any]]

    # ── Control flow ────────────────────────────────────────────
    current_phase: str
    error: Optional[str]
    metadata: Dict[str, Any]         # timing, token counts, etc.


def make_initial_state(project_id: str, problem: str, context: str = "") -> GovernanceState:
    """Return a blank initial state for a new governance project."""
    return GovernanceState(
        project_id=project_id,
        problem=problem,
        context=context,
        analyses=[],
        debate_arguments=[],
        opposition_attacks=[],
        rebuttals=[],
        votes=[],
        policy_options=[],
        vote_tally={},
        final_report=None,
        current_phase="analyzing",
        error=None,
        metadata={},
    )
