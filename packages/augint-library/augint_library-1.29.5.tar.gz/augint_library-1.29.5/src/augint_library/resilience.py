"""Resilience patterns for handling transient failures.

This module provides production-ready retry and circuit breaker patterns for
building fault-tolerant systems. It demonstrates:
- Retry with exponential backoff and jitter
- Circuit breaker pattern to prevent cascading failures
- Thread-safe implementations
- Monitoring and observability hooks

Common Use Cases:
    1. External API calls that may fail transiently
    2. Database operations during high load
    3. Microservice communication
    4. Preventing thundering herd problems
    5. Graceful degradation of services

Examples:
    Basic retry pattern:
    >>> from augint_library.resilience import retry
    >>>
    >>> @retry(max_attempts=3, initial_delay=1.0)
    >>> def call_flaky_api():
    ...     # This might fail occasionally
    ...     response = requests.get("https://api.example.com/data")
    ...     return response.json()

    Circuit breaker for cascading failure prevention:
    >>> from augint_library.resilience import circuit_breaker
    >>>
    >>> @circuit_breaker(failure_threshold=5, recovery_timeout=60)
    >>> def call_payment_service(amount):
    ...     # If this fails 5 times, circuit opens for 60 seconds
    ...     return payment_api.charge(amount)

    Combining patterns for maximum resilience:
    >>> @circuit_breaker(failure_threshold=5, recovery_timeout=60)
    >>> @retry(max_attempts=3, initial_delay=0.5)
    >>> def robust_api_call(endpoint):
    ...     # Circuit breaker prevents overwhelming a failing service
    ...     # Retry handles transient network issues
    ...     return fetch_data(endpoint)

    Monitoring circuit breaker state:
    >>> from augint_library.resilience import get_circuit_breakers
    >>>
    >>> # Check all circuit breakers
    >>> states = get_circuit_breakers()
    >>> for name, state in states.items():
    ...     print(f"{name}: {state['state']} (failures: {state['failure_count']})")

    Handling circuit breaker exceptions:
    >>> from augint_library.resilience import CircuitOpenError
    >>>
    >>> try:
    ...     result = call_payment_service(100)
    ... except CircuitOpenError as e:
    ...     # Circuit is open, use fallback
    ...     logger.warning(f"Payment service down: {e}")
    ...     return {"status": "queued", "retry_after": e.details['retry_after']}

Best Practices:
    1. Always set reasonable timeouts on retried operations
    2. Use jitter to prevent thundering herd
    3. Monitor circuit breaker states
    4. Have fallback strategies when circuits open
    5. Log all retry attempts and circuit state changes

Configuration Guidelines:
    Retry:
    - max_attempts: 3-5 for user-facing, up to 10 for background
    - initial_delay: 0.1-1.0 seconds
    - exponential_base: 2.0 (doubles each time)
    - jitter: True (prevents synchronized retries)

    Circuit Breaker:
    - failure_threshold: 5-10 consecutive failures
    - recovery_timeout: 30-300 seconds
    - success_threshold: 2-5 successes to close

Advanced Patterns:
    Custom retry conditions:
    >>> @retry(max_attempts=3, retryable_exceptions=(TimeoutError, ConnectionError))
    >>> def network_operation():
    ...     # Only retries on specific network errors
    ...     pass

    Circuit breaker with half-open testing:
    >>> @circuit_breaker(
    ...     failure_threshold=5,
    ...     recovery_timeout=60,
    ...     success_threshold=3  # Need 3 successes to fully close
    ... )
    >>> def gradual_recovery_service():
    ...     pass

Note:
    These patterns are thread-safe but not process-safe. For distributed
    systems, consider using Redis-backed circuit breakers or service mesh
    features like Istio/Envoy.
"""

import random
import time
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from threading import Lock
from typing import Any, Callable, Optional

from .constants import (
    DEFAULT_EXPONENTIAL_BASE,
    DEFAULT_FAILURE_THRESHOLD,
    DEFAULT_INITIAL_DELAY,
    DEFAULT_MAX_DELAY,
    DEFAULT_RECOVERY_TIMEOUT,
    DEFAULT_RETRY_ATTEMPTS,
    DEFAULT_SUCCESS_THRESHOLD,
    JITTER_MAX_FACTOR,
    JITTER_MIN_FACTOR,
)
from .exceptions import AugintError, ErrorCode


class CircuitState(Enum):
    """States for the circuit breaker pattern."""

    CLOSED = "closed"  # Normal operation, requests pass through
    OPEN = "open"  # Failures exceeded threshold, requests are blocked
    HALF_OPEN = "half_open"  # Testing if service has recovered


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = DEFAULT_RETRY_ATTEMPTS
    initial_delay: float = DEFAULT_INITIAL_DELAY
    max_delay: float = DEFAULT_MAX_DELAY
    exponential_base: float = DEFAULT_EXPONENTIAL_BASE
    jitter: bool = True
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,)


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""

    failure_threshold: int = DEFAULT_FAILURE_THRESHOLD
    recovery_timeout: float = DEFAULT_RECOVERY_TIMEOUT
    success_threshold: int = DEFAULT_SUCCESS_THRESHOLD
    expected_exception: type[Exception] = Exception


