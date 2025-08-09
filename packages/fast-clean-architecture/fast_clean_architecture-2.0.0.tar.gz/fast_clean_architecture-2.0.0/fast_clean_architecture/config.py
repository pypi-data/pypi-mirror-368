"""Configuration management for Fast Clean Architecture.

This module provides configuration loading, validation, and management
functionalities for the Fast Clean Architecture framework.
"""

# mypy: disable-error-code=unreachable

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field

from .exceptions import ConfigurationError, ValidationError
from .utils import generate_timestamp


class ComponentInfo(BaseModel):
    """Information about a component."""

    name: str
    file_path: Optional[str] = None
    created_at: str = Field(default_factory=generate_timestamp)
    updated_at: str = Field(default_factory=generate_timestamp)


class ComponentsConfig(BaseModel):
    """Configuration for component default imports."""

    # Domain layer components
    entities: List[ComponentInfo] = Field(default_factory=list)
    events: List[ComponentInfo] = Field(default_factory=list)
    exceptions: List[ComponentInfo] = Field(default_factory=list)
    interfaces: List[ComponentInfo] = Field(default_factory=list)
    value_objects: List[ComponentInfo] = Field(default_factory=list)
    enums: List[ComponentInfo] = Field(default_factory=list)

    # Application layer components
    dtos: List[ComponentInfo] = Field(default_factory=list)
    use_cases: List[ComponentInfo] = Field(default_factory=list)
    commands: List[ComponentInfo] = Field(default_factory=list)
    queries: List[ComponentInfo] = Field(default_factory=list)
    services: List[ComponentInfo] = Field(default_factory=list)

    # Infrastructure layer components
    config: List[ComponentInfo] = Field(default_factory=list)
    database: List[ComponentInfo] = Field(default_factory=list)
    repositories: List[ComponentInfo] = Field(default_factory=list)
    models: List[ComponentInfo] = Field(default_factory=list)
    external: List[ComponentInfo] = Field(default_factory=list)

    # Presentation layer components
    controllers: List[ComponentInfo] = Field(default_factory=list)
    middleware: List[ComponentInfo] = Field(default_factory=list)
    routes: List[ComponentInfo] = Field(default_factory=list)
    schemas: List[ComponentInfo] = Field(default_factory=list)

    default_imports: Dict[str, List[str]] = Field(
        default={
            # Domain layer
            "entities": ["dataclasses", "typing", "datetime"],
            "events": ["dataclasses", "typing", "datetime"],
            "exceptions": ["typing"],
            "interfaces": ["abc", "typing"],
            "value_objects": ["dataclasses", "typing"],
            "enums": ["enum", "typing"],
            # Application layer
            "dtos": ["dataclasses", "typing"],
            "use_cases": ["typing"],
            "commands": ["dataclasses", "typing"],
            "queries": ["dataclasses", "typing"],
            "services": ["typing"],
            # Infrastructure layer
            "config": ["pydantic", "typing"],
            "database": ["sqlalchemy", "typing"],
            "repositories": ["typing"],
            "models": ["sqlalchemy", "typing"],
            "external": ["typing"],
            # Presentation layer
            "controllers": ["fastapi", "typing"],
            "middleware": ["fastapi", "typing"],
            "routes": ["fastapi", "typing"],
            "schemas": ["pydantic", "typing"],
        }
    )


class NamingConfig(BaseModel):
    """Configuration for naming conventions."""

    snake_case: bool = True
    auto_pluralize: bool = True


class TemplatesConfig(BaseModel):
    """Configuration for custom templates."""

    entity: Optional[str] = None
    repository: Optional[str] = None
    service: Optional[str] = None
    schemas: Optional[str] = None
    command: Optional[str] = None
    query: Optional[str] = None
    model: Optional[str] = None
    external: Optional[str] = None
    value_object: Optional[str] = None


class DomainComponents(BaseModel):
    """Domain layer components."""

    entities: List[ComponentInfo] = Field(default_factory=list)
    events: List[ComponentInfo] = Field(default_factory=list)
    exceptions: List[ComponentInfo] = Field(default_factory=list)
    interfaces: List[ComponentInfo] = Field(default_factory=list)
    value_objects: List[ComponentInfo] = Field(default_factory=list)
    enums: List[ComponentInfo] = Field(default_factory=list)


class ApplicationComponents(BaseModel):
    """Application layer components."""

    dtos: List[ComponentInfo] = Field(default_factory=list)
    commands: List[ComponentInfo] = Field(default_factory=list)
    queries: List[ComponentInfo] = Field(default_factory=list)
    services: List[ComponentInfo] = Field(default_factory=list)


