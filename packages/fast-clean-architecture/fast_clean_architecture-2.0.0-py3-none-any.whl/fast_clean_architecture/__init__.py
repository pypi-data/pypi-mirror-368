"""Fast Clean Architecture - CLI tool for scaffolding clean architecture in FastAPI projects."""

try:
    from importlib.metadata import version

    __version__ = version("fast-clean-architecture")
except ImportError:
    # Python < 3.8 fallback - try importlib_metadata
    try:
        from importlib_metadata import version  # type: ignore

        __version__ = version("fast-clean-architecture")
    except (ImportError, Exception):
        # Fallback version if importlib_metadata is not available or fails
        __version__ = "2.0.0"
except Exception:
    # Fallback version if package metadata is not available
    __version__ = "2.0.0"
__author__ = "Agoro, Adegbenga. B (IAM)"
__email__ = "opensource@aldentechnologies.com"

from .cli import app
from .config import Config
from .exceptions import (
    ConfigurationError,
    FastCleanArchitectureError,
    FileConflictError,
    ValidationError,
)

__all__ = [
    "app",
    "Config",
    "FastCleanArchitectureError",
    "ConfigurationError",
    "ValidationError",
    "FileConflictError",
]
