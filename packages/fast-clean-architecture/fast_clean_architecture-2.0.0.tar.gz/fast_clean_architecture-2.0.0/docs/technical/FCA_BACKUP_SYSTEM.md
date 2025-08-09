# FCA Configuration Backup System

## Overview

Fast Clean Architecture (FCA) implements an automatic backup system for `fca-config.yaml` files that provides configuration-specific recovery capabilities beyond traditional Git version control. This system creates timestamped backups during configuration-modifying operations, ensuring operational safety and enabling quick recovery from configuration errors.

## Purpose and Benefits

### Why FCA Needs Its Own Backup System

While Git provides excellent version control for source code, FCA's backup system serves specific operational needs:

1. **Configuration-Specific Recovery**: Provides immediate access to recent configuration states without navigating Git history
2. **Command-Level Safety**: Creates automatic backups before every config-modifying operation
3. **Development Workflow Integration**: Seamlessly integrates with FCA's CLI commands without requiring Git knowledge
4. **Operational Granularity**: Captures configuration changes at the command execution level, not just commit level

### Complementary Relationship with Git

- **Git**: Manages overall project history, branching, and collaborative development
- **FCA Backups**: Provides immediate, command-level configuration recovery and operational safety

## Implementation Details

### Backup Creation

Backups are automatically created in the following scenarios:

1. **Configuration Updates**: When `fca-config.yaml` is modified by any FCA command
2. **Sync Operations**: Before scanning and updating configuration during `sync-config`
3. **Module Management**: When adding, removing, or updating modules
4. **System Management**: When adding, removing, or updating system contexts

### Backup Storage

```
project-root/
├── fca-config.yaml                    # Current configuration
└── fca_config_backups/                # Backup directory
    ├── fca-config_20240115_143022.yaml # Timestamped backup
    ├── fca-config_20240115_142815.yaml # Previous backup
    └── fca-config_20240115_142301.yaml # Older backup
```

### Backup Naming Convention

```
fca-config_{YYYYMMDD}_{HHMMSS}.yaml
```

- **YYYY**: 4-digit year
- **MM**: 2-digit month
- **DD**: 2-digit day
- **HH**: 2-digit hour (24-hour format)
- **MM**: 2-digit minute
- **SS**: 2-digit second

### Retention Policy

- **Maximum Backups**: 5 most recent backups are retained
- **Automatic Cleanup**: Older backups are automatically removed when the limit is exceeded
- **Cleanup Timing**: Performed after each new backup creation

## Technical Implementation

### Core Components

#### 1. Backup Creation (`config.py`)

```python
def save_to_file(self, file_path: Path) -> None:
    """Save configuration with automatic backup creation."""
    # Create backup before saving new configuration
    if file_path.exists():
        self._create_backup(file_path)
    
    # Atomic write operation
    temp_file = file_path.with_suffix('.tmp')
    with temp_file.open('w', encoding='utf-8') as f:
        yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)
    
    temp_file.replace(file_path)
    self._cleanup_old_backups(file_path)
```

#### 2. Backup Management (`config_updater.py`)

```python
def backup_config(self, config_path: Path) -> Optional[Path]:
    """Create timestamped backup of configuration file."""
    if not config_path.exists():
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"fca-config_{timestamp}.yaml"
    backup_path = config_path.parent / "fca_config_backups" / backup_filename
    
    backup_path.parent.mkdir(exist_ok=True)
    shutil.copy2(config_path, backup_path)
    
    self._cleanup_old_backups(config_path)
    return backup_path
```

#### 3. Cleanup Management

```python
def _cleanup_old_backups(self, config_path: Path) -> None:
    """Keep only the 5 most recent backups."""
    backup_dir = config_path.parent / "fca_config_backups"
    if not backup_dir.exists():
        return
    
    backup_files = sorted(
        backup_dir.glob("fca-config_*.yaml"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    # Remove backups beyond the retention limit
    for old_backup in backup_files[5:]:
        old_backup.unlink()
```

### Integration Points

#### CLI Commands with Backup Integration

1. **`sync-config`**: Creates backup before scanning and updating configuration
2. **Module Commands**: Backup before adding, removing, or updating modules
3. **System Commands**: Backup before system context modifications
4. **Component Generation**: Backup when configuration is updated during generation

#### Error Handling and Rollback

```python
def create_component_with_rollback(self, component_data: dict) -> None:
    """Create component with automatic rollback on failure."""
    backup_path = self.backup_config(self.config_path)
    
    try:
        # Perform component creation
        self._create_component_files(component_data)
        self._update_configuration(component_data)
    except Exception as e:
        # Rollback on failure
        if backup_path and backup_path.exists():
            shutil.copy2(backup_path, self.config_path)
        raise ComponentCreationError(f"Component creation failed: {e}")
```

