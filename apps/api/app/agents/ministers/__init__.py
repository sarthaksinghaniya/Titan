"""Ministers package — clean public API."""
from app.agents.ministers.base import BaseMinisterAgent, extract_json
from app.agents.ministers.ministers import (
    EconomicMinister,
    TechnologyMinister,
    InfrastructureMinister,
    CitizenMinister,
    EnvironmentMinister,
    OppositionMinister,
    PrimeMinister,
)
from app.agents.ministers.simulation import SIMULATION_AGENT

# ── Cabinet registry — ordered for display ────────────────────
CABINET: list[BaseMinisterAgent] = [
    EconomicMinister(),
    TechnologyMinister(),
    InfrastructureMinister(),
    CitizenMinister(),
    EnvironmentMinister(),
    OppositionMinister(),
]

PRIME_MINISTER = PrimeMinister()

# ── Fast lookup by role key ────────────────────────────────────
MINISTER_REGISTRY: dict[str, BaseMinisterAgent] = {
    m.role: m for m in [*CABINET, PRIME_MINISTER]
}
# Simulation agent is special, not a base minister
MINISTER_REGISTRY[SIMULATION_AGENT.role] = SIMULATION_AGENT

__all__ = [
    "BaseMinisterAgent",
    "extract_json",
    "EconomicMinister",
    "TechnologyMinister",
    "InfrastructureMinister",
    "CitizenMinister",
    "EnvironmentMinister",
    "OppositionMinister",
    "PrimeMinister",
    "CABINET",
    "PRIME_MINISTER",
    "SIMULATION_AGENT",
    "MINISTER_REGISTRY",
]
