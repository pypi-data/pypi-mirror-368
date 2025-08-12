"""File system access control and sandboxing for Lackey.

This module provides comprehensive access control mechanisms to ensure
safe file system operations within defined boundaries and permissions.
"""

import os
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from lackey.security import SecurityError, SecurityEvent, get_security_manager


class Permission(Enum):
    """File system permission types."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    CREATE = "create"
    LIST = "list"
    EXECUTE = "execute"


class AccessLevel(Enum):
    """Access level definitions."""

    NONE = "none"
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    FULL = "full"


@dataclass
class AccessRule:
    """Access control rule for paths and operations."""

    path_pattern: str
    allowed_permissions: Set[Permission]
    denied_permissions: Set[Permission] = field(default_factory=set)
    max_file_size_mb: Optional[float] = None
    allowed_extensions: Optional[Set[str]] = None
    denied_extensions: Optional[Set[str]] = None
    time_restrictions: Optional[Dict[str, int]] = None  # hour ranges
    description: str = ""

    def matches_path(self, path: str) -> bool:
        """Check if this rule applies to the given path."""
        # Simple pattern matching - could be enhanced with regex
        if self.path_pattern == "*":
            return True

        # Exact match
        if self.path_pattern == path:
            return True

        # Prefix match with wildcard
        if self.path_pattern.endswith("*"):
            prefix = self.path_pattern[:-1]
            return path.startswith(prefix)

        # Directory match
        if self.path_pattern.endswith("/"):
            return path.startswith(self.path_pattern)

        return False

    def is_permission_allowed(self, permission: Permission) -> bool:
        """Check if a permission is allowed by this rule."""
        if permission in self.denied_permissions:
            return False
        return permission in self.allowed_permissions

    def validate_file_constraints(self, file_path: str) -> None:
        """Validate file against rule constraints."""
        path_obj = Path(file_path)

        # Check file extension
        if path_obj.suffix:
            ext = path_obj.suffix.lower()

            if self.denied_extensions and ext in self.denied_extensions:
                raise SecurityError(f"File extension '{ext}' is denied by access rule")

            if self.allowed_extensions and ext not in self.allowed_extensions:
                raise SecurityError(
                    f"File extension '{ext}' is not allowed by access rule"
                )

        # Check file size if file exists
        if os.path.exists(file_path) and self.max_file_size_mb:
            file_size = os.path.getsize(file_path)
            max_size_bytes = self.max_file_size_mb * 1024 * 1024

            if file_size > max_size_bytes:
                raise SecurityError(
                    f"File size ({file_size} bytes) exceeds rule limit "
                    f"({max_size_bytes} bytes)"
                )

        # Check time restrictions
        if self.time_restrictions:
            current_hour = time.localtime().tm_hour
            start_hour = self.time_restrictions.get("start_hour", 0)
            end_hour = self.time_restrictions.get("end_hour", 23)

            if not (start_hour <= current_hour <= end_hour):
                raise SecurityError(
                    f"Access denied due to time restrictions "
                    f"(allowed: {start_hour}:00-{end_hour}:00)"
                )


@dataclass
class SandboxConfig:
    """Configuration for file system sandbox."""

    # Base directories that are allowed
    allowed_base_paths: List[str] = field(default_factory=list)

    # Temporary directory for sandbox operations
    temp_directory: Optional[str] = None

    # Maximum total disk usage in MB
    max_total_size_mb: float = 100.0

    # Maximum number of files
    max_file_count: int = 1000

    # Maximum directory depth
    max_directory_depth: int = 10

    # Default access level for new paths
    default_access_level: AccessLevel = AccessLevel.READ_WRITE

    # Whether to log all access attempts
    log_all_access: bool = True

    # Whether to create missing directories automatically
    auto_create_directories: bool = True


class FileSystemSandbox:
    """File system sandbox with comprehensive access control."""

    def __init__(self, config: SandboxConfig):
        """Initialize file system sandbox."""
        self.config = config
        self.access_rules: List[AccessRule] = []
        self.security_manager = get_security_manager()

        # Initialize allowed base paths
        self.allowed_base_paths = set()
        for base_path in config.allowed_base_paths:
            abs_path = os.path.abspath(base_path)
            self.allowed_base_paths.add(abs_path)

            # Create directory if it doesn't exist and auto-creation is enabled
            if config.auto_create_directories:
                os.makedirs(abs_path, exist_ok=True)

        # Set up temporary directory
        self.temp_directory: Optional[str]
        if config.temp_directory:
            self.temp_directory = os.path.abspath(config.temp_directory)
            if config.auto_create_directories:
                os.makedirs(self.temp_directory, exist_ok=True)
        else:
            self.temp_directory = None

        # Initialize default access rules
        self._setup_default_rules()

    def _setup_default_rules(self) -> None:
        """Set up default access control rules."""
        # Allow full access to base paths
        for base_path in self.allowed_base_paths:
            self.add_access_rule(
                AccessRule(
                    path_pattern=f"{base_path}/*",
                    allowed_permissions={
                        Permission.READ,
                        Permission.WRITE,
                        Permission.CREATE,
                        Permission.DELETE,
                        Permission.LIST,
                    },
                    description=f"Full access to base path: {base_path}",
                )
            )

        # Deny access to system directories
        system_paths = [
            "/etc/*",
            "/sys/*",
            "/proc/*",
            "/dev/*",
            "C:\\Windows\\*",
            "C:\\System32\\*",
            "C:\\Program Files\\*",
        ]

        for sys_path in system_paths:
            self.add_access_rule(
                AccessRule(
                    path_pattern=sys_path,
                    allowed_permissions=set(),
                    denied_permissions={
                        Permission.READ,
                        Permission.WRITE,
                        Permission.CREATE,
                        Permission.DELETE,
                        Permission.LIST,
                    },
                    description=f"Deny access to system path: {sys_path}",
                )
            )

    def add_access_rule(self, rule: AccessRule) -> None:
        """Add an access control rule."""
        self.access_rules.append(rule)

        # Log rule addition
        self.security_manager.log_security_event(
            SecurityEvent(
                event_type="access_rule_added",
                severity="low",
                message=f"Access rule added: {rule.description}",
                metadata={
                    "path_pattern": rule.path_pattern,
                    "allowed_permissions": [p.value for p in rule.allowed_permissions],
                    "denied_permissions": [p.value for p in rule.denied_permissions],
                },
            )
        )

    def remove_access_rule(self, path_pattern: str) -> bool:
        """Remove access control rules matching the path pattern."""
        removed_count = 0
        self.access_rules = [
            rule
            for rule in self.access_rules
            if not (
                rule.path_pattern == path_pattern
                and (removed_count := removed_count + 1)
            )
        ]

        if removed_count > 0:
            self.security_manager.log_security_event(
                SecurityEvent(
                    event_type="access_rule_removed",
                    severity="low",
                    message=f"Access rule removed: {path_pattern}",
                    metadata={"path_pattern": path_pattern, "count": removed_count},
                )
            )

        return removed_count > 0

    def check_access(self, file_path: str, permission: Permission) -> bool:
        """Check if access is allowed for the given path and permission."""
        abs_path = os.path.abspath(file_path)

        # Check if path is within allowed base paths
        if not self._is_path_in_sandbox(abs_path):
            self._log_access_violation(abs_path, permission, "Path outside sandbox")
            return False

        # Apply access rules
        applicable_rules = [
            rule for rule in self.access_rules if rule.matches_path(abs_path)
        ]

        if not applicable_rules:
            # No specific rules, use default access level
            return self._check_default_access(permission)

        # Check each applicable rule
        for rule in applicable_rules:
            try:
                # Validate file constraints
                rule.validate_file_constraints(abs_path)

                # Check permission
                if not rule.is_permission_allowed(permission):
                    self._log_access_violation(
                        abs_path, permission, f"Denied by rule: {rule.description}"
                    )
                    return False

            except SecurityError as e:
                self._log_access_violation(abs_path, permission, str(e))
                return False

        # Log successful access if configured
        if self.config.log_all_access:
            self.security_manager.log_security_event(
                SecurityEvent(
                    event_type="file_access_granted",
                    severity="low",
                    message=f"File access granted: {permission.value}",
                    metadata={
                        "path": abs_path,
                        "permission": permission.value,
                        "rules_applied": len(applicable_rules),
                    },
                )
            )

        return True

    def _is_path_in_sandbox(self, abs_path: str) -> bool:
        """Check if path is within the sandbox boundaries."""
        for base_path in self.allowed_base_paths:
            if abs_path.startswith(base_path):
                return True

        # Check temporary directory if configured
        if self.temp_directory and abs_path.startswith(self.temp_directory):
            return True

        return False

    def _check_default_access(self, permission: Permission) -> bool:
        """Check access based on default access level."""
        if self.config.default_access_level == AccessLevel.NONE:
            return False
        elif self.config.default_access_level == AccessLevel.READ_ONLY:
            return permission in {Permission.READ, Permission.LIST}
        elif self.config.default_access_level == AccessLevel.READ_WRITE:
            return permission in {
                Permission.READ,
                Permission.WRITE,
                Permission.LIST,
                Permission.CREATE,
            }
        elif self.config.default_access_level == AccessLevel.FULL:
            return True

    def _log_access_violation(
        self, path: str, permission: Permission, reason: str
    ) -> None:
        """Log an access violation."""
        self.security_manager.log_security_event(
            SecurityEvent(
                event_type="file_access_denied",
                severity="medium",
                message=f"File access denied: {reason}",
                metadata={
                    "path": path,
                    "permission": permission.value,
                    "reason": reason,
                },
            )
        )

    def validate_sandbox_limits(self) -> None:
        """Validate that sandbox limits are not exceeded."""
        total_size = 0
        file_count = 0

        for base_path in self.allowed_base_paths:
            if os.path.exists(base_path):
                for root, dirs, files in os.walk(base_path):
                    # Check directory depth
                    depth = len(Path(root).relative_to(base_path).parts)
                    if depth > self.config.max_directory_depth:
                        raise SecurityError(
                            f"Directory depth ({depth}) exceeds maximum "
                            f"({self.config.max_directory_depth})"
                        )

                    # Count files and calculate size
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.isfile(file_path):
                            file_count += 1
                            total_size += os.path.getsize(file_path)

        # Check limits
        if file_count > self.config.max_file_count:
            raise SecurityError(
                f"File count ({file_count}) exceeds maximum "
                f"({self.config.max_file_count})"
            )

        total_size_mb = total_size / (1024 * 1024)
        if total_size_mb > self.config.max_total_size_mb:
            raise SecurityError(
                f"Total size ({total_size_mb:.2f} MB) exceeds maximum "
                f"({self.config.max_total_size_mb} MB)"
            )

    def get_sandbox_stats(self) -> Dict[str, Union[int, float]]:
        """Get current sandbox usage statistics."""
        total_size = 0
        file_count = 0
        dir_count = 0
        max_depth = 0

        for base_path in self.allowed_base_paths:
            if os.path.exists(base_path):
                for root, dirs, files in os.walk(base_path):
                    dir_count += len(dirs)

                    # Calculate depth
                    try:
                        depth = len(Path(root).relative_to(base_path).parts)
                        max_depth = max(max_depth, depth)
                    except ValueError:
                        # Handle case where root is not relative to base_path
                        pass

                    # Count files and calculate size
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.isfile(file_path):
                            file_count += 1
                            total_size += os.path.getsize(file_path)

        total_size_mb = total_size / (1024 * 1024)

        return {
            "total_size_mb": round(total_size_mb, 2),
            "file_count": file_count,
            "directory_count": dir_count,
            "max_depth": max_depth,
            "size_limit_mb": self.config.max_total_size_mb,
            "file_limit": self.config.max_file_count,
            "depth_limit": self.config.max_directory_depth,
            "size_usage_percent": round(
                (total_size_mb / self.config.max_total_size_mb) * 100, 2
            ),
            "file_usage_percent": round(
                (file_count / self.config.max_file_count) * 100, 2
            ),
        }

    def create_secure_temp_file(
        self, prefix: str = "lackey_", suffix: str = ".tmp"
    ) -> str:
        """Create a secure temporary file within the sandbox."""
        if not self.temp_directory:
            raise SecurityError("Temporary directory not configured")

        # Validate prefix and suffix
        safe_prefix = "".join(c for c in prefix if c.isalnum() or c in "_-")
        safe_suffix = "".join(c for c in suffix if c.isalnum() or c in "._-")

        # Generate unique filename
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        filename = f"{safe_prefix}{unique_id}{safe_suffix}"

        temp_path = os.path.join(self.temp_directory, filename)

        # Check access
        if not self.check_access(temp_path, Permission.CREATE):
            raise SecurityError("Cannot create temporary file: access denied")

        return temp_path

    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """Clean up old temporary files."""
        if not self.temp_directory or not os.path.exists(self.temp_directory):
            return 0

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        cleaned_count = 0

        for filename in os.listdir(self.temp_directory):
            file_path = os.path.join(self.temp_directory, filename)

            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)

                if file_age > max_age_seconds:
                    try:
                        if self.check_access(file_path, Permission.DELETE):
                            os.remove(file_path)
                            cleaned_count += 1
                    except OSError:
                        pass  # Ignore cleanup failures

        if cleaned_count > 0:
            self.security_manager.log_security_event(
                SecurityEvent(
                    event_type="temp_files_cleaned",
                    severity="low",
                    message=f"Cleaned up {cleaned_count} temporary files",
                    metadata={
                        "count": cleaned_count,
                        "max_age_hours": max_age_hours,
                    },
                )
            )

        return cleaned_count


# Global sandbox instance
_file_system_sandbox: Optional[FileSystemSandbox] = None


def get_file_system_sandbox(
    config: Optional[SandboxConfig] = None,
) -> FileSystemSandbox:
    """Get or create global file system sandbox instance."""
    global _file_system_sandbox
    if _file_system_sandbox is None or config:
        if not config:
            # Default configuration
            config = SandboxConfig(
                allowed_base_paths=[".lackey"], temp_directory=".lackey/temp"
            )
        _file_system_sandbox = FileSystemSandbox(config)
    return _file_system_sandbox


def initialize_sandbox(config: SandboxConfig) -> FileSystemSandbox:
    """Initialize global file system sandbox with configuration."""
    global _file_system_sandbox
    _file_system_sandbox = FileSystemSandbox(config)
    return _file_system_sandbox
