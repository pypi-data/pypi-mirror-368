"""Template validation and verification system.

This module provides comprehensive validation for templates to ensure
they are well-formed, secure, and functional.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from .templates import Template, TemplateType, TemplateVariable, VariableType


class ValidationSeverity(Enum):
    """Validation issue severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Represents a validation issue found in a template."""

    severity: ValidationSeverity
    code: str
    message: str
    field: Optional[str] = None
    suggestion: Optional[str] = None

    def __str__(self) -> str:
        """Return string representation of the validation issue."""
        prefix = f"[{self.severity.value.upper()}]"
        field_info = f" in {self.field}" if self.field else ""
        suggestion_info = f" Suggestion: {self.suggestion}" if self.suggestion else ""
        return f"{prefix} {self.code}: {self.message}{field_info}{suggestion_info}"


class TemplateValidator:
    """Validates templates for correctness, security, and best practices."""

    def __init__(self) -> None:
        """Initialize the template validator."""
        self.issues: List[ValidationIssue] = []

    def validate_template(self, template: Template) -> List[ValidationIssue]:
        """Validate a complete template and return all issues found."""
        self.issues = []

        # Basic structure validation
        self._validate_basic_structure(template)

        # Variable validation
        self._validate_variables(template)

        # Content validation
        self._validate_content(template)

        # File template validation
        self._validate_file_templates(template)

        # Security validation
        self._validate_security(template)

        # Best practices validation
        self._validate_best_practices(template)

        return self.issues.copy()

    def _add_issue(
        self,
        severity: ValidationSeverity,
        code: str,
        message: str,
        field: Optional[str] = None,
        suggestion: Optional[str] = None,
    ) -> None:
        """Add a validation issue to the list."""
        self.issues.append(
            ValidationIssue(
                severity=severity,
                code=code,
                message=message,
                field=field,
                suggestion=suggestion,
            )
        )

    def _validate_basic_structure(self, template: Template) -> None:
        """Validate basic template structure and required fields."""
        # Required fields
        if not template.id:
            self._add_issue(
                ValidationSeverity.CRITICAL,
                "MISSING_ID",
                "Template ID is required",
                "id",
            )

        if not template.name:
            self._add_issue(
                ValidationSeverity.CRITICAL,
                "MISSING_NAME",
                "Template name is required",
                "name",
            )

        if not template.friendly_name:
            self._add_issue(
                ValidationSeverity.ERROR,
                "MISSING_FRIENDLY_NAME",
                "Template friendly name is required",
                "friendly_name",
            )

        if not template.description:
            self._add_issue(
                ValidationSeverity.ERROR,
                "MISSING_DESCRIPTION",
                "Template description is required",
                "description",
            )

        # Name validation
        if template.name and not re.match(r"^[a-z0-9\-]+$", template.name):
            self._add_issue(
                ValidationSeverity.ERROR,
                "INVALID_NAME_FORMAT",
                "Template name must contain only lowercase letters, "
                "numbers, and hyphens",
                "name",
                "Use lowercase letters, numbers, and hyphens only",
            )

        # Version validation
        if template.version and not re.match(r"^\d+\.\d+\.\d+$", template.version):
            self._add_issue(
                ValidationSeverity.WARNING,
                "INVALID_VERSION_FORMAT",
                "Template version should follow semantic versioning (x.y.z)",
                "version",
                "Use semantic versioning format like '1.0.0'",
            )

    def _validate_variables(self, template: Template) -> None:
        """Validate template variables."""
        variable_names = set()

        for i, variable in enumerate(template.variables):
            field_prefix = f"variables[{i}]"

            # Check for duplicate variable names
            if variable.name in variable_names:
                self._add_issue(
                    ValidationSeverity.ERROR,
                    "DUPLICATE_VARIABLE",
                    f"Duplicate variable name: {variable.name}",
                    f"{field_prefix}.name",
                )
            variable_names.add(variable.name)

            # Variable name validation
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", variable.name):
                self._add_issue(
                    ValidationSeverity.ERROR,
                    "INVALID_VARIABLE_NAME",
                    f"Invalid variable name: {variable.name}",
                    f"{field_prefix}.name",
                    "Use letters, numbers, and underscores only, "
                    "starting with letter or underscore",
                )

            # Type-specific validation
            self._validate_variable_constraints(variable, field_prefix)

    def _validate_variable_constraints(
        self, variable: TemplateVariable, field_prefix: str
    ) -> None:
        """Validate variable type-specific constraints."""
        # Choice validation
        if variable.type == VariableType.CHOICE:
            if not variable.choices:
                self._add_issue(
                    ValidationSeverity.ERROR,
                    "MISSING_CHOICES",
                    f"Choice variable '{variable.name}' must have choices defined",
                    f"{field_prefix}.choices",
                )
            elif variable.default and variable.default not in variable.choices:
                self._add_issue(
                    ValidationSeverity.ERROR,
                    "INVALID_DEFAULT_CHOICE",
                    f"Default value '{variable.default}' not in choices "
                    f"for variable '{variable.name}'",
                    f"{field_prefix}.default",
                )

        # Pattern validation for string variables
        if variable.validation_pattern:
            try:
                re.compile(variable.validation_pattern)
            except re.error as e:
                self._add_issue(
                    ValidationSeverity.ERROR,
                    "INVALID_REGEX_PATTERN",
                    f"Invalid regex pattern for variable '{variable.name}': {e}",
                    f"{field_prefix}.validation_pattern",
                )

        # Range validation for numeric variables
        if variable.type == VariableType.INTEGER:
            if (
                variable.min_value is not None
                and variable.max_value is not None
                and variable.min_value > variable.max_value
            ):
                self._add_issue(
                    ValidationSeverity.ERROR,
                    "INVALID_RANGE",
                    f"Min value greater than max value for variable '{variable.name}'",
                    f"{field_prefix}.min_value",
                )

    def _validate_content(self, template: Template) -> None:
        """Validate template content structure."""
        if not template.content:
            self._add_issue(
                ValidationSeverity.WARNING,
                "EMPTY_CONTENT",
                "Template has no content defined",
                "content",
            )
            return

        # Type-specific content validation
        if template.template_type == TemplateType.PROJECT:
            self._validate_project_content(template.content)
        elif template.template_type in (TemplateType.TASK_CHAIN, TemplateType.WORKFLOW):
            self._validate_task_content(template.content)

        # Variable reference validation
        self._validate_variable_references(template)

    def _validate_project_content(self, content: Dict[str, Any]) -> None:
        """Validate project-specific content structure."""
        project_data = content.get("project", {})

        if not project_data:
            self._add_issue(
                ValidationSeverity.ERROR,
                "MISSING_PROJECT_DATA",
                "Project template must have 'project' section in content",
                "content.project",
            )
            return

        # Check required project fields
        required_fields = ["friendly_name", "description"]
        for field in required_fields:
            if field not in project_data:
                self._add_issue(
                    ValidationSeverity.WARNING,
                    "MISSING_PROJECT_FIELD",
                    f"Project content missing recommended field: {field}",
                    f"content.project.{field}",
                )

    def _validate_task_content(self, content: Dict[str, Any]) -> None:
        """Validate task-specific content structure."""
        tasks_data = content.get("tasks", [])

        if not tasks_data:
            self._add_issue(
                ValidationSeverity.WARNING,
                "NO_TASKS_DEFINED",
                "Task chain/workflow template has no tasks defined",
                "content.tasks",
            )
            return

        for i, task_data in enumerate(tasks_data):
            field_prefix = f"content.tasks[{i}]"

            # Check required task fields
            required_fields = ["title", "objective"]
            for field in required_fields:
                if field not in task_data:
                    self._add_issue(
                        ValidationSeverity.ERROR,
                        "MISSING_TASK_FIELD",
                        f"Task missing required field: {field}",
                        f"{field_prefix}.{field}",
                    )

            # Validate task complexity
            if "complexity" in task_data:
                valid_complexities = ["low", "medium", "high"]
                if task_data["complexity"] not in valid_complexities:
                    self._add_issue(
                        ValidationSeverity.ERROR,
                        "INVALID_COMPLEXITY",
                        f"Invalid task complexity: {task_data['complexity']}",
                        f"{field_prefix}.complexity",
                        f"Use one of: {', '.join(valid_complexities)}",
                    )

    def _validate_file_templates(self, template: Template) -> None:
        """Validate file templates."""
        for filename, content in template.files.items():
            # Check for potentially dangerous file paths
            if ".." in filename or filename.startswith("/"):
                self._add_issue(
                    ValidationSeverity.CRITICAL,
                    "UNSAFE_FILE_PATH",
                    f"Unsafe file path: {filename}",
                    f"files.{filename}",
                    "Use relative paths without '..' or leading '/'",
                )

            # Check for empty file content
            if not content.strip():
                self._add_issue(
                    ValidationSeverity.WARNING,
                    "EMPTY_FILE_TEMPLATE",
                    f"File template is empty: {filename}",
                    f"files.{filename}",
                )

    def _validate_variable_references(self, template: Template) -> None:
        """Validate that all variable references in content are defined."""
        defined_variables = {var.name for var in template.variables}

        # Find all variable references in content and files
        all_content = str(template.content) + " " + " ".join(template.files.values())

        # Find {{variable_name}} patterns
        variable_pattern = r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}"
        referenced_variables = set(re.findall(variable_pattern, all_content))

        # Check for undefined variables
        undefined_variables = referenced_variables - defined_variables
        for var_name in undefined_variables:
            self._add_issue(
                ValidationSeverity.ERROR,
                "UNDEFINED_VARIABLE",
                f"Variable '{var_name}' is referenced but not defined",
                "variables",
                f"Add variable definition for '{var_name}'",
            )

        # Check for unused variables
        unused_variables = defined_variables - referenced_variables
        for var_name in unused_variables:
            self._add_issue(
                ValidationSeverity.WARNING,
                "UNUSED_VARIABLE",
                f"Variable '{var_name}' is defined but never used",
                "variables",
                f"Remove unused variable '{var_name}' or use it in content",
            )

    def _validate_security(self, template: Template) -> None:
        """Validate template for security issues."""
        # Check for potentially dangerous content
        dangerous_patterns = [
            (r"<script", "SCRIPT_TAG", "Script tags in template content"),
            (r"javascript:", "JAVASCRIPT_URL", "JavaScript URLs in template"),
            (r"eval\s*\(", "EVAL_FUNCTION", "Eval function usage"),
            (r"exec\s*\(", "EXEC_FUNCTION", "Exec function usage"),
        ]

        all_content = str(template.content) + " " + " ".join(template.files.values())

        for pattern, code, message in dangerous_patterns:
            if re.search(pattern, all_content, re.IGNORECASE):
                self._add_issue(
                    ValidationSeverity.CRITICAL,
                    code,
                    message,
                    "content",
                    "Remove potentially dangerous content",
                )

    def _validate_best_practices(self, template: Template) -> None:
        """Validate template against best practices."""
        # Check for good documentation
        if len(template.description) < 50:
            self._add_issue(
                ValidationSeverity.INFO,
                "SHORT_DESCRIPTION",
                "Template description is quite short",
                "description",
                "Consider adding more detailed description",
            )

        # Check for tags
        if not template.tags:
            self._add_issue(
                ValidationSeverity.INFO,
                "NO_TAGS",
                "Template has no tags for categorization",
                "tags",
                "Add relevant tags for better discoverability",
            )

        # Check for author information
        if not template.author:
            self._add_issue(
                ValidationSeverity.INFO,
                "NO_AUTHOR",
                "Template has no author information",
                "author",
                "Add author information for attribution",
            )

        # Check variable descriptions
        for i, variable in enumerate(template.variables):
            if len(variable.description) < 10:
                self._add_issue(
                    ValidationSeverity.INFO,
                    "SHORT_VARIABLE_DESCRIPTION",
                    f"Variable '{variable.name}' has a short description",
                    f"variables[{i}].description",
                    "Provide more detailed variable description",
                )


def validate_template_file(template_path: str) -> List[ValidationIssue]:
    """Validate a template file and return validation issues."""
    import yaml

    try:
        with open(template_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        template = Template.from_dict(data)
        validator = TemplateValidator()
        return validator.validate_template(template)

    except Exception as e:
        return [
            ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                code="TEMPLATE_LOAD_ERROR",
                message=f"Failed to load template: {e}",
                field="file",
            )
        ]


def validate_template_instantiation(
    template: Template, values: Dict[str, Any]
) -> List[ValidationIssue]:
    """Validate template instantiation with provided values."""
    issues = []

    # Validate variable values
    validation_errors = template.validate_variables(values)
    for error in validation_errors:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="INVALID_VARIABLE_VALUE",
                message=error,
                field="values",
            )
        )

    # Try to render content to check for issues
    try:
        template.render_content(values)
    except Exception as e:
        issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="RENDER_ERROR",
                message=f"Failed to render template content: {e}",
                field="content",
            )
        )

    return issues
