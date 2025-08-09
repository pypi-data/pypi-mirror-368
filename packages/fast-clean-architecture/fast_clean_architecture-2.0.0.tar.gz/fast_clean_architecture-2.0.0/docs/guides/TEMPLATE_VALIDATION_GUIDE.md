# Template Validation Guide

This guide demonstrates the enhanced template validation system with comprehensive examples and best practices.

## Overview

The template validation system provides multiple validation strategies, comprehensive error handling, performance monitoring, and configuration-driven behavior.

## Quick Start

### Basic Usage

```python
from jinja2 import Environment
from fast_clean_architecture.generators.template_validator import TemplateValidatorFactory

# Create Jinja2 environment
env = Environment()

# Create validator with default settings
validator = TemplateValidatorFactory.create_default(env)

# Validate a template
template_source = "Hello {{ name }}!"
template_vars = {"name": "World"}

try:
    metrics = validator.validate(template_source, template_vars)
    print(f"Validation successful in {metrics.validation_time:.3f}s")
except TemplateSyntaxError as e:
    print(f"Template syntax error: {e}")
except TemplateMissingVariablesError as e:
    print(f"Missing variables: {e.missing_variables}")
```

## Validation Strategies

### 1. Static Analysis Only

Fast validation using AST analysis without rendering:

```python
from fast_clean_architecture.generators.validation_config import ValidationConfig, ValidationStrategy

# Create static-only validator
config = ValidationConfig(strategy=ValidationStrategy.STATIC_ONLY)
validator = TemplateValidatorFactory().create(env, config)

# Or use the convenience method
validator = TemplateValidatorFactory.create_static_only(env, strict_mode=True)
```

### 2. Runtime Validation Only

Validation by actually rendering the template:

```python
# Create runtime-only validator with timeout
validator = TemplateValidatorFactory.create_runtime_only(env, timeout_seconds=10)

# Validate complex template
template_source = """
{% for item in items %}
  {{ item.name }}: {{ item.value | default('N/A') }}
{% endfor %}
"""

template_vars = {
    "items": [
        {"name": "Item 1", "value": "Value 1"},
        {"name": "Item 2"}  # Missing 'value' - will use default
    ]
}

metrics = validator.validate(template_source, template_vars)
```

### 3. Static with Runtime Fallback

Try static analysis first, fall back to runtime if needed:

```python
validator = TemplateValidatorFactory.create_with_fallback(env, enable_metrics=True)

# This will try static analysis first, then runtime if static fails
metrics = validator.validate(template_source, template_vars)
print(f"Strategy used: {metrics.strategy_used}")
```

### 4. Comprehensive Validation

Run both static and runtime validation:

```python
validator = TemplateValidatorFactory.create_comprehensive(env)

# Both static and runtime validation will be performed
metrics = validator.validate(template_source, template_vars)
```

## Configuration Options

### Basic Configuration

```python
from fast_clean_architecture.generators.validation_config import (
    ValidationConfig, ValidationStrategy, LogLevel
)

config = ValidationConfig(
    strategy=ValidationStrategy.BOTH,
    strict_mode=True,
    allow_undefined=False,
    enable_fallback=True,
    enable_timing=True,
    log_level=LogLevel.DEBUG,
    max_template_size_bytes=1024 * 1024,  # 1MB limit
    render_timeout_seconds=30
)

validator = TemplateValidatorFactory().create(env, config)
```

### Security Configuration

```python
# Strict security settings
secure_config = ValidationConfig(
    strategy=ValidationStrategy.BOTH,
    strict_mode=True,
    allow_undefined=False,
    max_template_size_bytes=512 * 1024,  # 512KB limit
    render_timeout_seconds=10,
    security_checks=True
)
```

## Error Handling

### Exception Hierarchy

```python
from fast_clean_architecture.exceptions import (
    TemplateError,                    # Base template error
    TemplateValidationError,          # General validation error
    TemplateMissingVariablesError,    # Missing required variables
    TemplateUndefinedVariableError,   # Undefined variable during rendering
    TemplateSyntaxError              # Jinja2 syntax error
)

try:
    validator.validate(template_source, template_vars)
except TemplateMissingVariablesError as e:
    print(f"Missing variables: {', '.join(e.missing_variables)}")
    # Handle missing variables specifically
except TemplateUndefinedVariableError as e:
    print(f"Undefined variable: {e.variable_name}")
    # Handle undefined variables during rendering
except TemplateSyntaxError as e:
    print(f"Syntax error: {e}")
    # Handle template syntax errors
except TemplateValidationError as e:
    print(f"Validation error: {e}")
    # Handle other validation errors
```

### Detailed Error Information

