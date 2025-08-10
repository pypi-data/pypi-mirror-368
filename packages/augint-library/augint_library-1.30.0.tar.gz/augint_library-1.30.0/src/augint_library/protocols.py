"""Protocol definitions for augint-library.

This module demonstrates how to use Python's Protocol classes to define
flexible, type-safe interfaces. Protocols enable:
- Duck typing with static type checking
- Dependency injection patterns
- Testable, loosely coupled code
- Clear contracts between components

Common Use Cases:
    1. Defining plugin interfaces
    2. Creating mockable dependencies
    3. Supporting multiple implementations
    4. Building extensible libraries
    5. Enabling dependency injection

Examples:
    Basic protocol usage:
    >>> from augint_library.protocols import DataProcessor
    >>>
    >>> class CSVProcessor:
    ...     def process(self, data: str, timeout: Optional[int] = None) -> dict:
    ...         # Implementation details
    ...         return {"rows": data.count("\\n")}
    ...
    >>> # Type checker knows CSVProcessor implements DataProcessor
    >>> processor: DataProcessor = CSVProcessor()

    Using protocols for dependency injection:
    >>> from augint_library.protocols import CacheProvider
    >>>
    >>> class UserService:
    ...     def __init__(self, cache: CacheProvider):
    ...         self.cache = cache
    ...
    ...     def get_user(self, user_id: str):
    ...         cached = self.cache.get(f"user:{user_id}")
    ...         if cached:
    ...             return cached
    ...         # Fetch from database...

    Testing with protocol mocks:
    >>> from unittest.mock import Mock
    >>>
    >>> # Create a mock that satisfies the protocol
    >>> mock_cache = Mock(spec=CacheProvider)
    >>> mock_cache.get.return_value = {"id": "123", "name": "Alice"}
    >>>
    >>> service = UserService(mock_cache)
    >>> user = service.get_user("123")

    Runtime protocol checking:
    >>> from augint_library.protocols import EventHandler
    >>>
    >>> @runtime_checkable
    >>> class EventHandler(Protocol):
    ...     def handle(self, event: dict) -> bool: ...
    >>>
    >>> def process_event(handler: Any) -> None:
    ...     if not isinstance(handler, EventHandler):
    ...         raise TypeError("Handler must implement EventHandler protocol")
    ...     handler.handle({"type": "user_login"})

Best Practices:
    1. Keep protocols focused and minimal
    2. Use Optional for optional parameters
    3. Document expected behavior in docstrings
    4. Consider using @runtime_checkable for dynamic validation
    5. Prefer protocols over abstract base classes

Advanced Patterns:
    Protocol inheritance:
    >>> class BasicProcessor(Protocol):
    ...     def process(self, data: Any) -> Any: ...
    >>>
    >>> class AdvancedProcessor(BasicProcessor, Protocol):
    ...     def process_batch(self, items: list[Any]) -> list[Any]: ...
    ...     def get_stats(self) -> dict[str, Any]: ...

    Generic protocols:
    >>> from typing import TypeVar, Generic
    >>>
    >>> T = TypeVar('T')
    >>>
    >>> class Repository(Protocol, Generic[T]):
    ...     def get(self, id: str) -> Optional[T]: ...
    ...     def save(self, entity: T) -> None: ...
    ...     def delete(self, id: str) -> bool: ...

Note:
    Protocols are a powerful feature for creating flexible, maintainable code.
    They work especially well with type checkers like mypy to catch errors
    early while maintaining Python's dynamic nature.
"""

from typing import Any, Optional, Protocol, runtime_checkable

from .constants import (
    DEFAULT_BATCH_CHUNK_SIZE,
    DEFAULT_DATA_PROCESSOR_TIMEOUT,
    DEFAULT_RETRY_ATTEMPTS,
)

__all__ = [
    "AdvancedProcessor",
    "CacheProvider",
    "ConfigurableClient",
    "DataProcessor",
    "EventHandler",
    "ProcessingResult",
]


@runtime_checkable
class ProcessingResult(Protocol):
    """Protocol for data processing operation results.

    This protocol defines the standard interface for results returned
    by data processing operations, providing consistent success/failure
    information and processed data access.

    Example:
        >>> result = some_processor.process(data)
        >>> if result.success:
        ...     print(f"Processed data: {result.data}")
        ... else:
        ...     print(f"Error: {result.error}")
    """

    @property
    def success(self) -> bool:
        """Whether the processing operation succeeded."""
        ...

    @property
    def data(self) -> Any:
        """The processed data (None if processing failed)."""
        ...

    @property
    def error(self) -> Optional[str]:
        """Error message if processing failed (None if successful)."""
        ...

    @property
    def metadata(self) -> dict[str, Any]:
        """Additional metadata about the processing operation.

        Common metadata keys:
        - 'duration': Processing time in seconds
        - 'timestamp': When processing completed
        - 'retries': Number of retry attempts made
        """
        ...


