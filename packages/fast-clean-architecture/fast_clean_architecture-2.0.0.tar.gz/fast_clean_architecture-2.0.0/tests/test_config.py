"""Tests for configuration management."""

from datetime import datetime
from pathlib import Path

import pytest

from fast_clean_architecture.config import (
    ComponentInfo,
    ComponentsConfig,
    Config,
    ModuleComponents,
    ModuleConfig,
    ProjectConfig,
    SystemConfig,
)
from fast_clean_architecture.exceptions import ConfigurationError, ValidationError


class TestComponentInfo:
    """Test ComponentInfo model."""

    def test_component_info_creation(self):
        """Test creating a ComponentInfo instance."""
        component = ComponentInfo(
            name="user",
            file_path="systems/user_management/auth/domain/entities/user.py",
        )

        assert component.name == "user"
        assert (
            component.file_path
            == "systems/user_management/auth/domain/entities/user.py"
        )
        assert isinstance(component.created_at, str)

        # Should be valid ISO timestamp
        datetime.fromisoformat(component.created_at.replace("Z", "+00:00"))


class TestComponentsConfig:
    """Test ComponentsConfig model."""

    def test_components_config_creation(self):
        """Test creating a ComponentsConfig instance."""
        components = ComponentsConfig()

        # All component lists should be empty by default
        assert components.entities == []
        assert components.repositories == []
        assert components.value_objects == []
        assert components.services == []
        assert components.commands == []
        assert components.queries == []
        assert components.models == []
        assert components.external == []

        assert components.schemas == []


class TestModuleComponents:
    """Test ModuleComponents model."""

    def test_module_components_creation(self):
        """Test creating a ModuleComponents instance."""
        components = ModuleComponents()

        # All layer components should be ComponentsConfig instances
        assert isinstance(components.domain, ComponentsConfig)
        assert isinstance(components.application, ComponentsConfig)
        assert isinstance(components.infrastructure, ComponentsConfig)
        assert isinstance(components.presentation, ComponentsConfig)


class TestModuleConfig:
    """Test ModuleConfig model."""

    def test_module_config_creation(self):
        """Test creating a ModuleConfig instance."""
        module = ModuleConfig(description="Test module")

        assert module.description == "Test module"
        assert isinstance(module.created_at, str)
        assert isinstance(module.updated_at, str)
        assert isinstance(module.components, ModuleComponents)

        # Timestamps should be valid ISO format
        datetime.fromisoformat(module.created_at.replace("Z", "+00:00"))
        datetime.fromisoformat(module.updated_at.replace("Z", "+00:00"))


class TestSystemConfig:
    """Test SystemConfig model."""

    def test_system_config_creation(self):
        """Test creating a SystemConfig instance."""
        system = SystemConfig(description="Test system")

        assert system.description == "Test system"
        assert isinstance(system.created_at, str)
        assert isinstance(system.updated_at, str)
        assert system.modules == {}

        # Timestamps should be valid ISO format
        datetime.fromisoformat(system.created_at.replace("Z", "+00:00"))
        datetime.fromisoformat(system.updated_at.replace("Z", "+00:00"))


class TestProjectConfig:
    """Test ProjectConfig model."""

    def test_project_config_creation(self):
        """Test creating a ProjectConfig instance."""
        project = ProjectConfig(
            name="test_project", description="Test project description", version="1.0.0"
        )

        assert project.name == "test_project"
        assert project.description == "Test project description"
        assert project.version == "1.0.0"
        assert isinstance(project.created_at, str)
        assert isinstance(project.updated_at, str)
        assert project.systems == {}

        # Timestamps should be valid ISO format
        datetime.fromisoformat(project.created_at.replace("Z", "+00:00"))
        datetime.fromisoformat(project.updated_at.replace("Z", "+00:00"))


