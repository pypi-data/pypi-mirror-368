"""Test configuration and fixtures."""

import shutil
import tempfile
from pathlib import Path
from typing import Generator, cast

import pytest
from rich.console import Console

from fast_clean_architecture.config import Config
from fast_clean_architecture.generators import (
    ConfigUpdater,
    PackageGenerator,
)
from fast_clean_architecture.generators.generator_factory import (
    create_generator_factory,
)
from fast_clean_architecture.protocols import ComponentGeneratorProtocol


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def config_file(temp_dir: Path) -> Path:
    """Create a temporary config file."""
    return temp_dir / "fca_config.yaml"


@pytest.fixture
def sample_config() -> Config:
    """Create a sample configuration for testing."""
    config = Config.create_default()
    config.project.name = "test_project"
    config.project.description = "Test project description"
    config.project.version = "1.0.0"
    return config


@pytest.fixture
def console() -> Console:
    """Create a console instance for testing."""
    return Console(file=open("/dev/null", "w"), force_terminal=False)


@pytest.fixture
def config_updater(config_file: Path, console: Console) -> ConfigUpdater:
    """Create a ConfigUpdater instance for testing."""
    return ConfigUpdater(config_file, console)


@pytest.fixture
def package_generator(sample_config: Config, console: Console) -> PackageGenerator:
    """Create a PackageGenerator instance for testing."""
    return PackageGenerator(console)


@pytest.fixture
def component_generator(
    sample_config: Config, console: Console
) -> ComponentGeneratorProtocol:
    """Create a ComponentGenerator instance for testing."""
    factory = create_generator_factory(sample_config, console)
    return cast(ComponentGeneratorProtocol, factory.create_generator("component"))


@pytest.fixture
def project_with_system(
    temp_dir: Path, config_updater: ConfigUpdater, package_generator: PackageGenerator
) -> Path:
    """Create a test project with a system."""
    # Create system structure
    package_generator.create_system_structure(
        base_path=temp_dir,
        system_name="test_system",
        dry_run=False,
    )

    # Update config
    config_updater.add_system("test_system", "Test system description")

    return temp_dir


@pytest.fixture
def project_with_module(
    project_with_system: Path,
    config_updater: ConfigUpdater,
    package_generator: PackageGenerator,
) -> Path:
    """Create a test project with a system and module."""
    # Create module structure
    package_generator.create_module_structure(
        base_path=project_with_system,
        system_name="test_system",
        module_name="test_module",
        dry_run=False,
    )

    # Update config
    config_updater.add_module("test_system", "test_module", "Test module description")

    return project_with_system
