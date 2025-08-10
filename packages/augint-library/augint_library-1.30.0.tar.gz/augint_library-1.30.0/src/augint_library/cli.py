"""CLI interface for augint-library.

This module demonstrates best practices for creating command-line interfaces
that wrap library functions. It showcases:
- Click framework for elegant CLI design
- Proper separation between CLI and library logic
- Error handling and user feedback
- Integration with logging, telemetry, and feature flags
- Command organization with groups

Common Use Cases:
    1. Creating user-friendly CLIs for Python libraries
    2. Building multi-command tools
    3. Adding telemetry and feature flags to CLIs
    4. Proper error handling and user feedback

Examples:
    Basic CLI usage:
    $ ai-test-script greet Alice
    Hi Alice

    $ ai-test-script fetch-data /api/users
    ✓ Successfully fetched data from /api/users

    Using with logging:
    $ AI_TEST_SCRIPT_LOG_JSON=true ai-test-script fetch-data /api/users
    {"timestamp": "2024-01-01T12:00:00Z", "level": "INFO", "message": "Fetching data", ...}

    Error handling:
    $ ai-test-script fetch-data /api/broken --timeout 0.1
    ✗ Network timeout after 0.1s

    Using feature flags:
    $ ai-test-script feature-flags status
    Feature Flags:
    ✓ new_feature: enabled
    ✗ experimental_api: disabled

CLI Design Patterns:
    1. Thin CLI layer - just parse args and call library
    2. Consistent output format (✓/✗ symbols, colors)
    3. Proper exit codes (0 for success, 1+ for errors)
    4. JSON output option for scripting
    5. Help text that includes examples

Creating Your Own CLI:
    >>> import click
    >>> from your_library import process_data
    >>>
    >>> @click.command()
    >>> @click.argument('input_file', type=click.Path(exists=True))
    >>> @click.option('--format', '-f', default='json', help='Output format')
    >>> def process(input_file, format):
    ...     '''Process a data file.'''
    ...     try:
    ...         result = process_data(input_file, format=format)
    ...         click.echo(f"✓ Processed {len(result)} records")
    ...     except Exception as e:
    ...         click.echo(f"✗ Error: {e}", err=True)
    ...         raise click.ClickException(str(e))

Note:
    This module demonstrates patterns that work for both simple scripts
    and complex enterprise CLIs. The key is keeping the CLI layer thin
    and delegating all business logic to the library modules.
"""

import contextlib
import json
import time
from typing import Optional

import click

from .constants import (
    CLI_RESILIENT_INITIAL_DELAY,
    CLI_RESILIENT_RECOVERY_TIMEOUT,
    CLI_SEPARATOR_LENGTH,
    DEFAULT_API_TIMEOUT,
    DEFAULT_FAILURE_RATE,
    DEFAULT_FAILURE_THRESHOLD,
    DEFAULT_RETRY_ATTEMPTS,
)
from .core import fetch_data, print_hi
from .exceptions import NetworkError, ValidationError
from .feature_flags import get_flags
from .logging import setup_logging
from .resilience import (
    CircuitOpenError,
    circuit_breaker,
    get_circuit_breakers,
    reset_circuit_breaker,
    retry,
)

# Telemetry imports (optional - requires telemetry group dependencies)
try:
    from .telemetry import get_telemetry_client, track_command_execution
except ImportError:
    from typing import Any, Callable

    # Create no-op decorator when telemetry is not available
    def track_command_execution(func: Callable[..., Any]) -> Callable[..., Any]:
        """No-op decorator when telemetry is not available."""
        return func

    def get_telemetry_client() -> None:  # type: ignore[misc]
        """Dummy telemetry client when telemetry is not available."""
        raise click.ClickException(
            "Telemetry is not available. Install with: poetry install --with telemetry"
        )


