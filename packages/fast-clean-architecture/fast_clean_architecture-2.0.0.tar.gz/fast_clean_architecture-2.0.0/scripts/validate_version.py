#!/usr/bin/env python3
"""Version validation script for fast-clean-architecture.

This script validates that all version references in the codebase are consistent
with the main version defined in pyproject.toml.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib # type: ignore[import-untyped]
    except ImportError:
        print("❌ Error: tomli package is required for Python < 3.11")
        print("Install it with: pip install tomli")
        sys.exit(1)


def get_pyproject_version() -> str:
    """Get the version from pyproject.toml."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    
    return data["project"]["version"]


def get_init_version() -> str:
    """Get the fallback version from __init__.py."""
    init_path = Path(__file__).parent.parent / "fast_clean_architecture" / "__init__.py"
    
    with open(init_path, "r") as f:
        content = f.read()
    
    # Find the fallback version line
    match = re.search(r'__version__ = "([^"]+)"', content)
    if match:
        return match.group(1)
    
    raise ValueError("Could not find fallback version in __init__.py")


def validate_versions() -> List[Tuple[str, str, str]]:
    """Validate version consistency across the codebase.
    
    Returns:
        List of (file_path, expected_version, actual_version) for mismatches
    """
    pyproject_version = get_pyproject_version()
    init_version = get_init_version()
    
    mismatches = []
    
    # Check __init__.py fallback version
    if pyproject_version != init_version:
        mismatches.append((
            "fast_clean_architecture/__init__.py",
            pyproject_version,
            init_version
        ))
    
    return mismatches


def main() -> int:
    """Main validation function."""
    try:
        mismatches = validate_versions()
        
        if not mismatches:
            print("✅ All version references are consistent!")
            return 0
        
        print("❌ Version mismatches found:")
        for file_path, expected, actual in mismatches:
            print(f"  {file_path}: expected {expected}, found {actual}")
        
        print("\n💡 Please update the mismatched versions to match pyproject.toml")
        return 1
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())