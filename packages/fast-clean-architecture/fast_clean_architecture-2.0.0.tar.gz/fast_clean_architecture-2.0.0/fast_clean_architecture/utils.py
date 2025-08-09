"""Utility functions for Fast Clean Architecture."""

import keyword
import re
import threading
import unicodedata
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from . import __version__
from .exceptions import (
    create_secure_error,
)
from .validation import ValidationRules


def generate_timestamp() -> str:
    """Generate ISO 8601 timestamp in UTC with validation."""
    try:
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        # Validate the timestamp format
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return timestamp
    except Exception as e:
        raise ValueError(f"Failed to generate valid timestamp: {e}")


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


# File locking utilities
_file_locks = {}
_locks_lock = threading.Lock()


def get_file_lock(file_path: Union[str, Path]) -> threading.Lock:
    """Get or create a lock for a specific file path."""
    file_path_str = str(file_path)
    with _locks_lock:
        if file_path_str not in _file_locks:
            _file_locks[file_path_str] = threading.Lock()
        return _file_locks[file_path_str]


def secure_file_operation(
    file_path: Union[str, Path],
    operation_func: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Execute file operation with proper locking."""
    lock = get_file_lock(file_path)
    with lock:
        return operation_func(*args, **kwargs)


def sanitize_error_message(
    error_msg: str, sensitive_info: Optional[List[str]] = None
) -> str:
    """Sanitize error messages to prevent information disclosure."""
    if sensitive_info is None:
        sensitive_info = []

    # Add common sensitive patterns
    sensitive_patterns = [
        r"/Users/[^/\s]+",  # User home directories
        r"/home/[^/\s]+",  # Linux home directories
        r"C:\\Users\\[^\\\s]+",  # Windows user directories
        r"/tmp/[^/\s]+",  # Temporary directories  # nosec B108
        r"/var/[^/\s]+",  # System directories
        r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",  # IP addresses
    ]

    # Add user-provided sensitive info
    sensitive_patterns.extend(sensitive_info)

    sanitized_msg = error_msg
    for pattern in sensitive_patterns:
        sanitized_msg = re.sub(pattern, "[REDACTED]", sanitized_msg)

    return sanitized_msg


def create_secure_error_message(
    error_type: str, operation: str, details: Optional[str] = None
) -> str:
    """Create a secure error message without exposing sensitive information."""
    import os

    base_msg = f"Failed to {operation}"
    if details:
        # Sanitize details to prevent information leakage
        safe_details = details.replace(os.path.expanduser("~"), "<HOME>")
        safe_details = re.sub(r"/Users/[^/]+", "/Users/<USER>", safe_details)
        safe_details = re.sub(r"\\Users\\[^\\]+", "\\Users\\<USER>", safe_details)
        return f"{base_msg}: {safe_details}"
    return base_msg


def to_snake_case(name: str) -> str:
    """Convert string to snake_case."""
    # Replace hyphens and spaces with underscores
    name = re.sub(r"[-\s]+", "_", name)
    # Handle sequences of uppercase letters followed by lowercase letters
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    # Insert underscore before uppercase letters that follow lowercase letters or digits
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


def to_pascal_case(name: str) -> str:
    """Convert string to PascalCase."""
    # First convert to snake_case to normalize, then split and capitalize
    snake_name = to_snake_case(name)
    words = snake_name.split("_")
    return "".join(word.capitalize() for word in words if word)


def to_camel_case(name: str) -> str:
    """Convert string to camelCase."""
    pascal = to_pascal_case(name)
    return pascal[0].lower() + pascal[1:] if pascal else ""


def pluralize(word: str) -> str:
    """Simple pluralization for English words."""
    # Handle irregular plurals
    irregular_plurals = {
        "person": "people",
        "child": "children",
        "mouse": "mice",
        "foot": "feet",
        "tooth": "teeth",
        "goose": "geese",
        "man": "men",
        "woman": "women",
    }

    # Handle uncountable nouns
    uncountable = {"data", "sheep", "fish", "deer", "species", "series"}

    if word.lower() in uncountable:
        return word

    if word.lower() in irregular_plurals:
        return irregular_plurals[word.lower()]

    # Regular pluralization rules
    if word.endswith("y") and len(word) > 1 and word[-2] not in "aeiou":
        return word[:-1] + "ies"
    elif word.endswith(("s", "sh", "ch", "x", "z")):
        return word + "es"
    elif word.endswith("f"):
        return word[:-1] + "ves"
    elif word.endswith("fe"):
        return word[:-2] + "ves"
    else:
        return word + "s"


def validate_python_identifier(name: str) -> bool:
    """Validate if string is a valid Python identifier."""
    return (
        name.isidentifier()
        and not keyword.iskeyword(name)
        and not name.startswith("__")
    )


def sanitize_name(name: str) -> str:
    """Sanitize name to be a valid Python identifier."""
    # Strip whitespace
    name = name.strip()

    # Remove invalid characters except letters, numbers, spaces, hyphens, underscores
    sanitized = re.sub(r"[^a-zA-Z0-9\s\-_]", "", name)

    # Convert to snake_case
    sanitized = to_snake_case(sanitized)

    # Remove leading/trailing underscores and collapse multiple underscores
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")

    # Handle names that start with numbers
    if sanitized and sanitized[0].isdigit():
        # Remove leading numbers
        sanitized = re.sub(r"^[0-9_]+", "", sanitized)

    # Ensure it's not empty
    if not sanitized:
        sanitized = "component"

    return sanitized


def validate_name(name: str) -> None:
    """Validate component name for security and correctness.

    Args:
        name: The name to validate

    Raises:
        ValueError: If the name is invalid
        TypeError: If the name is not a string
        ValidationError: If the name contains security risks
    """
    from fast_clean_architecture.exceptions import ValidationError

    # Check for None or non-string types
    if name is None:
        raise TypeError("Name cannot be None")

    if not isinstance(name, str):
        raise TypeError(f"Name must be a string, got {type(name).__name__}")

    # Check for empty or whitespace-only names
    if not name or not name.strip():
        raise ValueError("Name cannot be empty or whitespace-only")

    # Check length limits
    if len(name) > 100:
        raise ValueError(f"Name too long: {len(name)} characters (max 100)")

    # Check for path traversal attempts (including encoded and Unicode variants)
    # First, decode any URL-encoded sequences
    try:
        decoded_name = urllib.parse.unquote(name)
        # Apply Unicode normalization to handle Unicode attacks
        normalized_name = unicodedata.normalize("NFKC", decoded_name)
    except (ValueError, UnicodeDecodeError, UnicodeError):
        # If decoding fails, treat as suspicious
        raise create_secure_error(
            "encoding_attack",
            "name validation",
            f"Suspicious encoding detected in component name: {name[:50]}",
        )

    # Check for path traversal in original, decoded, and normalized forms
    names_to_check = [name, decoded_name, normalized_name]
    for check_name in names_to_check:
        if ".." in check_name or "/" in check_name or "\\" in check_name:
            raise create_secure_error(
                "path_traversal", "name validation", "Path traversal pattern detected"
            )

    # Check for encoded path traversal sequences
    encoded_patterns = [
        "%2e%2e",
        "%2E%2E",  # .. encoded
        "%2f",
        "%2F",  # / encoded
        "%5c",
        "%5C",  # \ encoded
        "%252e",
        "%252E",  # double-encoded .
        "%252f",
        "%252F",  # double-encoded /
        "%255c",
        "%255C",  # double-encoded \
    ]
    name_lower = name.lower()
    for pattern in encoded_patterns:
        if pattern in name_lower:
            raise create_secure_error(
                "encoded_path_traversal",
                "name validation",
                "Encoded path traversal sequence detected",
            )

    # Check for Unicode path traversal variants
    unicode_dots = ["\u002e", "\uff0e", "\u2024", "\u2025", "\u2026"]
    unicode_slashes = ["\u002f", "\uff0f", "\u2044", "\u29f8"]
    unicode_backslashes = ["\u005c", "\uff3c", "\u29f5", "\u29f9"]

    for dot in unicode_dots:
        for dot2 in unicode_dots:
            if dot + dot2 in name:
                raise create_secure_error(
                    "unicode_path_traversal",
                    "name validation",
                    "Unicode path traversal pattern detected",
                )

    for slash in unicode_slashes + unicode_backslashes:
        if slash in name:
            raise create_secure_error(
                "unicode_path_separator",
                "name validation",
                "Unicode path separator detected",
            )

    # Check for shell injection attempts
    dangerous_chars = [";", "&", "|", "`", "$", "(", ")", "<", ">", "'", '"']
    for char in dangerous_chars:
        if char in name:
            raise ValidationError(
                f"Invalid component name: dangerous character '{char}' in '{name}'"
            )

    # Check for special characters that could cause issues
    invalid_chars = [
        "@",
        "#",
        "%",
        "*",
        "+",
        "=",
        "?",
        "[",
        "]",
        "{",
        "}",
        ":",
        " ",
        "\t",
        "\n",
        "\r",
    ]
    for char in invalid_chars:
        if char in name:
            raise ValidationError(
                f"Invalid component name: invalid character '{char}' in '{name}'"
            )

    # Check for unicode control characters and dangerous unicode
    for char in name:
        if ord(char) < 32 or ord(char) in [
            0x202E,
            0x200B,
            0xFEFF,
            0x2028,
            0x2029,
            0xFFFE,
            0xFFFF,
        ]:
            raise ValidationError(
                f"Invalid component name: dangerous unicode character in '{name}'"
            )

    # Check for environment variable patterns
    if name.startswith("$") or "${" in name or "`" in name:
        raise ValidationError(
            f"Invalid component name: environment variable pattern detected in '{name}'"
        )

    # Check if name starts with a digit (invalid for Python identifiers)
    if name and name[0].isdigit():
        raise ValidationError(
            f"Invalid component name: '{name}' cannot start with a digit"
        )

    # Ensure it would make a valid Python identifier after sanitization
    sanitized = sanitize_name(name)
    if not validate_python_identifier(sanitized):
        raise ValidationError(
            f"Invalid component name: '{name}' cannot be converted to valid Python identifier"
        )


def get_template_variables(
    system_name: str,
    module_name: str,
    component_name: str,
    component_type: str,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Generate template variables for rendering."""
    snake_name = to_snake_case(component_name)
    pascal_name = to_pascal_case(component_name)
    camel_name = to_camel_case(component_name)

    # System and module variations
    system_snake = to_snake_case(system_name)
    system_pascal = to_pascal_case(system_name)
    system_camel = to_camel_case(system_name)

    module_snake = to_snake_case(module_name)
    module_pascal = to_pascal_case(module_name)
    module_camel = to_camel_case(module_name)

    component_type_snake = to_snake_case(component_type)
    component_type_pascal = to_pascal_case(component_type)
    component_type_camel = to_camel_case(component_type)

    variables = {
        # System variations
        "system_name": system_snake,
        "SystemName": system_pascal,
        "system_name_camel": system_camel,
        # Module variations
        "module_name": module_snake,
        "ModuleName": module_pascal,
        "module_name_camel": module_camel,
        # Component variations
        "component_name": snake_name,
        "ComponentName": pascal_name,
        "component_name_camel": camel_name,
        # Component type variations
        "component_type": component_type_snake,
        "ComponentType": component_type_pascal,
        "component_type_camel": component_type_camel,
        # Common naming variations
        "entity_name": snake_name,
        "EntityName": pascal_name,
        "entity_name_camel": camel_name,
        "repository_name": snake_name,
        "RepositoryName": pascal_name,
        "repository_name_camel": camel_name,
        "service_name": snake_name,
        "ServiceName": pascal_name,
        "service_name_camel": camel_name,
        "router_name": snake_name,
        "RouterName": pascal_name,
        "router_name_camel": camel_name,
        "schema_name": snake_name,
        "SchemaName": pascal_name,
        "schema_name_camel": camel_name,
        "command_name": snake_name,
        "CommandName": pascal_name,
        "command_name_camel": camel_name,
        "query_name": snake_name,
        "QueryName": pascal_name,
        "query_name_camel": camel_name,
        "model_name": snake_name,
        "ModelName": pascal_name,
        "model_name_camel": camel_name,
        "value_object_name": snake_name,
        "ValueObjectName": pascal_name,
        "value_object_name_camel": camel_name,
        "external_service_name": snake_name,
        "ExternalServiceName": pascal_name,
        "external_service_name_camel": camel_name,
        "enum_name": snake_name,
        "EnumName": pascal_name,
        "enum_name_camel": camel_name,
        "dto_name": snake_name,
        "DtoName": pascal_name,
        "dto_name_camel": camel_name,
        # File naming
        "entity_file": f"{snake_name}.py",
        "repository_file": f"{snake_name}_repository.py",
        "service_file": f"{snake_name}_service.py",
        "router_file": f"{snake_name}_router.py",
        "schema_file": f"{snake_name}_schemas.py",
        "command_file": f"{snake_name}.py",
        "query_file": f"{snake_name}.py",
        "model_file": f"{snake_name}_model.py",
        "value_object_file": f"{snake_name}_value_object.py",
        "external_service_file": f"{snake_name}_external_service.py",
        "dto_file": f"{snake_name}_dto.py",
        # Resource naming (for APIs)
        "resource_name": snake_name,
        "resource_name_plural": pluralize(snake_name),
        # Descriptions
        "entity_description": f"{snake_name.replace('_', ' ')}",
        "service_description": f"{snake_name.replace('_', ' ')} operations",
        "module_description": f"{module_snake.replace('_', ' ')} module",
        # Import paths (for better import management)
        "domain_import_path": f"{system_snake}.{module_snake}.domain",
        "application_import_path": f"{system_snake}.{module_snake}.application",
        "infrastructure_import_path": f"{system_snake}.{module_snake}.infrastructure",
        "presentation_import_path": f"{system_snake}.{module_snake}.presentation",
        # Relative imports
        "entity_import": f"..domain.entities.{snake_name}",
        "repository_import": f"..domain.interfaces.{snake_name}_repository",
        "service_import": f"..application.services.{snake_name}_service",
        # Timestamp for file generation
        "generated_at": generate_timestamp(),
        "generator_version": __version__,
        # Additional naming patterns
        "table_name": pluralize(snake_name),
        "collection_name": pluralize(snake_name),
        "endpoint_prefix": f"/{pluralize(snake_name.replace('_', '-'))}",
        # Type hints
        "entity_type": pascal_name,
        "repository_type": f"{pascal_name}Repository",
        "service_type": f"{pascal_name}Service",
    }

    # Add any additional variables
    variables.update(kwargs)

    return variables


def ensure_directory(path: Path) -> None:
    """Ensure directory exists, create if it doesn't."""
    path.mkdir(parents=True, exist_ok=True)


def get_layer_from_path(path: str) -> Optional[str]:
    """Extract layer name from file path."""
    layers = ["domain", "application", "infrastructure", "presentation"]
    path_parts = Path(path).parts

    for layer in layers:
        if layer in path_parts:
            return layer

    return None


def get_component_type_from_path(path: str) -> Optional[str]:
    """Extract component type from file path using centralized configuration."""
    # Use all valid component types including nested ones
    component_types = list(ValidationRules.VALID_COMPONENT_TYPES)

    path_parts = Path(path).parts

    for comp_type in component_types:
        if comp_type in path_parts:
            return comp_type

    return None


def parse_location_path(location: str) -> Dict[str, str]:
    """Parse location path to extract system, module, layer, and component type.

    Args:
        location: Path like 'user_management/authentication/domain/entities'

    Returns:
        Dict with keys: system_name, module_name, layer, component_type
    """
    from .exceptions import ValidationError

    path_parts = Path(location).parts

    if len(path_parts) != 4:
        raise ValidationError(
            "Location must be in format: {{system}}/{{module}}/{{layer}}/{{component_type}}"
        )

    system_name = path_parts[0]
    module_name = path_parts[1]
    layer = path_parts[2]
    component_type = path_parts[3]

    # Validate and normalize layer using centralized validation
    from .validation import Validator

    layer_result = Validator.validate_layer(layer)
    if layer_result.is_failure:
        error = layer_result.error
        if error is not None:
            raise error
        else:
            raise ValidationError(
                f"Layer validation failed for '{layer}' but no error details available"
            )

    # Update layer to the normalized form - guaranteed to be str when validation succeeds
    validated_layer = layer_result.unwrap()

    # Validate component type based on layer using centralized configuration
    layer_components = ValidationRules.LAYER_COMPONENT_TYPES

    if component_type not in layer_components[validated_layer]:
        raise ValidationError(
            f"Invalid component type '{component_type}' for layer '{validated_layer}'. "
            f"Valid types: {layer_components[validated_layer]}"
        )

    return {
        "system_name": system_name,
        "module_name": module_name,
        "layer": validated_layer,
        "component_type": component_type,
    }


class ProjectScanner:
    """Scanner for detecting FCA project structure from filesystem."""

    def __init__(self, project_root: Path):
        """Initialize scanner with project root directory."""
        self.project_root = Path(project_root)
        self.systems_dir = self.project_root / "systems"

    def scan_project_structure(self) -> Dict[str, Any]:
        """Scan entire project structure and return discovered items."""
        from .validation import Validator

        discovered: Dict[str, Any] = {
            "systems": {},
            "untracked_files": [],
            "errors": [],
        }

        if not self.systems_dir.exists():
            discovered["errors"].append("No 'systems' directory found")
            return discovered

        # Scan for systems
        for system_path in self.systems_dir.iterdir():
            if not system_path.is_dir() or system_path.name.startswith("."):
                continue

            system_name = system_path.name

            # Validate system name
            validation_result = Validator.validate_system_name(system_name)
            if validation_result.is_failure:
                discovered["errors"].append(
                    f"Invalid system name '{system_name}': {validation_result.error}"
                )
                continue

            discovered["systems"][system_name] = self._scan_system(system_path)

        return discovered

    def _scan_system(self, system_path: Path) -> Dict[str, Any]:
        """Scan a single system directory."""
        from .validation import Validator

        system_data: Dict[str, Any] = {"modules": {}, "errors": []}

        # Scan for modules
        for module_path in system_path.iterdir():
            if not module_path.is_dir() or module_path.name.startswith("."):
                continue

            module_name = module_path.name

            # Validate module name
            validation_result = Validator.validate_module_name(module_name)
            if validation_result.is_failure:
                system_data["errors"].append(
                    f"Invalid module name '{module_name}': {validation_result.error}"
                )
                continue

            system_data["modules"][module_name] = self._scan_module(module_path)

        return system_data

    def _scan_module(self, module_path: Path) -> Dict[str, Any]:
        """Scan a single module directory."""

        module_data: Dict[str, Any] = {"layers": {}, "errors": []}

        # Expected layers
        layers = ["domain", "application", "infrastructure", "presentation"]

        for layer in layers:
            layer_path = module_path / layer
            if layer_path.exists() and layer_path.is_dir():
                module_data["layers"][layer] = self._scan_layer(layer_path, layer)

        return module_data

    def _scan_layer(self, layer_path: Path, layer_name: str) -> Dict[str, Any]:
        """Scan a single layer directory."""
        layer_data: Dict[str, Any] = {"component_types": {}, "errors": []}

        # Expected component types per layer using centralized configuration
        layer_components = ValidationRules.LAYER_COMPONENT_TYPES

        expected_types = layer_components.get(layer_name, [])

        for comp_type in expected_types:
            comp_type_path = layer_path / comp_type
            if comp_type_path.exists() and comp_type_path.is_dir():
                layer_data["component_types"][comp_type] = self._scan_component_type(
                    comp_type_path
                )

        return layer_data

    def _scan_component_type(self, comp_type_path: Path) -> Dict[str, Any]:
        """Scan a component type directory for Python files."""
        from .validation import Validator

        comp_data: Dict[str, Any] = {"components": [], "errors": []}

        # Scan for Python files
        for file_path in comp_type_path.iterdir():
            if (
                file_path.is_file()
                and file_path.suffix == ".py"
                and file_path.name != "__init__.py"
            ):

                # Extract component name from filename
                component_name = file_path.stem

                # Remove common suffixes to get base component name
                suffixes_to_remove = [
                    "_repository",
                    "_service",
                    "_model",
                    "_schemas",
                    "_value_object",
                    "_external_service",
                ]

                for suffix in suffixes_to_remove:
                    if component_name.endswith(suffix):
                        component_name = component_name[: -len(suffix)]
                        break

                # Validate component name
                validation_result = Validator.validate_component_name(component_name)
                if validation_result.is_failure:
                    comp_data["errors"].append(
                        f"Invalid component name '{component_name}' in {file_path}: {validation_result.error}"
                    )
                    continue

                comp_data["components"].append(
                    {
                        "name": component_name,
                        "file_path": str(file_path.relative_to(self.project_root)),
                        "full_path": str(file_path),
                    }
                )

        return comp_data

    def find_untracked_components(
        self, current_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Find components that exist in filesystem but not in config."""
        discovered = self.scan_project_structure()
        untracked = {
            "systems": {},
            "modules": {},
            "components": [],
            "errors": discovered["errors"],
        }

        # Get current config data
        config_systems = current_config.get("systems", {})

        # Check for untracked systems
        for system_name, system_data in discovered["systems"].items():
            system_is_untracked = system_name not in config_systems

            if system_is_untracked:
                untracked["systems"][system_name] = system_data
                # For untracked systems, all modules are also untracked
                for module_name, module_data in system_data["modules"].items():
                    module_key = f"{system_name}/{module_name}"
                    untracked["modules"][module_key] = module_data

                    # Also add all components within these modules
                    self._find_untracked_components_in_module(
                        system_name,
                        module_name,
                        module_data,
                        {},
                        untracked[
                            "components"
                        ],  # Empty config_components since system is untracked
                    )
            else:
                # System exists in config, check for untracked modules
                config_modules = config_systems[system_name].get("modules", {})
                for module_name, module_data in system_data["modules"].items():
                    if module_name not in config_modules:
                        module_key = f"{system_name}/{module_name}"
                        untracked["modules"][module_key] = module_data

                        # Also add all components within this untracked module
                        self._find_untracked_components_in_module(
                            system_name,
                            module_name,
                            module_data,
                            {},
                            untracked[
                                "components"
                            ],  # Empty config_components since module is untracked
                        )
                    else:
                        # Module exists in config, check for untracked components
                        config_components = config_modules[module_name].get(
                            "components", {}
                        )
                        self._find_untracked_components_in_module(
                            system_name,
                            module_name,
                            module_data,
                            config_components,
                            untracked["components"],
                        )

        return untracked

    def _find_untracked_components_in_module(
        self,
        system_name: str,
        module_name: str,
        module_data: Dict[str, Any],
        config_components: Dict[str, Any],
        untracked_components: List[Dict[str, Any]],
    ) -> None:
        """Find untracked components within a specific module."""
        for layer_name, layer_data in module_data["layers"].items():
            for comp_type, comp_type_data in layer_data["component_types"].items():
                for component in comp_type_data["components"]:
                    component_name = component["name"]

                    # Check if component exists in config
                    # Config structure: config_components[layer][component_type][component_name]
                    component_exists = (
                        layer_name in config_components
                        and comp_type in config_components[layer_name]
                        and component_name in config_components[layer_name][comp_type]
                    )

                    if not component_exists:
                        untracked_components.append(
                            {
                                "system": system_name,
                                "module": module_name,
                                "layer": layer_name,
                                "component_type": comp_type,
                                "name": component_name,
                                "file_path": component["file_path"],
                                "full_path": component["full_path"],
                            }
                        )