## Operational Usage

### Automatic Backup Scenarios

#### During Sync Operations

```bash
# Backup created automatically before sync
$ fca-scaffold sync-config
✓ Configuration backed up to fca_config_backups/fca-config_20240115_143022.yaml
✓ Scanning project for untracked components...
✓ Configuration updated with 3 new components
```

#### During Module Management

```bash
# Backup created before module addition
$ fca-scaffold create-module user_management authentication
✓ Configuration backed up to fca_config_backups/fca-config_20240115_143045.yaml
✓ Module 'authentication' created in system 'user_management'
```

### Manual Recovery Process

#### 1. Identify Available Backups

```bash
$ ls -la fca_config_backups/
fca-config_20240115_143045.yaml  # Most recent
fca-config_20240115_143022.yaml
fca-config_20240115_142815.yaml
fca-config_20240115_142301.yaml
fca-config_20240115_141955.yaml  # Oldest retained
```

#### 2. Restore from Backup

```bash
# Copy desired backup to restore configuration
$ cp fca_config_backups/fca-config_20240115_143022.yaml fca-config.yaml
```

#### 3. Verify Restoration

```bash
# Validate restored configuration
$ fca-scaffold validate-config
✓ Configuration is valid
```

## Impact on Project Files

### What Happens During Backup Recovery

When you restore an FCA configuration backup, it's crucial to understand that **only the configuration metadata is restored**. The backup and recovery process has the following characteristics:

#### Configuration-Only Recovery

- **Only `fca-config.yaml` is affected**: Backup restoration only modifies the configuration file
- **All generated code remains unchanged**: Your actual project files, components, and source code are completely unaffected
- **Custom modifications are preserved**: Any manual changes you've made to generated files remain intact
- **Directory structure stays the same**: No files or folders are created, moved, or deleted during recovery

#### What Gets Restored vs. What Stays

**✅ Restored (Configuration Metadata Only)**:
- Module definitions and timestamps
- System context configurations
- Component tracking information
- Project metadata (name, description, version)
- FCA-specific settings and preferences

**🔒 Unchanged (All Project Files)**:
- Generated source code files (`.py` files)
- Custom modifications to generated code
- Additional files you've created
- Directory structure and file organization
- Git history and version control state

#### Configuration Metadata Backup and Restore

The backup system specifically handles project metadata stored in the `project` section of `fca-config.yaml`:

**Project Metadata in Backups**:
- **Project Name**: The `project.name` field as set during `fca-scaffold init`
- **Project Version**: The `project.version` field (defaults to "0.1.0")
- **Project Description**: The `project.description` field

**Important Notes About Project Metadata**:
- **Independent from `pyproject.toml`**: The project name and version in `fca-config.yaml` are completely separate from those in `pyproject.toml`
- **Source of Truth for FCA**: Commands like `fca-scaffold status` read project information exclusively from `fca-config.yaml`, not from `pyproject.toml`
- **Manual Synchronization Required**: If you update project metadata in either file, you must manually synchronize the other file if consistency is needed
- **Backup Restoration Impact**: Restoring a backup will revert project metadata to the backed-up state, potentially creating inconsistencies with `pyproject.toml`

**Post-Restore Verification for Project Metadata**:
```bash
# Check current project metadata in FCA config
$ fca-scaffold status

# Compare with pyproject.toml if consistency is required
$ grep -E "^(name|version)" pyproject.toml

# Update fca-config.yaml manually if needed
$ fca-scaffold config show
```

#### Potential Configuration-Filesystem Mismatches

After restoring a backup, you may encounter situations where the configuration doesn't match the actual filesystem:

**Common Scenarios**:
1. **Missing Components**: Configuration references components that no longer exist on disk
2. **Untracked Components**: Files exist on disk but aren't tracked in the restored configuration
3. **Timestamp Mismatches**: Configuration timestamps don't reflect actual file modification times
4. **Structural Changes**: Directory structure has evolved since the backup was created

#### Resolving Configuration-Filesystem Mismatches

When configuration and filesystem are out of sync after backup restoration, use the `sync-config` command to reconcile differences:

```bash
# Preview what sync-config will do (recommended first step)
$ fca-scaffold sync-config --dry-run
📋 Sync Preview:
  • Found 3 untracked components that will be added to config
  • Found 1 missing component that will be removed from config
  • Found 2 components with timestamp mismatches that will be updated

# Apply the synchronization
$ fca-scaffold sync-config
✓ Configuration backed up to fca_config_backups/fca-config_20240115_144512.yaml
✓ Added 3 untracked components to configuration
✓ Removed 1 missing component from configuration
✓ Updated 2 component timestamps
✓ Configuration synchronized with filesystem
```

