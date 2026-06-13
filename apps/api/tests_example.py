"""
TITAN Test Suite — Examples & Patterns
======================================
Comprehensive testing examples for backend components.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

# Import components to test
from app.core.validation import ProblemInputRequest, sanitize_text
from app.core.constants import DebatePhase, MinisterRole, SimulationMetric
from app.core.error_recovery import retry_with_backoff, CircuitBreaker
from app.core.cost_tracking import CostTracker, TokenUsage, SessionCostSummary


# ═══════════════════════════════════════════════════════════
# INPUT VALIDATION TESTS
# ═══════════════════════════════════════════════════════════

class TestInputValidation:
    """Test input sanitization and validation."""
    
    def test_valid_problem(self):
        """Test that valid problem passes validation."""
        req = ProblemInputRequest(
            problem="This is a valid problem statement about policy"
        )
        assert req.problem == "This is a valid problem statement about policy"
    
    def test_problem_too_short(self):
        """Test rejection of problem under 20 chars."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ProblemInputRequest(problem="too short")
    
    def test_problem_too_long(self):
        """Test rejection of problem over 5000 chars."""
        from pydantic import ValidationError
        long_text = "a" * 5001
        with pytest.raises(ValidationError):
            ProblemInputRequest(problem=long_text)
    
    def test_injection_attack_prevention(self):
        """Test that injection attempts are blocked."""
        from pydantic import ValidationError
        
        # Script injection
        with pytest.raises(ValidationError):
            ProblemInputRequest(problem="How to solve <script>alert('xss')</script> unemployment?")
        
        # Event handler injection
        with pytest.raises(ValidationError):
            ProblemInputRequest(problem="Policy on healthcare onclick=malicious()")
    
    def test_whitespace_normalization(self):
        """Test that multiple spaces are collapsed."""
        req = ProblemInputRequest(
            problem="Multiple    spaces    should    be    normalized"
        )
        assert "    " not in req.problem
        assert "Multiple spaces should be normalized" == req.problem
    
    def test_optional_context(self):
        """Test optional context field."""
        req = ProblemInputRequest(
            problem="Valid problem statement here",
            context=None
        )
        assert req.context is None
        
        req = ProblemInputRequest(
            problem="Valid problem statement here",
            context="Some valid context"
        )
        assert req.context == "Some valid context"
    
    def test_empty_context_becomes_none(self):
        """Test that empty string context becomes None."""
        req = ProblemInputRequest(
            problem="Valid problem statement here",
            context="   "
        )
        assert req.context is None


# ═══════════════════════════════════════════════════════════
# COST TRACKING TESTS
# ═══════════════════════════════════════════════════════════

class TestCostTracking:
    """Test cost tracking and budget management."""
    
    def test_token_usage_cost_calculation(self):
        """Test cost calculation for token usage."""
        usage = TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            model="gemini-1.5-flash",
            agent_role="economic_minister"
        )
        
        # Check costs (using Gemini pricing from cost_tracking.py)
        # gemini-1.5-flash: $0.075 per million input, $0.3 per million output
        expected_input_cost = (1000 / 1_000_000) * 0.075  # $0.000075
        expected_output_cost = (500 / 1_000_000) * 0.3     # $0.00015
        expected_total = expected_input_cost + expected_output_cost
        
        assert abs(usage.estimated_cost_usd - expected_total) < 0.00001
    
    def test_session_cost_summary(self):
        """Test cost summary aggregation."""
        summary = SessionCostSummary(session_id="test-123")
        
        usage1 = TokenUsage(
            input_tokens=1000,
            output_tokens=500,
            model="gemini-1.5-flash",
            agent_role="economic_minister"
        )
        
        usage2 = TokenUsage(
            input_tokens=2000,
            output_tokens=1000,
            model="gemini-1.5-flash",
            agent_role="environment_minister"
        )
        
        summary.add_usage(usage1, "analyzing")
        summary.add_usage(usage2, "debating")
        
        assert summary.total_input_tokens == 3000
        assert summary.total_output_tokens == 1500
        assert summary.total_tokens == 4500
        assert "economic_minister" in summary.token_usage_by_agent
        assert "analyzing" in summary.token_usage_by_phase
    
    def test_cost_tracker_budget_alert(self):
        """Test budget alert logic."""
        tracker = CostTracker("test-session")
        
        # Log usage under budget
        for i in range(5):
            tracker.log_usage(
                input_tokens=100,
                output_tokens=50,
                model="gemini-1.5-flash",
                agent_role="economic_minister",
                phase="analyzing"
            )
        
        # Should not exceed budget of $10
        assert not tracker.cost_exceeds_budget(10.0)
        
        # Log much more usage to exceed 80% threshold
        for i in range(1000):
            tracker.log_usage(
                input_tokens=1000,
                output_tokens=1000,
                model="gemini-1.5-pro",  # More expensive
                agent_role="prime_minister",
                phase="synthesizing"
            )
        
        # Should exceed small budget
        assert tracker.cost_exceeds_budget(0.01)


# ═══════════════════════════════════════════════════════════
# ERROR RECOVERY TESTS
# ═══════════════════════════════════════════════════════════

