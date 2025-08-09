"""Custom exceptions for Fast Clean Architecture."""

import time
from pathlib import Path
from typing import Any, Callable, Dict, Generic, List, Optional, Set, TypeVar, Union

U = TypeVar("U")


class FastCleanArchitectureError(Exception):
    """Base exception for all Fast Clean Architecture errors.

    Enhanced with better context handling, error chaining, and debugging support.
    """

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.error_code = error_code
        self.suggestions = suggestions or []
        self.timestamp = time.time()
        self.cause = cause

        # Add stack trace context for debugging
        if cause:
            self.__cause__ = cause

    def add_context(self, key: str, value: Any) -> "FastCleanArchitectureError":
        """Add context information to the error."""
        self.context[key] = value
        return self

    def add_suggestion(self, suggestion: str) -> "FastCleanArchitectureError":
        """Add a suggestion for resolving the error."""
        self.suggestions.append(suggestion)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/serialization."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "context": self.context,
            "suggestions": self.suggestions,
            "timestamp": self.timestamp,
            "cause": str(self.cause) if self.cause else None,
        }

    def __str__(self) -> str:
        """Enhanced string representation with context and suggestions."""
        parts = [self.message]

        if self.error_code:
            parts.append(f"Error Code: {self.error_code}")

        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")

        if self.suggestions:
            suggestions_str = "; ".join(self.suggestions)
            parts.append(f"Suggestions: {suggestions_str}")

        return " | ".join(parts)


class ConfigurationError(FastCleanArchitectureError):
    """Raised when there's an issue with configuration."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        config_path: Optional[Path] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message=message, context=context, error_code="CONFIG_ERROR", cause=cause
        )
        if config_path:
            self.add_context("config_path", str(config_path))
            self.add_suggestion(f"Check configuration file at: {config_path}")


class ValidationError(FastCleanArchitectureError):
    """Raised when validation fails."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        field_name: Optional[str] = None,
        invalid_value: Optional[Any] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message=message, context=context, error_code="VALIDATION_ERROR", cause=cause
        )
        if field_name:
            self.add_context("field_name", field_name)
        if invalid_value is not None:
            self.add_context("invalid_value", str(invalid_value))
            self.add_suggestion("Check the input value format and constraints")


class SecurityError(FastCleanArchitectureError):
    """Raised when security validation fails."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        security_check: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            context=context,
            error_code="SECURITY_ERROR",
            suggestions=[
                "Review input for potential security issues",
                "Check file paths and user input validation",
            ],
            cause=cause,
        )
        if security_check:
            self.add_context("security_check", security_check)


class FileConflictError(FastCleanArchitectureError):
    """Raised when there's a file or directory conflict."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        file_path: Optional[Path] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            context=context,
            error_code="FILE_CONFLICT",
            suggestions=[
                "Use --force flag to overwrite",
                "Choose a different location",
                "Remove existing files first",
            ],
            cause=cause,
        )
        if file_path:
            self.add_context("file_path", str(file_path))


class TemplateError(FastCleanArchitectureError):
    """Raised when there's an issue with template rendering."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        template_name: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message=message, context=context, error_code="TEMPLATE_ERROR", cause=cause
        )
        if template_name:
            self.add_context("template_name", template_name)
            self.add_suggestion(f"Check template file: {template_name}")


class TemplateValidationError(TemplateError):
    """Base class for template validation errors."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        template_name: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message=message, context=context, template_name=template_name, cause=cause
        )
        self.error_code = "TEMPLATE_VALIDATION_ERROR"


class TemplateMissingVariablesError(TemplateValidationError):
    """Raised when required template variables are missing."""

    def __init__(
        self,
        missing_vars: Set[str],
        message: Optional[str] = None,
        template_name: Optional[str] = None,
    ):
        self.missing_vars = missing_vars
        if message is None:
            message = f"Missing required template variables: {', '.join(sorted(missing_vars))}"

        super().__init__(message=message, template_name=template_name)
        self.add_context("missing_variables", list(sorted(missing_vars)))
        self.add_suggestion("Provide all required template variables")
        self.error_code = "TEMPLATE_MISSING_VARS"


