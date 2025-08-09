"""Package generator for creating directory structures and __init__.py files."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import jinja2
from rich.console import Console

from ..exceptions import TemplateError, ValidationError
from ..templates import TEMPLATES_DIR
from ..utils import ensure_directory


class PackageGenerator:
    """Generator for creating Python packages with proper __init__.py files."""

    def __init__(self, console: Optional[Console] = None):
        if console is None:
            raise ValueError(
                "Console dependency must be provided explicitly (Phase 3 Architecture Cleanup)"
            )
        self.console = console
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True,
        )

    def create_system_structure(
        self, base_path: Path, system_name: str, dry_run: bool = False
    ) -> None:
        """Create the complete system directory structure."""
        system_path = base_path / "systems" / system_name

        if dry_run:
            self.console.print(
                f"[yellow]DRY RUN:[/yellow] Would create system structure: {system_path}"
            )
            return

        # Create systems root if it doesn't exist
        systems_root = base_path / "systems"
        if not systems_root.exists():
            ensure_directory(systems_root)
            self._create_init_file(
                systems_root / "__init__.py",
                package_type="empty",
                package_description="Systems",
                context="fast-clean-architecture",
            )

        # Create system directory
        ensure_directory(system_path)

        # Create system __init__.py
        self._create_init_file(
            system_path / "__init__.py",
            package_type="system",
            system_name=system_name,
        )

        # Create main.py for system entry point
        main_content = f'"""\nMain entry point for {system_name} system.\n"""\n\n# System initialization and configuration\n'
        (system_path / "main.py").write_text(main_content, encoding="utf-8")

        self.console.print(f"✅ Created system structure: {system_path}")

    def create_module_structure(
        self,
        base_path: Path,
        system_name: str,
        module_name: str,
        api_version: Optional[str] = None,
        dry_run: bool = False,
    ) -> None:
        """Create the complete module directory structure."""
        module_path = base_path / "systems" / system_name / module_name

        if dry_run:
            self.console.print(
                f"[yellow]DRY RUN:[/yellow] Would create module structure: {module_path}"
            )
            return

        # Create module directory
        ensure_directory(module_path)

        # Create module __init__.py
        self._create_init_file(
            module_path / "__init__.py",
            package_type="module",
            module_name=module_name,
            system_name=system_name,
        )

        # Create enhanced layer directories with version-aware presentation layer
        layers: Dict[str, Dict[str, Any]] = {
            "domain": {
                "entities": [],
                "interfaces": [],  # Repository interfaces
                "value_objects": [],
                "events": [],  # Domain events
                "exceptions": [],  # Domain-specific exceptions
            },
            "application": {
                "use_cases": {
                    "commands": [],  # CQRS commands
                    "queries": [],  # CQRS queries
                },
                "services": [],
                "dtos": [],  # Data transfer objects
            },
            "infrastructure": {
                "database": {
                    "models": [],
                    "repositories": [],
                    "migrations": [],
                },
                "external": [],  # External service integrations
                "config": [],  # Module-specific configuration
            },
            "presentation": {
                "routes": [],
                "controllers": [],
                "schemas": [],
                "middleware": [],  # Module-specific middleware (version-agnostic)
            },
        }

        for layer_name, components in layers.items():
            layer_path = module_path / layer_name
            ensure_directory(layer_path)

            # Create layer __init__.py
            self._create_init_file(
                layer_path / "__init__.py",
                package_type="empty",
                package_description=layer_name.title(),
                context=f"{module_name} module",
            )

            # Handle nested component structures
            self._create_layer_components(
                layer_path, layer_name, components, module_name, api_version
            )

        # Create module API file
        module_content = f'"""\nModule registration for {module_name}.\n"""\n\n# Module configuration and dependencies\n'
        (module_path / f"{module_name}_module_api.py").write_text(
            module_content, encoding="utf-8"
        )

        self.console.print(
            f"✅ Created module structure: {module_path}{' with API version ' + api_version if api_version else ''}"
        )

    def _create_layer_components(
        self,
        layer_path: Path,
        layer_name: str,
        components: Dict[str, Any],
        module_name: str,
        api_version: Optional[str] = None,
    ) -> None:
        """Create component directories with support for nested structures and API versioning."""
        for component_type, component_config in components.items():
            component_path = layer_path / component_type
            ensure_directory(component_path)

            # Create component __init__.py
            self._create_init_file(
                component_path / "__init__.py",
                package_type="component",
                component_type=component_type,
                module_name=module_name,
                components=[],
            )

            # Handle nested structures (like use_cases with commands/queries)
            if isinstance(component_config, dict):
                for sub_component_type in component_config:
                    sub_component_path = component_path / sub_component_type
                    ensure_directory(sub_component_path)

                    self._create_init_file(
                        sub_component_path / "__init__.py",
                        package_type="component",
                        component_type=sub_component_type,
                        module_name=module_name,
                        components=[],
                    )

            # Special handling for presentation layer with API versioning
            if (
                layer_name == "presentation"
                and api_version
                and component_type in ["routes", "controllers", "schemas"]
            ):
                # Create version-specific subdirectory
                version_path = component_path / api_version
                ensure_directory(version_path)

                self._create_init_file(
                    version_path / "__init__.py",
                    package_type="component",
                    component_type=f"{component_type}_{api_version}",
                    module_name=module_name,
                    components=[],
                )

    def update_component_init(
        self,
        component_path: Path,
        component_type: str,
        module_name: str,
        components: List[Dict[str, str]],
    ) -> None:
        """Update component __init__.py with new imports."""
        init_path = component_path / "__init__.py"

        self._create_init_file(
            init_path,
            package_type="component",
            component_type=component_type,
            module_name=module_name,
            components=components,
        )

        self.console.print(f"📝 Updated {init_path}")

    def _create_init_file(self, file_path: Path, **template_vars: Any) -> None:
        """Create __init__.py file from template."""
        try:
            template = self.template_env.get_template("__init__.py.j2")
            content = template.render(**template_vars)

            file_path.write_text(content, encoding="utf-8")

        except jinja2.TemplateError as e:
            raise TemplateError(f"Error rendering __init__.py template: {e}")
        except Exception as e:
            raise TemplateError(f"Error creating __init__.py file: {e}")

    def migrate_to_api_versioning(
        self,
        base_path: Path,
        system_name: str,
        module_name: str,
        target_version: str,
        components: List[str],
        dry_run: bool = False,
        force: bool = False,
    ) -> None:
        """Migrate existing unversioned presentation layer files to API versioning.

        Args:
            base_path: Project root path
            system_name: System context name
            module_name: Module name
            target_version: Target API version (e.g., v1, v2)
            components: List of components to migrate (controllers, routes, schemas)
            dry_run: If True, only show what would be done
            force: If True, overwrite existing versioned files
        """
        module_path = base_path / "systems" / system_name / module_name
        presentation_path = module_path / "presentation"

        if not presentation_path.exists():
            raise ValidationError(f"Presentation layer not found: {presentation_path}")

        # Create backup before migration (unless dry run)
        if not dry_run:
            self._create_migration_backup(module_path)

        migrated_files = []
        conflicts = []

        for component in components:
            component_path = presentation_path / component

            if not component_path.exists():
                self.console.print(
                    f"[yellow]⚠️  Component '{component}' not found, skipping[/yellow]"
                )
                continue

            # Find files to migrate (exclude __init__.py and directories)
            files_to_migrate = [
                f
                for f in component_path.iterdir()
                if f.is_file() and f.suffix == ".py" and f.name != "__init__.py"
            ]

            if not files_to_migrate:
                self.console.print(
                    f"[yellow]ℹ️  No files to migrate in '{component}'[/yellow]"
                )
                continue

            # Check for existing versioned directory
            version_path = component_path / target_version
            if version_path.exists() and not force:
                existing_files = list(version_path.glob("*.py"))
                if existing_files:
                    conflicts.extend([(component, f.name) for f in existing_files])
                    continue

            if dry_run:
                self.console.print(
                    f"[cyan]📁 Would migrate {len(files_to_migrate)} files from {component}/ to {component}/{target_version}/[/cyan]"
                )
                for file_path in files_to_migrate:
                    self.console.print(f"  • {file_path.name}")
            else:
                # Create version directory
                ensure_directory(version_path)

                # Create version-specific __init__.py
                self._create_init_file(
                    version_path / "__init__.py",
                    package_type="component",
                    component_type=f"{component}_{target_version}",
                    module_name=module_name,
                    components=[],
                )

                # Move files
                for file_path in files_to_migrate:
                    target_file_path = version_path / file_path.name

                    # Read original content
                    original_content = file_path.read_text(encoding="utf-8")

                    # Update import statements
                    updated_content = self._update_imports_for_versioning(
                        original_content, component, target_version
                    )

                    # Write to new location
                    target_file_path.write_text(updated_content, encoding="utf-8")

                    # Remove original file
                    file_path.unlink()

                    migrated_files.append((component, file_path.name))
                    self.console.print(
                        f"[green]📦 Moved {component}/{file_path.name} → {component}/{target_version}/{file_path.name}[/green]"
                    )

        # Report conflicts
        if conflicts:
            self.console.print(
                "\n[red]⚠️  Conflicts detected (use --force to overwrite):[/red]"
            )
            for component, filename in conflicts:
                self.console.print(
                    f"  • {component}/{target_version}/{filename} already exists"
                )

            if not force:
                raise ValidationError(
                    "Migration aborted due to conflicts. Use --force to overwrite existing files."
                )

        # Summary
        if dry_run:
            total_files = sum(
                len(list((presentation_path / comp).glob("*.py"))) - 1
                for comp in components
                if (presentation_path / comp).exists()
            )  # -1 for __init__.py
            self.console.print(
                f"\n[yellow]DRY RUN SUMMARY:[/yellow] Would migrate {total_files} files to {target_version}"
            )
        else:
            if migrated_files:
                self.console.print(
                    f"\n[green]✅ Migration completed! Migrated {len(migrated_files)} files to {target_version}[/green]"
                )
            else:
                self.console.print("\n[yellow]ℹ️  No files were migrated[/yellow]")

    def _create_migration_backup(self, module_path: Path) -> None:
        """Create a backup of the module before migration."""
        import shutil
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{module_path.name}_backup_{timestamp}"
        backup_path = module_path.parent / backup_name

        try:
            shutil.copytree(module_path, backup_path)
            self.console.print(f"[blue]💾 Created backup: {backup_path}[/blue]")
        except Exception as e:
            self.console.print(f"[yellow]⚠️  Failed to create backup: {e}[/yellow]")

    def _update_imports_for_versioning(
        self, content: str, component: str, target_version: str
    ) -> str:
        """Update import statements in migrated files to account for new directory structure.

        This handles relative imports that might break after moving files to versioned directories.
        """
        import re

        lines = content.split("\n")
        updated_lines = []

        for line in lines:
            # Handle relative imports from sibling components
            # Example: from ..routes.user_routes import router
            # Should become: from ..routes.v1.user_routes import router

            # Pattern for relative imports to presentation layer components
            pattern = r"from \.\.([a-zA-Z_]+)\.([a-zA-Z_][a-zA-Z0-9_]*) import"
            match = re.search(pattern, line)

            if match:
                sibling_component = match.group(1)
                module_name = match.group(2)

                # Only update imports to components that support versioning
                if sibling_component in ["controllers", "routes", "schemas"]:
                    # Update the import to include version
                    updated_line = re.sub(
                        pattern,
                        f"from ..{sibling_component}.{target_version}.{module_name} import",
                        line,
                    )
                    updated_lines.append(updated_line)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        return "\n".join(updated_lines)

    def create_base_project_structure(
        self,
        base_path: Path,
        project_name: str,
        description: str,
        version: str,
        dependency_manager: str = "poetry",
        dry_run: bool = False,
    ) -> None:
        """Create a complete FastAPI project structure with Clean Architecture.

        Args:
            base_path: The directory where the project will be created
            project_name: Name of the project
            description: Project description
            version: Initial project version
            dry_run: If True, only show what would be created
        """
        if dry_run:
            self.console.print(
                f"[yellow]DRY RUN:[/yellow] Would create complete FastAPI project: {base_path}"
            )
            return

        # Create the main project directory
        ensure_directory(base_path)

        # Create core directory structure
        core_dirs = ["core", "systems", "shared", "tests", "docs", "scripts"]

        for dir_name in core_dirs:
            dir_path = base_path / dir_name
            ensure_directory(dir_path)
            if dir_name in ["systems", "shared", "tests"]:
                self._create_init_file(
                    dir_path / "__init__.py",
                    package_type="empty",
                    package_description=dir_name.title(),
                    context="fast-clean-architecture",
                )

        # Create enhanced docs structure
        self._create_enhanced_docs_structure(base_path)

        # Create enhanced shared infrastructure structure
        self._create_enhanced_shared_structure(base_path)

        # Create core application files
        self._create_core_files(base_path, project_name, description, version)

        # Create configuration files
        self._create_config_files(
            base_path, project_name, description, version, dependency_manager
        )

        # Create documentation files
        self._create_docs_files(
            base_path, project_name, description, dependency_manager
        )

        self.console.print(
            f"[green]✅ Complete FastAPI project structure created at {base_path}[/green]"
        )

    def _create_core_files(
        self, base_path: Path, project_name: str, description: str, version: str
    ) -> None:
        """Create core application files."""
        core_path = base_path / "core"

        # Create main.py
        main_content = '''"""Main application entry point for {{ project_name }}."""\n\nfrom fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware\n\n\ndef create_app() -> FastAPI:\n    """Create and configure the FastAPI application."""\n    app = FastAPI(\n        title="{{ project_name }}",\n        description="{{ description }}",\n        version="{{ version }}",\n        docs_url="/docs",\n        redoc_url="/redoc"\n    )\n    \n    # Add CORS middleware\n    app.add_middleware(\n        CORSMiddleware,\n        allow_origins=["*"],\n        allow_credentials=True,\n        allow_methods=["*"],\n        allow_headers=["*"],\n    )\n    \n    @app.get("/health")\n    async def health_check():\n        """Health check endpoint."""\n        return {"status": "healthy", "version": "{{ version }}"}\n    \n    return app\n\n\napp = create_app()\n\n\nif __name__ == "__main__":\n    import uvicorn\n    uvicorn.run(app, host="0.0.0.0", port=8000)\n'''

        template = self.template_env.from_string(main_content)
        rendered_content = template.render(
            project_name=project_name, description=description, version=version
        )

        with open(core_path / "main.py", "w") as f:
            f.write(rendered_content)

        # Create __init__.py for core
        self._create_init_file(
            core_path / "__init__.py",
            package_type="empty",
            package_description="Core application",
            context="fast-clean-architecture",
        )

    def _create_config_files(
        self,
        base_path: Path,
        project_name: str,
        description: str,
        version: str,
        dependency_manager: str = "poetry",
    ) -> None:
        """Create configuration files based on dependency manager choice."""

        if dependency_manager.lower() == "poetry":
            self._create_poetry_config(base_path, project_name, description, version)
        else:
            self._create_pip_config(base_path)

        # Create other config files
        self._create_common_config_files(base_path)

    def _create_poetry_config(
        self, base_path: Path, project_name: str, description: str, version: str
    ) -> None:
        """Create Poetry configuration (pyproject.toml)."""

        # Create pyproject.toml
        pyproject_content = """[tool.poetry]
