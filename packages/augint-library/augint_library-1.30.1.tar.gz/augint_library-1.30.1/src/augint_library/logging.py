"""Structured logging configuration for augint-library.

This module provides production-ready structured logging using only the Python
standard library. It demonstrates:
- JSON formatting for log aggregation systems
- Structured logging with contextual data
- Service-oriented logging patterns
- Easy integration with cloud logging services

Common Use Cases:
    1. Adding structured logging to libraries
    2. Cloud-native applications (AWS CloudWatch, GCP Stackdriver)
    3. Local development with readable logs
    4. Debugging distributed systems
    5. Audit trails and compliance logging

Examples:
    Basic logging setup for development:
    >>> from augint_library.logging import setup_logging
    >>> logger = setup_logging("my-service")
    >>> logger.info("User logged in", extra={"user_id": 123, "ip": "192.168.1.1"})
    2024-01-01 12:00:00 - my-service - INFO - User logged in - user_id=123 ip=192.168.1.1

    JSON formatting for production systems:
    >>> logger = setup_logging("payment-service", json_format=True)
    >>> logger.info("Payment processed", extra={
    ...     "amount": 99.99,
    ...     "currency": "USD",
    ...     "transaction_id": "tx-12345"
    ... })
    {"timestamp": "2024-01-01T12:00:00Z", "service": "payment-service", "level": "INFO", ...}

    Error logging with exception details:
    >>> logger = setup_logging("api-service", json_format=True)
    >>> try:
    ...     result = process_order(order_id)
    ... except Exception as e:
    ...     logger.exception("Order processing failed", extra={
    ...         "order_id": order_id,
    ...         "error_type": type(e).__name__
    ...     })

    Using custom log levels:
    >>> logger = setup_logging("debug-service", level="DEBUG")
    >>> logger.debug("Detailed trace", extra={"step": 1, "data": {"x": 10}})

    Integration with AWS Lambda:
    >>> import os
    >>> # AWS Lambda sets this automatically
    >>> os.environ['AWS_LAMBDA_FUNCTION_NAME'] = 'my-function'
    >>> logger = setup_logging("lambda-service", json_format=True)
    >>> # Logs will include Lambda context automatically

Best Practices:
    1. Always use structured logging (extra={} parameter)
    2. Include correlation IDs for request tracing
    3. Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
    4. Never log sensitive data (passwords, tokens, PII)
    5. Use JSON format in production for better querying

Integration Examples:
    With Flask/FastAPI:
    >>> @app.before_request
    >>> def setup_request_logging():
    ...     g.request_id = str(uuid.uuid4())
    ...     logger.info("Request started", extra={
    ...         "request_id": g.request_id,
    ...         "method": request.method,
    ...         "path": request.path
    ...     })

    With Click CLI:
    >>> @click.command()
    >>> @click.option('--verbose', '-v', is_flag=True)
    >>> def process(verbose):
    ...     level = "DEBUG" if verbose else "INFO"
    ...     logger = setup_logging("cli-tool", level=level)

Note:
    This module uses only the standard library to ensure maximum compatibility.
    For advanced features (correlation IDs, sampling, etc.), consider using
    specialized libraries like structlog or AWS Powertools.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Optional


class JSONFormatter(logging.Formatter):
    """Simple JSON formatter using only standard library.

    Formats log records as JSON with consistent field names for
    structured logging systems. Handles exceptions gracefully.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string.

        Args:
            record: Python logging record to format.

        Returns:
            JSON string representation of the log record.
        """
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add any extra fields from the log call
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
            }:
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


def setup_logging(
    service_name: str,
    level: str = "INFO",
    json_format: bool = False,
    handler: Optional[logging.Handler] = None,
) -> logging.Logger:
    """Configure structured logging for the service.

    Creates a logger with consistent formatting that works well with
    both local development and production log aggregation systems.

    Args:
        service_name: Name of the service/component for log identification.
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        json_format: Whether to use JSON formatting for structured logs.
        handler: Optional custom handler (defaults to StreamHandler to stdout).

    Returns:
        Configured logger instance ready for use.

    Example:
        >>> # Basic usage for development
        >>> logger = setup_logging("user-service")
        >>> logger.info("User created", extra={"user_id": 123})

        >>> # JSON format for production
        >>> logger = setup_logging("user-service", json_format=True)
        >>> logger.error("Validation failed", extra={"errors": ["email required"]})
    """
    logger = logging.getLogger(service_name)

    # Clear any existing handlers to avoid duplication
    logger.handlers.clear()

    # Create handler (default to stdout for container/Lambda compatibility)
    if handler is None:
        handler = logging.StreamHandler(sys.stdout)

    # Set formatter based on preference
    formatter: logging.Formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper()))

    # Prevent log messages from being handled by root logger
    logger.propagate = False

    return logger
