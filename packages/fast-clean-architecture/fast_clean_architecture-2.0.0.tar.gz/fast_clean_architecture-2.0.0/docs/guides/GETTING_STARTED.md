# Getting Started with Fast Clean Architecture

This guide will walk you through creating a complete FastAPI application using the Fast Clean Architecture (FCA) scaffolding tool.

## What's New in v2.0.0

- **Enhanced Component Validation System**: Centralized validation with layer-aware component type checking
  - Layer-specific component type validation (domain, application, infrastructure, presentation)
  - Support for nested component structures (e.g., `use_cases/commands`, `use_cases/queries`)
  - Comprehensive validation rules with enhanced error messages
- **Improved Type Safety**: Complete mypy compliance across the entire codebase
  - Resolved all type checking errors in component generator
  - Enhanced protocol-based design patterns
  - Better handling of Union types in component generation
- **Backward Compatibility Support**: Legacy component type mapping for seamless migration
  - `api` component type automatically mapped to `controllers` in presentation layer
  - Maintains support for all existing component types
  - Deprecation warnings for legacy types with migration guidance
- **Enhanced Security**: Strengthened validation rules and secure path handling
- **Component Type Organization**: Restructured component types by architectural layer for better Clean Architecture compliance
- **Protocol Enhancement**: Updated `ComponentGeneratorProtocol` with improved type safety

## How This Tool Fits Into Your FastAPI Workflow

Fast Clean Architecture is a **scaffolding and code generation tool** that creates the architectural foundation for your FastAPI projects. Here's how it integrates into your development workflow:

### Traditional FastAPI Development:
```
Create FastAPI app → Write endpoints → Add business logic → Organize code
```

### With Fast Clean Architecture:
```
Create FastAPI app → Scaffold architecture → Generate components → Wire dependencies → Implement business logic
```

### What This Tool Provides:
- **Clean architecture structure** with proper layer separation
- **Code templates** for entities, repositories, services, and API routers
- **Consistent project organization** following DDD principles
- **Type-safe boilerplate** with Pydantic models and type hints

### What You Still Need To Do:
- **Create the main FastAPI application** (`main.py`)
- **Configure dependency injection** to wire components together
- **Implement business logic** in the generated templates
- **Set up database connections** and other infrastructure
- **Add authentication, middleware, and error handling**

This tool accelerates the initial setup and ensures your project follows clean architecture principles from day one.

## Prerequisites

- Python 3.8 or higher
- pip package manager or Poetry
- Basic understanding of FastAPI and web API development
- Familiarity with clean architecture principles (recommended)

**Important Note**: This tool does not create a complete, runnable FastAPI application on its own. It generates the architectural components and structure for your FastAPI project. You will need to:

1. Create the main FastAPI application instance (`main.py`)
2. Configure dependency injection to wire components together
3. Add database connections and other infrastructure requirements
4. Implement your specific business logic

This guide will walk you through all these steps.

## Installation

### Using pip

```bash
pip install fast-clean-architecture
```

### Using Poetry

```bash
poetry add fast-clean-architecture
```

Or if you're starting a new project with Poetry:

```bash
# Create Project Folder
mkdir project-folder-name

# Go into the project folder
cd project-folder-name

# Initialize a new Poetry project
poetry init

# Add fast-clean-architecture as a dependency
poetry add fast-clean-architecture

# Activate the virtual environment
poetry shell
```

## Quick Start: Create a Complete Project Structure

**New Feature**: You can now create a complete project structure with a single command using the `create-scalable-baseline` command:

```bash
# Create project with Poetry (default)
fca-scaffold create-scalable-baseline my-fastapi-app

# Or with Pip
fca-scaffold create-scalable-baseline my-fastapi-app --deps pip

# With additional options
fca-scaffold create-scalable-baseline my-fastapi-app \
  --description "My awesome FastAPI application" \
  --version "1.0.0" \
  --deps poetry
```

### Scalable Baseline Features

The `create-scalable-baseline` command creates a complete project structure with:

