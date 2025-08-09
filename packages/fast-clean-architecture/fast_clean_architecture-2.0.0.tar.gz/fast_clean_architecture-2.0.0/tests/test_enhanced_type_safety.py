"""Tests for enhanced type safety features with protocol-based design.

This module tests the new type-safe protocols, generic type constraints,
and enhanced security features implemented in the component generator.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from fast_clean_architecture.config import Config
from fast_clean_architecture.exceptions import (
    SecurityError,
    ValidationError,
)
from fast_clean_architecture.generators.generator_factory import (
    create_generator_factory,
)
from fast_clean_architecture.protocols import (
    ComponentGeneratorProtocol,
    ComponentValidationStrategy,
    SecurePathHandler,
)


class TestSecurePathHandler:
    """Test the SecurePathHandler with generic type constraints."""

    def test_path_handler_with_string_input(self):
        """Test path handler with string input maintains type consistency."""
        handler = SecurePathHandler[str]()
        input_path = "valid/path/to/file.py"
        result = handler.process(input_path)

        assert isinstance(result, str)
        assert result == input_path

    def test_path_handler_with_path_input(self):
        """Test path handler with Path input maintains type consistency."""
        handler = SecurePathHandler[Path]()
        input_path = Path("valid/path/to/file.py")
        result = handler.process(input_path)

        assert isinstance(result, Path)
        assert result == input_path

    def test_path_traversal_detection(self):
        """Test that path traversal attempts are detected and blocked."""
        handler = SecurePathHandler[str]()
        malicious_path = "../../../etc/passwd"

        with pytest.raises(SecurityError, match="Path security validation failed"):
            handler.process(malicious_path)

    def test_dangerous_characters_detection(self):
        """Test that dangerous characters in paths are detected."""
        handler = SecurePathHandler[str]()
        dangerous_paths = [
            "file<script>.py",
            "file>output.py",
            "file|pipe.py",
            "file\x00null.py",
        ]

        for dangerous_path in dangerous_paths:
            with pytest.raises(SecurityError):
                handler.process(dangerous_path)

    def test_path_length_validation(self):
        """Test that overly long paths are rejected."""
        handler = SecurePathHandler[str](max_path_length=50)
        long_path = "a" * 100 + ".py"

        with pytest.raises(ValidationError, match="Path too long"):
            handler.process(long_path)

    def test_file_extension_validation(self):
        """Test that only allowed file extensions are accepted."""
        handler = SecurePathHandler[str](allowed_extensions=[".py", ".yaml"])

        # Valid extension should pass
        valid_path = "component.py"
        result = handler.process(valid_path)
        assert result == valid_path

        # Invalid extension should fail
        invalid_path = "malicious.exe"
        with pytest.raises(ValidationError, match="File extension not allowed"):
            handler.process(invalid_path)

    def test_windows_reserved_names(self):
        """Test that Windows reserved names are detected."""
        handler = SecurePathHandler[str]()
        reserved_names = ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1"]

        for name in reserved_names:
            with pytest.raises(SecurityError):
                handler.process(name)


class TestComponentValidationStrategy:
    """Test the ComponentValidationStrategy with generic type support."""

    def test_entity_validation_strategy(self):
        """Test validation strategy for entity components."""
        rules = {
            "required_fields": ["name", "type"],
            "field_types": {
                "name": str,
                "type": str,
                "attributes": (list, type(None)),
            },
        }
        strategy = ComponentValidationStrategy("entity", rules)

        # Valid entity should pass
        valid_entity = {
            "name": "User",
            "type": "entity",
            "attributes": ["id", "name", "email"],
        }
        assert strategy.validate(valid_entity) is True

        # Missing required field should fail
        invalid_entity = {"name": "User"}
        with pytest.raises(ValidationError, match="Missing required field 'type'"):
            strategy.validate(invalid_entity)

        # Wrong field type should fail
        wrong_type_entity = {"name": 123, "type": "entity"}  # Should be string
        with pytest.raises(ValidationError, match="Field 'name' must be of type str"):
            strategy.validate(wrong_type_entity)

    def test_service_validation_strategy(self):
        """Test validation strategy for service components."""
        rules = {
            "required_fields": ["name", "type"],
            "field_types": {
                "name": str,
                "type": str,
                "dependencies": (list, type(None)),
            },
        }
        strategy = ComponentValidationStrategy("service", rules)

        # Valid service should pass
        valid_service = {
            "name": "UserService",
            "type": "service",
            "dependencies": ["UserRepository"],
        }
        assert strategy.validate(valid_service) is True

    def test_error_message_generation(self):
        """Test that descriptive error messages are generated."""
        rules = {"required_fields": ["name", "type"]}
        strategy = ComponentValidationStrategy("test", rules)

        invalid_data = {"name": "Test"}
        error_msg = strategy.get_error_message(invalid_data)

        assert "Validation failed for test" in error_msg
        assert "Missing required field 'type'" in error_msg


class TestComponentGeneratorProtocol:
    """Test the ComponentGenerator implementation of the protocol."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        config = Mock(spec=Config)
        config.templates = Mock()
        return config

    @pytest.fixture
    def component_generator(self, mock_config):
        """Create a ComponentGenerator instance for testing."""
        factory = create_generator_factory(config=mock_config)
        return factory.create_generator("component")

    def test_implements_protocol(self, component_generator):
        """Test that ComponentGenerator implements the protocol correctly."""
        assert isinstance(component_generator, ComponentGeneratorProtocol)

    def test_validate_component_with_valid_data(self, component_generator):
        """Test component validation with valid data."""
        valid_component = {
            "name": "TestEntity",
            "type": "entity",
            "attributes": ["id", "name"],
        }

        result = component_generator.validate_component(valid_component)
        assert result is True

    def test_validate_component_with_invalid_data(self, component_generator):
        """Test component validation with invalid data."""
        invalid_component = {
            "name": "TestEntity"
            # Missing 'type' field
        }

        with pytest.raises(ValidationError, match="Missing required field 'type'"):
            component_generator.validate_component(invalid_component)

    def test_validate_component_with_non_dict(self, component_generator):
        """Test component validation with non-dictionary input."""
        invalid_input = "not a dictionary"

        with pytest.raises(ValidationError, match="Component must be a dictionary"):
            component_generator.validate_component(invalid_input)

    def test_validate_component_with_invalid_name(self, component_generator):
        """Test component validation with invalid component name."""
        invalid_component = {"name": "../malicious", "type": "entity"}

        with pytest.raises((ValidationError, SecurityError)):
            component_generator.validate_component(invalid_component)

    @patch("fast_clean_architecture.generators.component_generator.ensure_directory")
    @patch(
        "fast_clean_architecture.generators.component_generator.get_template_variables"
    )
    def test_create_component_with_validation(
        self, mock_get_vars, mock_ensure_dir, component_generator, tmp_path
    ):
        """Test component creation with enhanced validation."""
        # Setup mocks
        mock_get_vars.return_value = {"component_name": "TestEntity"}
        component_generator._get_template_name = Mock(return_value="entity.py.j2")
        component_generator._validate_template_variables = Mock()
        component_generator._render_template = Mock(return_value="# Test content")
        component_generator._atomic_write_file = Mock()

        # Test data
        component_config = {
            "name": "TestEntity",
            "type": "entities",  # Use valid component type
            "system_name": "test_system",
            "module_name": "test_module",
            "layer": "domain",
        }

        # Call the new validation-enhanced method
        result = component_generator.create_component_with_validation(
            component_config=component_config, base_path=tmp_path, dry_run=True
        )

        # Verify result
        assert isinstance(result, Path)
        assert result.name == "test_entity.py"

    def test_create_component_with_validation_invalid_config(
        self, component_generator, tmp_path
    ):
        """Test component creation with invalid configuration."""
        invalid_config = {"name": "../malicious", "type": "entities"}

        with pytest.raises((ValidationError, SecurityError)):
            component_generator.create_component_with_validation(
                component_config=invalid_config, base_path=tmp_path
            )

    def test_create_component_with_validation_insecure_path(self, component_generator):
        """Test component creation with insecure base path."""
        component_config = {"name": "TestEntity", "type": "entities"}

        insecure_path = Path("../../../etc")

        with pytest.raises(SecurityError):
            component_generator.create_component_with_validation(
                component_config=component_config, base_path=insecure_path
            )