class DatabaseComponents(BaseModel):
    """Database layer components."""

    migrations: List[ComponentInfo] = Field(default_factory=list)
    models: List[ComponentInfo] = Field(default_factory=list)
    repositories: List[ComponentInfo] = Field(default_factory=list)


class InfrastructureComponents(BaseModel):
    """Infrastructure layer components."""

    config: List[ComponentInfo] = Field(default_factory=list)
    external: List[ComponentInfo] = Field(default_factory=list)
    database: DatabaseComponents = Field(default_factory=DatabaseComponents)


class PresentationComponents(BaseModel):
    """Presentation layer components."""

    controllers: List[ComponentInfo] = Field(default_factory=list)
    routes: List[ComponentInfo] = Field(default_factory=list)
    schemas: List[ComponentInfo] = Field(default_factory=list)
    middleware: List[ComponentInfo] = Field(default_factory=list)


class ModuleComponents(BaseModel):
    """Components within a module."""

    domain: ComponentsConfig = Field(default_factory=ComponentsConfig)
    application: ComponentsConfig = Field(default_factory=ComponentsConfig)
    infrastructure: ComponentsConfig = Field(default_factory=ComponentsConfig)
    presentation: ComponentsConfig = Field(default_factory=ComponentsConfig)


class ModuleConfig(BaseModel):
    """Configuration for a module."""

    description: str = ""
    created_at: str = Field(default_factory=generate_timestamp)
    updated_at: str = Field(default_factory=generate_timestamp)
    components: ModuleComponents = Field(default_factory=ModuleComponents)


class SystemConfig(BaseModel):
    """Configuration for a system context."""

    description: str = ""
    created_at: str = Field(default_factory=generate_timestamp)
    updated_at: str = Field(default_factory=generate_timestamp)
    modules: Dict[str, ModuleConfig] = Field(default_factory=dict)


class ProjectConfig(BaseModel):
    """Configuration for the project."""

    name: str = ""
    description: str = ""
    version: str = ""
    base_path: Optional[Path] = None
    created_at: str = Field(default_factory=generate_timestamp)
    updated_at: str = Field(default_factory=generate_timestamp)
    systems: Dict[str, SystemConfig] = Field(default_factory=dict)