class CircuitOpenError(AugintError):
    """Raised when circuit breaker is open and rejecting requests."""

    def __init__(self, service: str, recovery_time: float) -> None:
        """Initialize CircuitOpenError."""
        super().__init__(
            f"Circuit breaker is OPEN for {service}",
            code=ErrorCode.NETWORK_ERROR,
            details={
                "service": service,
                "recovery_in": f"{recovery_time:.1f}s",
                "state": CircuitState.OPEN.value,
            },
        )


class CircuitBreaker:
    """Circuit breaker implementation to prevent cascading failures."""

    def __init__(self, name: str, config: CircuitBreakerConfig):
        """Initialize circuit breaker."""
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self._lock = Lock()

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute function through circuit breaker."""
        with self._lock:
            # Check if we should transition from OPEN to HALF_OPEN
            if self.state == CircuitState.OPEN:
                if (
                    self.last_failure_time
                    and time.time() - self.last_failure_time >= self.config.recovery_timeout
                ):
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    recovery_time = self.config.recovery_timeout - (
                        time.time() - (self.last_failure_time or 0)
                    )
                    raise CircuitOpenError(self.name, recovery_time)

        try:
            result = func(*args, **kwargs)
        except self.config.expected_exception:
            self._on_failure()
            raise
        else:
            self._on_success()
            return result

    def _on_success(self) -> None:
        """Handle successful call."""
        with self._lock:
            self.failure_count = 0

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED

    def _on_failure(self) -> None:
        """Handle failed call."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == CircuitState.HALF_OPEN or (
                self.state == CircuitState.CLOSED
                and self.failure_count >= self.config.failure_threshold
            ):
                self.state = CircuitState.OPEN

    def get_state(self) -> dict[str, Any]:
        """Get current circuit breaker state."""
        with self._lock:
            return {
                "name": self.name,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "last_failure": self.last_failure_time,
            }


# Global registry for circuit breakers (for CLI inspection)
_circuit_breakers: dict[str, CircuitBreaker] = {}
_registry_lock = Lock()


def retry(
    max_attempts: int = DEFAULT_RETRY_ATTEMPTS,
    initial_delay: float = DEFAULT_INITIAL_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    exponential_base: float = DEFAULT_EXPONENTIAL_BASE,
    jitter: bool = True,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for retrying functions with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts.
        initial_delay: Initial delay between retries in seconds.
        max_delay: Maximum delay between retries.
        exponential_base: Base for exponential backoff.
        jitter: Whether to add random jitter to delays.
        retryable_exceptions: Tuple of exceptions to retry on.

    Returns:
        Decorated function that implements retry logic.

    Example:
        >>> @retry(max_attempts=3, initial_delay=1.0)
        ... def flaky_operation():
        ...     # This might fail transiently
        ...     return fetch_external_data()
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        initial_delay=initial_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        retryable_exceptions=retryable_exceptions,
    )

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Optional[Exception] = None

            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e

                    if attempt == config.max_attempts - 1:
                        # Last attempt, re-raise
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(
                        config.initial_delay * (config.exponential_base**attempt), config.max_delay
                    )

                    # Add jitter to prevent thundering herd
                    if config.jitter:
                        delay *= JITTER_MIN_FACTOR + (random.random() * JITTER_MAX_FACTOR)  # noqa: S311 - jitter for backoff

                    time.sleep(delay)

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
            return None

        return wrapper

    return decorator


def circuit_breaker(
    failure_threshold: int = DEFAULT_FAILURE_THRESHOLD,
    recovery_timeout: float = DEFAULT_RECOVERY_TIMEOUT,
    success_threshold: int = DEFAULT_SUCCESS_THRESHOLD,
    expected_exception: type[Exception] = Exception,
    name: Optional[str] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for circuit breaker pattern.

    Args:
        failure_threshold: Number of failures before opening circuit.
        recovery_timeout: Time in seconds before attempting recovery.
        success_threshold: Successes needed to close circuit from half-open.
        expected_exception: Exception type that indicates failure.
        name: Optional name for the circuit breaker.

    Returns:
        Decorated function with circuit breaker protection.

    Example:
        >>> @circuit_breaker(failure_threshold=5, recovery_timeout=60)
        ... def call_external_service():
        ...     return requests.get("https://api.example.com/data")
    """
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        success_threshold=success_threshold,
        expected_exception=expected_exception,
    )

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Use function name as circuit breaker name if not provided
        cb_name = name or f"{func.__module__}.{func.__name__}"

        # Get or create circuit breaker
        with _registry_lock:
            if cb_name not in _circuit_breakers:
                _circuit_breakers[cb_name] = CircuitBreaker(cb_name, config)
            cb = _circuit_breakers[cb_name]

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return cb.call(func, *args, **kwargs)

        return wrapper

    return decorator


def get_circuit_breakers() -> dict[str, dict[str, Any]]:
    """Get status of all circuit breakers.

    Returns:
        Dictionary mapping circuit breaker names to their states.
    """
    with _registry_lock:
        return {name: cb.get_state() for name, cb in _circuit_breakers.items()}


def reset_circuit_breaker(name: str) -> bool:
    """Reset a specific circuit breaker.

    Args:
        name: Name of the circuit breaker to reset.

    Returns:
        True if reset was successful, False if breaker not found.
    """
    with _registry_lock:
        if name in _circuit_breakers:
            cb = _circuit_breakers[name]
            with cb._lock:
                cb.state = CircuitState.CLOSED
                cb.failure_count = 0
                cb.success_count = 0
                cb.last_failure_time = None
            return True
    return False
