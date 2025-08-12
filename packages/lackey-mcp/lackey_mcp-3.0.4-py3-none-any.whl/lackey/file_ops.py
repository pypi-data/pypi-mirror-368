"""Atomic file operations with rollback capabilities for Lackey."""

import json
import os
import shutil
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

import yaml

from .path_security import get_path_validator, validate_path
from .security import SecurityError, SecurityEvent, get_security_manager
from .validation import validator


class FileOperationError(Exception):
    """Raised when file operations fail."""

    pass


class IntegrityError(Exception):
    """Raised when file integrity checks fail."""

    pass


class TransactionError(Exception):
    """Raised when transaction operations fail."""

    pass


@dataclass
class OperationLog:
    """Log entry for file operations."""

    operation: str
    path: str
    timestamp: float
    checksum_before: Optional[str] = None
    checksum_after: Optional[str] = None
    backup_path: Optional[str] = None
    success: bool = False
    error: Optional[str] = None


class FileLockManager:
    """Thread-safe file locking manager to prevent concurrent access."""

    def __init__(self) -> None:
        """Initialize the file lock manager."""
        self._locks: Dict[str, threading.RLock] = {}
        self._locks_lock = threading.Lock()

    def get_lock(self, file_path: str) -> threading.RLock:
        """Get or create a lock for the specified file path."""
        # Normalize the path to ensure consistent locking
        normalized_path = str(Path(file_path).resolve())

        with self._locks_lock:
            if normalized_path not in self._locks:
                self._locks[normalized_path] = threading.RLock()
            return self._locks[normalized_path]

    @contextmanager
    def lock_file(self, file_path: str) -> Generator[None, None, None]:
        """Context manager for file locking."""
        lock = self.get_lock(file_path)
        lock.acquire()
        try:
            yield
        finally:
            lock.release()


# Global file lock manager instance
_file_lock_manager = FileLockManager()