- **Production-Ready Setup**: Complete FastAPI project with all features
- **Multiple Systems**: User management, order processing, and notification systems
- **Database Integration**: SQLAlchemy models and repository implementations
- **API Versioning**: Built-in support for v1, v2, v3 API versions
- **Security Features**: Authentication, authorization, and security middleware
- **Testing Suite**: Comprehensive test structure with fixtures
- **CI/CD Ready**: GitHub Actions workflows and Docker configuration
- **Perfect for**: Production applications, team projects, or complex systems

```bash
fca-scaffold create-scalable-baseline my-app
```

### Dependency Manager Options

**Poetry (Recommended)**:
- Modern dependency management with lock files
- Virtual environment management built-in
- Better dependency resolution
- Includes development dependencies and build system
- Ideal for new projects and teams

**Pip**:
- Traditional and widely supported
- Compatible with older deployment systems
- Simpler for basic projects
- Good for environments with existing pip workflows

### What Gets Created

The baseline creates a complete project structure including:

**Core Structure:**
- Core FastAPI application (`core/main.py` or `main.py`)
- Project configuration (`fca_config.yaml`)
- Dependency management files (`pyproject.toml` or `requirements.txt`)
- Environment configuration (`.env.example`)
- Git configuration (`.gitignore`)
- Documentation (`README.md`, evolution guides)

**Clean Architecture Layers:**
- `systems/` - Business systems (bounded contexts)
- `shared/infrastructure/` - Shared components
- `tests/` - Test structure
- `scripts/` - Utility scripts

**Enhanced Folder Structure:**
- `events/` - Domain and application events
- `exceptions/` - Custom exception classes
- `interfaces/` - Abstract interfaces and protocols
- `dtos/` - Data transfer objects
- `use_cases/` - Application use cases (commands/queries)
- `config/` - Configuration modules
- `database/` - Database-specific implementations
- `middleware/` - Custom middleware components
- `migrations/` - Database migration scripts

### Running Your New Project

After creating a baseline project:

```bash
cd my-fastapi-app

# If using Poetry
poetry install
poetry run uvicorn main:app --reload

# If using Pip
pip install -r requirements.txt
uvicorn main:app --reload
```

Your application will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

If you prefer the step-by-step approach, continue with the manual initialization below.

## Step 1: Initialize Your Project (Manual Approach)

First, create a new directory for your project and initialize it:

```bash
mkdir my-fastapi-app
cd my-fastapi-app

# Initialize the project
fca-scaffold init my_fastapi_app --description "My awesome FastAPI application" --version "1.0.0"
```

This creates:
- `fca_config.yaml` - Project configuration file
- `systems/` - Directory for system contexts

## Step 2: Create System Contexts

System contexts represent major functional areas of your application. Let's create a user management system:

```bash
fca-scaffold create-system-context user_management --description "User management and authentication system"
```

This creates:
```
systems/
└── user_management/
    ├── __init__.py
    └── main.py
```

## Step 3: Create Modules

Modules are logical groupings within a system context. Let's create an authentication module:

```bash
fca-scaffold create-module user_management authentication --description "User authentication and authorization"
```

This creates the complete clean architecture structure with enhanced organization:
```
systems/
└── user_management/
    ├── __init__.py
    ├── main.py
    └── authentication/
        ├── __init__.py
        ├── authentication_module_api.py
        ├── domain/
        │   ├── __init__.py
        │   ├── entities/
        │   │   └── __init__.py
        │   ├── interfaces/          # Repository interfaces
        │   │   └── __init__.py
        │   ├── value_objects/
        │   │   └── __init__.py
        │   ├── events/              # Domain events
        │   │   └── __init__.py
        │   └── exceptions/          # Domain-specific exceptions
        │       └── __init__.py
        ├── application/
        │   ├── __init__.py
        │   ├── use_cases/
        │   │   ├── __init__.py
        │   │   ├── commands/        # CQRS commands
        │   │   │   └── __init__.py
        │   │   └── queries/         # CQRS queries
        │   │       └── __init__.py
        │   ├── services/
        │   │   └── __init__.py
        │   └── dtos/                # Data Transfer Objects
        │       └── __init__.py
        ├── infrastructure/
        │   ├── __init__.py
        │   ├── database/
        │   │   ├── __init__.py
        │   │   ├── models/
        │   │   │   └── __init__.py
        │   │   ├── repositories/
        │   │   │   └── __init__.py
        │   │   └── migrations/
        │   │       └── __init__.py
        │   ├── external/            # External service integrations
        │   │   └── __init__.py
        │   └── config/              # Module-specific configuration
        │       └── __init__.py
        └── presentation/
            ├── __init__.py
            ├── routes/
            │   └── __init__.py
            ├── controllers/
            │   └── __init__.py
            ├── schemas/
            │   └── __init__.py
            └── middleware/          # Module-specific middleware
                └── __init__.py
```

