"""
Centralized Constants for TITAN
================================
Single source of truth for all constants (phases, roles, metrics).
Shared between backend and can be exported to frontend via API.
"""
from enum import Enum
from typing import List, Dict


# ─── DEBATE PHASES ────────────────────────────────────────
class DebatePhase(str, Enum):
    """Enum for debate phases - single source of truth."""
    PENDING = "pending"
    ANALYZING = "analyzing"
    DEBATING = "debating"
    CHALLENGING = "challenging"
    REBUTTING = "rebutting"
    VOTING = "voting"
    SIMULATING = "simulating"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"


# ─── MINISTER ROLES ───────────────────────────────────────
class MinisterRole(str, Enum):
    """Enum for minister roles - replaces magic strings."""
    PRIME_MINISTER = "prime_minister"
    ECONOMIC_MINISTER = "economic_minister"
    TECHNOLOGY_MINISTER = "technology_minister"
    INFRASTRUCTURE_MINISTER = "infrastructure_minister"
    CITIZEN_MINISTER = "citizen_minister"
    ENVIRONMENT_MINISTER = "environment_minister"
    OPPOSITION_MINISTER = "opposition_minister"
    SIMULATION_AGENT = "simulation_agent"


# ─── SIMULATION FUTURES ───────────────────────────────────
class SimulationFuture(str, Enum):
    """Four distinct world-states for stress testing."""
    OPTIMISTIC = "future_optimistic"
    PESSIMISTIC = "future_pessimistic"
    TECHNOLOGY_DRIVEN = "future_tech_driven"
    CONSTRAINED = "future_constrained"


# ─── SIMULATION METRICS ───────────────────────────────────
class SimulationMetric(str, Enum):
    """Five key metrics for policy evaluation."""
    ECONOMIC_IMPACT = "economic_impact"
    SUSTAINABILITY = "sustainability"
    CITIZEN_SATISFACTION = "citizen_satisfaction"
    IMPLEMENTATION_COST = "implementation_cost"
    RISK_RESILIENCE = "risk_resilience"


# ─── DEBATE PHASES METADATA ───────────────────────────────
PHASE_DESCRIPTIONS: Dict[DebatePhase, str] = {
    DebatePhase.PENDING: "Session created, awaiting initialization",
    DebatePhase.ANALYZING: "Six ministers analyzing problem in parallel",
    DebatePhase.DEBATING: "Proposal presentations from five ministers",
    DebatePhase.CHALLENGING: "Opposition minister attacking proposals",
    DebatePhase.REBUTTING: "Ministers defending against opposition",
    DebatePhase.VOTING: "Democratic vote on policy options",
    DebatePhase.SIMULATING: "Stress-testing winning policy across four futures",
    DebatePhase.SYNTHESIZING: "Prime Minister synthesizing final recommendation",
    DebatePhase.COMPLETED: "Session complete, report available",
    DebatePhase.FAILED: "Session failed with error",
}

PHASE_ORDERING: List[DebatePhase] = [
    DebatePhase.PENDING,
    DebatePhase.ANALYZING,
    DebatePhase.DEBATING,
    DebatePhase.CHALLENGING,
    DebatePhase.REBUTTING,
    DebatePhase.VOTING,
    DebatePhase.SIMULATING,
    DebatePhase.SYNTHESIZING,
    DebatePhase.COMPLETED,
]

# ─── MINISTER METADATA ────────────────────────────────────
MINISTER_DISPLAY_NAMES: Dict[MinisterRole, str] = {
    MinisterRole.PRIME_MINISTER: "👑 Prime Minister",
    MinisterRole.ECONOMIC_MINISTER: "📈 Economic Minister",
    MinisterRole.TECHNOLOGY_MINISTER: "💻 Technology Minister",
    MinisterRole.INFRASTRUCTURE_MINISTER: "🏗️ Infrastructure Minister",
    MinisterRole.CITIZEN_MINISTER: "👥 Citizen Minister",
    MinisterRole.ENVIRONMENT_MINISTER: "🌿 Environment Minister",
    MinisterRole.OPPOSITION_MINISTER: "🛡️ Opposition Minister",
    MinisterRole.SIMULATION_AGENT: "🔬 Simulation Agent",
}

