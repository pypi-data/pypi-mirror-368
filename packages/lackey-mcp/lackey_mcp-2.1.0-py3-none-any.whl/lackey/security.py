"""Comprehensive security module for Lackey task management system.

This module provides enhanced security measures including:
- Advanced input validation and sanitization
- Path traversal protection
- Rate limiting
- Security logging and monitoring
- Authentication framework
- File system access controls
"""

import hashlib
import hmac
import logging
import os
import re
import secrets
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from lackey.validation import SecurityError, ValidationError, validator

logger = logging.getLogger(__name__)


@dataclass
class SecurityConfig:
    """Security configuration settings."""

    # Rate limiting settings
    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000
    rate_limit_window_minutes: int = 1

    # File system security
    max_file_size_mb: float = 10.0
    allowed_file_extensions: Set[str] = field(
        default_factory=lambda: {".md", ".yaml", ".yml", ".json", ".txt"}
    )
    max_path_depth: int = 10

    # Content security
    max_content_length: int = 50000
    blocked_patterns: List[str] = field(
        default_factory=lambda: [
            "javascript:",
            "data:",
            "<script",
            "eval(",
            "exec(",
            "system(",
            "shell_exec(",
            "__import__",
            "subprocess",
            "os.system",
            "rm -rf",
            "del /f",
            "format c:",
            "../../",
            "../..",
            "..\\\\",
            "file://",
            "ftp://",
            "http://",
            "https://",
            "ldap://",
            "gopher://",
        ]
    )

    # Authentication settings
    session_timeout_minutes: int = 60
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 15

    # Logging settings
    log_security_events: bool = True
    log_failed_validations: bool = True
    log_rate_limit_violations: bool = True


@dataclass
class RateLimitEntry:
    """Rate limiting entry for tracking requests."""

    timestamps: deque = field(default_factory=deque)
    blocked_until: Optional[float] = None


