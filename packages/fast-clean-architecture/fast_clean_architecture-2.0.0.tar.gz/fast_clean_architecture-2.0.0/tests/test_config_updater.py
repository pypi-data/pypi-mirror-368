"""Tests for ConfigUpdater functionality."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest
from rich.console import Console

from fast_clean_architecture.config import Config
from fast_clean_architecture.exceptions import ConfigurationError, ValidationError
from fast_clean_architecture.generators.config_updater import ConfigUpdater


class TestConfigUpdater:
    """Test ConfigUpdater class functionality."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def config_file(self, temp_project_dir: Path):
        """Create a test configuration file."""
        config_path = temp_project_dir / "fca_config.yaml"
        config = Config.create_default()
        config.project.name = "test_project"
        config.project.description = "Test project for ConfigUpdater"
        config.save_to_file(config_path)
        return config_path

    @pytest.fixture
    def console(self):
        """Create a console instance for testing."""
        return Console()

    @pytest.fixture
    def config_updater(self, config_file: Path, console: Console):
        """Create a ConfigUpdater instance for testing."""
        return ConfigUpdater(config_file, console)

    def test_config_updater_initialization(self, config_file: Path, console: Console):
        """Test ConfigUpdater initialization."""
        updater = ConfigUpdater(config_file, console)

        assert updater.config_path == config_file
        assert updater.console == console
        assert updater.config is not None
        assert updater.config.project.name == "test_project"

    def test_add_system(self, config_updater: ConfigUpdater, temp_project_dir: Path):
        """Test adding a system through ConfigUpdater."""
        system_name = "user_management"
        description = "User management system"

        config_updater.add_system(system_name, description)

        # Verify system was added
        assert system_name in config_updater.config.project.systems
        system = config_updater.config.project.systems[system_name]
        assert system.description == description

        # Verify config file was updated
        reloaded_config = Config.load_from_file(config_updater.config_path)
        assert system_name in reloaded_config.project.systems

    def test_add_module(self, config_updater: ConfigUpdater, temp_project_dir: Path):
        """Test adding a module through ConfigUpdater."""
        system_name = "user_management"
        module_name = "authentication"
        system_description = "User management system"
        module_description = "Authentication module"

        # Add system first
        config_updater.add_system(system_name, system_description)

        # Add module
        is_new = config_updater.add_module(system_name, module_name, module_description)

        assert is_new is True
        system = config_updater.config.project.systems[system_name]
        assert module_name in system.modules
        module = system.modules[module_name]
        assert module.description == module_description

    def test_add_component(self, config_updater: ConfigUpdater, temp_project_dir: Path):
        """Test adding a component through ConfigUpdater."""
        system_name = "user_management"
        module_name = "authentication"
        component_name = "user"
        layer = "domain"
        component_type = "entities"

        # Setup system and module
        config_updater.add_system(system_name, "User management system")
        config_updater.add_module(system_name, module_name, "Authentication module")

        # Add component
        config_updater.add_component(
            system_name=system_name,
            module_name=module_name,
            layer=layer,
            component_type=component_type,
            component_name=component_name,
        )

        # Verify component was added
        system = config_updater.config.project.systems[system_name]
        module = system.modules[module_name]
        components = module.components.model_dump()
        component_names = [comp["name"] for comp in components[layer][component_type]]
        assert component_name in component_names