**Note:** When using API versioning with `--api-version v1`, the presentation layer components (routes, controllers, schemas) will have version-specific subdirectories like `routes/v1/`, `controllers/v1/`, etc.

## Step 4: Create Components

Now let's create the actual components. We'll start with a User entity:

### Domain Layer Components

```bash
# Create User entity
fca-scaffold create-component user_management/authentication/domain/entities user

# Create User repository interface
fca-scaffold create-component user_management/authentication/domain/repositories user

# Create value objects
fca-scaffold create-component user_management/authentication/domain/value_objects email
fca-scaffold create-component user_management/authentication/domain/value_objects password
```

### Application Layer Components

```bash
# Create authentication service
fca-scaffold create-component user_management/authentication/application/services auth_service

# Create CQRS commands
fca-scaffold create-component user_management/authentication/application/use_cases/commands create_user
fca-scaffold create-component user_management/authentication/application/use_cases/commands login_user

# Create CQRS queries
fca-scaffold create-component user_management/authentication/application/use_cases/queries get_user
fca-scaffold create-component user_management/authentication/application/use_cases/queries list_users

# Create DTOs
fca-scaffold create-component user_management/authentication/application/dtos user_dto
```

### Infrastructure Layer Components

```bash
# Create database model
fca-scaffold create-component user_management/authentication/infrastructure/database/models user

# Create repository implementation
fca-scaffold create-component user_management/authentication/infrastructure/database/repositories user

# Create external service client
fca-scaffold create-component user_management/authentication/infrastructure/external email_service

# Create configuration
fca-scaffold create-component user_management/authentication/infrastructure/config auth_config
```

### Presentation Layer Components (with API Versioning)

```bash
# Create versioned API controllers
fca-scaffold create-component user_management/authentication/presentation/controllers/v1 auth_controller
fca-scaffold create-component user_management/authentication/presentation/controllers/v2 auth_controller

# Create versioned routes
fca-scaffold create-component user_management/authentication/presentation/routes/v1 auth_routes
fca-scaffold create-component user_management/authentication/presentation/routes/v2 auth_routes

# Create versioned Pydantic schemas
fca-scaffold create-component user_management/authentication/presentation/schemas/v1 user_schema
fca-scaffold create-component user_management/authentication/presentation/schemas/v2 user_schema

# Create middleware
fca-scaffold create-component user_management/authentication/presentation/middleware auth_middleware

# Create additional organizational components (new in v1.2.0+)
fca-scaffold create-component user_management/authentication/application/events user_created
fca-scaffold create-component user_management/authentication/domain/exceptions auth_exception
fca-scaffold create-component user_management/authentication/application/interfaces auth_interface
fca-scaffold create-component user_management/authentication/infrastructure/config database_config
fca-scaffold create-component user_management/authentication/infrastructure/middleware rate_limiter
```

### Migrating Existing Modules to API Versioning

If you have existing modules without API versioning, you can migrate them using the new `migrate-to-api-versioning` command:

```bash
# Migrate all presentation layer components to v1
fca-scaffold migrate-to-api-versioning user_management authentication --target-version v1

# Migrate specific components only
fca-scaffold migrate-to-api-versioning user_management authentication --target-version v1 --components controllers,routes,schemas

# Preview migration without making changes
fca-scaffold migrate-to-api-versioning user_management authentication --target-version v1 --dry-run
```

