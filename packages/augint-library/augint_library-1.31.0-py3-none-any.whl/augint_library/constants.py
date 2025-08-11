"""Constants for augint-library configuration values.

This module provides named constants for all magic numbers used throughout the library,
improving maintainability and providing a single source of truth for configuration values.

The constants are organized into logical groups:
- Resilience: Retry and circuit breaker configuration
- Network: API timeouts and connection settings
- Percentage: Rate and percentage boundaries
- Hash/ID: Hashing and identifier configuration
- CLI: Command-line interface specific values
- Data Processing: Batch and formatting settings
"""

# =============================================================================
# Resilience - Retry Configuration
# =============================================================================

# Default retry attempts for operations that can be retried
DEFAULT_RETRY_ATTEMPTS: int = 3

# Initial delay between retry attempts in seconds
DEFAULT_INITIAL_DELAY: float = 1.0

# Maximum delay between retry attempts in seconds
DEFAULT_MAX_DELAY: float = 60.0

# Exponential backoff base multiplier
DEFAULT_EXPONENTIAL_BASE: float = 2.0

# Jitter factors for randomizing delays to avoid thundering herd
JITTER_MIN_FACTOR: float = 0.5  # 50% minimum delay multiplier
JITTER_MAX_FACTOR: float = 1.0  # 100% maximum delay multiplier (adds to min for 150% total)

# =============================================================================
# Resilience - Circuit Breaker Configuration
# =============================================================================

# Number of consecutive failures before circuit breaker opens
DEFAULT_FAILURE_THRESHOLD: int = 5

# Time in seconds before attempting to close an open circuit breaker
DEFAULT_RECOVERY_TIMEOUT: float = 60.0

# Number of consecutive successes required to close circuit breaker
DEFAULT_SUCCESS_THRESHOLD: int = 2

# =============================================================================
# Network and API Configuration
# =============================================================================

# Default timeout for API calls in seconds
DEFAULT_API_TIMEOUT: float = 1.0

# Default timeout for data processor operations in seconds
DEFAULT_DATA_PROCESSOR_TIMEOUT: int = 30

# Default timeout for telemetry flush operations in seconds
DEFAULT_TELEMETRY_FLUSH_TIMEOUT: float = 2.0

# Minimum delay for simulation operations in seconds
SIMULATION_DELAY_MIN: float = 0.1

# Multiplier for timeout when simulating failures (120% of timeout)
TIMEOUT_FAILURE_MULTIPLIER: float = 1.2

# Multiplier for timeout when simulating successes (80% of timeout)
TIMEOUT_SUCCESS_MULTIPLIER: float = 0.8

# =============================================================================
# Feature Flags and Percentage Configuration
# =============================================================================

# Default failure rate for operations (30%)
DEFAULT_FAILURE_RATE: float = 0.3

# Minimum percentage value for feature flag rollouts
PERCENTAGE_MIN: int = 0

# Maximum percentage value for feature flag rollouts
PERCENTAGE_MAX: int = 100

# Default telemetry sampling rate (10% of operations)
TELEMETRY_SAMPLE_RATE: float = 0.1

# =============================================================================
# Hash and Identifier Configuration
# =============================================================================

# Length of hash prefix used for feature flag bucketing
HASH_PREFIX_LENGTH: int = 8

# Maximum value for random user ID generation
USER_ID_RANDOM_MAX: int = 10**9

# =============================================================================
# CLI and User Interface Configuration
# =============================================================================

# Initial delay for CLI resilient operations in seconds
CLI_RESILIENT_INITIAL_DELAY: float = 0.5

# Recovery timeout for CLI circuit breaker in seconds
CLI_RESILIENT_RECOVERY_TIMEOUT: int = 30

# Length of separator lines in CLI output
CLI_SEPARATOR_LENGTH: int = 60

# =============================================================================
# Data Processing Configuration
# =============================================================================

# Default chunk size for batch processing operations
DEFAULT_BATCH_CHUNK_SIZE: int = 100

# Indentation level for JSON formatting
JSON_INDENT: int = 2