class TestTypeConstraints:
    """Test generic type constraints and type safety features."""

    def test_path_handler_type_preservation(self):
        """Test that path handler preserves input types correctly."""
        # Test with string
        string_handler = SecurePathHandler[str]()
        string_input = "test/path.py"
        string_result = string_handler.process(string_input)
        assert type(string_result) is str

        # Test with Path
        path_handler = SecurePathHandler[Path]()
        path_input = Path("test/path.py")
        path_result = path_handler.process(path_input)
        assert isinstance(path_result, Path)

    def test_validation_strategy_type_consistency(self):
        """Test that validation strategies maintain type consistency."""
        rules = {"required_fields": ["name"]}
        strategy = ComponentValidationStrategy[str]("test", rules)

        # The strategy should work with the specified component type
        assert strategy.component_type == "test"
        assert isinstance(strategy.validation_rules, dict)

    def test_protocol_runtime_checking(self):
        """Test that protocols can be checked at runtime."""
        from fast_clean_architecture.protocols import ComponentGeneratorProtocol

        # Mock implementation
        class MockGenerator:
            def __init__(self):
                from fast_clean_architecture.config import Config

                # Create simple mock objects for required attributes
                class MockPathHandler:
                    pass

                class MockTemplateValidator:
                    pass

                self.config = Config.create_default()
                self.path_handler = MockPathHandler()
                self.template_validator = MockTemplateValidator()

            def create_component(self, *args, **kwargs):
                return Path("test.py")

            def validate_component(self, component):
                return True

            def create_multiple_components(self, *args, **kwargs):
                return [Path("test1.py"), Path("test2.py")]

        mock_gen = MockGenerator()
        assert isinstance(mock_gen, ComponentGeneratorProtocol)

        # Incomplete implementation should fail
        class IncompleteGenerator:
            def create_component(self, *args, **kwargs):
                return Path("test.py")

            # Missing validate_component method

        incomplete_gen = IncompleteGenerator()
        assert not isinstance(incomplete_gen, ComponentGeneratorProtocol)


