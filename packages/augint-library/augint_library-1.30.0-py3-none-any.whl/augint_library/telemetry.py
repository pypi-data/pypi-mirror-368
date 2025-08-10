"""Telemetry module for anonymous usage tracking and error reporting.

This module provides opt-in telemetry functionality for gathering anonymous
usage statistics and error reports to improve the library. All telemetry is
privacy-conscious and requires explicit user consent.

Privacy guarantees:
- No personal information is collected
- All file paths and hostnames are scrubbed
- Users must explicitly opt-in
- Telemetry can be disabled at any time
"""

import contextlib
import json
import logging
import os
import platform
import uuid
from datetime import datetime, timezone
from functools import wraps
from importlib.metadata import version
from pathlib import Path
from typing import Any, Callable, Optional

from .constants import DEFAULT_TELEMETRY_FLUSH_TIMEOUT, JSON_INDENT, TELEMETRY_SAMPLE_RATE

try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.types import Event, Hint

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

    # Import types module to create a proper module type
    from types import ModuleType

    # Dummy LoggingIntegration when sentry is not available
    class LoggingIntegration:  # type: ignore[no-redef]
        """Dummy LoggingIntegration for tests."""

        def __init__(self, **kwargs: Any) -> None:
            pass

    # Create a module-like object that mypy will accept
    class _DummySentryModule(ModuleType):
        """Dummy sentry_sdk module when the real module is not available."""

        def __init__(self) -> None:
            super().__init__("sentry_sdk")
            self.metrics = self._Metrics()

        def init(self, *args: Any, **kwargs: Any) -> None:
            pass

        def set_user(self, *args: Any, **kwargs: Any) -> None:
            pass

        def set_tag(self, *args: Any, **kwargs: Any) -> None:
            pass

        def capture_message(self, *args: Any, **kwargs: Any) -> None:
            pass

        def capture_exception(self, *args: Any, **kwargs: Any) -> None:
            pass

        def flush(self, *args: Any, **kwargs: Any) -> None:
            pass

        @contextlib.contextmanager
        def push_scope(self) -> Any:
            """Dummy push_scope context manager."""

            class DummyScope:
                def set_extra(self, *args: Any, **kwargs: Any) -> None:
                    pass

            yield DummyScope()

        class _Metrics:
            def incr(self, *args: Any, **kwargs: Any) -> None:
                pass

            def distribution(self, *args: Any, **kwargs: Any) -> None:
                pass

    sentry_sdk = _DummySentryModule()

    # Define dummy types when sentry is not available
    class Event(dict):  # type: ignore[no-redef,type-arg]
        """Dummy Event type when sentry is not available."""

    class Hint(dict):  # type: ignore[no-redef,type-arg]
        """Dummy Hint type when sentry is not available."""


logger = logging.getLogger(__name__)