This command will:
- Move existing presentation layer files to versioned directories
- Update import statements and references
- Create module API entry points
- Maintain backward compatibility

## Enhanced Validation and Backward Compatibility

### Layer-Aware Component Validation

FCA now features an enhanced validation system that validates component types based on their architectural layer:

**Domain Layer Components:**
- `entities` - Core business entities
- `events` - Domain events for business logic
- `exceptions` - Domain-specific exceptions
- `interfaces` - Repository and service contracts
- `value_objects` - Immutable value objects
- `enums` - Domain enumerations

**Application Layer Components:**
- `dtos` - Data Transfer Objects
- `services` - Application orchestration services
- `use_cases` - Business use cases (supports nested `commands` and `queries`)

**Infrastructure Layer Components:**
- `config` - Configuration management
- `external` - External service integrations
- `database` - Database layer with nested components:
  - `database/migrations` - Database migrations
  - `database/models` - Database models and schemas
  - `database/repositories` - Repository implementations

**Presentation Layer Components:**
- `controllers` - API controllers
- `middleware` - Request/response middleware
- `routes` - Route definitions
- `schemas` - API validation schemas

### Enhanced Error Messages

The validation system now provides detailed, context-aware error messages:

```bash
# Invalid component type for layer
$ fca-scaffold create-component user_management/auth/domain/controllers UserController
Error: Component type 'controllers' is not valid for layer 'domain'.
Valid component types for 'domain' layer: entities, events, exceptions, interfaces, value_objects, enums

# Clear validation messages
$ fca-scaffold create-component user_management/auth/presentation/invalid_type UserAPI
Error: Component type 'invalid_type' is not valid for layer 'presentation'.
```

## Step 5: Check Project Status

You can check your project's current state at any time:

```bash
fca-scaffold status
```

This shows:
- Project information
- Systems overview
- Module counts
- Creation and update timestamps

## Step 6: Batch Creation (Alternative Approach)

Instead of creating components one by one, you can use batch creation with a YAML specification file:

```bash
# Use the provided example specification
fca-scaffold batch-create examples/components_spec.yaml
```

Or create your own specification file:

```yaml
# my-components.yaml
systems:
  - name: user_management
    modules:
      - name: authentication
        components:
          domain:
            entities: ["user", "role"]
            repositories: ["user", "role"]
            value_objects: ["email", "password"]
          application:
            services: ["auth_service"]
            commands: ["create_user", "login"]
            queries: ["get_user", "list_users"]
          infrastructure:
            models: ["user", "role"]
            repositories: ["user", "role"]
          presentation:
            api: ["auth", "users"]
            schemas: ["user", "auth"]
```

Then run:
```bash
fca-scaffold batch-create my-components.yaml
```

## Step 7: Understanding the Generated Code

Let's look at what was generated. Note that FCA now creates an enhanced folder structure with additional organizational directories for better code organization:

### Enhanced Project Structure (v1.2.0+)

