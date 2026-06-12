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
    "MINISTER_REGISTRY",
]