class TelemetryClient:
    """Privacy-conscious telemetry client for community usage tracking."""

    def __init__(self) -> None:
        """Initialize telemetry client, checking consent and configuration."""
        self._enabled = False
        self._initialized = False
        self._anonymous_id: Optional[str] = None
        self._package_name = self._get_package_name()
        self._consent_file = Path.home() / f".{self._package_name}" / "consent.json"

        # Check if telemetry should be enabled
        if self._should_enable_telemetry():
            self._initialize_sentry()

    def _get_package_name(self) -> str:
        """Get the package name dynamically."""
        if __package__:
            # Extract root package name from module path
            return __package__.split(".")[0].replace("_", "-")
        # Fallback to extracting from module path
        return Path(__file__).parent.name.replace("_", "-")

    def _should_enable_telemetry(self) -> bool:
        """Check if telemetry should be enabled based on consent and environment."""
        # Environment variable override (highest priority)
        env_var_name = f"{self._package_name.replace('-', '_').upper()}_TELEMETRY_ENABLED"
        env_enabled = os.getenv(env_var_name, "").lower()
        if env_enabled == "false":
            return False
        if env_enabled == "true":
            return True

        # CI environment detection (disable in CI)
        if self._is_ci_environment():
            return False

        # Check stored consent
        return self._check_stored_consent()

    def _is_ci_environment(self) -> bool:
        """Detect if running in a CI environment."""
        ci_env_vars = [
            "CI",
            "CONTINUOUS_INTEGRATION",
            "GITHUB_ACTIONS",
            "GITLAB_CI",
            "JENKINS_URL",
            "TRAVIS",
        ]
        return any(os.getenv(var) for var in ci_env_vars)

    def _check_stored_consent(self) -> bool:
        """Check if user has previously consented to telemetry."""
        if not self._consent_file.exists():
            return False

        try:
            with self._consent_file.open() as f:
                consent_data = json.load(f)
                return bool(consent_data.get("telemetry_enabled", False))
        except (OSError, json.JSONDecodeError, KeyError):
            return False

    def _get_anonymous_id(self) -> str:
        """Get or create anonymous user ID."""
        if self._anonymous_id:
            return self._anonymous_id

        consent_data = {}
        if self._consent_file.exists():
            try:
                with self._consent_file.open() as f:
                    consent_data = json.load(f)
            except (OSError, json.JSONDecodeError):
                pass

        # Use existing ID or create new one
        self._anonymous_id = consent_data.get("anonymous_id") or str(uuid.uuid4())
        return self._anonymous_id

    def _initialize_sentry(self) -> None:
        """Initialize Sentry SDK with privacy-conscious settings."""
        # Use helper to allow test mocking of SENTRY_AVAILABLE
        if not _is_sentry_available():
            return

        # Get DSN from environment
        dsn = os.getenv("SENTRY_DSN")
        if not dsn:
            return

        try:
            # Get package name dynamically from module
            package_name = __package__.split(".")[0].replace("_", "-")

            # Try to get version, fallback to 'unknown' for test environments
            try:
                pkg_version = version(package_name)
                release = f"{package_name}@{pkg_version}"
            except Exception:
                # In test environments, the package might not be installed
                release = f"{package_name}@unknown"

            sentry_sdk.init(
                dsn=dsn,
                # Scrub sensitive data
                before_send=self._scrub_sensitive_data,
                before_send_transaction=self._scrub_sensitive_data,
                # Sample rate for performance monitoring
                traces_sample_rate=TELEMETRY_SAMPLE_RATE,
                # Release tracking
                release=release,
                # Environment
                environment=os.getenv(
                    f"{self._package_name.replace('-', '_').upper()}_ENVIRONMENT", "production"
                ),
                # Disable automatic user tracking
                send_default_pii=False,
                # Integrations
                integrations=[
                    LoggingIntegration(
                        level=None,  # Don't capture logs
                        event_level=None,
                    ),
                ],
                # Don't attach stack locals (might contain sensitive data)
                attach_stacktrace=False,
            )

            # Set anonymous user context
            sentry_sdk.set_user({"id": self._get_anonymous_id()})

            # Set global tags
            sentry_sdk.set_tag("python_version", platform.python_version())
            sentry_sdk.set_tag("platform", platform.system())
            sentry_sdk.set_tag("platform_version", platform.version())

            self._initialized = True
            self._enabled = True

        except Exception:
            # Silently fail if Sentry initialization fails
            logger.debug("Failed to initialize Sentry", exc_info=True)

    def _scrub_sensitive_data(
        self,
        event: Event,
        hint: Hint,  # noqa: ARG002
    ) -> Optional[Event]:
        """Scrub sensitive data from Sentry events."""
        if not event:
            return None

        # Work directly with event as it's dict-like
        # Scrub file paths in stack traces
        self._scrub_stacktraces(event)

        # Scrub breadcrumbs
        self._scrub_breadcrumbs(event)

        # Scrub extra context
        if "extra" in event and isinstance(event["extra"], dict):
            event["extra"] = self._scrub_dict(event["extra"])

        # Scrub user data (though we shouldn't have any)
        if "user" in event:
            event["user"] = {"id": self._get_anonymous_id()}

        # Remove request data and server name
        event.pop("request", None)
        event.pop("server_name", None)

        return event

    def _scrub_stacktraces(self, event_dict: Event) -> None:
        """Scrub sensitive data from stack traces."""
        if "exception" not in event_dict:
            return

        exceptions = event_dict.get("exception", {})
        if not isinstance(exceptions, dict) or "values" not in exceptions:
            return

        for exception in exceptions.get("values", []):
            stacktrace = exception.get("stacktrace", {})
            if isinstance(stacktrace, dict) and "frames" in stacktrace:
                for frame in stacktrace.get("frames", []):
                    if "filename" in frame:
                        frame["filename"] = self._anonymize_path(frame["filename"])
                    frame.pop("vars", None)

    def _scrub_breadcrumbs(self, event_dict: Event) -> None:
        """Scrub sensitive data from breadcrumbs."""
        if "breadcrumbs" not in event_dict:
            return

        breadcrumbs = event_dict.get("breadcrumbs", {})
        if isinstance(breadcrumbs, dict) and "values" in breadcrumbs:
            for crumb in breadcrumbs.get("values", []):
                if "data" in crumb and isinstance(crumb["data"], dict):
                    crumb["data"] = self._scrub_dict(crumb["data"])

    def _anonymize_path(self, filepath: str) -> str:
        """Anonymize file paths to remove user-specific information."""
        # Convert to Path for easier manipulation
        path = Path(filepath)

        # If it's within site-packages, show relative path
        for part in path.parts:
            if "site-packages" in part:
                idx = path.parts.index(part)
                return str(Path(*path.parts[idx + 1 :]))

        # If it contains the package module, show path from there
        module_name = self._package_name.replace("-", "_")
        for i, part in enumerate(path.parts):
            if part == module_name:
                return str(Path(*path.parts[i:]))

        # Otherwise just show the filename
        return path.name

    def _scrub_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Recursively scrub sensitive information from dictionaries."""
        scrubbed: dict[str, Any] = {}
        sensitive_keys = {
            "password",
            "token",
            "key",
            "secret",
            "credential",
            "auth",
            "api_key",
            "access_token",
            "private",
            "path",
            "file",
            "dir",
            "directory",
            "home",
            "user",
            "username",
            "email",
            "host",
            "hostname",
            "ip",
            "address",
        }

        for key, value in data.items():
            # Check if key contains sensitive terms
            if any(term in key.lower() for term in sensitive_keys):
                scrubbed[key] = "[REDACTED]"
            elif isinstance(value, dict):
                scrubbed[key] = self._scrub_dict(value)
            elif isinstance(value, str):
                # Scrub file paths
                if "/" in value or "\\" in value:
                    scrubbed[key] = "[PATH]"
                else:
                    scrubbed[key] = value
            else:
                scrubbed[key] = value

        return scrubbed

    @property
    def enabled(self) -> bool:
        """Check if telemetry is enabled."""
        return self._enabled

    def set_consent(self, enabled: bool, prompt_shown: bool = True) -> None:
        """Set telemetry consent and persist it."""
        # Create config directory if it doesn't exist
        self._consent_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing data or create new
        consent_data = {}
        if self._consent_file.exists():
            try:
                with self._consent_file.open() as f:
                    consent_data = json.load(f)
            except (OSError, json.JSONDecodeError):
                pass

        # Update consent data
        consent_data.update(
            {
                "telemetry_enabled": enabled,
                "anonymous_id": self._get_anonymous_id(),
                "consent_timestamp": datetime.now(timezone.utc).isoformat(),
                "prompt_shown": prompt_shown,
            }
        )

        # Write consent file
        with self._consent_file.open("w") as f:
            json.dump(consent_data, f, indent=JSON_INDENT)

        # Update internal state
        self._enabled = enabled
        if enabled and not self._initialized:
            self._initialize_sentry()
        elif not enabled and self._initialized:
            # Disable Sentry
            if _is_sentry_available():
                sentry_sdk.init(dsn=None)
            self._initialized = False

    def track_command(
        self, command: str, success: bool = True, duration: Optional[float] = None
    ) -> None:
        """Track CLI command execution."""
        if not self._enabled or not _is_sentry_available():
            return

        try:
            # Track as custom event
            sentry_sdk.capture_message(
                f"Command executed: {command}",
                level="info",
                extras={
                    "command": command,
                    "success": success,
                    "duration": duration,
                },
            )

            # Also track as metric
            tags = {
                "command": command,
                "success": str(success),
            }

            # Increment counter
            sentry_sdk.metrics.incr(
                key="cli.command.executed",
                value=1,
                tags=tags,
            )

            # Track duration if provided
            if duration is not None:
                sentry_sdk.metrics.distribution(
                    key="cli.command.duration",
                    value=duration,
                    unit="second",
                    tags=tags,
                )

        except Exception:
            # Never let telemetry break the application
            logger.debug("Failed to track telemetry", exc_info=True)

    def track_error(self, error: Exception, context: Optional[dict[str, Any]] = None) -> None:
        """Track errors with context."""
        if not self._enabled or not _is_sentry_available():
            return

        try:
            # Add context if provided
            if context:
                scrubbed_context = self._scrub_dict(context)
                with sentry_sdk.push_scope() as scope:
                    for key, value in scrubbed_context.items():
                        scope.set_extra(key, value)
                    sentry_sdk.capture_exception(error)
            else:
                sentry_sdk.capture_exception(error)

        except Exception:
            # Never let telemetry break the application
            logger.debug("Failed to track telemetry", exc_info=True)

    def track_metric(
        self,
        name: str,
        value: float,
        unit: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
    ) -> None:
        """Track custom metrics."""
        if not self._enabled or not _is_sentry_available():
            return

        try:
            if unit is not None:
                sentry_sdk.metrics.distribution(
                    key=f"custom.{name}",
                    value=value,
                    unit=unit,
                    tags=tags or {},
                )
            else:
                sentry_sdk.metrics.distribution(
                    key=f"custom.{name}",
                    value=value,
                    tags=tags or {},
                )
        except Exception:
            # Never let telemetry break the application
            logger.debug("Failed to track telemetry", exc_info=True)

    def flush(self, timeout: float = DEFAULT_TELEMETRY_FLUSH_TIMEOUT) -> None:
        """Flush pending telemetry events."""
        if self._enabled and _is_sentry_available():
            with contextlib.suppress(Exception):
                sentry_sdk.flush(timeout=timeout)


# Global telemetry instance holder
class _TelemetryClientHolder:
    client: Optional[TelemetryClient] = None


# Test helper to set SENTRY_AVAILABLE
def _set_sentry_available(value: bool) -> None:
    """Set SENTRY_AVAILABLE for testing. Not part of public API."""
    globals()["SENTRY_AVAILABLE"] = value


# Helper to check SENTRY_AVAILABLE from within module
def _is_sentry_available() -> bool:
    """Check if sentry is available. Used internally to allow test mocking."""
    return bool(globals().get("SENTRY_AVAILABLE", False))


def get_telemetry_client() -> TelemetryClient:
    """Get or create the global telemetry client."""
    if _TelemetryClientHolder.client is None:
        _TelemetryClientHolder.client = TelemetryClient()
    return _TelemetryClientHolder.client


def track_command_execution(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to automatically track command execution."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        client = get_telemetry_client()
        command_name = func.__name__
        start_time = datetime.now(timezone.utc)

        try:
            result = func(*args, **kwargs)
        except Exception as e:
            # Track failed execution
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            client.track_command(command_name, success=False, duration=duration)
            client.track_error(e, {"command": command_name})
            raise
        else:
            # Track successful execution
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            client.track_command(command_name, success=True, duration=duration)
            return result

    return wrapper