```
systems/
├── __init__.py
└── user_management/
    ├── __init__.py
    ├── authentication/
    │   ├── __init__.py
    │   ├── authentication_module_api.py  # Module API entry point
    │   ├── application/
    │   │   ├── __init__.py
    │   │   ├── dtos/
    │   │   │   └── __init__.py
    │   │   ├── events/                  # Application events
    │   │   │   └── __init__.py
    │   │   ├── interfaces/              # Application interfaces
    │   │   │   └── __init__.py
    │   │   ├── services/
    │   │   │   └── __init__.py
    │   │   └── use_cases/
    │   │       ├── __init__.py
    │   │       ├── commands/
    │   │       │   └── __init__.py
    │   │       └── queries/
    │   │           └── __init__.py
    │   ├── domain/
    │   │   ├── __init__.py
    │   │   ├── entities/
    │   │   │   └── __init__.py
    │   │   ├── events/                  # Domain events
    │   │   │   └── __init__.py
    │   │   ├── exceptions/              # Domain exceptions
    │   │   │   └── __init__.py
    │   │   ├── interfaces/              # Domain interfaces
    │   │   │   └── __init__.py
    │   │   ├── repositories/
    │   │   │   └── __init__.py
    │   │   └── value_objects/
    │   │       └── __init__.py
    │   ├── infrastructure/
    │   │   ├── __init__.py
    │   │   ├── config/                  # Infrastructure config
    │   │   │   └── __init__.py
    │   │   ├── database/
    │   │   │   ├── __init__.py
    │   │   │   ├── migrations/          # Database migrations
    │   │   │   │   └── __init__.py
    │   │   │   ├── models/
    │   │   │   │   └── __init__.py
    │   │   │   └── repositories/
    │   │   │       └── __init__.py
    │   │   ├── external/
    │   │   │   └── __init__.py
    │   │   └── middleware/              # Infrastructure middleware
    │   │       └── __init__.py
    │   └── presentation/
    │       ├── __init__.py
    │       ├── controllers/
    │       │   ├── __init__.py
    │       │   ├── v1/                  # Versioned controllers
    │       │   │   └── __init__.py
    │       │   └── v2/
    │       │       └── __init__.py
    │       ├── middleware/              # Presentation middleware
    │       │   └── __init__.py
    │       ├── routes/
    │       │   ├── __init__.py
    │       │   ├── v1/                  # Versioned routes
    │       │   │   └── __init__.py
    │       │   └── v2/
    │       │       └── __init__.py
    │       └── schemas/
    │           ├── __init__.py
    │           ├── v1/                  # Versioned schemas
    │           │   └── __init__.py
    │           └── v2/
    │               └── __init__.py
    └── main.py
```

### Domain Entity (`systems/user_management/authentication/domain/entities/user.py`)

```python
"""
User entity for authentication module.

Generated at: 2024-01-15T10:30:00Z
Generator version: 1.2.2
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class User:
    """User domain entity.
    
    Represents a user in the authentication domain.
    """
    
    # Primary identifier
    id: Optional[UUID] = field(default_factory=uuid4)
    
    # Add your domain-specific fields here
    # Example:
    # email: str = ""
    # username: str = ""
    # is_active: bool = True
    
    # Audit fields
    created_at: Optional[datetime] = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self) -> None:
        """Post-initialization validation and setup."""
        if self.id is None:
            self.id = uuid4()
        
        now = datetime.now(timezone.utc)
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)
    
    def is_new(self) -> bool:
        """Check if this is a new entity (not persisted yet)."""
        return self.created_at == self.updated_at
```

### Repository Interface (`systems/user_management/authentication/domain/interfaces/user_repository.py`)

```python
"""User repository interface for authentication module."""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from ..entities.user import User


class UserRepository(ABC):
    """Abstract repository interface for user operations.
    
    This is an abstract base class that enforces implementation of all methods
    in concrete repository classes.
    """
    
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[User]:
        """Retrieve user by ID.
        
        Args:
            id: The unique identifier of the user
            
        Returns:
            The user entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def save(self, entity: User) -> User:
        """Save user entity.
        
        Args:
            entity: The user entity to save
            
        Returns:
            The saved user entity with updated fields
        """
        pass
    
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete user by ID.
        
        Args:
            id: The unique identifier of the user to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List all users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of user entities
        """
        pass
```

### Application Service (`systems/user_management/authentication/application/services/auth_service_service.py`)

