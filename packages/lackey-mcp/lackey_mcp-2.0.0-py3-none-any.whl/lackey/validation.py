"""Input validation and security module for Lackey."""

import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class ValidationError(Exception):
    """Raised when input validation fails."""

    pass


class SecurityError(Exception):
    """Raised when security validation fails."""

    pass


@dataclass
class ValidationRule:
    """Represents a validation rule with constraints."""

    field_name: str
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    pattern: Optional[str] = None
    required: bool = False
    allowed_values: Optional[Set[str]] = None

    def validate(self, value: Any) -> List[str]:
        """Validate a value against this rule. Returns list of errors."""
        errors = []

        if value is None:
            if self.required:
                errors.append(f"{self.field_name} is required")
            return errors

        # Convert to string for validation
        str_value = str(value) if not isinstance(value, str) else value

        # Length validation
        if self.min_length is not None and len(str_value) < self.min_length:
            errors.append(
                f"{self.field_name} must be at least {self.min_length} "
                f"characters long"
            )

        if self.max_length is not None and len(str_value) > self.max_length:
            errors.append(
                f"{self.field_name} must be no more than {self.max_length} "
                f"characters long"
            )

        # Pattern validation
        if self.pattern and not re.match(self.pattern, str_value):
            errors.append(f"{self.field_name} contains invalid characters")

        # Allowed values validation
        if self.allowed_values and str_value not in self.allowed_values:
            errors.append(
                f"{self.field_name} must be one of: "
                f"{', '.join(sorted(self.allowed_values))}"
            )

        return errors


