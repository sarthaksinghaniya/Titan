"""SQLAlchemy ORM models for TITAN platform."""
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Column, String, Text, Integer, Float, DateTime,
    ForeignKey, JSON, Enum as SAEnum, Boolean,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

# ─── Enums ────────────────────────────────────────────────────
import enum

class SessionStatus(str, enum.Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    DEBATING = "debating"
    VOTING = "voting"
    SIMULATING = "simulating"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"


class MinisterRole(str, enum.Enum):
    PRIME_MINISTER = "prime_minister"
    ECONOMIC_MINISTER = "economic_minister"
    TECHNOLOGY_MINISTER = "technology_minister"
    INFRASTRUCTURE_MINISTER = "infrastructure_minister"
    CITIZEN_MINISTER = "citizen_minister"
    ENVIRONMENT_MINISTER = "environment_minister"
    OPPOSITION_MINISTER = "opposition_minister"
    SIMULATION_AGENT = "simulation_agent"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ─── Session ──────────────────────────────────────────────────
class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    problem = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    status = Column(SAEnum(SessionStatus), nullable=False, default=SessionStatus.PENDING)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    analyses = relationship("MinisterAnalysis", back_populates="session", cascade="all, delete-orphan")
    debate_rounds = relationship("DebateRound", back_populates="session", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="session", cascade="all, delete-orphan")
    simulation_results = relationship("SimulationResult", back_populates="session", cascade="all, delete-orphan")
    final_policy = relationship("FinalPolicy", back_populates="session", uselist=False, cascade="all, delete-orphan")


# ─── Minister Analysis ────────────────────────────────────────
class MinisterAnalysis(Base):
    __tablename__ = "minister_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    minister_role = Column(SAEnum(MinisterRole), nullable=False)
    analysis_text = Column(Text, nullable=False)
    key_points = Column(JSON, nullable=False, default=list)
    proposed_solutions = Column(JSON, nullable=False, default=list)
    concerns = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session = relationship("Session", back_populates="analyses")


# ─── Debate Round ─────────────────────────────────────────────
class DebateRound(Base):
    __tablename__ = "debate_rounds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    round_number = Column(Integer, nullable=False)
    minister_role = Column(SAEnum(MinisterRole), nullable=False)
    argument_text = Column(Text, nullable=False)
    supporting_ministers = Column(JSON, nullable=False, default=list)
    opposing_ministers = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session = relationship("Session", back_populates="debate_rounds")


# ─── Vote ─────────────────────────────────────────────────────
class Vote(Base):
    __tablename__ = "votes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    minister_role = Column(SAEnum(MinisterRole), nullable=False)
    voted_option = Column(String(500), nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0–100
    justification = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session = relationship("Session", back_populates="votes")


# ─── Simulation Result ────────────────────────────────────────
class SimulationResult(Base):
    __tablename__ = "simulation_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    option_name = Column(String(500), nullable=False)
    economic_score = Column(Float, nullable=False)  # 0–100
    social_score = Column(Float, nullable=False)
    environmental_score = Column(Float, nullable=False)
    feasibility_score = Column(Float, nullable=False)
    risk_level = Column(SAEnum(RiskLevel), nullable=False)
    time_to_implement_months = Column(Integer, nullable=False)
    cost_estimate_usd_millions = Column(Float, nullable=False)
    projected_population_impact = Column(Float, nullable=False)
    key_risks = Column(JSON, nullable=False, default=list)
    key_benefits = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session = relationship("Session", back_populates="simulation_results")


# ─── Final Policy ─────────────────────────────────────────────
class FinalPolicy(Base):
    __tablename__ = "final_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, unique=True)
    chosen_option = Column(String(500), nullable=False)
    overall_rationale = Column(Text, nullable=False)
    implementation_steps = Column(JSON, nullable=False, default=list)
    success_metrics = Column(JSON, nullable=False, default=list)
    risks_and_mitigations = Column(JSON, nullable=False, default=dict)
    expected_outcomes = Column(JSON, nullable=False, default=list)
    review_timeline = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session = relationship("Session", back_populates="final_policy")