```python
"""User service for authentication module.

Generated at: 2024-01-15T10:30:00Z
Generator version: 1.2.2
"""
from typing import List, Optional, Dict, Any
from uuid import UUID

from ...domain.entities.user import User
from ...domain.interfaces.user_repository import UserRepository


class UserService:
    """Application service for authentication operations.
    
    This service orchestrates business logic and coordinates between
    domain entities and infrastructure components.
    """
    
    def __init__(self, user_repository: UserRepository):
        """Initialize the service with required dependencies.
        
        Args:
            user_repository: Repository for user data operations
        """
        self._user_repository = user_repository
    
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user.
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            The created user entity
            
        Raises:
            ValueError: If user data is invalid
        """
        # Add business logic validation here
        user = User(**user_data)
        return await self._user_repository.save(user)
    
    async def get_user(self, user_id: UUID) -> Optional[User]:
        """Retrieve user by ID.
        
        Args:
            user_id: The unique identifier of the user
            
        Returns:
            The user entity if found, None otherwise
        """
        return await self._user_repository.get_by_id(user_id)
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of user entities
        """
        return await self._user_repository.list_all(skip=skip, limit=limit)
    
    async def update_user(self, user_id: UUID, user_data: Dict[str, Any]) -> Optional[User]:
        """Update an existing user.
        
        Args:
            user_id: The unique identifier of the user
            user_data: Dictionary containing updated user information
            
        Returns:
            The updated user entity if found, None otherwise
        """
        user = await self._user_repository.get_by_id(user_id)
        if user:
            for key, value in user_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.update_timestamp()
            return await self._user_repository.save(user)
        return None
    
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user.
        
        Args:
            user_id: The unique identifier of the user to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        return await self._user_repository.delete(user_id)
```

### Pydantic Schemas (`systems/user_management/authentication/presentation/schemas/v1/user_schema.py`)

```python
"""
User schemas for authentication module.

Generated at: 2024-01-15T10:30:00Z
Generator version: 1.2.2
"""
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base schema for user."""
    # Add your domain-specific fields here
    # Example:
    # email: str = Field(..., description="User email address")
    # username: str = Field(..., description="User username")
    # is_active: bool = Field(True, description="Whether user is active")
    pass


class UserCreate(UserBase):
    """Schema for creating user."""
    # Add creation-specific fields here
    # Example:
    # password: str = Field(..., min_length=8, description="User password")
    pass


class UserUpdate(UserBase):
    """Schema for updating user."""
    # Make fields optional for updates
    # Example:
    # email: Optional[str] = Field(None, description="User email address")
    # username: Optional[str] = Field(None, description="User username")
    pass


class UserResponse(UserBase):
    """Schema for user response."""
    
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

### Module API Entry Point (`systems/user_management/authentication/authentication_module_api.py`)

```python
"""
Authentication module API entry point.

This file serves as the main interface for the authentication module,
exposing the module's functionality to other parts of the system.
"""
from fastapi import APIRouter
from .presentation.api.v1.user_api import router as user_v1_router

# Create the main module router
module_router = APIRouter(prefix="/auth", tags=["authentication"])

# Include versioned API routers
module_router.include_router(user_v1_router, prefix="/v1")

# You can add more API versions here:
# from .presentation.api.v2.user_api import router as user_v2_router
# module_router.include_router(user_v2_router, prefix="/v2")

