"""Protocol definitions for enhanced type safety in Fast Clean Architecture.

This module provides protocol-based interfaces that enable better type checking,
modular design, and enhanced security through type constraints.
"""

from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    TypeVar,
    Union,
    runtime_checkable,
)

if TYPE_CHECKING:
    from .generators.validation_config import ValidationMetrics

from .config import Config
from .exceptions import SecurityError, ValidationError

# Type variables for generic constraints
T = TypeVar("T", bound=Union[str, Path])
ComponentType = TypeVar("ComponentType", bound=str)
T_contra = TypeVar("T_contra", contravariant=True)


@runtime_checkable
class ComponentGeneratorProtocol(Protocol):
    """Protocol for component generators with type safety guarantees.

    This protocol ensures that all component generators implement
    the required methods with proper type annotations and error handling.
    """

    # Required attributes
    config: "Config"
    template_validator: "TemplateValidatorProtocol"
    path_handler: "SecurePathHandler[Union[str, Path]]"

    def create_component(
        self,
        base_path: Path,
        system_name: str,
        module_name: str,
        layer: str,
        component_type: str,
        component_name: str,
        dry_run: bool = False,
        force: bool = False,
        template_variant: Optional[str] = None,
        nested_type: Optional[str] = None,
    ) -> Path:
        """Create a component with validated inputs and secure file operations.

        Args:
            base_path: Base directory for component creation
            system_name: Name of the system (validated)
            module_name: Name of the module (validated)
            layer: Architecture layer (domain, application, etc.)
            component_type: Type of component (entity, service, etc.)
            component_name: Name of the component (validated)
            dry_run: If True, only simulate the operation
            force: If True, overwrite existing files
            template_variant: Optional template variant (e.g., simple, full, api for enums)
            nested_type: Optional nested component type (e.g., commands, queries for use_cases)

        Returns:
            Path to the created component file

        Raises:
            ValidationError: If inputs are invalid
            ComponentError: If component creation fails
            SecurityError: If security constraints are violated
        """
        ...

    def validate_component(self, component: Dict[str, Any]) -> bool:
        """Validate component configuration and structure.

        Args:
            component: Component configuration dictionary

        Returns:
            True if component is valid

        Raises:
            ValidationError: If component is invalid
        """
        ...

    def create_multiple_components(
        self,
        base_path: Path,
        system_name: str,
        module_name: str,
        components_spec: Dict[str, Union[Dict[str, List[str]], Dict[str, Union[List[str], Dict[str, List[str]]]]]],
        dry_run: bool = False,
        force: bool = False,
    ) -> List[Path]:
        """Create multiple components from specification.

        Args:
            base_path: Base directory for component creation
            system_name: Name of the system (validated)
            module_name: Name of the module (validated)
            components_spec: Dict like {
                "domain": {"entities": ["user", "order"], "repositories": ["user"]},
                "application": {"services": ["user_service"]}
            }
            dry_run: If True, only simulate the operation
            force: If True, overwrite existing files

        Returns:
            List of paths to created component files

        Raises:
            ValidationError: If inputs are invalid
            ComponentError: If component creation fails
            SecurityError: If security constraints are violated
        """
        ...


@runtime_checkable
class SecurePathHandlerProtocol(Protocol, Generic[T]):
    """Protocol for secure path handling with generic type constraints.

    This protocol ensures type-safe path operations with security validation.
    """

    def process(self, path: T) -> T:
        """Process a path with security validation.

        Args:
            path: Input path (str or Path)

        Returns:
            Processed and validated path of the same type

        Raises:
            SecurityError: If path contains security violations
            ValidationError: If path is invalid
        """
        ...

    def validate_path_security(self, path: T) -> bool:
        """Validate path for security constraints.

        Args:
            path: Path to validate

        Returns:
            True if path is secure
        """
        ...