name = "{{ project_name }}"
version = "{{ version }}"
description = "{{ description }}"
authors = ["Your Name <your.email@example.com>"]
readme = "README.md"
packages = [{include = "core"}]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
sqlalchemy = "^2.0.0"
alembic = "^1.13.0"
psycopg2-binary = "^2.9.0"
redis = "^5.0.0"
python-multipart = "^0.0.6"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^1.1.0"
httpx = "^0.25.0"
rich = "^13.7.0"
black = "^23.0.0"
isort = "^5.12.0"
flake8 = "^6.0.0"
mypy = "^1.7.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 88
target-version = ["py311"]
include = "\\\\.pyi?$"

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q"
testpaths = [
    "tests",
]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
"""

        template = self.template_env.from_string(pyproject_content)
        rendered_content = template.render(
            project_name=project_name, description=description, version=version
        )

        with open(base_path / "pyproject.toml", "w") as f:
            f.write(rendered_content)

    def _create_pip_config(self, base_path: Path) -> None:
        """Create pip configuration (requirements.txt)."""

        # Create requirements.txt
        requirements_content = """# Core FastAPI dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
alembic==1.13.1
psycopg2-binary==2.9.9

# Cache
redis==5.0.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Development dependencies (install with: pip install -r requirements-dev.txt)
# pytest==7.4.3
# pytest-asyncio==1.1.0
# httpx==0.25.2
# black==23.11.0
# isort==5.12.0
# flake8==6.1.0
# mypy==1.7.1
"""

        with open(base_path / "requirements.txt", "w") as f:
            f.write(requirements_content)

        # Create requirements-dev.txt
        dev_requirements_content = """# Development dependencies
