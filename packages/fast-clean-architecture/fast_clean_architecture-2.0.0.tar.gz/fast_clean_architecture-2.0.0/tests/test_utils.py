"""Tests for utility functions."""

from datetime import datetime
from pathlib import Path

import pytest

from fast_clean_architecture.exceptions import ValidationError
from fast_clean_architecture.utils import (
    ensure_directory,
    generate_timestamp,
    get_component_type_from_path,
    get_layer_from_path,
    get_template_variables,
    parse_location_path,
    pluralize,
    sanitize_name,
    to_camel_case,
    to_pascal_case,
    to_snake_case,
    validate_python_identifier,
)


class TestTimestamp:
    """Test timestamp generation."""

    def test_generate_timestamp_format(self):
        """Test that timestamp is in correct ISO 8601 format."""
        timestamp = generate_timestamp()

        # Should be able to parse as ISO format
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        assert isinstance(parsed, datetime)

        # Should end with Z for UTC
        assert timestamp.endswith("Z")

        # Should contain milliseconds
        assert "." in timestamp


class TestStringConversions:
    """Test string conversion functions."""

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("CamelCase", "camel_case"),
            ("PascalCase", "pascal_case"),
            ("snake_case", "snake_case"),
            ("kebab-case", "kebab_case"),
            ("MixedCase_string", "mixed_case_string"),
            ("HTTPSConnection", "https_connection"),
            ("XMLParser", "xml_parser"),
            ("APIKey", "api_key"),
        ],
    )
    def test_to_snake_case(self, input_str: str, expected: str):
        """Test snake_case conversion."""
        assert to_snake_case(input_str) == expected

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("snake_case", "SnakeCase"),
            ("camelCase", "CamelCase"),
            ("PascalCase", "PascalCase"),
            ("kebab-case", "KebabCase"),
            ("mixed_Case-string", "MixedCaseString"),
            ("user_repository", "UserRepository"),
            ("api_key", "ApiKey"),
        ],
    )
    def test_to_pascal_case(self, input_str: str, expected: str):
        """Test PascalCase conversion."""
        assert to_pascal_case(input_str) == expected

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("snake_case", "snakeCase"),
            ("PascalCase", "pascalCase"),
            ("camelCase", "camelCase"),
            ("kebab-case", "kebabCase"),
            ("user_repository", "userRepository"),
            ("api_key", "apiKey"),
        ],
    )
    def test_to_camel_case(self, input_str: str, expected: str):
        """Test camelCase conversion."""
        assert to_camel_case(input_str) == expected

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("user", "users"),
            ("entity", "entities"),
            ("repository", "repositories"),
            ("query", "queries"),
            ("category", "categories"),
            ("box", "boxes"),
            ("child", "children"),
            ("person", "people"),
            ("mouse", "mice"),
            ("data", "data"),  # Uncountable
            ("sheep", "sheep"),  # Uncountable
        ],
    )
    def test_pluralize(self, input_str: str, expected: str):
        """Test pluralization."""
        assert pluralize(input_str) == expected


class TestValidation:
    """Test validation functions."""

    @pytest.mark.parametrize(
        "identifier,expected",
        [
            ("valid_name", True),
            ("ValidName", True),
            ("_private", True),
            ("name123", True),
            ("123invalid", False),
            ("invalid-name", False),
            ("invalid.name", False),
            ("invalid name", False),
            ("", False),
            ("class", False),  # Python keyword
            ("def", False),  # Python keyword
            ("import", False),  # Python keyword
        ],
    )
    def test_validate_python_identifier(self, identifier: str, expected: bool):
        """Test Python identifier validation."""
        assert validate_python_identifier(identifier) == expected

    @pytest.mark.parametrize(
        "name,expected",
        [
            ("Valid Name", "valid_name"),
            ("Invalid-Name!", "invalid_name"),
            ("123Invalid", "invalid"),
            ("Special@#$Characters", "special_characters"),
            ("  Whitespace  ", "whitespace"),
            ("CamelCase", "camel_case"),
            ("snake_case", "snake_case"),
        ],
    )
    def test_sanitize_name(self, name: str, expected: str):
        """Test name sanitization."""
        assert sanitize_name(name) == expected


