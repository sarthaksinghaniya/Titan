"""
LangGraph State definition for the governance agent graph.
"""
from typing import Any, Dict, List, Optional, TypedDict


class GovernanceState(TypedDict):
    """Shared state flowing through the LangGraph governance graph."""
    session_id: str
    problem: str
    context: str

    # Analysis phase outputs
    analyses: List[Dict[str, Any]]

    # Debate phase outputs
    debate_rounds: List[Dict[str, Any]]

    # Voting phase outputs
    votes: List[Dict[str, Any]]

    # Policy options extracted from debate
    policy_options: List[str]

    # Simulation phase outputs
    simulation_results: List[Dict[str, Any]]

    # Final synthesis
    final_policy: Optional[Dict[str, Any]]

    # Control flow
    current_phase: str
    debate_round_number: int
    error: Optional[str]


def create_initial_state(session_id: str, problem: str, context: str = "") -> GovernanceState:
    """Create the initial state for a new governance session."""
    return GovernanceState(
        session_id=session_id,
        problem=problem,
        context=context,
        analyses=[],
        debate_rounds=[],
        votes=[],
        policy_options=[],
        simulation_results=[],
        final_policy=None,
        current_phase="analyzing",
        debate_round_number=0,
        error=None,
    )
