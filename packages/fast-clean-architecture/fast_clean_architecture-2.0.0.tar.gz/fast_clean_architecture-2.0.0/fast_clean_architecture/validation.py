"""Validation utilities for Fast Clean Architecture."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Set, Union

from .exceptions import Result, SecurityError, ValidationError


class ValidationRules:
    """Centralized validation rules and patterns."""

    # Component naming patterns
    COMPONENT_NAME_PATTERN: Pattern[str] = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")
    SYSTEM_NAME_PATTERN: Pattern[str] = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")
    MODULE_NAME_PATTERN: Pattern[str] = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")

    # Security patterns
    DANGEROUS_PATH_PATTERNS: List[Pattern[str]] = [
        re.compile(r"\.\."),  # Path traversal
        re.compile(r"^/etc/|^/root/|^/proc/|^/sys/"),  # Dangerous system paths only
        re.compile(r"^~"),  # Home directory
        re.compile(r"\$\{"),  # Variable expansion
        re.compile(r"\$\("),  # Command substitution
    ]

    # Valid component types and layers
    VALID_LAYERS: Set[str] = {"domain", "application", "infrastructure", "presentation"}

    # Layer normalization mapping (plural to singular)
    LAYER_NORMALIZATION: Dict[str, str] = {
        "domains": "domain",
        "applications": "application",
        "infrastructures": "infrastructure",
        "presentations": "presentation",
    }

    @classmethod
    def normalize_layer(cls, layer: str) -> str:
        """Normalize layer name by converting common plural forms to singular.

        Args:
            layer: The layer name to normalize

        Returns:
            The normalized layer name
        """
        return cls.LAYER_NORMALIZATION.get(layer, layer)

    # Layer-specific component types mapping (aligned with Clean Architecture)
    LAYER_COMPONENT_TYPES: Dict[str, List[str]] = {
        "domain": [
            "entities",
            "events",
            "exceptions",
            "interfaces",
            "value_objects",
            "enums",
        ],
        "application": ["dtos", "services", "use_cases"],
        "infrastructure": ["config", "external", "database"],
        "presentation": ["controllers", "middleware", "routes", "schemas"],
    }

    # Nested component types for use_cases
    USE_CASES_COMPONENT_TYPES: Set[str] = {"commands", "queries"}

    # Nested component types for database
    DATABASE_COMPONENT_TYPES: Set[str] = {"migrations", "models", "repositories"}

    # Global component types (flattened from all layers)
    VALID_COMPONENT_TYPES: Set[str] = {
        "entities",
        "services",
        "controllers",
        "external",
        "value_objects",
        "use_cases",
        "commands",  # Nested under use_cases
        "queries",  # Nested under use_cases
        "schemas",
        "events",
        "exceptions",
        "interfaces",
        "enums",
        "dtos",
        "config",
        "database",
        "migrations",  # Nested under database
        "models",  # Nested under database
        "repositories",  # Nested under database
        "middleware",
        "routes",
    }

    @classmethod
    def validate_nested_component_type(
        cls, layer: str, component_type: str, nested_type: Optional[str] = None
    ) -> Result[bool, ValidationError]:
        """Validate component type with support for nested structures.

        Args:
            layer: The architecture layer
            component_type: The component type (e.g., 'use_cases', 'database')
            nested_type: Optional nested type (e.g., 'commands', 'queries', 'migrations', 'models', 'repositories')

        Returns:
            Result indicating validation success or failure
        """
        # Validate layer first
        if layer not in cls.VALID_LAYERS:
            return Result.failure(ValidationError(f"Invalid layer: {layer}"))

        # Get valid component types for the layer
        valid_types = cls.LAYER_COMPONENT_TYPES.get(layer, [])

        # Check if component type is directly valid for the layer
        if component_type in valid_types:
            # Handle nested validation for use_cases
            if component_type == "use_cases" and nested_type:
                if nested_type not in cls.USE_CASES_COMPONENT_TYPES:
                    return Result.failure(
                        ValidationError(
                            f"Invalid nested type '{nested_type}' for use_cases. Valid options: {', '.join(cls.USE_CASES_COMPONENT_TYPES)}"
                        )
                    )

            # Handle nested validation for database
            elif component_type == "database" and nested_type:
                if nested_type not in cls.DATABASE_COMPONENT_TYPES:
                    return Result.failure(
                        ValidationError(
                            f"Invalid nested type '{nested_type}' for database. Valid options: {', '.join(cls.DATABASE_COMPONENT_TYPES)}"
                        )
                    )

            return Result.success(True)

        # Check if it's a nested component type that should be allowed
        # Check if it's a nested use_cases component type
        if (
            component_type in cls.USE_CASES_COMPONENT_TYPES
            and "use_cases" in valid_types
        ):
            return Result.success(True)

        # Check if it's a nested database component type
        if component_type in cls.DATABASE_COMPONENT_TYPES and "database" in valid_types:
            return Result.success(True)

        # Build comprehensive list of valid types including nested ones
        all_valid_types = list(valid_types)
        if "use_cases" in valid_types:
            all_valid_types.extend(cls.USE_CASES_COMPONENT_TYPES)
        if "database" in valid_types:
            all_valid_types.extend(cls.DATABASE_COMPONENT_TYPES)

        return Result.failure(
            ValidationError(
                f"Component type '{component_type}' not valid for layer '{layer}'. "
                f"Valid types: {', '.join(sorted(set(all_valid_types)))}"
            )
        )

    # File extension validation
    ALLOWED_EXTENSIONS: Set[str] = {
        ".py",
        ".yaml",
        ".yml",
        ".json",
        ".md",
        ".txt",
        ".toml",
    }


class Validator:
    """Main validation class with comprehensive checks."""

    @staticmethod
    def validate_component_name(name: str) -> Result[str, ValidationError]:
        """Validate component name format."""
        if not name:
            return Result.failure(
                ValidationError(
                    "Component name cannot be empty", context={"name": name}
                )
            )

        if not ValidationRules.COMPONENT_NAME_PATTERN.match(name):
            return Result.failure(
                ValidationError(
                    f"Invalid component name format: {name}. Must start with letter and contain only letters, numbers, and underscores.",
                    context={
                        "name": name,
                        "pattern": ValidationRules.COMPONENT_NAME_PATTERN.pattern,
                    },
                )
            )

        if len(name) > 50:
            return Result.failure(
                ValidationError(
                    f"Component name too long: {len(name)} characters. Maximum 50 allowed.",
                    context={"name": name, "length": len(name)},
                )
            )

        return Result.success(name)

    @staticmethod
    def validate_system_name(name: str) -> Result[str, ValidationError]:
        """Validate system name format."""
        if not name:
            return Result.failure(
                ValidationError("System name cannot be empty", context={"name": name})
            )

        if not ValidationRules.SYSTEM_NAME_PATTERN.match(name):
            return Result.failure(
                ValidationError(
                    f"Invalid system name format: {name}. Must start with letter and contain only letters, numbers, underscores, and hyphens.",
                    context={
                        "name": name,
                        "pattern": ValidationRules.SYSTEM_NAME_PATTERN.pattern,
                    },
                )
            )

        return Result.success(name)

    @staticmethod
    def validate_module_name(name: str) -> Result[str, ValidationError]:
        """Validate module name format."""
        if not name:
            return Result.failure(
                ValidationError("Module name cannot be empty", context={"name": name})
            )

        if not ValidationRules.MODULE_NAME_PATTERN.match(name):
            return Result.failure(
                ValidationError(
                    f"Invalid module name format: {name}. Must start with letter and contain only letters, numbers, and underscores.",
                    context={
                        "name": name,
                        "pattern": ValidationRules.MODULE_NAME_PATTERN.pattern,
                    },
                )
            )

        return Result.success(name)

    @staticmethod
    def validate_layer(layer: str) -> Result[str, ValidationError]:
        """Validate layer name."""
        # Normalize layer name (handle common plural forms)
        normalized_layer = ValidationRules.normalize_layer(layer)

        if normalized_layer not in ValidationRules.VALID_LAYERS:
            # Provide helpful error message with suggestions
            suggestions = []
            if layer in ValidationRules.LAYER_NORMALIZATION:
                suggestions.append(
                    f"Did you mean '{ValidationRules.LAYER_NORMALIZATION[layer]}' instead of '{layer}'?"
                )

            error_msg = f"Invalid layer: {layer}. Must be one of: {', '.join(sorted(ValidationRules.VALID_LAYERS))}"
            if suggestions:
                error_msg += f" | {' '.join(suggestions)}"

            return Result.failure(
                ValidationError(
                    error_msg,
                    context={
                        "layer": layer,
                        "normalized_layer": normalized_layer,
                        "valid_layers": list(ValidationRules.VALID_LAYERS),
                        "suggestions": suggestions,
                    },
                )
            )

        return Result.success(normalized_layer)

    @staticmethod
    def validate_component_type_for_layer(
        component_type: str, layer: str
    ) -> Result[str, ValidationError]:
        """Validate component type for a specific layer using enhanced layer-aware validation.

        Args:
            component_type: The component type to validate
            layer: The layer where the component will be created

        Returns:
            Result containing the validated component type or validation error
        """
        # Normalize layer name
        normalized_layer = ValidationRules.normalize_layer(layer)

        # Use the enhanced nested component validation
        validation_result = ValidationRules.validate_nested_component_type(
            layer=normalized_layer, component_type=component_type
        )

        if validation_result.is_failure:
            return Result.failure(validation_result.error)  # type: ignore

        return Result.success(component_type)

    @staticmethod
    def validate_file_path(file_path: Union[str, Path]) -> Result[Path, SecurityError]:
        """Validate file path for security issues."""
        path_str = str(file_path)

        # Check for dangerous patterns
        for pattern in ValidationRules.DANGEROUS_PATH_PATTERNS:
            if pattern.search(path_str):
                return Result.failure(
                    SecurityError(
                        f"Potentially dangerous path pattern detected: {path_str}",
                        context={"path": path_str, "pattern": pattern.pattern},
                    )
                )

        # Convert to Path object
        try:
            path_obj = Path(path_str)
        except Exception as e:
            return Result.failure(
                SecurityError(
                    f"Invalid path format: {path_str}",
                    context={"path": path_str, "error": str(e)},
                )
            )

        # Check file extension
        if (
            path_obj.suffix
            and path_obj.suffix not in ValidationRules.ALLOWED_EXTENSIONS
        ):
            return Result.failure(
                SecurityError(
                    f"File extension not allowed: {path_obj.suffix}",
                    context={
                        "path": path_str,
                        "extension": path_obj.suffix,
                        "allowed": list(ValidationRules.ALLOWED_EXTENSIONS),
                    },
                )
            )

        return Result.success(path_obj)

    @staticmethod
    def validate_description(
        description: str, max_length: int = 500
    ) -> Result[str, Union[ValidationError, SecurityError]]:
        """Validate description text."""
        if len(description) > max_length:
            return Result.failure(
                ValidationError(
                    f"Description too long: {len(description)} characters. Maximum {max_length} allowed.",
                    context={
                        "description": description[:100] + "...",
                        "length": len(description),
                        "max_length": max_length,
                    },
                )
            )

        # Check for potentially dangerous content
        dangerous_patterns = ["<script", "${", "$(", "javascript:"]
        for pattern in dangerous_patterns:
            if pattern.lower() in description.lower():
                return Result.failure(
                    SecurityError(
                        f"Potentially dangerous content in description: {pattern}",
                        context={
                            "description": description[:100] + "...",
                            "pattern": pattern,
                        },
                    )
                )

        return Result.success(description)

    @classmethod
    def validate_component_creation(
        cls,
        system_name: str,
        module_name: str,
        layer: str,
        component_type: str,
        component_name: str,
        file_path: Optional[Union[str, Path]] = None,
        description: Optional[str] = None,
    ) -> Result[Dict[str, Any], Union[ValidationError, SecurityError]]:
        """Comprehensive validation for component creation."""

        # Validate all required fields
        system_validation = cls.validate_system_name(system_name)
        if system_validation.is_failure:
            return system_validation  # type: ignore

        module_validation = cls.validate_module_name(module_name)
        if module_validation.is_failure:
            return module_validation  # type: ignore

        layer_validation = cls.validate_layer(layer)
        if layer_validation.is_failure:
            return layer_validation  # type: ignore

        # Get the validated layer value (guaranteed to be str after successful validation)
        validated_layer = layer_validation.unwrap()
        component_type_validation = cls.validate_component_type_for_layer(
            component_type, validated_layer
        )
        if component_type_validation.is_failure:
            return component_type_validation  # type: ignore

        component_name_validation = cls.validate_component_name(component_name)
        if component_name_validation.is_failure:
            return component_name_validation  # type: ignore

        # Validate optional fields
        validated_file_path = None
        if file_path is not None:
            file_validation = cls.validate_file_path(file_path)
            if file_validation.is_failure:
                return file_validation  # type: ignore
            else:
                validated_file_path = file_validation.unwrap()

        if description is not None:
            description_validation = cls.validate_description(description)
            if description_validation.is_failure:
                return description_validation  # type: ignore

        # Return validated data
        validated_data = {
            "system_name": system_name,
            "module_name": module_name,
            "layer": layer,
            "component_type": component_type,
            "component_name": component_name,
        }

        if validated_file_path is not None:
            validated_data["file_path"] = str(validated_file_path)

        if description is not None:
            validated_data["description"] = description

        return Result.success(validated_data)