# Export the router for use in the main application
__all__ = ["module_router"]
```

### FastAPI Router (`systems/user_management/authentication/presentation/api/v1/user_api.py`)

```python
"""
User API router for authentication module.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..schemas.v1.user_schemas import UserCreate, UserResponse
from ...application.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse)
async def create_user(
    data: UserCreate,
    service: UserService = Depends()
):
    """Create new user."""
    entity = await service.create_user(data.model_dump())
    return UserResponse.model_validate(entity)


@router.get("/", response_model=List[UserResponse])
async def list_users(
    service: UserService = Depends()
):
    """List all users."""
    entities = await service.list_users()
    return [UserResponse.model_validate(entity) for entity in entities]


@router.get("/{id}", response_model=UserResponse)
async def get_user(
    id: str,
    service: UserService = Depends()
):
    """Get user by ID."""
    entity = await service.get_user_by_id(id)
    if not entity:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(entity)


@router.put("/{id}", response_model=UserResponse)
async def update_user(
    id: str,
    data: UserCreate,
    service: UserService = Depends()
):
    """Update user."""
    entity = await service.update_user(id, data.model_dump())
    if not entity:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(entity)


@router.delete("/{id}")
async def delete_user(
    id: str,
    service: UserService = Depends()
):
    """Delete user."""
    success = await service.delete_user(id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
```

## Step 8: Customization

The generated code provides a solid foundation, but you'll need to customize it for your specific needs:

1. **Add business logic** to your entities and services
2. **Implement dependency injection** in your FastAPI application
3. **Add database connections** and configure your repository implementations
4. **Customize validation** in your Pydantic schemas
5. **Add authentication and authorization** middleware
6. **Configure logging and error handling**

## Step 9: FastAPI Integration and Running Your Application

### Install FastAPI Dependencies

First, install FastAPI and uvicorn if you haven't already:

```bash
# Using pip
pip install fastapi uvicorn[standard]

# Using Poetry
poetry add fastapi uvicorn[standard]
```

### Create the Main FastAPI Application

Use the FastAPI CLI to bootstrap your application:

```bash
# Install FastAPI with all standard dependencies
pip install "fastapi[standard]"

# Or with Poetry
poetry add "fastapi[standard]"

# Create and run a basic FastAPI app (this will create main.py if it doesn't exist)
fastapi dev main.py
```

This command will:
- Create a basic `main.py` file if it doesn't exist
- Start the development server with auto-reload
- Set up the FastAPI application with sensible defaults

Once the basic structure is created, enhance the generated `main.py` with your scaffolded components:

```python
# main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from systems.user_management.authentication.presentation.api.auth_router import router as auth_router

# Create FastAPI instance
app = FastAPI(
    title="My Clean Architecture FastAPI App",
    description="A FastAPI application built with clean architecture principles",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware (configure as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with proper prefixes and tags
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

# Add startup and shutdown events
@app.on_event("startup")
async def startup_event():
    # Initialize database connections, load configurations, etc.
    print("Application starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    # Clean up resources
    print("Application shutting down...")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )
```

### Run Your Application

```bash
# Method 1: Run directly with Python
python main.py

# Method 2: Use uvicorn directly (recommended for development)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Method 3: Using Poetry (if using Poetry)
poetry run uvicorn main:app --reload
```

### Access Your Application

Once running, your application will be available at:

- **API Base URL**: `http://localhost:8000`
- **Interactive API Documentation**: `http://localhost:8000/docs`
- **Alternative Documentation**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

### Next Steps for Production

For production deployment, consider:

1. **Environment Configuration**: Use environment variables for sensitive data
2. **Database Setup**: Configure your database connections in the startup event
3. **Dependency Injection**: Set up proper DI for your repositories and services
4. **Authentication**: Implement JWT or other authentication mechanisms
5. **Logging**: Configure structured logging
6. **Error Handling**: Add global exception handlers
7. **Testing**: Write comprehensive tests for your endpoints

## Advanced Features

### Dry Run Mode

Test what would be created without actually creating files:

```bash
fca-scaffold create-component user_management/authentication/domain/entities product --dry-run
```

### Force Overwrite

Overwrite existing files without confirmation:

```bash
fca-scaffold create-component user_management/authentication/domain/entities user --force
```

### Custom Configuration

Use a custom configuration file:

```bash
fca-scaffold init --config custom-config.yaml
fca-scaffold create-system-context payment --config custom-config.yaml
```

### Configuration Management

```bash
# View current configuration
fca-scaffold config show

# Validate configuration
fca-scaffold config validate

# Check project status
fca-scaffold status

# Update package to latest version
fca-scaffold update-package

# Update to specific version
fca-scaffold update-package 2.0.0

# Update from TestPyPI (for testing)
fca-scaffold update-package --test-pypi
```

### Configuration Metadata

The `fca-config.yaml` file is the central source of truth for your project's metadata within `fca-scaffold`. This includes the project name, version, and description.

- **Project Name, Version, and Description**: These values are primarily set during the `fca-scaffold init` command. For example:
  ```bash
  fca-scaffold init my-new-project --description "A description of my new project"
  ```
  This command will populate the `project.name`, `project.version` (defaulting to `0.1.0`), and `project.description` fields in your `fca-config.yaml`.

- **Independence from `pyproject.toml`**: It's important to note that the project name and version displayed by `fca-scaffold status` are read *exclusively* from `fca-config.yaml`. They are independent of the `name` and `version` defined in your `pyproject.toml` file. While `pyproject.toml` is used for Python package management and versioning, `fca-scaffold` maintains its own configuration for scaffolding purposes.

- **Manual Updates**: If you manually edit the `project.name` or `project.version` in `fca-config.yaml`, `fca-scaffold status` will reflect these changes. However, these manual edits will not automatically update your `pyproject.toml` or vice-versa. Ensure consistency between these files if needed for your project's release process.

- **Accuracy of `fca-scaffold status`**: If `fca-scaffold status` shows inaccurate information, it is likely due to manual modifications to `fca-config.yaml` that have not been synchronized with your expectations, or a misunderstanding of its source of truth (which is always `fca-config.yaml`).

- **Configuration Validation**: When you run `fca-scaffold config validate` and see "Configuration is valid!", it means your `fca-config.yaml` file adheres to the expected schema with all required fields present, correct data types, and values within acceptable ranges. This validation ensures the scaffolding process functions correctly and prevents errors during code generation.

### Module API Entry Points

Starting with v1.2.0, FCA automatically generates module API entry point files (`{module_name}_module_api.py`) that provide a centralized interface for each module:

```python
# systems/user_management/authentication/authentication_module_api.py
"""Authentication module API entry point.

