"""Factory pattern implementation for generators.

This module provides a factory for creating different types of generators
with proper dependency injection and type safety.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Protocol, Type, TypeVar, Union

from rich.console import Console

from ..config import Config
from ..protocols import (
    SecurePathHandler,
    TemplateValidatorProtocol,
)
from .component_generator import ComponentGenerator
from .config_updater import ConfigUpdater
from .package_generator import PackageGenerator
from .template_validator import SimpleTemplateValidator
from .validation_config import ValidationConfig

# Type variables for enhanced type safety
T = TypeVar("T")
GeneratorType = TypeVar("GeneratorType")


class GeneratorProtocol(Protocol):
    """Base protocol for all generators."""

    pass


# ComponentGeneratorProtocol is imported from protocols module


class GeneratorFactoryProtocol(Protocol):
    """Protocol for generator factories."""

    def create_generator(self, generator_type: str, **kwargs: Any) -> GeneratorProtocol:
        """Create a generator of the specified type.

        Args:
            generator_type: Type of generator to create
            **kwargs: Additional arguments for generator creation

        Returns:
            Generator instance

        Raises:
            ValueError: If generator type is not supported
        """
        ...


class DependencyContainer:
    """Container for managing dependencies and their lifecycle.

    Phase 3 Architecture Cleanup: Requires explicit dependency injection.
    No fallback creation - all dependencies must be provided explicitly.
    """

    def __init__(
        self,
        config: Config,
        template_validator: TemplateValidatorProtocol,
        path_handler: SecurePathHandler[Union[str, Path]],
        console: Optional[Console] = None,
    ):
        """Initialize container with explicit dependencies.

        Args:
            config: Configuration object
            template_validator: Template validator (required)
            path_handler: Secure path handler (required)
            console: Optional console for output

        Raises:
            ValueError: If required dependencies are None
        """
        if template_validator is None:
            raise ValueError("template_validator is required - no fallback creation")
        if path_handler is None:
            raise ValueError("path_handler is required - no fallback creation")

        self.config = config
        if console is None:
            raise ValueError(
                "Console dependency must be provided explicitly (Phase 3 Architecture Cleanup)"
            )
        self.console = console
        self.template_validator = template_validator
        self.path_handler = path_handler


class GeneratorFactory(GeneratorFactoryProtocol):
    """Factory for creating generators with dependency injection.

    This factory implements the factory pattern and provides dependency
    injection for all generator types, ensuring loose coupling and
    better testability.
    """

    def __init__(self, dependency_container: DependencyContainer):
        """Initialize factory with dependency container.

        Args:
            dependency_container: Container with all required dependencies
        """
        self.dependencies = dependency_container

        # Registry of available generators
        self._generators: Dict[str, Type[GeneratorProtocol]] = {
            "component": ComponentGenerator,
            "package": PackageGenerator,
            "config": ConfigUpdater,
        }

    def create_generator(self, generator_type: str, **kwargs: Any) -> GeneratorProtocol:
        """Create a generator of the specified type with dependency injection.

        Args:
            generator_type: Type of generator ('component', 'package', 'config')
            **kwargs: Additional arguments for specific generator types

        Returns:
            Generator instance with injected dependencies

        Raises:
            ValueError: If generator type is not supported
        """
        if generator_type not in self._generators:
            available_types = ", ".join(self._generators.keys())
            raise ValueError(
                f"Unsupported generator type: {generator_type}. "
                f"Available types: {available_types}"
            )

        # Create generator with appropriate dependencies
        if generator_type == "component":
            return self._create_component_generator(**kwargs)
        elif generator_type == "package":
            return self._create_package_generator(**kwargs)
        elif generator_type == "config":
            return self._create_config_updater(**kwargs)
        else:
            # This should never happen due to the check above, but included for completeness
            raise ValueError(f"Unknown generator type: {generator_type}")

    def _create_component_generator(self, **kwargs: Any) -> ComponentGenerator:
        """Create ComponentGenerator with injected dependencies."""
        return ComponentGenerator(
            config=self.dependencies.config,
            template_validator=self.dependencies.template_validator,
            path_handler=self.dependencies.path_handler,
            console=self.dependencies.console,
            **kwargs,
        )

    def _create_package_generator(self, **kwargs: Any) -> PackageGenerator:
        """Create PackageGenerator with injected dependencies."""
        return PackageGenerator(console=self.dependencies.console, **kwargs)

    def _create_config_updater(
        self, config_path: Optional[Path] = None, **kwargs: Any
    ) -> ConfigUpdater:
        """Create ConfigUpdater with injected dependencies."""
        if config_path is None:
            # Use default config path from dependencies
            config_path = Path("fca_config.yaml")

        return ConfigUpdater(
            config_path=config_path, console=self.dependencies.console, **kwargs
        )

    def register_generator(
        self, generator_type: str, generator_class: Type[GeneratorProtocol]
    ) -> None:
        """Register a new generator type.

        Args:
            generator_type: Name of the generator type
            generator_class: Class implementing the generator
        """
        self._generators[generator_type] = generator_class

    def get_available_types(self) -> list[str]:
        """Get list of available generator types.

        Returns:
            List of available generator type names
        """
        return list(self._generators.keys())


# Convenience function for creating a factory with explicit dependencies
def create_generator_factory(
    config: Config, console: Optional[Console] = None
) -> GeneratorFactory:
    """Create a generator factory with explicit dependencies.

    Phase 3 Architecture Cleanup: Creates all dependencies explicitly.
    Factory function creates Console if not provided.

    Args:
        config: Configuration object
        console: Optional console for output (creates default if None)

    Returns:
        Configured generator factory

    Raises:
        ImportError: If required dependencies cannot be imported
        ValueError: If dependencies cannot be created
    """
    # Create console if not provided (factory responsibility)
    if console is None:
        console = Console()
    # Create template environment explicitly
    import jinja2
    from jinja2.sandbox import SandboxedEnvironment

    from ..templates import TEMPLATES_DIR

    template_env = SandboxedEnvironment(
        loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Create validation config explicitly
    validation_config = ValidationConfig(
        sandbox_mode=True,
        max_template_size_bytes=64 * 1024,  # 64KB limit
        render_timeout_seconds=10,
        max_variable_nesting_depth=10,
    )

    # Create template validator explicitly
    template_validator = SimpleTemplateValidator(template_env, validation_config)

    # Create path handler explicitly
    path_handler = SecurePathHandler[Union[str, Path]](
        max_path_length=4096,
        allowed_extensions=[".py", ".j2", ".yaml", ".yml", ".json"],
    )

    # Create dependency container with explicit dependencies
    dependency_container = DependencyContainer(
        config=config,
        template_validator=template_validator,
        path_handler=path_handler,
        console=console,
    )

    return GeneratorFactory(dependency_container)