```python
try:
    validator.validate("{{ missing_var }}", {})
except TemplateMissingVariablesError as e:
    print(f"Error: {e}")
    print(f"Missing variables: {e.missing_variables}")
    print(f"Error details: {e.details}")
```

## Performance Monitoring

### Collecting Metrics

```python
from fast_clean_architecture.generators.validation_metrics import get_metrics_collector

# Enable timing in configuration
config = ValidationConfig(enable_timing=True)
validator = TemplateValidatorFactory().create(env, config)

# Perform validations
for i in range(100):
    validator.validate(f"Template {i}: {{{{ value_{i} }}}}", {f"value_{i}": f"Value {i}"})

# Get aggregated metrics
metrics = validator.get_metrics()
print(f"Total validations: {metrics['total_validations']}")
print(f"Success rate: {metrics['success_rate']:.2%}")
print(f"Average time: {metrics['average_time']:.3f}s")
print(f"Total time: {metrics['total_time']:.3f}s")
```

### Performance Analysis

```python
# Get detailed metrics
metrics_collector = get_metrics_collector()
stats = metrics_collector.get_stats()

print(f"Validation Statistics:")
print(f"  Total: {stats.total_validations}")
print(f"  Successful: {stats.successful_validations}")
print(f"  Failed: {stats.failed_validations}")
print(f"  Success Rate: {stats.success_rate:.2%}")
print(f"  Average Time: {stats.average_time:.3f}s")
print(f"  Total Time: {stats.total_time:.3f}s")
print(f"  Average Template Size: {stats.average_template_size} bytes")
print(f"  Average Variable Count: {stats.average_variable_count}")

# Reset metrics for next measurement period
validator.reset_metrics()
```

## Advanced Usage

### Custom Validators

```python
from fast_clean_architecture.generators.template_validator import TemplateValidationStrategy

class CustomValidator(TemplateValidationStrategy):
    """Custom validation strategy with business logic."""
    
    def __init__(self, template_env: Environment, config: Optional[ValidationConfig] = None):
        self.template_env = template_env
        self.config = config or ValidationConfig()
    
    def validate(self, template_source: str, template_vars: Dict[str, Any]) -> None:
        # Custom validation logic
        if "dangerous_function" in template_source:
            raise TemplateValidationError("Dangerous function not allowed")
        
        # Check for required business variables
        required_vars = {"user_id", "tenant_id"}
        missing = required_vars - set(template_vars.keys())
        if missing:
            raise TemplateMissingVariablesError(missing)
        
        # Delegate to static analysis for syntax checking
        static_validator = StaticAnalysisValidator(self.template_env, self.config)
        static_validator.validate(template_source, template_vars)

# Use custom validator
custom_validator = CustomValidator(env)
validator = TemplateValidator(
    template_env=env,
    static_validator=custom_validator
)
```

### Validation with Context Managers

```python
from fast_clean_architecture.generators.validation_metrics import timed_validation

# Manual timing for custom operations
with timed_validation("CustomOperation", template_size=1024, variable_count=5) as metrics:
    # Perform custom validation logic
    time.sleep(0.1)  # Simulate work
    metrics.custom_data = {"processed_items": 42}

print(f"Custom operation took {metrics.validation_time:.3f}s")
```

## Best Practices

### 1. Choose the Right Strategy

- **Static Only**: For fast validation during development
- **Runtime Only**: For complex templates with dynamic content
- **Static with Fallback**: For production with performance optimization
- **Both**: For comprehensive validation in CI/CD pipelines

### 2. Configure Appropriately

```python
# Development configuration
dev_config = ValidationConfig(
    strategy=ValidationStrategy.STATIC_ONLY,
    strict_mode=False,
    log_level=LogLevel.DEBUG,
    enable_timing=True
)

# Production configuration
prod_config = ValidationConfig(
    strategy=ValidationStrategy.STATIC_WITH_RUNTIME_FALLBACK,
    strict_mode=True,
    allow_undefined=False,
    max_template_size_bytes=256 * 1024,  # 256KB limit
    render_timeout_seconds=5,
    enable_timing=False  # Reduce overhead
)
```

### 3. Handle Errors Gracefully

```python
def safe_validate_template(validator, template_source, template_vars):
    """Safely validate template with comprehensive error handling."""
    try:
        metrics = validator.validate(template_source, template_vars)
        return {"success": True, "metrics": metrics}
    except TemplateSyntaxError as e:
        return {"success": False, "error": "syntax", "message": str(e)}
    except TemplateMissingVariablesError as e:
        return {
            "success": False, 
            "error": "missing_variables", 
            "missing": list(e.missing_variables)
        }
    except TemplateValidationError as e:
        return {"success": False, "error": "validation", "message": str(e)}
    except Exception as e:
        return {"success": False, "error": "unexpected", "message": str(e)}
```

