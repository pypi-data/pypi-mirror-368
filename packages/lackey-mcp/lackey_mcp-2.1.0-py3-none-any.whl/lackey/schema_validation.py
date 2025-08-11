"""Schema validation engine for parameter structure validation.

This module implements a comprehensive schema validation engine that validates
parameter structures against gateway schemas without referencing actual data.
Provides format validation for complex nested objects while maintaining
data isolation.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union


class ValidationResult(Enum):
    """Validation result status."""

    VALID = "valid"
    INVALID = "invalid"
    MISSING_REQUIRED = "missing_required"
    TYPE_MISMATCH = "type_mismatch"
    CONSTRAINT_VIOLATION = "constraint_violation"


@dataclass
class ValidationError:
    """Represents a validation error with context."""

    field: str
    error_type: ValidationResult
    message: str
    path: str = ""


@dataclass
class SchemaField:
    """Represents a schema field definition."""

    name: str
    field_type: str
    required: bool = False
    constraints: Optional[Dict[str, Any]] = None
    nested_schema: Optional[Dict[str, Any]] = None


class SchemaValidationEngine:
    """Core schema validation engine for parameter structure validation."""

    def __init__(self) -> None:
        """Initialize the schema validation engine."""
        self._type_validators = {
            "str": self._validate_string,
            "int": self._validate_integer,
            "float": self._validate_float,
            "bool": self._validate_boolean,
            "list": self._validate_list,
            "dict": self._validate_dict,
            "optional[str]": self._validate_optional_string,
            "optional[int]": self._validate_optional_integer,
            "optional[list]": self._validate_optional_list,
            "optional[dict]": self._validate_optional_dict,
        }

        self._constraint_validators: Dict[str, Callable] = {
            "validate_uuid": self._validate_uuid_format,
            "validate_status": self._validate_status_format,
            "validate_complexity": self._validate_complexity_format,
            "validate_note_type": self._validate_note_type_format,
            "min_length": self._validate_min_length,
            "max_length": self._validate_max_length,
            "pattern": self._validate_pattern,
            "range": self._validate_range,
        }

    def validate_parameters(
        self, parameters: Dict[str, Any], schema: Dict[str, Any]
    ) -> List[ValidationError]:
        """Validate parameters against schema definition.

        Args:
            parameters: Parameter dictionary to validate
            schema: Schema definition with required/optional fields and constraints

        Returns:
            List of validation errors, empty if valid
        """
        errors = []

        # Extract schema components
        required_fields = schema.get("required", [])
        optional_fields = schema.get("optional", {})
        types = schema.get("types", {})
        constraints = schema.get("constraints", {})

        # Check required fields
        for field in required_fields:
            if field not in parameters:
                errors.append(
                    ValidationError(
                        field=field,
                        error_type=ValidationResult.MISSING_REQUIRED,
                        message=f"Required field '{field}' is missing",
                    )
                )
            else:
                # Validate field type and constraints
                field_errors = self._validate_field(
                    field, parameters[field], types, constraints
                )
                errors.extend(field_errors)

        # Check optional fields if present
        for field in optional_fields:
            if field in parameters:
                field_errors = self._validate_field(
                    field, parameters[field], types, constraints
                )
                errors.extend(field_errors)

        # Check for unexpected fields
        allowed_fields = set(required_fields) | set(optional_fields.keys())
        for field in parameters:
            if field not in allowed_fields:
                errors.append(
                    ValidationError(
                        field=field,
                        error_type=ValidationResult.INVALID,
                        message=f"Unexpected field '{field}'",
                    )
                )

        return errors

    def validate_nested_structure(
        self, data: Dict[str, Any], schema: Dict[str, SchemaField]
    ) -> List[ValidationError]:
        """Validate complex nested object structures.

        Args:
            data: Data structure to validate
            schema: Schema definition with nested field specifications

        Returns:
            List of validation errors
        """
        errors = []

        for field_name, field_schema in schema.items():
            if field_schema.required and field_name not in data:
                errors.append(
                    ValidationError(
                        field=field_name,
                        error_type=ValidationResult.MISSING_REQUIRED,
                        message=f"Required nested field '{field_name}' is missing",
                    )
                )
                continue

            if field_name in data:
                value = data[field_name]

                # Type validation
                if not self._validate_type(value, field_schema.field_type):
                    errors.append(
                        ValidationError(
                            field=field_name,
                            error_type=ValidationResult.TYPE_MISMATCH,
                            message=f"Field '{field_name}' has invalid type",
                        )
                    )
                    continue

                # Constraint validation
                if field_schema.constraints:
                    constraint_errors = self._validate_constraints(
                        field_name, value, field_schema.constraints
                    )
                    errors.extend(constraint_errors)

                # Nested schema validation
                if field_schema.nested_schema and isinstance(value, dict):
                    nested_errors = self.validate_nested_structure(
                        value, field_schema.nested_schema
                    )
                    for error in nested_errors:
                        error.path = f"{field_name}.{error.path}".strip(".")
                    errors.extend(nested_errors)

        return errors

    def _validate_field(
        self,
        field_name: str,
        value: Any,
        types: Dict[str, str],
        constraints: Dict[str, Dict[str, Any]],
    ) -> List[ValidationError]:
        """Validate individual field against type and constraints."""
        errors = []

        # Type validation
        if field_name in types:
            expected_type = types[field_name]
            if not self._validate_type(value, expected_type):
                errors.append(
                    ValidationError(
                        field=field_name,
                        error_type=ValidationResult.TYPE_MISMATCH,
                        message=f"Field '{field_name}' expected type '{expected_type}'",
                    )
                )
                return errors  # Skip constraint validation if type is wrong

        # Constraint validation
        if field_name in constraints:
            constraint_errors = self._validate_constraints(
                field_name, value, constraints[field_name]
            )
            errors.extend(constraint_errors)

        return errors

    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value against expected type."""
        validator = self._type_validators.get(expected_type)
        if validator:
            return validator(value)
        return True  # Unknown types pass validation

    def _validate_constraints(
        self, field_name: str, value: Any, constraints: Dict[str, Any]
    ) -> List[ValidationError]:
        """Validate field constraints."""
        errors = []

        for constraint_name, constraint_value in constraints.items():
            if constraint_name == "validator":
                # Custom validator function
                validator = self._constraint_validators.get(constraint_value)
                if validator and not validator(value):
                    error_msg = constraints.get(
                        "error", f"Constraint '{constraint_value}' failed"
                    )
                    errors.append(
                        ValidationError(
                            field=field_name,
                            error_type=ValidationResult.CONSTRAINT_VIOLATION,
                            message=error_msg,
                        )
                    )
            elif constraint_name in self._constraint_validators:
                # Direct constraint validation
                validator = self._constraint_validators[constraint_name]
                if not validator(value, constraint_value):
                    errors.append(
                        ValidationError(
                            field=field_name,
                            error_type=ValidationResult.CONSTRAINT_VIOLATION,
                            message=f"Constraint '{constraint_name}' failed",
                        )
                    )

        return errors

    # Type validators
    def _validate_string(self, value: Any) -> bool:
        """Validate string type."""
        return isinstance(value, str)

    def _validate_integer(self, value: Any) -> bool:
        """Validate integer type."""
        return isinstance(value, int) and not isinstance(value, bool)

    def _validate_float(self, value: Any) -> bool:
        """Validate float type."""
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    def _validate_boolean(self, value: Any) -> bool:
        """Validate boolean type."""
        return isinstance(value, bool)

    def _validate_list(self, value: Any) -> bool:
        """Validate list type."""
        return isinstance(value, list)

    def _validate_dict(self, value: Any) -> bool:
        """Validate dictionary type."""
        return isinstance(value, dict)

    def _validate_optional_string(self, value: Any) -> bool:
        """Validate optional string type."""
        return value is None or isinstance(value, str)

    def _validate_optional_integer(self, value: Any) -> bool:
        """Validate optional integer type."""
        return value is None or (isinstance(value, int) and not isinstance(value, bool))

    def _validate_optional_list(self, value: Any) -> bool:
        """Validate optional list type."""
        return value is None or isinstance(value, list)

    def _validate_optional_dict(self, value: Any) -> bool:
        """Validate optional dictionary type."""
        return value is None or isinstance(value, dict)

    # Constraint validators
    def _validate_uuid_format(self, value: Any) -> bool:
        """Validate UUID format."""
        if not isinstance(value, str):
            return False
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            re.IGNORECASE,
        )
        return bool(uuid_pattern.match(value))

    def _validate_status_format(self, value: Any) -> bool:
        """Validate status format."""
        if not isinstance(value, str):
            return False
        valid_statuses = {"todo", "in_progress", "blocked", "done"}
        return value.lower() in valid_statuses

    def _validate_complexity_format(self, value: Any) -> bool:
        """Validate complexity format."""
        if not isinstance(value, str):
            return False
        valid_complexities = {"low", "medium", "high"}
        return value.lower() in valid_complexities

    def _validate_note_type_format(self, value: Any) -> bool:
        """Validate note type format."""
        if not isinstance(value, str):
            return False
        valid_types = {
            "user",
            "system",
            "status_change",
            "assignment",
            "progress",
            "dependency",
            "archive",
        }
        return value.lower() in valid_types

    def _validate_min_length(self, value: Any, min_length: int) -> bool:
        """Validate minimum length constraint."""
        if isinstance(value, str):
            return len(value) >= min_length
        elif isinstance(value, (list, dict)):
            return len(value) >= min_length
        return True

    def _validate_max_length(self, value: Any, max_length: int) -> bool:
        """Validate maximum length constraint."""
        if isinstance(value, str):
            return len(value) <= max_length
        elif isinstance(value, (list, dict)):
            return len(value) <= max_length
        return True

    def _validate_pattern(self, value: Any, pattern: str) -> bool:
        """Validate regex pattern constraint."""
        if not isinstance(value, str):
            return False
        return bool(re.match(pattern, value))

    def _validate_range(
        self, value: Any, range_spec: Dict[str, Union[int, float]]
    ) -> bool:
        """Validate numeric range constraint."""
        if not isinstance(value, (int, float)):
            return False

        min_val = range_spec.get("min")
        max_val = range_spec.get("max")

        if min_val is not None and value < min_val:
            return False
        if max_val is not None and value > max_val:
            return False

        return True


# Global schema validation engine instance
schema_validator = SchemaValidationEngine()
