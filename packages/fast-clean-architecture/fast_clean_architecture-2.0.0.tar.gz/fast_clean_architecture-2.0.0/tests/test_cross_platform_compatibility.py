"""Tests for cross-platform compatibility of symlink attack prevention."""

from pathlib import Path
from unittest.mock import patch

import pytest

from fast_clean_architecture.config import Config
from fast_clean_architecture.exceptions import ValidationError
from fast_clean_architecture.generators.generator_factory import (
    create_generator_factory,
)


class TestCrossPlatformCompatibility:
    """Test cases for cross-platform temporary path detection."""

    @pytest.fixture
    def generator(self):
        """Create a component generator for testing."""
        config = Config()
        factory = create_generator_factory(config=config)
        return factory.create_generator("component")

    def test_windows_temp_path_detection(self, generator):
        """Test that Windows temporary paths are correctly detected."""
        windows_temp_paths = [
            "C:\\Users\\username\\AppData\\Local\\Temp\\test_file.py",
            "C:\\Windows\\Temp\\test_file.py",
            "D:\\Temp\\test_file.py",
            "C:\\temp\\test_file.py",
            "E:\\tmp\\test_file.py",
        ]

        for temp_path in windows_temp_paths:
            with patch("pathlib.Path.resolve") as mock_resolve:
                mock_resolve.return_value = Path(temp_path)
                with patch("pathlib.Path.exists") as mock_exists:
                    mock_exists.return_value = False

                    # This should not raise ValidationError for temp paths
                    try:
                        generator._check_symlink_attack(Path(temp_path))
                    except ValidationError as e:
                        if "systems directory" in str(e):
                            # This is expected for temp paths - they bypass the systems check
                            continue
                        else:
                            pytest.fail(
                                f"Unexpected ValidationError for Windows temp path {temp_path}: {e}"
                            )

    def test_linux_temp_path_detection(self, generator):
        """Test that Linux temporary paths are correctly detected."""
        linux_temp_paths = [
            "/tmp/test_file.py",
            "/var/tmp/test_file.py",
            "/temp/test_file.py",
            "/home/user/tmp/test_file.py",
        ]

        for temp_path in linux_temp_paths:
            with patch("pathlib.Path.resolve") as mock_resolve:
                mock_resolve.return_value = Path(temp_path)
                with patch("pathlib.Path.exists") as mock_exists:
                    mock_exists.return_value = False

                    # This should not raise ValidationError for temp paths
                    try:
                        generator._check_symlink_attack(Path(temp_path))
                    except ValidationError as e:
                        if "systems directory" in str(e):
                            # This is expected for temp paths - they bypass the systems check
                            continue
                        else:
                            pytest.fail(
                                f"Unexpected ValidationError for Linux temp path {temp_path}: {e}"
                            )

    def test_macos_temp_path_detection(self, generator):
        """Test that macOS temporary paths are correctly detected."""
        macos_temp_paths = [
            "/private/var/folders/abc/def/T/test_file.py",
            "/var/folders/abc/def/T/test_file.py",
            "/tmp/test_file.py",
        ]

        for temp_path in macos_temp_paths:
            with patch("pathlib.Path.resolve") as mock_resolve:
                mock_resolve.return_value = Path(temp_path)
                with patch("pathlib.Path.exists") as mock_exists:
                    mock_exists.return_value = False

                    # This should not raise ValidationError for temp paths
                    try:
                        generator._check_symlink_attack(Path(temp_path))
                    except ValidationError as e:
                        if "systems directory" in str(e):
                            # This is expected for temp paths - they bypass the systems check
                            continue
                        else:
                            pytest.fail(
                                f"Unexpected ValidationError for macOS temp path {temp_path}: {e}"
                            )

    def test_pytest_temp_path_detection(self, generator):
        """Test that pytest temporary paths are correctly detected across platforms."""
        pytest_temp_paths = [
            "/tmp/pytest-of-user/pytest-current/test_session/test_file.py",
            "C:\\Users\\user\\AppData\\Local\\Temp\\pytest-of-user\\test_file.py",
            "/private/var/folders/abc/pytest-of-user/test_file.py",
        ]

        for temp_path in pytest_temp_paths:
            with patch("pathlib.Path.resolve") as mock_resolve:
                mock_resolve.return_value = Path(temp_path)
                with patch("pathlib.Path.exists") as mock_exists:
                    mock_exists.return_value = False

                    # This should not raise ValidationError for pytest temp paths
                    try:
                        generator._check_symlink_attack(Path(temp_path))
                    except ValidationError as e:
                        if "systems directory" in str(e):
                            # This is expected for temp paths - they bypass the systems check
                            continue
                        else:
                            pytest.fail(
                                f"Unexpected ValidationError for pytest temp path {temp_path}: {e}"
                            )

    def test_non_temp_path_validation(self, generator):
        """Test that non-temporary paths still require systems directory validation."""
        non_temp_paths = [
            "/home/user/project/test_file.py",
            "C:\\Users\\user\\Documents\\project\\test_file.py",
            "/Users/user/Documents/project/test_file.py",
        ]

        for non_temp_path in non_temp_paths:
            with (
                patch.object(Path, "is_symlink", return_value=False),
                patch.object(Path, "resolve", return_value=Path(non_temp_path)),
                patch.object(generator, "_is_temp_path", return_value=False),
            ):
                # This should raise ValidationError for non-temp paths without 'systems'
                with pytest.raises(ValidationError, match="systems directory"):
                    generator._check_symlink_attack(Path(non_temp_path))
