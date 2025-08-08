"""A Python library built with enterprise-grade tooling.

This library provides a solid foundation with comprehensive testing,
security scanning, and automated documentation.
"""

from .core import fetch_data, print_hi
from .exceptions import (
    AugintError,
    ConfigurationError,
    ErrorCode,
    MultiError,
    NetworkError,
    NetworkTimeoutError,
    RateLimitError,
    ResourceAlreadyExistsError,
    ResourceError,
    ResourceNotFoundError,
    ValidationError,
    collect_errors,
    error_context,
    handle_exceptions,
)
from .feature_flags import FeatureFlags, feature_flag, get_flags
from .logging import setup_logging
from .protocols import (
    AdvancedProcessor,
    CacheProvider,
    ConfigurableClient,
    DataProcessor,
    EventHandler,
    ProcessingResult,
)
from .resilience import (
    CircuitBreakerConfig,
    CircuitOpenError,
    CircuitState,
    RetryConfig,
    circuit_breaker,
    get_circuit_breakers,
    reset_circuit_breaker,
    retry,
)

# Telemetry imports (optional - requires telemetry group dependencies)
try:
    from .telemetry import TelemetryClient, get_telemetry_client, track_command_execution

    TELEMETRY_AVAILABLE = True
except ImportError:
    # Telemetry module requires optional dependencies
    TELEMETRY_AVAILABLE = False

    # Create dummy implementations when telemetry is not available
    from typing import Any, Callable

    class TelemetryClient:  # type: ignore[no-redef]
        """Dummy TelemetryClient when telemetry dependencies are not installed."""

        def __init__(self) -> None:
            raise ImportError(
                "Telemetry requires optional dependencies. "
                "Install with: poetry install --with telemetry"
            )

    def get_telemetry_client() -> "TelemetryClient":
        """Dummy function when telemetry dependencies are not installed."""
        raise ImportError(
            "Telemetry requires optional dependencies. "
            "Install with: poetry install --with telemetry"
        )

    def track_command_execution(func: Callable[..., Any]) -> Callable[..., Any]:
        """Dummy decorator when telemetry dependencies are not installed."""
        return func


__version__ = "1.25.0"

__all__ = [
    # Protocols
    "AdvancedProcessor",
    # Exceptions
    "AugintError",
    "CacheProvider",
    "CircuitBreakerConfig",
    "CircuitOpenError",
    "CircuitState",
    "ConfigurableClient",
    "ConfigurationError",
    "DataProcessor",
    "ErrorCode",
    "EventHandler",
    # Feature Flags
    "FeatureFlags",
    "MultiError",
    "NetworkError",
    "NetworkTimeoutError",
    "ProcessingResult",
    "RateLimitError",
    "ResourceAlreadyExistsError",
    "ResourceError",
    "ResourceNotFoundError",
    "RetryConfig",
    "ValidationError",
    # Utilities and metadata
    "__version__",
    # Resilience patterns
    "circuit_breaker",
    "collect_errors",
    "error_context",
    # Feature flags
    "feature_flag",
    # Core functions
    "fetch_data",
    "get_circuit_breakers",
    # Feature flags
    "get_flags",
    "handle_exceptions",
    "print_hi",
    "reset_circuit_breaker",
    "retry",
    "setup_logging",
]

# Add telemetry exports only if available
if TELEMETRY_AVAILABLE:
    __all__.extend(
        [
            "TelemetryClient",
            "get_telemetry_client",
            "track_command_execution",
        ]
    )
