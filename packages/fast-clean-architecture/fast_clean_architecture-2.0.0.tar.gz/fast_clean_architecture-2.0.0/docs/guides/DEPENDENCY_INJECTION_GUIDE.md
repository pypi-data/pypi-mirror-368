# Dependency Injection and Factory Pattern Guide

This guide demonstrates the implementation of dependency injection and factory patterns in Fast Clean Architecture, providing better testability, loose coupling, and maintainable code.

## Overview

The Fast Clean Architecture now implements:

1. **Dependency Injection Pattern**: Components receive their dependencies through constructor injection rather than creating them internally
2. **Factory Pattern**: A centralized factory creates generators with proper dependency injection
3. **Protocol-Based Design**: All dependencies are defined through protocols for better type safety

## Architecture Improvements

### Before: Tight Coupling

```python
# Old approach - tight coupling
class ComponentGenerator:
    def __init__(self, config: Config):
        self.config = config
        # Direct instantiation creates tight coupling
        self.validator = TemplateValidator()  # Hard dependency
        self.path_handler = SecurePathHandler()  # Hard dependency
```

### After: Dependency Injection

```python
# New approach - loose coupling through dependency injection
class ComponentGenerator:
    def __init__(
        self, 
        config: Config, 
        template_validator: Optional[TemplateValidatorProtocol] = None,
        path_handler: Optional[SecurePathHandler] = None,
        console: Optional[Console] = None
    ):
        """Initialize ComponentGenerator with dependency injection.
        
        Args:
            config: Configuration object
            template_validator: Template validator (injected dependency)
            path_handler: Secure path handler (injected dependency)
            console: Console for output
        """
        self.config = config
        self.console = console or Console()
        
        # Use injected dependencies or create defaults for backward compatibility
        self.template_validator = template_validator or self._create_default_validator()
        self.path_handler = path_handler or self._create_default_path_handler()
```

## Factory Pattern Implementation

### Generator Factory

The `GeneratorFactory` provides a centralized way to create generators with proper dependency injection:

```python
from fast_clean_architecture.generators import create_generator_factory
from fast_clean_architecture.config import Config

# Create factory with dependencies
config = Config.load_from_file('fca_config.yaml')
factory = create_generator_factory(config)

# Create generators using the factory
component_generator = factory.create_generator('component')
package_generator = factory.create_generator('package')
config_updater = factory.create_generator('config', config_path=Path('custom_config.yaml'))
```

### Dependency Container

The `DependencyContainer` manages the lifecycle of shared dependencies:

```python
from fast_clean_architecture.generators.generator_factory import DependencyContainer, GeneratorFactory

# Create dependency container
dependencies = DependencyContainer(config, console)

# Create factory with dependency container
factory = GeneratorFactory(dependencies)

# All generators created by this factory will share the same dependencies
gen1 = factory.create_generator('component')
gen2 = factory.create_generator('component')
# Both generators share the same template validator and path handler instances
```

## Benefits

### 1. Improved Testability

```python
# Easy to mock dependencies for testing
from unittest.mock import Mock

mock_validator = Mock(spec=TemplateValidatorProtocol)
mock_path_handler = Mock(spec=SecurePathHandler)

# Inject mocks for testing
generator = ComponentGenerator(
    config=test_config,
    template_validator=mock_validator,
    path_handler=mock_path_handler
)

# Test with controlled dependencies
generator.create_component(...)
mock_validator.validate.assert_called_once()
```

### 2. Flexible Configuration

```python
# Custom validator for specific use cases
class StrictTemplateValidator(TemplateValidatorProtocol):
    def validate(self, template_source: str, template_vars: Dict[str, Any]) -> None:
        # Custom strict validation logic
        pass

# Use custom validator
custom_validator = StrictTemplateValidator()
generator = ComponentGenerator(
    config=config,
    template_validator=custom_validator
)
```

### 3. Resource Management

```python
# Shared dependencies reduce resource usage
factory = create_generator_factory(config)

# Multiple generators share the same validator and path handler
for i in range(10):
    generator = factory.create_generator('component')
    # All generators use the same validator instance
```

