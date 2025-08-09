"""Feature flags system for controlling feature rollout and A/B testing.

This module provides a comprehensive feature flag system that enables:
- Gradual feature rollouts
- A/B testing
- Emergency kill switches
- User targeting
- Environment-specific configuration

Common Use Cases:
    1. Rolling out new features gradually
    2. A/B testing different implementations
    3. Emergency feature disabling
    4. Beta testing with specific users
    5. Environment-specific features

Examples:
    Basic feature flag usage:
    >>> from augint_library import FeatureFlags, feature_flag
    >>>
    >>> flags = FeatureFlags()
    >>>
    >>> @feature_flag("new_algorithm", default=False)
    >>> def process_data(data):
    ...     if flags.is_enabled("new_algorithm"):
    ...         return new_algorithm(data)
    ...     else:
    ...         return old_algorithm(data)

    Percentage-based rollout:
    >>> flags.set_flag("dark_mode", {
    ...     "enabled": True,
    ...     "rollout_percentage": 25  # 25% of users
    ... })
    >>>
    >>> # Check for specific user
    >>> if flags.is_enabled("dark_mode", user_id="user123"):
    ...     render_dark_theme()

    User targeting:
    >>> flags.set_flag("beta_feature", {
    ...     "enabled": True,
    ...     "allowed_users": ["alice@example.com", "bob@example.com"],
    ...     "denied_users": ["charlie@example.com"]
    ... })

    Environment-specific flags:
    >>> # In production config
    >>> flags.set_flag("debug_mode", {"enabled": False})
    >>>
    >>> # In development config
    >>> flags.set_flag("debug_mode", {"enabled": True})

    A/B testing with variants:
    >>> flags.set_flag("checkout_flow", {
    ...     "enabled": True,
    ...     "variants": {
    ...         "control": {"weight": 50, "config": {"steps": 3}},
    ...         "test": {"weight": 50, "config": {"steps": 1}}
    ...     }
    ... })
    >>>
    >>> variant = flags.get_variant("checkout_flow", user_id="user123")
    >>> if variant == "test":
    ...     show_single_page_checkout()

Configuration Examples:
    JSON configuration file:
    ```json
    {
        "features": {
            "new_dashboard": {
                "enabled": true,
                "rollout_percentage": 10,
                "allowed_users": ["beta@example.com"]
            },
            "experimental_api": {
                "enabled": false,
                "description": "New API endpoint - disabled due to bug"
            }
        }
    }
    ```

    Environment variables:
    ```bash
    export FEATURE_NEW_DASHBOARD=true
    export FEATURE_EXPERIMENTAL_API=false
    ```

Best Practices:
    1. Always provide meaningful defaults
    2. Document feature flags in code
    3. Clean up old flags regularly
    4. Use descriptive flag names
    5. Monitor flag usage

Advanced Patterns:
    Context manager for temporary flags:
    >>> with flags.override("debug_mode", True):
    ...     # Debug mode is enabled here
    ...     debug_function()
    ... # Debug mode returns to previous state

    Decorator with fallback:
    >>> @feature_flag("new_feature", fallback=legacy_function)
    >>> def new_function(data):
    ...     return enhanced_processing(data)

Note:
    Feature flags are powerful but can add complexity. Use them judiciously
    and have a process for removing flags once features are fully rolled out.
"""

import hashlib
import json
import logging
import os
import random
import re
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Optional, Union

from .constants import HASH_PREFIX_LENGTH, PERCENTAGE_MAX, PERCENTAGE_MIN, USER_ID_RANDOM_MAX
from .exceptions import ConfigurationError, ValidationError

logger = logging.getLogger(__name__)