class InputValidator:
    """Comprehensive input validation for Lackey operations."""

    # Safe character pattern: alphanumeric, spaces, and safe punctuation
    SAFE_CHARS = r"^[a-zA-Z0-9\s\-_\.\,\!\?\:\;\(\)\[\]\/]+$"

    # Path-safe pattern: no path traversal or dangerous characters
    PATH_SAFE = r"^[a-zA-Z0-9._/-]+$"

    # Project name pattern: URL-safe characters only
    PROJECT_NAME = r"^[a-zA-Z0-9_-]+$"

    # Tag pattern: simple alphanumeric with hyphens and underscores
    TAG_PATTERN = r"^[a-zA-Z0-9\-_]+$"

    # UUID pattern for IDs
    UUID_PATTERN = (
        r"^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-"
        r"[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"
    )

    # Blocked patterns that could indicate malicious content
    BLOCKED_PATTERNS = [
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
    ]

    def __init__(self) -> None:
        """Initialize validator with validation rules."""
        self.rules = self._create_validation_rules()

    def _create_validation_rules(self) -> Dict[str, ValidationRule]:
        """Create validation rules for different field types."""
        return {
            "task_title": ValidationRule(
                "task_title",
                max_length=200,
                min_length=1,
                pattern=self.SAFE_CHARS,
                required=True,
            ),
            "task_objective": ValidationRule(
                "task_objective",
                max_length=2000,
                min_length=1,
                pattern=self.SAFE_CHARS,
                required=True,
            ),
            "task_context": ValidationRule(
                "task_context", max_length=5000, pattern=self.SAFE_CHARS
            ),
            "task_step": ValidationRule(
                "task_step", max_length=1000, pattern=self.SAFE_CHARS
            ),
            "success_criterion": ValidationRule(
                "success_criterion", max_length=500, pattern=self.SAFE_CHARS
            ),
            "project_name": ValidationRule(
                "project_name",
                max_length=100,
                min_length=1,
                pattern=self.PROJECT_NAME,
                required=True,
            ),
            "friendly_name": ValidationRule(
                "friendly_name",
                max_length=200,
                min_length=1,
                pattern=self.SAFE_CHARS,
                required=True,
            ),
            "project_description": ValidationRule(
                "project_description",
                max_length=10000,
                min_length=1,
                pattern=self.SAFE_CHARS,
                required=True,
            ),
            "file_path": ValidationRule(
                "file_path", max_length=4096, pattern=self.PATH_SAFE
            ),
            "agent_role": ValidationRule(
                "agent_role",
                max_length=50,
                pattern=self.PROJECT_NAME,
                allowed_values={
                    "manager",
                    "architect",
                    "developer",
                    "sysadmin",
                    "writer",
                },
            ),
            "tag": ValidationRule("tag", max_length=50, pattern=self.TAG_PATTERN),
            "task_id": ValidationRule(
                "task_id", pattern=self.UUID_PATTERN, required=True
            ),
            "project_id": ValidationRule(
                "project_id", pattern=self.UUID_PATTERN, required=True
            ),
        }

    def validate_field(self, field_type: str, value: Any) -> List[str]:
        """Validate a single field value."""
        if field_type not in self.rules:
            raise ValueError(f"Unknown field type: {field_type}")

        rule = self.rules[field_type]
        return rule.validate(value)

    def validate_task_data(self, task_data: Dict[str, Any]) -> List[str]:
        """Validate task creation/update data."""
        errors = []

        # Validate required fields
        errors.extend(self.validate_field("task_title", task_data.get("title")))
        errors.extend(self.validate_field("task_objective", task_data.get("objective")))

        # Validate optional fields if present
        if "context" in task_data:
            errors.extend(self.validate_field("task_context", task_data["context"]))

        # Validate steps
        steps = task_data.get("steps", [])
        if not steps:
            errors.append("At least one step is required")
        elif len(steps) > 50:
            errors.append("Maximum 50 steps allowed")
        else:
            for i, step in enumerate(steps):
                step_errors = self.validate_field("task_step", step)
                errors.extend([f"Step {i+1}: {err}" for err in step_errors])

        # Validate success criteria
        criteria = task_data.get("success_criteria", [])
        if not criteria:
            errors.append("At least one success criterion is required")
        elif len(criteria) > 20:
            errors.append("Maximum 20 success criteria allowed")
        else:
            for i, criterion in enumerate(criteria):
                crit_errors = self.validate_field("success_criterion", criterion)
                errors.extend(
                    [f"Success criterion {i+1}: {err}" for err in crit_errors]
                )

        # Validate complexity
        complexity = task_data.get("complexity")
        if complexity not in ["low", "medium", "high"]:
            errors.append("Complexity must be 'low', 'medium', or 'high'")

        # Validate tags
        tags = task_data.get("tags", [])
        if len(tags) > 10:
            errors.append("Maximum 10 tags allowed")
        else:
            for tag in tags:
                errors.extend(self.validate_field("tag", tag))

        # Validate dependencies
        dependencies = task_data.get("dependencies", [])
        if len(dependencies) > 50:
            errors.append("Maximum 50 dependencies allowed")
        else:
            for dep_id in dependencies:
                errors.extend(self.validate_field("task_id", dep_id))

        # Check for blocked patterns
        content_fields = ["title", "objective", "context", "steps", "success_criteria"]
        for field in content_fields:
            if field in task_data:
                field_value = task_data[field]
                if isinstance(field_value, list):
                    field_value = " ".join(str(item) for item in field_value)
                else:
                    field_value = str(field_value)

                blocked_errors = self._check_blocked_patterns(field_value, field)
                errors.extend(blocked_errors)

        return errors

    def validate_project_data(self, project_data: Dict[str, Any]) -> List[str]:
        """Validate project creation/update data."""
        errors = []

        # Validate required fields
        errors.extend(
            self.validate_field("friendly_name", project_data.get("friendly_name"))
        )
        errors.extend(
            self.validate_field("project_description", project_data.get("description"))
        )

        # Validate objectives
        objectives = project_data.get("objectives", [])
        if not objectives:
            errors.append("At least one objective is required")
        elif len(objectives) > 10:
            errors.append("Maximum 10 objectives allowed")
        else:
            for i, objective in enumerate(objectives):
                obj_errors = self.validate_field("project_description", objective)
                errors.extend([f"Objective {i+1}: {err}" for err in obj_errors])

        # Validate tags
        tags = project_data.get("tags", [])
        if len(tags) > 20:
            errors.append("Maximum 20 tags allowed")
        else:
            for tag in tags:
                errors.extend(self.validate_field("tag", tag))

        # Check for blocked patterns
        content_fields = ["friendly_name", "description", "objectives"]
        for field in content_fields:
            if field in project_data:
                field_value = project_data[field]
                if isinstance(field_value, list):
                    field_value = " ".join(str(item) for item in field_value)
                else:
                    field_value = str(field_value)

                blocked_errors = self._check_blocked_patterns(field_value, field)
                errors.extend(blocked_errors)

        return errors

    def _check_blocked_patterns(self, content: str, field_name: str) -> List[str]:
        """Check content for blocked patterns."""
        errors = []
        content_lower = content.lower()

        for pattern in self.BLOCKED_PATTERNS:
            if pattern in content_lower:
                errors.append(f"{field_name} contains blocked pattern: " f"{pattern}")

        return errors

    def sanitize_path(self, path: str) -> str:
        """Sanitize and validate file paths."""
        if not path:
            raise SecurityError("Empty path provided")

        # Normalize path separators
        path = os.path.normpath(path)

        # Block path traversal attempts (but allow absolute paths for testing)
        if ".." in path:
            raise SecurityError("Path traversal attempt detected")

        # For relative paths, ensure they don't start with /
        # But allow absolute paths that don't contain ..
        if path.startswith("/") and ".." in path:
            raise SecurityError("Path traversal attempt detected")

        # Validate character set
        if not re.match(self.PATH_SAFE, path):
            raise SecurityError("Invalid characters in path")

        # Check length
        if len(path) > 4096:
            raise SecurityError("Path too long")

        return path

    def sanitize_content(self, content: str, content_type: str) -> str:
        """Sanitize user-provided content."""
        # Length validation based on content type
        max_lengths = {
            "title": 200,
            "objective": 2000,
            "context": 5000,
            "step": 1000,
            "criterion": 500,
            "description": 10000,
            "note": 2000,
        }

        max_length = max_lengths.get(content_type, 1000)
        if len(content) > max_length:
            raise ValidationError(
                f"Content exceeds maximum length of " f"{max_length} characters"
            )

        # Pattern detection
        for pattern in self.BLOCKED_PATTERNS:
            if pattern.lower() in content.lower():
                raise SecurityError(f"Blocked pattern detected: {pattern}")

        # HTML/Script tag removal for markdown content
        if content_type in ["objective", "context", "description"]:
            content = re.sub(
                r"<script[^>]*>.*?</script>",
                "",
                content,
                flags=re.IGNORECASE | re.DOTALL,
            )
            content = re.sub(r"<[^>]+>", "", content)  # Remove HTML tags

        return content.strip()

    def validate_file_size(self, file_path: str, max_size_mb: float = 1.0) -> None:
        """Validate file size limits."""
        if not os.path.exists(file_path):
            return

        file_size = os.path.getsize(file_path)
        max_size_bytes = max_size_mb * 1024 * 1024

        if file_size > max_size_bytes:
            raise ValidationError(
                f"File size ({file_size} bytes) exceeds "
                f"maximum allowed size ({max_size_bytes} bytes)"
            )

    def validate_file_extension(self, file_path: str) -> None:
        """Validate file extension against whitelist."""
        allowed_extensions = {".md", ".yaml", ".yml", ".json"}

        file_ext = Path(file_path).suffix.lower()
        if file_ext not in allowed_extensions:
            raise SecurityError(
                f"File extension '{file_ext}' not allowed. "
                f"Allowed: {', '.join(allowed_extensions)}"
            )

    def calculate_file_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum for file integrity validation."""
        hash_sha256 = hashlib.sha256()

        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
        except IOError as e:
            raise ValidationError(f"Cannot read file for checksum: {e}")

        return hash_sha256.hexdigest()

    def validate_encoding(self, file_path: str) -> None:
        """Validate file encoding is UTF-8."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                f.read()
        except UnicodeDecodeError:
            raise ValidationError("File must be UTF-8 encoded")
        except IOError as e:
            raise ValidationError(f"Cannot read file: {e}")


# Global validator instance
validator = InputValidator()
