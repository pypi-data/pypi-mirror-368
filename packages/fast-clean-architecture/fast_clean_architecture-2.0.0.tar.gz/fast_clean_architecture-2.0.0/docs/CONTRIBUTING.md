# Contributing to Fast Clean Architecture

We love your input! We want to make contributing to Fast Clean Architecture as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## Pull Requests

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- Package manager: pip with virtual environment tool (venv, conda, etc.) or Poetry

### Setup Steps

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/fast-clean-architecture.git
   cd fast-clean-architecture
   ```

2. **Choose Your Setup Method**

   #### Option A: Using pip with virtual environment
   
   **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
   
   **Install Development Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

   #### Option B: Using Poetry (Recommended)
   
   **Install Poetry** (if not already installed)
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   # Or using pip: pip install poetry
   ```
   
   **Install Dependencies**
   ```bash
   poetry install --with dev
   ```
   
   **Activate Poetry Shell**
   ```bash
   poetry shell
   ```

3. **Install Pre-commit Hooks**
   
   #### Using pip/venv
   ```bash
   pre-commit install
   ```
   
   #### Using Poetry
   ```bash
   poetry run pre-commit install
   ```

4. **Verify Setup**
   
   #### Using pip/venv
   ```bash
   pytest
   black --check .
   isort --check-only .
   mypy fast_clean_architecture
   ```
   
   #### Using Poetry
   ```bash
   poetry run pytest
   poetry run black --check .
   poetry run isort --check-only .
   poetry run mypy fast_clean_architecture
   ```

## Dependency Management

This project uses **Poetry** as the primary dependency manager, but also provides `requirements.txt` files for pip-based workflows.

### Understanding the Files

- **`pyproject.toml`**: Primary dependency definition (Poetry format)
- **`poetry.lock`**: Locked dependency versions (Poetry)
- **`requirements.txt`**: Production dependencies (pip format)
- **`requirements-dev.txt`**: Development dependencies (pip format)

### Updating Dependencies

#### Adding New Dependencies

**Using Poetry (Recommended)**
```bash
# Add production dependency
poetry add package-name

# Add development dependency
poetry add --group dev package-name
```

**Using pip**
```bash
# Add to pyproject.toml manually, then update requirements files
./update-requirements.sh
```

#### Updating Requirements Files

The `requirements.txt` files are automatically updated by pre-commit hooks when `pyproject.toml` changes. You can also update them manually:

```bash
# Using the provided script
./update-requirements.sh

# Or manually with Poetry
poetry export -f requirements.txt --output requirements.txt
poetry export -f requirements.txt --output requirements-dev.txt --extras dev
```

### Installation Options for Contributors

#### Option A: Using pip with requirements.txt
```bash
git clone https://github.com/YOUR_USERNAME/fast-clean-architecture.git
cd fast-clean-architecture
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
```

#### Option B: Using Poetry (Recommended)
```bash
git clone https://github.com/YOUR_USERNAME/fast-clean-architecture.git
cd fast-clean-architecture
poetry install --extras dev
poetry shell
```

## Code Style

We use several tools to maintain code quality:

### Formatting
- **Black**: Code formatting
- **isort**: Import sorting

#### Using pip/venv
```bash
# Format code
black fast_clean_architecture tests
isort fast_clean_architecture tests
```

#### Using Poetry
```bash
# Format code
poetry run black fast_clean_architecture tests
poetry run isort fast_clean_architecture tests
```

### Type Checking
- **mypy**: Static type checking

#### Using pip/venv
```bash
mypy fast_clean_architecture
```

#### Using Poetry
```bash
poetry run mypy fast_clean_architecture
```

### Security
- **bandit**: Security linting
- **safety**: Dependency vulnerability scanning

#### Using pip/venv
```bash
bandit -r fast_clean_architecture
safety check
```

#### Using Poetry
```bash
poetry run bandit -r fast_clean_architecture
poetry run safety check
```

### Testing
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting

#### Using pip/venv
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=fast_clean_architecture --cov-report=html
```

#### Using Poetry
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=fast_clean_architecture --cov-report=html

# Run specific test file
pytest tests/test_cli.py -v
```

#### Using Poetry
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=fast_clean_architecture --cov-report=html

# Run specific test file
poetry run pytest tests/test_cli.py -v
```

## Coding Standards

### Python Style
- Follow PEP 8 (enforced by Black)
- Use type hints for all public functions and methods
- Write docstrings for all public modules, functions, classes, and methods
- Use descriptive variable and function names

### Documentation Style
- Use Google-style docstrings
- Include examples in docstrings when helpful
- Keep line length under 88 characters (Black default)

### Example Function
```python
from typing import List, Optional

def process_components(
    components: List[str], 
    system_name: str, 
    dry_run: bool = False
) -> Optional[List[str]]:
    """Process a list of components for a given system.
    
    Args:
        components: List of component names to process.
        system_name: Name of the system context.
        dry_run: If True, only validate without creating files.
        
    Returns:
        List of created file paths, or None if dry_run is True.
        
    Raises:
        ValueError: If system_name is empty or invalid.
        ComponentError: If component creation fails.
        
    Example:
        >>> process_components(["user", "order"], "ecommerce")
        ["systems/ecommerce/entities/user.py", "systems/ecommerce/entities/order.py"]
    """
    if not system_name.strip():
        raise ValueError("System name cannot be empty")
    
    # Implementation here...
    pass
