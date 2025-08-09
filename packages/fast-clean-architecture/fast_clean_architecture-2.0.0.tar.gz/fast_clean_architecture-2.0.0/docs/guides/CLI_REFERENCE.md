# Fast Clean Architecture CLI Reference

This comprehensive guide covers all CLI commands available in Fast Clean Architecture (FCA) v2.0.0.

## Table of Contents

1. [Project Initialization](#project-initialization)
2. [Baseline Creation](#baseline-creation)
3. [System and Module Management](#system-and-module-management)
4. [Component Generation](#component-generation)
5. [API Versioning](#api-versioning)
6. [Batch Operations](#batch-operations)
7. [Project Management](#project-management)
8. [Configuration Management](#configuration-management)
9. [Global Options](#global-options)

## Project Initialization

### `fca-scaffold init`

Initialize a new Fast Clean Architecture project.

```bash
fca-scaffold init [PROJECT_NAME] [OPTIONS]
```

**Arguments:**
- `PROJECT_NAME` (optional): Project name (will be sanitized for Python compatibility)

**Options:**
- `--description, --desc TEXT`: Project description for documentation
- `--version TEXT`: Initial project version (default: 0.1.0)
- `--config PATH`: Custom config file path
- `--force`: Overwrite existing files
- `--verbose`: Show detailed output

**Examples:**
```bash
# Interactive mode
fca-scaffold init

# With project name
fca-scaffold init my-api

# With description and version
fca-scaffold init my-api --desc "User management API" --version 1.0.0

# Force overwrite existing
fca-scaffold init my-api --force
```

**What it creates:**
- `fca_config.yaml` - Project configuration file
- `systems/` - Directory for system contexts

## Baseline Creation

### `fca-scaffold create-scalable-baseline`

Create a complete FastAPI project structure with Clean Architecture.

```bash
fca-scaffold create-scalable-baseline PROJECT_NAME [OPTIONS]
```

**Arguments:**
- `PROJECT_NAME`: Project name (required)

**Options:**
- `--description, --desc TEXT`: Project description
- `--version TEXT`: Project version (default: 0.1.0)
- `--dependency-manager, --deps [poetry|pip]`: Dependency manager (default: poetry)
- `--config PATH`: Custom config file path
- `--force`: Overwrite existing files
- `--verbose`: Show detailed output

**Features:**
- Production-ready FastAPI project
- Multiple systems (user management, orders, notifications)
- Database integration with SQLAlchemy
- API versioning support (v1, v2, v3)
- Security features and middleware
- Comprehensive testing suite
- CI/CD configuration

**Examples:**
```bash
# Create baseline with Poetry (default)
fca-scaffold create-scalable-baseline my-api

# Use pip instead of Poetry
fca-scaffold create-scalable-baseline my-api --deps pip

# With custom description and version
fca-scaffold create-scalable-baseline my-api \
  --desc "E-commerce API" \
  --version 1.0.0 \
  --deps poetry
```

## System and Module Management

### `fca-scaffold create-system-context`

Create a new system (bounded context) within your project.

```bash
fca-scaffold create-system-context SYSTEM_NAME [OPTIONS]
```

**Arguments:**
- `SYSTEM_NAME`: Name of the system to create

**Options:**
- `--description TEXT`: System description
- `--config PATH`: Custom config file path
- `--force`: Overwrite existing files
- `--verbose`: Show detailed output

**Examples:**
```bash
# Create user management system
fca-scaffold create-system-context user_management

# With description
fca-scaffold create-system-context inventory \
  --description "Inventory and stock management"
```

### `fca-scaffold create-module`

Create a module within a system.

```bash
fca-scaffold create-module SYSTEM_NAME MODULE_NAME [OPTIONS]
```

**Arguments:**
- `SYSTEM_NAME`: Target system name
- `MODULE_NAME`: Name of the module to create

**Options:**
- `--description TEXT`: Module description
- `--config PATH`: Custom config file path
- `--force`: Overwrite existing files
- `--verbose`: Show detailed output

**Examples:**
```bash
# Create authentication module
fca-scaffold create-module user_management authentication

# With description
fca-scaffold create-module order_management payments \
  --description "Payment processing and billing"
```

## Component Generation

### `fca-scaffold create-component`

Create individual components within the Clean Architecture layers.

```bash
fca-scaffold create-component SYSTEM MODULE COMPONENT_TYPE COMPONENT_NAME [OPTIONS]
```

**Arguments:**
- `SYSTEM`: System name
- `MODULE`: Module name
- `COMPONENT_TYPE`: Type of component to create
- `COMPONENT_NAME`: Name of the component

**Options:**
- `--template-dir PATH`: Custom template directory
- `--config PATH`: Custom config file path
- `--force`: Overwrite existing files
- `--dry-run`: Preview without creating files
- `--verbose`: Show detailed output

**Available Component Types:**

| Layer | Component Types | Examples | Notes |
|-------|----------------|-----------|-------|
| **Domain** | `entities`, `value_objects`, `interfaces`, `events`, `exceptions`, `enums` | `user`, `email`, `user_repository`, `user_status` | Core business logic |
| **Application** | `services`, `dtos`, `use_cases/commands`, `use_cases/queries` | `user_service`, `user_dto`, `create_user` | Use cases and orchestration |
| **Infrastructure** | `config`, `external`, `database/migrations`, `database/models`, `database/repositories` | `app_config`, `payment_service`, `user_model` | External concerns |
| **Presentation** | `controllers`, `routes`, `schemas`, `middleware` | `user_controller`, `user_routes`, `user_schema` | API layer |

**Examples:
```bash
# Create domain entity
fca-scaffold create-component user_management users entities user

# Create application service
fca-scaffold create-component user_management users services user_service

# Create repository
fca-scaffold create-component user_management users repositories user_repository

# Create API controller
fca-scaffold create-component user_management users controllers user_controller

# Create with versioning
fca-scaffold create-component user_management users controllers/v1 user_controller

# Preview without creating
fca-scaffold create-component user_management users entities user --dry-run
```

## API Versioning

### `fca-scaffold migrate-to-api-versioning`

Migrate existing unversioned presentation layer files to API versioning.

```bash
fca-scaffold migrate-to-api-versioning SYSTEM MODULE [OPTIONS]
```

**Arguments:**
- `SYSTEM`: Target system name
- `MODULE`: Target module name

**Options:**
- `--target-version TEXT`: Target API version (e.g., v1, v2)
- `--components TEXT`: Specific components to migrate (comma-separated)
- `--config PATH`: Custom config file path
- `--dry-run`: Preview changes without making them
- `--force`: Overwrite existing files
- `--verbose`: Show detailed output

**Examples:**
```bash
# Migrate all presentation components to v1
fca-scaffold migrate-to-api-versioning user_management authentication --target-version v1

# Migrate specific components only
fca-scaffold migrate-to-api-versioning user_management auth \
  --target-version v1 \
  --components controllers,routes,schemas

# Preview migration
fca-scaffold migrate-to-api-versioning customer payment --dry-run
```

**What it does:**
- Scans presentation layer for unversioned .py files
- Creates version-specific directories (e.g., v1/, v2/)
- Moves existing files into versioned directories
- Updates import statements within moved files
- Creates backup before migration
- Preserves middleware/ directory (version-agnostic)

## Batch Operations

### `fca-scaffold batch-create`

Create multiple components from a YAML specification file.

```bash
fca-scaffold batch-create SPEC_FILE [OPTIONS]
```

**Arguments:**
- `SPEC_FILE`: Path to YAML specification file

**Options:**
- `--config PATH`: Custom config file path
- `--force`: Overwrite existing files
- `--dry-run`: Preview without creating files
- `--verbose`: Show detailed output

**Examples:**
```bash
# Use provided example specification
fca-scaffold batch-create examples/components_spec.yaml

# Preview batch creation
fca-scaffold batch-create my_spec.yaml --dry-run

# Force overwrite existing files
fca-scaffold batch-create my_spec.yaml --force
```

**YAML Specification Format:**
```yaml
systems:
  - name: user_management
    description: "User management system"
    modules:
      - name: authentication
        description: "User authentication"
        components:
          domain:
            entities: ["user", "role"]
            repositories: ["user"]
          application:
            services: ["auth_service"]
            commands: ["login", "logout"]
          infrastructure:
            models: ["user"]
            repositories: ["user"]
          presentation:
            controllers: ["auth"]
            schemas: ["user"]
```

## Project Management

### `fca-scaffold status`

Show comprehensive project overview and statistics.

```bash
fca-scaffold status [OPTIONS]
```

**Options:**
- `--config PATH`: Custom config file path
- `--verbose`: Show detailed output

**Example:**
```bash
fca-scaffold status
```

**Output includes:**
- Project information (name, version, description)
- Systems overview with module counts
- Component statistics by layer
- Creation and update timestamps
- Project health indicators

### `fca-scaffold system-status`

Show system health and analytics.

```bash
fca-scaffold system-status [OPTIONS]
```

**Options:**
- `--config PATH`: Custom config file path
- `--verbose`: Show detailed analytics

**Features:**
- Usage analytics and command patterns
- Performance metrics
- Error tracking and monitoring
- Security monitoring
- Resource usage statistics

### `fca-scaffold update-package`

Update the Fast Clean Architecture package to the latest version.

```bash
fca-scaffold update-package [OPTIONS]
```

**Options:**
- `--check-only`: Only check for updates without installing
- `--verbose`: Show detailed update information

**Examples:**
```bash
# Update to latest version
fca-scaffold update-package

# Check for updates only
fca-scaffold update-package --check-only
```

### `fca-scaffold version`

Show version information.

```bash
fca-scaffold version
```

## Configuration Management

### `fca-scaffold config`

Manage project configuration.

#### `fca-scaffold config show`

Display current configuration.

```bash
fca-scaffold config show [OPTIONS]
```

**Options:**
- `--config PATH`: Custom config file path

#### `fca-scaffold config validate`

Validate configuration file.

```bash
fca-scaffold config validate [OPTIONS]
```

**Options:**
- `--config PATH`: Custom config file path
- `--verbose`: Show detailed validation results

### `fca-scaffold sync-config`

Synchronize fca_config.yaml with filesystem structure.

```bash
fca-scaffold sync-config [OPTIONS]
```

**Arguments:**
- None

**Options:**
- `--systems TEXT`: Comma-separated list of systems to sync (e.g., 'user_management,payment')
- `--config PATH`: Custom config file path
- `--dry-run`: Preview changes without making them
- `--force`: Overwrite existing configuration entries
- `--verbose`: Show detailed output

**What it does:**
- Scans the project filesystem for FCA-structured components, modules, and systems
- Identifies untracked systems, modules, and components that exist but aren't in config
- Updates fca_config.yaml with discovered items
- Creates automatic backups before changes
- Validates naming conventions and structure

**Use cases:**
- Files were manually copied into the project
- Components were created outside of FCA commands
- Configuration file was lost or corrupted
- Migrating existing code to FCA structure

**Examples:**
```bash
# Sync entire project
fca-scaffold sync-config

# Preview changes without applying
fca-scaffold sync-config --dry-run

# Sync specific systems only
fca-scaffold sync-config --systems user_management,payment

# Force overwrite with detailed output
fca-scaffold sync-config --force --verbose
```

**Configuration Management Examples:**
```bash
# Show current configuration
fca-scaffold config show

# Validate configuration
fca-scaffold config validate

# Validate custom config file
fca-scaffold config validate --config custom_config.yaml

# Sync filesystem with config
fca-scaffold sync-config --dry-run
```

## Global Options

These options work with most commands:

- `--dry-run`: Preview changes without writing files
- `--force`: Overwrite existing files
- `--verbose`: Show detailed output
- `--config PATH`: Use custom config file
- `--help`: Show command help

## Help and Documentation

### Command-specific Help

Get detailed help for any command:

```bash
fca-scaffold [COMMAND] --help
```

**Examples:**
```bash
fca-scaffold create-component --help
fca-scaffold create-scalable-baseline --help
fca-scaffold migrate-to-api-versioning --help
```

## Best Practices

### 1. Project Structure
- Use `create-scalable-baseline` for new projects
- Use the scalable baseline for all project types
- Follow naming conventions (snake_case for systems/modules)

### 2. Development Workflow
- Start with `init` or `create-scalable-baseline`
- Create systems and modules before components
- Use `--dry-run` to preview changes
- Validate configuration regularly

### 3. API Versioning
- Plan versioning strategy early
- Use `migrate-to-api-versioning` for existing modules
- Create versioned components from the start for new features

### 4. Batch Operations
- Use YAML specifications for complex project setups
- Version control your specification files
- Test with `--dry-run` before applying

### 5. Configuration Management
- Keep `fca_config.yaml` in version control
- Validate configuration after manual edits
- Use custom config files for different environments

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure write permissions in target directory
2. **Configuration Errors**: Run `fca-scaffold config validate`
3. **Template Errors**: Check template syntax and variables
4. **Path Issues**: Use absolute paths when in doubt

### Getting Help

- Use `--help` with any command
- Check `fca-scaffold status` for project overview
- Validate configuration with `fca-scaffold config validate`
- Use `--verbose` for detailed error information

---

*This CLI reference is for Fast Clean Architecture v2.0.0. For the latest updates, visit the [FCA GitHub repository](https://github.com/alden-technologies/fast-clean-architecture).*