This module provides a centralized interface for the authentication module,
exposing key components and services for external consumption.
"""

from .application.services.auth_service_service import AuthServiceService
from .domain.entities.user import User
from .domain.interfaces.user_repository import UserRepository
from .presentation.api.auth_router import router as auth_router
from .presentation.schemas.v1.user_schema import UserResponse, UserCreate, UserUpdate

# Export main components
__all__ = [
    "AuthServiceService",
    "User",
    "UserRepository", 
    "auth_router",
    "UserResponse",
    "UserCreate",
    "UserUpdate",
]

# Module metadata
MODULE_NAME = "authentication"
MODULE_VERSION = "1.0.0"
MODULE_DESCRIPTION = "User authentication and authorization module"
```

This approach provides:
- **Clear module boundaries**: Easy to understand what each module exposes
- **Simplified imports**: Import from module API instead of deep paths
- **Version tracking**: Each module can have its own version
- **Documentation**: Centralized place for module documentation

## Best Practices

1. **Start with system contexts** - Think about major functional areas first
2. **Keep modules focused** - Each module should have a single responsibility
3. **Follow naming conventions** - Use snake_case for files and PascalCase for classes
4. **Use batch creation** for large projects to save time
5. **Leverage API versioning** - Plan for API evolution from the start
6. **Use module API entry points** - Import from module APIs for cleaner dependencies
7. **Organize with enhanced folders** - Utilize events, exceptions, interfaces, dtos, etc.
8. **Migrate existing modules** - Use `migrate-to-api-versioning` for legacy code
9. **Choose appropriate dependency manager** - Poetry for modern projects, Pip for compatibility
10. **Customize templates** if you have specific coding standards
11. **Version control your config** - Include `fca_config.yaml` in your repository
12. **Use dry run mode** to preview changes before applying them
13. **Keep packages updated** - Use `update-package` command regularly

## Next Steps

- **Explore the generated code** and understand the clean architecture patterns
- **Implement your business logic** in the domain layer using entities and value objects
- **Add database models** and repository implementations in the infrastructure layer
- **Set up dependency injection** for your FastAPI application using the module API entry points
- **Leverage API versioning** for future-proof API design
- **Use enhanced organizational folders** (events, exceptions, interfaces, dtos) for better code structure
- **Add comprehensive tests** for your components across all layers
- **Configure CI/CD pipelines** with the generated workflow templates
- **Implement proper error handling** using the exceptions folders
- **Add monitoring and logging** using the middleware components
- **Deploy your application** using the provided Docker configurations

## Version Information

This guide covers Fast Clean Architecture v2.0.0. For the latest features and updates, check:
- [Changelog](CHANGELOG.md) for recent additions
- [GitHub Releases](https://github.com/alden-technologies/fast-clean-architecture/releases) for version history
- Use `fca-scaffold version` to check your installed version
- Use `fca-scaffold update-package` to get the latest version

Congratulations! You now have a well-structured FastAPI application following clean architecture principles with modern organizational patterns and API versioning support.