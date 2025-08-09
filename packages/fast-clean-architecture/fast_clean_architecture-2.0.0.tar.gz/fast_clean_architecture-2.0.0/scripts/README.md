# Version Management Scripts

This directory contains automated tools for managing versions in the fast-clean-architecture project.

## Scripts

### `validate_version.py`

Validates version consistency across the codebase.

**Usage:**
```bash
python scripts/validate_version.py
```

**What it checks:**
- Ensures `pyproject.toml` version matches `__init__.py` fallback version
- Reports any version mismatches found

**Exit codes:**
- `0`: All versions are consistent
- `1`: Version mismatches found or validation error

### `bump_version.py`

Automatically bumps the project version following semantic versioning.

**Usage:**
```bash
# Bump patch version (1.2.2 -> 1.2.3)
python scripts/bump_version.py patch

# Bump minor version (1.2.2 -> 1.3.0)
python scripts/bump_version.py minor

# Bump major version (1.2.2 -> 2.0.0)
python scripts/bump_version.py major

# Set custom version
python scripts/bump_version.py custom 2.0.0

# Preview changes without applying them
python scripts/bump_version.py patch --dry-run
```

**What it updates:**
- `pyproject.toml` - Primary version source
- `fast_clean_architecture/__init__.py` - Fallback version

**Features:**
- Interactive confirmation before making changes
- Dry-run mode for previewing changes
- Semantic version validation
- Clear next-steps guidance

## Integration

### Pre-commit Hook

Version validation runs automatically as a pre-commit hook when you modify:
- `pyproject.toml`
- `fast_clean_architecture/__init__.py`

This ensures version consistency is maintained across commits.

### CI/CD

These scripts can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Validate version consistency
  run: python scripts/validate_version.py
```

## Version Management Philosophy

1. **Single Source of Truth**: `pyproject.toml` is the primary version source
2. **Dynamic References**: All version references are derived programmatically
3. **Automated Validation**: Pre-commit hooks catch inconsistencies early
4. **Semantic Versioning**: Strict adherence to semver principles
5. **Developer Experience**: Simple tools with clear feedback

## Dependencies

These scripts require:
- Python 3.8+
- `tomllib` (Python 3.11+) or `tomli` (fallback for older versions)

No additional dependencies beyond the project's existing requirements.