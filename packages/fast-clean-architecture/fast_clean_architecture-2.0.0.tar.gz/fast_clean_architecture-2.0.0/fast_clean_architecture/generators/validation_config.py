"""Configuration classes for template validation."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Literal


class ValidationStrategy(Enum):
    """Available validation strategies."""

    STATIC_ONLY = "static_only"
    RUNTIME_ONLY = "runtime_only"
    BOTH = "both"
    STATIC_WITH_RUNTIME_FALLBACK = "static_with_runtime_fallback"


class LogLevel(Enum):
    """Logging levels for validation."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationConfig:
    """Simplified configuration for template validation with essential security."""

    # Core validation settings (simplified)
    strict_mode: bool = False
    allow_undefined: bool = True

    # Security settings (essential only)
    sandbox_mode: bool = True
    max_template_size_bytes: int = 64 * 1024  # 64KB
    render_timeout_seconds: int = 10
    max_variable_nesting_depth: int = 10  # Prevent deep recursion DoS

    # Basic monitoring
    enable_metrics: bool = False  # Disabled by default to reduce complexity
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = (
        "WARNING"  # Reduced logging
    )

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.max_variable_nesting_depth < 1:
            raise ValueError("max_variable_nesting_depth must be at least 1")

        if self.max_template_size_bytes <= 0:
            raise ValueError("max_template_size_bytes must be positive")


@dataclass
class ValidationMetrics:
    """Metrics collected during template validation."""

    strategy_used: str
    validation_time_ms: float
    template_size_bytes: int
    variables_count: int
    undefined_variables_found: int
    fallback_used: bool = False
    errors_encountered: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for logging."""
        return {
            "strategy_used": self.strategy_used,
            "validation_time_ms": round(self.validation_time_ms, 3),
            "template_size_bytes": self.template_size_bytes,
            "variables_count": self.variables_count,
            "undefined_variables_found": self.undefined_variables_found,
            "fallback_used": self.fallback_used,
            "errors_encountered": self.errors_encountered,
        }
