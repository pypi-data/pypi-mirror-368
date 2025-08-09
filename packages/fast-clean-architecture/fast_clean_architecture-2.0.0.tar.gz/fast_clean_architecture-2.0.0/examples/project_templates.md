# FCA Project Templates and Examples

This directory contains practical examples and templates for Fast Clean Architecture (FCA) projects. These examples demonstrate different approaches to building scalable, maintainable applications using Clean Architecture principles.

## Available Examples

### 1. Batch Specification (`batch_spec.yaml`)

**Purpose**: Perfect for learning FCA concepts and building small to medium applications.

**What it creates**:
- Blog system with posts and comments
- Basic user authentication
- Clean separation of concerns
- Simple domain models

**Use case**: Educational projects, personal blogs, small content management systems.

```bash
# Create the blog system
fca-scaffold batch-create examples/batch_spec.yaml
```

**Generated structure**:
```
blog_system/
├── posts/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── presentation/
└── comments/
    ├── domain/
    ├── application/
    ├── infrastructure/
    └── presentation/
```

### 2. Advanced Batch Specification (`advanced_batch_spec.yaml`)

**Purpose**: Comprehensive e-commerce system demonstrating enterprise-level architecture.

**What it creates**:
- Complete e-commerce platform
- Multiple bounded contexts
- Advanced domain modeling
- API versioning support
- External service integrations

**Use case**: Enterprise applications, e-commerce platforms, complex business systems.

```bash
# Create the advanced e-commerce system
fca-scaffold batch-create examples/advanced_batch_spec.yaml
```

**Generated systems**:
- **User Management**: Authentication, profiles, preferences
- **Product Catalog**: Products, categories, inventory
- **Order Management**: Orders, payments, fulfillment
- **Shipping Logistics**: Shipping, tracking, carriers
- **Notification System**: Multi-channel notifications
- **Analytics & Reporting**: Business intelligence
- **Customer Support**: Ticket management

### 3. Error Handling Examples (`error_handling_examples.py`)

**Purpose**: Demonstrates robust error handling patterns in FCA applications.

**Key concepts**:
- Enhanced exception hierarchy
- Result pattern implementation
- Safe execution utilities
- Error context management
- Validation strategies

**Usage**:
```python
from examples.error_handling_examples import (
    ValidationError,
    Result,
    safe_execute,
    ErrorContext
)

# Example: Safe operation with Result pattern
result = safe_execute(risky_operation, fallback_value="default")
if result.is_success():
    print(f"Success: {result.value}")
else:
    print(f"Error: {result.error}")
```

## Scalable Baseline

The `create-scalable-baseline` command creates a complete FastAPI project with Clean Architecture.

**Best for**:
- Learning Clean Architecture
- Prototypes and MVPs
- Small to medium applications
- Single-team projects
- Enterprise applications
- Multi-team projects
- Complex business domains
- Production-ready systems

**Features**:
- Complete Clean Architecture implementation
- API versioning support
- Enhanced security features
- Comprehensive middleware
- Advanced error handling
- Monitoring and logging
- Configuration management
- Essential components
- Quick setup with room for growth

**Command**:
```bash
fca-scaffold create-scalable-baseline my-project --dependency-manager poetry
```

## Dependency Manager Options

### Poetry (Recommended)

**Advantages**:
- Modern dependency management
- Virtual environment handling
- Lock file for reproducible builds
- Easy publishing to PyPI

**Generated files**:
- `pyproject.toml`
- `poetry.lock`

### Pip

**Advantages**:
- Universal Python package manager
- Simple and familiar
- Works in any Python environment

**Generated files**:
- `requirements.txt`
- `requirements-dev.txt`

## Project Evolution Path

### Phase 1: Start with Baseline
```bash
# Create a scalable baseline
fca-scaffold create-scalable-baseline my-app

# Add your first module
fca-scaffold create-module users

# Add components as needed
fca-scaffold create-component users user entity
```

