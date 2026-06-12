"""Pydantic schemas — API request/response models."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ─── Enums ────────────────────────────────────────────────────
from enum import Enum

class SessionStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    DEBATING = "debating"
    VOTING = "voting"
    SIMULATING = "simulating"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"


class MinisterRole(str, Enum):
    PRIME_MINISTER = "prime_minister"
    ECONOMIC_MINISTER = "economic_minister"
    TECHNOLOGY_MINISTER = "technology_minister"
    INFRASTRUCTURE_MINISTER = "infrastructure_minister"
    CITIZEN_MINISTER = "citizen_minister"
    ENVIRONMENT_MINISTER = "environment_minister"
    OPPOSITION_MINISTER = "opposition_minister"
    SIMULATION_AGENT = "simulation_agent"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ─── Session Schemas ──────────────────────────────────────────
class CreateSessionRequest(BaseModel):
    problem: str = Field(..., min_length=20, max_length=2000, description="The societal problem to analyze")
    context: Optional[str] = Field(None, max_length=1000, description="Additional context")

    @field_validator("problem")
    @classmethod
    def problem_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Problem cannot be empty or whitespace")
        return v.strip()


class CreateSessionResponse(BaseModel):
    session_id: str
    status: SessionStatus
    message: str


class SessionSchema(BaseModel):
    id: str
    problem: str
    context: Optional[str]
    status: SessionStatus
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    has_next: bool


# ─── Minister Analysis Schemas ────────────────────────────────
class MinisterAnalysisSchema(BaseModel):
    id: str
    session_id: str
    minister_role: MinisterRole
    analysis_text: str
    key_points: List[str]
    proposed_solutions: List[str]
    concerns: List[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Debate Round Schemas ─────────────────────────────────────
class DebateRoundSchema(BaseModel):
    id: str
    session_id: str
    round_number: int
    minister_role: MinisterRole
    argument_text: str
    supporting_ministers: List[str]
    opposing_ministers: List[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Vote Schemas ─────────────────────────────────────────────
class VoteSchema(BaseModel):
    id: str
    session_id: str
    minister_role: MinisterRole
    voted_option: str
    confidence_score: float = Field(..., ge=0, le=100)
    justification: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Simulation Result Schemas ────────────────────────────────
class SimulationResultSchema(BaseModel):
    id: str
    session_id: str
    option_name: str
    economic_score: float
    social_score: float
    environmental_score: float
    feasibility_score: float
    risk_level: RiskLevel
    time_to_implement_months: int
    cost_estimate_usd_millions: float
    projected_population_impact: float
    key_risks: List[str]
    key_benefits: List[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Policy Step Schema ───────────────────────────────────────
class PolicyStepSchema(BaseModel):
    phase: str
    duration: str
    actions: List[str]
    responsible_ministry: str
    budget_allocation_percent: float


# ─── Final Policy Schemas ─────────────────────────────────────
class FinalPolicySchema(BaseModel):
    id: str
    session_id: str
    chosen_option: str
    overall_rationale: str
    implementation_steps: List[Dict[str, Any]]
    success_metrics: List[str]
    risks_and_mitigations: Dict[str, str]
    expected_outcomes: List[str]
    review_timeline: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Full Report Schema ───────────────────────────────────────
class SessionReportSchema(BaseModel):
    session: SessionSchema
    analyses: List[MinisterAnalysisSchema]
    debate_rounds: List[DebateRoundSchema]
    votes: List[VoteSchema]
    simulation_results: List[SimulationResultSchema]
    final_policy: Optional[FinalPolicySchema]


# ─── Health Check ─────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: str
    gemini_configured: bool
