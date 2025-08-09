"""Error tracking and analytics for fast-clean-architecture."""

import hashlib
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .logging_config import get_logger

# Set up logger
logger = get_logger(__name__)


class ErrorTracker:
    """Track and analyze errors for debugging and monitoring."""

    def __init__(self) -> None:
        """Initialize error tracker."""
        self.error_counts: Counter[str] = Counter()
        self.error_details: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.error_patterns: Dict[str, int] = defaultdict(int)

    def track_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        operation: Optional[str] = None,
    ) -> str:
        """Track an error occurrence.

        Args:
            error: The exception that occurred
            context: Additional context about the error
            operation: The operation that was being performed

        Returns:
            Error ID for tracking
        """
        # Generate error ID based on error type and message
        error_signature = f"{type(error).__name__}:{str(error)}"
        error_id = hashlib.sha256(error_signature.encode()).hexdigest()[:8]

        # Get stack trace
        stack_trace = traceback.format_exc()

        # Create error record
        error_record = {
            "error_id": error_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "operation": operation,
            "context": context or {},
            "stack_trace": stack_trace,
        }

        # Update counters and storage
        self.error_counts[error_signature] += 1
        self.error_details[error_id].append(error_record)

        # Track error patterns
        error_pattern = f"{type(error).__name__}:{operation or 'unknown'}"
        self.error_patterns[error_pattern] += 1

        # Log the error with structured data
        logger.error(
            "Error tracked",
            operation="error_tracking",
            error_id=error_id,
            error_type=type(error).__name__,
            error_message=str(error),
            error_operation=operation,
            error_context=context,
            occurrence_count=self.error_counts[error_signature],
        )

        return error_id

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of tracked errors.

        Returns:
            Dictionary containing error statistics
        """
        total_errors = sum(self.error_counts.values())
        unique_errors = len(self.error_counts)

        # Get most common errors
        most_common_errors = self.error_counts.most_common(5)

        # Get most common error patterns
        most_common_patterns = dict(Counter(self.error_patterns).most_common(5))

        summary = {
            "total_errors": total_errors,
            "unique_errors": unique_errors,
            "most_common_errors": [
                {"signature": sig, "count": count} for sig, count in most_common_errors
            ],
            "most_common_patterns": most_common_patterns,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return summary

    def get_error_details(self, error_id: str) -> List[Dict[str, Any]]:
        """Get detailed information about a specific error.

        Args:
            error_id: The error ID to look up

        Returns:
            List of error occurrences for the given ID
        """
        return self.error_details.get(error_id, [])

    def log_error_summary(self) -> None:
        """Log current error summary."""
        summary = self.get_error_summary()

        logger.info("Error tracking summary", operation="error_summary", **summary)


def track_exception(
    operation: Optional[str] = None, context: Optional[Dict[str, Any]] = None
) -> Any:
    """Decorator to automatically track exceptions.

    Args:
        operation: Name of the operation being performed
        context: Additional context to include
    """

    def decorator(func: Any) -> Any:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get the global error tracker
                error_tracker = get_error_tracker()

                # Add function context
                func_context = {
                    "function": func.__name__,
                    "module": func.__module__,
                    **(context or {}),
                }

                # Track the error
                error_tracker.track_error(
                    error=e, context=func_context, operation=operation or func.__name__
                )

                # Re-raise the exception
                raise

        return wrapper

    return decorator


# Global error tracker instance
_error_tracker: Optional[ErrorTracker] = None


def get_error_tracker() -> ErrorTracker:
    """Get the global error tracker instance.

    Returns:
        Global ErrorTracker instance
    """
    global _error_tracker
    if _error_tracker is None:
        _error_tracker = ErrorTracker()
    return _error_tracker


def track_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    operation: Optional[str] = None,
) -> str:
    """Track an error using the global error tracker.

    Args:
        error: The exception that occurred
        context: Additional context about the error
        operation: The operation that was being performed

    Returns:
        Error ID for tracking
    """
    tracker = get_error_tracker()
    return tracker.track_error(error, context, operation)


def log_error_summary() -> None:
    """Log error summary using the global error tracker."""
    tracker = get_error_tracker()
    tracker.log_error_summary()