class Config(BaseModel):
    """Main configuration model."""

    project: ProjectConfig = Field(default_factory=ProjectConfig)
    templates: TemplatesConfig = Field(default_factory=TemplatesConfig)
    naming: NamingConfig = Field(default_factory=NamingConfig)
    components: ComponentsConfig = Field(default_factory=ComponentsConfig)

    @classmethod
    def load_from_file(cls, config_path: Path) -> "Config":
        """Load configuration from YAML file with enhanced security validation."""
        try:
            if not config_path.exists():
                raise ConfigurationError(f"Configuration file not found: {config_path}")

            # Check file size to prevent DoS attacks
            file_size = config_path.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                raise ConfigurationError(
                    f"Configuration file too large: {file_size} bytes"
                )

            with open(config_path, "r", encoding="utf-8") as f:
                # Use safe_load for security
                data = yaml.safe_load(f) or {}

            # Validate loaded data structure
            if not isinstance(data, dict):
                raise ConfigurationError(
                    "Configuration file must contain a YAML object/dictionary"
                )

            # Sanitize loaded data before creating config object
            sanitized_data = cls._sanitize_loaded_data(data)

            # Ensure sanitized_data is a dict for Config construction
            if not isinstance(sanitized_data, dict):
                raise ConfigurationError("Sanitized data must be a dictionary")

            return cls(**sanitized_data)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading config: {e}")

    @staticmethod
    def _sanitize_loaded_data(
        data: Dict[str, Any],
    ) -> Union[Dict[str, Any], List[Any], str, int, float, bool, None]:
        """Sanitize data loaded from YAML file to prevent injection attacks.

        Args:
            data: Raw data loaded from YAML file

        Returns:
            Sanitized data safe for Config object creation
        """

        def sanitize_value(
            value: Union[Dict[str, Any], List[Any], str, int, float, bool, None],
        ) -> Union[Dict[str, Any], List[Any], str, int, float, bool, None]:
            if value is None:
                return None
            elif isinstance(value, bool):
                return value
            elif isinstance(value, (int, float)):
                # Validate numeric ranges
                if isinstance(value, float) and (
                    value != value or abs(value) == float("inf")
                ):
                    return 0.0
                return value
            elif isinstance(value, str):
                # Remove control characters and YAML-specific dangerous patterns
                sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", value)
                sanitized = re.sub(r"^[!&*|>%@`]", "", sanitized)
                # Limit string length
                if len(sanitized) > 10000:
                    sanitized = sanitized[:10000]
                return sanitized
            elif isinstance(value, list):
                return [sanitize_value(item) for item in value]
            elif isinstance(value, dict):
                sanitized_dict = {}
                for k, v in value.items():
                    # Sanitize keys
                    if not isinstance(k, str):
                        k = str(k)
                    sanitized_key = re.sub(
                        r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", k
                    )
                    sanitized_key = re.sub(r"^[!&*|>%@`]", "", sanitized_key)
                    if len(sanitized_key) > 1000:
                        sanitized_key = sanitized_key[:1000]
                    if sanitized_key:  # Skip empty keys
                        sanitized_dict[sanitized_key] = sanitize_value(v)
                return sanitized_dict
            else:
                # Convert unknown types to string and sanitize
                return sanitize_value(str(value))

        return sanitize_value(data)

    @classmethod
    def create_default(cls) -> "Config":
        """Create default configuration without saving to file."""
        timestamp = generate_timestamp()

        return cls(
            project=ProjectConfig(
                name="my_project",
                description="My FastAPI project",
                version="0.1.0",
                created_at=timestamp,
                updated_at=timestamp,
            )
        )

    @classmethod
    def create_default_config(cls, config_path: Path) -> "Config":
        """Create default configuration."""
        timestamp = generate_timestamp()
        project_name = config_path.parent.name

        config = cls(
            project=ProjectConfig(
                name=project_name,
                created_at=timestamp,
                updated_at=timestamp,
            )
        )

        config.save_to_file(config_path)
        return config

    def save_to_file(self, config_path: Path) -> None:
        """Save configuration to YAML file with atomic write and backup."""
        import tempfile
        from datetime import datetime

        backup_path = None
        temp_path = None

        try:
            # Create timestamped backup if file exists
            if config_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                # Create backup directory if it doesn't exist
                backup_dir = config_path.parent / "fca_config_backups"
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / f"{config_path.stem}.yaml.backup.{timestamp}"
                backup_path.write_bytes(config_path.read_bytes())

                # Clean up old backups (keep only last 5)
                self._cleanup_old_backups(config_path)

            # Ensure parent directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to temporary file first (atomic write)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=config_path.parent,
                delete=False,
                suffix=".tmp",
            ) as f:
                temp_path = Path(f.name)
                # Sanitize configuration data before dumping
                raw_data = self.model_dump(exclude_none=True)
                config_data = self._sanitize_config_data(raw_data)

                # Ensure we have a dict for YAML serialization
                if not isinstance(config_data, dict):
                    raise ConfigurationError(
                        "Sanitized configuration data must be a dictionary"
                    )

                # Use safe_dump for security
                yaml.safe_dump(
                    config_data,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    indent=2,
                    allow_unicode=True,
                )

            # Atomic move
            temp_path.replace(config_path)

        except Exception as e:
            # Clean up temporary file on error
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except (OSError, FileNotFoundError):
                    pass

            # Restore from backup if available
            if backup_path and backup_path.exists() and not config_path.exists():
                try:
                    backup_path.rename(config_path)
                except (OSError, FileExistsError):
                    pass

            raise ConfigurationError(f"Error saving config: {e}")

    def _sanitize_config_data(
        self, data: Union[Dict[str, Any], List[Any], str, int, float, bool, None]
    ) -> Union[Dict[str, Any], List[Any], str, int, float, bool, None]:
        """Sanitize configuration data to prevent injection attacks and ensure safe YAML output.

        Args:
            data: The configuration data to sanitize

        Returns:
            Sanitized configuration data safe for YAML serialization
        """
        if data is None:
            return None
        elif isinstance(data, bool):
            return data
        elif isinstance(data, (int, float)):
            # Validate numeric ranges to prevent potential issues
            if isinstance(data, float) and (data != data or abs(data) == float("inf")):
                return 0.0  # Replace NaN and infinity with safe default
            return data
        elif isinstance(data, str):
            # Remove potentially dangerous characters and control sequences
            sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", data)
            # Remove YAML-specific dangerous patterns
            sanitized = re.sub(r"^[!&*|>%@`]", "", sanitized)
            # Limit string length to prevent DoS
            if len(sanitized) > 10000:
                sanitized = sanitized[:10000]
            return sanitized
        elif isinstance(data, list):
            # Recursively sanitize list items
            return [self._sanitize_config_data(item) for item in data]
        elif isinstance(data, dict):
            # Recursively sanitize dictionary values and validate keys
            sanitized_dict = {}
            for key, value in data.items():
                # Sanitize keys (must be strings for YAML)
                if not isinstance(key, str):
                    key = str(key)
                # Remove dangerous characters from keys
                sanitized_key = re.sub(
                    r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", key
                )
                sanitized_key = re.sub(r"^[!&*|>%@`]", "", sanitized_key)
                if len(sanitized_key) > 1000:
                    sanitized_key = sanitized_key[:1000]

                # Skip empty keys
                if not sanitized_key:
                    continue

                sanitized_dict[sanitized_key] = self._sanitize_config_data(value)
            return sanitized_dict
        else:
            # Convert unknown types to string and sanitize
            return self._sanitize_config_data(str(data))

    def _cleanup_old_backups(self, config_path: Path, keep_count: int = 5) -> None:
        """Clean up old backup files, keeping only the most recent ones."""
        try:
            backup_dir = config_path.parent / "fca_config_backups"
            if not backup_dir.exists():
                return

            backup_pattern = f"{config_path.stem}.yaml.backup.*"
            backup_files = list(backup_dir.glob(backup_pattern))

            if len(backup_files) > keep_count:
                # Sort by modification time (newest first)
                backup_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

                # Remove old backups
                for old_backup in backup_files[keep_count:]:
                    try:
                        old_backup.unlink()
                    except OSError:
                        # Ignore errors when cleaning up old backups
                        pass
        except OSError:
            # Don't fail the main operation if backup cleanup fails
            pass

    def add_system(self, system_name: str, description: str = "") -> None:
        """Add a new system context."""
        if system_name in self.project.systems:
            raise ValidationError(f"System '{system_name}' already exists")

        # Generate fresh timestamp for the new system
        current_time = generate_timestamp()

        self.project.systems[system_name] = SystemConfig(
            description=description,
            created_at=current_time,
            updated_at=current_time,
        )
        # Update project timestamp with fresh timestamp
        self.project.updated_at = current_time

    def add_module(
        self,
        system_name: str,
        module_name: str,
        description: str = "",
        api_version: Optional[str] = None,
    ) -> bool:
        """Add a new module to a system or update existing module with new API version.

        Returns:
            bool: True if module was newly created, False if existing module was updated
        """
        if system_name not in self.project.systems:
            raise ValidationError(f"System '{system_name}' not found")

        # Generate fresh timestamps
        current_time = generate_timestamp()
        is_new_module = False

        # If module exists and api_version is provided, update the existing module
        if module_name in self.project.systems[system_name].modules:
            if api_version:
                # Update existing module with new API version info
                existing_module = self.project.systems[system_name].modules[module_name]
                existing_module.updated_at = current_time
                if description:
                    existing_module.description = description
                is_new_module = False
            else:
                # No API version provided for existing module - this is an error
                raise ValidationError(f"Module '{module_name}' already exists")
        else:
            # Create new module
            self.project.systems[system_name].modules[module_name] = ModuleConfig(
                description=description,
                created_at=current_time,
                updated_at=current_time,
            )
            is_new_module = True

        # Update parent timestamps with fresh timestamp
        self.project.systems[system_name].updated_at = current_time
        self.project.updated_at = current_time

        return is_new_module

    def add_component(
        self,
        system_name: str,
        module_name: str,
        layer: str,
        component_type: str,
        component_name: str,
        file_path: Optional[str] = None,
    ) -> None:
        """Add a component to a module."""
        if system_name not in self.project.systems:
            raise ConfigurationError(f"System '{system_name}' does not exist")

        if module_name not in self.project.systems[system_name].modules:
            raise ValidationError(f"Module '{module_name}' not found")

        # Validate layer
        valid_layers = ["domain", "application", "infrastructure", "presentation"]
        if layer not in valid_layers:
            raise ValidationError(f"Invalid layer: {layer}")

        timestamp = generate_timestamp()
        module = self.project.systems[system_name].modules[module_name]

        # Validate component type for the layer using centralized validation
        from .validation import Validator

        component_type_validation = Validator.validate_component_type_for_layer(
            component_type, layer
        )
        if component_type_validation.is_failure:
            error = component_type_validation.error
            if error is not None:
                raise error
            else:
                raise ValidationError(
                    f"Component type validation failed for '{component_type}' in layer '{layer}'"
                )

        # Use the validated (potentially mapped) component type
        validated_component_type = component_type_validation.unwrap()

        # Get the layer components
        layer_components = getattr(module.components, layer)

        # Get the specific component type list using the validated component type
        component_list = getattr(layer_components, validated_component_type)

        # Check if component already exists
        existing_component = next(
            (comp for comp in component_list if comp.name == component_name), None
        )

        if existing_component is None:
            # Create new component
            component_info = ComponentInfo(
                name=component_name,
                file_path=file_path,
                created_at=timestamp,
                updated_at=timestamp,
            )
            component_list.append(component_info)
            # Sort by name to keep alphabetical order
            component_list.sort(key=lambda x: x.name)

        # Update timestamps
        module.updated_at = timestamp
        self.project.systems[system_name].updated_at = timestamp
        self.project.updated_at = timestamp
