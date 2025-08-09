#!/usr/bin/env python3
"""Version bump script for fast-clean-architecture.

This script updates the version in pyproject.toml and ensures all other
version references are updated accordingly.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[import-untyped]
    except ImportError:
        print("Error: tomli is required for Python versions less than 3.11")
        print("Install it with: pip install tomli")
        sys.exit(1)


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse a semantic version string into major, minor, patch components."""
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version)
    if not match:
        raise ValueError(f"Invalid version format: {version}. Expected format: X.Y.Z")
    
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def format_version(major: int, minor: int, patch: int) -> str:
    """Format version components into a semantic version string."""
    return f"{major}.{minor}.{patch}"


def get_current_version() -> str:
    """Get the current version from pyproject.toml."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    
    return data["project"]["version"]


def update_pyproject_version(new_version: str) -> None:
    """Update the version in pyproject.toml."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "r") as f:
        content = f.read()
    
    # Update the version line
    updated_content = re.sub(
        r'version = "[^"]+"',
        f'version = "{new_version}"',
        content
    )
    
    with open(pyproject_path, "w") as f:
        f.write(updated_content)
    
    print(f"✅ Updated pyproject.toml version to {new_version}")


def update_init_fallback_version(new_version: str) -> None:
    """Update the fallback version in __init__.py."""
    init_path = Path(__file__).parent.parent / "fast_clean_architecture" / "__init__.py"
    
    with open(init_path, "r") as f:
        content = f.read()
    
    # Update the fallback version line
    updated_content = re.sub(
        r'__version__ = "[^"]+"',
        f'__version__ = "{new_version}"',
        content
    )
    
    with open(init_path, "w") as f:
        f.write(updated_content)
    
    print(f"✅ Updated __init__.py fallback version to {new_version}")


def bump_version(bump_type: str, custom_version: Optional[str] = None) -> str:
    """Bump the version according to the specified type.
    
    Args:
        bump_type: One of 'major', 'minor', 'patch', or 'custom'
        custom_version: Required if bump_type is 'custom'
    
    Returns:
        The new version string
    """
    if bump_type == "custom":
        if not custom_version:
            raise ValueError("Custom version must be provided when bump_type is 'custom'")
        # Validate the custom version format
        parse_version(custom_version)
        return custom_version
    
    current_version = get_current_version()
    major, minor, patch = parse_version(current_version)
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}. Must be 'major', 'minor', 'patch', or 'custom'")
    
    return format_version(major, minor, patch)


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Bump version for fast-clean-architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/bump_version.py patch          # Bump patch version (1.2.2 -> 1.2.3)
  python scripts/bump_version.py minor          # Bump minor version (1.2.2 -> 1.3.0)
  python scripts/bump_version.py major          # Bump major version (1.2.2 -> 2.0.0)
  python scripts/bump_version.py custom 2.0.0   # Set custom version
"""
    )
    
    parser.add_argument(
        "bump_type",
        choices=["major", "minor", "patch", "custom"],
        help="Type of version bump to perform"
    )
    
    parser.add_argument(
        "version",
        nargs="?",
        help="Custom version (required when bump_type is 'custom')"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes"
    )
    
    args = parser.parse_args()
    
    try:
        current_version = get_current_version()
        new_version = bump_version(args.bump_type, args.version)
        
        print(f"Current version: {current_version}")
        print(f"New version: {new_version}")
        
        if args.dry_run:
            print("\n🔍 DRY RUN - No changes will be made")
            print("Files that would be updated:")
            print("  - pyproject.toml")
            print("  - fast_clean_architecture/__init__.py")
            return 0
        
        # Confirm the change
        response = input(f"\nUpdate version from {current_version} to {new_version}? [y/N]: ")
        if response.lower() not in ['y', 'yes']:
            print("❌ Version bump cancelled")
            return 1
        
        # Update files
        update_pyproject_version(new_version)
        update_init_fallback_version(new_version)
        
        print(f"\n🎉 Successfully bumped version from {current_version} to {new_version}")
        print("\n📝 Next steps:")
        print("  1. Review the changes")
        print("  2. Run tests to ensure everything works")
        print("  3. Commit the version bump")
        print("  4. Create a git tag for the new version")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())