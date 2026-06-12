"""
Agent package — public API.
Import the compiled graph and minister registry from here.
"""
from app.agents.graph import governance_graph, create_governance_graph
from app.agents.state import GovernanceState, make_initial_state
from app.agents.ministers import (
    CABINET,
    PRIME_MINISTER,
    MINISTER_REGISTRY,
)

__all__ = [
    "governance_graph",
    "create_governance_graph",
    "GovernanceState",
    "make_initial_state",
    "CABINET",
    "PRIME_MINISTER",
    "MINISTER_REGISTRY",
]
