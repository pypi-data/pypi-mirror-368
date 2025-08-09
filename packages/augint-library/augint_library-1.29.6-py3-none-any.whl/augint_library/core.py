"""Core library functions for augint-library.

This module demonstrates the fundamental pattern for creating library functions
that can be used both programmatically and through a CLI. It showcases:
- Simple, focused functions with clear purposes
- Proper error handling with custom exceptions
- Type hints for better IDE support
- Comprehensive docstrings with examples

Common Use Cases:
    1. Direct library usage in Python scripts
    2. Building CLIs that wrap library functions
    3. Creating testable, reusable components
    4. Demonstrating error simulation for testing

Example:
    Basic library usage:
    >>> from augint_library import print_hi, fetch_data
    >>>
    >>> # Simple function call
    >>> print_hi("World")
    Hi World
    >>>
    >>> # Function with error handling
    >>> try:
    ...     data = fetch_data("/api/users", timeout=5.0)
    ...     print(f"Success: {data['status']}")
    ... except NetworkError as e:
    ...     print(f"Failed: {e.message}")

    Building a CLI wrapper:
    >>> import click
    >>> from augint_library import print_hi
    >>>
    >>> @click.command()
    >>> @click.argument('name')
    >>> def greet(name):
    ...     '''Greet someone.'''
    ...     print_hi(name)

Note:
    This module uses simple examples to demonstrate patterns that scale
    to complex production libraries. The patterns shown here (error handling,
    type hints, documentation) should be applied consistently across all
    library modules.
"""

import random
import time
from typing import Any

from .constants import (
    DEFAULT_API_TIMEOUT,
    DEFAULT_FAILURE_RATE,
    SIMULATION_DELAY_MIN,
    TIMEOUT_FAILURE_MULTIPLIER,
    TIMEOUT_SUCCESS_MULTIPLIER,
)
from .exceptions import NetworkError, NetworkTimeoutError


def print_hi(name: str) -> None:
    """Print a friendly greeting to the given name.

    This is the main library function that can be imported and used
    in other Python code.

    Args:
        name: The name of the person to greet.

    Example:
        >>> print_hi("Alice")
        Hi Alice
    """
    print(f"Hi {name}")


def fetch_data(
    endpoint: str, timeout: float = DEFAULT_API_TIMEOUT, failure_rate: float = DEFAULT_FAILURE_RATE
) -> dict[str, Any]:
    """Fetch data from a remote endpoint (simulated).

    This function simulates an external API call that might fail transiently.
    It's designed to demonstrate when retry and circuit breaker patterns are useful.

    In a real application, this would make an actual HTTP request to an external service.
    The simulation allows us to control failure rates for testing and demonstration.

    Args:
        endpoint: The API endpoint to fetch from.
        timeout: Maximum time to wait for response (seconds).
        failure_rate: Probability of failure (0.0-1.0) for simulation.

    Returns:
        A dictionary containing the fetched data.

    Raises:
        NetworkTimeoutError: If the request times out.
        NetworkError: If the network request fails.

    Examples:
        Basic usage with guaranteed success:
        >>> data = fetch_data("/api/users", timeout=2.0, failure_rate=0.0)
        >>> print(data["status"])
        ok
        >>> print(data["endpoint"])
        /api/users

        Handling timeout errors:
        >>> try:
        ...     data = fetch_data("/api/slow", timeout=0.001)
        ... except NetworkTimeoutError as e:
        ...     print(f"Timeout: {e.message}")
        ...     print(f"Service: {e.details['service']}")
        Timeout: Timeout connecting to API endpoint /api/slow after 0.001s
        Service: API endpoint /api/slow

        Using with retry decorator for resilience:
        >>> from augint_library.resilience import retry
        >>>
        >>> @retry(max_attempts=3, initial_delay=0.1)
        ... def reliable_fetch(endpoint):
        ...     return fetch_data(endpoint, failure_rate=0.5)
        >>>
        >>> # This will retry up to 3 times on failure
        >>> data = reliable_fetch("/api/data")

        Testing error conditions:
        >>> # Force a failure for testing
        >>> try:
        ...     data = fetch_data("/api/test", failure_rate=1.0)
        ... except NetworkError as e:
        ...     print(f"Expected failure: {e.code.value}")
        Expected failure: NETWORK_ERROR

    Note:
        This function is intentionally simple to demonstrate patterns.
        In production, you would:
        - Use actual HTTP libraries (requests, httpx, urllib)
        - Add authentication and headers
        - Handle different status codes
        - Parse response formats (JSON, XML, etc.)
        - Add logging and metrics
    """
    # Simulate network delay
    if failure_rate > 0:
        # Allow delays that might exceed timeout when failures are possible
        delay = random.uniform(SIMULATION_DELAY_MIN, timeout * TIMEOUT_FAILURE_MULTIPLIER)  # noqa: S311 - simulation only
    else:
        # When failure_rate is 0, ensure we never timeout
        delay = random.uniform(SIMULATION_DELAY_MIN, timeout * TIMEOUT_SUCCESS_MULTIPLIER)  # noqa: S311 - simulation only

    if delay > timeout:
        raise NetworkTimeoutError(
            service=f"API endpoint {endpoint}", timeout=timeout, attempted_duration=delay
        )

    time.sleep(delay)

    # Simulate random failures (but not when failure_rate is 0)
    if failure_rate > 0 and random.random() < failure_rate:  # noqa: S311 - simulation only
        raise NetworkError(
            f"Failed to connect to {endpoint}", service=f"API endpoint {endpoint}", status_code=503
        )

    # Return simulated successful response
    return {
        "status": "ok",
        "endpoint": endpoint,
        "data": {"users": ["Alice", "Bob", "Charlie"]},
        "timestamp": time.time(),
    }
