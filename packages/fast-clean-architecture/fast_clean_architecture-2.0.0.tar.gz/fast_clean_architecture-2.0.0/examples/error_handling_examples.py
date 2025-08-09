#!/usr/bin/env python3
"""Examples demonstrating enhanced error handling patterns in Fast Clean Architecture.

This file shows how to use the improved exception hierarchy, Result pattern,
and error handling utilities for robust error management.
"""

from pathlib import Path
from typing import Dict, Any

from fast_clean_architecture.exceptions import (
    FastCleanArchitectureError,
    ValidationError,
    SecurityError,
    ConfigurationError,
    Result,
    ErrorContext,
    create_validation_error,
    create_secure_error,
    create_config_error,
    safe_execute,
    combine_results,
    first_success
)


def example_enhanced_exceptions():
    """Demonstrate enhanced exception features."""
    print("=== Enhanced Exception Examples ===")
    
    # Example 1: Enhanced ValidationError with context
    try:
        error = ValidationError(
            message="Invalid component name",
            field_name="component_name",
            invalid_value="invalid-name!"
        )
        error.add_context("user_id", "user123")
        error.add_suggestion("Use only alphanumeric characters and underscores")
        raise error
    except ValidationError as e:
        print(f"Caught ValidationError: {e}")
        print(f"Error dict: {e.to_dict()}")
        print()
    
    # Example 2: SecurityError with automatic suggestions
    try:
        raise create_secure_error(
            error_type="path_traversal",
            operation="file creation",
            details="Detected '../' in file path"
        )
    except SecurityError as e:
        print(f"Caught SecurityError: {e}")
        print(f"Suggestions: {e.suggestions}")
        print()
    
    # Example 3: ConfigurationError with file context
    try:
        raise create_config_error(
            operation="loading configuration",
            details="YAML syntax error on line 15",
            config_path=Path("/path/to/config.yaml")
        )
    except ConfigurationError as e:
        print(f"Caught ConfigurationError: {e}")
        print(f"Context: {e.context}")
        print()


def example_error_context():
    """Demonstrate ErrorContext usage."""
    print("=== ErrorContext Examples ===")
    
    # Example 1: Automatic context enhancement
    try:
        with ErrorContext("component_generation", component_type="service", user="admin"):
            # Simulate an error that gets enhanced
            raise ValueError("Template not found")
    except FastCleanArchitectureError as e:
        print(f"Enhanced error: {e}")
        print(f"Context: {e.context}")
        print()
    
    # Example 2: Enhancing existing FCA errors
    try:
        with ErrorContext("validation", step="name_check"):
            error = ValidationError("Invalid name format")
            raise error
    except ValidationError as e:
        print(f"Enhanced ValidationError: {e}")
        print(f"Context: {e.context}")
        print()


def example_result_pattern():
    """Demonstrate Result pattern usage."""
    print("=== Result Pattern Examples ===")
    
    # Example 1: Basic Result usage
    def validate_name(name: str) -> Result[str, ValidationError]:
        if not name:
            return Result.failure(ValidationError("Name cannot be empty"))
        if len(name) > 50:
            return Result.failure(ValidationError("Name too long"))
        return Result.success(name.strip())
    
    # Test successful case
    result = validate_name("valid_name")
    if result.is_success:
        print(f"Valid name: {result.value}")
    
    # Test failure case
    result = validate_name("")
    if result.is_failure:
        print(f"Validation failed: {result.error}")
    print()
    
    # Example 2: Chaining operations with and_then
    def validate_and_format_name(name: str) -> Result[str, ValidationError]:
        return (validate_name(name)
                .and_then(lambda n: Result.success(n.upper()))
                .map(lambda n: f"COMPONENT_{n}"))
    
    result = validate_and_format_name("my_service")
    print(f"Formatted name: {result.unwrap_or('UNKNOWN')}")
    
    # Example 3: Error transformation
    result = validate_name("").map_error(
        lambda e: ValidationError(f"Enhanced: {e.message}", field_name="component_name")
    )
    print(f"Transformed error: {result.error}")
    print()


