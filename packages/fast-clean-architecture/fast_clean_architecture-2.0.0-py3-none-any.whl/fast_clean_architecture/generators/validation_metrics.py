"""Performance monitoring and metrics collection for template validation."""

import logging
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, Optional

from .validation_config import ValidationMetrics

__all__ = ["ValidationMetrics", "ValidationStats", "ValidationMetricsCollector"]

logger = logging.getLogger(__name__)


@dataclass
class ValidationStats:
    """Simplified statistics for template validation operations."""

    total_validations: int = 0
    successful_validations: int = 0
    failed_validations: int = 0
    errors_by_type: Dict[str, int] = field(default_factory=dict)
    fallback_used_count: int = 0
    total_time_ms: float = 0.0
    min_time_ms: float = float("inf")
    max_time_ms: float = 0.0
    strategy_usage: Dict[str, int] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def update(
        self,
        metrics: ValidationMetrics,
        success: bool,
        error_type: Optional[str] = None,
    ) -> None:
        """Update statistics with new validation metrics."""
        with self._lock:
            self.total_validations += 1

            if success:
                self.successful_validations += 1
            else:
                self.failed_validations += 1
                if error_type:
                    self.errors_by_type[error_type] = (
                        self.errors_by_type.get(error_type, 0) + 1
                    )

            if metrics.fallback_used:
                self.fallback_used_count += 1

            # Update timing statistics
            self.total_time_ms += metrics.validation_time_ms
            self.min_time_ms = min(self.min_time_ms, metrics.validation_time_ms)
            self.max_time_ms = max(self.max_time_ms, metrics.validation_time_ms)

            # Update strategy usage
            strategy = metrics.strategy_used
            self.strategy_usage[strategy] = self.strategy_usage.get(strategy, 0) + 1

    @property
    def average_time_ms(self) -> float:
        """Calculate average validation time."""
        if self.total_validations == 0:
            return 0.0
        return self.total_time_ms / self.total_validations

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_validations == 0:
            return 0.0
        return (self.successful_validations / self.total_validations) * 100

    @property
    def fallback_rate(self) -> float:
        """Calculate fallback usage rate as percentage."""
        if self.total_validations == 0:
            return 0.0
        return (self.fallback_used_count / self.total_validations) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert statistics to dictionary for reporting."""
        return {
            "total_validations": self.total_validations,
            "successful_validations": self.successful_validations,
            "failed_validations": self.failed_validations,
            "success_rate_percent": round(self.success_rate, 2),
            "fallback_used_count": self.fallback_used_count,
            "fallback_rate_percent": round(self.fallback_rate, 2),
            "timing": {
                "total_time_ms": round(self.total_time_ms, 3),
                "average_time_ms": round(self.average_time_ms, 3),
                "min_time_ms": (
                    round(self.min_time_ms, 3)
                    if self.min_time_ms != float("inf")
                    else 0
                ),
                "max_time_ms": round(self.max_time_ms, 3),
            },
            "strategy_usage": self.strategy_usage,
            "error_types": self.errors_by_type,
        }


class ValidationMetricsCollector:
    """Simplified collector for validation metrics."""

    def __init__(self) -> None:
        self.stats = ValidationStats()

    def record_validation(
        self, success: bool, error_type: Optional[str] = None
    ) -> None:
        """Record a validation operation.

        Args:
            success: Whether the validation succeeded
            error_type: Type of error if validation failed
        """
        self.stats.total_validations += 1
        if success:
            self.stats.successful_validations += 1
        else:
            self.stats.failed_validations += 1
            if error_type:
                self.stats.errors_by_type[error_type] = (
                    self.stats.errors_by_type.get(error_type, 0) + 1
                )

    def get_stats(self) -> ValidationStats:
        """Get current statistics."""
        return self.stats

    def reset(self) -> None:
        """Reset all statistics."""
        self.stats = ValidationStats()


# Global metrics collector instance
_metrics_collector = ValidationMetricsCollector()


def get_metrics_collector() -> ValidationMetricsCollector:
    """Get the global metrics collector instance."""
    return _metrics_collector


@contextmanager
def timed_validation(
    strategy_name: str,
    template_size: int,
    variables_count: int,
    enable_timing: bool = True,
) -> Generator[ValidationMetrics, None, None]:
    """Context manager for timing validation operations."""
    start_time = time.perf_counter()

    metrics = ValidationMetrics(
        strategy_used=strategy_name,
        validation_time_ms=0.0,
        template_size_bytes=template_size,
        variables_count=variables_count,
        undefined_variables_found=0,
    )

    try:
        yield metrics
    finally:
        if enable_timing:
            end_time = time.perf_counter()
            metrics.validation_time_ms = (end_time - start_time) * 1000

            # Log slow validations
            if metrics.validation_time_ms > 100:  # Configurable threshold
                logger.warning(
                    f"Slow validation detected: {strategy_name} took {metrics.validation_time_ms:.3f}ms"
                )


@contextmanager
def validation_timeout(timeout_seconds: float) -> Generator[None, None, None]:
    """Context manager for validation timeout (placeholder for future implementation)."""
    # Note: This is a placeholder. Full timeout implementation would require
    # threading or async support, which depends on the application architecture.
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            logger.warning(
                f"Validation exceeded timeout: {elapsed:.3f}s > {timeout_seconds}s"
            )
