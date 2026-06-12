"""
TITAN Database Models
=====================
Six-table architecture:
  projects       → governance sessions
  agents         → minister analysis records
  debates        → debate round arguments
  votes          → minister votes
  simulations    → policy stress-test results
  final_reports  → prime minister synthesis

All tables use UUID primary keys, cascading deletes, and
timezone-aware timestamps.
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


# ══════════════════════════════════════════════════════════════
# ENUMS
# ══════════════════════════════════════════════════════════════

class ProjectStatus(str, enum.Enum):
    PENDING      = "pending"
    ANALYZING    = "analyzing"
    DEBATING     = "debating"
    VOTING       = "voting"
    SIMULATING   = "simulating"
    SYNTHESIZING = "synthesizing"
    COMPLETED    = "completed"
    FAILED       = "failed"


class AgentRole(str, enum.Enum):
    PRIME_MINISTER          = "prime_minister"
    ECONOMIC_MINISTER       = "economic_minister"
    TECHNOLOGY_MINISTER     = "technology_minister"
    INFRASTRUCTURE_MINISTER = "infrastructure_minister"
    CITIZEN_MINISTER        = "citizen_minister"
    ENVIRONMENT_MINISTER    = "environment_minister"
    OPPOSITION_MINISTER     = "opposition_minister"
    SIMULATION_AGENT        = "simulation_agent"


class RiskLevel(str, enum.Enum):
    LOW      = "low"
    MEDIUM   = "medium"
    HIGH     = "high"
    CRITICAL = "critical"


# ══════════════════════════════════════════════════════════════
# PROJECTS
# Primary table — one row per governance session
# ══════════════════════════════════════════════════════════════

class Project(Base):
    """
    A governance session initiated by a user problem submission.
    Owns all related agent work via cascading relationships.
    """
    __tablename__ = "projects"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title         = Column(String(300), nullable=False)                          # auto-generated summary
    problem       = Column(Text, nullable=False)                                 # raw user input
    context       = Column(Text, nullable=True)                                  # optional extra context
    status        = Column(SAEnum(ProjectStatus, name="project_status_enum"),
                           nullable=False, default=ProjectStatus.PENDING, index=True)
    error_message = Column(Text, nullable=True)
    metadata_     = Column("metadata", JSONB, nullable=False, default=dict)      # extensible bag
    created_at    = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at    = Column(DateTime(timezone=True), server_default=func.now(),
                           onupdate=func.now(), nullable=False)
    completed_at  = Column(DateTime(timezone=True), nullable=True)

    # ── Relationships ─────────────────────────────────────────
    agents        = relationship("Agent",       back_populates="project", cascade="all, delete-orphan",
                                 order_by="Agent.created_at")
    debates       = relationship("Debate",      back_populates="project", cascade="all, delete-orphan",
                                 order_by="[Debate.round_number, Debate.created_at]")
    votes         = relationship("Vote",        back_populates="project", cascade="all, delete-orphan")
    simulations   = relationship("Simulation",  back_populates="project", cascade="all, delete-orphan",
                                 order_by="Simulation.composite_score.desc()")
    final_report  = relationship("FinalReport", back_populates="project", uselist=False,
                                 cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_projects_status_created", "status", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} status={self.status} title={self.title[:40]!r}>"


# ══════════════════════════════════════════════════════════════
# AGENTS
# One row per minister per project (6 ministers × 1 project = 6 rows)
# ══════════════════════════════════════════════════════════════

class Agent(Base):
    """
    Records an individual minister's independent analysis of the problem.
    Each project has exactly one Agent row per AgentRole (6 total).
    """
    __tablename__ = "agents"

    id                 = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id         = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"),
                                nullable=False, index=True)
    role               = Column(SAEnum(AgentRole, name="agent_role_enum"), nullable=False, index=True)
    model_used         = Column(String(100), nullable=False, default="gemini-1.5-flash")
    analysis           = Column(Text, nullable=False, default="")
    key_points         = Column(JSONB, nullable=False, default=list)          # List[str]
    proposed_solutions = Column(JSONB, nullable=False, default=list)          # List[str]
    concerns           = Column(JSONB, nullable=False, default=list)          # List[str]
    tokens_used        = Column(Integer, nullable=True)
    processing_ms      = Column(Integer, nullable=True)                        # latency tracking
    created_at         = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ── Relationships ─────────────────────────────────────────
    project = relationship("Project", back_populates="agents")
    debates = relationship("Debate",  back_populates="agent",  cascade="all, delete-orphan")
    vote    = relationship("Vote",    back_populates="agent",  uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("project_id", "role", name="uq_agents_project_role"),
        Index("ix_agents_project_role", "project_id", "role"),
    )

    def __repr__(self) -> str:
        return f"<Agent id={self.id} role={self.role} project={self.project_id}>"


# ══════════════════════════════════════════════════════════════
# DEBATES
# Multi-round cross-ministerial arguments
# ══════════════════════════════════════════════════════════════

class Debate(Base):
    """
    One argument entry per minister per debate round.
    Multiple rounds supported (default 2).
    """
    __tablename__ = "debates"

    id                 = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id         = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"),
                                nullable=False, index=True)
    agent_id           = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"),
                                nullable=False, index=True)
    round_number       = Column(Integer, nullable=False)                        # 1-based
    argument           = Column(Text, nullable=False)
    supporting_agents  = Column(JSONB, nullable=False, default=list)           # List[str] — agent roles
    opposing_agents    = Column(JSONB, nullable=False, default=list)           # List[str] — agent roles
    word_count         = Column(Integer, nullable=True)
    created_at         = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ── Relationships ─────────────────────────────────────────
    project = relationship("Project", back_populates="debates")
    agent   = relationship("Agent",   back_populates="debates")

    __table_args__ = (
        Index("ix_debates_project_round", "project_id", "round_number"),
    )

    def __repr__(self) -> str:
        return f"<Debate id={self.id} round={self.round_number} agent={self.agent_id}>"


# ══════════════════════════════════════════════════════════════
# VOTES
# One vote per minister per project
# ══════════════════════════════════════════════════════════════

class Vote(Base):
    """
    Each minister casts one vote for their preferred policy option.
    Includes confidence score and written justification.
    """
    __tablename__ = "votes"

    id               = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id       = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"),
                              nullable=False, index=True)
    agent_id         = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"),
                              nullable=False, index=True)
    voted_option     = Column(String(500), nullable=False)
    confidence_score = Column(Float, nullable=False)                            # 0.0–100.0
    justification    = Column(Text, nullable=False)
    created_at       = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ── Relationships ─────────────────────────────────────────
    project = relationship("Project", back_populates="votes")
    agent   = relationship("Agent",   back_populates="vote")

    __table_args__ = (
        UniqueConstraint("project_id", "agent_id", name="uq_votes_project_agent"),
        Index("ix_votes_project_option", "project_id", "voted_option"),
    )

    def __repr__(self) -> str:
        return f"<Vote id={self.id} option={self.voted_option[:40]!r} confidence={self.confidence_score}>"


# ══════════════════════════════════════════════════════════════
# SIMULATIONS
# Synthetic stress-test results per policy option
# ══════════════════════════════════════════════════════════════

class Simulation(Base):
    """
    Synthetic simulation results for a specific policy option.
    Multiple simulations per project (one per candidate option).
    Composite score is stored for fast sorting queries.
    """
    __tablename__ = "simulations"

    id                         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id                 = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"),
                                        nullable=False, index=True)
    option_name                = Column(String(500), nullable=False)
    option_description         = Column(Text, nullable=True)

    # ── Dimension Scores (0–100) ──────────────────────────────
    economic_score             = Column(Float, nullable=False)
    social_score               = Column(Float, nullable=False)
    environmental_score        = Column(Float, nullable=False)
    feasibility_score          = Column(Float, nullable=False)
    composite_score            = Column(Float, nullable=False)                  # weighted average

    # ── Risk & Logistics ─────────────────────────────────────
    risk_level                 = Column(SAEnum(RiskLevel, name="risk_level_enum"),
                                        nullable=False, default=RiskLevel.MEDIUM)
    time_to_implement_months   = Column(Integer, nullable=False)
    cost_estimate_usd_millions = Column(Float, nullable=False)
    projected_population_impact= Column(Float, nullable=False)                  # millions of people

    # ── Narrative Outputs ─────────────────────────────────────
    key_risks                  = Column(JSONB, nullable=False, default=list)    # List[str]
    key_benefits               = Column(JSONB, nullable=False, default=list)    # List[str]
    scenario_data              = Column(JSONB, nullable=False, default=dict)    # 5 scenario breakdown

    created_at                 = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ── Relationships ─────────────────────────────────────────
    project = relationship("Project", back_populates="simulations")

    __table_args__ = (
        Index("ix_simulations_project_composite", "project_id", "composite_score"),
    )

    def __repr__(self) -> str:
        return f"<Simulation id={self.id} option={self.option_name[:40]!r} score={self.composite_score}>"


# ══════════════════════════════════════════════════════════════
# FINAL REPORTS
# Prime Minister's binding policy recommendation
# ══════════════════════════════════════════════════════════════

class FinalReport(Base):
    """
    The Prime Minister's final policy synthesis.
    One report per project (1:1 with projects).
    """
    __tablename__ = "final_reports"

    id                      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id              = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"),
                                     nullable=False, unique=True, index=True)

    # ── Policy Decision ───────────────────────────────────────
    chosen_option           = Column(String(500), nullable=False)
    executive_summary       = Column(Text, nullable=False)
    overall_rationale       = Column(Text, nullable=False)

    # ── Structured Output ─────────────────────────────────────
    implementation_steps    = Column(JSONB, nullable=False, default=list)       # List[PolicyStep]
    success_metrics         = Column(JSONB, nullable=False, default=list)       # List[str]
    risks_and_mitigations   = Column(JSONB, nullable=False, default=dict)       # Dict[str, str]
    expected_outcomes       = Column(JSONB, nullable=False, default=list)       # List[str]
    review_timeline         = Column(String(200), nullable=False)

    # ── Voting Summary ────────────────────────────────────────
    total_votes             = Column(Integer, nullable=False, default=0)
    winning_votes           = Column(Integer, nullable=False, default=0)
    vote_percentage         = Column(Float, nullable=False, default=0.0)        # % for chosen option
    consensus_level         = Column(String(50), nullable=False, default="moderate")  # low/moderate/high

    # ── Simulation Summary ────────────────────────────────────
    best_simulation_score   = Column(Float, nullable=True)
    model_used              = Column(String(100), nullable=False, default="gemini-1.5-pro")

    created_at              = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # ── Relationships ─────────────────────────────────────────
    project = relationship("Project", back_populates="final_report")

    def __repr__(self) -> str:
        return f"<FinalReport id={self.id} option={self.chosen_option[:40]!r} votes={self.vote_percentage}%>"


# ══════════════════════════════════════════════════════════════
# EXPORT — all models for Alembic auto-detection
# ══════════════════════════════════════════════════════════════
__all__ = [
    "Project",
    "Agent",
    "Debate",
    "Vote",
    "Simulation",
    "FinalReport",
    "ProjectStatus",
    "AgentRole",
    "RiskLevel",
]