class TestIntegrationWithExistingCode:
    """Test integration of enhanced type safety with existing codebase."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        config = Mock(spec=Config)
        config.templates = Mock()
        return config

    @pytest.fixture
    def component_generator(self, mock_config):
        """Create a ComponentGenerator instance for testing."""
        from fast_clean_architecture.generators.generator_factory import (
            create_generator_factory,
        )

        factory = create_generator_factory(config=mock_config)
        return factory.create_generator("component")

    def test_backward_compatibility(self, component_generator, tmp_path):
        """Test that enhanced features don't break existing functionality."""
        # The original create_component method should still work
        with patch.object(component_generator, "_validate_file_system"):
            with patch.object(
                component_generator, "_get_template_name", return_value="entity.py.j2"
            ):
                with patch.object(component_generator, "_validate_template_variables"):
                    with patch.object(
                        component_generator, "_render_template", return_value="# Test"
                    ):
                        with patch.object(component_generator, "_atomic_write_file"):
                            result = component_generator.create_component(
                                base_path=tmp_path,
                                system_name="test",
                                module_name="test",
                                layer="domain",
                                component_type="entities",
                                component_name="TestEntity",
                                dry_run=True,
                            )

                            assert isinstance(result, Path)

    def test_enhanced_security_in_existing_methods(self, component_generator, tmp_path):
        """Test that existing methods now use enhanced security features."""
        # The path handler should be used in create_component
        assert hasattr(component_generator, "path_handler")
        assert isinstance(component_generator.path_handler, SecurePathHandler)

        # Validation strategies should be initialized
        assert hasattr(component_generator, "_validation_strategies")
        assert isinstance(component_generator._validation_strategies, dict)
        assert "entity" in component_generator._validation_strategies
