"""Pydantic schemas — API request/response models matching the new architecture."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ─── Enums ────────────────────────────────────────────────────
from app.models.session import ProjectStatus, AgentRole, RiskLevel


# ─── Project Schemas (Session) ────────────────────────────────
class CreateProjectRequest(BaseModel):
    problem: str = Field(..., min_length=20, max_length=2000, description="The societal problem to analyze")
    context: Optional[str] = Field(None, max_length=1000, description="Additional context")

    @field_validator("problem")
    @classmethod
    def problem_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Problem cannot be empty or whitespace")
        return v.strip()


class CreateProjectResponse(BaseModel):
    session_id: str = None  # Alias for project_id for frontend compatibility
    project_id: str = None
    status: ProjectStatus
    message: str
    
    def __init__(self, **data):
        # Support both session_id and project_id naming conventions
        if 'project_id' in data and 'session_id' not in data:
            data['session_id'] = data['project_id']
        super().__init__(**data)


class ProjectSchema(BaseModel):
    id: UUID
    title: str
    problem: str
    context: Optional[str]
    status: ProjectStatus
    error_message: Optional[str]
    metadata_: Dict[str, Any] = Field(alias="metadata_")
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True, "populate_by_name": True}


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    has_next: bool


# ─── Agent Analysis Schemas ───────────────────────────────────
class AgentSchema(BaseModel):
    id: UUID
    project_id: UUID
    role: AgentRole
    model_used: str
    analysis: str
    key_points: List[str]
    proposed_solutions: List[str]
    concerns: List[str]
    tokens_used: Optional[int]
    processing_ms: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Debate Schemas ───────────────────────────────────────────
class DebateSchema(BaseModel):
    id: UUID
    project_id: UUID
    agent_id: UUID
    round_number: int
    phase: str
    argument: str
    supporting_agents: List[str]
    opposing_agents: List[str]
    word_count: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Vote Schemas ─────────────────────────────────────────────
class VoteSchema(BaseModel):
    id: UUID
    project_id: UUID
    agent_id: UUID
    voted_option: str
    confidence_score: float = Field(..., ge=0, le=100)
    justification: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Simulation Schemas ───────────────────────────────────────
class SimulationSchema(BaseModel):
    id: UUID
    project_id: UUID
    option_name: str
    option_description: Optional[str]
    economic_score: float
    social_score: float
    environmental_score: float
    feasibility_score: float
    composite_score: float
    risk_level: RiskLevel
    time_to_implement_months: int
    cost_estimate_usd_millions: float
    projected_population_impact: float
    key_risks: List[str]
    key_benefits: List[str]
    scenario_data: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Final Report Schemas ─────────────────────────────────────
class FinalReportSchema(BaseModel):
    id: UUID
    project_id: UUID
    chosen_option: str
    executive_summary: str
    overall_rationale: str
    confidence_score: float
    implementation_steps: List[Dict[str, Any]]
    success_metrics: List[Any]
    risks_and_mitigations: Dict[str, Any]
    expected_outcomes: List[str]
    review_timeline: str
    total_votes: int
    winning_votes: int
    vote_percentage: float
    consensus_level: str
    best_simulation_score: Optional[float]
    black_swan_crisis: Optional[str] = None
    black_swan_impact: Optional[str] = None
    resilience_score: Optional[float] = None
    alternative_hypotheses: Optional[List[str]] = None
    requires_human_review: Optional[bool] = False
    model_used: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Full Report Schema ───────────────────────────────────────
class ProjectReportSchema(BaseModel):
    project: ProjectSchema
    agents: List[AgentSchema]
    debates: List[DebateSchema]
    votes: List[VoteSchema]
    simulations: List[SimulationSchema]
    final_report: Optional[FinalReportSchema]
    executive_reports: Optional[List[Any]] = None


# ─── Health Check ─────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: str
    gemini_configured: bool