#### Recovery Workflow Best Practices

1. **Restore Configuration**:
   ```bash
   $ cp fca_config_backups/fca-config_YYYYMMDD_HHMMSS.yaml fca-config.yaml
   ```

2. **Validate Configuration**:
   ```bash
   $ fca-scaffold validate-config
   ```

3. **Check for Mismatches**:
   ```bash
   $ fca-scaffold sync-config --dry-run
   ```

4. **Resolve Mismatches** (if needed):
   ```bash
   $ fca-scaffold sync-config
   ```

5. **Verify Final State**:
   ```bash
   $ fca-scaffold status
   ```

#### Important Considerations

- **No Data Loss**: Backup recovery never deletes or modifies your source code
- **Safe Operation**: You can safely restore any backup without fear of losing work
- **Incremental Sync**: Use `sync-config` to gradually align configuration with filesystem changes
- **Git Integration**: Consider committing configuration changes after successful recovery and sync

### Best Practices

#### 1. Regular Backup Monitoring

- Check backup directory periodically to ensure backups are being created
- Verify backup timestamps align with configuration changes
- Monitor backup directory size (should contain maximum 5 files)

#### 2. Recovery Planning

- Understand the relationship between backups and specific operations
- Test recovery procedures in development environments
- Document custom recovery procedures for your team

#### 3. Integration with Git Workflow

```bash
# Recommended workflow for configuration changes
$ git add fca-config.yaml                    # Stage current config
$ fca-scaffold create-module system module   # FCA creates backup automatically
$ git add fca-config.yaml                    # Stage updated config
$ git commit -m "Add new module configuration"
```

## Troubleshooting

### Common Issues

#### 1. Missing Backup Directory

**Symptom**: `fca_config_backups/` directory doesn't exist

**Solution**: Directory is created automatically on first backup. If missing, it will be recreated on next configuration change.

#### 2. Backup Creation Failures

**Symptom**: Error messages during backup creation

**Possible Causes**:
- Insufficient disk space
- Permission issues
- File system limitations

**Solution**:
```bash
# Check disk space
$ df -h .

# Check permissions
$ ls -la fca_config_backups/

# Manually create backup directory if needed
$ mkdir -p fca_config_backups
$ chmod 755 fca_config_backups
```

#### 3. Backup Cleanup Issues

**Symptom**: More than 5 backups in directory

**Solution**: Cleanup is automatic, but can be triggered manually:
```bash
# Remove excess backups manually
$ cd fca_config_backups
$ ls -t fca-config_*.yaml | tail -n +6 | xargs rm -f
```

### Recovery Scenarios

#### 1. Corrupted Configuration

```bash
# Restore from most recent backup
$ cp fca_config_backups/$(ls -t fca_config_backups/ | head -1) fca-config.yaml
$ fca-scaffold validate-config
```

#### 2. Accidental Module Deletion

```bash
# Find backup before deletion
$ ls -la fca_config_backups/
# Restore appropriate backup
$ cp fca_config_backups/fca-config_YYYYMMDD_HHMMSS.yaml fca-config.yaml
```

#### 3. Sync Operation Issues

```bash
# Restore pre-sync state
$ cp fca_config_backups/$(ls -t fca_config_backups/ | head -1) fca-config.yaml
# Re-run sync with dry-run first
$ fca-scaffold sync-config --dry-run
```

## Security Considerations

### File Permissions

- Backup files inherit permissions from the original `fca-config.yaml`
- Backup directory is created with standard directory permissions (755)
- No sensitive data should be stored in configuration files

### Backup Content

- Backups contain only configuration metadata, not source code
- No credentials or secrets should be present in configuration files
- Backup files are plain text YAML, easily inspectable

## Monitoring and Maintenance

### Health Checks

```bash
# Verify backup system health
$ test -d fca_config_backups && echo "Backup directory exists" || echo "No backup directory"
$ ls -1 fca_config_backups/ | wc -l  # Should be ≤ 5
```

### Maintenance Tasks

1. **Periodic Verification**: Ensure backups are being created during operations
2. **Disk Space Monitoring**: Monitor backup directory size
3. **Recovery Testing**: Periodically test backup restoration procedures

## Conclusion

FCA's backup system provides essential operational safety for configuration management, complementing Git's version control capabilities with immediate, command-level recovery options. The automatic backup creation, retention management, and seamless integration with FCA commands ensure that configuration changes can be safely made and quickly reverted when necessary.

This system enables developers to work confidently with FCA's configuration management features, knowing that recent configuration states are always preserved and easily recoverable.