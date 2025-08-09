"""Health monitoring for fast-clean-architecture."""

import os
import sys
import time
from typing import Any, Dict, Optional

import psutil  # type: ignore

from .logging_config import get_logger

# Set up logger
logger = get_logger(__name__)


class HealthMonitor:
    """Monitor system health and resource usage."""

    def __init__(self) -> None:
        """Initialize health monitor."""
        self.start_time = time.time()

    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health metrics.

        Returns:
            Dictionary containing system health information
        """
        try:
            # Get process information
            process = psutil.Process()

            # Memory usage
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()

            # CPU usage
            cpu_percent = process.cpu_percent()

            # System memory
            system_memory = psutil.virtual_memory()

            # Disk usage for current directory
            disk_usage = psutil.disk_usage(".")

            health_data = {
                "timestamp": time.time(),
                "uptime_seconds": time.time() - self.start_time,
                "process": {
                    "pid": os.getpid(),
                    "memory_rss_mb": round(memory_info.rss / 1024 / 1024, 2),
                    "memory_vms_mb": round(memory_info.vms / 1024 / 1024, 2),
                    "memory_percent": round(memory_percent, 2),
                    "cpu_percent": round(cpu_percent, 2),
                },
                "system": {
                    "memory_total_gb": round(
                        system_memory.total / 1024 / 1024 / 1024, 2
                    ),
                    "memory_available_gb": round(
                        system_memory.available / 1024 / 1024 / 1024, 2
                    ),
                    "memory_used_percent": round(system_memory.percent, 2),
                    "disk_total_gb": round(disk_usage.total / 1024 / 1024 / 1024, 2),
                    "disk_free_gb": round(disk_usage.free / 1024 / 1024 / 1024, 2),
                    "disk_used_percent": round(
                        (disk_usage.used / disk_usage.total) * 100, 2
                    ),
                },
                "python": {
                    "version": sys.version,
                    "executable": sys.executable,
                },
            }

            return health_data

        except Exception as e:
            logger.error(
                "Failed to get system health metrics",
                operation="get_system_health",
                error=str(e),
                error_type=type(e).__name__,
            )
            return {"timestamp": time.time(), "error": str(e), "status": "unhealthy"}

    def log_health_status(self) -> None:
        """Log current health status."""
        health_data = self.get_system_health()

        if "error" in health_data:
            logger.error(
                "System health check failed", operation="health_check", **health_data
            )
        else:
            logger.info("System health check", operation="health_check", **health_data)

    def check_resource_limits(
        self,
        max_memory_mb: Optional[int] = None,
        max_cpu_percent: Optional[float] = None,
    ) -> bool:
        """Check if resource usage is within limits.

        Args:
            max_memory_mb: Maximum memory usage in MB
            max_cpu_percent: Maximum CPU usage percentage

        Returns:
            True if within limits, False otherwise
        """
        health_data = self.get_system_health()

        if "error" in health_data:
            return False

        process_data = health_data.get("process", {})

        # Check memory limit
        if max_memory_mb and process_data.get("memory_rss_mb", 0) > max_memory_mb:
            logger.warning(
                "Memory usage exceeds limit",
                operation="resource_check",
                current_memory_mb=process_data.get("memory_rss_mb"),
                limit_memory_mb=max_memory_mb,
            )
            return False

        # Check CPU limit
        if max_cpu_percent and process_data.get("cpu_percent", 0) > max_cpu_percent:
            logger.warning(
                "CPU usage exceeds limit",
                operation="resource_check",
                current_cpu_percent=process_data.get("cpu_percent"),
                limit_cpu_percent=max_cpu_percent,
            )
            return False

        return True


# Global health monitor instance
_health_monitor: Optional[HealthMonitor] = None


def get_health_monitor() -> HealthMonitor:
    """Get the global health monitor instance.

    Returns:
        Global HealthMonitor instance
    """
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor


def log_startup_health() -> None:
    """Log health status at application startup."""
    monitor = get_health_monitor()
    monitor.log_health_status()

    logger.info(
        "Application started",
        operation="startup",
        pid=os.getpid(),
        python_version=sys.version.split()[0],
    )