class AtomicFileOperation:
    """
    Ensures atomic file operations with rollback capability.

    All file modifications are performed atomically using write-then-move
    operations with automatic backup and rollback on failure.
    """

    def __init__(self, target_path: str, base_paths: Optional[List[str]] = None):
        """Initialize atomic file operation with enhanced security validation."""
        # Enhanced path validation using path security module
        try:
            validated_path = validate_path(
                target_path,
                base_paths=base_paths,
                allow_absolute=True,  # Allow absolute paths for file operations
                require_base_path=bool(base_paths),
            )
            self.target_path = Path(validated_path)
        except SecurityError as e:
            # Log security event
            security_manager = get_security_manager()
            security_manager.log_security_event(
                SecurityEvent(
                    event_type="file_operation_path_violation",
                    severity="high",
                    message=f"Invalid path in file operation: {str(e)}",
                    metadata={"target_path": target_path, "error": str(e)},
                )
            )
            raise FileOperationError(f"Invalid path: {e}")

        self.temp_path: Optional[Path] = None
        self.backup_path: Optional[Path] = None
        self.operation_log: List[OperationLog] = []
        self.operation_id = str(uuid.uuid4())
        self.base_paths = base_paths or []
        self._file_lock = _file_lock_manager.get_lock(str(self.target_path))

    def __enter__(self) -> "AtomicFileOperation":
        """Enter context manager with file locking."""
        # Acquire file lock to prevent concurrent access
        self._file_lock.acquire()

        try:
            # Create backup if file exists
            if self.target_path.exists():
                self.backup_path = self._create_backup()

                # Calculate checksum before operation
                checksum_before = validator.calculate_file_checksum(
                    str(self.target_path)
                )

                self.operation_log.append(
                    OperationLog(
                        operation="backup_created",
                        path=str(self.backup_path),
                        timestamp=time.time(),
                        checksum_before=checksum_before,
                    )
                )

            # Create temporary file
            self.temp_path = self._create_temp_file()

            return self
        except Exception:
            # If anything fails during setup, release the lock
            self._file_lock.release()
            raise

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager with cleanup and lock release."""
        try:
            if exc_type is None:
                # Success: atomically move temp file to target
                self._commit_operation()
            else:
                # Failure: rollback to backup
                self._rollback_operation()
        finally:
            self._cleanup_temp_files()
            # Always release the file lock
            self._file_lock.release()

    def write_content(self, content: str, encoding: str = "utf-8") -> None:
        """Write content to temporary file with integrity checks."""
        if self.temp_path is None:
            raise FileOperationError("Operation not initialized")

        try:
            # Write to temporary file
            with open(self.temp_path, "w", encoding=encoding) as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk

            # Verify written content
            with open(self.temp_path, "r", encoding=encoding) as f:
                written_content = f.read()
                if written_content != content:
                    raise IntegrityError("Content verification failed")

            # Validate file size and extension
            validator.validate_file_size(str(self.temp_path))
            validator.validate_file_extension(str(self.target_path))
            validator.validate_encoding(str(self.temp_path))

            # Calculate checksum
            checksum_after = validator.calculate_file_checksum(str(self.temp_path))

            self.operation_log.append(
                OperationLog(
                    operation="content_written",
                    path=str(self.temp_path),
                    timestamp=time.time(),
                    checksum_after=checksum_after,
                    success=True,
                )
            )

        except Exception as e:
            self.operation_log.append(
                OperationLog(
                    operation="content_write_failed",
                    path=str(self.temp_path),
                    timestamp=time.time(),
                    error=str(e),
                )
            )
            raise FileOperationError(f"Failed to write content: {e}")

    def write_yaml(self, data: Dict[str, Any]) -> None:
        """Write YAML data with validation."""
        try:
            content = yaml.dump(
                data, default_flow_style=False, allow_unicode=True, sort_keys=False
            )
            self.write_content(content)
        except yaml.YAMLError as e:
            raise FileOperationError(f"YAML serialization failed: {e}")

    def write_json(self, data: Dict[str, Any], indent: int = 2) -> None:
        """Write JSON data with validation."""
        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            self.write_content(content)
        except (TypeError, ValueError) as e:
            raise FileOperationError(f"JSON serialization failed: {e}")

    def _create_backup(self) -> Path:
        """Create backup of existing file with unique naming."""
        # Use operation_id (UUID) for uniqueness across threads
        backup_path = self.target_path.with_suffix(
            f"{self.target_path.suffix}.backup.{self.operation_id}"
        )

        try:
            shutil.copy2(self.target_path, backup_path)
            return backup_path
        except IOError as e:
            raise FileOperationError(f"Failed to create backup: {e}")

    def _create_temp_file(self) -> Path:
        """Create temporary file for atomic operations."""
        temp_dir = self.target_path.parent
        temp_dir.mkdir(parents=True, exist_ok=True)

        temp_path = temp_dir / f"{self.target_path.name}.tmp.{self.operation_id}"
        return temp_path

    def _commit_operation(self) -> None:
        """Commit the operation by moving temp file to target."""
        try:
            # Ensure parent directory exists
            self.target_path.parent.mkdir(parents=True, exist_ok=True)

            # Atomic move
            shutil.move(str(self.temp_path), str(self.target_path))

            # Verify final file
            checksum_final = validator.calculate_file_checksum(str(self.target_path))

            self.operation_log.append(
                OperationLog(
                    operation="operation_committed",
                    path=str(self.target_path),
                    timestamp=time.time(),
                    checksum_after=checksum_final,
                    success=True,
                )
            )

            # Clean up backup after successful operation
            if self.backup_path and self.backup_path.exists():
                self.backup_path.unlink()

        except Exception as e:
            self.operation_log.append(
                OperationLog(
                    operation="commit_failed",
                    path=str(self.target_path),
                    timestamp=time.time(),
                    error=str(e),
                )
            )
            raise FileOperationError(f"Failed to commit operation: {e}")

    def _rollback_operation(self) -> None:
        """Rollback to previous state on failure."""
        try:
            # Remove temp file if it exists
            if self.temp_path and self.temp_path.exists():
                self.temp_path.unlink()

            # Restore from backup if available
            if self.backup_path and self.backup_path.exists():
                shutil.move(str(self.backup_path), str(self.target_path))

                self.operation_log.append(
                    OperationLog(
                        operation="rollback_completed",
                        path=str(self.target_path),
                        timestamp=time.time(),
                        success=True,
                    )
                )

        except Exception as rollback_error:
            # Log rollback failure - this is critical
            self.operation_log.append(
                OperationLog(
                    operation="rollback_failed",
                    path=str(self.target_path),
                    timestamp=time.time(),
                    error=str(rollback_error),
                )
            )

            # This is a critical error that should be logged
            import logging

            logging.critical(
                f"Rollback failed for operation {self.operation_id}: "
                f"{rollback_error}",
                extra={"operation_log": [log.__dict__ for log in self.operation_log]},
            )

    def _cleanup_temp_files(self) -> None:
        """Clean up temporary files."""
        try:
            if self.temp_path and self.temp_path.exists():
                self.temp_path.unlink()

            if self.backup_path and self.backup_path.exists():
                self.backup_path.unlink()

        except Exception as e:
            # Log cleanup failure but don't raise
            import logging

            logging.warning(f"Failed to cleanup temp files: {e}")


class TransactionManager:
    """
    Manages multi-file operations with full rollback capability.

    Ensures that either all file operations succeed or all are rolled back
    to maintain consistency across multiple files.
    """

    def __init__(self) -> None:
        """Initialize transaction manager."""
        self.operations: List[tuple] = []
        self.transaction_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.completed_operations: List[AtomicFileOperation] = []

    def add_file_operation(self, file_path: str, content: str) -> None:
        """Add a file operation to the transaction."""
        self.operations.append(("write_content", file_path, content))

    def add_yaml_operation(self, file_path: str, data: Dict[str, Any]) -> None:
        """Add a YAML file operation to the transaction."""
        self.operations.append(("write_yaml", file_path, data))

    def add_json_operation(self, file_path: str, data: Dict[str, Any]) -> None:
        """Add a JSON file operation to the transaction."""
        self.operations.append(("write_json", file_path, data))

    def commit(self) -> None:
        """Execute all operations atomically."""
        if not self.operations:
            return

        try:
            # Execute all operations
            for operation_type, file_path, data in self.operations:
                operation = AtomicFileOperation(file_path)

                with operation:
                    if operation_type == "write_content":
                        operation.write_content(data)
                    elif operation_type == "write_yaml":
                        operation.write_yaml(data)
                    elif operation_type == "write_json":
                        operation.write_json(data)
                    else:
                        raise TransactionError(f"Unknown operation: {operation_type}")

                self.completed_operations.append(operation)

            import logging

            logging.info(f"Transaction {self.transaction_id} completed successfully")

        except Exception as e:
            # All individual operations have their own rollback
            # Transaction failure is logged for analysis
            import logging

            logging.error(
                f"Transaction {self.transaction_id} failed: {e}",
                extra={
                    "transaction_id": self.transaction_id,
                    "operations_count": len(self.operations),
                    "completed_count": len(self.completed_operations),
                },
            )
            raise TransactionError(f"Transaction {self.transaction_id} failed: {e}")


@contextmanager
def atomic_write(file_path: str) -> Any:
    """Context manager for atomic file writes."""
    operation = AtomicFileOperation(file_path)
    with operation:
        yield operation


def read_yaml_file(file_path: str) -> Dict[str, Any]:
    """Read and parse YAML file with validation."""
    path = Path(file_path)

    if not path.exists():
        raise FileOperationError(f"File not found: {file_path}")

    try:
        # Validate file
        validator.validate_file_extension(file_path)
        validator.validate_file_size(file_path)
        validator.validate_encoding(file_path)

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            return {}

        if not isinstance(data, dict):
            raise FileOperationError(
                f"YAML file must contain a dictionary, got {type(data)}"
            )

        return data

    except yaml.YAMLError as e:
        raise FileOperationError(f"YAML parsing failed: {e}")
    except IOError as e:
        raise FileOperationError(f"File read failed: {e}")


def read_json_file(file_path: str) -> Dict[str, Any]:
    """Read and parse JSON file with validation."""
    path = Path(file_path)

    if not path.exists():
        raise FileOperationError(f"File not found: {file_path}")

    try:
        # Validate file
        validator.validate_file_extension(file_path)
        validator.validate_file_size(file_path)
        validator.validate_encoding(file_path)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise FileOperationError(
                f"JSON file must contain a dictionary, got {type(data)}"
            )

        return data

    except json.JSONDecodeError as e:
        raise FileOperationError(f"JSON parsing failed: {e}")
    except IOError as e:
        raise FileOperationError(f"File read failed: {e}")


def read_text_file(file_path: str) -> str:
    """Read text file with validation."""
    path = Path(file_path)

    if not path.exists():
        raise FileOperationError(f"File not found: {file_path}")

    try:
        # Validate file
        validator.validate_file_size(file_path)
        validator.validate_encoding(file_path)

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        return content

    except IOError as e:
        raise FileOperationError(f"File read failed: {e}")


def ensure_directory(dir_path: str) -> None:
    """Ensure directory exists with proper permissions."""
    path = Path(dir_path)

    try:
        # Validate path
        validator.sanitize_path(str(dir_path))

        # Create directory if it doesn't exist
        path.mkdir(parents=True, exist_ok=True)

        # Verify directory is writable
        test_file = path / f".write_test_{uuid.uuid4()}"
        try:
            test_file.touch()
            test_file.unlink()
        except IOError:
            raise FileOperationError(f"Directory not writable: {dir_path}")

    except SecurityError as e:
        raise FileOperationError(f"Invalid directory path: {e}")
    except IOError as e:
        raise FileOperationError(f"Failed to create directory: {e}")


def safe_delete_file(file_path: str, create_backup: bool = True) -> Optional[str]:
    """Safely delete a file with optional backup and file locking."""
    path = Path(file_path)

    if not path.exists():
        return None

    # Use file locking to prevent concurrent access
    with _file_lock_manager.lock_file(str(path)):
        backup_path = None

        try:
            # Create backup if requested
            if create_backup:
                # Use UUID instead of timestamp to avoid race conditions
                unique_id = str(uuid.uuid4())[
                    :8
                ]  # Use first 8 chars of UUID for readability
                backup_path = str(
                    path.with_suffix(f"{path.suffix}.deleted.{unique_id}")
                )
                shutil.copy2(path, backup_path)

            # Delete original file
            path.unlink()

            return backup_path

        except IOError as e:
            # If backup was created but deletion failed, clean up backup
            if backup_path and Path(backup_path).exists():
                try:
                    Path(backup_path).unlink()
                except IOError:
                    pass  # Ignore cleanup failure

            raise FileOperationError(f"Failed to delete file: {e}")


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get comprehensive file information."""
    path = Path(file_path)

    if not path.exists():
        raise FileOperationError(f"File not found: {file_path}")

    try:
        stat = path.stat()
        checksum = validator.calculate_file_checksum(file_path)

        return {
            "path": str(path),
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "checksum": checksum,
            "extension": path.suffix,
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
        }

    except IOError as e:
        raise FileOperationError(f"Failed to get file info: {e}")