```

## Testing Guidelines

### Test Structure
- Place tests in the `tests/` directory
- Mirror the source code structure in test files
- Use descriptive test function names
- Group related tests in classes

### Test Categories
1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test component interactions
3. **CLI Tests**: Test command-line interface
4. **Template Tests**: Test code generation
5. **Validation Tests**: Test enhanced validation system and backward compatibility

### Example Test
```python
import pytest
from fast_clean_architecture.generators.component_generator import ComponentGenerator
from fast_clean_architecture.exceptions import ComponentError

class TestComponentGenerator:
    """Test cases for ComponentGenerator class."""
    
    def test_generate_entity_success(self, tmp_path):
        """Test successful entity generation."""
        generator = ComponentGenerator(base_path=tmp_path)
        result = generator.generate_component(
            system_name="test_system",
            module_name="test_module",
            component_type="entities",
            component_name="user"
        )
        
        assert result.success
        assert result.file_path.exists()
        assert "class User" in result.file_path.read_text()
    
    def test_generate_entity_invalid_name(self, tmp_path):
        """Test entity generation with invalid name."""
        generator = ComponentGenerator(base_path=tmp_path)
        
        with pytest.raises(ComponentError, match="Invalid component name"):
            generator.generate_component(
                system_name="test_system",
                module_name="test_module",
                component_type="entities",
                component_name="123invalid"
            )
    
    def test_layer_aware_validation(self, tmp_path):
        """Test enhanced layer-aware component validation."""
        generator = ComponentGenerator(base_path=tmp_path)
        
        # Valid component type for domain layer
        result = generator.generate_component(
            system_name="test_system",
            module_name="test_module",
            component_type="entities",
            component_name="user"
        )
        assert result.success
        
        # Invalid component type for domain layer
        with pytest.raises(ComponentError, match="not valid for layer 'domain'"):
            generator.generate_component(
                system_name="test_system",
                module_name="test_module",
                component_type="controllers",  # Invalid for domain layer
                component_name="user_controller"
            )
    
    def test_backward_compatibility_mapping(self, tmp_path):
        """Test component generation for presentation layer."""
        generator = ComponentGenerator(base_path=tmp_path)
        
        # Test controllers component type
        result = generator.generate_component(
            system_name="test_system",
            module_name="test_module",
            component_type="controllers",
            component_name="auth_controller"
        )
        
        assert result.success
        # Should create controller file, not api file
        assert "controller" in str(result.file_path).lower()
```

### Test Fixtures
Use pytest fixtures for common test setup:

```python
@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure for testing."""
    config_path = tmp_path / "fca_config.yaml"
    config_path.write_text("""
project:
  name: test-project
  description: Test project
  version: 0.1.0
  systems: {}
""")
    return tmp_path
```

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

### Examples
```
feat(cli): add batch component creation command

fix(templates): resolve entity template import issues

docs: update README with new examples

test(generators): add tests for component validation
```

## Issue Guidelines

### Bug Reports
When filing a bug report, please include:

1. **Environment**: Python version, OS, package version
2. **Steps to reproduce**: Minimal example that demonstrates the issue
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Error messages**: Full error output if applicable

### Feature Requests
When requesting a feature:

1. **Use case**: Describe the problem you're trying to solve
2. **Proposed solution**: How you think it should work
3. **Alternatives**: Other solutions you've considered
4. **Examples**: Code examples if applicable

## Release Process

### Version Numbering
We use [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Version Management
The project uses automated version management to ensure consistency:

#### Single Source of Truth
- **Primary version**: `pyproject.toml` (`project.version`)
- **Fallback version**: `fast_clean_architecture/__init__.py` (`__version__`)
- All other version references are dynamically derived from these sources

#### Version Bump Script
Use the automated version bump script for releases:

```bash
# Bump patch version (1.2.2 -> 1.2.3)
python scripts/bump_version.py patch

# Bump minor version (1.2.2 -> 1.3.0)
python scripts/bump_version.py minor

# Bump major version (1.2.2 -> 2.0.0)
python scripts/bump_version.py major

# Set custom version
python scripts/bump_version.py custom 2.0.0

# Dry run to preview changes
python scripts/bump_version.py patch --dry-run
```

#### Version Validation
The project includes automated version validation:

```bash
# Manual validation
python scripts/validate_version.py

# Automatic validation (runs on pre-commit)
git commit  # Version validation runs automatically
```

### Release Checklist
1. **Bump version**: Use `python scripts/bump_version.py [type]`
2. Update `CHANGELOG.md`
3. Run full test suite: `poetry run pytest`
4. Validate version consistency: `python scripts/validate_version.py`
5. Create release PR
6. Tag release after merge: `git tag v[VERSION]`
7. Publish to PyPI

## Documentation

### Types of Documentation
1. **API Documentation**: Docstrings in code
2. **User Guide**: README.md and examples
3. **Developer Guide**: This file
4. **Changelog**: CHANGELOG.md

### Documentation Standards
- Keep documentation up-to-date with code changes
- Use clear, concise language
- Include practical examples
- Test code examples to ensure they work

## Community Guidelines

### Code of Conduct
We are committed to providing a welcoming and inspiring community for all. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

### Communication
- Be respectful and constructive
- Ask questions if you're unsure
- Help others when you can
- Share knowledge and experiences

### Getting Help
- Check existing issues and documentation first
- Use GitHub Discussions for questions
- Create issues for bugs and feature requests
- Join our community channels

## Recognition

Contributors are recognized in several ways:
- Listed in `CONTRIBUTORS.md`
- Mentioned in release notes
- GitHub contributor statistics
- Special recognition for significant contributions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Fast Clean Architecture! 🚀