class TestErrorRecovery:
    """Test retry and circuit breaker logic."""
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_success_first_try(self):
        """Test successful operation on first attempt."""
        call_count = 0
        
        async def successful_op():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await retry_with_backoff(successful_op, max_attempts=3)
        
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_eventual_success(self):
        """Test eventual success after retries."""
        call_count = 0
        
        async def flaky_op():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError(f"Attempt {call_count} failed")
            return "success"
        
        result = await retry_with_backoff(
            flaky_op,
            max_attempts=5,
            initial_delay=0.01,  # Short delay for testing
            exponential_base=2.0
        )
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_exhaustion(self):
        """Test that retries are exhausted properly."""
        async def always_fails():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            await retry_with_backoff(
                always_fails,
                max_attempts=3,
                initial_delay=0.01
            )
    
    def test_circuit_breaker_state_transitions(self):
        """Test circuit breaker state machine."""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
        
        # Initial state
        assert breaker.state == "CLOSED"
        assert breaker.failure_count == 0
        
        # Record failures
        breaker._on_failure()
        breaker._on_failure()
        assert breaker.state == "CLOSED"
        
        # Third failure opens circuit
        breaker._on_failure()
        assert breaker.state == "OPEN"
        assert breaker.failure_count == 3
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_prevents_cascading(self):
        """Test that circuit breaker prevents cascading failures."""
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=10)
        
        async def flaky_service():
            raise ValueError("Service down")
        
        # First two calls fail and trigger circuit open
        with pytest.raises(ValueError):
            await breaker.call(flaky_service)
        
        with pytest.raises(ValueError):
            await breaker.call(flaky_service)
        
        # Third call should fail with CircuitBreakerError, not try again
        from app.core.error_recovery import CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            await breaker.call(flaky_service)


# ═══════════════════════════════════════════════════════════
# CONSTANTS TESTS
# ═══════════════════════════════════════════════════════════

class TestConstants:
    """Test constants definitions."""
    
    def test_debate_phases_enum(self):
        """Test debate phase enum values."""
        assert DebatePhase.PENDING.value == "pending"
        assert DebatePhase.ANALYZING.value == "analyzing"
        assert DebatePhase.COMPLETED.value == "completed"
    
    def test_minister_roles_enum(self):
        """Test minister role enum values."""
        assert MinisterRole.ECONOMIC_MINISTER.value == "economic_minister"
        assert MinisterRole.OPPOSITION_MINISTER.value == "opposition_minister"
    
    def test_simulation_metrics(self):
        """Test simulation metrics."""
        metrics = [
            SimulationMetric.ECONOMIC_IMPACT,
            SimulationMetric.SUSTAINABILITY,
            SimulationMetric.CITIZEN_SATISFACTION,
            SimulationMetric.IMPLEMENTATION_COST,
            SimulationMetric.RISK_RESILIENCE,
        ]
        assert len(metrics) == 5
    
    def test_minister_metadata_completeness(self):
        """Test that all ministers have metadata."""
        from app.core.constants import MINISTER_DISPLAY_NAMES, MINISTER_DESCRIPTIONS
        
        for role in MinisterRole:
            assert role in MINISTER_DISPLAY_NAMES, f"Missing display name for {role}"
            assert role in MINISTER_DESCRIPTIONS, f"Missing description for {role}"


# ═══════════════════════════════════════════════════════════
# INTEGRATION TEST EXAMPLE
# ═══════════════════════════════════════════════════════════

class TestIntegration:
    """Integration tests for multi-component flows."""
    
    def test_full_request_validation_flow(self):
        """Test complete validation pipeline."""
        # Valid request
        req = ProblemInputRequest(
            problem="How can we reduce urban unemployment by 50% in 5 years?",
            context="Current unemployment rate is 8%, budget available is $500B"
        )
        
        assert len(req.problem) >= 20
        assert req.context is not None
        
        # Convert to dict for API
        data = {
            "problem": req.problem,
            "context": req.context,
        }
        
        # Should be able to recreate from dict
        req2 = ProblemInputRequest(**data)
        assert req2.problem == req.problem


# ═══════════════════════════════════════════════════════════
# FIXTURES FOR COMMON TEST SETUP
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def sample_problem():
    """Sample valid problem statement."""
    return "How can India transition to 100% renewable energy by 2035 without economic disruption?"


@pytest.fixture
def sample_context():
    """Sample context for problem."""
    return "Current renewable penetration is 40%, fossil fuel jobs employ 2.5M people"


@pytest.fixture
def mock_llm():
    """Mock LLM for testing without API calls."""
    mock = AsyncMock()
    mock.return_value = {
        "situation_assessment": "Test assessment",
        "key_findings": ["Finding 1", "Finding 2"],
        "proposed_solutions": ["Solution 1"],
        "concerns": ["Concern 1"],
        "confidence": 0.85
    }
    return mock


@pytest.fixture
def cost_tracker():
    """Create cost tracker for testing."""
    return CostTracker("test-session-id")


# ═══════════════════════════════════════════════════════════
# PYTEST CONFIGURATION
# ═══════════════════════════════════════════════════════════

# pytest.ini or pyproject.toml:
# [tool:pytest]
# testpaths = tests
# asyncio_mode = auto
# addopts = --strict-markers -v

# conftest.py entries
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