class FeatureFlag:
    """Represents a single feature flag with its configuration."""

    def __init__(
        self,
        name: str,
        default: str = "disabled",
        description: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        evaluator: Optional[Callable[[dict[str, Any]], bool]] = None,
    ):
        """Initialize a feature flag.

        Args:
            name: Flag identifier (alphanumeric + underscore/hyphen)
            default: Default state ("enabled", "disabled", "percentage:N", "conditional")
            description: Human-readable description
            metadata: Additional metadata for the flag
            evaluator: Function for conditional evaluation
        """
        self.name = self._validate_name(name)
        self.default = self._validate_state(default)
        self.description = description
        self.metadata = metadata or {}
        self.evaluator = evaluator
        self.state = self.default
        self._override_state: Optional[str] = None

    @staticmethod
    def _validate_name(name: str) -> str:
        """Validate flag name format."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", name):
            raise ValidationError(
                f"Invalid flag name '{name}'. Use only alphanumeric, underscore, and hyphen."
            )
        return name

    @staticmethod
    def _validate_state(state: str) -> str:
        """Validate state format."""
        if state in ["enabled", "disabled", "conditional"]:
            return state
        if state.startswith("percentage:"):
            try:
                percentage = int(state.split(":")[1])
                if PERCENTAGE_MIN <= percentage <= PERCENTAGE_MAX:
                    return state
            except (IndexError, ValueError):
                pass
        raise ValidationError(
            f"Invalid state '{state}'. Use 'enabled', 'disabled', 'percentage:N' (0-100), or 'conditional'."  # noqa: E501
        )

    def evaluate(self, context: Optional[dict[str, Any]] = None) -> bool:  # noqa: PLR0911
        """Evaluate if the flag is enabled given the context."""
        state = self._override_state if self._override_state else self.state

        if state == "enabled":
            return True
        if state == "disabled":
            return False
        if state.startswith("percentage:"):
            percentage = int(state.split(":")[1])
            return self._evaluate_percentage(percentage, context)
        if state == "conditional":
            if not self.evaluator:
                logger.warning(
                    f"No evaluator for conditional flag '{self.name}', defaulting to disabled"
                )
                return False
            try:
                return self.evaluator(context or {})
            except Exception:
                logger.exception(f"Error evaluating conditional flag '{self.name}'")
                return False
        return False

    def _evaluate_percentage(
        self, percentage: int, context: Optional[dict[str, Any]] = None
    ) -> bool:
        """Evaluate percentage-based rollout with consistent hashing."""
        if percentage == 0:
            return False
        if percentage == 100:  # noqa: PLR2004
            return True

        context = context or {}
        user_id = context.get("user_id", str(random.randint(0, USER_ID_RANDOM_MAX)))  # noqa: S311
        hash_input = f"{self.name}:{user_id}"
        hash_value = hashlib.md5(hash_input.encode(), usedforsecurity=False).hexdigest()
        user_bucket = int(hash_value[:HASH_PREFIX_LENGTH], 16) % PERCENTAGE_MAX
        return user_bucket < percentage


class FeatureFlags:
    """Main class for managing feature flags."""

    _instance: Optional["FeatureFlags"] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "FeatureFlags":  # noqa: ARG004
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_file: Optional[str] = None, auto_load_env: bool = True):
        """Initialize feature flags manager.

        Args:
            config_file: Path to JSON configuration file
            auto_load_env: Whether to automatically load from environment variables
        """
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        self._flags: dict[str, FeatureFlag] = {}
        self._evaluators: dict[str, Callable[[dict[str, Any]], bool]] = {}

        if config_file:
            self.load_from_file(config_file)

        if auto_load_env:
            self.load_from_env()

    def register(
        self,
        name: str,
        default: str = "disabled",
        description: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        evaluator: Optional[str] = None,
    ) -> None:
        """Register a new feature flag.

        Args:
            name: Flag identifier
            default: Default state
            description: Human-readable description
            metadata: Additional metadata
            evaluator: Name of registered evaluator function
        """
        evaluator_func = None
        if evaluator:
            if evaluator not in self._evaluators:
                raise ConfigurationError(f"Evaluator '{evaluator}' not registered")
            evaluator_func = self._evaluators[evaluator]

        flag = FeatureFlag(name, default, description, metadata, evaluator_func)
        self._flags[name] = flag
        logger.debug(f"Registered feature flag '{name}' with default state '{default}'")

    def register_evaluator(self, name: str, func: Callable[[dict[str, Any]], bool]) -> None:
        """Register a custom evaluator function.

        Args:
            name: Evaluator name
            func: Function that takes context and returns bool
        """
        self._evaluators[name] = func
        logger.debug(f"Registered evaluator '{name}'")

    def is_enabled(self, name: str, context: Optional[dict[str, Any]] = None) -> bool:
        """Check if a feature flag is enabled.

        Args:
            name: Flag name
            context: Evaluation context (e.g., user_id, environment)

        Returns:
            True if enabled, False otherwise
        """
        if name not in self._flags:
            logger.warning(f"Unknown feature flag '{name}', defaulting to disabled")
            return False

        return self._flags[name].evaluate(context)

    def set_state(self, name: str, state: str) -> None:
        """Set the runtime state of a flag.

        Args:
            name: Flag name
            state: New state
        """
        if name not in self._flags:
            raise ValidationError(f"Unknown feature flag '{name}'")

        self._flags[name].state = self._flags[name]._validate_state(state)
        logger.info(f"Set feature flag '{name}' to state '{state}'")

    def get_state(self, name: str) -> str:
        """Get the current state of a flag."""
        if name not in self._flags:
            raise ValidationError(f"Unknown feature flag '{name}'")
        return self._flags[name].state

    def get_all_flags(self) -> dict[str, dict[str, Any]]:
        """Get all registered flags with their current state."""
        return {
            name: {
                "state": flag.state,
                "default": flag.default,
                "description": flag.description,
                "metadata": flag.metadata,
            }
            for name, flag in self._flags.items()
        }

    @contextmanager
    def override(self, name: str, state: str) -> Iterator[None]:
        """Temporarily override a flag's state.

        Args:
            name: Flag name
            state: Temporary state
        """
        if name not in self._flags:
            raise ValidationError(f"Unknown feature flag '{name}'")

        flag = self._flags[name]
        validated_state = flag._validate_state(state)
        original_override = flag._override_state

        try:
            flag._override_state = validated_state
            logger.debug(f"Overriding flag '{name}' to '{state}'")
            yield
        finally:
            flag._override_state = original_override
            logger.debug(f"Restored flag '{name}' override")

    def load_from_file(self, file_path: Union[str, Path]) -> None:
        """Load flag configuration from JSON file.

        Args:
            file_path: Path to JSON configuration file
        """
        path = Path(file_path)
        if not path.exists():
            raise ConfigurationError(f"Configuration file not found: {file_path}")

        try:
            with path.open() as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {e}") from e

        for flag_name, flag_config in config.items():
            if isinstance(flag_config, str):
                # Simple state configuration
                self.register(flag_name, default=flag_config)
            elif isinstance(flag_config, dict):
                # Detailed configuration
                self.register(
                    flag_name,
                    default=flag_config.get("state", "disabled"),
                    description=flag_config.get("description"),
                    metadata=flag_config.get("metadata"),
                    evaluator=flag_config.get("evaluator"),
                )
                # Set current state if different from default
                if "state" in flag_config:
                    self.set_state(flag_name, flag_config["state"])

    def load_from_env(self) -> None:
        """Load flag states from environment variables.

        Environment variables should be in format: FEATURE_FLAG_{NAME}=state
        """
        prefix = "FEATURE_FLAG_"
        for key, value in os.environ.items():
            if key.startswith(prefix):
                flag_name = key[len(prefix) :].lower()
                try:
                    if flag_name in self._flags:
                        self.set_state(flag_name, value)
                    else:
                        self.register(flag_name, default=value)
                except ValidationError as e:
                    logger.warning(f"Invalid environment variable {key}: {e}")


# Decorator for conditional execution
def feature_flag(
    flag_name: str,
    fallback: Any = None,
    flags: Optional[FeatureFlags] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for conditional feature execution.

    Args:
        flag_name: Name of the feature flag
        fallback: Value to return if flag is disabled
        flags: FeatureFlags instance (uses singleton if not provided)
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            _flags = flags or FeatureFlags()

            # Extract context from kwargs if provided
            context = kwargs.pop("_feature_context", None)

            if _flags.is_enabled(flag_name, context):
                return func(*args, **kwargs)

            if callable(fallback):
                return fallback(*args, **kwargs)
            return fallback

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__wrapped__ = func  # type: ignore[attr-defined]
        return wrapper

    return decorator


def get_flags() -> FeatureFlags:
    """Get the global FeatureFlags instance."""
    return FeatureFlags()