@runtime_checkable
class DataProcessor(Protocol):
    """Protocol for data processing operations.

    This protocol defines the interface for processing various data types
    with configurable options, error handling, and batch operations.

    Implementations should handle various data types gracefully and
    provide consistent error reporting through ProcessingResult objects.

    Example:
        >>> processor = ConcreteProcessor()
        >>> result = processor.process(data, timeout=30, retries=2)
        >>> if result.success:
        ...     print(f"Success: {len(result.data)} items processed")
    """

    def process(
        self,
        data: Any,
        *,
        timeout: int = DEFAULT_DATA_PROCESSOR_TIMEOUT,
        retries: int = DEFAULT_RETRY_ATTEMPTS,
        validate: bool = True,
    ) -> ProcessingResult:
        """Process the given data with specified options.

        Args:
            data: The input data to process (any type).
            timeout: Maximum processing time in seconds.
            retries: Number of retry attempts on failure.
            validate: Whether to validate input data before processing.

        Returns:
            ProcessingResult with success status and processed data.

        Raises:
            ValidationError: If validate=True and data is invalid.
            TimeoutError: If processing exceeds timeout.
            ProcessingError: If processing fails after all retries.
        """
        ...

    def batch_process(
        self,
        data_list: list[Any],
        *,
        parallel: bool = True,
        chunk_size: int = DEFAULT_BATCH_CHUNK_SIZE,
    ) -> list[ProcessingResult]:
        """Process multiple data items efficiently.

        Args:
            data_list: List of data items to process.
            parallel: Whether to process items in parallel.
            chunk_size: Number of items per processing chunk.

        Returns:
            List of ProcessingResult objects, one per input item.

        Note:
            Results are returned in the same order as input data,
            even when parallel=True.
        """
        ...


@runtime_checkable
class ConfigurableClient(Protocol):
    """Protocol for configurable API clients.

    This protocol defines the interface for HTTP clients that can be
    configured with authentication, timeouts, and retry behavior.

    Example:
        >>> client = SomeAPIClient(
        ...     api_key="secret",
        ...     base_url="https://api.example.com",
        ...     timeout=30
        ... )
        >>> response = client.get("/users", limit=10)
        >>> users = response["data"]
    """

    def get(self, endpoint: str, **params: Any) -> dict[str, Any]:
        """Make GET request to specified endpoint.

        Args:
            endpoint: API endpoint path (without base_url).
            **params: Query parameters for the request.

        Returns:
            JSON response as dictionary.

        Raises:
            APIError: If request fails after retries.
            AuthenticationError: If API key is invalid.
            TimeoutError: If request exceeds timeout.
        """
        ...

    def post(
        self, endpoint: str, data: Optional[dict[str, Any]] = None, **params: Any
    ) -> dict[str, Any]:
        """Make POST request to specified endpoint.

        Args:
            endpoint: API endpoint path (without base_url).
            data: JSON data for request body.
            **params: Query parameters for the request.

        Returns:
            JSON response as dictionary.

        Raises:
            APIError: If request fails after retries.
            AuthenticationError: If API key is invalid.
            TimeoutError: If request exceeds timeout.
        """
        ...


@runtime_checkable
class EventHandler(Protocol):
    """Protocol for handling application events.

    This protocol defines the interface for components that process
    application events with different priority levels and types.

    Example:
        >>> handler = MyEventHandler()
        >>> if handler.can_handle("user_created"):
        ...     success = handler.handle_event(
        ...         "user_created",
        ...         {"user_id": 123, "email": "user@example.com"},
        ...         priority="high"
        ...     )
    """

    def handle_event(
        self, event_type: str, event_data: dict[str, Any], *, priority: str = "normal"
    ) -> bool:
        """Handle a single event.

        Args:
            event_type: Type identifier for the event.
            event_data: Event payload data.
            priority: Event priority level ("low", "normal", "high").

        Returns:
            True if event was handled successfully, False otherwise.

        Note:
            Implementations should not raise exceptions for handling
            failures - return False instead and log errors internally.
        """
        ...

    def can_handle(self, event_type: str) -> bool:
        """Check if this handler can process the given event type.

        Args:
            event_type: Type identifier to check.

        Returns:
            True if this handler supports the event type.
        """
        ...


@runtime_checkable
class CacheProvider(Protocol):
    """Protocol for caching implementations.

    This protocol defines a generic interface for different caching
    backends (memory, Redis, file system, etc.) with TTL support.

    Example:
        >>> cache = SomeCacheProvider()
        >>> cache.set("user:123", {"name": "Alice"}, ttl=300)
        >>> user_data = cache.get("user:123")
        >>> if user_data is not None:
        ...     print(f"Found user: {user_data['name']}")
    """

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache.

        Args:
            key: Cache key to retrieve.

        Returns:
            Cached value or None if key not found/expired.
        """
        ...

    def set(self, key: str, value: Any, *, ttl: Optional[int] = None) -> bool:
        """Store value in cache.

        Args:
            key: Cache key for storage.
            value: Value to cache (must be serializable).
            ttl: Time-to-live in seconds (None for no expiration).

        Returns:
            True if value was cached successfully.
        """
        ...

    def delete(self, key: str) -> bool:
        """Remove key from cache.

        Args:
            key: Cache key to remove.

        Returns:
            True if key was removed or didn't exist.
        """
        ...

    def clear(self) -> bool:
        """Clear all cache entries.

        Returns:
            True if cache was cleared successfully.

        Warning:
            This operation may be expensive and should be used carefully
            in production environments.
        """
        ...


# Protocol composition example
@runtime_checkable
class AdvancedProcessor(DataProcessor, EventHandler, Protocol):
    """Protocol combining data processing with event handling.

    This demonstrates how to compose multiple protocols into a single
    interface specification for more complex components.

    Implementations must satisfy both DataProcessor and EventHandler
    protocols, plus any additional methods defined here.
    """

    def process_with_events(
        self,
        data: Any,
        on_progress: Optional[Any] = None,  # EventCallback would be defined elsewhere
    ) -> ProcessingResult:
        """Process data while emitting progress events.

        This method combines data processing with event emission,
        allowing callers to monitor processing progress in real-time.

        Args:
            data: Data to process.
            on_progress: Optional callback for progress updates.

        Returns:
            ProcessingResult with final processing status.

        Note:
            Progress events should be emitted at regular intervals
            during processing to provide meaningful feedback.
        """
        ...