MINISTER_DESCRIPTIONS: Dict[MinisterRole, str] = {
    MinisterRole.ECONOMIC_MINISTER: "GDP, employment, fiscal policy, economic stability",
    MinisterRole.TECHNOLOGY_MINISTER: "Innovation, digital infrastructure, tech adoption",
    MinisterRole.INFRASTRUCTURE_MINISTER: "Roads, energy, water, physical infrastructure",
    MinisterRole.CITIZEN_MINISTER: "Social equity, welfare, citizen wellbeing",
    MinisterRole.ENVIRONMENT_MINISTER: "Climate, sustainability, environmental impact",
    MinisterRole.OPPOSITION_MINISTER: "Critical analysis, risk identification, contrarian view",
    MinisterRole.SIMULATION_AGENT: "Synthetic scenario testing, stress testing policies",
}

# Analyzing ministers (not opposition or PM)
ANALYZING_MINISTERS: List[MinisterRole] = [
    MinisterRole.ECONOMIC_MINISTER,
    MinisterRole.TECHNOLOGY_MINISTER,
    MinisterRole.INFRASTRUCTURE_MINISTER,
    MinisterRole.CITIZEN_MINISTER,
    MinisterRole.ENVIRONMENT_MINISTER,
    MinisterRole.OPPOSITION_MINISTER,
]

VOTING_MINISTERS: List[MinisterRole] = ANALYZING_MINISTERS  # Same set votes

# ─── FUTURE METADATA ──────────────────────────────────────
FUTURE_DISPLAY_NAMES: Dict[SimulationFuture, str] = {
    SimulationFuture.OPTIMISTIC: "Future A — Optimistic",
    SimulationFuture.PESSIMISTIC: "Future B — Pessimistic",
    SimulationFuture.TECHNOLOGY_DRIVEN: "Future C — Technology-Driven",
    SimulationFuture.CONSTRAINED: "Future D — Resource-Constrained",
}

FUTURE_DESCRIPTIONS: Dict[SimulationFuture, str] = {
    SimulationFuture.OPTIMISTIC: "Best case — strong political will, stable economy, high adoption",
    SimulationFuture.PESSIMISTIC: "Worst case — weak will, economic headwinds, resistance",
    SimulationFuture.TECHNOLOGY_DRIVEN: "Tech surge — 2x faster adoption, digital-first, equity gaps",
    SimulationFuture.CONSTRAINED: "Budget crisis — 40% budget cuts, supply chain issues",
}

FUTURE_COLORS: Dict[SimulationFuture, str] = {
    SimulationFuture.OPTIMISTIC: "emerald",
    SimulationFuture.PESSIMISTIC: "rose",
    SimulationFuture.TECHNOLOGY_DRIVEN: "indigo",
    SimulationFuture.CONSTRAINED: "amber",
}

# ─── SIMULATION METRIC METADATA ────────────────────────────
METRIC_DISPLAY_NAMES: Dict[SimulationMetric, str] = {
    SimulationMetric.ECONOMIC_IMPACT: "Economic Impact",
    SimulationMetric.SUSTAINABILITY: "Sustainability",
    SimulationMetric.CITIZEN_SATISFACTION: "Citizen Satisfaction",
    SimulationMetric.IMPLEMENTATION_COST: "Implementation Cost",
    SimulationMetric.RISK_RESILIENCE: "Risk Resilience",
}

METRIC_DESCRIPTIONS: Dict[SimulationMetric, str] = {
    SimulationMetric.ECONOMIC_IMPACT: "GDP growth, employment impact, fiscal sustainability",
    SimulationMetric.SUSTAINABILITY: "Environmental footprint, resource efficiency, long-term viability",
    SimulationMetric.CITIZEN_SATISFACTION: "Public support, quality of life improvement, fairness",
    SimulationMetric.IMPLEMENTATION_COST: "Fiscal cost, resource requirements, cost efficiency",
    SimulationMetric.RISK_RESILIENCE: "Downside protection, robustness to shocks, adaptability",
}

# ─── TIMEOUTS & LIMITS ────────────────────────────────────
AGENT_TIMEOUT_SECONDS = 120  # Max time for single LLM call
DEBATE_ROUND_TIMEOUT_SECONDS = 300  # Max time for full debate round
SESSION_TIMEOUT_SECONDS = 1800  # Max time for entire session (30 min)

LLM_MAX_TOKENS = 4096
LLM_TEMPERATURE = 0.7

# ─── API CONSTRAINTS ──────────────────────────────────────
MAX_PROBLEM_LENGTH = 5000
MIN_PROBLEM_LENGTH = 20
MAX_CONTEXT_LENGTH = 2000
MAX_SESSIONS_PER_HOUR = 100  # Rate limit

# ─── CABINET SIZE ─────────────────────────────────────────
CABINET_SIZE = 6  # Number of analyzing ministers
TOTAL_AGENTS = 8  # Including PM and Simulation agent