## Usage Examples

### Basic Usage (Backward Compatible)

```python
# Still works - uses default dependencies
from fast_clean_architecture.generators import ComponentGenerator
from fast_clean_architecture.config import Config

config = Config.load_from_file('fca_config.yaml')
generator = ComponentGenerator(config)
```

### Factory Pattern Usage

```python
# Recommended approach - uses factory
from fast_clean_architecture.generators import create_generator_factory

factory = create_generator_factory(config)
component_generator = factory.create_generator('component')
package_generator = factory.create_generator('package')
```

### Custom Dependencies

```python
# Advanced usage - custom dependencies
from fast_clean_architecture.generators.generator_factory import DependencyContainer, GeneratorFactory
from fast_clean_architecture.protocols import SecurePathHandler

# Create custom path handler with different settings
custom_path_handler = SecurePathHandler(
    max_path_length=8192,  # Longer paths allowed
    allowed_extensions=['.py', '.j2', '.yaml', '.yml', '.json', '.txt']
)

# Create dependency container
dependencies = DependencyContainer(config, console)

# Override default path handler
dependencies._path_handler = custom_path_handler

# Create factory with custom dependencies
factory = GeneratorFactory(dependencies)
generator = factory.create_generator('component')
```

### CLI Integration

The CLI now uses the factory pattern internally:

```python
# In CLI code
config_updater = ConfigUpdater(config_path, console)
generator_factory = create_generator_factory(config_updater.config, console)
component_generator = generator_factory.create_generator('component')
```

## Protocol-Based Design

All dependencies are defined through protocols for better type safety:

```python
from fast_clean_architecture.protocols import (
    ComponentGeneratorProtocol,
    TemplateValidatorProtocol,
    SecurePathHandler
)

# Type-safe dependency injection
def create_custom_generator(
    config: Config,
    validator: TemplateValidatorProtocol,
    path_handler: SecurePathHandler
) -> ComponentGeneratorProtocol:
    return ComponentGenerator(
        config=config,
        template_validator=validator,
        path_handler=path_handler
    )
```

## Migration Guide

### For Existing Code

1. **No changes required**: Existing code continues to work due to backward compatibility
2. **Gradual migration**: Replace direct instantiation with factory pattern over time
3. **Testing improvements**: Start using dependency injection in tests immediately

### Recommended Migration Steps

1. **Update imports**:
   ```python
   # Old
   from fast_clean_architecture.generators import ComponentGenerator
   
   # New
   from fast_clean_architecture.generators import create_generator_factory
   ```

2. **Replace instantiation**:
   ```python
   # Old
   generator = ComponentGenerator(config, console)
   
   # New
   factory = create_generator_factory(config, console)
   generator = factory.create_generator('component')
   ```

3. **Update tests**:
   ```python
   # Old
   generator = ComponentGenerator(config)
   
   # New - with mocked dependencies
   generator = ComponentGenerator(
       config=config,
       template_validator=mock_validator,
       path_handler=mock_path_handler
   )
   ```

## Best Practices

1. **Use the factory pattern** for creating generators in application code
2. **Use dependency injection** for testing and custom configurations
3. **Leverage protocols** for type safety and interface contracts
4. **Share dependencies** through the dependency container for resource efficiency
5. **Mock dependencies** in tests for better isolation and control

## Error Handling

The factory pattern includes proper error handling:

```python
try:
    generator = factory.create_generator('invalid_type')
except ValueError as e:
    print(f"Error: {e}")  # "Unsupported generator type: invalid_type"

# Check available types
available_types = factory.get_available_types()
print(f"Available generator types: {available_types}")
```

## Extending the Factory

You can register custom generator types:

```python
class CustomGenerator:
    def __init__(self, config: Config, console: Console):
        self.config = config
        self.console = console

# Register custom generator
factory.register_generator('custom', CustomGenerator)

# Use custom generator
custom_gen = factory.create_generator('custom')
```

This architecture provides a solid foundation for maintainable, testable, and extensible code while maintaining backward compatibility with existing implementations.