class TemplateUndefinedVariableError(TemplateValidationError):
    """Raised when template contains undefined variables during rendering."""

    def __init__(
        self,
        variable_name: str,
        message: Optional[str] = None,
        template_name: Optional[str] = None,
    ):
        self.variable_name = variable_name
        if message is None:
            message = f"Undefined template variable: {variable_name}"

        super().__init__(message=message, template_name=template_name)
        self.add_context("undefined_variable", variable_name)
        self.add_suggestion(f"Define variable '{variable_name}' in template context")
        self.error_code = "TEMPLATE_UNDEFINED_VAR"


class ComponentError(FastCleanArchitectureError):
    """Raised when there's an issue with component generation."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        component_name: Optional[str] = None,
        component_type: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(
            message=message, context=context, error_code="COMPONENT_ERROR", cause=cause
        )
        if component_name:
            self.add_context("component_name", component_name)
        if component_type:
            self.add_context("component_type", component_type)
            self.add_suggestion(f"Check {component_type} component requirements")


# Error Handling Utilities
def create_secure_error(
    error_type: str, operation: str, details: Optional[str] = None
) -> SecurityError:
    """Create a SecurityError with standardized context."""
    error = SecurityError(
        f"Security violation during {operation}: {details or error_type}"
    )
    error.add_context("error_type", error_type).add_context("operation", operation)
    return error


def create_validation_error(
    field: str, value: Any, reason: str, suggestions: Optional[List[str]] = None
) -> ValidationError:
    """Create a validation error with standardized format."""
    message = f"Validation failed for {field}: {reason}"
    error = ValidationError(message=message, field_name=field, invalid_value=value)
    if suggestions:
        for suggestion in suggestions:
            error.add_suggestion(suggestion)
    return error


def create_config_error(
    operation: str,
    details: str,
    config_path: Optional[Path] = None,
    cause: Optional[Exception] = None,
) -> ConfigurationError:
    """Create a configuration error with standardized format."""
    message = f"Configuration error during {operation}: {details}"
    return ConfigurationError(
        message=message,
        config_path=config_path,
        cause=cause,
        context={"operation": operation},
    )


class ErrorContext:
    """Context manager for enhanced error handling."""

    def __init__(self, operation: str, **context: Any) -> None:
        self.operation = operation
        self.context = context

    def __enter__(self) -> "ErrorContext":
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> Optional[bool]:
        if exc_type and issubclass(exc_type, FastCleanArchitectureError):
            # Enhance existing FCA errors with context
            if exc_val and isinstance(exc_val, FastCleanArchitectureError):
                exc_val.add_context("operation", self.operation)
                for key, value in self.context.items():
                    exc_val.add_context(key, value)
        elif exc_type and exc_type != FastCleanArchitectureError:
            # Wrap other exceptions in FCA error
            enhanced_error = FastCleanArchitectureError(
                message=f"Error during {self.operation}: {str(exc_val)}",
                context=self.context,
                cause=exc_val,
            )
            raise enhanced_error from exc_val
        return None


# Result Pattern for Better Error Handling
T = TypeVar("T")
E = TypeVar("E", bound=Exception)


_SENTINEL = object()  # Module-level sentinel to detect when no value is provided


class Result(Generic[T, E]):
    """Result type for better error handling without exceptions."""

    def __init__(self, value: Union[T, object] = _SENTINEL, error: Optional[E] = None):
        # Check if both value and error are explicitly provided
        if value is not _SENTINEL and error is not None:
            raise ValueError("Result cannot have both value and error")
        # Check if neither value nor error are provided
        if value is _SENTINEL and error is None:
            raise ValueError("Result must have either value or error")

        # Set the actual values
        self._value: Optional[T] = value if value is not _SENTINEL else None  # type: ignore
        self._error = error

    @classmethod
    def success(cls, value: T) -> "Result[T, E]":
        """Create a successful result."""
        return cls(value=value)

    @classmethod
    def failure(cls, error: E) -> "Result[T, E]":
        """Create a failed result."""
        return cls(error=error)

    @property
    def is_success(self) -> bool:
        """Check if result is successful."""
        return self._error is None

    @property
    def is_failure(self) -> bool:
        """Check if result is a failure."""
        return self._error is not None

    def unwrap(self) -> T:
        """Get the value, raising the error if failed."""
        if self._error is not None:
            raise self._error
        return self._value  # type: ignore

    def unwrap_or(self, default: T) -> T:
        """Get the value or return default if failed."""
        return self._value if self._error is None else default  # type: ignore

    def map(self, func: Callable[[T], U]) -> "Result[U, E]":
        """Transform the value if successful, preserving the error type."""
        if self._error is not None:
            return Result.failure(self._error)
        try:
            return Result.success(func(self._value))  # type: ignore
        except Exception as e:
            # When map function raises an exception, we need to handle it carefully
            # Since we want to preserve the error type E, we can only do this if
            # the exception is compatible with E or if we have a way to convert it
            if isinstance(e, Exception) and hasattr(self, "_error_type_hint"):
                # Try to convert the exception to the expected error type
                return Result.failure(e)  # type: ignore
            # Re-raise the exception to preserve error information
            raise

    def and_then(self, func: Callable[[T], "Result[Any, E]"]) -> "Result[Any, E]":
        """Chain operations that return Results."""
        if self._error is not None:
            return Result.failure(self._error)
        return func(self._value)  # type: ignore

    @property
    def error(self) -> Optional[E]:
        """Get the error if any."""
        return self._error

    @property
    def value(self) -> Optional[T]:
        """Get the value if successful."""
        return self._value

    def map_error(self, func: Callable[[E], Any]) -> "Result[T, Exception]":
        """Transform the error if failed."""
        if self._error is None:
            return Result.success(self._value)  # type: ignore
        try:
            new_error = func(self._error)
            if isinstance(new_error, Exception):
                return Result.failure(new_error)
            else:
                return Result.failure(Exception(str(new_error)))
        except Exception as e:
            return Result.failure(e)

    def or_else(self, func: Callable[[E], "Result[T, Any]"]) -> "Result[T, Any]":
        """Provide alternative result if failed."""
        if self._error is None:
            return Result.success(self._value)  # type: ignore
        return func(self._error)

    def inspect(self, func: Callable[[T], None]) -> "Result[T, E]":
        """Inspect the value without changing the result."""
        if self._error is None and self._value is not None:
            func(self._value)
        return self

    def inspect_error(self, func: Callable[[E], None]) -> "Result[T, E]":
        """Inspect the error without changing the result."""
        if self._error is not None:
            func(self._error)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        if self.is_success:
            return {"success": True, "value": self._value, "error": None}
        else:
            error_dict = None
            if isinstance(self._error, FastCleanArchitectureError):
                error_dict = self._error.to_dict()
            else:
                error_dict = {
                    "error_type": self._error.__class__.__name__,
                    "message": str(self._error),
                }

            return {"success": False, "value": None, "error": error_dict}


# Utility functions for Result pattern
def safe_execute(func: Callable[[], T]) -> Result[T, Exception]:
    """Safely execute a function and return a Result."""
    try:
        result = func()
        return Result.success(result)
    except Exception as e:
        return Result.failure(e)


def combine_results(results: List[Result[T, Exception]]) -> Result[List[T], Exception]:
    """Combine multiple results into a single result with a list of values."""
    values: List[T] = []
    for result in results:
        if result.is_failure:
            return Result.failure(result._error)  # type: ignore
        if result._value is not None:
            values.append(result._value)
    return Result.success(values)


def first_success(*results: Result[T, Exception]) -> Result[T, Exception]:
    """Return the first successful result, or the last error if all fail."""
    last_error = None
    for result in results:
        if result.is_success:
            return result
        last_error = result.error
    return Result.failure(last_error or Exception("All results failed"))