class TestConfig:
    """Test main Config model."""

    def test_config_creation(self):
        """Test creating a Config instance."""
        config = Config(
            project=ProjectConfig(
                name="test_project", description="Test description", version="1.0.0"
            )
        )

        assert isinstance(config.project, ProjectConfig)
        assert config.project.name == "test_project"

    def test_create_default(self):
        """Test creating default configuration."""
        config = Config.create_default()

        assert config.project.name == "my_project"
        assert config.project.description == "My FastAPI project"
        assert config.project.version == "0.1.0"
        assert config.project.systems == {}

    def test_save_and_load_config(self, temp_dir: Path):
        """Test saving and loading configuration."""
        config_file = temp_dir / "test-config.yaml"

        # Create and save config
        original_config = Config.create_default()
        original_config.project.name = "test_project"
        original_config.save_to_file(config_file)

        # Load config
        loaded_config = Config.load_from_file(config_file)

        assert loaded_config.project.name == "test_project"
        assert loaded_config.project.description == original_config.project.description
        assert loaded_config.project.version == original_config.project.version

    def test_load_nonexistent_file(self, temp_dir: Path):
        """Test loading non-existent configuration file."""
        config_file = temp_dir / "nonexistent.yaml"

        with pytest.raises(ConfigurationError, match="Configuration file not found"):
            Config.load_from_file(config_file)

    def test_add_system(self):
        """Test adding a system to configuration."""
        config = Config.create_default()

        # Add system
        config.add_system("user_management", "User management system")

        assert "user_management" in config.project.systems
        system = config.project.systems["user_management"]
        assert system.description == "User management system"
        assert isinstance(system.created_at, str)
        assert isinstance(system.updated_at, str)

    def test_add_duplicate_system(self):
        """Test adding duplicate system raises error."""
        config = Config.create_default()
        config.add_system("user_management", "User management system")

        with pytest.raises(
            ValidationError, match="System 'user_management' already exists"
        ):
            config.add_system("user_management", "Duplicate system")

    def test_add_module(self):
        """Test adding a module to a system."""
        config = Config.create_default()
        config.add_system("user_management", "User management system")

        # Add module
        config.add_module("user_management", "authentication", "Authentication module")

        system = config.project.systems["user_management"]
        assert "authentication" in system.modules
        module = system.modules["authentication"]
        assert module.description == "Authentication module"
        assert isinstance(module.created_at, str)
        assert isinstance(module.updated_at, str)

    def test_add_module_to_nonexistent_system(self):
        """Test adding module to non-existent system raises error."""
        config = Config.create_default()

        with pytest.raises(ValidationError, match="System 'nonexistent' not found"):
            config.add_module("nonexistent", "authentication", "Auth module")

    def test_add_duplicate_module(self):
        """Test adding duplicate module raises error."""
        config = Config.create_default()
        config.add_system("user_management", "User management system")
        config.add_module("user_management", "authentication", "Auth module")

        with pytest.raises(
            ValidationError, match="Module 'authentication' already exists"
        ):
            config.add_module("user_management", "authentication", "Duplicate module")

    def test_add_component(self):
        """Test adding a component to a module."""
        config = Config.create_default()
        config.add_system("user_management", "User management system")
        config.add_module("user_management", "authentication", "Auth module")

        # Add component
        config.add_component(
            system_name="user_management",
            module_name="authentication",
            layer="domain",
            component_type="entities",
            component_name="user",
            file_path="systems/user_management/authentication/domain/entities/user.py",
        )

        system = config.project.systems["user_management"]
        module = system.modules["authentication"]
        entities = module.components.domain.entities

        assert len(entities) == 1
        component = entities[0]
        assert component.name == "user"
        assert (
            component.file_path
            == "systems/user_management/authentication/domain/entities/user.py"
        )

    def test_add_component_invalid_layer(self):
        """Test adding component with invalid layer raises error."""
        config = Config.create_default()
        config.add_system("user_management", "User management system")
        config.add_module("user_management", "authentication", "Auth module")

        with pytest.raises(ValidationError, match="Invalid layer: invalid"):
            config.add_component(
                system_name="user_management",
                module_name="authentication",
                layer="invalid",
                component_type="entities",
                component_name="user",
            )

    def test_add_component_invalid_type(self):
        """Test adding component with invalid type raises error."""
        config = Config.create_default()
        config.add_system("user_management", "User management system")
        config.add_module("user_management", "authentication", "Auth module")

        with pytest.raises(
            ValidationError,
            match="Component type 'invalid' not valid for layer 'domain'",
        ):
            config.add_component(
                system_name="user_management",
                module_name="authentication",
                layer="domain",
                component_type="invalid",
                component_name="user",
            )

    def test_add_component_to_nonexistent_module(self):
        """Test adding component to non-existent module raises error."""
        config = Config.create_default()
        config.add_system("user_management", "User management system")

        with pytest.raises(ValidationError, match="Module 'nonexistent' not found"):
            config.add_component(
                system_name="user_management",
                module_name="nonexistent",
                layer="domain",
                component_type="entities",
                component_name="user",
            )

    def test_timestamp_updates(self):
        """Test that timestamps are updated correctly."""
        config = Config.create_default()
        original_project_time = config.project.updated_at

        # Add system - should update project timestamp
        config.add_system("user_management", "User management system")
        assert config.project.updated_at > original_project_time

        system_time = config.project.systems["user_management"].updated_at
        project_time = config.project.updated_at

        # Add module - should update system and project timestamps
        config.add_module("user_management", "authentication", "Auth module")
        assert config.project.systems["user_management"].updated_at > system_time
        assert config.project.updated_at > project_time

        module_time = (
            config.project.systems["user_management"]
            .modules["authentication"]
            .updated_at
        )
        system_time = config.project.systems["user_management"].updated_at
        project_time = config.project.updated_at

        # Add component - should update module, system, and project timestamps
        config.add_component(
            system_name="user_management",
            module_name="authentication",
            layer="domain",
            component_type="entities",
            component_name="user",
        )

        assert (
            config.project.systems["user_management"]
            .modules["authentication"]
            .updated_at
            > module_time
        )
        assert config.project.systems["user_management"].updated_at > system_time
        assert config.project.updated_at > project_time
