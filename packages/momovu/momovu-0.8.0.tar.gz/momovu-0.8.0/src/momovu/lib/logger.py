"""Enhanced logging configuration for Momovu.

This module provides structured logging with context, performance metrics,
and decorators for common operations.
"""

import functools
import json
import logging
import time
from contextlib import contextmanager
from typing import Any, Callable, Optional, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

_console_logging_enabled = False
_performance_metrics: dict[str, list[float]] = {}
_log_context: dict[str, Any] = {}


class StructuredFormatter(logging.Formatter):
    """Formatter that outputs structured log messages with context."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with structured context."""
        message = super().format(record)

        if hasattr(record, "context") and record.context:
            context_str = json.dumps(record.context, default=str)
            message = f"{message} | context={context_str}"

        return message


def configure_logging(verbose: int = 0, debug: bool = False) -> None:
    """Configure logging based on command line arguments.

    Args:
        verbose: Verbosity level (0=WARNING, 1=INFO, 2+=DEBUG)
        debug: Enable debug logging
    """
    global _console_logging_enabled

    if debug or verbose >= 2:
        log_level = logging.DEBUG
    elif verbose == 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    _console_logging_enabled = verbose > 0 or debug

    root_logger = logging.getLogger()
    try:
        handlers_copy = list(root_logger.handlers)
        for handler in handlers_copy:
            root_logger.removeHandler(handler)
    except (TypeError, AttributeError):
        # In case we're in a test environment with mocked logger
        pass

    if _console_logging_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = StructuredFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)

        root_logger.addHandler(console_handler)
        root_logger.setLevel(log_level)
    else:
        null_handler = logging.NullHandler()
        root_logger.addHandler(null_handler)
        root_logger.setLevel(logging.WARNING)

    logging.getLogger("PySide6").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    # Don't add handlers or set levels here - let the root logger configuration handle it
    return logger


@contextmanager
def log_context(**context: Any) -> Any:
    """Context manager to add structured context to log messages.

    Args:
        **context: Key-value pairs to add to log context
    """
    global _log_context
    old_context = _log_context.copy()
    _log_context.update(context)
    try:
        yield
    finally:
        _log_context = old_context


def log_with_context(
    logger: logging.Logger, level: int, message: str, **context: Any
) -> None:
    """Log a message with structured context.

    Args:
        logger: Logger instance
        level: Log level (e.g., logging.INFO)
        message: Log message
        **context: Additional context as key-value pairs
    """
    full_context = {**_log_context, **context}

    record = logger.makeRecord(
        logger.name,
        level,
        "(unknown file)",
        0,
        message,
        (),
        None,
    )
    record.context = full_context if full_context else None
    logger.handle(record)


def log_operation(
    operation: str,
    level: int = logging.DEBUG,
    log_args: bool = False,
    log_result: bool = False,
    log_time: bool = True,
) -> Callable[[F], F]:
    """Decorator to log function operations with context.

    Args:
        operation: Name of the operation
        level: Log level for the operation
        log_args: Whether to log function arguments
        log_result: Whether to log function result
        log_time: Whether to log execution time

    Returns:
        Decorated function
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_logger(func.__module__)

            context: dict[str, Any] = {"operation": operation}

            if log_args:
                func_args = args[1:] if args and hasattr(args[0], "__class__") else args
                if func_args:
                    context["args"] = func_args
                if kwargs:
                    context["kwargs"] = kwargs

            log_with_context(logger, level, f"Starting {operation}", **context)

            start_time = time.perf_counter() if log_time else None

            try:
                result = func(*args, **kwargs)

                if log_time and start_time is not None:
                    elapsed = time.perf_counter() - start_time
                    context["duration_ms"] = round(elapsed * 1000, 2)

                    if operation not in _performance_metrics:
                        _performance_metrics[operation] = []
                    _performance_metrics[operation].append(elapsed)

                if log_result:
                    context["result"] = str(result)[:100]  # Truncate long results

                log_with_context(logger, level, f"Completed {operation}", **context)

                return result

            except Exception as e:
                if log_time and start_time:
                    elapsed = time.perf_counter() - start_time
                    context["duration_ms"] = round(elapsed * 1000, 2)

                context["error"] = str(e)
                context["error_type"] = type(e).__name__

                log_with_context(
                    logger, logging.ERROR, f"Failed {operation}", **context
                )
                raise

        return wrapper  # type: ignore

    return decorator


def log_performance(operation: str) -> Callable[[F], F]:
    """Decorator to log performance metrics for a function.

    This is a simplified version of log_operation focused on performance.

    Args:
        operation: Name of the operation being measured

    Returns:
        Decorated function
    """
    return log_operation(
        operation,
        level=logging.DEBUG,
        log_args=False,
        log_result=False,
        log_time=True,
    )


def log_error_with_context(
    logger: logging.Logger,
    message: str,
    error: Optional[Exception] = None,
    **context: Any,
) -> None:
    """Log an error with additional context information.

    Args:
        logger: Logger instance
        message: Error message
        error: Optional exception object
        **context: Additional context as key-value pairs
    """
    if error:
        context["error"] = str(error)
        context["error_type"] = type(error).__name__
        log_with_context(logger, logging.ERROR, message, **context)
        logger.debug("Exception details:", exc_info=error)
    else:
        log_with_context(logger, logging.ERROR, message, **context)


def get_performance_metrics() -> dict[str, dict[str, float]]:
    """Get aggregated performance metrics.

    Returns:
        Dictionary with operation names and their statistics
    """
    metrics = {}
    for operation, times in _performance_metrics.items():
        if times:
            metrics[operation] = {
                "count": len(times),
                "total": sum(times),
                "average": sum(times) / len(times),
                "min": min(times),
                "max": max(times),
            }
    return metrics


def clear_performance_metrics() -> None:
    """Clear all stored performance metrics."""
    global _performance_metrics
    _performance_metrics = {}


def log_debug(logger: logging.Logger, message: str, **context: Any) -> None:
    """Convenience function for debug logging with context."""
    log_with_context(logger, logging.DEBUG, message, **context)


def log_info(logger: logging.Logger, message: str, **context: Any) -> None:
    """Convenience function for info logging with context."""
    log_with_context(logger, logging.INFO, message, **context)


def log_warning(logger: logging.Logger, message: str, **context: Any) -> None:
    """Convenience function for warning logging with context."""
    log_with_context(logger, logging.WARNING, message, **context)


def log_error(logger: logging.Logger, message: str, **context: Any) -> None:
    """Convenience function for error logging with context."""
    log_with_context(logger, logging.ERROR, message, **context)


class LogMessages:
    """Standardized log messages for consistency."""

    DOCUMENT_LOADING = "Loading document"
    DOCUMENT_LOADED = "Document loaded successfully"
    DOCUMENT_LOAD_FAILED = "Failed to load document"
    DOCUMENT_CLOSED = "Document closed"

    RENDERING_PAGE = "Rendering page"
    RENDERING_COMPLETE = "Rendering complete"
    RENDERING_FAILED = "Rendering failed"

    NAVIGATION_PAGE_CHANGE = "Page changed"
    NAVIGATION_VIEW_MODE_CHANGE = "View mode changed"

    UI_WINDOW_INITIALIZED = "Window initialized"
    UI_TOOLBAR_CREATED = "Toolbar created"
    UI_MENU_CREATED = "Menu created"

    PERF_OPERATION_START = "Operation started"
    PERF_OPERATION_COMPLETE = "Operation completed"
    PERF_OPERATION_FAILED = "Operation failed"
