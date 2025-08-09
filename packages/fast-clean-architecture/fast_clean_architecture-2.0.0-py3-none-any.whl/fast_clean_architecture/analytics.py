"""Usage analytics for fast-clean-architecture."""

import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .logging_config import get_logger

# Set up logger
logger = get_logger(__name__)


class UsageAnalytics:
    """Track and analyze usage patterns of the tool."""

    def __init__(self) -> None:
        """Initialize usage analytics."""
        self.session_start = time.time()
        self.command_counts: Counter[str] = Counter()
        self.component_types: Counter[str] = Counter()
        self.layer_usage: Counter[str] = Counter()
        self.system_usage: Counter[str] = Counter()
        self.execution_times: Dict[str, List[float]] = defaultdict(list)
        self.daily_usage: Dict[str, int] = defaultdict(int)

    def track_command(
        self, command: str, execution_time: Optional[float] = None, **context: Any
    ) -> None:
        """Track command usage.

        Args:
            command: The command that was executed
            execution_time: Time taken to execute the command
            context: Additional context about the command
        """
        # Update counters
        self.command_counts[command] += 1

        # Track execution time if provided
        if execution_time is not None:
            self.execution_times[command].append(execution_time)

        # Track daily usage
        today = datetime.now().strftime("%Y-%m-%d")
        self.daily_usage[today] += 1

        # Extract specific analytics from context
        if "component_type" in context:
            self.component_types[context["component_type"]] += 1

        if "layer" in context:
            self.layer_usage[context["layer"]] += 1

        if "system_name" in context:
            self.system_usage[context["system_name"]] += 1

        # Log the usage
        logger.info(
            "Command usage tracked",
            operation="usage_tracking",
            command=command,
            execution_time=execution_time,
            session_duration=time.time() - self.session_start,
            **context,
        )

    def track_component_creation(
        self,
        system_name: str,
        module_name: str,
        layer: str,
        component_type: str,
        component_name: str,
        execution_time: Optional[float] = None,
    ) -> None:
        """Track component creation specifically.

        Args:
            system_name: Name of the system
            module_name: Name of the module
            layer: Layer where component was created
            component_type: Type of component
            component_name: Name of the component
            execution_time: Time taken to create the component
        """
        self.track_command(
            command="create_component",
            execution_time=execution_time,
            system_name=system_name,
            module_name=module_name,
            layer=layer,
            component_type=component_type,
            component_name=component_name,
        )

    def get_usage_summary(self) -> Dict[str, Any]:
        """Get comprehensive usage summary.

        Returns:
            Dictionary containing usage statistics
        """
        session_duration = time.time() - self.session_start
        total_commands = sum(self.command_counts.values())

        # Calculate average execution times
        avg_execution_times = {}
        for command, times in self.execution_times.items():
            if times:
                avg_execution_times[command] = {
                    "average_ms": round(sum(times) / len(times) * 1000, 2),
                    "min_ms": round(min(times) * 1000, 2),
                    "max_ms": round(max(times) * 1000, 2),
                    "count": len(times),
                }

        summary = {
            "session": {
                "duration_seconds": round(session_duration, 2),
                "total_commands": total_commands,
                "commands_per_minute": (
                    round(total_commands / (session_duration / 60), 2)
                    if session_duration > 0
                    else 0
                ),
            },
            "commands": dict(self.command_counts.most_common()),
            "component_types": dict(self.component_types.most_common()),
            "layers": dict(self.layer_usage.most_common()),
            "systems": dict(self.system_usage.most_common()),
            "performance": avg_execution_times,
            "daily_usage": dict(self.daily_usage),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return summary

    def get_productivity_metrics(self) -> Dict[str, Any]:
        """Get productivity-focused metrics.

        Returns:
            Dictionary containing productivity metrics
        """
        session_duration = time.time() - self.session_start
        total_components = self.command_counts.get("create_component", 0)

        # Calculate components per hour
        components_per_hour = (
            (total_components / (session_duration / 3600))
            if session_duration > 0
            else 0
        )

        # Most productive layer/type combinations
        layer_type_combinations: Counter[str] = Counter()
        for layer in self.layer_usage:
            for comp_type in self.component_types:
                # This is a simplified combination - in practice you'd track actual pairs
                layer_type_combinations[f"{layer}/{comp_type}"] = min(
                    self.layer_usage[layer], self.component_types[comp_type]
                )

        metrics = {
            "components_created": total_components,
            "components_per_hour": round(components_per_hour, 2),
            "average_time_per_component": (
                round(session_duration / total_components, 2)
                if total_components > 0
                else 0
            ),
            "most_used_layer": (
                self.layer_usage.most_common(1)[0] if self.layer_usage else None
            ),
            "most_used_component_type": (
                self.component_types.most_common(1)[0] if self.component_types else None
            ),
            "layer_type_combinations": dict(layer_type_combinations.most_common(5)),
            "session_duration_minutes": round(session_duration / 60, 2),
        }

        return metrics

    def log_usage_summary(self) -> None:
        """Log current usage summary."""
        summary = self.get_usage_summary()

        logger.info("Usage analytics summary", operation="usage_summary", **summary)

    def log_productivity_metrics(self) -> None:
        """Log productivity metrics."""
        metrics = self.get_productivity_metrics()

        logger.info("Productivity metrics", operation="productivity_metrics", **metrics)


# Global analytics instance
_analytics: Optional[UsageAnalytics] = None


def get_analytics() -> UsageAnalytics:
    """Get the global analytics instance.

    Returns:
        Global UsageAnalytics instance
    """
    global _analytics
    if _analytics is None:
        _analytics = UsageAnalytics()
    return _analytics


def track_command_usage(
    command: str, execution_time: Optional[float] = None, **context: Any
) -> None:
    """Track command usage using the global analytics instance.

    Args:
        command: The command that was executed
        execution_time: Time taken to execute the command
        context: Additional context about the command
    """
    analytics = get_analytics()
    analytics.track_command(command, execution_time, **context)


def track_component_creation(
    system_name: str,
    module_name: str,
    layer: str,
    component_type: str,
    component_name: str,
    execution_time: Optional[float] = None,
) -> None:
    """Track component creation using the global analytics instance.

    Args:
        system_name: Name of the system
        module_name: Name of the module
        layer: Layer where component was created
        component_type: Type of component
        component_name: Name of the component
        execution_time: Time taken to create the component
    """
    analytics = get_analytics()
    analytics.track_component_creation(
        system_name, module_name, layer, component_type, component_name, execution_time
    )


def log_usage_summary() -> None:
    """Log usage summary using the global analytics instance."""
    analytics = get_analytics()
    analytics.log_usage_summary()


def log_productivity_metrics() -> None:
    """Log productivity metrics using the global analytics instance."""
    analytics = get_analytics()
    analytics.log_productivity_metrics()
