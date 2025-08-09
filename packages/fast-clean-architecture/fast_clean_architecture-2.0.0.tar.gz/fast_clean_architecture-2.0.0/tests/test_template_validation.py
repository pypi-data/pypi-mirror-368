"""Tests for template validation and error handling."""

from unittest.mock import patch

import pytest
from jinja2 import TemplateSyntaxError

from fast_clean_architecture.config import Config
from fast_clean_architecture.exceptions import TemplateError
from fast_clean_architecture.generators.generator_factory import (
    create_generator_factory,
)
from fast_clean_architecture.utils import get_template_variables


class TestTemplateValidation:
    """Test cases for template validation functionality."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create a ComponentGenerator instance."""
        config = Config.create_default()
        factory = create_generator_factory(config)
        return factory.create_generator("component")

    def test_validate_template_variables_success(self, generator):
        """Test successful template validation with all required variables."""
        template_content = """
        Hello {{ component_name }}!
        System: {{ system_name }}
        Module: {{ module_name }}
        """

        template_vars = {
            "component_name": "user",
            "system_name": "auth",
            "module_name": "users",
        }

        # Should not raise any exception
        generator._validate_template_variables(template_content, template_vars)

    def test_validate_template_variables_missing_single_variable(self, generator):
        """Test template validation with one missing variable."""
        template_content = "Hello {{ component_name }}! Missing: {{ undefined_var }}"
        template_vars = {"component_name": "user"}

        with pytest.raises(TemplateError) as exc_info:
            generator._validate_template_variables(template_content, template_vars)

        assert "Missing required template variables" in str(exc_info.value)
        assert "undefined_var" in str(exc_info.value)

    def test_validate_template_variables_missing_multiple_variables(self, generator):
        """Test template validation with multiple missing variables."""
        template_content = """
        Component: {{ component_name }}
        Missing1: {{ var1 }}
        Missing2: {{ var2 }}
        System: {{ system_name }}
        Missing3: {{ var3 }}
        """

        template_vars = {"component_name": "user", "system_name": "auth"}

        with pytest.raises(TemplateError) as exc_info:
            generator._validate_template_variables(template_content, template_vars)

        error_msg = str(exc_info.value)
        assert "Missing required template variables" in error_msg
        assert "var1" in error_msg
        assert "var2" in error_msg
        assert "var3" in error_msg

    def test_validate_template_variables_with_filters(self, generator):
        """Test template validation with Jinja2 filters."""
        template_content = """
        Upper: {{ component_name | upper }}
        Title: {{ system_name | title }}
        Default: {{ missing_var | default('fallback') }}
        """

        template_vars = {"component_name": "user", "system_name": "auth"}

        # Should not raise exception because missing_var has a default filter
        generator._validate_template_variables(template_content, template_vars)

    def test_validate_template_variables_with_conditionals(self, generator):
        """Test template validation with conditional statements."""
        template_content = """
        {% if component_name %}
        Component: {{ component_name }}
        {% endif %}
        {% if optional_var is defined %}
        Optional: {{ optional_var }}
        {% endif %}
        """

        template_vars = {"component_name": "user"}

        # Should not raise exception because optional_var is in a conditional
        generator._validate_template_variables(template_content, template_vars)

    def test_validate_template_variables_with_loops(self, generator):
        """Test template validation with loop constructs."""
        template_content = """
        {% for item in items %}
        Item: {{ item.name }}
        {% endfor %}
        Component: {{ component_name }}
        """

        template_vars = {
            "items": [{"name": "test1"}, {"name": "test2"}],
            "component_name": "user",
        }

        generator._validate_template_variables(template_content, template_vars)

    def test_validate_template_variables_syntax_error(self, generator):
        """Test template validation with syntax errors."""
        template_content = "Hello {{ component_name !"
        template_vars = {"component_name": "user"}

        with pytest.raises(TemplateSyntaxError):
            generator._validate_template_variables(template_content, template_vars)

    def test_validate_template_variables_empty_template(self, generator):
        """Test template validation with empty template."""
        template_content = ""
        template_vars = {"component_name": "user"}

        # Should not raise any exception
        generator._validate_template_variables(template_content, template_vars)

    def test_validate_template_variables_no_variables(self, generator):
        """Test template validation with template containing no variables."""
        template_content = "This is a static template with no variables."
        template_vars = {"component_name": "user"}

        # Should not raise any exception
        generator._validate_template_variables(template_content, template_vars)

    def test_get_template_variables_completeness(self):
        """Test that get_template_variables provides all necessary variables."""
        template_vars = get_template_variables(
            system_name="user_management",
            module_name="authentication",
            component_name="user",
            component_type="entities",
        )

        # Check all required variable categories are present
        required_vars = [
            # System variations
            "system_name",
            "SystemName",
            "system_name_camel",
            # Module variations
            "module_name",
            "ModuleName",
            "module_name_camel",
            # Component variations
            "component_name",
            "ComponentName",
            "component_name_camel",
            # Entity variations
            "entity_name",
            "EntityName",
            "entity_name_camel",
            # Repository variations
            "repository_name",
            "RepositoryName",
            "repository_name_camel",
            # Service variations
            "service_name",
            "ServiceName",
            "service_name_camel",
            # File naming
            "entity_file",
            "repository_file",
            "service_file",
            # Import paths
            "entity_import",
            "repository_import",
            "service_import",
            # Metadata
            "generated_at",
            "generator_version",
            # Additional naming
            "table_name",
            "collection_name",
            "endpoint_prefix",
            # Type hints
            "entity_type",
            "repository_type",
            "service_type",
        ]

        for var in required_vars:
            assert var in template_vars, f"Missing required template variable: {var}"
            assert template_vars[var] is not None, f"Template variable {var} is None"

    def test_template_variables_naming_consistency(self):
        """Test that template variables follow consistent naming patterns."""
        template_vars = get_template_variables(
            system_name="user_management",
            module_name="authentication_service",
            component_name="user_profile",
            component_type="entities",
        )

        # Test snake_case to PascalCase conversion
        assert template_vars["SystemName"] == "UserManagement"
        assert template_vars["ModuleName"] == "AuthenticationService"
        assert template_vars["ComponentName"] == "UserProfile"

        # Test snake_case to camelCase conversion
        assert template_vars["system_name_camel"] == "userManagement"
        assert template_vars["module_name_camel"] == "authenticationService"
        assert template_vars["component_name_camel"] == "userProfile"

        # Test entity naming
        assert template_vars["EntityName"] == "UserProfile"
        assert template_vars["entity_name"] == "user_profile"

        # Test repository naming
        assert template_vars["RepositoryName"] == "UserProfile"
        assert template_vars["repository_name"] == "user_profile"

    def test_template_variables_file_paths(self):
        """Test that template variables generate correct file paths."""
        template_vars = get_template_variables(
            system_name="user_management",
            module_name="authentication",
            component_name="user",
            component_type="entities",
        )

        # Test file naming patterns
        assert template_vars["entity_file"] == "user.py"
        assert template_vars["repository_file"] == "user_repository.py"
        assert template_vars["service_file"] == "user_service.py"

        # Test import paths
        assert "domain.entities" in template_vars["entity_import"]
        assert "domain.interfaces" in template_vars["repository_import"]
        assert "application.services" in template_vars["service_import"]

    def test_template_variables_metadata(self):
        """Test that template variables include proper metadata."""
        template_vars = get_template_variables(
            system_name="test_system",
            module_name="test_module",
            component_name="test_component",
            component_type="entities",
        )

        # Test metadata presence and format
        assert "generated_at" in template_vars
        assert "generator_version" in template_vars

        # Test timestamp format (should be ISO 8601)
        generated_at = template_vars["generated_at"]
        assert "T" in generated_at
        assert generated_at.endswith("Z")

        # Test version format
        version = template_vars["generator_version"]
        assert isinstance(version, str)
        assert len(version) > 0

    def test_template_variables_database_naming(self):
        """Test database-related naming conventions."""
        template_vars = get_template_variables(
            system_name="user_management",
            module_name="authentication",
            component_name="user_profile",
            component_type="entities",
        )

        # Test table naming (should be snake_case)
        assert template_vars["table_name"] == "user_profiles"

        # Test collection naming (for NoSQL databases)
        assert template_vars["collection_name"] == "user_profiles"

        # Test endpoint prefix
        assert template_vars["endpoint_prefix"] == "/user-profiles"

    def test_template_variables_type_hints(self):
        """Test type hint generation for templates."""
        template_vars = get_template_variables(
            system_name="user_management",
            module_name="authentication",
            component_name="user",
            component_type="entities",
        )

        # Test type hint patterns
        assert template_vars["entity_type"] == "User"
        assert template_vars["repository_type"] == "UserRepository"
        assert template_vars["service_type"] == "UserService"

    @patch(
        "fast_clean_architecture.generators.component_generator.ComponentGenerator._validate_template_variables"
    )
    def test_template_validation_integration(self, mock_validate, generator, tmp_path):
        """Test that template validation is called during component generation."""
        # Setup test environment
        systems_dir = (
            tmp_path / "systems" / "test_system" / "test_module" / "domain" / "entities"
        )
        systems_dir.mkdir(parents=True)

        # Generate component
        generator.create_component(
            base_path=tmp_path,
            system_name="test_system",
            module_name="test_module",
            layer="domain",
            component_type="entities",
            component_name="user",
        )

        # Verify validation was called
        mock_validate.assert_called_once()

    def test_template_validation_with_real_templates(self, generator, tmp_path):
        """Test template validation with actual template files."""
        # Setup test environment
        systems_dir = (
            tmp_path / "systems" / "test_system" / "test_module" / "domain" / "entities"
        )
        systems_dir.mkdir(parents=True)

        # This should work without raising validation errors
        result = generator.create_component(
            base_path=tmp_path,
            system_name="test_system",
            module_name="test_module",
            layer="domain",
            component_type="entities",
            component_name="user",
        )

        assert result.exists()

        # Verify the generated content contains expected elements
        content = result.read_text()
        assert "class User" in content
        assert "@dataclass" in content
