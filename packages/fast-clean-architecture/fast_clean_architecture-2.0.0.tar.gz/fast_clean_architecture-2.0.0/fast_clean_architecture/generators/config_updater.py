"""Configuration updater for managing fca_config.yaml updates."""

import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console

from ..config import Config
from ..exceptions import ConfigurationError, Result
from ..utils import generate_timestamp
from ..validation import Validator


class ConfigUpdater:
    """Handles updates to the fca_config.yaml file with proper timestamp management."""

    def __init__(self, config_path: Path, console: Optional[Console] = None):
        self.config_path = config_path
        if console is None:
            raise ValueError(
                "Console dependency must be provided explicitly (Phase 3 Architecture Cleanup)"
            )
        self.console = console
        self._config: Optional[Config] = None

    @property
    def config(self) -> Config:
        """Lazy load the configuration."""
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def _load_config(self) -> Config:
        """Load configuration from file or create default."""
        result = self._load_config_safe()
        return result.unwrap()

    def _load_config_safe(self) -> Result[Config, ConfigurationError]:
        """Safely load configuration with Result pattern.

        Phase 3 Architecture Cleanup: Requires explicit configuration.
        No fallback creation - configuration must exist or be explicitly provided.
        """
        try:
            if self.config_path.exists():
                config = Config.load_from_file(self.config_path)
                return Result.success(config)
            else:
                # No fallback creation - configuration must be explicitly provided
                return Result.failure(
                    ConfigurationError(
                        f"Configuration file not found: {self.config_path}. "
                        f"Please initialize the project first with 'fca-scaffold init' "
                        f"or provide explicit configuration.",
                        context={
                            "path": str(self.config_path),
                            "action": "missing_config",
                        },
                    )
                )
        except Exception as e:
            return Result.failure(
                ConfigurationError(
                    f"Failed to load configuration from {self.config_path}",
                    context={"path": str(self.config_path), "error": str(e)},
                )
            )

    def backup_config(self) -> Path:
        """Create a backup of the current configuration."""
        result = self._backup_config_safe()
        return result.unwrap()

    def _backup_config_safe(self) -> Result[Path, ConfigurationError]:
        """Safely create a backup with Result pattern."""
        try:
            if not self.config_path.exists():
                return Result.failure(
                    ConfigurationError(
                        f"Configuration file does not exist: {self.config_path}",
                        context={"path": str(self.config_path)},
                    )
                )

            timestamp = generate_timestamp().replace(":", "-").replace(".", "-")
            # Create backup directory if it doesn't exist
            backup_dir = self.config_path.parent / "fca_config_backups"
            backup_dir.mkdir(exist_ok=True)
            backup_path = (
                backup_dir / f"{self.config_path.stem}.backup.{timestamp}.yaml"
            )

            shutil.copy2(self.config_path, backup_path)
            self.console.print(f"📋 Config backed up to: {backup_path}")

            # Clean up old backups (keep only last 5)
            self._cleanup_old_backups()

            return Result.success(backup_path)
        except Exception as e:
            return Result.failure(
                ConfigurationError(
                    f"Failed to create backup: {e}",
                    context={"source": str(self.config_path), "error": str(e)},
                )
            )

    def _cleanup_old_backups(self, keep_count: int = 5) -> None:
        """Clean up old backup files created by ConfigUpdater, keeping only the most recent ones."""
        try:
            backup_dir = self.config_path.parent / "fca_config_backups"
            if not backup_dir.exists():
                return

            # Pattern for ConfigUpdater backups: filename.backup.timestamp.yaml
            backup_pattern = f"{self.config_path.stem}.backup.*.yaml"
            backup_files = list(backup_dir.glob(backup_pattern))

            if len(backup_files) > keep_count:
                # Sort by modification time (newest first)
                backup_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

                # Remove old backups
                for old_backup in backup_files[keep_count:]:
                    try:
                        old_backup.unlink()
                        self.console.print(
                            f"🗑️  Removed old backup: {old_backup.name}", style="dim"
                        )
                    except OSError:
                        # Ignore errors when cleaning up old backups
                        pass
        except OSError:
            # Don't fail the main operation if backup cleanup fails
            pass

    def add_system(
        self,
        system_name: str,
        description: Optional[str] = None,
        backup: bool = True,
    ) -> None:
        """Add a new system to the configuration with validation."""
        # Validate system name
        name_result = Validator.validate_system_name(system_name)
        if name_result.is_failure:
            name_result.unwrap()  # This will raise the error

        # Validate description if provided
        if description:
            desc_result = Validator.validate_description(description)
            if desc_result.is_failure:
                desc_result.unwrap()  # This will raise the error

        if backup and self.config_path.exists():
            self.backup_config()

        # Add system to config
        validated_name = name_result.unwrap()
        self.config.add_system(validated_name, description or "")

        # Save updated config
        self._save_config_atomically()

        self.console.print(f"✅ Added system: {validated_name}")

    def add_module(
        self,
        system_name: str,
        module_name: str,
        description: Optional[str] = None,
        api_version: Optional[str] = None,
        backup: bool = True,
    ) -> bool:
        """Add a new module to a system with validation.

        Returns:
            bool: True if module was newly created, False if existing module was updated
        """
        # Validate system name
        system_result = Validator.validate_system_name(system_name)
        if system_result.is_failure:
            system_result.unwrap()  # This will raise the error

        # Validate module name
        module_result = Validator.validate_module_name(module_name)
        if module_result.is_failure:
            module_result.unwrap()  # This will raise the error

        # Validate description if provided
        if description:
            desc_result = Validator.validate_description(description)
            if desc_result.is_failure:
                desc_result.unwrap()  # This will raise the error

        if backup and self.config_path.exists():
            self.backup_config()

        # Add module to config
        validated_system = system_result.unwrap()
        validated_module = module_result.unwrap()
        is_new_module = self.config.add_module(
            validated_system, validated_module, description or "", api_version
        )

        # Save updated config
        self._save_config_atomically()

        # Provide appropriate feedback based on whether module was new or updated
        if is_new_module:
            self.console.print(
                f"✅ Added module: {validated_module} to system: {validated_system}"
            )
        else:
            version_info = f" (API version {api_version})" if api_version else ""
            self.console.print(
                f"✅ Module '{validated_module}' already exists. Updated presentation layers{version_info} in system: {validated_system}"
            )

        return is_new_module

    def add_component(
        self,
        system_name: str,
        module_name: str,
        layer: str,
        component_type: str,
        component_name: str,
        file_path: Optional[Path] = None,
        backup: bool = True,
    ) -> None:
        """Add a new component to a module with comprehensive validation."""
        # Validate all inputs
        validation_result = Validator.validate_component_creation(
            system_name=system_name,
            module_name=module_name,
            layer=layer,
            component_type=component_type,
            component_name=component_name,
            file_path=file_path,
        )

        if validation_result.is_failure:
            validation_result.unwrap()  # This will raise the error

        if backup and self.config_path.exists():
            self.backup_config()

        # Add component to config using validated data
        validated_data = validation_result.unwrap()

        self.config.add_component(
            system_name=validated_data["system_name"],
            module_name=validated_data["module_name"],
            layer=validated_data["layer"],
            component_type=validated_data["component_type"],
            component_name=validated_data["component_name"],
            file_path=(
                str(validated_data["file_path"])
                if "file_path" in validated_data and validated_data["file_path"]
                else None
            ),
        )

        # Save updated config
        self._save_config_atomically()

        self.console.print(
            f"✅ Added component: {component_name} ({component_type}) "
            f"to {system_name}/{module_name}/{layer}"
        )

    def update_system_timestamp(self, system_name: str, backup: bool = True) -> None:
        """Update the timestamp for a system and cascade to project."""
        if backup and self.config_path.exists():
            self.backup_config()

        # Update system timestamp
        if system_name in self.config.project.systems:
            current_time = generate_timestamp()
            self.config.project.systems[system_name].updated_at = current_time
            self.config.project.updated_at = current_time

        # Save updated config
        self._save_config_atomically()

    def update_module_timestamp(
        self, system_name: str, module_name: str, backup: bool = True
    ) -> None:
        """Update the timestamp for a module and cascade to system and project."""
        if backup and self.config_path.exists():
            self.backup_config()

        # Update module, system, and project timestamps
        if (
            system_name in self.config.project.systems
            and module_name in self.config.project.systems[system_name].modules
        ):
            current_time = generate_timestamp()
            self.config.project.systems[system_name].modules[
                module_name
            ].updated_at = current_time
            self.config.project.systems[system_name].updated_at = current_time
            self.config.project.updated_at = current_time

        # Save updated config
        self._save_config_atomically()

    def update_project_metadata(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        version: Optional[str] = None,
        backup: bool = True,
    ) -> None:
        """Update project metadata."""
        if backup and self.config_path.exists():
            self.backup_config()

        # Update project metadata
        current_time = generate_timestamp()

        if name is not None:
            self.config.project.name = name
        if description is not None:
            self.config.project.description = description
        if version is not None:
            self.config.project.version = version

        self.config.project.updated_at = current_time

        # Save updated config
        self._save_config_atomically()

        self.console.print("✅ Updated project metadata")

    def remove_system(self, system_name: str, backup: bool = True) -> None:
        """Remove a system from the configuration."""
        if backup and self.config_path.exists():
            self.backup_config()

        # Remove system
        if system_name in self.config.project.systems:
            del self.config.project.systems[system_name]
            self.config.project.updated_at = generate_timestamp()

        # Save updated config
        self._save_config_atomically()

        self.console.print(f"🗑️ Removed system: {system_name}")

    def remove_module(
        self, system_name: str, module_name: str, backup: bool = True
    ) -> None:
        """Remove a module from a system."""
        if backup and self.config_path.exists():
            self.backup_config()

        # Remove module
        if (
            system_name in self.config.project.systems
            and module_name in self.config.project.systems[system_name].modules
        ):
            del self.config.project.systems[system_name].modules[module_name]
            current_time = generate_timestamp()
            self.config.project.systems[system_name].updated_at = current_time
            self.config.project.updated_at = current_time

        # Save updated config
        self._save_config_atomically()

        self.console.print(
            f"🗑️ Removed module: {module_name} from system: {system_name}"
        )

    def remove_component(
        self,
        system_name: str,
        module_name: str,
        layer: str,
        component_type: str,
        component_name: str,
        backup: bool = True,
    ) -> None:
        """Remove a component from a module."""
        if backup and self.config_path.exists():
            self.backup_config()

        # Navigate to the component and remove it
        try:
            system = self.config.project.systems[system_name]
            module = system.modules[module_name]
            layer_components = getattr(module.components, layer)
            component_list = getattr(layer_components, component_type)

            # Find and remove the component
            component_list[:] = [
                comp for comp in component_list if comp.name != component_name
            ]

            # Update timestamps
            current_time = generate_timestamp()
            module.updated_at = current_time
            system.updated_at = current_time
            self.config.project.updated_at = current_time

        except (KeyError, AttributeError) as e:
            raise ConfigurationError(f"Component not found: {e}")

        # Save updated config
        self._save_config_atomically()

        self.console.print(
            f"🗑️ Removed component: {component_name} ({component_type}) "
            f"from {system_name}/{module_name}/{layer}"
        )

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        summary: Dict[str, Any] = {
            "project": {
                "name": self.config.project.name,
                "version": self.config.project.version,
                "created_at": self.config.project.created_at,
                "updated_at": self.config.project.updated_at,
            },
            "systems": {},
        }

        for system_name, system in self.config.project.systems.items():
            summary["systems"][system_name] = {
                "description": system.description,
                "created_at": system.created_at,
                "updated_at": system.updated_at,
                "modules": list(system.modules.keys()),
            }

        return summary

    def _save_config_atomically(self) -> None:
        """Save configuration atomically to prevent corruption."""
        result = self._save_config_atomically_safe()
        result.unwrap()

    def _save_config_atomically_safe(self) -> Result[None, ConfigurationError]:
        """Safely save configuration with Result pattern."""
        temp_path: Optional[Path] = None
        try:
            # Write to temporary file first
            temp_path = self.config_path.with_suffix(".tmp")
            self.config.save_to_file(temp_path)

            # Atomic move
            temp_path.replace(self.config_path)
            return Result.success(None)

        except Exception as e:
            # Clean up temp file if it exists
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass  # Ignore cleanup errors
            return Result.failure(
                ConfigurationError(
                    f"Failed to save configuration: {e}",
                    context={"config_path": str(self.config_path), "error": str(e)},
                )
            )

    def reload_config(self) -> None:
        """Reload configuration from file."""
        self._config = None  # Force reload on next access

    def sync_config(
        self,
        project_root: Path,
        dry_run: bool = False,
        systems_filter: Optional[List[str]] = None,
        force: bool = False,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """Synchronize config with filesystem structure.

        Args:
            project_root: Root directory of the project
            dry_run: If True, only show what would be changed
            systems_filter: Only sync specific systems
            force: Overwrite existing entries
            verbose: Show detailed output

        Returns:
            Dict with sync results and statistics
        """
        from ..utils import ProjectScanner

        scanner = ProjectScanner(project_root)

        # Get current config data
        current_config_data = {
            "systems": {
                name: system.model_dump()
                for name, system in self.config.project.systems.items()
            }
        }

        # Find untracked items
        untracked = scanner.find_untracked_components(current_config_data)

        # Filter by systems if specified
        if systems_filter:
            untracked = self._filter_untracked_by_systems(untracked, systems_filter)

        # Prepare sync results
        # Filter out "No 'systems' directory found" error for empty projects
        filtered_errors = [
            error
            for error in untracked["errors"]
            if error != "No 'systems' directory found"
        ]

        sync_results: Dict[str, Any] = {
            "dry_run": dry_run,
            "systems_added": 0,
            "modules_added": 0,
            "components_added": 0,
            "errors": filtered_errors,
            "changes": [],
            "skipped": [],
        }

        if not dry_run:
            # Create backup before making changes
            if self.config_path.exists():
                self.backup_config()

        # Process untracked systems
        for system_name, system_data in untracked["systems"].items():
            if verbose:
                self.console.print(f"📁 Found untracked system: {system_name}")

            if not dry_run:
                try:
                    self.add_system(
                        system_name,
                        f"Auto-discovered system: {system_name}",
                        backup=False,
                    )
                    sync_results["systems_added"] += 1
                    sync_results["changes"].append(f"Added system: {system_name}")
                except Exception as e:
                    sync_results["errors"].append(
                        f"Failed to add system {system_name}: {e}"
                    )
            else:
                sync_results["changes"].append(f"Would add system: {system_name}")

        # Process existing systems when force=True
        if force:
            # Get all systems that exist in filesystem (including those already in config)
            all_discovered_systems = scanner.scan_project_structure()
            for system_name in all_discovered_systems.get("systems", {}).keys():
                if system_name in self.config.project.systems:
                    if verbose:
                        self.console.print(
                            f"🔄 Updating existing system: {system_name}"
                        )

                    if not dry_run:
                        try:
                            # Update the system description
                            system = self.config.project.systems[system_name]
                            system.description = (
                                f"Auto-discovered system: {system_name}"
                            )
                            sync_results["changes"].append(
                                f"Updated system: {system_name}"
                            )
                        except Exception as e:
                            sync_results["errors"].append(
                                f"Failed to update system {system_name}: {e}"
                            )
                    else:
                        sync_results["changes"].append(
                            f"Would update system: {system_name}"
                        )

        # Process untracked modules
        for module_key, module_data in untracked["modules"].items():
            system_name, module_name = module_key.split("/")
            if verbose:
                self.console.print(
                    f"📂 Found untracked module: {system_name}/{module_name}"
                )

            if not dry_run:
                try:
                    self.add_module(
                        system_name,
                        module_name,
                        f"Auto-discovered module: {module_name}",
                        backup=False,
                    )
                    sync_results["modules_added"] += 1
                    sync_results["changes"].append(
                        f"Added module: {system_name}/{module_name}"
                    )
                except Exception as e:
                    sync_results["errors"].append(
                        f"Failed to add module {system_name}/{module_name}: {e}"
                    )
            else:
                sync_results["changes"].append(
                    f"Would add module: {system_name}/{module_name}"
                )

        # Process untracked components
        for component in untracked["components"]:
            component_key = f"{component['system']}/{component['module']}/{component['layer']}/{component['component_type']}/{component['name']}"

            if verbose:
                self.console.print(f"📄 Found untracked component: {component_key}")

            # Check if component already exists and force is not enabled
            if not force and self._component_exists(component):
                sync_results["skipped"].append(
                    f"Component already exists: {component_key}"
                )
                continue

            if not dry_run:
                try:
                    self.add_component(
                        system_name=component["system"],
                        module_name=component["module"],
                        layer=component["layer"],
                        component_type=component["component_type"],
                        component_name=component["name"],
                        file_path=component["file_path"],
                        backup=False,
                    )
                    sync_results["components_added"] += 1
                    sync_results["changes"].append(f"Added component: {component_key}")
                except Exception as e:
                    sync_results["errors"].append(
                        f"Failed to add component {component_key}: {e}"
                    )
            else:
                sync_results["changes"].append(f"Would add component: {component_key}")

        # Save config if changes were made
        if not dry_run and (
            sync_results["systems_added"] > 0
            or sync_results["modules_added"] > 0
            or sync_results["components_added"] > 0
        ):
            try:
                self._save_config_atomically()
                if verbose:
                    self.console.print("💾 Configuration saved successfully")
            except Exception as e:
                sync_results["errors"].append(f"Failed to save configuration: {e}")

        return sync_results

    def _filter_untracked_by_systems(
        self, untracked: Dict[str, Any], systems_filter: List[str]
    ) -> Dict[str, Any]:
        """Filter untracked items by specified systems."""
        filtered = {
            "systems": {},
            "modules": {},
            "components": [],
            "errors": untracked["errors"],
        }

        # Filter systems
        for system_name in systems_filter:
            if system_name in untracked["systems"]:
                filtered["systems"][system_name] = untracked["systems"][system_name]

        # Filter modules
        for module_key, module_data in untracked["modules"].items():
            system_name = module_key.split("/")[0]
            if system_name in systems_filter:
                filtered["modules"][module_key] = module_data

        # Filter components
        for component in untracked["components"]:
            if component["system"] in systems_filter:
                filtered["components"].append(component)

        return filtered

    def _component_exists(self, component: Dict[str, Any]) -> bool:
        """Check if a component already exists in the config."""
        try:
            system = self.config.project.systems[component["system"]]
            module = system.modules[component["module"]]
            return component["name"] in module.components.model_dump().get(
                component["layer"], {}
            ).get(component["component_type"], {})
        except (KeyError, AttributeError):
            return False
