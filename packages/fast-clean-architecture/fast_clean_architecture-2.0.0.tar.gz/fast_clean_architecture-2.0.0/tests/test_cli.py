"""Tests for CLI functionality."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from fast_clean_architecture import __version__
from fast_clean_architecture.cli import app
from fast_clean_architecture.config import Config


class TestCLI:
    """Test CLI commands."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()

    def test_version_command(self):
        """Test version command."""
        result = self.runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "Fast Clean Architecture" in result.stdout
        assert "Version:" in result.stdout

    def test_init_command_with_args(self, temp_dir: Path):
        """Test init command with arguments."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--version",
                    "1.0.0",
                    "--config",
                    str(config_file),
                ],
            )

        assert result.exit_code == 0
        assert "initialized successfully" in result.stdout
        assert config_file.exists()

        # Verify config content
        config = Config.load_from_file(config_file)
        assert config.project.name == "test_project"
        assert config.project.description == "Test project"
        assert config.project.version == "1.0.0"

    def test_init_command_interactive(self, temp_dir: Path):
        """Test init command with interactive input."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            with patch("fast_clean_architecture.cli.Prompt.ask") as mock_prompt:
                mock_prompt.side_effect = [
                    "interactive_project",
                    "Interactive description",
                ]

                result = self.runner.invoke(app, ["init", "--config", str(config_file)])

        assert result.exit_code == 0
        assert config_file.exists()

        # Verify config content
        config = Config.load_from_file(config_file)
        assert config.project.name == "interactive_project"
        assert config.project.description == "Interactive description"

    def test_init_command_force_overwrite(self, temp_dir: Path):
        """Test init command with force overwrite."""
        config_file = temp_dir / "test-config.yaml"

        # Create existing config
        existing_config = Config.create_default()
        existing_config.project.name = "existing_project"
        existing_config.save_to_file(config_file)

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(
                app,
                [
                    "init",
                    "new_project",
                    "--description",
                    "New project",
                    "--config",
                    str(config_file),
                    "--force",
                ],
            )

        assert result.exit_code == 0

        # Verify config was overwritten
        config = Config.load_from_file(config_file)
        assert config.project.name == "new_project"

    def test_create_system_context(self, temp_dir: Path):
        """Test create-system-context command."""
        config_file = temp_dir / "test-config.yaml"

        # Initialize project first
        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--version",
                    "1.0.0",
                    "--config",
                    str(config_file),
                ],
            )

            # Create system context
            result = self.runner.invoke(
                app,
                [
                    "create-system-context",
                    "user_management",
                    "--description",
                    "User management system",
                    "--config",
                    str(config_file),
                ],
            )

        assert result.exit_code == 0
        assert "created successfully" in result.stdout

        # Verify system directory was created
        system_dir = temp_dir / "systems" / "user_management"
        assert system_dir.exists()
        assert (system_dir / "__init__.py").exists()
        assert (system_dir / "main.py").exists()

        # Verify config was updated
        config = Config.load_from_file(config_file)
        assert "user_management" in config.project.systems
        assert (
            config.project.systems["user_management"].description
            == "User management system"
        )

    def test_create_module(self, temp_dir: Path):
        """Test create-module command."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project and system
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-system-context",
                    "user_management",
                    "--description",
                    "User management system",
                    "--config",
                    str(config_file),
                ],
            )

            # Create module
            result = self.runner.invoke(
                app,
                [
                    "create-module",
                    "user_management",
                    "authentication",
                    "--description",
                    "Authentication module",
                    "--config",
                    str(config_file),
                ],
            )

        assert result.exit_code == 0
        assert "created in system" in result.stdout

        # Verify module directory structure
        module_dir = temp_dir / "systems" / "user_management" / "authentication"
        assert module_dir.exists()
        assert (module_dir / "__init__.py").exists()

        # Check layer directories
        for layer in ["domain", "application", "infrastructure", "presentation"]:
            layer_dir = module_dir / layer
            assert layer_dir.exists()
            assert (layer_dir / "__init__.py").exists()

        # Verify config was updated
        config = Config.load_from_file(config_file)
        system = config.project.systems["user_management"]
        assert "authentication" in system.modules
        assert system.modules["authentication"].description == "Authentication module"

    def test_create_component(self, temp_dir: Path):
        """Test create-component command."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project, system, and module
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-system-context",
                    "user_management",
                    "--description",
                    "User management system",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-module",
                    "user_management",
                    "authentication",
                    "--description",
                    "Authentication module",
                    "--config",
                    str(config_file),
                ],
            )

            # Create component
            result = self.runner.invoke(
                app,
                [
                    "create-component",
                    "user_management/authentication/domain/entities",
                    "user",
                    "--config",
                    str(config_file),
                ],
            )

        assert result.exit_code == 0
        assert "Created" in result.stdout and "entities" in result.stdout

        # Verify component file was created
        component_file = (
            temp_dir
            / "systems"
            / "user_management"
            / "authentication"
            / "domain"
            / "entities"
            / "user.py"
        )
        assert component_file.exists()

        # Verify config was updated
        config = Config.load_from_file(config_file)
        module = config.project.systems["user_management"].modules["authentication"]
        entities = module.components.domain.entities
        assert len(entities) == 1
        assert entities[0].name == "user"

    def test_create_component_invalid_location(self, temp_dir: Path):
        """Test create-component with invalid location format."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(
                app,
                [
                    "create-component",
                    "invalid/location",  # Missing layer and component type
                    "user",
                    "--config",
                    str(config_file),
                ],
            )

        assert result.exit_code == 1
        assert "Location must be in format" in result.stdout

    def test_create_enum_component_default_template(self, temp_dir: Path):
        """Test create-component for enum with default (simple) template."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project, system, and module
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-system-context",
                    "user_management",
                    "--description",
                    "User management system",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-module",
                    "user_management",
                    "authentication",
                    "--description",
                    "Authentication module",
                    "--config",
                    str(config_file),
                ],
            )

            # Create enum component without template flag (should use default simple)
            result = self.runner.invoke(
                app,
                [
                    "create-component",
                    "user_management/authentication/domain/enums",
                    "UserStatus",
                    "--config",
                    str(config_file),
                ],
            )

        assert result.exit_code == 0
        assert "Created" in result.stdout and "enums" in result.stdout

        # Verify enum file was created
        enum_file = (
            temp_dir
            / "systems"
            / "user_management"
            / "authentication"
            / "domain"
            / "enums"
            / "user_status.py"
        )
        assert enum_file.exists()

        # Verify it uses simple template (should not have advanced methods)
        content = enum_file.read_text()
        assert "class UserStatus(Enum):" in content
        assert "from_string" in content
        assert "all_values" not in content  # Not in simple template
        assert "__modify_schema__" not in content  # Not in simple template

    def test_create_enum_component_simple_template(self, temp_dir: Path):
        """Test create-component for enum with explicit simple template."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project, system, and module
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-system-context",
                    "user_management",
                    "--description",
                    "User management system",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-module",
                    "user_management",
                    "authentication",
                    "--description",
                    "Authentication module",
                    "--config",
                    str(config_file),
                ],
            )

            # Create enum component with explicit simple template
            result = self.runner.invoke(
                app,
                [
                    "create-component",
                    "user_management/authentication/domain/enums",
                    "UserRole",
                    "--template",
                    "simple",
                    "--config",
                    str(config_file),
                ],
            )

        assert result.exit_code == 0
        assert "Created" in result.stdout and "enums" in result.stdout

        # Verify enum file was created
        enum_file = (
            temp_dir
            / "systems"
            / "user_management"
            / "authentication"
            / "domain"
            / "enums"
            / "user_role.py"
        )
        assert enum_file.exists()

        # Verify it uses simple template
        content = enum_file.read_text()
        assert "class UserRole(Enum):" in content
        assert "from_string" in content
        assert "all_values" not in content  # Not in simple template

    def test_create_enum_component_full_template(self, temp_dir: Path):
        """Test create-component for enum with full template."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project, system, and module
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-system-context",
                    "user_management",
                    "--description",
                    "User management system",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-module",
                    "user_management",
                    "authentication",
                    "--description",
                    "Authentication module",
                    "--config",
                    str(config_file),
                ],
            )

            # Create enum component with full template
            result = self.runner.invoke(
                app,
                [
                    "create-component",
                    "user_management/authentication/domain/enums",
                    "Priority",
                    "--template",
                    "full",
                    "--config",
                    str(config_file),
                ],
            )

        assert result.exit_code == 0
        assert "Created" in result.stdout and "enums" in result.stdout

        # Verify enum file was created
        enum_file = (
            temp_dir
            / "systems"
            / "user_management"
            / "authentication"
            / "domain"
            / "enums"
            / "priority.py"
        )
        assert enum_file.exists()

        # Verify it uses full template (has advanced methods)
        content = enum_file.read_text()
        assert "class Priority(Enum):" in content
        assert "from_string" in content
        assert "all_values" in content  # Full template feature
        assert "all_names" in content  # Full template feature
        assert "to_dict" in content  # Full template feature
        assert "is_valid" in content  # Full template feature

    def test_create_enum_component_api_template(self, temp_dir: Path):
        """Test create-component for enum with API template."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project, system, and module
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-system-context",
                    "user_management",
                    "--description",
                    "User management system",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-module",
                    "user_management",
                    "authentication",
                    "--description",
                    "Authentication module",
                    "--config",
                    str(config_file),
                ],
            )

            # Create enum component with API template
            result = self.runner.invoke(
                app,
                [
                    "create-component",
                    "user_management/authentication/domain/enums",
                    "ApiStatus",
                    "--template",
                    "api",
                    "--config",
                    str(config_file),
                ],
            )

        assert result.exit_code == 0
        assert "Created" in result.stdout and "enums" in result.stdout

        # Verify enum file was created
        enum_file = (
            temp_dir
            / "systems"
            / "user_management"
            / "authentication"
            / "domain"
            / "enums"
            / "api_status.py"
        )
        assert enum_file.exists()

        # Verify it uses API template (has API-specific features)
        content = enum_file.read_text()
        assert "class ApiStatus(Enum):" in content
        assert "from_string" in content
        assert "def choices(cls)" in content  # API template feature
        assert "__modify_schema__" in content  # API template feature
        assert "to_dict" in content  # API template feature
        assert "from typing import Any, Dict, List, Union" in content  # API imports

    def test_create_enum_component_invalid_template(self, temp_dir: Path):
        """Test create-component for enum with invalid template variant."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project, system, and module
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-system-context",
                    "user_management",
                    "--description",
                    "User management system",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-module",
                    "user_management",
                    "authentication",
                    "--description",
                    "Authentication module",
                    "--config",
                    str(config_file),
                ],
            )

            # Create enum component with invalid template
            result = self.runner.invoke(
                app,
                [
                    "create-component",
                    "user_management/authentication/domain/enums",
                    "TestEnum",
                    "--template",
                    "invalid",
                    "--config",
                    str(config_file),
                ],
            )

        assert result.exit_code == 1
        assert "Invalid template variant" in result.stdout

    def test_create_component_template_with_non_enum(self, temp_dir: Path):
        """Test create-component with template flag for non-enum component type."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project, system, and module
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-system-context",
                    "user_management",
                    "--description",
                    "User management system",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-module",
                    "user_management",
                    "authentication",
                    "--description",
                    "Authentication module",
                    "--config",
                    str(config_file),
                ],
            )

            # Try to use template flag with entity (non-enum)
            result = self.runner.invoke(
                app,
                [
                    "create-component",
                    "user_management/authentication/domain/entities",
                    "User",
                    "--template",
                    "simple",
                    "--config",
                    str(config_file),
                ],
            )

        assert result.exit_code == 1
        assert (
            "Template variants are only supported for enum components" in result.stdout
        )

    def test_dry_run_mode(self, temp_dir: Path):
        """Test dry run mode."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )

            # Create system in dry run mode
            result = self.runner.invoke(
                app,
                [
                    "create-system-context",
                    "user_management",
                    "--config",
                    str(config_file),
                    "--dry-run",
                ],
            )

        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout

        # Verify nothing was actually created
        system_dir = temp_dir / "systems" / "user_management"
        assert not system_dir.exists()

        # Verify config was not updated
        config = Config.load_from_file(config_file)
        assert "user_management" not in config.project.systems

    def test_status_command(self, temp_dir: Path):
        """Test status command."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project with system and module
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-system-context",
                    "user_management",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-module",
                    "user_management",
                    "authentication",
                    "--config",
                    str(config_file),
                ],
            )

            # Check status
            result = self.runner.invoke(app, ["status", "--config", str(config_file)])

        assert result.exit_code == 0
        assert "Project Information" in result.stdout
        assert "test_project" in result.stdout
        # The status command should show project information at minimum
        # Systems may or may not be displayed depending on the state

    def test_status_no_config(self, temp_dir: Path):
        """Test status command with no config file."""
        config_file = temp_dir / "nonexistent-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(app, ["status", "--config", str(config_file)])

        assert result.exit_code == 0
        assert "No configuration file found" in result.stdout

    def test_config_show_command(self, temp_dir: Path):
        """Test config show command."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )

            # Show config
            result = self.runner.invoke(
                app, ["config", "show", "--config", str(config_file)]
            )

        assert result.exit_code == 0
        assert "Configuration:" in result.stdout
        assert "test_project" in result.stdout

    def test_config_validate_command(self, temp_dir: Path):
        """Test config validate command."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )

            # Validate config
            result = self.runner.invoke(
                app, ["config", "validate", "--config", str(config_file)]
            )

        assert result.exit_code == 0
        assert "Configuration is valid" in result.stdout

    def test_config_validate_invalid(self, temp_dir: Path):
        """Test config validate with invalid config."""
        config_file = temp_dir / "invalid-config.yaml"

        # Create invalid YAML
        config_file.write_text("invalid: yaml: content: [")

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(
                app, ["config", "validate", "--config", str(config_file)]
            )

        assert result.exit_code == 0
        assert "Configuration is invalid" in result.stdout

    def test_batch_create_command(self, temp_dir: Path):
        """Test batch-create command."""
        config_file = temp_dir / "test-config.yaml"
        spec_file = temp_dir / "components.yaml"

        # Create specification file
        spec_content = """
