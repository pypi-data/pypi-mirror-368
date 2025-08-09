"""Performance metrics for fast-clean-architecture."""

import functools
import time
from typing import Any, Callable, TypeVar, cast

from .logging_config import get_logger

# Type variables for generic function decorators
F = TypeVar("F", bound=Callable[..., Any])
R = TypeVar("R")

# Set up logger
logger = get_logger(__name__)


def measure_execution_time(operation_name: str) -> Callable[[F], F]:
    """Decorator to measure and log execution time of functions.

    Args:
        operation_name: Name of the operation being measured

    Returns:
        Decorator function that measures execution time
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Log performance metrics
                logger.info(
                    f"{operation_name} completed",
                    operation=operation_name,
                    execution_time_ms=round(execution_time * 1000, 2),
                    success=True,
                )

                return result
            except Exception as e:
                execution_time = time.time() - start_time

                # Log performance metrics with error
                logger.error(
                    f"{operation_name} failed",
                    operation=operation_name,
                    execution_time_ms=round(execution_time * 1000, 2),
                    error=str(e),
                    error_type=type(e).__name__,
                    success=False,
                )

                # Re-raise the exception
                raise

        return cast(F, wrapper)

    return decorator


class PerformanceTracker:
    """Context manager for tracking performance of code blocks."""

    def __init__(self, operation_name: str, **context: Any):
        """Initialize performance tracker.

        Args:
            operation_name: Name of the operation being tracked
            context: Additional context to include in logs
        """
        self.operation_name = operation_name
        self.context = context
        self.start_time: float = 0

    def __enter__(self) -> "PerformanceTracker":
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        execution_time = time.time() - self.start_time

        # Prepare log context
        log_context = {
            "operation": self.operation_name,
            "execution_time_ms": round(execution_time * 1000, 2),
            "success": exc_type is None,
            **self.context,
        }

        if exc_type is None:
            # Log successful completion
            logger.info(f"{self.operation_name} completed", **log_context)
        else:
            # Log error
            logger.error(
                f"{self.operation_name} failed",
                error=str(exc_val),
                error_type=exc_type.__name__,
                **log_context,
            )