def example_safe_execution():
    """Demonstrate safe execution utilities."""
    print("=== Safe Execution Examples ===")
    
    # Example 1: Safe function execution
    def risky_operation() -> str:
        import random
        if random.random() < 0.5:
            raise ValueError("Random failure")
        return "Success!"
    
    result = safe_execute(risky_operation)
    if result.is_success:
        print(f"Operation succeeded: {result.value}")
    else:
        print(f"Operation failed: {result.error}")
    
    # Example 2: Combining multiple results
    results = [
        Result.success("value1"),
        Result.success("value2"),
        Result.success("value3")
    ]
    
    combined = combine_results(results)
    if combined.is_success:
        print(f"All operations succeeded: {combined.value}")
    
    # Example 3: First success pattern
    results_with_failures = [
        Result.failure(ValueError("First failed")),
        Result.failure(ValueError("Second failed")),
        Result.success("Third succeeded!")
    ]
    
    first_ok = first_success(*results_with_failures)
    print(f"First success: {first_ok.value}")
    print()


def example_result_inspection():
    """Demonstrate Result inspection methods."""
    print("=== Result Inspection Examples ===")
    
    # Example 1: Inspecting successful results
    result = Result.success("important_data")
    result.inspect(lambda value: print(f"Processing: {value}"))
    
    # Example 2: Inspecting errors
    error_result = Result.failure(ValidationError("Something went wrong"))
    error_result.inspect_error(lambda error: print(f"Logging error: {error}"))
    
    # Example 3: Converting to dictionary for serialization
    success_dict = result.to_dict()
    error_dict = error_result.to_dict()
    
    print(f"Success as dict: {success_dict}")
    print(f"Error as dict: {error_dict}")
    print()


def example_practical_usage():
    """Demonstrate practical usage in a realistic scenario."""
    print("=== Practical Usage Example ===")
    
    def create_component_safe(
        name: str, 
        component_type: str, 
        config_path: Path
    ) -> Result[Dict[str, Any], FastCleanArchitectureError]:
        """Safely create a component with comprehensive error handling."""
        
        with ErrorContext("component_creation", name=name, type=component_type):
            # Validate inputs
            name_result = safe_execute(
                lambda: validate_component_name(name)
            )
            if name_result.is_failure:
                return Result.failure(name_result.error)
            
            # Check configuration
            config_result = safe_execute(
                lambda: load_config(config_path)
            )
            if config_result.is_failure:
                return Result.failure(config_result.error)
            
            # Create component data
            component_data = {
                "name": name_result.value,
                "type": component_type,
                "config": config_result.value,
                "created_at": "2024-01-01T00:00:00Z"
            }
            
            return Result.success(component_data)
    
    def validate_component_name(name: str) -> str:
        if not name or not name.strip():
            raise create_validation_error(
                field="component_name",
                value=name,
                reason="Name cannot be empty",
                suggestions=["Provide a non-empty component name"]
            )
        return name.strip()
    
    def load_config(path: Path) -> Dict[str, Any]:
        if not path.exists():
            raise create_config_error(
                operation="loading",
                details=f"Configuration file not found: {path}",
                config_path=path
            )
        return {"template_dir": "/templates", "output_dir": "/output"}
    
    # Test the practical example
    result = create_component_safe(
        name="UserService",
        component_type="service",
        config_path=Path("/nonexistent/config.yaml")
    )
    
    if result.is_success:
        print(f"Component created successfully: {result.value}")
    else:
        print(f"Component creation failed: {result.error}")
        if isinstance(result.error, FastCleanArchitectureError):
            print(f"Error details: {result.error.to_dict()}")


if __name__ == "__main__":
    """Run all examples."""
    example_enhanced_exceptions()
    example_error_context()
    example_result_pattern()
    example_safe_execution()
    example_result_inspection()
    example_practical_usage()
    
    print("\n=== Summary ===")
    print("Enhanced error handling provides:")
    print("✅ Rich context and suggestions in exceptions")
    print("✅ Automatic error enhancement with ErrorContext")
    print("✅ Functional error handling with Result pattern")
    print("✅ Safe execution utilities")
    print("✅ Error chaining and transformation")
    print("✅ Serializable error information")