@runtime_checkable
class TemplateValidatorProtocol(Protocol):
    """Protocol for template validation with security constraints."""

    def validate(
        self, template_source: str, template_vars: Dict[str, Any]
    ) -> "ValidationMetrics":
        """Validate template source and variables.

        Args:
            template_source: Template source code
            template_vars: Template variables

        Returns:
            ValidationMetrics: Metrics from the validation process

        Raises:
            TemplateError: If template is invalid or insecure
        """
        ...

    def sanitize_variables(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize template variables for security.

        Args:
            variables: Raw template variables

        Returns:
            Sanitized variables
        """
        ...


@runtime_checkable
class ValidationStrategyProtocol(Protocol, Generic[T_contra]):
    """Protocol for validation strategies with generic type support."""

    def validate(self, value: T_contra) -> object:
        """Validate a value according to strategy rules.

        Args:
            value: Value to validate

        Returns:
            Validation result
        """
        ...

    def get_error_message(self, value: T_contra) -> str:
        """Get descriptive error message for validation failure.

        Args:
            value: Invalid value

        Returns:
            Error message
        """
        ...


class SecurePathHandler(Generic[T]):
    """Concrete implementation of secure path handling with generic type constraints.

    This class provides type-safe path operations with security validation,
    supporting both string and Path types while maintaining type consistency.
    """

    def __init__(
        self,
        max_path_length: int = 4096,
        allowed_extensions: Optional[List[str]] = None,
    ):
        """Initialize secure path handler.

        Args:
            max_path_length: Maximum allowed path length
            allowed_extensions: List of allowed file extensions (None for no restriction)
        """
        self.max_path_length = max_path_length
        self.allowed_extensions = allowed_extensions or []

        # Security patterns to detect
        self._dangerous_patterns = [
            r"\.\.",  # Path traversal
            r'[<>:"|?*]',  # Invalid filename characters
            r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$",  # Windows reserved names
            r"\x00",  # Null bytes
        ]

    def process(self, path: T) -> T:
        """Process a path with comprehensive security validation.

        Args:
            path: Input path (str or Path)

        Returns:
            Processed and validated path of the same type

        Raises:
            SecurityError: If path contains security violations
            ValidationError: If path is invalid
        """
        # Convert to string for validation
        path_str = str(path)

        # Validate path security
        if not self.validate_path_security(path):
            from .exceptions import SecurityError

            raise SecurityError(
                f"Path security validation failed: {path_str}",
                security_check="path_traversal_prevention",
            )

        # Validate path length
        if len(path_str) > self.max_path_length:
            raise ValidationError(
                f"Path too long: {len(path_str)} > {self.max_path_length}"
            )

        # Validate file extension if specified
        if self.allowed_extensions:
            path_obj = Path(path_str)
            if path_obj.suffix and path_obj.suffix not in self.allowed_extensions:
                raise ValidationError(f"File extension not allowed: {path_obj.suffix}")

        # Return same type as input
        if isinstance(path, Path):
            return Path(path_str)  # type: ignore
        return path_str  # type: ignore

    def validate_path_security(self, path: T) -> bool:
        """Validate path for security constraints.

        Args:
            path: Path to validate

        Returns:
            True if path is secure
        """
        import re

        path_str = str(path)

        # Check for dangerous patterns
        for pattern in self._dangerous_patterns:
            if re.search(pattern, path_str, re.IGNORECASE):
                return False

        # Additional security checks
        try:
            # Resolve path to detect traversal attempts
            resolved = Path(path_str).resolve()

            # Check if resolved path escapes intended directory
            # This is a basic check - more sophisticated logic may be needed
            if ".." in str(resolved):
                return False

        except (OSError, ValueError):
            return False

        return True


class ComponentValidationStrategy(Generic[ComponentType]):
    """Generic validation strategy for different component types.

    This class provides type-safe validation for various component types
    while maintaining consistency across the validation process.
    """

    def __init__(self, component_type: ComponentType, validation_rules: Dict[str, Any]):
        """Initialize validation strategy.

        Args:
            component_type: Type of component to validate
            validation_rules: Rules specific to this component type
        """
        self.component_type = component_type
        self.validation_rules = validation_rules

    def validate(self, component_data: Dict[str, Any]) -> bool:
        """Validate component data according to type-specific rules.

        Args:
            component_data: Component configuration data

        Returns:
            True if component is valid

        Raises:
            ValidationError: If component is invalid
        """
        # Basic validation
        if not isinstance(component_data, dict):
            raise ValidationError(
                f"Component data must be a dictionary, got {type(component_data)}"
            )

        # Check required fields
        required_fields = self.validation_rules.get("required_fields", [])
        for field in required_fields:
            if field not in component_data:
                raise ValidationError(
                    f"Missing required field '{field}' for {self.component_type}"
                )

        # Validate field types
        field_types = self.validation_rules.get("field_types", {})
        for field, expected_type in field_types.items():
            if field in component_data:
                if not isinstance(component_data[field], expected_type):
                    raise ValidationError(
                        f"Field '{field}' must be of type {expected_type.__name__}, "
                        f"got {type(component_data[field]).__name__}"
                    )

        # Validate component name for security if present
        if "name" in component_data:
            from fast_clean_architecture.utils import validate_name

            try:
                validate_name(component_data["name"])
            except (ValueError, TypeError) as e:
                raise ValidationError(f"Invalid component name: {e}")
            except SecurityError:
                # Re-raise SecurityError as-is for proper handling
                raise

        return True

    def get_error_message(self, component_data: Dict[str, Any]) -> str:
        """Get descriptive error message for validation failure.

        Args:
            component_data: Invalid component data

        Returns:
            Descriptive error message
        """
        try:
            self.validate(component_data)
            return "No validation errors found"
        except ValidationError as e:
            return f"Validation failed for {self.component_type}: {str(e)}"