# CLI is not part of the library API
__all__: list[str] = []


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Main CLI entry point for augint-library."""
    # Store shared context for subcommands
    ctx.ensure_object(dict)


@cli.command()
@click.argument("name", default="there", type=str)
@click.option("--json-logs", is_flag=True, help="Output logs in JSON format")
@click.option("--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR)")
@track_command_execution
def greet(name: str, json_logs: bool, log_level: str) -> None:
    """Greet someone by name.

    Args:
        name: The name to greet (default: "there").
        json_logs: Whether to output logs in JSON format.
        log_level: The logging level to use.
    """
    # Setup logging based on CLI options
    logger = setup_logging("cli", level=log_level, json_format=json_logs)
    logger.info("Starting greeting command", extra={"target_name": name})

    try:
        print_hi(name)
        logger.info("Greeting completed successfully", extra={"target_name": name})
    except Exception as e:
        logger.exception(
            "Failed to complete greeting", extra={"target_name": name, "error": str(e)}
        )
        raise


# Apply resilience patterns to the library function
resilient_fetch_data = retry(
    max_attempts=DEFAULT_RETRY_ATTEMPTS, initial_delay=CLI_RESILIENT_INITIAL_DELAY
)(
    circuit_breaker(
        failure_threshold=DEFAULT_FAILURE_THRESHOLD, recovery_timeout=CLI_RESILIENT_RECOVERY_TIMEOUT
    )(fetch_data)
)


@cli.command("fetch-data")
@click.argument("endpoint", type=str)
@click.option("--timeout", default=DEFAULT_API_TIMEOUT, help="Request timeout in seconds")
@click.option(
    "--failure-rate", default=DEFAULT_FAILURE_RATE, help="Simulated failure rate (0.0-1.0)"
)
@click.option("--json-logs", is_flag=True, help="Output logs in JSON format")
@click.option("--log-level", default="INFO", help="Logging level")
@track_command_execution
def fetch_data_command(
    endpoint: str, timeout: float, failure_rate: float, json_logs: bool, log_level: str
) -> None:
    """Fetch data from a remote endpoint with resilience patterns.

    This command demonstrates retry and circuit breaker patterns
    for handling transient failures in external service calls.
    """
    logger = setup_logging("cli", level=log_level, json_format=json_logs)
    logger.info("Fetching data", extra={"endpoint": endpoint, "timeout": timeout})

    try:
        result = resilient_fetch_data(endpoint, timeout=timeout, failure_rate=failure_rate)
        click.echo(f"Success: {result['status']}")
        click.echo(f"Data: {result['data']}")
        logger.info("Data fetched successfully", extra={"endpoint": endpoint})
    except CircuitOpenError as e:
        click.echo(f"Circuit breaker OPEN: {e.message}", err=True)
        logger.warning("Circuit breaker open", extra=e.details)
        raise click.ClickException("Service temporarily unavailable") from e
    except NetworkError as e:
        click.echo(f"Network error: {e.message}", err=True)
        logger.exception("Network request failed", extra=e.details)
        raise click.ClickException("Failed to fetch data after retries") from e


@cli.group("circuit-breaker")
def circuit_breaker_group() -> None:
    """Manage circuit breakers."""


@circuit_breaker_group.command("status")
def circuit_breaker_status() -> None:
    """Show status of all circuit breakers."""
    breakers = get_circuit_breakers()

    if not breakers:
        click.echo("No circuit breakers registered yet.")
        return

    click.echo("Circuit Breaker Status:")
    click.echo("-" * CLI_SEPARATOR_LENGTH)

    for name, state in breakers.items():
        click.echo(f"Name: {name}")
        click.echo(f"  State: {state['state'].upper()}")
        click.echo(f"  Failures: {state['failure_count']}")
        click.echo(f"  Successes: {state['success_count']}")
        if state["last_failure"]:
            click.echo(
                f"  Last failure: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(state['last_failure']))}"
            )
        click.echo()


@circuit_breaker_group.command("reset")
@click.argument("name", required=False)
def circuit_breaker_reset(name: Optional[str]) -> None:
    """Reset circuit breaker(s) to closed state."""
    if name:
        if reset_circuit_breaker(name):
            click.echo(f"Reset circuit breaker: {name}")
        else:
            click.echo(f"Circuit breaker not found: {name}", err=True)
            raise click.ClickException("Invalid circuit breaker name")
    else:
        # Reset all breakers
        breakers = get_circuit_breakers()
        for breaker_name in breakers:
            reset_circuit_breaker(breaker_name)
        click.echo(f"Reset {len(breakers)} circuit breaker(s)")


@cli.group("feature-flags")
def feature_flags_group() -> None:
    """Manage feature flags."""


@feature_flags_group.command("list")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def feature_flags_list(output_json: bool) -> None:
    """List all feature flags and their current state."""
    flags = get_flags()
    all_flags = flags.get_all_flags()

    if not all_flags:
        click.echo("No feature flags registered.")
        return

    if output_json:
        click.echo(json.dumps(all_flags, indent=2))
    else:
        click.echo("Feature Flags:")
        click.echo("-" * CLI_SEPARATOR_LENGTH)

        for name, info in sorted(all_flags.items()):
            click.echo(f"Name: {name}")
            click.echo(f"  State: {info['state']}")
            click.echo(f"  Default: {info['default']}")
            if info["description"]:
                click.echo(f"  Description: {info['description']}")
            if info["metadata"]:
                click.echo(f"  Metadata: {info['metadata']}")
            click.echo()


@feature_flags_group.command("set")
@click.argument("name")
@click.argument("state")
def feature_flags_set(name: str, state: str) -> None:
    """Set the state of a feature flag.

    STATE can be: enabled, disabled, percentage:N (0-100), or conditional.

    Examples:
        ai-test-script feature-flags set new_feature enabled
        ai-test-script feature-flags set beta_feature percentage:50
    """
    flags = get_flags()

    try:
        flags.set_state(name, state)
        click.echo(f"Set feature flag '{name}' to '{state}'")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.ClickException(str(e)) from e


@feature_flags_group.command("check")
@click.argument("name")
@click.option("--user-id", help="User ID for context")
@click.option("--environment", help="Environment for context")
def feature_flags_check(name: str, user_id: Optional[str], environment: Optional[str]) -> None:
    """Check if a feature flag is enabled.

    Optionally provide context for percentage and conditional flags.
    """
    flags = get_flags()

    context = {}
    if user_id:
        context["user_id"] = user_id
    if environment:
        context["environment"] = environment

    enabled = flags.is_enabled(name, context)

    try:
        state = flags.get_state(name)
    except ValidationError:
        # Unknown flag - show as disabled
        state = "unknown (defaulting to disabled)"

    click.echo(f"Flag: {name}")
    click.echo(f"State: {state}")
    click.echo(f"Enabled: {'Yes' if enabled else 'No'}")

    if context:
        click.echo(f"Context: {context}")


@feature_flags_group.command("register")
@click.argument("name")
@click.option("--default", default="disabled", help="Default state (default: disabled)")
@click.option("--description", help="Description of the flag")
def feature_flags_register(name: str, default: str, description: Optional[str]) -> None:
    """Register a new feature flag."""
    flags = get_flags()

    try:
        flags.register(name, default=default, description=description)
        click.echo(f"Registered feature flag '{name}' with default state '{default}'")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.ClickException(str(e)) from e


@cli.group("telemetry")
def telemetry_group() -> None:
    """Manage anonymous usage telemetry settings.

    Telemetry helps improve augint-library by collecting anonymous usage
    statistics and error reports. No personal information is ever collected.
    """
    # Check if telemetry is available at group level
    with contextlib.suppress(click.ClickException):
        get_telemetry_client()


@telemetry_group.command("status")
def telemetry_status() -> None:
    """Show current telemetry status and configuration."""
    client = get_telemetry_client()

    click.echo("Telemetry Status")
    click.echo("-" * 40)
    click.echo(f"Enabled: {'Yes' if client.enabled else 'No'}")

    if client.enabled:
        # Show anonymous ID
        anonymous_id = client._get_anonymous_id()
        click.echo(f"Anonymous ID: {anonymous_id}")
        click.echo()
        click.echo("Data collected:")
        click.echo("- Command usage (names only, no arguments)")
        click.echo("- Success/failure rates")
        click.echo("- Performance metrics")
        click.echo("- Python and OS versions")
        click.echo("- Anonymous error reports")
        click.echo()
        click.echo("Data NOT collected:")
        click.echo("- Personal information")
        click.echo("- File paths or contents")
        click.echo("- Command arguments")
        click.echo("- Network locations")
    else:
        click.echo()
        click.echo("Telemetry is disabled. To help improve augint-library, run:")
        click.echo("  ai-test-script telemetry enable")


@telemetry_group.command("enable")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def telemetry_enable(yes: bool) -> None:
    """Enable anonymous telemetry."""
    client = get_telemetry_client()

    if client.enabled:
        click.echo("Telemetry is already enabled.")
        return

    if not yes:
        click.echo("augint-library Telemetry")
        click.echo("-" * 40)
        click.echo()
        click.echo("Help improve augint-library by sharing anonymous usage data.")
        click.echo()
        click.echo("What we collect:")
        click.echo("  ✓ Command usage patterns (no arguments)")
        click.echo("  ✓ Error types and frequencies")
        click.echo("  ✓ Performance metrics")
        click.echo("  ✓ Python/OS versions")
        click.echo()
        click.echo("What we DON'T collect:")
        click.echo("  ✗ Personal information")
        click.echo("  ✗ File paths or contents")
        click.echo("  ✗ IP addresses or hostnames")
        click.echo("  ✗ Command arguments or data")
        click.echo()

        if not click.confirm("Enable telemetry?"):
            click.echo("Telemetry remains disabled.")
            return

    client.set_consent(enabled=True)
    click.echo("✓ Telemetry enabled. Thank you for helping improve augint-library!")
    click.echo("  You can disable this at any time with: ai-test-script telemetry disable")


@telemetry_group.command("disable")
def telemetry_disable() -> None:
    """Disable telemetry."""
    client = get_telemetry_client()

    if not client.enabled:
        click.echo("Telemetry is already disabled.")
        return

    client.set_consent(enabled=False)
    click.echo("✓ Telemetry disabled.")
    click.echo("  Your anonymous ID has been preserved for consistency if you re-enable.")


@telemetry_group.command("test")
def telemetry_test() -> None:
    """Send a test event to verify telemetry is working."""
    client = get_telemetry_client()

    if not client.enabled:
        click.echo("Telemetry is disabled. Enable it first with:")
        click.echo("  ai-test-script telemetry enable")
        return

    click.echo("Sending test telemetry event...")

    # Track test command
    client.track_command("telemetry_test", success=True, duration=0.1)

    # Track test metric
    client.track_metric("test_metric", 42.0, unit="test", tags={"type": "verification"})

    # Track test error
    def _create_test_error() -> None:
        raise ValueError("This is a test error for telemetry verification")

    try:
        _create_test_error()
    except ValueError as e:
        client.track_error(e, {"context": "telemetry_test_command"})

    # Flush to ensure events are sent
    client.flush()

    click.echo("✓ Test events sent successfully!")
    click.echo("  Check your Sentry dashboard to verify they were received.")


if __name__ == "__main__":
    cli()