pytest==7.4.3
pytest-asyncio==1.1.0
httpx==0.25.2
black==23.11.0
isort==5.12.0
flake8==6.1.0
mypy==1.7.1
rich==13.7.0
"""

        with open(base_path / "requirements-dev.txt", "w") as f:
            f.write(dev_requirements_content)

    def _create_common_config_files(self, base_path: Path) -> None:
        """Create common configuration files (.env.example, .gitignore)."""

        # Create .env.example
        env_content = """# Database Configuration\nDATABASE_URL=postgresql://user:password@localhost:5432/{{ project_name }}_db\n\n# Redis Configuration\nREDIS_URL=redis://localhost:6379/0\n\n# Security\nSECRET_KEY=your-secret-key-here\nALGORITHM=HS256\nACCESS_TOKEN_EXPIRE_MINUTES=30\n\n# Environment\nENVIRONMENT=development\nDEBUG=true\n\n# API Configuration\nAPI_V1_STR=/api/v1\nPROJECT_NAME={{ project_name }}\n"""

        template = self.template_env.from_string(env_content)
        rendered_content = template.render(project_name=base_path.name)

        with open(base_path / ".env.example", "w") as f:
            f.write(rendered_content)

        # Create .gitignore
        gitignore_content = """# Python\n__pycache__/\n*.py[cod]\n*$py.class\n*.so\n.Python\nbuild/\ndevelop-eggs/\ndist/\ndownloads/\neggs/\n.eggs/\nlib/\nlib64/\nparts/\nsdist/\nvar/\nwheels/\n*.egg-info/\n.installed.cfg\n*.egg\nPIPFILE.lock\n\n# Environment\n.env\n.venv\nenv/\nvenv/\nENV/\nenv.bak/\nvenv.bak/\n\n# IDE\n.vscode/\n.idea/\n*.swp\n*.swo\n*~\n\n# Database\n*.db\n*.sqlite3\n\n# Logs\n*.log\nlogs/\n\n# Testing\n.coverage\n.pytest_cache/\n.tox/\nhtmlcov/\n\n# OS\n.DS_Store\nThumbs.db\n"""

        with open(base_path / ".gitignore", "w") as f:
            f.write(gitignore_content)

    def _create_docs_files(
        self,
        base_path: Path,
        project_name: str,
        description: str,
        dependency_manager: str = "poetry",
    ) -> None:
        """Create documentation files."""

        # Create README.md based on dependency manager
        if dependency_manager.lower() == "poetry":
            readme_content = self._get_poetry_readme_template()
        else:
            readme_content = self._get_pip_readme_template()

        template = self.template_env.from_string(readme_content)
        rendered_content = template.render(
            project_name=project_name, description=description
        )

        with open(base_path / "README.md", "w") as f:
            f.write(rendered_content)

    def _get_poetry_readme_template(self) -> str:
        """Get README template for Poetry projects."""
        return """# {{ project_name }}\n\n{{ description }}\n\n## Quick Start\n\n### Prerequisites\n\n- Python 3.11+\n- Poetry (install from [python-poetry.org](https://python-poetry.org/docs/#installation))\n\n### Setup\n\n1. Install dependencies:\n   ```bash\n   poetry install\n   ```\n\n2. Set up environment:\n   ```bash\n   cp .env.example .env\n   # Edit .env with your configuration\n   ```\n\n3. Activate the virtual environment:\n   ```bash\n   poetry shell\n   ```\n\n4. Run the application:\n   ```bash\n   cd core\n   python main.py\n   ```\n   \n   Or using Poetry:\n   ```bash\n   poetry run python core/main.py\n   ```\n\n5. Open your browser to [http://localhost:8000/docs](http://localhost:8000/docs)\n\n## Project Structure\n\n```\n{{ project_name }}/\n├── core/                 # Core application\n│   └── main.py          # FastAPI application\n├── systems/             # Business systems\n├── shared/              # Shared utilities\n├── tests/               # Test files\n├── docs/                # Documentation\n├── scripts/             # Utility scripts\n├── pyproject.toml       # Poetry configuration\n├── .env.example        # Environment template\n└── README.md           # This file\n```\n\n## Development\n\n### Code Quality Tools\n\nThis project includes several development tools configured in `pyproject.toml`:\n\n```bash\n# Format code\npoetry run black .\n\n# Sort imports\npoetry run isort .\n\n# Lint code\npoetry run flake8\n\n# Type checking\npoetry run mypy core/\n\n# Run tests\npoetry run pytest\n```\n\n### Adding New Systems\n\nUse the FCA CLI to add new systems:\n\n```bash\nfca-scaffold create-system-context user_management\n```\n\n### Adding New Modules\n\n```bash\nfca-scaffold create-module authentication --system user_management\n```\n\n### Adding Components\n\n```bash\nfca-scaffold create-component user --module authentication --layer domain\n```\n\n## API Documentation\n\n- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)\n- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)\n\n## License\n\nMIT License\n"""

    def _get_pip_readme_template(self) -> str:
        """Get README template for pip projects."""
        return """# {{ project_name }}\n\n{{ description }}\n\n## Quick Start\n\n### Prerequisites\n\n- Python 3.11+\n- pip (comes with Python)\n\n### Setup\n\n1. Create and activate virtual environment:\n   ```bash\n   python -m venv venv\n   \n   # On Linux/Mac:\n   source venv/bin/activate\n   \n   # On Windows:\n   venv\\Scripts\\activate\n   ```\n\n2. Install dependencies:\n   ```bash\n   pip install -r requirements.txt\n   ```\n\n3. Install development dependencies (optional):\n   ```bash\n   pip install -r requirements-dev.txt\n   ```\n\n4. Set up environment:\n   ```bash\n   cp .env.example .env\n   # Edit .env with your configuration\n   ```\n\n5. Run the application:\n   ```bash\n   python core/main.py\n   ```\n\n6. Open your browser to [http://localhost:8000/docs](http://localhost:8000/docs)\n\n## Project Structure\n\n```\n{{ project_name }}/\n├── core/                 # Core application\n│   └── main.py          # FastAPI application\n├── systems/             # Business systems\n├── shared/              # Shared utilities\n├── tests/               # Test files\n├── docs/                # Documentation\n├── scripts/             # Utility scripts\n├── requirements.txt     # Production dependencies\n├── requirements-dev.txt # Development dependencies\n├── .env.example        # Environment template\n└── README.md           # This file\n```\n\n## Development\n\n### Code Quality Tools\n\nThis project includes development dependencies for code quality:\n\n```bash\n# Format code\nblack .\n\n# Sort imports\nisort .\n\n# Lint code\nflake8\n\n# Type checking\nmypy core/\n\n# Run tests\npytest\n```\n\n### Adding New Systems\n\nUse the FCA CLI to add new systems:\n\n```bash\nfca-scaffold create-system-context user_management\n```\n\n### Adding New Modules\n\n```bash\nfca-scaffold create-module authentication --system user_management\n```\n\n### Adding Components\n\n```bash\nfca-scaffold create-component user --module authentication --layer domain\n```\n\n## API Documentation\n\n- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)\n- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)\n\n## License\n\nMIT License
"""

    def _create_enhanced_docs_structure(self, base_path: Path) -> None:
        """Create enhanced docs structure with schemas and examples."""
        docs_path = base_path / "docs"

        # Create __init__.py for docs
        self._create_init_file(
            docs_path / "__init__.py",
            package_type="empty",
            package_description="Documentation",
            context="fast-clean-architecture",
        )

        # Create schemas directory
        schemas_path = docs_path / "schemas"
        ensure_directory(schemas_path)
        self._create_init_file(
            schemas_path / "__init__.py",
            package_type="empty",
            package_description="API Schemas Documentation",
            context="fast-clean-architecture",
        )

        # Create examples directory
        examples_path = docs_path / "examples"
        ensure_directory(examples_path)
        self._create_init_file(
            examples_path / "__init__.py",
            package_type="empty",
            package_description="Code Examples",
            context="fast-clean-architecture",
        )

    def _create_enhanced_shared_structure(self, base_path: Path) -> None:
        """Create enhanced shared infrastructure structure."""
        shared_path = base_path / "shared"

        # Create infrastructure directory
        infrastructure_path = shared_path / "infrastructure"
        ensure_directory(infrastructure_path)
        self._create_init_file(
            infrastructure_path / "__init__.py",
            package_type="empty",
            package_description="Shared Infrastructure",
            context="fast-clean-architecture",
        )

        # Create infrastructure subdirectories with implementation files
        self._create_config_infrastructure(infrastructure_path)
        self._create_database_infrastructure(infrastructure_path)
        self._create_cache_infrastructure(infrastructure_path)
        self._create_logging_infrastructure(infrastructure_path)
        self._create_middleware_infrastructure(infrastructure_path)

    def _create_config_infrastructure(self, infrastructure_path: Path) -> None:
        """Create configuration infrastructure with implementation files."""
        config_path = infrastructure_path / "config"
        ensure_directory(config_path)

        self._create_init_file(
            config_path / "__init__.py",
            package_type="config",
            package_description="Configuration modules",
            context="shared infrastructure",
            imports=[
                "from .database import DatabaseConfig, get_database_config",
                "from .settings import (",
                "    AppSettings,",
                "    Environment,",
                "    LogLevel,",
                "    get_settings,",
                "    reload_settings,",
                ")",
                "from .environment import (",
                "    EnvironmentConfig,",
                "    EnvironmentManager,",
                "    EnvironmentType,",
                "    get_environment_manager,",
                "    get_env,",
                "    get_current_environment,",
                "    is_production,",
                "    is_development,",
                ")",
                "from .security import (",
                "    SecurityConfig,",
                "    PasswordManager,",
                "    JWTManager,",
                "    get_security_config,",
                "    get_password_manager,",
                "    get_jwt_manager,",
                "    generate_secure_token,",
                "    hash_string,",
                ")",
            ],
            exports=[
                "# Database",
                '"DatabaseConfig",',
                '"get_database_config",',
                "# Settings",
                '"AppSettings",',
                '"Environment",',
                '"LogLevel",',
                '"get_settings",',
                '"reload_settings",',
                "# Environment",
                '"EnvironmentConfig",',
                '"EnvironmentManager",',
                '"EnvironmentType",',
                '"get_environment_manager",',
                '"get_env",',
                '"get_current_environment",',
                '"is_production",',
                '"is_development",',
                "# Security",
                '"SecurityConfig",',
                '"PasswordManager",',
                '"JWTManager",',
                '"get_security_config",',
                '"get_password_manager",',
                '"get_jwt_manager",',
                '"generate_secure_token",',
                '"hash_string",',
            ],
        )

        # Create database.py
        database_config = '''"""Database configuration module.

Provides database connection settings and configuration management.
Modify the settings according to your database requirements.
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field


class DatabaseConfig(BaseSettings):
    """Database configuration settings.
    
    Attributes:
        database_url: Complete database connection URL
        pool_size: Connection pool size (default: 10)
        max_overflow: Maximum overflow connections (default: 20)
        pool_timeout: Connection timeout in seconds (default: 30)
        pool_recycle: Connection recycle time in seconds (default: 3600)
        echo: Enable SQL query logging (default: False)
    """
    
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/app_db",
        env="DATABASE_URL",
        description="Database connection URL"
    )
    pool_size: int = Field(
        default=10,
        env="DB_POOL_SIZE",
        description="Database connection pool size"
    )
    max_overflow: int = Field(
        default=20,
        env="DB_MAX_OVERFLOW",
        description="Maximum overflow connections"
    )
    pool_timeout: int = Field(
        default=30,
        env="DB_POOL_TIMEOUT",
        description="Connection timeout in seconds"
    )
    pool_recycle: int = Field(
        default=3600,
        env="DB_POOL_RECYCLE",
        description="Connection recycle time in seconds"
    )
    echo: bool = Field(
        default=False,
        env="DB_ECHO",
        description="Enable SQL query logging"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_database_config() -> DatabaseConfig:
    """Get database configuration instance.
    
    Returns:
        DatabaseConfig: Configured database settings
    """
    return DatabaseConfig()
'''

        with open(config_path / "database.py", "w") as f:
            f.write(database_config)

        # Create settings.py
        settings_config = '''"""Application settings configuration.

Provides centralized application settings and configuration management.
Customize according to your application requirements.
"""

import os
from typing import List, Optional, Dict, Any
from pydantic import BaseSettings, Field, validator
from enum import Enum


class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Logging level types."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AppSettings(BaseSettings):
    """Application settings configuration.
    
    Centralized configuration for the entire application.
    All settings can be overridden via environment variables.
    """
    
    # Application Info
    app_name: str = Field(
        default="FastCleanArchitecture App",
        env="APP_NAME",
        description="Application name"
    )
    app_version: str = Field(
        default="1.0.0",
        env="APP_VERSION",
        description="Application version"
    )
    app_description: str = Field(
        default="A FastAPI application built with Clean Architecture",
        env="APP_DESCRIPTION",
        description="Application description"
    )
    
    # Environment
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        env="ENVIRONMENT",
        description="Application environment"
    )
    debug: bool = Field(
        default=True,
        env="DEBUG",
        description="Enable debug mode"
    )
    
    # Server Configuration
    host: str = Field(
        default="0.0.0.0",
        env="HOST",
        description="Server host"
    )
    port: int = Field(
        default=8000,
        env="PORT",
        description="Server port"
    )
    reload: bool = Field(
        default=True,
        env="RELOAD",
        description="Enable auto-reload in development"
    )
    
    # API Configuration
    api_prefix: str = Field(
        default="/api/v1",
        env="API_PREFIX",
        description="API URL prefix"
    )
    docs_url: Optional[str] = Field(
        default="/docs",
        env="DOCS_URL",
        description="API documentation URL"
    )
    redoc_url: Optional[str] = Field(
        default="/redoc",
        env="REDOC_URL",
        description="ReDoc documentation URL"
    )
    openapi_url: Optional[str] = Field(
        default="/openapi.json",
        env="OPENAPI_URL",
        description="OpenAPI schema URL"
    )
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY",
        description="Secret key for JWT and other cryptographic operations"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES",
        description="Access token expiration time in minutes"
    )
    
    # CORS
    allowed_hosts: List[str] = Field(
        default=["*"],
        env="ALLOWED_HOSTS",
        description="Allowed hosts for CORS"
    )
    
    # Logging
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        env="LOG_LEVEL",
        description="Logging level"
    )
    log_file: Optional[str] = Field(
        default=None,
        env="LOG_FILE",
        description="Log file path"
    )
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(
        default=False,
        env="RATE_LIMIT_ENABLED",
        description="Enable rate limiting"
    )
    rate_limit_requests: int = Field(
        default=100,
        env="RATE_LIMIT_REQUESTS",
        description="Rate limit requests per minute"
    )
    
    # Monitoring
    enable_metrics: bool = Field(
        default=True,
        env="ENABLE_METRICS",
        description="Enable application metrics"
    )
    enable_health_check: bool = Field(
        default=True,
        env="ENABLE_HEALTH_CHECK",
        description="Enable health check endpoint"
    )
    
    @validator("environment", pre=True)
    def validate_environment(cls, v):
        """Validate environment value."""
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    @validator("debug")
    def validate_debug_for_production(cls, v, values):
        """Ensure debug is False in production."""
        if values.get("environment") == Environment.PRODUCTION and v:
            raise ValueError("Debug mode cannot be enabled in production")
        return v
    
    @validator("secret_key")
    def validate_secret_key(cls, v, values):
        """Validate secret key for production."""
        if values.get("environment") == Environment.PRODUCTION:
            if v == "your-secret-key-change-in-production":
                raise ValueError("Secret key must be changed in production")
            if len(v) < 32:
                raise ValueError("Secret key must be at least 32 characters long")
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.environment == Environment.TESTING
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        use_enum_values = True


# Global settings instance
_settings: Optional[AppSettings] = None


def get_settings() -> AppSettings:
    """Get application settings instance.
    
    Returns:
        AppSettings: Application settings
    """
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings


def reload_settings() -> AppSettings:
    """Reload application settings.
    
    Returns:
        AppSettings: Reloaded application settings
    """
    global _settings
    _settings = None
    return get_settings()
'''

        with open(config_path / "settings.py", "w") as f:
            f.write(settings_config)

        # Create environment.py
        environment_config = '''"""Environment configuration management.

Provides environment-specific configuration loading and validation.
Supports multiple environments with proper validation.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseSettings, Field
from enum import Enum


class EnvironmentType(str, Enum):
    """Supported environment types."""
    LOCAL = "local"
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentConfig(BaseSettings):
    """Environment-specific configuration.
    
    Manages environment variables and configuration files
    for different deployment environments.
    """
    
    # Environment identification
    env_name: EnvironmentType = Field(
        default=EnvironmentType.DEVELOPMENT,
        env="ENV_NAME",
        description="Current environment name"
    )
    
    # Configuration file paths
    config_dir: str = Field(
        default="config",
        env="CONFIG_DIR",
        description="Configuration directory path"
    )
    
    env_file: str = Field(
        default=".env",
        env="ENV_FILE",
        description="Environment file path"
    )
    
    # Environment-specific settings
    load_dotenv: bool = Field(
        default=True,
        env="LOAD_DOTENV",
        description="Load .env file"
    )
    
    validate_config: bool = Field(
        default=True,
        env="VALIDATE_CONFIG",
        description="Validate configuration on load"
    )
    
    # Environment variables prefix
    env_prefix: str = Field(
        default="APP_",
        env="ENV_PREFIX",
        description="Environment variables prefix"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        use_enum_values = True


class EnvironmentManager:
    """Environment configuration manager.
    
    Handles loading and validation of environment-specific configurations.
    """
    
    def __init__(self, config: EnvironmentConfig = None):
        """Initialize environment manager.
        
        Args:
            config: Environment configuration
        """
        if config is None:
            raise ValueError("EnvironmentConfig dependency must be provided explicitly (Phase 3 Architecture Cleanup)")
        self.config = config
        self._env_vars: Dict[str, Any] = {}
        self._config_files: Dict[str, Path] = {}
        
        self._discover_config_files()
        self._load_environment_variables()
    
    def _discover_config_files(self) -> None:
        """Discover configuration files for current environment."""
        config_dir = Path(self.config.config_dir)
        
        # Standard configuration files
        config_files = {
            "base": config_dir / "base.env",
            "environment": config_dir / f"{self.config.env_name.value}.env",
            "local": config_dir / "local.env",
            "secrets": config_dir / "secrets.env"
        }
        
        # Filter existing files
        self._config_files = {
            name: path for name, path in config_files.items()
            if path.exists()
        }
    
    def _load_environment_variables(self) -> None:
        """Load environment variables from various sources."""
        # Load from system environment
        self._env_vars.update(os.environ)
        
        # Load from configuration files in order
        load_order = ["base", "environment", "local", "secrets"]
        
        for config_name in load_order:
            if config_name in self._config_files:
                self._load_env_file(self._config_files[config_name])
    
    def _load_env_file(self, file_path: Path) -> None:
        """Load environment variables from file.
        
        Args:
            file_path: Path to environment file
        """
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        self._env_vars[key] = value
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get environment variable value.
        
        Args:
            key: Environment variable key
            default: Default value if key not found
        
        Returns:
            Environment variable value
        """
        # Try with prefix first
        prefixed_key = f"{self.config.env_prefix}{key}"
        if prefixed_key in self._env_vars:
            return self._env_vars[prefixed_key]
        
        # Try without prefix
        if key in self._env_vars:
            return self._env_vars[key]
        
        return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable.
        
        Args:
            key: Environment variable key
            default: Default boolean value
        
        Returns:
            Boolean value
        """
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer environment variable.
        
        Args:
            key: Environment variable key
            default: Default integer value
        
        Returns:
            Integer value
        """
        value = self.get(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def get_list(self, key: str, separator: str = ",", default: List[str] = None) -> List[str]:
        """Get list environment variable.
        
        Args:
            key: Environment variable key
            separator: List item separator
            default: Default list value
        
        Returns:
            List of strings
        """
        if default is None:
            default = []
        
        value = self.get(key)
        if value is None:
            return default
        
        if isinstance(value, list):
            return value
        
        if isinstance(value, str):
            return [item.strip() for item in value.split(separator) if item.strip()]
        
        return default
    
    def is_environment(self, env_type: EnvironmentType) -> bool:
        """Check if current environment matches type.
        
        Args:
            env_type: Environment type to check
        
        Returns:
            True if environment matches
        """
        return self.config.env_name == env_type
    
    def get_all_vars(self) -> Dict[str, Any]:
        """Get all environment variables.
        
        Returns:
            Dictionary of all environment variables
        """
        return self._env_vars.copy()
    
    def validate_required_vars(self, required_vars: List[str]) -> None:
        """Validate that required environment variables are set.
        
        Args:
            required_vars: List of required variable names
        
        Raises:
            ValueError: If required variables are missing
        """
        missing_vars = []
        
        for var in required_vars:
            if self.get(var) is None:
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")


# Global environment manager instance
_env_manager: Optional[EnvironmentManager] = None


def get_environment_manager() -> EnvironmentManager:
    """Get global environment manager instance.
    
    Returns:
        EnvironmentManager: Environment manager instance
    """
    global _env_manager
    if _env_manager is None:
        _env_manager = EnvironmentManager()
    return _env_manager


def get_env(key: str, default: Any = None) -> Any:
    """Get environment variable value.
    
    Args:
        key: Environment variable key
        default: Default value
    
    Returns:
        Environment variable value
    """
    return get_environment_manager().get(key, default)


def get_current_environment() -> EnvironmentType:
    """Get current environment type.
    
    Returns:
        EnvironmentType: Current environment
    """
    return get_environment_manager().config.env_name


def is_production() -> bool:
    """Check if running in production.
    
    Returns:
        True if production environment
    """
    return get_current_environment() == EnvironmentType.PRODUCTION


def is_development() -> bool:
    """Check if running in development.
    
    Returns:
        True if development environment
    """
    return get_current_environment() == EnvironmentType.DEVELOPMENT
'''

        with open(config_path / "environment.py", "w") as f:
            f.write(environment_config)

        # Create security.py
        security_config = '''"""Security configuration and utilities.

Provides security-related configuration and utility functions.
Includes password hashing, JWT handling, and security settings.
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseSettings, Field, validator


class SecurityConfig(BaseSettings):
    """Security configuration settings.
    
    Centralized security configuration for authentication,
    authorization, and cryptographic operations.
    """
    
    # JWT Configuration
    secret_key: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        env="SECRET_KEY",
        description="Secret key for JWT signing"
    )
    algorithm: str = Field(
        default="HS256",
        env="JWT_ALGORITHM",
        description="JWT signing algorithm"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES",
        description="Access token expiration time in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        env="REFRESH_TOKEN_EXPIRE_DAYS",
        description="Refresh token expiration time in days"
    )
    
    # Password Configuration
    password_min_length: int = Field(
        default=8,
        env="PASSWORD_MIN_LENGTH",
        description="Minimum password length"
    )
    password_require_uppercase: bool = Field(
        default=True,
        env="PASSWORD_REQUIRE_UPPERCASE",
        description="Require uppercase letters in password"
    )
    password_require_lowercase: bool = Field(
        default=True,
        env="PASSWORD_REQUIRE_LOWERCASE",
        description="Require lowercase letters in password"
    )
    password_require_numbers: bool = Field(
        default=True,
        env="PASSWORD_REQUIRE_NUMBERS",
        description="Require numbers in password"
    )
    password_require_special: bool = Field(
        default=True,
        env="PASSWORD_REQUIRE_SPECIAL",
        description="Require special characters in password"
    )
    
    # Session Configuration
    session_expire_minutes: int = Field(
        default=60,
        env="SESSION_EXPIRE_MINUTES",
        description="Session expiration time in minutes"
    )
    max_login_attempts: int = Field(
        default=5,
        env="MAX_LOGIN_ATTEMPTS",
        description="Maximum login attempts before lockout"
    )
    lockout_duration_minutes: int = Field(
        default=15,
        env="LOCKOUT_DURATION_MINUTES",
        description="Account lockout duration in minutes"
    )
    
    # CORS Security
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000"],
        env="ALLOWED_ORIGINS",
        description="Allowed CORS origins"
    )
    allowed_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE"],
        env="ALLOWED_METHODS",
        description="Allowed HTTP methods"
    )
    allowed_headers: List[str] = Field(
        default=["Authorization", "Content-Type"],
        env="ALLOWED_HEADERS",
        description="Allowed HTTP headers"
    )
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(
        default=True,
        env="RATE_LIMIT_ENABLED",
        description="Enable rate limiting"
    )
    rate_limit_requests_per_minute: int = Field(
        default=60,
        env="RATE_LIMIT_REQUESTS_PER_MINUTE",
        description="Rate limit requests per minute"
    )
    
    @validator("secret_key")
    def validate_secret_key(cls, v):
        """Validate secret key strength."""
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v
    
    @validator("algorithm")
    def validate_algorithm(cls, v):
        """Validate JWT algorithm."""
        allowed_algorithms = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
        if v not in allowed_algorithms:
            raise ValueError(f"Algorithm must be one of: {allowed_algorithms}")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class PasswordManager:
    """Password hashing and validation manager."""
    
    def __init__(self, config: SecurityConfig = None):
        """Initialize password manager.
        
        Args:
            config: Security configuration
        """
        if config is None:
            raise ValueError("SecurityConfig dependency must be provided explicitly (Phase 3 Architecture Cleanup)")
        self.config = config
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """Hash a password.
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password
        """
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
        
        Returns:
            True if password matches
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength.
        
        Args:
            password: Password to validate
        
        Returns:
            Validation result with details
        """
        errors = []
        
        if len(password) < self.config.password_min_length:
            errors.append(f"Password must be at least {self.config.password_min_length} characters long")
        
        if self.config.password_require_uppercase and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.config.password_require_lowercase and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.config.password_require_numbers and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number")
        
        if self.config.password_require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            errors.append("Password must contain at least one special character")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "strength_score": self._calculate_strength_score(password)
        }
    
    def _calculate_strength_score(self, password: str) -> int:
        """Calculate password strength score (0-100).
        
        Args:
            password: Password to score
        
        Returns:
            Strength score
        """
        score = 0
        
        # Length score (up to 25 points)
        score += min(25, len(password) * 2)
        
        # Character variety (up to 75 points)
        if any(c.isupper() for c in password):
            score += 15
        if any(c.islower() for c in password):
            score += 15
        if any(c.isdigit() for c in password):
            score += 15
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 15
        
        # Uniqueness bonus (up to 15 points)
        unique_chars = len(set(password))
        score += min(15, unique_chars)
        
        return min(100, score)


class JWTManager:
    """JWT token management."""
    
    def __init__(self, config: SecurityConfig = None):
        """Initialize JWT manager.
        
        Args:
            config: Security configuration
        """
        if config is None:
            raise ValueError("SecurityConfig dependency must be provided explicitly (Phase 3 Architecture Cleanup)")
        self.config = config
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create access token.
        
        Args:
            data: Token payload data
            expires_delta: Custom expiration time
        
        Returns:
            JWT access token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.config.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        return jwt.encode(to_encode, self.config.secret_key, algorithm=self.config.algorithm)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create refresh token.
        
        Args:
            data: Token payload data
        
        Returns:
            JWT refresh token
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=self.config.refresh_token_expire_days)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        
        return jwt.encode(to_encode, self.config.secret_key, algorithm=self.config.algorithm)
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify and decode token.
        
        Args:
            token: JWT token
            token_type: Expected token type
        
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.config.secret_key, algorithms=[self.config.algorithm])
            
            if payload.get("type") != token_type:
                return None
            
            return payload
        except JWTError:
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired.
        
        Args:
            token: JWT token
        
        Returns:
            True if token is expired
        """
        try:
            payload = jwt.decode(token, self.config.secret_key, algorithms=[self.config.algorithm], options={"verify_exp": False})
            exp = payload.get("exp")
            
            if exp is None:
                return True
            
            return datetime.now(timezone.utc) > datetime.fromtimestamp(exp, tz=timezone.utc)
        except JWTError:
            return True


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token.
    
    Args:
        length: Token length
    
    Returns:
        Secure random token
    """
    return secrets.token_urlsafe(length)


def hash_string(value: str, salt: str = "") -> str:
    """Hash a string value.
    
    Args:
        value: String to hash
        salt: Optional salt
    
    Returns:
        Hashed string
    """
    return hashlib.sha256(f"{value}{salt}".encode()).hexdigest()


# Global instances
_security_config: Optional[SecurityConfig] = None
_password_manager: Optional[PasswordManager] = None
_jwt_manager: Optional[JWTManager] = None


def get_security_config() -> SecurityConfig:
    """Get security configuration instance.
    
    Returns:
        SecurityConfig: Security configuration
    """
    global _security_config
    if _security_config is None:
        _security_config = SecurityConfig()
    return _security_config


def get_password_manager() -> PasswordManager:
    """Get password manager instance.
    
    Returns:
        PasswordManager: Password manager
    """
    global _password_manager
    if _password_manager is None:
        _password_manager = PasswordManager()
    return _password_manager


def get_jwt_manager() -> JWTManager:
    """Get JWT manager instance.
    
    Returns:
        JWTManager: JWT manager
    """
    global _jwt_manager
    if _jwt_manager is None:
        _jwt_manager = JWTManager()
    return _jwt_manager
'''

        with open(config_path / "security.py", "w") as f:
            f.write(security_config)

    def _create_logging_config(self, config_path: Path) -> None:
        """Create logging configuration files.

        Args:
            config_path: Path to the logging configuration directory
        """
        logging_config = '''"""Logging configuration module.

Provides centralized logging configuration for the application.
Customize log levels, formats, and handlers as needed.
"""

import logging
import sys
from typing import Dict, Any
from pydantic import BaseSettings, Field


class LoggingConfig(BaseSettings):
    """Logging configuration settings.
    
    Attributes:
        log_level: Logging level (default: INFO)
        log_format: Log message format
        log_file: Optional log file path
        enable_console: Enable console logging (default: True)
        enable_file: Enable file logging (default: False)
    """
    
    log_level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Logging level"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT",
        description="Log message format"
    )
    log_file: str = Field(
        default="",
        env="LOG_FILE",
        description="Log file path"
    )
    enable_console: bool = Field(
        default=True,
        env="LOG_ENABLE_CONSOLE",
        description="Enable console logging"
    )
    enable_file: bool = Field(
        default=False,
        env="LOG_ENABLE_FILE",
        description="Enable file logging"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def configure_logging(config: LoggingConfig = None) -> None:
    """Configure application logging.
    
    Args:
        config: Logging configuration (optional)
    """
    if config is None:
        config = LoggingConfig()
    
    # Create formatter
    formatter = logging.Formatter(config.log_format)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    if config.enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if config.enable_file and config.log_file:
        file_handler = logging.FileHandler(config.log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def get_logging_config() -> LoggingConfig:
    """Get logging configuration instance.
    
    Returns:
        LoggingConfig: Configured logging settings
    """
    return LoggingConfig()
'''

        with open(config_path / "logging.py", "w") as f:
            f.write(logging_config)

        # Create __init__.py
        init_content = '''"""Middleware infrastructure module."""

from .middleware import (
    MiddlewareConfig,
    CORSMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    get_middleware_config,
    create_middleware_stack
)
from .auth_middleware import (
    JWTAuthMiddleware,
    RoleBasedAuthMiddleware,
    AuthenticationError,
    AuthorizationError,
    create_auth_middleware,
    create_role_middleware
)
from .cors_middleware import (
    CORSConfig,
    CORSMiddleware as CORSMiddlewareStandalone,
    create_cors_middleware,
    create_permissive_cors,
    create_restrictive_cors
)

__all__ = [
    # Core middleware
    "MiddlewareConfig",
    "CORSMiddleware",
    "RateLimitMiddleware",
    "RequestLoggingMiddleware",
    "get_middleware_config",
    "create_middleware_stack",
    # Authentication middleware
    "JWTAuthMiddleware",
    "RoleBasedAuthMiddleware",
    "AuthenticationError",
    "AuthorizationError",
    "create_auth_middleware",
    "create_role_middleware",
    # CORS middleware
    "CORSConfig",
    "CORSMiddlewareStandalone",
    "create_cors_middleware",
    "create_permissive_cors",
    "create_restrictive_cors"
]
'''
        with open(config_path / "__init__.py", "w") as f:
            f.write(init_content)

        # Create logger.py
        logger_content = '''"""Application logger implementation.

Provides structured logging with context and correlation IDs.
Customize according to your application logging requirements.
"""

import logging
import sys
import json
import uuid
from typing import Any, Dict, Optional, Union
from datetime import datetime
from contextvars import ContextVar
from pathlib import Path


# Context variables for request tracking
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
user_id: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
request_id: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging.
    
    Outputs logs in JSON format with additional context information.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON.
        
        Args:
            record: Log record to format
        
        Returns:
            Formatted log message
        """
        # Base log data
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add context information
        if correlation_id.get():
            log_data["correlation_id"] = correlation_id.get()
        if user_id.get():
            log_data["user_id"] = user_id.get()
        if request_id.get():
            log_data["request_id"] = request_id.get()
        
        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "lineno", "funcName", "created",
                "msecs", "relativeCreated", "thread", "threadName",
                "processName", "process", "getMessage", "exc_info",
                "exc_text", "stack_info"
            }:
                log_data[key] = value
        
        return json.dumps(log_data, default=str)


class ApplicationLogger:
    """Application logger with context management.
    
    Provides structured logging with correlation IDs and context information.
    """
    
    def __init__(self, name: str, level: str = "INFO"):
        """Initialize application logger.
        
        Args:
            name: Logger name
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Setup logging handlers."""
        # Console handler with structured formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(console_handler)
    
    def set_correlation_id(self, corr_id: Optional[str] = None) -> str:
        """Set correlation ID for request tracking.
        
        Args:
            corr_id: Correlation ID (generates new if None)
        
        Returns:
            Correlation ID
        """
        if corr_id is None:
            corr_id = str(uuid.uuid4())
        correlation_id.set(corr_id)
        return corr_id
    
    def set_user_id(self, uid: str) -> None:
        """Set user ID for request tracking.
        
        Args:
            uid: User ID
        """
        user_id.set(uid)
    
    def set_request_id(self, req_id: str) -> None:
        """Set request ID for request tracking.
        
        Args:
            req_id: Request ID
        """
        request_id.set(req_id)
    
    def clear_context(self) -> None:
        """Clear all context variables."""
        correlation_id.set(None)
        user_id.set(None)
        request_id.set(None)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message.
        
        Args:
            message: Log message
            **kwargs: Additional context
        """
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message.
        
        Args:
            message: Log message
            **kwargs: Additional context
        """
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message.
        
        Args:
            message: Log message
            **kwargs: Additional context
        """
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """Log error message.
        
        Args:
            message: Log message
            exc_info: Include exception information
            **kwargs: Additional context
        """
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def critical(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """Log critical message.
        
        Args:
            message: Log message
            exc_info: Include exception information
            **kwargs: Additional context
        """
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback.
        
        Args:
            message: Log message
            **kwargs: Additional context
        """
        self.logger.exception(message, extra=kwargs)


class FileLogger(ApplicationLogger):
    """File-based logger with rotation support.
    
    Extends ApplicationLogger to support file output with rotation.
    """
    
    def __init__(
        self,
        name: str,
        log_file: Union[str, Path],
        level: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        """Initialize file logger.
        
        Args:
            name: Logger name
            log_file: Log file path
            level: Logging level
            max_bytes: Maximum file size before rotation
            backup_count: Number of backup files to keep
        """
        self.log_file = Path(log_file)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        super().__init__(name, level)
    
    def _setup_handlers(self) -> None:
        """Setup logging handlers with file rotation."""
        from logging.handlers import RotatingFileHandler
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        file_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(file_handler)
        
        # Also add console handler
        super()._setup_handlers()


# Global logger instances
_loggers: Dict[str, ApplicationLogger] = {}


def get_logger(name: str, level: str = "INFO") -> ApplicationLogger:
    """Get or create application logger.
    
    Args:
        name: Logger name
        level: Logging level
    
    Returns:
        ApplicationLogger instance
    """
    if name not in _loggers:
        _loggers[name] = ApplicationLogger(name, level)
    return _loggers[name]


def get_file_logger(
    name: str,
    log_file: Union[str, Path],
    level: str = "INFO",
    **kwargs
) -> FileLogger:
    """Get or create file logger.
    
    Args:
        name: Logger name
        log_file: Log file path
        level: Logging level
        **kwargs: Additional FileLogger arguments
    
    Returns:
        FileLogger instance
    """
    logger_key = f"{name}:{log_file}"
    if logger_key not in _loggers:
        _loggers[logger_key] = FileLogger(name, log_file, level, **kwargs)
    return _loggers[logger_key]


def setup_application_logging(
    level: str = "INFO",
    log_file: Optional[Union[str, Path]] = None,
    structured: bool = True
) -> None:
    """Setup application-wide logging configuration.
    
    Args:
        level: Default logging level
        log_file: Optional log file path
        structured: Use structured JSON logging
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Setup formatter
    if structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
'''

        with open(config_path / "logger.py", "w") as f:
            f.write(logger_content)

    def _create_cache_config(self, config_path: Path) -> None:
        """Create cache configuration files.

        Args:
            config_path: Path to the cache configuration directory
        """
        cache_config = '''"""Cache configuration module.

Provides centralized cache configuration for the application.
Supports Redis, Memcached, and in-memory caching.
"""

from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field
from enum import Enum


class CacheBackend(str, Enum):
    """Supported cache backends."""
    REDIS = "redis"
    MEMCACHED = "memcached"
    MEMORY = "memory"


class CacheConfig(BaseSettings):
    """Cache configuration settings.
    
    Attributes:
        backend: Cache backend type
        host: Cache server host
        port: Cache server port
        password: Cache server password (optional)
        database: Cache database number (Redis only)
        ttl: Default time-to-live in seconds
        max_connections: Maximum connection pool size
        timeout: Connection timeout in seconds
    """
    
    backend: CacheBackend = Field(
        default=CacheBackend.MEMORY,
        env="CACHE_BACKEND",
        description="Cache backend type"
    )
    host: str = Field(
        default="localhost",
        env="CACHE_HOST",
        description="Cache server host"
    )
    port: int = Field(
        default=6379,
        env="CACHE_PORT",
        description="Cache server port"
    )
    password: Optional[str] = Field(
        default=None,
        env="CACHE_PASSWORD",
        description="Cache server password"
    )
    database: int = Field(
        default=0,
        env="CACHE_DATABASE",
        description="Cache database number"
    )
    ttl: int = Field(
        default=3600,
        env="CACHE_TTL",
        description="Default TTL in seconds"
    )
    max_connections: int = Field(
        default=10,
        env="CACHE_MAX_CONNECTIONS",
        description="Maximum connection pool size"
    )
    timeout: int = Field(
        default=5,
        env="CACHE_TIMEOUT",
        description="Connection timeout in seconds"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class CacheManager:
    """Cache manager for handling different cache backends."""
    
    def __init__(self, config: CacheConfig = None):
        """Initialize cache manager.
        
        Args:
            config: Cache configuration
        """
        if config is None:
            raise ValueError("CacheConfig dependency must be provided explicitly (Phase 3 Architecture Cleanup)")
        self.config = config
        self._client = None
    
    def get_client(self):
        """Get cache client instance.
        
        Returns:
            Cache client instance
        """
        if self._client is None:
            self._client = self._create_client()
        return self._client
    
    def _create_client(self):
        """Create cache client based on backend type.
        
        Returns:
            Cache client instance
        """
        if self.config.backend == CacheBackend.REDIS:
            return self._create_redis_client()
        elif self.config.backend == CacheBackend.MEMCACHED:
            return self._create_memcached_client()
        else:
            return self._create_memory_client()
    
    def _create_redis_client(self):
        """Create Redis client.
        
        Returns:
            Redis client instance
        """
        try:
            import redis
            return redis.Redis(
                host=self.config.host,
                port=self.config.port,
                password=self.config.password,
                db=self.config.database,
                socket_timeout=self.config.timeout,
                max_connections=self.config.max_connections
            )
        except ImportError:
            raise ImportError("Redis package not installed. Install with: pip install redis")
    
    def _create_memcached_client(self):
        """Create Memcached client.
        
        Returns:
            Memcached client instance
        """
        try:
            import pymemcache.client.base as memcache
            return memcache.Client(
                (self.config.host, self.config.port),
                timeout=self.config.timeout
            )
        except ImportError:
            raise ImportError("Pymemcache package not installed. Install with: pip install pymemcache")
    
    def _create_memory_client(self):
        """Create in-memory cache client.
        
        Returns:
            In-memory cache instance
        """
        return {}


def get_cache_config() -> CacheConfig:
    """Get cache configuration instance.
    
    Returns:
        CacheConfig: Configured cache settings
    """
    return CacheConfig()


def get_cache_manager(config: CacheConfig = None) -> CacheManager:
    """Get cache manager instance.
    
    Args:
        config: Cache configuration (optional)
    
    Returns:
        CacheManager: Cache manager instance
    """
    return CacheManager(config)
'''

        with open(config_path / "cache.py", "w") as f:
            f.write(cache_config)

        # Create __init__.py
        with open(config_path / "__init__.py", "w") as f:
            f.write('"""Cache infrastructure module."""\n')

        # Create redis_client.py
        redis_client_content = '''"""Redis client implementation.

Provides Redis connection management and operations.
Customize according to your caching requirements.
"""

from typing import Any, Optional, Union, Dict, List
import json
import pickle
import time
from contextlib import asynccontextmanager
from redis.asyncio import Redis, ConnectionPool
from redis.exceptions import RedisError, ConnectionError
import logging


logger = logging.getLogger(__name__)


class RedisClient:
    """Async Redis client with connection pooling and error handling.
    
    Provides high-level Redis operations with automatic serialization,
    connection management, and error handling.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        max_connections: int = 10,
        decode_responses: bool = True,
        **kwargs
    ):
        """Initialize Redis client.
        
        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password
            max_connections: Maximum connections in pool
            decode_responses: Whether to decode responses
            **kwargs: Additional Redis configuration
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        
        # Create connection pool
        self.pool = ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            max_connections=max_connections,
            decode_responses=decode_responses,
            **kwargs
        )
        
        self.redis = Redis(connection_pool=self.pool)
        self._connected = False
    
    async def connect(self) -> None:
        """Establish Redis connection.
        
        Raises:
            ConnectionError: If connection fails
        """
        try:
            await self.redis.ping()
            self._connected = True
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise ConnectionError(f"Redis connection failed: {e}")
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._connected:
            await self.redis.close()
            self._connected = False
            logger.info("Disconnected from Redis")
    
    def _serialize_value(self, value: Any) -> Union[str, bytes]:
        """Serialize value for Redis storage.
        
        Args:
            value: Value to serialize
        
        Returns:
            Serialized value
        """
        if isinstance(value, (str, int, float, bool)):
            return json.dumps(value)
        else:
            return pickle.dumps(value)
    
    def _deserialize_value(self, value: Union[str, bytes]) -> Any:
        """Deserialize value from Redis.
        
        Args:
            value: Serialized value
        
        Returns:
            Deserialized value
        """
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        else:
            return pickle.loads(value)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None
        """
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
            return self._deserialize_value(value)
        except RedisError as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """Set value in Redis.
        
        Args:
            key: Cache key
            value: Value to cache
            ex: Expiration in seconds
            px: Expiration in milliseconds
            nx: Only set if key doesn\'t exist
            xx: Only set if key exists
        
        Returns:
            True if successful
        """
        try:
            serialized_value = self._serialize_value(value)
            result = await self.redis.set(key, serialized_value, ex=ex, px=px, nx=nx, xx=xx)
            return bool(result)
        except RedisError as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    async def delete(self, *keys: str) -> int:
        """Delete keys from Redis.
        
        Args:
            *keys: Keys to delete
        
        Returns:
            Number of keys deleted
        """
        try:
            return await self.redis.delete(*keys)
        except RedisError as e:
            logger.error(f"Redis DELETE error for keys {keys}: {e}")
            return 0
    
    async def exists(self, *keys: str) -> int:
        """Check if keys exist in Redis.
        
        Args:
            *keys: Keys to check
        
        Returns:
            Number of existing keys
        """
        try:
            return await self.redis.exists(*keys)
        except RedisError as e:
            logger.error(f"Redis EXISTS error for keys {keys}: {e}")
            return 0
    
    async def expire(self, key: str, time: int) -> bool:
        """Set expiration for key.
        
        Args:
            key: Cache key
            time: Expiration time in seconds
        
        Returns:
            True if successful
        """
        try:
            return await self.redis.expire(key, time)
        except RedisError as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """Get time to live for key.
        
        Args:
            key: Cache key
        
        Returns:
            TTL in seconds (-1 if no expiration, -2 if key doesn\'t exist)
        """
        try:
            return await self.redis.ttl(key)
        except RedisError as e:
            logger.error(f"Redis TTL error for key {key}: {e}")
            return -2
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern.
        
        Args:
            pattern: Key pattern
        
        Returns:
            List of matching keys
        """
        try:
            return await self.redis.keys(pattern)
        except RedisError as e:
            logger.error(f"Redis KEYS error for pattern {pattern}: {e}")
            return []
    
    async def flushdb(self) -> bool:
        """Clear current database.
        
        Returns:
            True if successful
        """
        try:
            await self.redis.flushdb()
            return True
        except RedisError as e:
            logger.error(f"Redis FLUSHDB error: {e}")
            return False
    
    @asynccontextmanager
    async def pipeline(self):
        """Get Redis pipeline for batch operations.
        
        Yields:
            Redis pipeline
        """
        pipe = self.redis.pipeline()
        try:
            yield pipe
            await pipe.execute()
        except RedisError as e:
            logger.error(f"Redis pipeline error: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform Redis health check.
        
        Returns:
            Health check results
        """
        try:
            start_time = time.time()
            await self.redis.ping()
            response_time = time.time() - start_time
            
            info = await self.redis.info()
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "redis_version": info.get("redis_version", "unknown")
            }
        except RedisError as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


def initialize_redis(
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    password: Optional[str] = None,
    **kwargs
) -> RedisClient:
    """Initialize global Redis client.
    
    Args:
        host: Redis server host
        port: Redis server port
        db: Redis database number
        password: Redis password
        **kwargs: Additional Redis configuration
    
    Returns:
        RedisClient: Initialized Redis client
    """
    global _redis_client
    _redis_client = RedisClient(host=host, port=port, db=db, password=password, **kwargs)
    return _redis_client


def get_redis_client() -> RedisClient:
    """Get global Redis client instance.
    
    Returns:
        RedisClient: Redis client instance
    
    Raises:
        RuntimeError: If Redis not initialized
    """
    if _redis_client is None:
        raise RuntimeError("Redis not initialized. Call initialize_redis() first.")
    return _redis_client
'''

        with open(config_path / "redis_client.py", "w") as f:
            f.write(redis_client_content)

    def _create_middleware_config(self, config_path: Path) -> None:
        """Create middleware configuration files.

        Args:
            config_path: Path to the middleware configuration directory
        """
        middleware_config = '''"""Middleware configuration module.

Provides common middleware components for web applications.
Includes CORS, authentication, rate limiting, and request logging.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseSettings, Field
from enum import Enum
import time
import logging


class MiddlewareConfig(BaseSettings):
    """Middleware configuration settings.
    
    Attributes:
        enable_cors: Enable CORS middleware
        cors_origins: Allowed CORS origins
        cors_methods: Allowed CORS methods
        cors_headers: Allowed CORS headers
        enable_rate_limiting: Enable rate limiting
        rate_limit_requests: Requests per minute
        enable_request_logging: Enable request logging
        log_request_body: Log request body (security consideration)
    """
    
    enable_cors: bool = Field(
        default=True,
        env="MIDDLEWARE_ENABLE_CORS",
        description="Enable CORS middleware"
    )
    cors_origins: List[str] = Field(
        default=["*"],
        env="MIDDLEWARE_CORS_ORIGINS",
        description="Allowed CORS origins"
    )
    cors_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        env="MIDDLEWARE_CORS_METHODS",
        description="Allowed CORS methods"
    )
    cors_headers: List[str] = Field(
        default=["*"],
        env="MIDDLEWARE_CORS_HEADERS",
        description="Allowed CORS headers"
    )
    enable_rate_limiting: bool = Field(
        default=False,
        env="MIDDLEWARE_ENABLE_RATE_LIMITING",
        description="Enable rate limiting"
    )
    rate_limit_requests: int = Field(
        default=100,
        env="MIDDLEWARE_RATE_LIMIT_REQUESTS",
        description="Requests per minute"
    )
    enable_request_logging: bool = Field(
        default=True,
        env="MIDDLEWARE_ENABLE_REQUEST_LOGGING",
        description="Enable request logging"
    )
    log_request_body: bool = Field(
        default=False,
        env="MIDDLEWARE_LOG_REQUEST_BODY",
        description="Log request body"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class CORSMiddleware:
    """CORS middleware for handling cross-origin requests."""
    
    def __init__(self, config: MiddlewareConfig):
        """Initialize CORS middleware.
        
        Args:
            config: Middleware configuration
        """
        self.config = config
    
    def process_request(self, request):
        """Process incoming request for CORS.
        
        Args:
            request: HTTP request object
        
        Returns:
            Modified request or response
        """
        if not self.config.enable_cors:
            return request
        
        # Add CORS headers logic here
        # This is a placeholder for actual CORS implementation
        return request
    
    def process_response(self, response):
        """Process outgoing response for CORS.
        
        Args:
            response: HTTP response object
        
        Returns:
            Modified response with CORS headers
        """
        if not self.config.enable_cors:
            return response
        
        # Add CORS headers to response
        if hasattr(response, 'headers'):
            response.headers['Access-Control-Allow-Origin'] = ','.join(self.config.cors_origins)
            response.headers['Access-Control-Allow-Methods'] = ','.join(self.config.cors_methods)
            response.headers['Access-Control-Allow-Headers'] = ','.join(self.config.cors_headers)
        
        return response


class RateLimitMiddleware:
    """Rate limiting middleware."""
    
    def __init__(self, config: MiddlewareConfig):
        """Initialize rate limiting middleware.
        
        Args:
            config: Middleware configuration
        """
        self.config = config
        self.requests = {}  # In-memory store (use Redis in production)
    
    def process_request(self, request):
        """Process request for rate limiting.
        
        Args:
            request: HTTP request object
        
        Returns:
            Request or rate limit response
        """
        if not self.config.enable_rate_limiting:
            return request
        
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Clean old entries
        self._cleanup_old_requests(current_time)
        
        # Check rate limit
        if self._is_rate_limited(client_ip, current_time):
            return self._create_rate_limit_response()
        
        # Record request
        self._record_request(client_ip, current_time)
        
        return request
    
    def _get_client_ip(self, request):
        """Extract client IP from request.
        
        Args:
            request: HTTP request object
        
        Returns:
            Client IP address
        """
        # Placeholder implementation
        return getattr(request, 'remote_addr', '127.0.0.1')
    
    def _cleanup_old_requests(self, current_time):
        """Remove old request records.
        
        Args:
            current_time: Current timestamp
        """
        cutoff_time = current_time - 60  # 1 minute window
        for ip in list(self.requests.keys()):
            self.requests[ip] = [t for t in self.requests[ip] if t > cutoff_time]
            if not self.requests[ip]:
                del self.requests[ip]
    
    def _is_rate_limited(self, client_ip, current_time):
        """Check if client is rate limited.
        
        Args:
            client_ip: Client IP address
            current_time: Current timestamp
        
        Returns:
            True if rate limited, False otherwise
        """
        if client_ip not in self.requests:
            return False
        
        return len(self.requests[client_ip]) >= self.config.rate_limit_requests
    
    def _record_request(self, client_ip, current_time):
        """Record request timestamp.
        
        Args:
            client_ip: Client IP address
            current_time: Current timestamp
        """
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append(current_time)
    
    def _create_rate_limit_response(self):
        """Create rate limit exceeded response.
        
        Returns:
            Rate limit response
        """
        # Placeholder for actual response creation
        return {"error": "Rate limit exceeded", "status_code": 429}


class RequestLoggingMiddleware:
    """Request logging middleware."""
    
    def __init__(self, config: MiddlewareConfig):
        """Initialize request logging middleware.
        
        Args:
            config: Middleware configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def process_request(self, request):
        """Log incoming request.
        
        Args:
            request: HTTP request object
        
        Returns:
            Request object
        """
        if not self.config.enable_request_logging:
            return request
        
        # Log request details
        method = getattr(request, 'method', 'UNKNOWN')
        path = getattr(request, 'path', '/')
        
        log_data = {
            'method': method,
            'path': path,
            'timestamp': time.time()
        }
        
        if self.config.log_request_body and hasattr(request, 'body'):
            log_data['body'] = str(request.body)[:1000]  # Limit body size
        
        self.logger.info(f"Request: {log_data}")
        
        return request


def get_middleware_config() -> MiddlewareConfig:
    """Get middleware configuration instance.
    
    Returns:
        MiddlewareConfig: Configured middleware settings
    """
    return MiddlewareConfig()


def create_middleware_stack(config: MiddlewareConfig = None) -> List:
    """Create middleware stack.
    
    Args:
        config: Middleware configuration (optional)
    
    Returns:
        List of middleware instances
    """
    if config is None:
        config = MiddlewareConfig()
    
    middleware_stack = []
    
    if config.enable_request_logging:
        middleware_stack.append(RequestLoggingMiddleware(config))
    
    if config.enable_cors:
        middleware_stack.append(CORSMiddleware(config))
    
    if config.enable_rate_limiting:
        middleware_stack.append(RateLimitMiddleware(config))
    
    return middleware_stack
'''

        with open(config_path / "middleware.py", "w") as f:
            f.write(middleware_config)

        # Create auth_middleware.py
        auth_middleware_content = '''"""Authentication middleware.

Provides authentication and authorization middleware components.
Customize according to your authentication requirements.
"""

from typing import Dict, Any, Optional, Callable
from functools import wraps
import jwt
import time
from datetime import datetime, timedelta


class AuthenticationError(Exception):
    """Authentication error exception."""
    pass


class AuthorizationError(Exception):
    """Authorization error exception."""
    pass


class JWTAuthMiddleware:
    """JWT-based authentication middleware.
    
    Provides JWT token validation and user authentication.
    """
    
    def __init__(self, secret_key: str, algorithm: str = "HS256", token_expiry: int = 3600):
        """Initialize JWT authentication middleware.
        
        Args:
            secret_key: Secret key for JWT signing
            algorithm: JWT algorithm (default: HS256)
            token_expiry: Token expiry time in seconds (default: 1 hour)
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expiry = token_expiry
    
    def generate_token(self, user_id: str, user_data: Dict[str, Any] = None) -> str:
        """Generate JWT token for user.
        
        Args:
            user_id: User identifier
            user_data: Additional user data to include in token
        
        Returns:
            JWT token string
        """
        payload = {
            "user_id": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(seconds=self.token_expiry),
            "iat": datetime.now(timezone.utc)
        }
        
        if user_data:
            payload.update(user_data)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token.
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded token payload
        
        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
    
    def extract_token(self, request) -> Optional[str]:
        """Extract token from request.
        
        Args:
            request: HTTP request object
        
        Returns:
            Token string if found, None otherwise
        """
        # Check Authorization header
        auth_header = getattr(request, 'headers', {}).get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Check query parameters
        if hasattr(request, 'query_params'):
            return request.query_params.get('token')
        
        return None
    
    def process_request(self, request):
        """Process request for authentication.
        
        Args:
            request: HTTP request object
        
        Returns:
            Modified request with user context
        
        Raises:
            AuthenticationError: If authentication fails
        """
        token = self.extract_token(request)
        
        if not token:
            raise AuthenticationError("No authentication token provided")
        
        try:
            payload = self.verify_token(token)
            # Add user context to request
            if hasattr(request, 'state'):
                request.state.user = payload
            else:
                request.user = payload
            
            return request
        except AuthenticationError:
            raise


class RoleBasedAuthMiddleware:
    """Role-based authorization middleware.
    
    Provides role-based access control functionality.
    """
    
    def __init__(self, role_permissions: Dict[str, list] = None):
        """Initialize role-based authorization middleware.
        
        Args:
            role_permissions: Mapping of roles to permissions
        """
        self.role_permissions = role_permissions or {
            'admin': ['read', 'write', 'delete', 'manage'],
            'user': ['read', 'write'],
            'guest': ['read']
        }
    
    def check_permission(self, user_role: str, required_permission: str) -> bool:
        """Check if user role has required permission.
        
        Args:
            user_role: User's role
            required_permission: Required permission
        
        Returns:
            True if permission granted, False otherwise
        """
        role_perms = self.role_permissions.get(user_role, [])
        return required_permission in role_perms
    
    def require_permission(self, permission: str):
        """Decorator to require specific permission.
        
        Args:
            permission: Required permission
        
        Returns:
            Decorator function
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Extract user from request context
                # This is a placeholder - implement based on your framework
                user_role = kwargs.get('user_role', 'guest')
                
                if not self.check_permission(user_role, permission):
                    raise AuthorizationError(f"Permission '{permission}' required")
                
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def process_request(self, request, required_permission: str = None):
        """Process request for authorization.
        
        Args:
            request: HTTP request object
            required_permission: Required permission for this request
        
        Returns:
            Request object
        
        Raises:
            AuthorizationError: If authorization fails
        """
        if not required_permission:
            return request
        
        # Extract user role from request
        user_data = getattr(request, 'user', {}) or getattr(request.state, 'user', {})
        user_role = user_data.get('role', 'guest')
        
        if not self.check_permission(user_role, required_permission):
            raise AuthorizationError(f"Insufficient permissions. Required: {required_permission}")
        
        return request


def create_auth_middleware(secret_key: str, **kwargs) -> JWTAuthMiddleware:
    """Create JWT authentication middleware instance.
    
    Args:
        secret_key: Secret key for JWT signing
        **kwargs: Additional configuration options
    
    Returns:
        JWTAuthMiddleware instance
    """
    return JWTAuthMiddleware(secret_key, **kwargs)


def create_role_middleware(role_permissions: Dict[str, list] = None) -> RoleBasedAuthMiddleware:
    """Create role-based authorization middleware instance.
    
    Args:
        role_permissions: Role to permissions mapping
    
    Returns:
        RoleBasedAuthMiddleware instance
    """
    return RoleBasedAuthMiddleware(role_permissions)
'''

        with open(config_path / "auth_middleware.py", "w") as f:
            f.write(auth_middleware_content)

        # Create cors_middleware.py
        cors_middleware_content = '''"""CORS middleware.

Provides Cross-Origin Resource Sharing (CORS) middleware.
Customize according to your CORS requirements.
"""

from typing import List, Dict, Any, Optional, Union
import re


class CORSConfig:
    """CORS configuration settings."""
    
    def __init__(
        self,
        allow_origins: List[str] = None,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
        expose_headers: List[str] = None,
        allow_credentials: bool = False,
        max_age: int = 600
    ):
        """Initialize CORS configuration.
        
        Args:
            allow_origins: Allowed origins (default: ["*"])
            allow_methods: Allowed HTTP methods
            allow_headers: Allowed headers
            expose_headers: Headers to expose to client
            allow_credentials: Allow credentials in requests
            max_age: Preflight cache duration in seconds
        """
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allow_headers = allow_headers or ["*"]
        self.expose_headers = expose_headers or []
        self.allow_credentials = allow_credentials
        self.max_age = max_age
        
        # Compile origin patterns for efficient matching
        self._origin_patterns = []
        for origin in self.allow_origins:
            if origin == "*":
                self._origin_patterns.append(re.compile(r".*"))
            else:
                # Escape special regex characters except *
                pattern = re.escape(origin).replace(r"\\*", ".*")
                self._origin_patterns.append(re.compile(f"^{pattern}$"))
    
    def is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed.
        
        Args:
            origin: Origin to check
        
        Returns:
            True if origin is allowed, False otherwise
        """
        if not origin:
            return False
        
        for pattern in self._origin_patterns:
            if pattern.match(origin):
                return True
        
        return False


class CORSMiddleware:
    """CORS middleware for handling cross-origin requests."""
    
    def __init__(self, config: CORSConfig):
        """Initialize CORS middleware.
        
        Args:
            config: CORS configuration
        
        Raises:
            ValueError: If config is None
        """
        if config is None:
            raise ValueError("CORSConfig is required and cannot be None")
        self.config = config
    
    def is_preflight_request(self, request) -> bool:
        """Check if request is a CORS preflight request.
        
        Args:
            request: HTTP request object
        
        Returns:
            True if preflight request, False otherwise
        """
        method = getattr(request, 'method', '').upper()
        has_origin = self._get_header(request, 'Origin') is not None
        has_access_control = self._get_header(request, 'Access-Control-Request-Method') is not None
        
        return method == 'OPTIONS' and has_origin and has_access_control
    
    def _get_header(self, request, header_name: str) -> Optional[str]:
        """Get header value from request.
        
        Args:
            request: HTTP request object
            header_name: Header name
        
        Returns:
            Header value if found, None otherwise
        """
        headers = getattr(request, 'headers', {})
        return headers.get(header_name) or headers.get(header_name.lower())
    
    def _set_header(self, response, header_name: str, header_value: str):
        """Set header on response.
        
        Args:
            response: HTTP response object
            header_name: Header name
            header_value: Header value
        """
        if hasattr(response, 'headers'):
            response.headers[header_name] = header_value
        elif hasattr(response, 'set_header'):
            response.set_header(header_name, header_value)
    
    def process_preflight_request(self, request) -> Dict[str, Any]:
        """Process CORS preflight request.
        
        Args:
            request: HTTP request object
        
        Returns:
            Preflight response data
        """
        origin = self._get_header(request, 'Origin')
        requested_method = self._get_header(request, 'Access-Control-Request-Method')
        requested_headers = self._get_header(request, 'Access-Control-Request-Headers')
        
        response_headers = {}
        
        # Check origin
        if origin and self.config.is_origin_allowed(origin):
            response_headers['Access-Control-Allow-Origin'] = origin
        elif '*' in self.config.allow_origins:
            response_headers['Access-Control-Allow-Origin'] = '*'
        
        # Check method
        if requested_method and requested_method in self.config.allow_methods:
            response_headers['Access-Control-Allow-Methods'] = ', '.join(self.config.allow_methods)
        
        # Check headers
        if requested_headers:
            if '*' in self.config.allow_headers:
                response_headers['Access-Control-Allow-Headers'] = requested_headers
            else:
                allowed_headers = []
                for header in requested_headers.split(', '):
                    if header.strip() in self.config.allow_headers:
                        allowed_headers.append(header.strip())
                if allowed_headers:
                    response_headers['Access-Control-Allow-Headers'] = ', '.join(allowed_headers)
        
        # Set credentials
        if self.config.allow_credentials:
            response_headers['Access-Control-Allow-Credentials'] = 'true'
        
        # Set max age
        response_headers['Access-Control-Max-Age'] = str(self.config.max_age)
        
        return {
            'status_code': 200,
            'headers': response_headers,
            'body': ''
        }
    
    def process_request(self, request):
        """Process incoming request for CORS.
        
        Args:
            request: HTTP request object
        
        Returns:
            Request object or preflight response
        """
        if self.is_preflight_request(request):
            return self.process_preflight_request(request)
        
        return request
    
    def process_response(self, request, response):
        """Process outgoing response for CORS.
        
        Args:
            request: HTTP request object
            response: HTTP response object
        
        Returns:
            Modified response with CORS headers
        """
        origin = self._get_header(request, 'Origin')
        
        if origin and self.config.is_origin_allowed(origin):
            self._set_header(response, 'Access-Control-Allow-Origin', origin)
        elif '*' in self.config.allow_origins and not self.config.allow_credentials:
            self._set_header(response, 'Access-Control-Allow-Origin', '*')
        
        # Set exposed headers
        if self.config.expose_headers:
            self._set_header(response, 'Access-Control-Expose-Headers', ', '.join(self.config.expose_headers))
        
        # Set credentials
        if self.config.allow_credentials:
            self._set_header(response, 'Access-Control-Allow-Credentials', 'true')
        
        return response


def create_cors_middleware(
    allow_origins: List[str] = None,
    allow_methods: List[str] = None,
    allow_headers: List[str] = None,
    **kwargs
) -> CORSMiddleware:
    """Create CORS middleware instance.
    
    Args:
        allow_origins: Allowed origins
        allow_methods: Allowed HTTP methods
        allow_headers: Allowed headers
        **kwargs: Additional CORS configuration
    
    Returns:
        CORSMiddleware instance
    """
    config = CORSConfig(
        allow_origins=allow_origins,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        **kwargs
    )
    return CORSMiddleware(config)


# Predefined configurations
def create_permissive_cors() -> CORSMiddleware:
    """Create permissive CORS middleware (allow all).
    
    Returns:
        CORSMiddleware with permissive settings
    """
    return create_cors_middleware(
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"]
    )


def create_restrictive_cors(allowed_origins: List[str]) -> CORSMiddleware:
    """Create restrictive CORS middleware.
    
    Args:
        allowed_origins: List of allowed origins
    
    Returns:
        CORSMiddleware with restrictive settings
    """
    return create_cors_middleware(
        allow_origins=allowed_origins,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
        allow_credentials=True
    )
'''

        with open(config_path / "cors_middleware.py", "w") as f:
            f.write(cors_middleware_content)

        # Create __init__.py
        with open(config_path / "__init__.py", "w") as f:
            f.write('"""Middleware infrastructure module."""\n')

    def _create_database_infrastructure(self, infrastructure_path: Path) -> None:
        """Create database infrastructure configuration.

        Args:
            infrastructure_path: Path to infrastructure directory
        """
        # Create database directory
        db_path = infrastructure_path / "database"
        db_path.mkdir(exist_ok=True)

        # Create __init__.py
        with open(db_path / "__init__.py", "w") as f:
            f.write('"""Database infrastructure module."""\n')

        # Create session.py
        session_content = '''"""Database session management.

Provides database session handling and connection management.
Customize according to your ORM and database requirements.
"""

from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool


class DatabaseSession:
    """Database session manager for SQLAlchemy async sessions.
    
    This class manages database sessions and provides context managers
    for safe database operations with automatic cleanup.
    """
    
    def __init__(self, database_url: str, **engine_kwargs):
        """Initialize database session manager.
        
        Args:
            database_url: Database connection URL
            **engine_kwargs: Additional engine configuration
        """
        self.database_url = database_url
        self.engine = create_async_engine(
            database_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False} if "sqlite" in database_url else {},
            **engine_kwargs
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with automatic cleanup.
        
        Yields:
            AsyncSession: Database session
        """
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self):
        """Close database engine and cleanup resources."""
        await self.engine.dispose()


# Global session manager instance
_session_manager: Optional[DatabaseSession] = None


def initialize_database(database_url: str, **engine_kwargs) -> DatabaseSession:
    """Initialize global database session manager.
    
    Args:
        database_url: Database connection URL
        **engine_kwargs: Additional engine configuration
    
    Returns:
        DatabaseSession: Initialized session manager
    """
    global _session_manager
    _session_manager = DatabaseSession(database_url, **engine_kwargs)
    return _session_manager


def get_session_manager() -> DatabaseSession:
    """Get global session manager instance.
    
    Returns:
        DatabaseSession: Session manager instance
    
    Raises:
        RuntimeError: If database not initialized
    """
    if _session_manager is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    return _session_manager


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session context manager.
    
    Yields:
        AsyncSession: Database session
    """
    session_manager = get_session_manager()
    async with session_manager.get_session() as session:
        yield session
'''

        with open(db_path / "session.py", "w") as f:
            f.write(session_content)

        # Create base.py
        base_content = '''"""Database base models and configuration.

Provides base classes and configuration for database models.
Extend and customize according to your application needs.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Base(DeclarativeBase):
    """Base class for all database models.
    
    Provides common functionality and fields for all models.
    """
    pass


class TimestampMixin:
    """Mixin for adding timestamp fields to models."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Record creation timestamp"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Record last update timestamp"
    )


class UUIDMixin:
    """Mixin for adding UUID primary key to models."""
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc="Unique identifier"
    )


class BaseModel(Base, TimestampMixin, UUIDMixin):
    """Base model with common fields and functionality.
    
    Includes:
    - UUID primary key
    - Created/updated timestamps
    - Common utility methods
    """
    
    __abstract__ = True
    
    def to_dict(self, exclude: Optional[set] = None) -> Dict[str, Any]:
        """Convert model instance to dictionary.
        
        Args:
            exclude: Set of field names to exclude
        
        Returns:
            Dictionary representation of the model
        """
        exclude = exclude or set()
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name not in exclude
        }
    
    def update_from_dict(self, data: Dict[str, Any], exclude: Optional[set] = None) -> None:
        """Update model instance from dictionary.
        
        Args:
            data: Dictionary with field values
            exclude: Set of field names to exclude from update
        """
        exclude = exclude or {"id", "created_at", "updated_at"}
        for key, value in data.items():
            if key not in exclude and hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"



'''

        with open(db_path / "base.py", "w") as f:
            f.write(base_content)

    def _create_cache_infrastructure(self, infrastructure_path: Path) -> None:
        """Create cache infrastructure configuration.

        Args:
            infrastructure_path: Path to infrastructure directory
        """
        # Create cache directory
        cache_path = infrastructure_path / "cache"
        cache_path.mkdir(exist_ok=True)

        # Use the cache configuration from _create_cache_config method
        self._create_cache_config(cache_path)

    def _create_logging_infrastructure(self, infrastructure_path: Path) -> None:
        """Create logging infrastructure configuration.

        Args:
            infrastructure_path: Path to infrastructure directory
        """
        # Create logging directory
        logging_path = infrastructure_path / "logging"
        logging_path.mkdir(exist_ok=True)

        # Use the logging configuration from _create_logging_config method
        self._create_logging_config(logging_path)

    def _create_middleware_infrastructure(self, infrastructure_path: Path) -> None:
        """Create middleware infrastructure configuration.

        Args:
            infrastructure_path: Path to infrastructure directory
        """
        # Create middleware directory
        middleware_path = infrastructure_path / "middleware"
        middleware_path.mkdir(exist_ok=True)

        # Use the middleware configuration from _create_middleware_config method
        self._create_middleware_config(middleware_path)