@dataclass
class SecurityEvent:
    """Security event for logging and monitoring."""

    event_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SecurityManager:
    """Comprehensive security manager for Lackey operations."""

    def __init__(self, config: Optional[SecurityConfig] = None):
        """Initialize security manager with configuration."""
        self.config = config or SecurityConfig()
        self.rate_limits: Dict[str, RateLimitEntry] = defaultdict(RateLimitEntry)
        self.security_events: List[SecurityEvent] = []
        self.failed_attempts: Dict[str, List[float]] = defaultdict(list)
        self.blocked_ips: Dict[str, float] = {}

        # Initialize security logging
        self._setup_security_logging()

    def _setup_security_logging(self) -> None:
        """Set up security-specific logging."""
        security_logger = logging.getLogger("lackey.security")
        security_logger.setLevel(logging.INFO)

        # Create security log handler if it doesn't exist
        if not security_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - SECURITY - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            security_logger.addHandler(handler)

    def log_security_event(self, event: SecurityEvent) -> None:
        """Log a security event."""
        self.security_events.append(event)

        if self.config.log_security_events:
            security_logger = logging.getLogger("lackey.security")
            log_message = f"{event.event_type}: {event.message}"

            if event.metadata:
                log_message += f" | Metadata: {event.metadata}"

            if event.severity == "critical":
                security_logger.critical(log_message)
            elif event.severity == "high":
                security_logger.error(log_message)
            elif event.severity == "medium":
                security_logger.warning(log_message)
            else:
                security_logger.info(log_message)

    def validate_and_sanitize_input(
        self, data: Dict[str, Any], validation_rules: Dict[str, str]
    ) -> Dict[str, Any]:
        """Validate and sanitize input data comprehensively."""
        sanitized_data = {}
        errors = []

        for field_name, field_value in data.items():
            try:
                # Get validation rule for field
                rule_type = validation_rules.get(field_name, "safe_text")

                # Validate field
                if rule_type in validator.rules:
                    field_errors = validator.validate_field(rule_type, field_value)
                    if field_errors:
                        errors.extend(field_errors)
                        continue

                # Sanitize field value
                sanitized_value = self._sanitize_value(field_value, rule_type)
                sanitized_data[field_name] = sanitized_value

            except (ValidationError, SecurityError) as e:
                errors.append(f"{field_name}: {str(e)}")
                self.log_security_event(
                    SecurityEvent(
                        event_type="input_validation_failed",
                        severity="medium",
                        message=f"Input validation failed for field "
                        f"{field_name}: {str(e)}",
                        metadata={"field": field_name, "error": str(e)},
                    )
                )

        if errors:
            raise ValidationError(f"Input validation failed: {'; '.join(errors)}")

        return sanitized_data

    def _sanitize_value(self, value: Any, value_type: str) -> Any:
        """Sanitize a single value based on its type."""
        if value is None:
            return None

        if isinstance(value, (list, tuple)):
            return [self._sanitize_string(str(item)) for item in value]

        if isinstance(value, dict):
            return {k: self._sanitize_value(v, value_type) for k, v in value.items()}

        return self._sanitize_string(str(value))

    def _sanitize_string(self, text: str) -> str:
        """Sanitize string content."""
        if not text:
            return text

        # Check for blocked patterns
        text_lower = text.lower()
        for pattern in self.config.blocked_patterns:
            if pattern.lower() in text_lower:
                self.log_security_event(
                    SecurityEvent(
                        event_type="blocked_pattern_detected",
                        severity="high",
                        message=f"Blocked pattern detected: {pattern}",
                        metadata={"pattern": pattern, "content_preview": text[:100]},
                    )
                )
                raise SecurityError(f"Blocked pattern detected: {pattern}")

        # Remove potentially dangerous characters
        # Allow alphanumeric, spaces, and safe punctuation
        sanitized = re.sub(r'[^\w\s\-_.,!?:;()\[\]{}@#$%^&*+=|\\/<>"\']', "", text)

        # Normalize whitespace
        sanitized = " ".join(sanitized.split())

        # Check length
        if len(sanitized) > self.config.max_content_length:
            raise ValidationError(
                f"Content exceeds maximum length of "
                f"{self.config.max_content_length}"
            )

        return sanitized

    def validate_file_path(self, file_path: str, base_path: str = "") -> str:
        """Validate and sanitize file paths with comprehensive security checks."""
        if not file_path:
            raise SecurityError("Empty file path provided")

        # Normalize path
        normalized_path = os.path.normpath(file_path)

        # Check for path traversal attempts
        if ".." in normalized_path or normalized_path.startswith("/"):
            self.log_security_event(
                SecurityEvent(
                    event_type="path_traversal_attempt",
                    severity="high",
                    message=f"Path traversal attempt detected: {file_path}",
                    metadata={
                        "original_path": file_path,
                        "normalized": normalized_path,
                    },
                )
            )
            raise SecurityError("Path traversal attempt detected")

        # Validate path depth
        path_parts = Path(normalized_path).parts
        if len(path_parts) > self.config.max_path_depth:
            raise SecurityError(
                f"Path depth exceeds maximum of {self.config.max_path_depth}"
            )

        # Validate file extension
        file_ext = Path(normalized_path).suffix.lower()
        if file_ext and file_ext not in self.config.allowed_file_extensions:
            raise SecurityError(
                f"File extension '{file_ext}' not allowed. "
                f"Allowed: {', '.join(sorted(self.config.allowed_file_extensions))}"
            )

        # Construct safe absolute path
        if base_path:
            safe_path = os.path.join(base_path, normalized_path)
            safe_path = os.path.abspath(safe_path)

            # Ensure the resolved path is still within base_path
            base_abs = os.path.abspath(base_path)
            if not safe_path.startswith(base_abs):
                raise SecurityError("Path escapes base directory")

            return safe_path

        return normalized_path

    def check_rate_limit(self, identifier: str, endpoint: str = "default") -> bool:
        """Check if request is within rate limits."""
        current_time = time.time()
        rate_key = f"{identifier}:{endpoint}"

        # Check if currently blocked
        if rate_key in self.blocked_ips:
            if current_time < self.blocked_ips[rate_key]:
                self.log_security_event(
                    SecurityEvent(
                        event_type="rate_limit_blocked_request",
                        severity="medium",
                        message=f"Request blocked due to rate limiting: {identifier}",
                        metadata={"identifier": identifier, "endpoint": endpoint},
                    )
                )
                return False
            else:
                # Unblock if timeout expired
                del self.blocked_ips[rate_key]

        # Get or create rate limit entry
        entry = self.rate_limits[rate_key]

        # Clean old timestamps (older than window)
        window_start = current_time - (self.config.rate_limit_window_minutes * 60)
        while entry.timestamps and entry.timestamps[0] < window_start:
            entry.timestamps.popleft()

        # Check if within limits
        if len(entry.timestamps) >= self.config.max_requests_per_minute:
            # Block for lockout duration
            self.blocked_ips[rate_key] = current_time + (
                self.config.lockout_duration_minutes * 60
            )

            self.log_security_event(
                SecurityEvent(
                    event_type="rate_limit_exceeded",
                    severity="high",
                    message=f"Rate limit exceeded for {identifier}",
                    metadata={
                        "identifier": identifier,
                        "endpoint": endpoint,
                        "requests_in_window": len(entry.timestamps),
                    },
                )
            )
            return False

        # Add current request timestamp
        entry.timestamps.append(current_time)
        return True

    def validate_file_content(self, file_path: str) -> None:
        """Validate file content for security issues."""
        if not os.path.exists(file_path):
            return

        # Check file size
        file_size = os.path.getsize(file_path)
        max_size_bytes = self.config.max_file_size_mb * 1024 * 1024

        if file_size > max_size_bytes:
            raise ValidationError(
                f"File size ({file_size} bytes) exceeds maximum allowed "
                f"size ({max_size_bytes} bytes)"
            )

        # Check file encoding and content
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

                # Check for blocked patterns in file content
                content_lower = content.lower()
                for pattern in self.config.blocked_patterns:
                    if pattern.lower() in content_lower:
                        self.log_security_event(
                            SecurityEvent(
                                event_type="malicious_file_content",
                                severity="high",
                                message=f"Blocked pattern found in file: {pattern}",
                                metadata={"file_path": file_path, "pattern": pattern},
                            )
                        )
                        raise SecurityError(f"File contains blocked pattern: {pattern}")

        except UnicodeDecodeError:
            raise ValidationError("File must be UTF-8 encoded")
        except IOError as e:
            raise ValidationError(f"Cannot read file: {e}")

    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a cryptographically secure random token."""
        return secrets.token_urlsafe(length)

    def hash_password(
        self, password: str, salt: Optional[str] = None
    ) -> tuple[str, str]:
        """Hash password with salt using PBKDF2."""
        if salt is None:
            salt = secrets.token_hex(16)

        # Use PBKDF2 with SHA-256
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000,  # 100k iterations
        )

        return password_hash.hex(), salt

    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash."""
        computed_hash, _ = self.hash_password(password, salt)
        return hmac.compare_digest(computed_hash, password_hash)

    def create_hmac_signature(self, data: str, secret_key: str) -> str:
        """Create HMAC signature for data integrity."""
        return hmac.new(
            secret_key.encode("utf-8"), data.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def verify_hmac_signature(self, data: str, signature: str, secret_key: str) -> bool:
        """Verify HMAC signature."""
        expected_signature = self.create_hmac_signature(data, secret_key)
        return hmac.compare_digest(signature, expected_signature)

    def get_security_report(self) -> Dict[str, Any]:
        """Generate security report with recent events and statistics."""
        current_time = time.time()

        # Count events by type and severity
        event_counts: Dict[str, int] = defaultdict(int)
        severity_counts: Dict[str, int] = defaultdict(int)

        # Only include events from last 24 hours
        recent_events = [
            event
            for event in self.security_events
            if current_time - event.timestamp < 86400  # 24 hours
        ]

        for event in recent_events:
            event_counts[event.event_type] += 1
            severity_counts[event.severity] += 1

        # Count active rate limits
        active_blocks = sum(
            1 for block_time in self.blocked_ips.values() if current_time < block_time
        )

        return {
            "total_events_24h": len(recent_events),
            "events_by_type": dict(event_counts),
            "events_by_severity": dict(severity_counts),
            "active_rate_limit_blocks": active_blocks,
            "total_rate_limit_entries": len(self.rate_limits),
            "config": {
                "max_requests_per_minute": self.config.max_requests_per_minute,
                "max_file_size_mb": self.config.max_file_size_mb,
                "allowed_extensions": list(self.config.allowed_file_extensions),
                "max_path_depth": self.config.max_path_depth,
            },
        }


def security_required(
    rate_limit_key: Optional[str] = None,
    validate_input: bool = True,
    validation_rules: Optional[Dict[str, str]] = None,
) -> Callable:
    """Add security checks to MCP endpoints."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get security manager instance
            security_manager = get_security_manager()

            # Rate limiting check
            if rate_limit_key:
                identifier = rate_limit_key
                if not security_manager.check_rate_limit(identifier, func.__name__):
                    raise SecurityError("Rate limit exceeded")

            # Input validation
            if validate_input and validation_rules:
                try:
                    # Validate and sanitize kwargs
                    sanitized_kwargs = security_manager.validate_and_sanitize_input(
                        kwargs, validation_rules
                    )
                    kwargs.update(sanitized_kwargs)
                except (ValidationError, SecurityError) as e:
                    security_manager.log_security_event(
                        SecurityEvent(
                            event_type="endpoint_security_violation",
                            severity="medium",
                            message=f"Security violation in {func.__name__}: {str(e)}",
                            metadata={"function": func.__name__, "error": str(e)},
                        )
                    )
                    raise

            # Call original function
            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Global security manager instance
_security_manager: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    """Get or create global security manager instance."""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager


def initialize_security(config: Optional[SecurityConfig] = None) -> SecurityManager:
    """Initialize global security manager with configuration."""
    global _security_manager
    _security_manager = SecurityManager(config)
    return _security_manager
