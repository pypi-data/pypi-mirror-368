"""Template validation module with simplified architecture."""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Protocol, Set, TypeVar

import jinja2
from jinja2 import Environment, TemplateSyntaxError, UndefinedError, meta

from ..exceptions import (
    TemplateError,
    TemplateMissingVariablesError,
    TemplateUndefinedVariableError,
    TemplateValidationError,
)
from .validation_config import ValidationConfig
from .validation_metrics import (
    ValidationMetrics,
    get_metrics_collector,
    timed_validation,
    validation_timeout,
)

logger = logging.getLogger(__name__)

# Type variables for enhanced type safety
T = TypeVar("T", bound="TemplateValidationStrategy")


class ValidatorFactory(Protocol):
    """Protocol for validator factory implementations."""

    def create(self, config: ValidationConfig) -> "TemplateValidator":
        """Create a validator with the given configuration."""
        ...

    def create_default(self) -> "TemplateValidator":
        """Create a validator with default configuration."""
        ...


class TemplateValidationStrategy(ABC):
    """Abstract base class for template validation strategies."""

    @abstractmethod
    def validate(
        self, template_source: str, template_vars: Dict[str, Any]
    ) -> "ValidationMetrics":
        """Validate template with given variables.

        Args:
            template_source: The template source code
            template_vars: Variables to validate against

        Returns:
            ValidationMetrics: Metrics about the validation process

        Raises:
            TemplateError: If validation fails
        """
        pass

    @abstractmethod
    def sanitize_variables(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize template variables for safe processing.

        Args:
            variables: Raw template variables

        Returns:
            Dict[str, Any]: Sanitized variables safe for template processing
        """
        pass


class SimpleTemplateValidator:
    """Simplified template validator with essential security features.

    This replaces the complex validation strategies with a single, secure approach.
    """

    def __init__(
        self, template_env: Environment, config: Optional[ValidationConfig] = None
    ):
        self.template_env = template_env
        if config is None:
            raise ValueError(
                "ValidationConfig dependency must be provided explicitly (Phase 3 Architecture Cleanup)"
            )
        self.config = config
        self._metrics_collector = (
            get_metrics_collector() if config and config.enable_metrics else None
        )

    def validate(
        self, template_source: str, template_vars: Dict[str, Any]
    ) -> "ValidationMetrics":
        """Validate template with essential security checks.

        Args:
            template_source: The template source code
            template_vars: Variables to validate against

        Raises:
            TemplateSyntaxError: If template has syntax errors
            TemplateMissingVariablesError: If required variables are missing
            TemplateValidationError: For other validation errors
        """
        template_size = len(template_source.encode("utf-8"))

        # Check template size limits (security)
        if template_size > self.config.max_template_size_bytes:
            raise TemplateValidationError(
                f"Template size ({template_size} bytes) exceeds limit "
                f"({self.config.max_template_size_bytes} bytes)"
            )

        try:
            # Parse template to check for syntax errors
            try:
                parsed = self.template_env.parse(template_source)
            except TemplateSyntaxError:
                if self._metrics_collector:
                    self._metrics_collector.record_validation(
                        False, "TemplateSyntaxError"
                    )
                raise

            # Find undefined variables
            undefined_vars = meta.find_undeclared_variables(parsed)
            missing_vars = undefined_vars - set(template_vars.keys())

            # Filter out variables that are optional (have defaults or in conditionals)
            if missing_vars:
                optional_vars = self._find_optional_variables(
                    template_source, missing_vars
                )
                truly_missing = missing_vars - optional_vars

                if truly_missing:
                    error = TemplateMissingVariablesError(truly_missing)
                    if self._metrics_collector:
                        self._metrics_collector.record_validation(
                            False, "TemplateMissingVariablesError"
                        )
                    raise error

            # Record successful validation
            if self._metrics_collector:
                self._metrics_collector.record_validation(True)

            # Return success metrics
            return ValidationMetrics(
                strategy_used="simple",
                validation_time_ms=0,  # Not tracked in simple validator
                template_size_bytes=template_size,
                variables_count=len(template_vars),
                undefined_variables_found=0,
                fallback_used=False,
            )

        except (
            TemplateSyntaxError,
            TemplateValidationError,
            TemplateMissingVariablesError,
        ):
            # These exceptions are already handled above or should propagate
            raise
        except Exception as e:
            logger.error(f"Unexpected error during validation: {e}")
            if self._metrics_collector:
                self._metrics_collector.record_validation(False, type(e).__name__)
            raise TemplateValidationError(f"Template validation error: {e}")

    def _find_optional_variables(
        self, template_source: str, missing_vars: Set[str]
    ) -> Set[str]:
        """Find variables that are optional (have default filters or are in conditionals)."""
        import re

        optional_vars = set()

        # Simplified and secure patterns to prevent ReDoS attacks
        # Only match simple variable names with basic default filters
        default_pattern = re.compile(
            r"{{\s*([a-zA-Z_][a-zA-Z0-9_]{0,50})\s*\|\s*default\b", re.MULTILINE
        )
        # Simple conditional pattern without nested matching
        conditional_pattern = re.compile(
            r"{%\s*if\s+([a-zA-Z_][a-zA-Z0-9_]{0,50})(?:\s+is\s+defined)?\s*%}",
            re.MULTILINE,
        )

        # Find variables with default filters
        for match in default_pattern.finditer(template_source):
            var_name = match.group(1).strip()
            if var_name in missing_vars:
                optional_vars.add(var_name)

        # Find variables in conditionals (simplified detection)
        for match in conditional_pattern.finditer(template_source):
            var_name = match.group(1).strip()
            if var_name in missing_vars:
                optional_vars.add(var_name)

        return optional_vars

    def sanitize_variables(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize template variables for security.

        Args:
            variables: Raw template variables

        Returns:
            Sanitized variables
        """
        # Basic sanitization - remove potentially dangerous values
        sanitized = {}
        for key, value in variables.items():
            if isinstance(value, str):
                # Remove null bytes and control characters
                sanitized[key] = "".join(
                    char for char in value if ord(char) >= 32 or char in "\t\n\r"
                )
            else:
                sanitized[key] = value
        return sanitized


class RuntimeValidator(TemplateValidationStrategy):
    """Validates templates by attempting to render them.

    Examples:
        >>> env = Environment()
        >>> validator = RuntimeValidator(env)
        >>> validator.validate("Hello {{ name }}!", {"name": "World"})
        >>> # Raises TemplateUndefinedVariableError for undefined variables
        >>> validator.validate("Hello {{ missing }}!", {"name": "World"})
    """

    def __init__(
        self, template_env: Environment, config: Optional[ValidationConfig] = None
    ):
        self.template_env = template_env
        if config is None:
            raise ValueError(
                "ValidationConfig dependency must be provided explicitly (Phase 3 Architecture Cleanup)"
            )
        self.config = config
        self._metrics_collector = get_metrics_collector()

    def validate(
        self, template_source: str, template_vars: Dict[str, Any]
    ) -> ValidationMetrics:
        """Validate by attempting to render the template.

        Args:
            template_source: The template source code
            template_vars: Variables to use for rendering

        Returns:
            ValidationMetrics: Metrics from the validation process

        Raises:
            TemplateSyntaxError: If template has syntax errors
            TemplateUndefinedVariableError: If undefined variables are encountered
            TemplateValidationError: For other validation errors
        """
        template_size = len(template_source.encode("utf-8"))

        with timed_validation(
            "RuntimeValidator",
            template_size,
            len(template_vars),
            True,  # Always enable timing for simplified approach
        ) as metrics:
            try:
                logger.debug(
                    f"Starting runtime validation for template of size {template_size} bytes"
                )

                template = self.template_env.from_string(template_source)

                # Attempt to render with timeout if configured
                if self.config.render_timeout_seconds > 0:
                    with validation_timeout(self.config.render_timeout_seconds):
                        rendered = template.render(**template_vars)
                else:
                    rendered = template.render(**template_vars)

                rendered_size = len(rendered.encode("utf-8"))

                logger.debug(
                    f"Runtime validation successful: rendered {rendered_size} bytes"
                )
                self._metrics_collector.record_validation(True)

            except TemplateSyntaxError as e:
                logger.error(f"Template syntax error during runtime validation: {e}")
                metrics.errors_encountered = 1
                self._metrics_collector.record_validation(False, "TemplateSyntaxError")
                # Let TemplateSyntaxError propagate for proper error handling
                raise
            except UndefinedError as e:
                logger.error(f"Undefined variable during runtime validation: {e}")
                metrics.errors_encountered = 1
                metrics.undefined_variables_found = 1
                error = TemplateUndefinedVariableError(str(e))
                self._metrics_collector.record_validation(
                    False, "TemplateUndefinedVariableError"
                )
                raise error
            except Exception as e:
                logger.error(f"Unexpected error during runtime validation: {e}")
                metrics.errors_encountered = 1
                self._metrics_collector.record_validation(False, type(e).__name__)
                raise TemplateValidationError(f"Template rendering error: {e}")

        return metrics

    def sanitize_variables(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize template variables for safe processing.

        Args:
            variables: Raw template variables

        Returns:
            Dict[str, Any]: Sanitized variables safe for template processing
        """
        # Basic sanitization - remove potentially dangerous values
        sanitized = {}
        for key, value in variables.items():
            if isinstance(value, str):
                # Remove null bytes and control characters
                sanitized[key] = "".join(
                    char for char in value if ord(char) >= 32 or char in "\t\n\r"
                )
            else:
                sanitized[key] = value
        return sanitized


class TemplateSourceResolver:
    """Resolves template source from various inputs."""

    def __init__(self, template_env: Environment):
        self.template_env = template_env

    def resolve_source(self, template_input: str) -> str:
        """Resolve template source from input (content or filename).

        Args:
            template_input: Either template content or template filename

        Returns:
            str: The template source code

        Raises:
            TemplateError: If template cannot be resolved
        """
        try:
            # Check if it's template content or template name
            if self._is_template_content(template_input):
                return template_input
            else:
                # It's a template name, load from file
                template = self.template_env.get_template(template_input)
                if template.environment.loader is None:
                    raise TemplateError(
                        f"No loader available for template: {template_input}"
                    )
                return template.environment.loader.get_source(
                    template.environment, template_input
                )[0]
        except jinja2.TemplateNotFound:
            raise TemplateError(f"Template not found: {template_input}")
        except Exception as e:
            if isinstance(e, TemplateError):
                raise
            raise TemplateError(f"Error resolving template source: {e}")

    def _is_template_content(self, template_input: str) -> bool:
        """Check if input is template content or filename."""
        return (
            "{{" in template_input
            or "{%" in template_input
            or not template_input.endswith(".j2")
        )


class TemplateValidator:
    """Main template validator that orchestrates different validation strategies.

    This class provides a unified interface for template validation using
    configurable strategies and comprehensive error handling.

    Examples:
        >>> env = Environment()
        >>> config = ValidationConfig(sandbox_mode=True)
        >>> validator = TemplateValidator(env, config=config)
        >>> validator.validate("Hello {{ name }}!", {"name": "World"})

        >>> # With custom validators
        >>> static = SimpleTemplateValidator(env)
        >>> runtime = RuntimeValidator(env)
        >>> validator = TemplateValidator(env, static_validator=static, runtime_validator=runtime)
    """

    def __init__(
        self,
        template_env: Environment,
        config: Optional[ValidationConfig] = None,
        static_validator: Optional[TemplateValidationStrategy] = None,
        runtime_validator: Optional[TemplateValidationStrategy] = None,
        fallback_strategy: Optional[RuntimeValidator] = None,
    ):
        """Initialize the template validator.

        Args:
            template_env: Jinja2 environment for template processing
            config: Validation configuration settings
            static_validator: Custom static analysis validator
            runtime_validator: Custom runtime validator
            fallback_strategy: Fallback validator for error recovery
        """
        self.template_env = template_env
        if config is None:
            raise ValueError(
                "ValidationConfig dependency must be provided explicitly (Phase 3 Architecture Cleanup)"
            )
        self.config = config
        self._metrics_collector = get_metrics_collector()

        # Initialize validators with explicit dependencies (Phase 3 Architecture Cleanup)
        if static_validator is None:
            raise ValueError("static_validator dependency must be provided explicitly")
        if runtime_validator is None:
            raise ValueError("runtime_validator dependency must be provided explicitly")

        self.static_validator = static_validator
        self.runtime_validator = runtime_validator
        self.fallback_strategy = fallback_strategy

        # Logging is configured at application level

    def validate(
        self, template_source: str, template_vars: Dict[str, Any]
    ) -> ValidationMetrics:
        """Validate template using configured strategies.

        Args:
            template_source: The template source code to validate
            template_vars: Variables to validate against

        Returns:
            ValidationMetrics: Metrics from the validation process

        Raises:
            TemplateSyntaxError: If template has syntax errors
            TemplateMissingVariablesError: If required variables are missing
            TemplateUndefinedVariableError: If undefined variables are encountered
            TemplateValidationError: For other validation errors
        """
        validation_start = time.time()
        template_size = len(template_source.encode("utf-8"))

        logger.info("Starting template validation")

        try:
            # Use simplified validation approach
            self.static_validator.validate(template_source, template_vars)

            # Create success metrics
            validation_time = time.time() - validation_start
            metrics = ValidationMetrics(
                strategy_used="simple",
                validation_time_ms=validation_time * 1000,
                template_size_bytes=template_size,
                variables_count=len(template_vars),
                undefined_variables_found=0,
                fallback_used=False,
            )

            logger.info(f"Template validation successful in {validation_time:.3f}s")
            if self._metrics_collector:
                self._metrics_collector.record_validation(True)
            return metrics

        except (
            TemplateSyntaxError,
            TemplateValidationError,
            TemplateMissingVariablesError,
            TemplateUndefinedVariableError,
        ) as e:
            validation_time = time.time() - validation_start
            metrics = ValidationMetrics(
                strategy_used="simple",
                validation_time_ms=validation_time * 1000,
                template_size_bytes=template_size,
                variables_count=len(template_vars),
                undefined_variables_found=0,
                fallback_used=False,
                errors_encountered=1,
            )

            logger.error(f"Template validation failed in {validation_time:.3f}s: {e}")
            if self._metrics_collector:
                self._metrics_collector.record_validation(False, type(e).__name__)
            raise

    def get_metrics(self) -> Dict[str, Any]:
        """Get validation metrics from the metrics collector.

        Returns:
            Dict containing validation statistics and metrics
        """
        return self._metrics_collector.get_stats().to_dict()

    def reset_metrics(self) -> None:
        """Reset validation metrics."""
        self._metrics_collector.reset()

    def sanitize_variables(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize template variables for safe processing.

        Args:
            variables: Raw template variables

        Returns:
            Dict[str, Any]: Sanitized variables safe for template processing
        """
        # Use the static validator's sanitize method if available
        if hasattr(self.static_validator, "sanitize_variables"):
            return self.static_validator.sanitize_variables(variables)

        # Basic sanitization fallback
        sanitized = {}
        for key, value in variables.items():
            if isinstance(key, str) and key.isidentifier():
                sanitized[key] = value
        return sanitized


class TemplateValidatorFactory:
    """Factory for creating template validators with different configurations.

    This factory implements the ValidatorFactory protocol and provides
    convenient methods for creating validators with common configurations.

    Examples:
        >>> env = Environment()
        >>> factory = TemplateValidatorFactory()
        >>>
        >>> # Create with default configuration
        >>> validator = factory.create_default(env)
        >>>
        >>> # Create with custom configuration
        >>> config = ValidationConfig(sandbox_mode=True)
        >>> validator = factory.create(env, config)
        >>>
        >>> # Create with predefined configurations
        >>> static_validator = factory.create_static_only(env)
        >>> runtime_validator = factory.create_runtime_only(env)
    """

    def create(
        self, template_env: Environment, config: ValidationConfig
    ) -> TemplateValidator:
        """Create a validator with the given configuration.

        Args:
            template_env: Jinja2 environment for template processing
            config: Validation configuration settings

        Returns:
            TemplateValidator: Configured validator instance
        """
        return TemplateValidator(template_env=template_env, config=config)

    def create_default(self, template_env: Environment) -> TemplateValidator:
        """Create a validator with default configuration.

        Args:
            template_env: Jinja2 environment for template processing

        Returns:
            TemplateValidator: Validator with default settings
        """
        return TemplateValidator(template_env=template_env)

    @staticmethod
    def create_static_only(
        template_env: Environment, strict_mode: bool = False
    ) -> TemplateValidator:
        """Create a validator that only uses static analysis.

        Args:
            template_env: Jinja2 environment for template processing
            strict_mode: Whether to enable strict validation mode

        Returns:
            TemplateValidator: Static-only validator
        """
        config = ValidationConfig(sandbox_mode=True)
        return TemplateValidator(template_env=template_env, config=config)

    @staticmethod
    def create_runtime_only(
        template_env: Environment, timeout_seconds: int = 30
    ) -> TemplateValidator:
        """Create a validator that only uses runtime validation.

        Args:
            template_env: Jinja2 environment for template processing
            timeout_seconds: Timeout for template rendering

        Returns:
            TemplateValidator: Runtime-only validator
        """
        config = ValidationConfig(
            sandbox_mode=True, render_timeout_seconds=timeout_seconds
        )
        return TemplateValidator(template_env=template_env, config=config)

    @staticmethod
    def create_with_fallback(
        template_env: Environment, enable_metrics: bool = True
    ) -> TemplateValidator:
        """Create a validator with static analysis and runtime fallback.

        Args:
            template_env: Jinja2 environment for template processing
            enable_metrics: Whether to enable performance metrics collection

        Returns:
            TemplateValidator: Validator with fallback strategy
        """
        config = ValidationConfig(sandbox_mode=True)
        return TemplateValidator(
            template_env=template_env,
            config=config,
            fallback_strategy=RuntimeValidator(template_env, config),
        )

    @staticmethod
    def create_comprehensive(template_env: Environment) -> TemplateValidator:
        """Create a validator that runs both static and runtime validation.

        Args:
            template_env: Jinja2 environment for template processing

        Returns:
            TemplateValidator: Comprehensive validator
        """
        config = ValidationConfig(sandbox_mode=True)
        return TemplateValidator(template_env=template_env, config=config)