class TestSyncConfig:
    """Test sync_config functionality."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def config_file(self, temp_project_dir: Path):
        """Create a test configuration file."""
        config_path = temp_project_dir / "fca_config.yaml"
        config = Config.create_default()
        config.project.name = "test_project"
        config.project.description = "Test project for sync_config"
        config.save_to_file(config_path)
        return config_path

    @pytest.fixture
    def console(self):
        """Create a console instance for testing."""
        return Console()

    @pytest.fixture
    def config_updater(self, config_file: Path, console: Console):
        """Create a ConfigUpdater instance for testing."""
        return ConfigUpdater(config_file, console)

    def create_test_system_structure(
        self, project_dir: Path, system_name: str, modules: list
    ):
        """Helper to create test system directory structure."""
        systems_dir = project_dir / "systems"
        system_dir = systems_dir / system_name

        for module_name in modules:
            module_dir = system_dir / module_name
            # Create basic Clean Architecture structure
            for layer in ["domain", "application", "infrastructure", "presentation"]:
                layer_dir = module_dir / layer
                layer_dir.mkdir(parents=True, exist_ok=True)

                # Create some test files
                if layer == "domain":
                    entities_dir = layer_dir / "entities"
                    entities_dir.mkdir(exist_ok=True)
                    (entities_dir / "user.py").write_text("# User entity")
                elif layer == "application":
                    services_dir = layer_dir / "services"
                    services_dir.mkdir(exist_ok=True)
                    (services_dir / "auth_service.py").write_text("# Auth service")
                elif layer == "infrastructure":
                    repositories_dir = layer_dir / "repositories"
                    repositories_dir.mkdir(exist_ok=True)
                    (repositories_dir / "user_repository.py").write_text(
                        "# User repository"
                    )
                elif layer == "presentation":
                    controllers_dir = layer_dir / "controllers"
                    controllers_dir.mkdir(exist_ok=True)
                    (controllers_dir / "auth_controller.py").write_text(
                        "# Auth controller"
                    )

    def test_sync_config_empty_project(
        self, config_updater: ConfigUpdater, temp_project_dir: Path
    ):
        """Test sync_config with empty project (no systems directory)."""
        result = config_updater.sync_config(temp_project_dir, dry_run=True)

        assert result["systems_added"] == 0
        assert result["modules_added"] == 0
        assert result["components_added"] == 0
        assert len(result["errors"]) == 0

    def test_sync_config_dry_run(
        self, config_updater: ConfigUpdater, temp_project_dir: Path
    ):
        """Test sync_config in dry-run mode."""
        # Create test system structure
        self.create_test_system_structure(
            temp_project_dir, "user_management", ["authentication", "profile"]
        )
        self.create_test_system_structure(
            temp_project_dir, "payment", ["billing", "invoicing"]
        )

        result = config_updater.sync_config(
            temp_project_dir, dry_run=True, verbose=True
        )

        # Should detect systems but not add them
        assert len(result["changes"]) > 0
        assert any("user_management" in change for change in result["changes"])
        assert any("payment" in change for change in result["changes"])

        # Config should not be modified in dry-run
        assert "user_management" not in config_updater.config.project.systems
        assert "payment" not in config_updater.config.project.systems

    def test_sync_config_add_systems(
        self, config_updater: ConfigUpdater, temp_project_dir: Path
    ):
        """Test sync_config actually adding systems."""
        # Create test system structure
        self.create_test_system_structure(
            temp_project_dir, "user_management", ["authentication"]
        )
        self.create_test_system_structure(temp_project_dir, "notification", ["email"])

        result = config_updater.sync_config(
            temp_project_dir, dry_run=False, verbose=True
        )

        # Should add systems
        assert result["systems_added"] == 2
        assert result["modules_added"] == 2  # authentication + email
        assert len(result["errors"]) == 0

        # Verify systems were added to config
        assert "user_management" in config_updater.config.project.systems
        assert "notification" in config_updater.config.project.systems

        # Verify modules were added
        user_system = config_updater.config.project.systems["user_management"]
        assert "authentication" in user_system.modules

        notification_system = config_updater.config.project.systems["notification"]
        assert "email" in notification_system.modules

    def test_sync_config_with_systems_filter(
        self, config_updater: ConfigUpdater, temp_project_dir: Path
    ):
        """Test sync_config with systems filter."""
        # Create multiple systems
        self.create_test_system_structure(
            temp_project_dir, "user_management", ["authentication"]
        )
        self.create_test_system_structure(temp_project_dir, "payment", ["billing"])
        self.create_test_system_structure(temp_project_dir, "notification", ["email"])

        # Sync only user_management and notification
        result = config_updater.sync_config(
            temp_project_dir,
            dry_run=False,
            systems_filter=["user_management", "notification"],
        )

        # Should only add filtered systems
        assert result["systems_added"] == 2
        assert "user_management" in config_updater.config.project.systems
        assert "notification" in config_updater.config.project.systems
        assert "payment" not in config_updater.config.project.systems

    def test_sync_config_existing_systems(
        self, config_updater: ConfigUpdater, temp_project_dir: Path
    ):
        """Test sync_config with existing systems in config."""
        # Add a system to config first
        config_updater.add_system("user_management", "Existing user management")

        # Create filesystem structure with same system + new system
        self.create_test_system_structure(
            temp_project_dir, "user_management", ["authentication"]
        )
        self.create_test_system_structure(temp_project_dir, "payment", ["billing"])

        result = config_updater.sync_config(temp_project_dir, dry_run=False)

        # Should only add new system (payment)
        assert result["systems_added"] == 1
        assert "payment" in config_updater.config.project.systems

        # Existing system should remain unchanged
        user_system = config_updater.config.project.systems["user_management"]
        assert user_system.description == "Existing user management"

    def test_sync_config_force_overwrite(
        self, config_updater: ConfigUpdater, temp_project_dir: Path
    ):
        """Test sync_config with force overwrite."""
        # Add a system to config first
        config_updater.add_system("user_management", "Original description")

        # Create filesystem structure
        self.create_test_system_structure(
            temp_project_dir, "user_management", ["authentication"]
        )

        result = config_updater.sync_config(temp_project_dir, dry_run=False, force=True)

        # Should update existing system
        assert (
            result["systems_added"] >= 0
        )  # May be 0 if system exists, modules/components added
        user_system = config_updater.config.project.systems["user_management"]
        # Description should be updated to auto-generated one
        assert "Auto-discovered" in user_system.description

    def test_sync_config_backup_creation(
        self, config_updater: ConfigUpdater, temp_project_dir: Path
    ):
        """Test that sync_config creates backups."""
        # Create test system structure
        self.create_test_system_structure(
            temp_project_dir, "user_management", ["authentication"]
        )

        # Sync config
        config_updater.sync_config(temp_project_dir, dry_run=False)

        # Check that backup was created
        backup_dir = temp_project_dir / "fca_config_backups"
        assert backup_dir.exists()
        backup_files = list(backup_dir.glob("fca_config.backup.*.yaml"))
        assert len(backup_files) >= 1

    def test_sync_config_invalid_project_root(self, config_updater: ConfigUpdater):
        """Test sync_config with invalid project root."""
        invalid_path = Path("/nonexistent/path")

        result = config_updater.sync_config(invalid_path, dry_run=True)

        # Should handle gracefully
        assert result["systems_added"] == 0
        assert result["modules_added"] == 0
        assert result["components_added"] == 0

    def test_sync_config_component_detection(
        self, config_updater: ConfigUpdater, temp_project_dir: Path
    ):
        """Test that sync_config detects and adds components."""
        # Create detailed system structure with components
        systems_dir = temp_project_dir / "systems"
        user_system_dir = systems_dir / "user_management" / "authentication"

        # Create domain entities
        entities_dir = user_system_dir / "domain" / "entities"
        entities_dir.mkdir(parents=True)
        (entities_dir / "user.py").write_text("# User entity")
        (entities_dir / "role.py").write_text("# Role entity")

        # Create application services
        services_dir = user_system_dir / "application" / "services"
        services_dir.mkdir(parents=True)
        (services_dir / "auth_service.py").write_text("# Auth service")

        result = config_updater.sync_config(
            temp_project_dir, dry_run=False, verbose=True
        )

        # Should detect and add components
        assert result["components_added"] > 0

        # Verify components were added to config
        user_system = config_updater.config.project.systems["user_management"]
        auth_module = user_system.modules["authentication"]
        components = auth_module.components.model_dump()

        # Check domain entities
        entity_names = [comp["name"] for comp in components["domain"]["entities"]]
        assert "user" in entity_names
        assert "role" in entity_names

        # Check application services
        service_names = [comp["name"] for comp in components["application"]["services"]]
        assert "auth" in service_names

    def test_sync_config_error_handling(
        self, config_updater: ConfigUpdater, temp_project_dir: Path
    ):
        """Test sync_config error handling."""
        # Create a system structure
        self.create_test_system_structure(
            temp_project_dir, "user_management", ["authentication"]
        )

        # Mock a failure in config saving
        original_save = config_updater._save_config_atomically

        def failing_save():
            raise Exception("Simulated save failure")

        config_updater._save_config_atomically = failing_save

        result = config_updater.sync_config(temp_project_dir, dry_run=False)

        # Should capture the error
        assert len(result["errors"]) > 0
        assert any("save" in error.lower() for error in result["errors"])

        # Restore original method
        config_updater._save_config_atomically = original_save

    def test_sync_config_verbose_output(
        self, config_updater: ConfigUpdater, temp_project_dir: Path
    ):
        """Test sync_config verbose output."""
        # Create test system structure
        self.create_test_system_structure(
            temp_project_dir, "user_management", ["authentication"]
        )

        # Capture console output
        mock_console = Mock()
        config_updater.console = mock_console

        result = config_updater.sync_config(
            temp_project_dir, dry_run=False, verbose=True
        )

        # Should have made console print calls for verbose output
        assert mock_console.print.called

        # Check that result contains detailed information
        assert len(result["changes"]) > 0
        assert result["systems_added"] > 0
