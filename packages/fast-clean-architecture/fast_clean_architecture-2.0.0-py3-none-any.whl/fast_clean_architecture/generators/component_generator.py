"""Component generator for creating individual component files."""

import functools
import os
import re
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

import jinja2
from jinja2.sandbox import SandboxedEnvironment
from rich.console import Console

from ..config import Config
from ..error_tracking import track_exception
from ..exceptions import (
    ComponentError,
    FileConflictError,
    SecurityError,
    TemplateError,
    ValidationError,
    create_secure_error,
)
from ..logging_config import get_logger
from ..metrics import PerformanceTracker, measure_execution_time
from ..protocols import (
    ComponentGeneratorProtocol,
    ComponentValidationStrategy,
    SecurePathHandler,
    TemplateValidatorProtocol,
)
from ..templates import TEMPLATES_DIR
from ..utils import (
    ensure_directory,
    get_template_variables,
    sanitize_name,
    secure_file_operation,
    to_snake_case,
    validate_name,
    validate_python_identifier,
)

# Set up structured logger
logger = get_logger(__name__)


class ComponentGenerator(ComponentGeneratorProtocol):
    """Generator for creating individual component files from templates.

    This class implements the ComponentGeneratorProtocol to ensure type safety
    and provides enhanced security through protocol-based design patterns.
    """

    # Mapping of component types to their template files
    TEMPLATE_MAPPING = {
        "entities": "entity.py.j2",
        "repositories": "repository.py.j2",
        "value_objects": "value_object.py.j2",
        "services": "service.py.j2",
        "commands": "command.py.j2",
        "queries": "query.py.j2",
        "models": "model.py.j2",
        "external": "external.py.j2",
        "api": "api.py.j2",
        "schemas": "schemas.py.j2",
        "events": "event.py.j2",
        "exceptions": "exception.py.j2",
        "interfaces": "interface.py.j2",
        "enums": "enum.py.j2",
        "dtos": "dto.py.j2",
    }

    # Infrastructure repositories use a different template
    INFRASTRUCTURE_REPOSITORY_TEMPLATE = "infrastructure_repository.py.j2"

    def __init__(
        self,
        config: Config,
        template_validator: Optional[TemplateValidatorProtocol] = None,
        path_handler: Optional[SecurePathHandler[Union[str, Path]]] = None,
        console: Optional[Console] = None,
    ):
        """Initialize ComponentGenerator with dependency injection.

        Args:
            config: Configuration object
            template_validator: Template validator (injected dependency)
            path_handler: Secure path handler (injected dependency)
            console: Console for output
        """
        self.config = config
        if console is None:
            raise ValueError(
                "Console dependency must be provided explicitly (Phase 3 Architecture Cleanup)"
            )
        self.console = console

        # Use SandboxedEnvironment for security
        self.template_env = SandboxedEnvironment(
            loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
            trim_blocks=True,
            lstrip_blocks=True,
            # Restrict available functions and filters for security
            finalize=self._sanitize_template_output,
        )
        # Define allowed filters and functions
        self._setup_sandbox_security()

        # Use injected template validator (required)
        if template_validator is None:
            raise ValueError("template_validator is required")
        self.template_validator = template_validator

        # Use injected path handler (required)
        if path_handler is None:
            raise ValueError("path_handler is required")
        self.path_handler: SecurePathHandler[Union[str, Path]] = path_handler

        # Initialize component validation strategies
        self._validation_strategies = self._setup_validation_strategies()

    @measure_execution_time("create_component")
    @track_exception(operation="create_component")  # type: ignore[misc]
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
        """Create a single component file with enhanced type safety.

        This method implements the ComponentGeneratorProtocol interface
        and uses secure path handling for enhanced security.
        """
        # Log component creation start
        logger.info(
            "Starting component creation",
            operation="create_component",
            system_name=system_name,
            module_name=module_name,
            layer=layer,
            component_type=component_type,
            component_name=component_name,
            dry_run=dry_run,
            force=force,
            template_variant=template_variant,
        )

        # Validate and secure the base path using type-safe path handler
        secure_base_path = Path(self.path_handler.process(base_path))

        # Validate inputs
        self._validate_component_inputs(
            system_name, module_name, layer, component_type, component_name
        )

        # Validate nested component type if applicable
        if component_type == "use_cases" and nested_type:
            from ..validation import ValidationRules

            validation_result = ValidationRules.validate_nested_component_type(
                layer, component_type, nested_type
            )
            if validation_result.is_failure:
                error = validation_result.error
                if error is not None:
                    raise error
                else:
                    raise ValidationError(
                        f"Nested component type validation failed for '{nested_type}' in '{component_type}'"
                    )

        # Sanitize component name
        sanitized_name = sanitize_name(component_name)
        if not validate_python_identifier(sanitized_name):
            raise ValidationError(f"Invalid component name: {component_name}")

        # Determine file path and name with nested structure support
        file_path, file_name = self._get_component_file_path(
            secure_base_path,
            system_name,
            module_name,
            layer,
            component_type,
            sanitized_name,
            nested_type,
        )

        # Additional security validation for the final file path
        secure_file_path = Path(self.path_handler.process(file_path))

        # Check for conflicts using secure file path
        if secure_file_path.exists() and not force:
            raise FileConflictError(
                f"Component file already exists: {secure_file_path}. Use --force to overwrite."
            )

        if dry_run:
            self.console.print(
                f"[yellow]DRY RUN:[/yellow] Would create {secure_file_path}"
            )
            return secure_file_path

        # Validate file system permissions and space
        self._validate_file_system(secure_file_path)

        # Ensure directory exists
        ensure_directory(secure_file_path.parent)

        # Generate template variables
        template_vars = get_template_variables(
            system_name=system_name,
            module_name=module_name,
            component_name=sanitized_name,
            component_type=component_type,
        )

        # Get template name with nested type support
        template_name = self._get_template_name(
            layer, nested_type or component_type, template_variant
        )

        # Validate template variables
        self._validate_template_variables(template_name, template_vars)

        # Check for custom template
        custom_template = getattr(self.config.templates, component_type, None)
        if custom_template:
            template_name = custom_template

        # Render and write file with performance tracking
        with PerformanceTracker(
            "template_rendering",
            template_name=template_name,
            component_type=component_type,
        ):
            content = self._render_template(template_name, template_vars)

        # Write file with atomic operations and error handling using secure path
        backup_path = None
        lock_file = secure_file_path.with_suffix(f"{secure_file_path.suffix}.lock")

        try:
            # Use file locking to prevent race conditions

            import portalocker

            # Create lock file for atomic operations
            with open(lock_file, "w") as lock:
                try:
                    portalocker.lock(lock, portalocker.LOCK_EX | portalocker.LOCK_NB)
                except portalocker.LockException:
                    raise ValidationError(
                        f"File {secure_file_path} is locked by another process"
                    )

                # Create backup if file exists (within lock)
                if secure_file_path.exists():
                    backup_path = secure_file_path.with_suffix(
                        f"{secure_file_path.suffix}.backup"
                    )
                    # Use atomic copy to prevent corruption
                    with (
                        open(secure_file_path, "rb") as src,
                        open(backup_path, "wb") as dst,
                    ):
                        dst.write(src.read())

                # Atomic write operation to prevent TOCTOU vulnerabilities
                self._atomic_write_file(secure_file_path, content)

                # Clean up backup on success
                if backup_path and backup_path.exists():
                    backup_path.unlink()

                # Success - print message and log
                self.console.print(f"[green]✓[/green] Created {secure_file_path}")
                logger.info(
                    "Component created successfully",
                    operation="create_component",
                    file_path=str(secure_file_path),
                    component_name=component_name,
                    component_type=component_type,
                    layer=layer,
                )
                # secure_file_path is already guaranteed to be a Path object
                # Return will happen after finally block

        except Exception as e:
            # Log the error with context
            logger.error(
                "Component creation failed",
                operation="create_component",
                error=str(e),
                error_type=type(e).__name__,
                component_name=component_name,
                component_type=component_type,
                file_path=(
                    str(secure_file_path) if "secure_file_path" in locals() else None
                ),
            )

            # Rollback on failure
            if backup_path and backup_path.exists():
                try:
                    if secure_file_path.exists():
                        secure_file_path.unlink()
                    backup_path.rename(secure_file_path)
                    logger.info(
                        "Rollback completed successfully",
                        operation="rollback",
                        file_path=str(secure_file_path),
                    )
                except Exception as rollback_error:
                    logger.error(
                        "Rollback failed",
                        operation="rollback",
                        error=str(rollback_error),
                        file_path=str(secure_file_path),
                    )
                    self.console.print(
                        f"[red]Error during rollback: {rollback_error}[/red]"
                    )

            if isinstance(e, (ComponentError, ValidationError)):
                raise
            raise ValidationError(f"Failed to write file: {e}")
        finally:
            # Always clean up lock file
            if lock_file.exists():
                try:
                    lock_file.unlink()
                except (OSError, FileNotFoundError):
                    pass  # Ignore cleanup errors

        # Return the secure file path after successful completion
        return secure_file_path

    def _atomic_write_file(self, file_path: Path, content: str) -> None:
        """Write file atomically to prevent corruption and TOCTOU vulnerabilities.

        Uses temporary file in same directory and atomic rename to ensure:
        1. No partial writes visible to other processes
        2. No race conditions between check and write
        3. Proper cleanup on failure
        4. File locking to prevent concurrent access
        """
        # Ensure we have absolute path
        file_path = file_path.resolve()

        # Use secure file operation with locking
        secure_file_operation(file_path, self._perform_atomic_write, file_path, content)

    def _perform_atomic_write(self, file_path: Path, content: str) -> None:
        """Perform the actual atomic write operation."""
        import os
        import tempfile

        # file_path is already guaranteed to be a Path object by type annotation
        # Ensure we have a valid parent directory
        parent_dir = file_path.parent
        if parent_dir is None or str(parent_dir) == ".":
            parent_dir = Path.cwd()

        # Ensure parent directory exists with proper error handling
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise create_secure_error("directory_creation", "create directory", str(e))

        # Use atomic write with temporary file in same directory
        temp_fd = None
        temp_path = None
        try:
            # Create temporary file in same directory as target
            temp_fd, temp_path = tempfile.mkstemp(
                dir=parent_dir, prefix=f".{file_path.name}.", suffix=".tmp"
            )

            # Write content to temporary file
            with os.fdopen(temp_fd, "w", encoding="utf-8") as temp_file:
                temp_file.write(content)
                temp_file.flush()
                os.fsync(temp_file.fileno())  # Ensure data is written to disk
            # File descriptor is now closed by context manager

            # Atomically move temporary file to target location
            temp_path_obj = Path(temp_path)
            temp_path_obj.replace(file_path)

            # Verify file was written correctly
            if not file_path.exists() or file_path.stat().st_size == 0:
                raise create_secure_error(
                    "file_write", "write file", "verification failed"
                )

        except OSError as e:
            # Handle permission errors and other OS-level issues
            if e.errno == 13:  # Permission denied
                raise create_secure_error(
                    "file_write", "write file", "permission denied"
                )
            elif e.errno == 28:  # No space left on device
                raise create_secure_error(
                    "file_write", "write file", "insufficient disk space"
                )
            else:
                raise create_secure_error("file_write", "write file", str(e))
        except Exception:
            # Clean up temporary file on any other failure
            if temp_path and Path(temp_path).exists():
                try:
                    Path(temp_path).unlink()
                except OSError:
                    pass
            raise

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
            components_spec: Dict like {
                "domain": {"entities": ["user", "order"], "repositories": ["user"]},
                "application": {"services": ["user_service"]},
                "infrastructure": {"database": {"repositories": ["user"]}}
            }
        """
        created_files = []

        for layer, layer_components in components_spec.items():
            # Handle nested infrastructure database components
            if layer == "infrastructure" and isinstance(layer_components, dict):
                for component_type, component_data in layer_components.items():
                    if component_type == "database" and isinstance(
                        component_data, dict
                    ):
                        # Handle nested database components
                        for (
                            db_component_type,
                            component_names,
                        ) in component_data.items():
                            for component_name in component_names:
                                try:
                                    file_path = self.create_component(
                                        base_path=base_path,
                                        system_name=system_name,
                                        module_name=module_name,
                                        layer=layer,
                                        component_type=db_component_type,
                                        component_name=component_name,
                                        dry_run=dry_run,
                                        force=force,
                                    )
                                    created_files.append(file_path)
                                except Exception as e:
                                    self.console.print(
                                        f"[red]Error creating {component_name}:[/red] {e}"
                                    )
                                    if not force:
                                        raise
                    else:
                        # Handle non-database infrastructure components
                        for component_name in component_data:
                            try:
                                file_path = self.create_component(
                                    base_path=base_path,
                                    system_name=system_name,
                                    module_name=module_name,
                                    layer=layer,
                                    component_type=component_type,
                                    component_name=component_name,
                                    dry_run=dry_run,
                                    force=force,
                                )
                                created_files.append(file_path)
                            except Exception as e:
                                self.console.print(
                                    f"[red]Error creating {component_name}:[/red] {e}"
                                )
                                if not force:
                                    raise
            else:
                # Handle standard layer components
                for component_type, component_names in layer_components.items():  # type: ignore[assignment]
                    # Ensure component_names is a list
                    if isinstance(component_names, list):
                        names_list: List[str] = component_names
                        for component_name in names_list:
                            try:
                                file_path = self.create_component(
                                    base_path=base_path,
                                    system_name=system_name,
                                    module_name=module_name,
                                    layer=layer,
                                    component_type=component_type,
                                    component_name=component_name,
                                    dry_run=dry_run,
                                    force=force,
                                )
                                created_files.append(file_path)
                            except Exception as e:
                                self.console.print(
                                    f"[red]Error creating {component_name}:[/red] {e}"
                                )
                                if not force:
                                    raise

        return created_files

    def _validate_component_inputs(
        self,
        system_name: str,
        module_name: str,
        layer: str,
        component_type: str,
        component_name: str,
    ) -> None:
        """Validate component creation inputs."""
        # Validate system name
        try:
            validate_name(system_name)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid system name: {e}")

        # Validate module name
        try:
            validate_name(module_name)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid module name: {e}")

        # Validate component name
        try:
            validate_name(component_name)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid component name: {e}")

        # Validate and normalize layer using centralized validation
        from ..validation import Validator

        layer_result = Validator.validate_layer(layer)
        if layer_result.is_failure:
            error = layer_result.error
            if error is not None:
                raise error
            else:
                raise ValidationError(
                    f"Layer validation failed for '{layer}' but no error details available"
                )

        # Update layer to the normalized form for further processing
        validated_layer = layer_result.unwrap()

        # Use centralized layer-aware validation
        component_validation_result = Validator.validate_component_type_for_layer(
            component_type, validated_layer
        )
        if component_validation_result.is_failure:
            error = component_validation_result.error
            if error is None:
                raise ValidationError("Validation failed but no error was provided")
            raise error

        if not component_name.strip():
            raise ValidationError("Component name cannot be empty")

    def _get_component_file_path(
        self,
        base_path: Path,
        system_name: str,
        module_name: str,
        layer: str,
        component_type: str,
        component_name: str,
        nested_type: Optional[str] = None,
    ) -> Tuple[Path, str]:
        """Get the file path and name for a component with nested structure support."""
        # Determine file name based on component type
        file_name = self._get_component_file_name(
            nested_type or component_type, component_name
        )

        # Map component type to actual directory name
        directory_name = component_type
        if layer == "domain" and component_type == "repositories":
            directory_name = "interfaces"

        # Handle nested structure for use_cases
        if component_type == "use_cases" and nested_type:
            # Build nested path: application/use_cases/commands or application/use_cases/queries
            file_path = (
                base_path
                / "systems"
                / system_name
                / module_name
                / layer
                / "use_cases"
                / nested_type
                / file_name
            )
        # Handle infrastructure database components
        elif layer == "infrastructure" and component_type in [
            "repositories",
            "models",
            "migrations",
        ]:
            # Build nested path: infrastructure/database/repositories, infrastructure/database/models, etc.
            file_path = (
                base_path
                / "systems"
                / system_name
                / module_name
                / layer
                / "database"
                / directory_name
                / file_name
            )
        else:
            # Build standard path
            file_path = (
                base_path
                / "systems"
                / system_name
                / module_name
                / layer
                / directory_name
                / file_name
            )

        return file_path, file_name

    def _get_component_file_name(self, component_type: str, component_name: str) -> str:
        """Get the file name for a component based on its type."""
        snake_name = to_snake_case(component_name)

        file_name_patterns = {
            "entities": f"{snake_name}.py",
            "repositories": f"{snake_name}_repository.py",
            "value_objects": f"{snake_name}.py",
            "services": f"{snake_name}_service.py",
            "commands": f"{snake_name}.py",
            "queries": f"{snake_name}.py",
            "models": f"{snake_name}_model.py",
            "external": f"{snake_name}_client.py",
            "api": f"{snake_name}_router.py",
            "schemas": f"{snake_name}_schemas.py",
        }

        return file_name_patterns.get(component_type, f"{snake_name}.py")

    def _get_template_name(
        self, layer: str, component_type: str, template_variant: Optional[str] = None
    ) -> str:
        """Get the template name for a component.

        Args:
            layer: Architecture layer (domain, application, etc.)
            component_type: Type of component (entity, service, etc.)
            template_variant: Optional template variant (simple, full, api)

        Returns:
            Template filename
        """
        # Special case for infrastructure repositories
        if layer == "infrastructure" and component_type == "repositories":
            return self.INFRASTRUCTURE_REPOSITORY_TEMPLATE

        base_template = self.TEMPLATE_MAPPING.get(component_type, "entity.py.j2")

        # Handle enum template variants
        if component_type == "enums" and template_variant:
            variant_mapping = {
                "simple": "enum.py.j2",  # Default simple template
                "full": "enum_full.py.j2",
                "api": "enum_api.py.j2",
            }
            return variant_mapping.get(template_variant, base_template)

        return base_template

    def _validate_template_variables(
        self, template_content_or_name: str, template_vars: Dict[str, Any]
    ) -> None:
        """Validate that all required template variables are available.

        Args:
            template_content_or_name: Template content or filename
            template_vars: Variables to validate against

        Raises:
            TemplateError: If validation fails
        """
        self.template_validator.validate(template_content_or_name, template_vars)

    def _validate_file_system(self, file_path: Path) -> None:
        """Validate file system security and basic requirements."""
        import os
        import shutil

        try:
            # Prevent symlink attacks by checking the entire path
            self._check_symlink_attack(file_path)

            # Basic permission check (not relied upon for security due to TOCTOU)
            # This is kept for early validation and test compatibility
            parent_dir = file_path.parent
            if parent_dir.exists():
                if not os.access(parent_dir, os.W_OK):
                    raise create_secure_error(
                        "permission_denied",
                        "access directory",
                        "write permission denied",
                    )

            # Check available disk space (require at least 1MB)
            # Use parent directory or current directory for disk space check
            check_dir = file_path.parent if file_path.parent.exists() else Path.cwd()
            try:
                disk_usage = shutil.disk_usage(check_dir)
                free_space = (
                    disk_usage[2] if isinstance(disk_usage, tuple) else disk_usage.free
                )
                if free_space < 1024 * 1024:  # 1MB
                    raise ValidationError("Insufficient disk space")
            except OSError:
                # If we can't check disk space, continue but warn
                import logging

                logging.warning("Could not check disk space")

        except (ComponentError, ValidationError):
            raise
        except Exception as e:
            raise create_secure_error(
                "file_system_validation", "validate file system", str(e)
            )

    def _check_symlink_attack(self, file_path: Path) -> None:
        """Check for potential symlink attacks in the file path.

        This method prevents symlink attacks by ensuring that no part of the path
        contains symbolic links that could redirect file creation outside the
        intended directory structure.
        """
        try:
            # Use strict=True to fail on broken symlinks and detect symlink issues early
            try:
                resolved_path = file_path.resolve(strict=True)
            except (OSError, RuntimeError):
                # If strict resolution fails, try non-strict and validate manually
                resolved_path = file_path.resolve(strict=False)
                # Additional validation: check if any component is a broken symlink
                current = file_path
                while current != current.parent:
                    if current.is_symlink() and not current.exists():
                        raise ValidationError(
                            f"Broken symlink detected in path: {current}. "
                            "File creation through broken symlinks is not allowed."
                        )
                    current = current.parent

            # More robust symlink detection - check each component of the original path
            current_path = file_path
            while current_path != current_path.parent:
                if current_path.exists() and current_path.is_symlink():
                    # Instead of hardcoded allowlist, use more sophisticated validation
                    # Use os.readlink for Python 3.8 compatibility
                    import os

                    try:
                        symlink_target = Path(os.readlink(current_path))
                    except (OSError, AttributeError):
                        # If readlink fails, treat as unsafe
                        raise ValidationError(f"Cannot resolve symlink: {current_path}")

                    # Check if symlink points outside the project or to dangerous locations
                    if symlink_target.is_absolute():
                        # Absolute symlinks are generally more dangerous
                        if not self._is_safe_system_symlink(
                            current_path, symlink_target
                        ):
                            raise ValidationError(
                                f"Potentially unsafe symlink detected: {current_path} -> {symlink_target}. "
                                "File creation through unsafe symlinks is not allowed for security reasons."
                            )
                    else:
                        # Relative symlinks - resolve and check if they stay within bounds
                        try:
                            resolved_target = (
                                current_path.parent / symlink_target
                            ).resolve(strict=True)
                            if not self._is_path_within_safe_bounds(resolved_target):
                                raise ValidationError(
                                    f"Symlink points outside safe boundaries: {current_path} -> {resolved_target}. "
                                    "File creation through such symlinks is not allowed."
                                )
                        except (OSError, RuntimeError):
                            raise ValidationError(
                                f"Invalid symlink target: {current_path} -> {symlink_target}. "
                                "File creation through invalid symlinks is not allowed."
                            )

                current_path = current_path.parent

            # Enhanced temp directory detection with more robust cross-platform support
            if (
                not self._is_temp_path(resolved_path)
                and "systems" not in resolved_path.parts
            ):
                raise ValidationError(
                    f"Invalid file path: {file_path}. "
                    "Component files must be created within the systems directory structure."
                )

            # Additional validation after path resolution
            self._validate_resolved_path(file_path, resolved_path)

        except ValidationError:
            # Re-raise validation errors as-is
            raise
        except (OSError, RuntimeError) as e:
            # Handle cases where path resolution fails
            raise create_secure_error("path_validation", "validate path", str(e))

    def _is_safe_system_symlink(self, symlink_path: Path, target_path: Path) -> bool:
        """Check if a symlink is a safe system symlink.

        This method uses more sophisticated logic than hardcoded allowlists
        to determine if a symlink is safe.
        """
        symlink_str = str(symlink_path)
        target_str = str(target_path)

        # Common safe system symlink patterns across platforms
        safe_patterns = [
            # Unix/Linux system symlinks
            ("/var", "/private/var"),  # macOS /var -> /private/var
            ("/tmp", "/private/tmp"),  # macOS /tmp -> /private/tmp  # nosec B108
            ("/etc", "/private/etc"),  # macOS /etc -> /private/etc
            # Other common system symlinks
            ("/usr/bin", "/bin"),
            ("/usr/lib", "/lib"),
        ]

        # Check if this matches known safe system symlink patterns
        for safe_source, safe_target in safe_patterns:
            if symlink_str.startswith(safe_source) and target_str.startswith(
                safe_target
            ):
                return True

        # Additional checks for system directories
        system_dirs = {"/usr", "/bin", "/lib", "/sbin", "/opt", "/System", "/Library"}
        if any(symlink_str.startswith(d) for d in system_dirs) and any(
            target_str.startswith(d) for d in system_dirs
        ):
            return True

        return False

    def _is_path_within_safe_bounds(self, path: Path) -> bool:
        """Check if a resolved path is within safe boundaries."""
        path_str = str(path)

        # Paths that should never be accessible
        dangerous_paths = {
            "/etc/passwd",
            "/etc/shadow",
            "/etc/hosts",
            "/root",
            "/boot",
            "/proc",
            "/sys",
            "/dev",
        }

        # Check for exact matches or if path starts with dangerous directories
        for dangerous in dangerous_paths:
            if path_str == dangerous or path_str.startswith(dangerous + "/"):
                return False

        return True

    def _is_temp_path(self, path: Union[Path, str]) -> bool:
        """Enhanced cross-platform temporary directory detection with caching.

        Args:
            path: Path to check (accepts both Path objects and strings)

        Returns:
            bool: True if path is detected as temporary, False otherwise
        """
        # Convert string to Path if needed
        if isinstance(path, str):
            path = Path(path)

        # Use cached version for performance
        result = self._is_temp_path_cached(str(path))

        # Log security events for temp path access
        if result:
            logger.debug(f"Temporary path access detected: {path}")

        return result

    @functools.lru_cache(maxsize=128)
    def _is_temp_path_cached(self, path_str: str) -> bool:
        """Cached implementation of temporary path detection."""
        import tempfile

        path = Path(path_str)

        try:
            # Primary method: Use system's temp directory detection
            system_temp = Path(tempfile.gettempdir()).resolve()

            # Check if path is relative to system temp directory
            try:
                # Use compatibility method for Python 3.8
                resolved_path = path.resolve()
                # Check if path is under system temp using relative_to
                try:
                    resolved_path.relative_to(system_temp)
                    return True
                except ValueError:
                    # Path is not relative to system temp
                    pass
            except (AttributeError, ValueError):
                # Fallback for older Python versions or path resolution issues
                if str(path.resolve()).startswith(str(system_temp)):
                    return True

        except (OSError, ValueError):
            pass

        # Always check fallback patterns if primary method didn't match
        return self._fallback_temp_detection(path)

    def _fallback_temp_detection(self, path: Path) -> bool:
        """Enhanced fallback temporary directory detection with configurable patterns.

        Args:
            path: Path object to check for temporary directory patterns

        Returns:
            bool: True if path matches temporary directory patterns
        """
        import os

        path_str = str(path).lower()

        # Check environment variables
        temp_env_vars = ["TMPDIR", "TEMP", "TMP"]
        for env_var in temp_env_vars:
            if env_var in os.environ:
                try:
                    env_temp = Path(os.environ[env_var]).resolve()
                    if str(path).startswith(str(env_temp)):
                        return True
                except (ValueError, OSError):
                    continue

        # Check for pytest temp directories (common in testing)
        if "pytest-of-" in path_str:
            return True

        # Get custom temp patterns from config if available
        custom_patterns = self._get_custom_temp_patterns()

        # Check for common temp directory patterns
        temp_patterns = [
            "/tmp/",  # nosec B108
            "/temp/",
            "/temporary/",
            "/var/tmp/",  # nosec B108
            "/var/temp/",
            "/private/var/folders/",  # macOS temp
            "appdata/local/temp/",  # Windows temp
        ] + custom_patterns

        for pattern in temp_patterns:
            if pattern in path_str:
                return True

        # Check for common temp directory names in path parts
        temp_names = {"tmp", "temp", "temporary"}
        for part in path.parts:
            if part.lower() in temp_names:
                return True

        return False

    def _get_custom_temp_patterns(self) -> List[str]:
        """Get custom temporary directory patterns from configuration.

        Returns:
            List[str]: Custom temporary directory patterns
        """
        try:
            # Try to get custom patterns from config
            if hasattr(self, "config") and hasattr(self.config, "custom_temp_patterns"):
                return getattr(self.config, "custom_temp_patterns", [])
        except (AttributeError, TypeError):
            pass

        # Return empty list if no custom patterns configured
        return []

    def _validate_resolved_path(self, original_path: Path, resolved_path: Path) -> None:
        """Enhanced validation after path resolution with security logging.

        Args:
            original_path: The original path before resolution
            resolved_path: The resolved absolute path

        Raises:
            ValidationError: If path validation fails
        """
        # Check for path traversal attempts
        if ".." in str(original_path):
            logger.warning(f"Path traversal attempt detected: {original_path}")

            # Verify that after resolution, we haven't escaped intended boundaries
            original_parts = str(original_path).split(os.sep)
            if ".." in original_parts:
                # Count directory traversals
                traversal_count = original_parts.count("..")
                if traversal_count > 2:  # Allow some reasonable traversal
                    logger.error(
                        f"Excessive path traversal blocked: {original_path} (count: {traversal_count})"
                    )
                    raise ValidationError(
                        f"Excessive path traversal detected in: {original_path}. "
                        "This may indicate a path traversal attack."
                    )

        # Ensure resolved path doesn't point to sensitive system locations
        if not self._is_path_within_safe_bounds(resolved_path):
            logger.error(f"Restricted path access blocked: {resolved_path}")
            raise ValidationError(
                f"Resolved path points to restricted location: {resolved_path}. "
                "File creation in this location is not allowed."
            )

    def _sanitize_template_variables(
        self, template_vars: Dict[str, Any], depth: int = 0
    ) -> Dict[str, Any]:
        """Enhanced sanitization of template variables with security logging and recursion protection.

        Args:
            template_vars: Dictionary of template variables to sanitize
            depth: Current recursion depth (for DoS protection)

        Returns:
            Dict[str, Any]: Sanitized template variables

        Raises:
            ValidationError: If recursion depth exceeds safe limits
        """
        # Prevent deep recursion DoS attacks
        if depth > 10:
            raise ValidationError(
                f"Template variable nesting too deep (max depth: 10, current: {depth})"
            )
        sanitized_vars: Dict[str, Any] = {}
        suspicious_patterns_found: List[str] = []

        for key, value in template_vars.items():
            if isinstance(value, str):
                original_value = value
                sanitized_vars[key] = self._sanitize_string_value(value)
                # Check if sanitization changed the value (potential injection attempt)
                if original_value != sanitized_vars[key]:
                    suspicious_patterns_found.append(
                        f"Variable '{key}': {original_value[:50]}..."
                    )
            elif isinstance(value, (int, float, bool)) or value is None:
                sanitized_vars[key] = value
            elif isinstance(value, (list, tuple)):
                # Recursively sanitize list/tuple items
                sanitized_list: List[Any] = []
                for item in value:
                    if isinstance(item, dict):
                        sanitized_list.append(
                            self._sanitize_template_variables(item, depth + 1)
                        )
                    else:
                        sanitized_list.append(self._sanitize_single_value(item))
                sanitized_vars[key] = sanitized_list
            elif isinstance(value, dict):
                # Recursively sanitize dict values
                sanitized_vars[key] = self._sanitize_template_variables(
                    value, depth + 1
                )
            else:
                # Convert other types to string and sanitize
                sanitized_vars[key] = self._sanitize_single_value(str(value))

        # Log security events if suspicious patterns were found
        if suspicious_patterns_found:
            logger.warning(
                f"Potential injection patterns sanitized in template variables: {suspicious_patterns_found}"
            )

        return sanitized_vars

    def _sanitize_string_value(self, value: Any) -> str:
        """Enhanced sanitization for string values to prevent various injection attacks."""
        import unicodedata
        import urllib.parse

        if not isinstance(value, str):
            value = str(value)

        # URL decode to catch encoded injection attempts
        try:
            decoded_value = urllib.parse.unquote(value)
        except (ValueError, UnicodeDecodeError):
            decoded_value = value

        # Unicode normalization to prevent Unicode-based attacks

        normalized_value = unicodedata.normalize("NFKC", decoded_value)

        # Remove dangerous patterns for template injection
        dangerous_patterns = [
            r"\{\{.*?\}\}",  # Jinja2 expressions
            r"\{%.*?%\}",  # Jinja2 statements
            r"\{#.*?#\}",  # Jinja2 comments
            r"<script[^>]*>.*?</script>",  # Script tags
            r"javascript:",  # JavaScript URLs
            r"data:",  # Data URLs
            r"vbscript:",  # VBScript URLs
            r"on\w+\s*=",  # Event handlers
            r"\\x[0-9a-fA-F]{2}",  # Hex escapes
            r"\\u[0-9a-fA-F]{4}",  # Unicode escapes
            r"\\[rnt]",  # Common escapes
            r"__.*__",  # Python dunder methods
            r"\beval\b",  # eval function
            r"\bexec\b",  # exec function
            r"\bimport\b",  # import statements
            r"\bopen\b",  # file operations
            r"\bfile\b",  # file operations
            r"\bos\.",  # os module access
            r"\bsys\.",  # sys module access
        ]

        sanitized = normalized_value
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE | re.DOTALL)

        # Remove control characters and dangerous Unicode categories
        sanitized = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", sanitized)

        # Remove potentially dangerous characters (but preserve forward slashes for URLs)
        sanitized = re.sub(r'[<>"\'\\`$]', "", sanitized)

        # Limit length to prevent DoS
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000]

        return sanitized

    def _sanitize_single_value(self, value: Any) -> str:
        """Sanitize a single value."""
        if not isinstance(value, str):
            value = str(value)
        return self._sanitize_string_value(value)

    def _sanitize_template_output(self, value: Any) -> str:
        """Finalize function to sanitize template output."""
        if value is None:
            return ""
        return self._sanitize_single_value(str(value))

    def _setup_sandbox_security(self) -> None:
        """Configure enhanced sandbox security settings with minimal attack surface."""
        # Define a minimal set of safe builtins (reduced from previous version)
        allowed_builtins = {
            "range": range,
            "len": len,
            "str": str,
            "int": int,
            "bool": bool,
            "list": list,
            "dict": dict,
            "enumerate": enumerate,
        }

        # Override the globals to only include safe functions
        self.template_env.globals.clear()
        self.template_env.globals.update(allowed_builtins)

        # Define allowed filters (keep only safe ones)
        safe_filters = {
            "upper",
            "lower",
            "title",
            "capitalize",
            "strip",
            "replace",
            "length",
            "first",
            "last",
            "join",
            "default",
            "trim",
            "truncate",
            "wordwrap",
            "center",
            "indent",
        }

        # Remove ALL potentially dangerous filters and globals
        dangerous_items = [
            # Attribute access
            "attr",
            "getattr",
            "setattr",
            "delattr",
            "hasattr",
            # Code execution
            "import",
            "exec",
            "eval",
            "compile",
            "__import__",
            # File operations
            "open",
            "file",
            "input",
            "raw_input",
            # System access
            "globals",
            "locals",
            "vars",
            "dir",
            # Object introspection
            "type",
            "isinstance",
            "issubclass",
            "callable",
            # Dangerous builtins removed from allowed list
            "float",
            "tuple",
            "zip",
            "map",
            "filter",
            "reduce",
        ]

        # Remove from filters
        for item_name in dangerous_items:
            if item_name in self.template_env.filters:
                del self.template_env.filters[item_name]
            # Also remove from globals if present
            if item_name in self.template_env.globals:
                del self.template_env.globals[item_name]

        # Remove potentially dangerous filters
        current_filters = set(self.template_env.filters.keys())
        dangerous_filters = current_filters - safe_filters

        for filter_name in dangerous_filters:
            if filter_name in self.template_env.filters:
                del self.template_env.filters[filter_name]

    def _render_template(
        self, template_name: str, template_vars: Dict[str, Any]
    ) -> str:
        """Render a template with the given variables."""
        try:
            # Sanitize template variables before rendering
            sanitized_vars = self._sanitize_template_variables(template_vars)

            template = self.template_env.get_template(template_name)
            return template.render(**sanitized_vars)
        except jinja2.TemplateNotFound:
            raise TemplateError(f"Template not found: {template_name}")
        except jinja2.TemplateError as e:
            raise TemplateError(f"Error rendering template {template_name}: {e}")
        except Exception as e:
            raise TemplateError(f"Unexpected error rendering template: {e}")

    def validate_component(self, component: Dict[str, Any]) -> bool:
        """Validate component configuration and structure.

        This method implements the ComponentGeneratorProtocol interface
        and provides comprehensive validation using type-safe strategies.

        Args:
            component: Component configuration dictionary

        Returns:
            True if component is valid

        Raises:
            ValidationError: If component is invalid
        """
        if not isinstance(component, dict):
            raise ValidationError(
                f"Component must be a dictionary, got {type(component)}"
            )

        # Extract component type for validation strategy selection
        component_type = component.get("type", "unknown")

        # Use appropriate validation strategy
        if component_type in self._validation_strategies:
            strategy = self._validation_strategies[component_type]
            return strategy.validate(component)

        # Fallback to basic validation
        required_fields = ["name", "type"]
        for field in required_fields:
            if field not in component:
                raise ValidationError(f"Missing required field '{field}' in component")

        # Validate component name
        try:
            validate_name(component["name"])
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid component name: {e}")
        except SecurityError:
            # Re-raise SecurityError as-is for proper handling
            raise

        return True

    def _setup_validation_strategies(
        self,
    ) -> Dict[str, ComponentValidationStrategy[str]]:
        """Setup type-safe validation strategies for different component types.

        Returns:
            Dictionary mapping component types to their validation strategies
        """
        strategies = {}

        # Entity validation strategy
        entity_rules = {
            "required_fields": ["name", "type"],
            "field_types": {
                "name": str,
                "type": str,
                "attributes": (list, type(None)),
                "methods": (list, type(None)),
            },
        }
        strategies["entity"] = ComponentValidationStrategy("entity", entity_rules)

        # Service validation strategy
        service_rules = {
            "required_fields": ["name", "type"],
            "field_types": {
                "name": str,
                "type": str,
                "dependencies": (list, type(None)),
                "methods": (list, type(None)),
            },
        }
        strategies["service"] = ComponentValidationStrategy("service", service_rules)

        # Repository validation strategy
        repository_rules = {
            "required_fields": ["name", "type"],
            "field_types": {
                "name": str,
                "type": str,
                "entity_type": (str, type(None)),
                "methods": (list, type(None)),
            },
        }
        strategies["repository"] = ComponentValidationStrategy(
            "repository", repository_rules
        )

        # Add more strategies for other component types
        for component_type in [
            "value_object",
            "command",
            "query",
            "model",
            "external",
            "api",
            "schema",
        ]:
            basic_rules = {
                "required_fields": ["name", "type"],
                "field_types": {
                    "name": str,
                    "type": str,
                },
            }
            strategies[component_type] = ComponentValidationStrategy(
                component_type, basic_rules
            )

        return strategies

    def create_component_with_validation(
        self,
        component_config: Dict[str, Any],
        base_path: Path,
        dry_run: bool = False,
        force: bool = False,
    ) -> Path:
        """Create a component with enhanced type-safe validation.

        This method provides an alternative interface that uses the new
        validation strategies and secure path handling.

        Args:
            component_config: Component configuration dictionary
            base_path: Base directory for component creation
            dry_run: If True, only simulate the operation
            force: If True, overwrite existing files

        Returns:
            Path to the created component file

        Raises:
            ValidationError: If component configuration is invalid
            SecurityError: If security constraints are violated
        """
        # Validate component configuration
        self.validate_component(component_config)

        # Validate and secure the base path
        secure_base_path = Path(self.path_handler.process(base_path))

        # Extract component details
        system_name = component_config.get("system_name", "default")
        module_name = component_config.get("module_name", "default")
        layer = component_config.get("layer", "domain")
        component_type = component_config["type"]
        component_name = component_config["name"]

        # Use the existing create_component method with validated inputs
        result = self.create_component(
            base_path=secure_base_path,
            system_name=system_name,
            module_name=module_name,
            layer=layer,
            component_type=component_type,
            component_name=component_name,
            dry_run=dry_run,
            force=force,
        )
        return Path(result)