systems:
  - name: user_management
    modules:
      - name: authentication
        components:
          domain:
            entities: ["user"]
            interfaces: ["user"]
          application:
            services: ["auth_service"]
          infrastructure:
            database:
              repositories: ["user"]
"""
        spec_file.write_text(spec_content)

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Initialize project, system, and module
            self.runner.invoke(
                app,
                [
                    "init",
                    "test_project",
                    "--description",
                    "Test project",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-system-context",
                    "user_management",
                    "--config",
                    str(config_file),
                ],
            )
            self.runner.invoke(
                app,
                [
                    "create-module",
                    "user_management",
                    "authentication",
                    "--config",
                    str(config_file),
                ],
            )

            # Run batch create
            result = self.runner.invoke(
                app, ["batch-create", str(spec_file), "--config", str(config_file)]
            )

        assert result.exit_code == 0
        assert "Batch creation completed" in result.stdout or "Created" in result.stdout

        # Verify components were created
        base_path = temp_dir / "systems" / "user_management" / "authentication"
        assert (base_path / "domain" / "entities" / "user.py").exists()
        assert (base_path / "domain" / "interfaces" / "user.py").exists()
        assert (
            base_path / "application" / "services" / "auth_service_service.py"
        ).exists()
        assert (
            base_path
            / "infrastructure"
            / "database"
            / "repositories"
            / "user_repository.py"
        ).exists()

    def test_error_handling(self, temp_dir: Path):
        """Test error handling in CLI."""
        config_file = temp_dir / "test-config.yaml"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            # Try to create module without system
            result = self.runner.invoke(
                app,
                [
                    "create-module",
                    "nonexistent_system",
                    "authentication",
                    "--config",
                    str(config_file),
                ],
            )

        assert result.exit_code == 1
        assert "Error:" in result.stdout

    def test_create_scalable_baseline_poetry(self, temp_dir: Path):
        """Test create-scalable-baseline command with Poetry dependency manager."""
        project_name = "test_poetry_project"
        project_path = temp_dir / project_name

        # Mock subprocess.run for poetry lock command
        mock_subprocess = MagicMock()
        mock_subprocess.return_value.returncode = 0

        with (
            patch(
                "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
            ),
            patch("subprocess.run", mock_subprocess),
            patch("shutil.which", return_value="poetry"),
        ):
            result = self.runner.invoke(
                app,
                [
                    "create-scalable-baseline",
                    project_name,
                    "--deps",
                    "poetry",
                    "--force",
                ],
            )

        assert result.exit_code == 0
        assert "Complete FastAPI project structure created" in result.stdout
        assert "Poetry lock completed successfully" in result.stdout
        assert project_path.exists()

        # Verify poetry lock was called
        mock_subprocess.assert_called_once_with(
            ["poetry", "lock"],
            cwd=project_path,
            capture_output=True,
            text=True,
            check=True,
        )

        # Check Poetry-specific files
        assert (project_path / "pyproject.toml").exists()
        assert not (project_path / "requirements.txt").exists()
        assert not (project_path / "requirements-dev.txt").exists()

        # Check README content for Poetry
        readme_path = project_path / "README.md"
        assert readme_path.exists()
        readme_content = readme_path.read_text()
        assert "poetry install" in readme_content
        assert "poetry shell" in readme_content
        assert "poetry run" in readme_content

    def test_create_scalable_baseline_pip(self, temp_dir: Path):
        """Test create-scalable-baseline command with Pip dependency manager."""
        project_name = "test_pip_project"
        project_path = temp_dir / project_name

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(
                app,
                ["create-scalable-baseline", project_name, "--deps", "pip", "--force"],
            )

        assert result.exit_code == 0
        assert "Complete FastAPI project structure created" in result.stdout
        assert project_path.exists()

        # Check Pip-specific files
        assert (project_path / "requirements.txt").exists()
        assert (project_path / "requirements-dev.txt").exists()
        assert not (project_path / "pyproject.toml").exists()

        # Check README content for Pip
        readme_path = project_path / "README.md"
        assert readme_path.exists()
        readme_content = readme_path.read_text()
        assert "pip install -r requirements.txt" in readme_content
        assert "python -m venv" in readme_content
        assert "source venv/bin/activate" in readme_content

    def test_create_scalable_baseline_default_poetry(self, temp_dir: Path):
        """Test create-scalable-baseline command defaults to Poetry."""
        project_name = "test_default_project"
        project_path = temp_dir / project_name

        # Mock subprocess.run for poetry lock command
        mock_subprocess = MagicMock()
        mock_subprocess.return_value.returncode = 0

        with (
            patch(
                "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
            ),
            patch("subprocess.run", mock_subprocess),
            patch("shutil.which", return_value="poetry"),
        ):
            result = self.runner.invoke(
                app,
                ["create-scalable-baseline", project_name, "--force"],
            )

        assert result.exit_code == 0
        assert "Poetry lock completed successfully" in result.stdout
        assert project_path.exists()

        # Verify poetry lock was called
        mock_subprocess.assert_called_once_with(
            ["poetry", "lock"],
            cwd=project_path,
            capture_output=True,
            text=True,
            check=True,
        )

        # Should default to Poetry
        assert (project_path / "pyproject.toml").exists()
        assert not (project_path / "requirements.txt").exists()

    def test_create_scalable_baseline_invalid_deps(self, temp_dir: Path):
        """Test create-scalable-baseline command with invalid dependency manager."""
        project_name = "test_invalid_project"

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(
                app,
                [
                    "create-scalable-baseline",
                    project_name,
                    "--deps",
                    "invalid",
                    "--force",
                ],
            )

        assert result.exit_code != 0

    def test_help_guide_command(self):
        """Test main help command (help-guide content merged into main help)."""
        result = self.runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        # Check for key sections in help guide output
        assert "Fast Clean Architecture" in result.stdout
        assert "Quick Start" in result.stdout
        assert "Commands" in result.stdout
        assert "Workflow" in result.stdout
        assert "Examples" in result.stdout
        assert "Pro Tips" in result.stdout

    def test_update_package_command_in_fca_directory(self, temp_dir: Path):
        """Test update-package command when run in FCA directory (should fail)."""
        # Create FCA indicators in temp directory to simulate FCA package directory
        fca_dir = temp_dir / "fast_clean_architecture"
        fca_dir.mkdir()
        (fca_dir / "__init__.py").touch()  # This is the key indicator
        (temp_dir / "poetry.lock").touch()

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(app, ["update-package"])

            assert (
                result.exit_code == 0
            )  # CLI doesn't exit with error code, just prints error
            assert "fast-clean-architecture package directory" in result.stdout

    def test_update_package_command_dry_run(self, temp_dir: Path):
        """Test update-package command with dry run."""
        # Create pyproject.toml to simulate a Poetry project
        (temp_dir / "pyproject.toml").touch()

        with (
            patch(
                "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
            ),
            patch("subprocess.run") as mock_run,
        ):

            # Mock successful poetry show command with correct format
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = f"name         : fast-clean-architecture\nversion      : {__version__}\nsummary      : Fast Clean Architecture scaffolding tool"
            mock_run.return_value = mock_result

            result = self.runner.invoke(app, ["update-package", "--dry-run"])

            assert result.exit_code == 0
            assert "DRY RUN" in result.stdout or "Dry run" in result.stdout
            assert "Would update" in result.stdout or "Would" in result.stdout

    def test_update_package_command_with_version(self, temp_dir: Path):
        """Test update-package command with specific version."""
        # Create pyproject.toml to simulate a Poetry project
        (temp_dir / "pyproject.toml").touch()

        with (
            patch(
                "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
            ),
            patch("subprocess.run") as mock_run,
        ):

            # Mock successful poetry show command with correct format
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = f"name         : fast-clean-architecture\nversion      : {__version__}\nsummary      : Fast Clean Architecture scaffolding tool"
            mock_run.return_value = mock_result

            result = self.runner.invoke(app, ["update-package", "1.3.0", "--dry-run"])

            assert result.exit_code == 0
            assert "1.3.0" in result.stdout

    def test_update_package_command_test_pypi(self, temp_dir: Path):
        """Test update-package command with TestPyPI option."""
        # Create pyproject.toml to simulate a Poetry project
        (temp_dir / "pyproject.toml").touch()

        with (
            patch(
                "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
            ),
            patch("subprocess.run") as mock_run,
        ):

            # Mock successful poetry show command with correct format
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = f"name         : fast-clean-architecture\nversion      : {__version__}\nsummary      : Fast Clean Architecture scaffolding tool"
            mock_run.return_value = mock_result

            result = self.runner.invoke(
                app, ["update-package", "--test-pypi", "--dry-run"]
            )

            assert result.exit_code == 0
            assert "TestPyPI" in result.stdout

    def test_update_package_command_no_poetry(self, temp_dir: Path):
        """Test update-package command when Poetry is not available."""
        # Create pyproject.toml to simulate a Poetry project
        (temp_dir / "pyproject.toml").touch()

        with (
            patch(
                "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
            ),
            patch("subprocess.run") as mock_run,
        ):

            # Mock Poetry not found
            mock_run.side_effect = FileNotFoundError("Poetry not found")

            result = self.runner.invoke(app, ["update-package"])

            assert (
                result.exit_code == 0
            )  # CLI doesn't exit with error code, just prints error
            assert "Poetry not found" in result.stdout

    def test_update_package_command_package_not_found(self, temp_dir: Path):
        """Test update-package command when package is not found in project."""
        # Create pyproject.toml to simulate a Poetry project
        (temp_dir / "pyproject.toml").touch()

        with (
            patch(
                "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
            ),
            patch("subprocess.run") as mock_run,
        ):

            # Mock package not found in project
            from subprocess import CalledProcessError

            mock_run.side_effect = CalledProcessError(
                1, "poetry show fast-clean-architecture"
            )

            result = self.runner.invoke(app, ["update-package"])

            assert (
                result.exit_code == 0
            )  # CLI doesn't exit with error code, just prints error
            assert "not found in this project" in result.stdout

    def test_sync_config_command_basic(self, temp_dir: Path):
        """Test sync-config command basic functionality."""
        # Create a basic FCA project structure
        config_path = temp_dir / "fca_config.yaml"
        systems_dir = temp_dir / "systems"
        systems_dir.mkdir()

        # Create test system
        test_system = systems_dir / "test_system"
        test_system.mkdir()
        (test_system / "__init__.py").touch()

        # Create initial config
        config_content = """
