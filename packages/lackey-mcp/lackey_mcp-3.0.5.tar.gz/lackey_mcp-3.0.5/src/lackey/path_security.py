"""Path security module for comprehensive path traversal protection.

This module provides advanced path validation and sanitization to prevent
path traversal attacks and ensure safe file system operations.
"""

import os
import re
from pathlib import Path, PurePath
from typing import Any, Dict, List, Optional
from urllib.parse import unquote

from .security import SecurityError, SecurityEvent, get_security_manager


class PathValidator:
    """Advanced path validation and sanitization."""

    # Dangerous path patterns that should be blocked
    DANGEROUS_PATTERNS = [
        r"\.\.\/",  # Parent directory traversal
        r"\.\.\.",  # Multiple dots
        r"\.\.\\\\",  # Windows path traversal
        r"\/\.\.",  # Unix path traversal
        r"\\\\\.\.",  # Windows path traversal
        r"~\/",  # Home directory access
        r"\$\{.*\}",  # Variable expansion
        r"%[0-9a-fA-F]{2}",  # URL encoding
        r"\\\\x[0-9a-fA-F]{2}",  # Hex encoding
        r"\\\\[0-7]{3}",  # Octal encoding
        r"\\\\u[0-9a-fA-F]{4}",  # Unicode encoding
        r"\\\\U[0-9a-fA-F]{8}",  # Extended unicode
    ]

    # Dangerous file names that should be blocked
    DANGEROUS_NAMES = {
        # Windows reserved names
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
        # Unix/Linux special files
        "/dev/null",
        "/dev/zero",
        "/dev/random",
        "/dev/urandom",
        "/proc/self/environ",
        "/proc/version",
        "/proc/cmdline",
        # Common sensitive files
        "/etc/passwd",
        "/etc/shadow",
        "/etc/hosts",
        "/etc/fstab",
        "id_rsa",
        "id_dsa",
        "id_ecdsa",
        "id_ed25519",
        ".ssh/config",
        ".ssh/known_hosts",
        ".env",
        ".env.local",
        ".env.production",
        "config.json",
        "secrets.json",
        "credentials.json",
    }

    # Characters that should not appear in file paths
    FORBIDDEN_CHARS = {
        "\x00",  # Null byte
        "\x01",
        "\x02",
        "\x03",
        "\x04",
        "\x05",
        "\x06",
        "\x07",  # Control chars
        "\x08",
        "\x09",
        "\x0b",
        "\x0c",
        "\x0e",
        "\x0f",
        "\x10",
        "\x11",
        "\x12",
        "\x13",
        "\x14",
        "\x15",
        "\x16",
        "\x17",
        "\x18",
        "\x19",
        "\x1a",
        "\x1b",
        "\x1c",
        "\x1d",
        "\x1e",
        "\x1f",
        "\x7f",  # DEL character
        "<",
        ">",
        "|",
        '"',
        "*",
        "?",  # Windows forbidden chars
    }

    def __init__(self, base_paths: Optional[List[str]] = None):
        """Initialize path validator with allowed base paths."""
        self.base_paths = []
        if base_paths:
            for base_path in base_paths:
                self.base_paths.append(os.path.abspath(base_path))

    def validate_path(
        self,
        path: str,
        allow_absolute: bool = False,
        require_base_path: bool = True,
    ) -> str:
        """Validate and sanitize a file path.

        Args:
            path: The path to validate
            allow_absolute: Whether to allow absolute paths
            require_base_path: Whether path must be within a base path

        Returns:
            Sanitized and validated path

        Raises:
            SecurityError: If path is invalid or dangerous
        """
        if not path:
            raise SecurityError("Empty path provided")

        # Decode URL encoding if present
        original_path = path
        try:
            path = unquote(path)
        except Exception:  # nosec B110
            pass  # If decoding fails, use original

        # Check for dangerous patterns
        self._check_dangerous_patterns(path, original_path)

        # Check for forbidden characters
        self._check_forbidden_characters(path)

        # Normalize the path
        normalized_path = self._normalize_path(path)

        # Check for dangerous file names
        self._check_dangerous_names(normalized_path)

        # Validate path structure
        self._validate_path_structure(normalized_path, allow_absolute)

        # Check against base paths if required
        if require_base_path and self.base_paths:
            validated_path = self._validate_against_base_paths(normalized_path)
        else:
            validated_path = normalized_path

        # Final security check
        self._final_security_check(validated_path)

        return validated_path

    def _check_dangerous_patterns(self, path: str, original_path: str) -> None:
        """Check for dangerous patterns in the path."""
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, path, re.IGNORECASE):
                security_manager = get_security_manager()
                security_manager.log_security_event(
                    SecurityEvent(
                        event_type="dangerous_path_pattern",
                        severity="high",
                        message=f"Dangerous pattern detected in path: {pattern}",
                        metadata={
                            "original_path": original_path,
                            "decoded_path": path,
                            "pattern": pattern,
                        },
                    )
                )
                raise SecurityError(f"Dangerous path pattern detected: {pattern}")

    def _check_forbidden_characters(self, path: str) -> None:
        """Check for forbidden characters in the path."""
        for char in self.FORBIDDEN_CHARS:
            if char in path:
                raise SecurityError(f"Forbidden character in path: {repr(char)}")

    def _normalize_path(self, path: str) -> str:
        """Normalize the path safely."""
        # Convert backslashes to forward slashes for consistency
        path = path.replace("\\", "/")

        # Remove multiple consecutive slashes
        path = re.sub(r"/+", "/", path)

        # Use pathlib for safe normalization
        try:
            # Create a PurePath to avoid file system access
            pure_path = PurePath(path)

            # Check for parent directory traversal in parts
            for part in pure_path.parts:
                if part == "..":
                    raise SecurityError("Path traversal attempt detected")
                if part.startswith(".") and len(part) > 1 and part != ".":
                    # Allow single dot but be suspicious of other dot patterns
                    if ".." in part or part.count(".") > 2:
                        raise SecurityError("Suspicious path component detected")

            # Normalize using os.path.normpath but validate result
            normalized = os.path.normpath(str(pure_path))

            # Ensure normalization didn't introduce traversal
            if ".." in normalized:
                raise SecurityError("Path normalization resulted in traversal")

            return normalized

        except Exception as e:
            if isinstance(e, SecurityError):
                raise
            raise SecurityError(f"Path normalization failed: {str(e)}")

    def _check_dangerous_names(self, path: str) -> None:
        """Check for dangerous file names."""
        path_obj = Path(path)

        # Check each part of the path (but be more lenient with intermediate dirs)
        for i, part in enumerate(path_obj.parts):
            part_upper = part.upper()

            # For intermediate directories, only check exact matches
            # For the final component (filename), be more strict
            is_final_component = i == len(path_obj.parts) - 1

            # Check against dangerous names (exact match only)
            if part_upper in self.DANGEROUS_NAMES:
                if is_final_component:
                    raise SecurityError(f"Dangerous file name detected: {part}")
                # For intermediate dirs, only block if it's an exact reserved name
                elif part_upper in {
                    "CON",
                    "PRN",
                    "AUX",
                    "NUL",
                    "COM1",
                    "COM2",
                    "COM3",
                    "COM4",
                    "COM5",
                    "COM6",
                    "COM7",
                    "COM8",
                    "COM9",
                    "LPT1",
                    "LPT2",
                    "LPT3",
                    "LPT4",
                    "LPT5",
                    "LPT6",
                    "LPT7",
                    "LPT8",
                    "LPT9",
                }:
                    # Only block if it's the exact reserved name, not a substring
                    if part.upper() == part_upper:
                        raise SecurityError(f"Reserved file name detected: {part}")

            # Check for Windows reserved names with extensions (final component only)
            if is_final_component:
                name_without_ext = part_upper.split(".")[0]
                if name_without_ext in self.DANGEROUS_NAMES:
                    raise SecurityError(f"Reserved file name detected: {part}")

    def _validate_path_structure(self, path: str, allow_absolute: bool) -> None:
        """Validate the overall path structure."""
        # Check if path is absolute
        is_absolute = os.path.isabs(path)

        if is_absolute and not allow_absolute:
            raise SecurityError("Absolute paths not allowed")

        # Check path length
        if len(path) > 4096:  # Common filesystem limit
            raise SecurityError("Path too long")

        # Check for empty components
        if "//" in path or path.endswith("/"):
            # Allow trailing slash for directories, but not empty components
            if "//" in path:
                raise SecurityError("Empty path components detected")

        # Validate individual path components
        path_obj = Path(path)
        for part in path_obj.parts:
            if not part or part.isspace():
                raise SecurityError("Empty or whitespace-only path component")

            # Check component length
            if len(part) > 255:  # Common filename length limit
                raise SecurityError("Path component too long")

    def _validate_against_base_paths(self, path: str) -> str:
        """Validate path against allowed base paths."""
        if not self.base_paths:
            return path

        # Try to resolve against each base path
        for base_path in self.base_paths:
            try:
                # Join with base path
                full_path = os.path.join(base_path, path)

                # Resolve to absolute path
                resolved_path = os.path.abspath(full_path)

                # Ensure the resolved path is within the base path
                if resolved_path.startswith(base_path):
                    return resolved_path

            except Exception:  # nosec B112
                continue

        raise SecurityError("Path not within allowed base directories")

    def _final_security_check(self, path: str) -> None:
        """Perform final security validation."""
        # Check for any remaining dangerous patterns after normalization
        if ".." in path:
            raise SecurityError("Path traversal detected after normalization")

        # Check for symbolic link attempts (basic check)
        if os.path.exists(path) and os.path.islink(path):
            raise SecurityError("Symbolic links not allowed")

        # Log successful validation for monitoring
        security_manager = get_security_manager()
        security_manager.log_security_event(
            SecurityEvent(
                event_type="path_validation_success",
                severity="low",
                message=f"Path validation successful: {path}",
                metadata={"validated_path": path},
            )
        )

    def is_safe_path(self, path: str) -> bool:
        """Check if a path is safe without raising exceptions."""
        try:
            self.validate_path(path)
            return True
        except SecurityError:
            return False

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize a filename for safe use."""
        if not filename:
            raise SecurityError("Empty filename provided")

        # Remove forbidden characters
        sanitized = filename
        for char in self.FORBIDDEN_CHARS:
            sanitized = sanitized.replace(char, "_")

        # Replace other problematic characters
        sanitized = re.sub(r'[<>:"|?*]', "_", sanitized)

        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip(". ")

        # Ensure it's not empty after sanitization
        if not sanitized:
            raise SecurityError("Filename becomes empty after sanitization")

        # Check against dangerous names
        if sanitized.upper() in self.DANGEROUS_NAMES:
            sanitized = f"safe_{sanitized}"

        # Limit length
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            max_name_len = 255 - len(ext)
            sanitized = name[:max_name_len] + ext

        return sanitized

    def get_safe_path_info(self, path: str) -> Dict[str, Any]:
        """Get information about path safety."""
        info: Dict[str, Any] = {
            "original_path": path,
            "is_safe": False,
            "issues": [],
            "sanitized_path": None,
        }

        try:
            sanitized = self.validate_path(path)
            info["is_safe"] = True
            info["sanitized_path"] = sanitized
        except SecurityError as e:
            info["issues"].append(str(e))

        return info


# Global path validator instance
_path_validator: Optional[PathValidator] = None


def get_path_validator(base_paths: Optional[List[str]] = None) -> PathValidator:
    """Get or create global path validator instance."""
    global _path_validator
    if _path_validator is None or base_paths:
        _path_validator = PathValidator(base_paths)
    return _path_validator


def validate_path(
    path: str,
    base_paths: Optional[List[str]] = None,
    allow_absolute: bool = False,
    require_base_path: bool = True,
) -> str:
    """Validate a path."""
    validator = get_path_validator(base_paths)
    return validator.validate_path(path, allow_absolute, require_base_path)


def is_safe_path(path: str, base_paths: Optional[List[str]] = None) -> bool:
    """Check if a path is safe."""
    validator = get_path_validator(base_paths)
    return validator.is_safe_path(path)


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename."""
    validator = get_path_validator()
    return validator.sanitize_filename(filename)