### 4. Monitor Performance

```python
# Regular performance monitoring
def monitor_validation_performance(validator):
    """Monitor and log validation performance."""
    metrics = validator.get_metrics()
    
    if metrics['success_rate'] < 0.95:  # Less than 95% success rate
        logger.warning(f"Low validation success rate: {metrics['success_rate']:.2%}")
    
    if metrics['average_time'] > 1.0:  # More than 1 second average
        logger.warning(f"High validation time: {metrics['average_time']:.3f}s")
    
    # Reset metrics after monitoring
    validator.reset_metrics()
```

## Integration Examples

### With Component Generation

```python
from fast_clean_architecture.generators.component_generator import ComponentGenerator

# Create component generator with enhanced validation
validator = TemplateValidatorFactory.create_comprehensive(env)
generator = ComponentGenerator(template_validator=validator)

# Generate component with validation
try:
    generator.generate_component(
        component_type="service",
        component_name="UserService",
        template_vars={"namespace": "user", "methods": ["create", "update"]}
    )
except TemplateValidationError as e:
    print(f"Template validation failed: {e}")
```

### Enhanced Component Validation

The system now includes layer-aware component validation that validates component types based on their architectural layer:

```python
from fast_clean_architecture.validation import validate_component_type

# Valid component type for domain layer
try:
    validate_component_type("entities", "domain")
    print("Valid component type for domain layer")
except ComponentError as e:
    print(f"Invalid component type: {e}")

# Invalid component type for domain layer
try:
    validate_component_type("controllers", "domain")
except ComponentError as e:
    print(f"Error: {e}")
    # Output: Component type 'controllers' is not valid for layer 'domain'
```

### Layer-Specific Validation Rules

The enhanced validation system enforces Clean Architecture principles by validating component types against their target layers:

```python
from fast_clean_architecture.validation import LAYER_COMPONENT_TYPES

# View available component types for each layer
for layer, component_types in LAYER_COMPONENT_TYPES.items():
    print(f"{layer.title()} Layer: {', '.join(component_types)}")

# Output:
# Domain Layer: entities, events, exceptions, interfaces, value_objects, enums
# Application Layer: dtos, services, use_cases
# Infrastructure Layer: config, external, database
# Presentation Layer: controllers, middleware, routes, schemas
```

**Domain Layer Components:**
- `entities` - Core business entities with business logic
- `events` - Domain events for business event handling
- `exceptions` - Domain-specific exceptions
- `interfaces` - Repository and service contracts (ports)
- `value_objects` - Immutable value objects with business rules
- `enums` - Domain enumerations and constants

**Application Layer Components:**
- `dtos` - Data Transfer Objects for cross-layer communication
- `services` - Application orchestration services
- `use_cases` - Business use cases (supports nested commands/queries)

**Infrastructure Layer Components:**
- `config` - Configuration management and settings
- `external` - External service integrations
- `database` - Database layer with nested components:
  - `database/migrations` - Database schema migrations
  - `database/models` - Database models and schemas
  - `database/repositories` - Repository pattern implementations

**Presentation Layer Components:**
- `controllers` - API controllers for request handling
- `middleware` - Request/response middleware
- `routes` - Route definitions and URL mapping
- `schemas` - API validation schemas (Pydantic models)

### With Testing

```python
import pytest
from fast_clean_architecture.generators.template_validator import TemplateValidatorFactory

class TestTemplateValidation:
    """Test template validation functionality."""
    
    @pytest.fixture
    def validator(self):
        env = Environment()
        return TemplateValidatorFactory.create_static_only(env, strict_mode=True)
    
    def test_valid_template(self, validator):
        """Test validation of valid template."""
        template = "Hello {{ name }}!"
        variables = {"name": "World"}
        
        metrics = validator.validate(template, variables)
        assert metrics.success
        assert metrics.validation_time > 0
    
    def test_missing_variables(self, validator):
        """Test validation with missing variables."""
        template = "Hello {{ name }} and {{ other }}!"
        variables = {"name": "World"}
        
        with pytest.raises(TemplateMissingVariablesError) as exc_info:
            validator.validate(template, variables)
        
        assert "other" in exc_info.value.missing_variables
    
    def test_syntax_error(self, validator):
        """Test validation with syntax error."""
        template = "Hello {{ name !"
        variables = {"name": "World"}
        
        with pytest.raises(TemplateSyntaxError):
            validator.validate(template, variables)
```

This enhanced template validation system provides comprehensive validation capabilities with excellent performance monitoring, flexible configuration, and robust error handling.