project:
  name: "test_project"
  version: "1.0.0"
  systems: {}
components:
  entities: []
  repositories: []
  value_objects: []
  services: []
  commands: []
  queries: []
  models: []
  external: []
  api: []
  schemas: []
"""
        config_path.write_text(config_content)

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(app, ["sync-config"])

            assert result.exit_code == 0
            assert "🔍 Scanning project structure" in result.stdout
            assert "test_system" in result.stdout

    def test_sync_config_command_dry_run(self, temp_dir: Path):
        """Test sync-config command with dry run."""
        # Create a basic FCA project structure
        config_path = temp_dir / "fca_config.yaml"
        systems_dir = temp_dir / "systems"
        systems_dir.mkdir()

        # Create test system
        test_system = systems_dir / "test_system"
        test_system.mkdir()
        (test_system / "__init__.py").touch()

        # Create initial config
        config_content = """
project:
  name: "test_project"
  version: "1.0.0"
  systems: {}
components:
  entities: []
  repositories: []
  value_objects: []
  services: []
  commands: []
  queries: []
  models: []
  external: []
  api: []
  schemas: []
"""
        config_path.write_text(config_content)

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(app, ["sync-config", "--dry-run"])

            assert result.exit_code == 0
            assert "📋 Planned Changes" in result.stdout
            assert "test_system" in result.stdout

    def test_sync_config_command_with_systems_filter(self, temp_dir: Path):
        """Test sync-config command with systems filter."""
        # Create a basic FCA project structure
        config_path = temp_dir / "fca_config.yaml"
        systems_dir = temp_dir / "systems"
        systems_dir.mkdir()

        # Create multiple test systems
        for system_name in ["system1", "system2", "system3"]:
            test_system = systems_dir / system_name
            test_system.mkdir()
            (test_system / "__init__.py").touch()

        # Create initial config
        config_content = """