### Phase 2: Add Features
```bash
# Add more modules
fca-scaffold create-module products
fca-scaffold create-module orders

# Create batch components
fca-scaffold batch-create my-batch-spec.yaml
```

### Phase 3: Scale Up
```bash
# Migrate to API versioning
fca-scaffold migrate-to-api-versioning

# Add advanced features
fca-scaffold create-component orders payment_processor service
fca-scaffold create-component users auth_middleware middleware
```

### Phase 4: Enterprise Ready
```bash
# Update to latest patterns
fca-scaffold update-package

# Sync configuration with filesystem
fca-scaffold sync-config --dry-run
fca-scaffold sync-config

# Monitor project health
fca-scaffold system-status

# Validate configuration
fca-scaffold config validate
```

## Advanced CLI Commands

### Configuration Management
```bash
# Show current configuration
fca-scaffold config show

# Validate configuration file
fca-scaffold config validate

# Sync filesystem with configuration
fca-scaffold sync-config --systems user_management,orders
```

### Project Monitoring
```bash
# Check project status
fca-scaffold status

# Detailed system analysis
fca-scaffold system-status

# Get comprehensive help
fca-scaffold help-guide
```

### Batch Operations
```bash
# Create multiple components at once
fca-scaffold batch-create examples/advanced_batch_spec.yaml

# Preview batch creation
fca-scaffold batch-create examples/batch_spec.yaml --dry-run
```

## Best Practices

### 1. Start with the Scalable Baseline
- Provides a complete foundation for any project size
- Includes all necessary features for both learning and production
- Can be customized based on your specific needs

### 2. Follow Domain-Driven Design
- Identify bounded contexts
- Model your domain entities first
- Use value objects for business concepts
- Implement domain events for integration

### 3. Maintain Clean Architecture
- Keep dependencies pointing inward
- Use interfaces for external dependencies
- Separate business logic from infrastructure
- Test each layer independently

### 4. Plan for Growth
- Design for API versioning from the start
- Implement proper error handling
- Use configuration management
- Plan your module boundaries

### 5. Security First
- Validate all inputs
- Implement proper authentication
- Use secure configuration management
- Follow security best practices

## Common Patterns

### Repository Pattern
```python
# Domain interface
class UserRepository(Protocol):
    def save(self, user: User) -> None: ...
    def find_by_id(self, user_id: UserId) -> Optional[User]: ...

# Infrastructure implementation
class SqlUserRepository(UserRepository):
    def save(self, user: User) -> None:
        # Database implementation
        pass
```

### Use Case Pattern
```python
# Application layer
class CreateUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self._user_repo = user_repo
    
    def execute(self, request: CreateUserRequest) -> CreateUserResponse:
        # Business logic here
        user = User.create(request.email, request.name)
        self._user_repo.save(user)
        return CreateUserResponse(user.id)
```

### Event-Driven Architecture
```python
# Domain events
class UserCreated(DomainEvent):
    def __init__(self, user_id: UserId, email: Email):
        self.user_id = user_id
        self.email = email

# Event handlers
class SendWelcomeEmailHandler:
    def handle(self, event: UserCreated) -> None:
        # Send welcome email
        pass
```

## Getting Help

- Check the [CLI Reference](../docs/guides/CLI_REFERENCE.md) for command details
- Read the [Getting Started Guide](../docs/guides/GETTING_STARTED.md) for basics
- Review [Template Validation Guide](../docs/guides/TEMPLATE_VALIDATION_GUIDE.md) for validation
- See [Dependency Injection Guide](../docs/guides/DEPENDENCY_INJECTION_GUIDE.md) for DI patterns

## Contributing

Want to add more examples? Please:
1. Follow the existing patterns
2. Include comprehensive documentation
3. Test your examples thoroughly
4. Submit a pull request

For more information, see our [Contributing Guide](../docs/CONTRIBUTING.md).