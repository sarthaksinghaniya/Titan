"""
Error Recovery & Retry Utilities
=================================
Implements exponential backoff, circuit breaker, and graceful degradation.
"""
import asyncio
import logging
from typing import TypeVar, Callable, Any, Optional
from functools import wraps
import structlog

logger = structlog.get_logger(__name__)

T = TypeVar('T')


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Simple circuit breaker for preventing cascade failures.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests fail immediately
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        """
        Args:
            failure_threshold: Number of failures before opening
            recovery_timeout: Seconds before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute func through circuit breaker."""
        if self.state == "OPEN":
            if self._should_attempt_recovery():
                self.state = "HALF_OPEN"
                logger.info("circuit_breaker_half_open", timeout=self.recovery_timeout)
            else:
                raise CircuitBreakerError(
                    f"Circuit breaker open. Recovers in {self._time_until_recovery()}s"
                )
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self) -> None:
        """Reset on success."""
        if self.state == "HALF_OPEN":
            logger.info("circuit_breaker_closed")
        self.state = "CLOSED"
        self.failure_count = 0
    
    def _on_failure(self) -> None:
        """Record failure and potentially open circuit."""
        import time
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning("circuit_breaker_opened", failures=self.failure_count)
    
    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        import time
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _time_until_recovery(self) -> int:
        """Seconds until recovery attempt."""
        import time
        if self.last_failure_time is None:
            return 0
        elapsed = time.time() - self.last_failure_time
        return max(0, int(self.recovery_timeout - elapsed))


async def retry_with_backoff(
    func: Callable[..., T],
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    *args,
    **kwargs
) -> T:
    """
    Retry async function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Multiplier for exponential backoff
        jitter: Add random jitter to delays
        *args, **kwargs: Arguments to pass to func
        
    Returns:
        Result of func if successful
        
    Raises:
        The last exception if all retries exhausted
    """
    import random
    
    last_exception = None
    delay = initial_delay
    
    for attempt in range(1, max_attempts + 1):
        try:
            logger.debug(
                "retry_attempt",
                attempt=attempt,
                max_attempts=max_attempts,
                func=func.__name__
            )
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            if attempt == max_attempts:
                logger.error(
                    "retry_exhausted",
                    func=func.__name__,
                    attempts=max_attempts,
                    error=str(e)
                )
                raise
            
            # Calculate delay with jitter
            if jitter:
                delay = delay * exponential_base * (0.5 + random.random())
            else:
                delay = delay * exponential_base
            
            delay = min(delay, max_delay)
            
            logger.warning(
                "retry_waiting",
                func=func.__name__,
                attempt=attempt,
                delay_seconds=delay,
                error=str(e)
            )
            
            await asyncio.sleep(delay)
    
    raise last_exception


def retry_decorator(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
):
    """
    Decorator for retrying async functions.
    
    Usage:
        @retry_decorator(max_attempts=3)
        async def flaky_operation():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_with_backoff(
                func,
                max_attempts=max_attempts,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                *args,
                **kwargs
            )
        return wrapper
    return decorator


class TimeoutManager:
    """Manages timeout handling for long-running operations."""
    
    @staticmethod
    async def with_timeout(
        coro,
        timeout_seconds: float,
        operation_name: str = "operation",
        fallback=None
    ):
        """
        Execute coroutine with timeout and optional fallback.
        
        Args:
            coro: Coroutine to execute
            timeout_seconds: Timeout in seconds
            operation_name: Name for logging
            fallback: Value to return if timeout occurs
            
        Returns:
            Result of coro, or fallback value if timeout
            
        Raises:
            asyncio.TimeoutError if no fallback provided
        """
        try:
            logger.debug(f"timeout_starting", op=operation_name, timeout=timeout_seconds)
            result = await asyncio.wait_for(coro, timeout=timeout_seconds)
            logger.debug(f"timeout_completed", op=operation_name)
            return result
        except asyncio.TimeoutError:
            logger.error(f"timeout_exceeded", op=operation_name, timeout=timeout_seconds)
            if fallback is not None:
                logger.info(f"timeout_using_fallback", op=operation_name)
                return fallback
            raise


# Global circuit breakers for external services
gemini_api_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
database_breaker = CircuitBreaker(failure_threshold=10, recovery_timeout=30)


async def call_with_breaker(
    breaker: CircuitBreaker,
    func: Callable,
    *args,
    **kwargs
) -> Any:
    """Call function through circuit breaker."""
    return await breaker.call(func, *args, **kwargs)
