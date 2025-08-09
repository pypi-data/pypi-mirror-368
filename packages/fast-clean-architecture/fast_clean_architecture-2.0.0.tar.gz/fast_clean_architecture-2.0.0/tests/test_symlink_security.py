"""Tests for symlink attack prevention enhancements."""

import os
import tempfile
from pathlib import Path
from typing import cast
from unittest.mock import patch

import pytest

from fast_clean_architecture.config import Config
from fast_clean_architecture.exceptions import ValidationError
from fast_clean_architecture.generators.component_generator import ComponentGenerator
from fast_clean_architecture.generators.generator_factory import (
    create_generator_factory,
)


class TestSymlinkSecurity:
    """Test enhanced symlink attack prevention."""

    def setup_method(self):
        """Set up test fixtures."""
        config = Config.create_default()
        factory = create_generator_factory(config)
        self.generator = factory.create_generator("component")

    def test_strict_path_resolution_with_broken_symlink(self, tmp_path):
        """Test that broken symlinks are properly detected and rejected."""
        # Create a broken symlink
        broken_symlink = tmp_path / "broken_link"
        target = tmp_path / "nonexistent_target"

        # Create symlink to non-existent target
        broken_symlink.symlink_to(target)

        # Verify symlink exists but target doesn't
        assert broken_symlink.is_symlink()
        assert not broken_symlink.exists()

        # Test file path that includes the broken symlink
        test_path = broken_symlink / "systems" / "test.py"

        with pytest.raises(ValidationError, match="Broken symlink detected"):
            cast(ComponentGenerator, self.generator)._check_symlink_attack(test_path)

    def test_safe_system_symlink_detection(self):
        """Test that safe system symlinks are properly identified."""
        # Test macOS system symlinks
        assert cast(ComponentGenerator, self.generator)._is_safe_system_symlink(
            Path("/var"), Path("/private/var")
        )
        assert cast(ComponentGenerator, self.generator)._is_safe_system_symlink(
            Path("/tmp"), Path("/private/tmp")
        )
        assert cast(ComponentGenerator, self.generator)._is_safe_system_symlink(
            Path("/etc"), Path("/private/etc")
        )

        # Test system directory symlinks
        assert cast(ComponentGenerator, self.generator)._is_safe_system_symlink(
            Path("/usr/bin/python"), Path("/bin/python")
        )

        # Test unsafe symlinks
        assert not cast(ComponentGenerator, self.generator)._is_safe_system_symlink(
            Path("/home/user/project"), Path("/etc/passwd")
        )
        assert not cast(ComponentGenerator, self.generator)._is_safe_system_symlink(
            Path("/tmp/malicious"), Path("/root/.ssh/id_rsa")
        )

    def test_path_within_safe_bounds(self):
        """Test that dangerous paths are properly identified."""
        # Test safe paths
        assert cast(ComponentGenerator, self.generator)._is_path_within_safe_bounds(
            Path("/home/user/project")
        )
        assert cast(ComponentGenerator, self.generator)._is_path_within_safe_bounds(
            Path("/tmp/test")
        )
        assert cast(ComponentGenerator, self.generator)._is_path_within_safe_bounds(
            Path("/var/log/app.log")
        )

        # Test dangerous paths
        assert not cast(ComponentGenerator, self.generator)._is_path_within_safe_bounds(
            Path("/etc/passwd")
        )
        assert not cast(ComponentGenerator, self.generator)._is_path_within_safe_bounds(
            Path("/etc/shadow")
        )
        assert not cast(ComponentGenerator, self.generator)._is_path_within_safe_bounds(
            Path("/root/secret")
        )
        assert not cast(ComponentGenerator, self.generator)._is_path_within_safe_bounds(
            Path("/boot/vmlinuz")
        )
        assert not cast(ComponentGenerator, self.generator)._is_path_within_safe_bounds(
            Path("/proc/version")
        )
        assert not cast(ComponentGenerator, self.generator)._is_path_within_safe_bounds(
            Path("/sys/kernel")
        )
        assert not cast(ComponentGenerator, self.generator)._is_path_within_safe_bounds(
            Path("/dev/sda")
        )

    def test_enhanced_temp_path_detection(self, tmp_path):
        """Test enhanced temporary directory detection."""
        # Test system temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            assert cast(ComponentGenerator, self.generator)._is_temp_path(temp_path)

        # Test pytest temp directory
        assert cast(ComponentGenerator, self.generator)._is_temp_path(tmp_path)

        # Test various temp patterns
        test_paths = [
            Path("/tmp/test"),
            Path("/var/tmp/test"),
            Path("/private/var/folders/test"),
            Path("/Users/test/AppData/Local/Temp/test"),
            Path("/pytest-of-user/test"),
        ]

        for path in test_paths:
            assert cast(ComponentGenerator, self.generator)._is_temp_path(path)

        # Test non-temp paths
        non_temp_paths = [
            Path("/home/user/project"),
            Path("/usr/local/bin"),
            Path("/opt/app"),
        ]

        for path in non_temp_paths:
            assert not cast(ComponentGenerator, self.generator)._is_temp_path(path)

    def test_path_traversal_detection(self, tmp_path):
        """Test detection of excessive path traversal attempts."""
        # Create a test path with excessive traversal
        malicious_path = tmp_path / "../../../../../../../etc/passwd"

        with pytest.raises(ValidationError, match="Excessive path traversal detected"):
            cast(ComponentGenerator, self.generator)._validate_resolved_path(
                malicious_path, Path("/etc/passwd")
            )

        # Test reasonable traversal (should pass)
        reasonable_path = tmp_path / "../systems/test.py"
        resolved_path = tmp_path.parent / "systems" / "test.py"

        # This should not raise an exception
        try:
            cast(ComponentGenerator, self.generator)._validate_resolved_path(
                reasonable_path, resolved_path
            )
        except ValidationError as e:
            if "Excessive path traversal" in str(e):
                pytest.fail("Reasonable path traversal was incorrectly flagged")

    def test_resolved_path_validation(self):
        """Test validation of resolved paths against restricted locations."""
        # Test that resolved paths pointing to dangerous locations are rejected
        with pytest.raises(
            ValidationError, match="Resolved path points to restricted location"
        ):
            cast(ComponentGenerator, self.generator)._validate_resolved_path(
                Path("test.py"), Path("/etc/passwd")
            )

        with pytest.raises(
            ValidationError, match="Resolved path points to restricted location"
        ):
            cast(ComponentGenerator, self.generator)._validate_resolved_path(
                Path("test.py"), Path("/root/secret")
            )

    def test_relative_symlink_validation(self, tmp_path):
        """Test validation of relative symlinks."""
        # Create a safe relative symlink
        safe_target = tmp_path / "safe_target.txt"
        safe_target.write_text("safe content")
        safe_symlink = tmp_path / "safe_link"
        safe_symlink.symlink_to("safe_target.txt")

        # Create test path through safe symlink
        test_path = safe_symlink / "systems" / "test.py"

        # Mock the safe bounds check to return True for this test
        with patch.object(
            self.generator, "_is_path_within_safe_bounds", return_value=True
        ):
            with patch.object(self.generator, "_is_temp_path", return_value=True):
                # This should not raise an exception
                try:
                    cast(ComponentGenerator, self.generator)._check_symlink_attack(
                        test_path
                    )
                except ValidationError as e:
                    if "symlink" in str(e).lower():
                        pytest.fail(
                            f"Safe relative symlink was incorrectly flagged: {e}"
                        )

    def test_absolute_symlink_validation(self, tmp_path):
        """Test validation of absolute symlinks."""
        # Create an unsafe absolute symlink
        unsafe_symlink = tmp_path / "unsafe_link"
        unsafe_symlink.symlink_to("/etc/passwd")

        # Test path through unsafe symlink
        test_path = unsafe_symlink / "systems" / "test.py"

        with pytest.raises(
            ValidationError, match="Potentially unsafe symlink detected"
        ):
            cast(ComponentGenerator, self.generator)._check_symlink_attack(test_path)

    @patch.dict(os.environ, {"TMPDIR": "/custom/temp"})
    def test_environment_based_temp_detection(self):
        """Test temp detection using environment variables."""
        custom_temp_path = Path("/custom/temp/test")

        # Mock Path.resolve to avoid actual filesystem operations
        with patch("pathlib.Path.resolve") as mock_resolve:
            mock_resolve.return_value = Path("/custom/temp")
            assert cast(ComponentGenerator, self.generator)._is_temp_path(
                custom_temp_path
            )

    def test_race_condition_mitigation(self, tmp_path):
        """Test that the enhanced validation helps mitigate race conditions."""
        # Create a path that will be validated
        test_path = tmp_path / "systems" / "test.py"

        # Mock path resolution to simulate a race condition scenario
        original_resolve = Path.resolve

        def mock_resolve(self, strict=False):
            if strict:
                # Simulate a race condition where strict resolution fails
                raise OSError("Simulated race condition")
            return original_resolve(self)

        with patch.object(Path, "resolve", mock_resolve):
            with patch.object(
                cast(ComponentGenerator, self.generator),
                "_is_temp_path",
                return_value=True,
            ):
                # The enhanced method should handle this gracefully
                try:
                    cast(ComponentGenerator, self.generator)._check_symlink_attack(
                        test_path
                    )
                except ValidationError as e:
                    if "race condition" in str(e).lower():
                        pytest.fail("Race condition was not properly handled")
