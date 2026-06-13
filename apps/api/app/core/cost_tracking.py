"""
Cost Tracking & Analytics
=========================
Monitors LLM token usage and associated costs for budget management.
"""
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger(__name__)


# Gemini API pricing (as of 2024)
GEMINI_PRICING = {
    "gemini-1.5-flash": {
        "input_per_million_tokens": 0.075,
        "output_per_million_tokens": 0.3,
    },
    "gemini-1.5-pro": {
        "input_per_million_tokens": 1.50,
        "output_per_million_tokens": 6.00,
    },
}


@dataclass
class TokenUsage:
    """Record of tokens used in a single LLM call."""
    input_tokens: int
    output_tokens: int
    model: str
    agent_role: str
    timestamp: str = field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())
    
    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens
    
    @property
    def estimated_cost_usd(self) -> float:
        """Calculate estimated cost for this token usage."""
        pricing = GEMINI_PRICING.get(self.model, {})
        if not pricing:
            return 0.0
        
        input_cost = (self.input_tokens / 1_000_000) * pricing["input_per_million_tokens"]
        output_cost = (self.output_tokens / 1_000_000) * pricing["output_per_million_tokens"]
        
        return round(input_cost + output_cost, 6)


@dataclass
class SessionCostSummary:
    """Aggregate cost metrics for a governance session."""
    session_id: str
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    estimated_total_cost_usd: float = 0.0
    token_usage_by_agent: Dict[str, Dict] = field(default_factory=dict)
    token_usage_by_phase: Dict[str, Dict] = field(default_factory=dict)
    estimated_cost_by_phase: Dict[str, float] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())
    
    def add_usage(self, usage: TokenUsage, phase: str) -> None:
        """Add a token usage record to summary."""
        self.total_input_tokens += usage.input_tokens
        self.total_output_tokens += usage.output_tokens
        self.total_tokens = self.total_input_tokens + self.total_output_tokens
        self.estimated_total_cost_usd += usage.estimated_cost_usd
        
        # Track by agent
        if usage.agent_role not in self.token_usage_by_agent:
            self.token_usage_by_agent[usage.agent_role] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "estimated_cost_usd": 0.0,
            }
        
        agent_stats = self.token_usage_by_agent[usage.agent_role]
        agent_stats["input_tokens"] += usage.input_tokens
        agent_stats["output_tokens"] += usage.output_tokens
        agent_stats["total_tokens"] += usage.total_tokens
        agent_stats["estimated_cost_usd"] += usage.estimated_cost_usd
        
        # Track by phase
        if phase not in self.token_usage_by_phase:
            self.token_usage_by_phase[phase] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "estimated_cost_usd": 0.0,
                "call_count": 0,
            }
        
        phase_stats = self.token_usage_by_phase[phase]
        phase_stats["input_tokens"] += usage.input_tokens
        phase_stats["output_tokens"] += usage.output_tokens
        phase_stats["total_tokens"] += usage.total_tokens
        phase_stats["estimated_cost_usd"] += usage.estimated_cost_usd
        phase_stats["call_count"] += 1
        
        if phase not in self.estimated_cost_by_phase:
            self.estimated_cost_by_phase[phase] = 0.0
        self.estimated_cost_by_phase[phase] += usage.estimated_cost_usd
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return {
            "session_id": self.session_id,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_tokens,
            "estimated_total_cost_usd": round(self.estimated_total_cost_usd, 6),
            "token_usage_by_agent": self.token_usage_by_agent,
            "token_usage_by_phase": self.token_usage_by_phase,
            "estimated_cost_by_phase": {
                phase: round(cost, 6)
                for phase, cost in self.estimated_cost_by_phase.items()
            },
            "created_at": self.created_at,
        }


class CostTracker:
    """Tracks costs for a single session."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.summary = SessionCostSummary(session_id=session_id)
    
    def log_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str,
        agent_role: str,
        phase: str,
    ) -> None:
        """Record token usage from an LLM call."""
        usage = TokenUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            agent_role=agent_role,
        )
        
        cost = usage.estimated_cost_usd
        
        logger.info(
            "token_usage_recorded",
            session_id=self.session_id,
            agent=agent_role,
            phase=phase,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=usage.total_tokens,
            estimated_cost_usd=cost,
        )
        
        self.summary.add_usage(usage, phase)
    
    def get_summary(self) -> SessionCostSummary:
        """Get current cost summary."""
        return self.summary
    
    def get_phase_cost(self, phase: str) -> float:
        """Get estimated cost for specific phase."""
        return self.summary.estimated_cost_by_phase.get(phase, 0.0)
    
    def get_agent_cost(self, agent_role: str) -> float:
        """Get estimated cost for specific agent."""
        if agent_role in self.summary.token_usage_by_agent:
            return self.summary.token_usage_by_agent[agent_role]["estimated_cost_usd"]
        return 0.0
    
    def cost_exceeds_budget(self, budget_usd: float) -> bool:
        """Check if costs exceed budget threshold."""
        return self.summary.estimated_total_cost_usd > budget_usd
    
    def log_budget_alert(self, budget_usd: float) -> None:
        """Log alert if approaching budget limit."""
        current_cost = self.summary.estimated_total_cost_usd
        if current_cost > budget_usd * 0.8:  # Alert at 80% of budget
            logger.warning(
                "budget_alert",
                session_id=self.session_id,
                current_cost_usd=round(current_cost, 6),
                budget_usd=budget_usd,
                percent_of_budget=round((current_cost / budget_usd) * 100, 1),
            )


# Global cost tracker per session
_session_cost_trackers: Dict[str, CostTracker] = {}


def get_cost_tracker(session_id: str) -> CostTracker:
    """Get or create cost tracker for session."""
    if session_id not in _session_cost_trackers:
        _session_cost_trackers[session_id] = CostTracker(session_id)
    return _session_cost_trackers[session_id]


def cleanup_tracker(session_id: str) -> Optional[SessionCostSummary]:
    """Remove tracker and return final summary."""
    tracker = _session_cost_trackers.pop(session_id, None)
    if tracker:
        logger.info(
            "cost_tracker_finalized",
            session_id=session_id,
            total_cost_usd=round(tracker.summary.estimated_total_cost_usd, 6),
        )
        return tracker.summary
    return None