project:
  name: "test_project"
  version: "1.0.0"
  systems: {}
components:
  entities: []
  repositories: []
  value_objects: []
  services: []
  commands: []
  queries: []
  models: []
  external: []
  api: []
  schemas: []
"""
        config_path.write_text(config_content)

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(
                app, ["sync-config", "--systems", "system1,system2"]
            )

            assert result.exit_code == 0
            assert "system1" in result.stdout
            assert "system2" in result.stdout
            # system3 should not be mentioned since it's filtered out

    def test_sync_config_command_verbose(self, temp_dir: Path):
        """Test sync-config command with verbose output."""
        # Create a basic FCA project structure
        config_path = temp_dir / "fca_config.yaml"
        systems_dir = temp_dir / "systems"
        systems_dir.mkdir()

        # Create test system
        test_system = systems_dir / "test_system"
        test_system.mkdir()
        (test_system / "__init__.py").touch()

        # Create initial config
        config_content = """
project:
  name: "test_project"
  version: "1.0.0"
  systems: {}
components:
  entities: []
  repositories: []
  value_objects: []
  services: []
  commands: []
  queries: []
  models: []
  external: []
  api: []
  schemas: []
"""
        config_path.write_text(config_content)

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(app, ["sync-config", "--verbose"])

            assert result.exit_code == 0
            assert "🔍 Scanning project structure" in result.stdout
            assert "test_system" in result.stdout

    def test_sync_config_command_force_overwrite(self, temp_dir: Path):
        """Test sync-config command with force overwrite."""
        # Create a basic FCA project structure
        config_path = temp_dir / "fca_config.yaml"
        systems_dir = temp_dir / "systems"
        systems_dir.mkdir()

        # Create test system
        test_system = systems_dir / "test_system"
        test_system.mkdir()
        (test_system / "__init__.py").touch()

        # Create initial config with existing system
        config_content = """
project:
  name: "test_project"
  version: "1.0.0"
  systems:
    test_system:
      description: "Test system"
      created_at: "2024-01-01T00:00:00"
      updated_at: "2024-01-01T00:00:00"
      modules: {}
components:
  entities: []
  repositories: []
  value_objects: []
  services: []
  commands: []
  queries: []
  models: []
  external: []
  api: []
  schemas: []
"""
        config_path.write_text(config_content)

        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(app, ["sync-config", "--force"])

            assert result.exit_code == 0
            assert "📊 Sync Results" in result.stdout

    def test_sync_config_command_no_config_file(self, temp_dir: Path):
        """Test sync-config command when no config file exists."""
        with patch(
            "fast_clean_architecture.cli.get_project_root", return_value=temp_dir
        ):
            result = self.runner.invoke(app, ["sync-config"])

            assert result.exit_code != 0
            assert "Configuration file not found" in result.stdout

    def test_sync_config_command_invalid_project_root(self):
        """Test sync-config command with invalid project root."""
        with patch("fast_clean_architecture.cli.get_project_root", return_value=None):
            result = self.runner.invoke(app, ["sync-config"])

            assert result.exit_code != 0
            assert "Unexpected error" in result.stdout