class TestTemplateVariables:
    """Test template variable generation."""

    def test_get_template_variables(self):
        """Test template variable generation."""
        variables = get_template_variables(
            system_name="user_management",
            module_name="authentication",
            component_name="user_entity",
            component_type="entities",
        )

        expected_keys = {
            "system_name",
            "SystemName",
            "system_name_camel",
            "module_name",
            "ModuleName",
            "module_name_camel",
            "component_name",
            "ComponentName",
            "component_name_camel",
            "component_type",
            "ComponentType",
            "component_type_camel",
            "entity_name",
            "EntityName",
            "entity_name_camel",
            "repository_name",
            "RepositoryName",
            "repository_name_camel",
            "service_name",
            "ServiceName",
            "service_name_camel",
            "router_name",
            "RouterName",
            "router_name_camel",
            "schema_name",
            "SchemaName",
            "schema_name_camel",
            "model_name",
            "ModelName",
            "model_name_camel",
            "command_name",
            "CommandName",
            "command_name_camel",
            "query_name",
            "QueryName",
            "query_name_camel",
            "value_object_name",
            "ValueObjectName",
            "value_object_name_camel",
            "external_service_name",
            "ExternalServiceName",
            "external_service_name_camel",
            "dto_name",
            "DtoName",
            "dto_name_camel",
            "enum_name",
            "EnumName",
            "enum_name_camel",
            "entity_file",
            "repository_file",
            "service_file",
            "router_file",
            "schema_file",
            "model_file",
            "command_file",
            "query_file",
            "value_object_file",
            "external_service_file",
            "dto_file",
            "resource_name",
            "resource_name_plural",
            "entity_description",
            "service_description",
            "module_description",
            "domain_import_path",
            "application_import_path",
            "infrastructure_import_path",
            "presentation_import_path",
            "entity_import",
            "repository_import",
            "service_import",
            "generated_at",
            "generator_version",
            "table_name",
            "collection_name",
            "endpoint_prefix",
            "entity_type",
            "repository_type",
            "service_type",
        }

        assert set(variables.keys()) == expected_keys

        # Test specific values
        assert variables["system_name"] == "user_management"
        assert variables["SystemName"] == "UserManagement"
        assert variables["module_name"] == "authentication"
        assert variables["ModuleName"] == "Authentication"
        assert variables["component_name"] == "user_entity"
        assert variables["ComponentName"] == "UserEntity"
        assert variables["entity_name"] == "user_entity"
        assert variables["EntityName"] == "UserEntity"


class TestPathUtilities:
    """Test path utility functions."""

    def test_ensure_directory(self, temp_dir: Path):
        """Test directory creation."""
        test_dir = temp_dir / "nested" / "directory" / "structure"

        # Directory should not exist initially
        assert not test_dir.exists()

        # Create directory
        ensure_directory(test_dir)

        # Directory should now exist
        assert test_dir.exists()
        assert test_dir.is_dir()

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("systems/user/auth/domain/entities/user.py", "domain"),
            ("systems/user/auth/application/services/user_service.py", "application"),
            ("systems/user/auth/infrastructure/models/user_model.py", "infrastructure"),
            ("systems/user/auth/presentation/api/user_router.py", "presentation"),
            ("invalid/path", None),
        ],
    )
    def test_get_layer_from_path(self, path: str, expected: str):
        """Test layer extraction from path."""
        result = get_layer_from_path(path)
        assert result == expected

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("systems/user/auth/domain/entities/user.py", "entities"),
            ("systems/user/auth/application/services/user_service.py", "services"),
            (
                "systems/user/auth/infrastructure/repositories/user_repo.py",
                "repositories",
            ),
            ("systems/user/auth/presentation/schemas/user_schemas.py", "schemas"),
            ("invalid/path", None),
        ],
    )
    def test_get_component_type_from_path(self, path: str, expected: str):
        """Test component type extraction from path."""
        result = get_component_type_from_path(path)
        assert result == expected

    def test_parse_location_path_valid(self):
        """Test parsing valid location path."""
        result = parse_location_path("user_management/authentication/domain/entities")

        expected = {
            "system_name": "user_management",
            "module_name": "authentication",
            "layer": "domain",
            "component_type": "entities",
        }

        assert result == expected

    def test_parse_location_path_invalid(self):
        """Test parsing invalid location path."""
        with pytest.raises(ValidationError, match="Location must be in format"):
            parse_location_path("invalid/path")

        with pytest.raises(ValidationError, match="Location must be in format"):
            parse_location_path("too/many/parts/here/extra")
