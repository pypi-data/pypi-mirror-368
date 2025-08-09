"""Tests for ComponentGenerator class."""

from unittest.mock import patch

import pytest

from fast_clean_architecture.config import Config
from fast_clean_architecture.exceptions import (
    FileConflictError,
    SecurityError,
    TemplateError,
    ValidationError,
)
from fast_clean_architecture.generators.generator_factory import (
    create_generator_factory,
)


class TestComponentGenerator:
    """Test cases for ComponentGenerator class."""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a temporary project structure for testing."""
        # Create basic project structure
        systems_dir = tmp_path / "systems"
        systems_dir.mkdir()

        # Create a test system
        test_system = systems_dir / "test_system"
        test_system.mkdir()

        # Create a test module
        test_module = test_system / "test_module"
        test_module.mkdir()

        # Create layer directories
        for layer in ["domain", "application", "infrastructure", "presentation"]:
            layer_dir = test_module / layer
            layer_dir.mkdir()

            # Create component type directories
            if layer == "domain":
                (layer_dir / "entities").mkdir()
                (layer_dir / "repositories").mkdir()
                (layer_dir / "value_objects").mkdir()
                (layer_dir / "enums").mkdir()
            elif layer == "application":
                (layer_dir / "services").mkdir()
                (layer_dir / "commands").mkdir()
                (layer_dir / "queries").mkdir()
            elif layer == "infrastructure":
                (layer_dir / "repositories").mkdir()
                (layer_dir / "external").mkdir()
                (layer_dir / "models").mkdir()
            elif layer == "presentation":
                (layer_dir / "api").mkdir()
                (layer_dir / "schemas").mkdir()

        return tmp_path

    @pytest.fixture
    def generator(self, temp_project):
        """Create a ComponentGenerator instance."""
        config = Config.create_default()
        factory = create_generator_factory(config=config)
        return factory.create_generator("component")

    def test_generate_entity_success(self, generator, temp_project):
        """Test successful entity generation."""
        result = generator.create_component(
            base_path=temp_project,
            system_name="test_system",
            module_name="test_module",
            layer="domain",
            component_type="entities",
            component_name="user",
        )

        expected_path = (
            temp_project
            / "systems"
            / "test_system"
            / "test_module"
            / "domain"
            / "entities"
            / "user.py"
        )

        assert result == expected_path
        assert expected_path.exists()

        content = expected_path.read_text()
        assert "class User" in content
        assert "@dataclass" in content
        assert "from dataclasses import dataclass" in content

    def test_generate_repository_success(self, generator, temp_project):
        """Test successful repository interface generation in domain layer."""
        result = generator.create_component(
            base_path=temp_project,
            system_name="test_system",
            module_name="test_module",
            layer="domain",
            component_type="interfaces",
            component_name="user",
        )

        expected_path = (
            temp_project
            / "systems"
            / "test_system"
            / "test_module"
            / "domain"
            / "interfaces"
            / "user.py"
        )

        assert result == expected_path
        assert expected_path.exists()

        content = expected_path.read_text()
        assert "class User(Protocol)" in content
        assert "@runtime_checkable" in content
        assert "from typing import" in content and "Protocol" in content

    def test_generate_service_success(self, generator, temp_project):
        """Test successful service generation."""
        result = generator.create_component(
            base_path=temp_project,
            system_name="test_system",
            module_name="test_module",
            layer="application",
            component_type="services",
            component_name="user",
        )

        expected_path = (
            temp_project
            / "systems"
            / "test_system"
            / "test_module"
            / "application"
            / "services"
            / "user_service.py"
        )

        assert result == expected_path
        assert expected_path.exists()

        content = expected_path.read_text()
        assert "class UserService" in content
        assert "def create" in content
        assert "def get" in content
        assert "def update" in content
        assert "def delete" in content

    def test_generate_component_invalid_name(self, generator, temp_project):
        """Test component generation with invalid name."""
        with pytest.raises(ValidationError, match="Invalid component name"):
            generator.create_component(
                base_path=temp_project,
                system_name="test_system",
                module_name="test_module",
                layer="domain",
                component_type="entities",
                component_name="123invalid",
            )

    def test_generate_component_invalid_system_name(self, generator, temp_project):
        """Test component generation with invalid system name."""
        with pytest.raises(ValidationError, match="Invalid"):
            generator.create_component(
                base_path=temp_project,
                system_name="123invalid",
                module_name="test_module",
                layer="domain",
                component_type="entities",
                component_name="user",
            )

    def test_generate_component_invalid_module_name(self, generator, temp_project):
        """Test component generation with invalid module name."""
        with pytest.raises(ValidationError, match="Invalid"):
            generator.create_component(
                base_path=temp_project,
                system_name="test_system",
                module_name="123invalid",
                layer="domain",
                component_type="entities",
                component_name="user",
            )

    def test_generate_component_invalid_type(self, generator, temp_project):
        """Test component generation with invalid component type."""
        with pytest.raises(
            ValidationError,
            match="Component type 'invalid_type' not valid for layer 'domain'",
        ):
            generator.create_component(
                base_path=temp_project,
                system_name="test_system",
                module_name="test_module",
                layer="domain",
                component_type="invalid_type",
                component_name="user",
            )

    def test_validate_template_variables_missing_variable(self, generator):
        """Test template validation with missing variables."""
        # Create a template with undefined variables
        template_content = "Hello {{ undefined_variable }}!"
        template_vars = {"defined_variable": "value"}

        with pytest.raises(TemplateError, match="Missing required template variables"):
            generator._validate_template_variables(template_content, template_vars)

    def test_validate_template_variables_success(self, generator):
        """Test successful template validation."""
        template_content = "Hello {{ defined_variable }}!"
        template_vars = {"defined_variable": "World"}

        # Should not raise any exception
        generator._validate_template_variables(template_content, template_vars)

    @patch("os.access")
    def test_validate_file_system_no_write_permission(
        self, mock_access, generator, temp_project
    ):
        """Test file system validation with no write permission."""
        mock_access.return_value = False

        file_path = temp_project / "test_file.py"

        with pytest.raises(
            (ValidationError, SecurityError),
            match="Security violation during validate file system|Failed to access directory",
        ):
            generator._validate_file_system(file_path)

    @patch("shutil.disk_usage")
    def test_validate_file_system_insufficient_disk_space(
        self, mock_disk_usage, generator, temp_project
    ):
        """Test file system validation with insufficient disk space."""
        # Mock disk usage to return less than 1MB free space
        mock_disk_usage.return_value = (1000000, 900000, 500000)  # total, used, free

        file_path = temp_project / "test_file.py"

        with pytest.raises(ValidationError, match="Insufficient disk space"):
            generator._validate_file_system(file_path)

    @patch("shutil.disk_usage")
    def test_validate_file_system_disk_usage_error(
        self, mock_disk_usage, generator, temp_project, caplog
    ):
        """Test file system validation when disk usage check fails."""
        mock_disk_usage.side_effect = OSError("Disk usage check failed")

        file_path = temp_project / "test_file.py"

        # Should not raise exception but log warning
        generator._validate_file_system(file_path)
        assert "Could not check disk space" in caplog.text

    def test_file_write_with_backup_and_rollback(self, generator, temp_project):
        """Test file write operation with backup and rollback on failure."""
        # Create an existing file
        existing_file = temp_project / "existing_file.py"
        original_content = "# Original content"
        existing_file.write_text(original_content)

        # Mock a write failure in the atomic write operation
        with patch("tempfile.mkstemp", side_effect=OSError("Write failed")):
            with pytest.raises(ValidationError, match="Failed to write file"):
                generator.create_component(
                    base_path=temp_project,
                    system_name="test_system",
                    module_name="test_module",
                    layer="domain",
                    component_type="entities",
                    component_name="user",
                )

    def test_dry_run_mode(self, generator, temp_project):
        """Test dry run mode doesn't create files."""
        result = generator.create_component(
            base_path=temp_project,
            system_name="test_system",
            module_name="test_module",
            layer="domain",
            component_type="entities",
            component_name="user",
            dry_run=True,
        )

        assert (
            result
            == temp_project
            / "systems"
            / "test_system"
            / "test_module"
            / "domain"
            / "entities"
            / "user.py"
        )
        assert not result.exists()

    def test_force_overwrite_existing_file(self, generator, temp_project):
        """Test force overwrite of existing file."""
        # Create existing file
        existing_path = (
            temp_project
            / "systems"
            / "test_system"
            / "test_module"
            / "domain"
            / "entities"
            / "user.py"
        )
        existing_path.parent.mkdir(parents=True, exist_ok=True)
        existing_path.write_text("# Existing content")

        result = generator.create_component(
            base_path=temp_project,
            system_name="test_system",
            module_name="test_module",
            layer="domain",
            component_type="entities",
            component_name="user",
            force=True,
        )

        assert result == existing_path
        assert existing_path.exists()

        content = existing_path.read_text()
        assert "class User" in content
        assert "# Existing content" not in content

    def test_refuse_overwrite_without_force(self, generator, temp_project):
        """Test refusal to overwrite existing file without force flag."""
        # Create existing file
        existing_path = (
            temp_project
            / "systems"
            / "test_system"
            / "test_module"
            / "domain"
            / "entities"
            / "user.py"
        )
        existing_path.parent.mkdir(parents=True, exist_ok=True)
        existing_path.write_text("# Existing content")

        with pytest.raises(FileConflictError, match="Component file already exists"):
            generator.create_component(
                base_path=temp_project,
                system_name="test_system",
                module_name="test_module",
                layer="domain",
                component_type="entities",
                component_name="user",
                force=False,
            )

    def test_template_variables_generation(self, generator):
        """Test that template variables are correctly generated."""
        from fast_clean_architecture.utils import get_template_variables

        template_vars = get_template_variables(
            system_name="user_management",
            module_name="authentication",
            component_name="user",
            component_type="entities",
        )

        # Check system name variations
        assert template_vars["system_name"] == "user_management"
        assert template_vars["SystemName"] == "UserManagement"
        assert template_vars["system_name_camel"] == "userManagement"

        # Check module name variations
        assert template_vars["module_name"] == "authentication"
        assert template_vars["ModuleName"] == "Authentication"
        assert template_vars["module_name_camel"] == "authentication"

        # Check component name variations
        assert template_vars["component_name"] == "user"
        assert template_vars["ComponentName"] == "User"
        assert template_vars["component_name_camel"] == "user"

        # Check metadata
        assert "generated_at" in template_vars
        assert "generator_version" in template_vars

        # Check import paths
        assert "entity_import" in template_vars
        assert "repository_import" in template_vars
        assert "service_import" in template_vars

    def test_all_component_types(self, generator, temp_project):
        """Test generation of all supported component types."""
        component_types = [
            ("entities", "domain"),
            ("value_objects", "domain"),
            ("enums", "domain"),
            ("services", "application"),
            ("commands", "application"),
            ("queries", "application"),
            ("repositories", "infrastructure"),
            ("external", "infrastructure"),
            ("models", "infrastructure"),
            ("controllers", "presentation"),
            ("schemas", "presentation"),
        ]

        for component_type, layer in component_types:
            result = generator.create_component(
                base_path=temp_project,
                system_name="test_system",
                module_name="test_module",
                layer=layer,
                component_type=component_type,
                component_name="test_component",
            )

            assert result is not None, f"Failed to generate {component_type} in {layer}"
            assert result.exists(), f"File not created for {component_type}"

    def test_enum_simple_template_default(self, generator, temp_project):
        """Test enum generation with simple template (default)."""
        result = generator.create_component(
            base_path=temp_project,
            system_name="test_system",
            module_name="test_module",
            layer="domain",
            component_type="enums",
            component_name="user_status",
        )

        expected_path = (
            temp_project
            / "systems"
            / "test_system"
            / "test_module"
            / "domain"
            / "enums"
            / "user_status.py"
        )

        assert result == expected_path
        assert expected_path.exists()

        content = expected_path.read_text()
        assert "class UserStatus(Enum):" in content
        assert "from enum import Enum" in content
        assert "def from_string(cls, value: str)" in content
        # Simple template should not have extensive methods
        assert "all_values" not in content
        assert "to_dict" not in content
        assert "__pydantic_serializer__" not in content

    def test_enum_simple_template_explicit(self, generator, temp_project):
        """Test enum generation with explicit simple template."""
        result = generator.create_component(
            base_path=temp_project,
            system_name="test_system",
            module_name="test_module",
            layer="domain",
            component_type="enums",
            component_name="user_role",
            template_variant="simple",
        )

        expected_path = (
            temp_project
            / "systems"
            / "test_system"
            / "test_module"
            / "domain"
            / "enums"
            / "user_role.py"
        )

        assert result == expected_path
        assert expected_path.exists()

        content = expected_path.read_text()
        assert "class UserRole(Enum):" in content
        assert "from enum import Enum" in content
        assert "def from_string(cls, value: str)" in content

    def test_enum_full_template(self, generator, temp_project):
        """Test enum generation with full template."""
        result = generator.create_component(
            base_path=temp_project,
            system_name="test_system",
            module_name="test_module",
            layer="domain",
            component_type="enums",
            component_name="order_status",
            template_variant="full",
        )

        expected_path = (
            temp_project
            / "systems"
            / "test_system"
            / "test_module"
            / "domain"
            / "enums"
            / "order_status.py"
        )

        assert result == expected_path
        assert expected_path.exists()

        content = expected_path.read_text()
        assert "class OrderStatus(Enum):" in content
        assert "from enum import Enum" in content
        assert "def from_string(cls, value: str)" in content
        assert "def all_values(cls)" in content
        assert "def all_names(cls)" in content
        assert "def to_dict(self)" in content
        assert "def is_valid(cls, value: Any) -> bool:" in content

    def test_enum_api_template(self, generator, temp_project):
        """Test enum generation with API template."""
        result = generator.create_component(
            base_path=temp_project,
            system_name="test_system",
            module_name="test_module",
            layer="domain",
            component_type="enums",
            component_name="api_status",
            template_variant="api",
        )

        expected_path = (
            temp_project
            / "systems"
            / "test_system"
            / "test_module"
            / "domain"
            / "enums"
            / "api_status.py"
        )

        assert result == expected_path
        assert expected_path.exists()

        content = expected_path.read_text()
        assert "class ApiStatus(Enum):" in content
        assert "from enum import Enum" in content
        assert "from typing import Any, Dict, List, Union" in content
        assert "def from_string(cls, value: str)" in content
        assert "def all_values(cls)" in content
        assert "def choices(cls)" in content
        assert "def to_dict(self)" in content
        assert "def is_valid(cls, value: Any)" in content
        assert "__modify_schema__" in content

    def test_enum_invalid_template_variant(self, generator, temp_project):
        """Test enum generation with invalid template variant."""
        # This should fall back to the base template
        result = generator.create_component(
            base_path=temp_project,
            system_name="test_system",
            module_name="test_module",
            layer="domain",
            component_type="enums",
            component_name="test_enum",
            template_variant="invalid",
        )

        expected_path = (
            temp_project
            / "systems"
            / "test_system"
            / "test_module"
            / "domain"
            / "enums"
            / "test_enum.py"
        )

        assert result == expected_path
        assert expected_path.exists()

        content = expected_path.read_text()
        assert "class TestEnum(Enum):" in content

    def test_template_variant_non_enum_component(self, generator, temp_project):
        """Test that template_variant parameter is ignored for non-enum components."""
        result = generator.create_component(
            base_path=temp_project,
            system_name="test_system",
            module_name="test_module",
            layer="domain",
            component_type="entities",
            component_name="user",
            template_variant="full",  # Should be ignored
        )

        expected_path = (
            temp_project
            / "systems"
            / "test_system"
            / "test_module"
            / "domain"
            / "entities"
            / "user.py"
        )

        assert result == expected_path
        assert expected_path.exists()

        content = expected_path.read_text()
        assert "class User" in content
        assert "@dataclass" in content