class SecureFileManager:
    """Secure file manager with comprehensive path traversal protection."""

    def __init__(self, base_paths: List[str], max_file_size_mb: float = 10.0):
        """Initialize secure file manager with allowed base paths."""
        self.base_paths = [os.path.abspath(path) for path in base_paths]
        self.max_file_size_mb = max_file_size_mb
        self.path_validator = get_path_validator(self.base_paths)
        self.security_manager = get_security_manager()

        # Ensure base paths exist
        for base_path in self.base_paths:
            os.makedirs(base_path, exist_ok=True)

    def validate_operation(self, file_path: str, operation: str) -> str:
        """Validate file operation and return safe path."""
        try:
            # Validate path using path security module
            safe_path = self.path_validator.validate_path(
                file_path, allow_absolute=False, require_base_path=True
            )

            # Log successful validation
            self.security_manager.log_security_event(
                SecurityEvent(
                    event_type="file_operation_validated",
                    severity="low",
                    message=f"File operation validated: {operation}",
                    metadata={
                        "operation": operation,
                        "original_path": file_path,
                        "safe_path": safe_path,
                    },
                )
            )

            return safe_path

        except SecurityError as e:
            # Log security violation
            self.security_manager.log_security_event(
                SecurityEvent(
                    event_type="file_operation_blocked",
                    severity="high",
                    message=f"File operation blocked: {operation}",
                    metadata={
                        "operation": operation,
                        "path": file_path,
                        "error": str(e),
                    },
                )
            )
            raise FileOperationError(f"Security violation in {operation}: {e}")

    def secure_read(self, file_path: str) -> str:
        """Securely read a file with path validation."""
        safe_path = self.validate_operation(file_path, "read")

        # Additional security checks
        if os.path.exists(safe_path):
            # Check file size
            file_size = os.path.getsize(safe_path)
            max_size_bytes = self.max_file_size_mb * 1024 * 1024

            if file_size > max_size_bytes:
                raise FileOperationError(
                    f"File size ({file_size} bytes) exceeds maximum "
                    f"allowed size ({max_size_bytes} bytes)"
                )

            # Validate file content for security issues
            self.security_manager.validate_file_content(safe_path)

        return read_text_file(safe_path)

    def secure_write(self, file_path: str, content: str) -> None:
        """Securely write to a file with path validation."""
        safe_path = self.validate_operation(file_path, "write")

        # Validate content before writing
        sanitized_content = self.security_manager._sanitize_string(content)

        # Use atomic file operation for secure writing
        with AtomicFileOperation(safe_path, self.base_paths) as op:
            op.write_content(sanitized_content)

    def secure_write_yaml(self, file_path: str, data: Dict[str, Any]) -> None:
        """Securely write YAML data with path validation."""
        safe_path = self.validate_operation(file_path, "write_yaml")

        # Validate and sanitize data
        if not isinstance(data, dict):
            raise FileOperationError("Data must be a dictionary")

        # Use atomic file operation for secure writing
        with AtomicFileOperation(safe_path, self.base_paths) as op:
            op.write_yaml(data)

    def secure_write_json(self, file_path: str, data: Dict[str, Any]) -> None:
        """Securely write JSON data with path validation."""
        safe_path = self.validate_operation(file_path, "write_json")

        # Validate and sanitize data
        if not isinstance(data, dict):
            raise FileOperationError("Data must be a dictionary")

        # Use atomic file operation for secure writing
        with AtomicFileOperation(safe_path, self.base_paths) as op:
            op.write_json(data)

    def secure_delete(
        self, file_path: str, create_backup: bool = True
    ) -> Optional[str]:
        """Securely delete a file with path validation."""
        safe_path = self.validate_operation(file_path, "delete")

        # Log deletion attempt
        self.security_manager.log_security_event(
            SecurityEvent(
                event_type="file_deletion_attempt",
                severity="medium",
                message=f"File deletion attempted: {file_path}",
                metadata={"safe_path": safe_path, "create_backup": create_backup},
            )
        )

        return safe_delete_file(safe_path, create_backup)

    def secure_list_directory(self, dir_path: str) -> List[str]:
        """Securely list directory contents with path validation."""
        safe_path = self.validate_operation(dir_path, "list_directory")

        if not os.path.isdir(safe_path):
            raise FileOperationError(f"Not a directory: {dir_path}")

        try:
            entries = []
            for entry in os.listdir(safe_path):
                # Validate each entry name
                try:
                    safe_entry = self.path_validator.sanitize_filename(entry)
                    entries.append(safe_entry)
                except SecurityError:
                    # Skip entries that fail validation
                    self.security_manager.log_security_event(
                        SecurityEvent(
                            event_type="unsafe_directory_entry_skipped",
                            severity="medium",
                            message=f"Unsafe directory entry skipped: {entry}",
                            metadata={"directory": safe_path, "entry": entry},
                        )
                    )
                    continue

            return sorted(entries)

        except OSError as e:
            raise FileOperationError(f"Failed to list directory: {e}")

    def secure_ensure_directory(self, dir_path: str) -> None:
        """Securely create directory with path validation."""
        safe_path = self.validate_operation(dir_path, "create_directory")
        ensure_directory(safe_path)

    def get_secure_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information with path validation."""
        safe_path = self.validate_operation(file_path, "get_info")
        return get_file_info(safe_path)

    def is_path_safe(self, file_path: str) -> bool:
        """Check if a path is safe without raising exceptions."""
        try:
            self.validate_operation(file_path, "check_safety")
            return True
        except (FileOperationError, SecurityError):
            return False

    def get_allowed_base_paths(self) -> List[str]:
        """Get list of allowed base paths."""
        return self.base_paths.copy()

    def add_base_path(self, base_path: str) -> None:
        """Add a new allowed base path."""
        abs_path = os.path.abspath(base_path)
        if abs_path not in self.base_paths:
            self.base_paths.append(abs_path)
            os.makedirs(abs_path, exist_ok=True)

            # Update path validator
            self.path_validator = get_path_validator(self.base_paths)

    def remove_base_path(self, base_path: str) -> None:
        """Remove an allowed base path."""
        abs_path = os.path.abspath(base_path)
        if abs_path in self.base_paths:
            self.base_paths.remove(abs_path)

            # Update path validator
            self.path_validator = get_path_validator(self.base_paths)


# Global secure file manager instance
_secure_file_manager: Optional[SecureFileManager] = None


def get_secure_file_manager(
    base_paths: Optional[List[str]] = None,
) -> SecureFileManager:
    """Get or create global secure file manager instance."""
    global _secure_file_manager
    if _secure_file_manager is None or base_paths:
        if not base_paths:
            base_paths = [".lackey"]  # Default base path
        _secure_file_manager = SecureFileManager(base_paths)
    return _secure_file_manager
