"""Tests for schema validation engine."""

from typing import Any

from lackey.schema_validation import (
    SchemaField,
    SchemaValidationEngine,
    ValidationError,
    ValidationResult,
    schema_validator,
)


class TestSchemaValidationEngine:
    """Test cases for SchemaValidationEngine."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.engine = SchemaValidationEngine()

        # Sample schema for testing
        self.sample_schema = {
            "required": ["task_id", "title"],
            "optional": {"description": None, "tags": None},
            "types": {
                "task_id": "str",
                "title": "str",
                "description": "optional[str]",
                "tags": "optional[list]",
            },
            "constraints": {
                "task_id": {
                    "validator": "validate_uuid",
                    "error": "task_id must be a valid UUID",
                },
                "title": {"min_length": 1, "max_length": 200},
            },
        }

    def test_validate_parameters_valid_required_only(self) -> None:
        """Test validation with only required parameters."""
        parameters = {
            "task_id": "12345678-1234-1234-1234-123456789abc",
            "title": "Test Task",
        }

        errors = self.engine.validate_parameters(parameters, self.sample_schema)
        assert len(errors) == 0

    def test_validate_parameters_valid_with_optional(self) -> None:
        """Test validation with required and optional parameters."""
        parameters = {
            "task_id": "12345678-1234-1234-1234-123456789abc",
            "title": "Test Task",
            "description": "Test description",
            "tags": ["tag1", "tag2"],
        }

        errors = self.engine.validate_parameters(parameters, self.sample_schema)
        assert len(errors) == 0

    def test_validate_parameters_missing_required(self) -> None:
        """Test validation with missing required field."""
        parameters = {"title": "Test Task"}

        errors = self.engine.validate_parameters(parameters, self.sample_schema)
        assert len(errors) == 1
        assert errors[0].error_type == ValidationResult.MISSING_REQUIRED
        assert errors[0].field == "task_id"

    def test_validate_parameters_invalid_uuid(self) -> None:
        """Test validation with invalid UUID format."""
        parameters = {"task_id": "invalid-uuid", "title": "Test Task"}

        errors = self.engine.validate_parameters(parameters, self.sample_schema)
        assert len(errors) == 1
        assert errors[0].error_type == ValidationResult.CONSTRAINT_VIOLATION
        assert "UUID" in errors[0].message

    def test_validate_parameters_unexpected_field(self) -> None:
        """Test validation with unexpected field."""
        parameters = {
            "task_id": "12345678-1234-1234-1234-123456789abc",
            "title": "Test Task",
            "unexpected_field": "value",
        }

        errors = self.engine.validate_parameters(parameters, self.sample_schema)
        assert len(errors) == 1
        assert errors[0].error_type == ValidationResult.INVALID
        assert "unexpected_field" in errors[0].message

    def test_validate_parameters_type_mismatch(self) -> None:
        """Test validation with type mismatch."""
        parameters = {
            "task_id": "12345678-1234-1234-1234-123456789abc",
            "title": 123,  # Should be string
        }

        errors = self.engine.validate_parameters(parameters, self.sample_schema)
        assert len(errors) == 1
        assert errors[0].error_type == ValidationResult.TYPE_MISMATCH
        assert errors[0].field == "title"

    def test_validate_nested_structure_valid(self) -> None:
        """Test nested structure validation with valid data."""
        schema = {
            "user": SchemaField(
                name="user",
                field_type="dict",
                required=True,
                nested_schema={
                    "name": SchemaField(name="name", field_type="str", required=True),
                    "email": SchemaField(
                        name="email", field_type="str", required=False
                    ),
                },
            )
        }

        data = {"user": {"name": "John Doe", "email": "john@example.com"}}

        errors = self.engine.validate_nested_structure(data, schema)
        assert len(errors) == 0

    def test_validate_nested_structure_missing_required(self) -> None:
        """Test nested structure validation with missing required field."""
        schema = {
            "user": SchemaField(
                name="user",
                field_type="dict",
                required=True,
                nested_schema={
                    "name": SchemaField(name="name", field_type="str", required=True),
                    "email": SchemaField(
                        name="email", field_type="str", required=False
                    ),
                },
            )
        }

        data = {"user": {"email": "john@example.com"}}

        errors = self.engine.validate_nested_structure(data, schema)
        assert len(errors) == 1
        assert errors[0].error_type == ValidationResult.MISSING_REQUIRED
        assert "name" in errors[0].field

    def test_type_validators(self) -> None:
        """Test individual type validators."""
        # String validation
        assert self.engine._validate_string("test") is True
        assert self.engine._validate_string(123) is False

        # Integer validation
        assert self.engine._validate_integer(123) is True
        assert self.engine._validate_integer(123.5) is False
        assert self.engine._validate_integer(True) is False  # bool is not int

        # Float validation
        assert self.engine._validate_float(123.5) is True
        assert self.engine._validate_float(123) is True
        assert self.engine._validate_float("123") is False

        # Boolean validation
        assert self.engine._validate_boolean(True) is True
        assert self.engine._validate_boolean(False) is True
        assert self.engine._validate_boolean(1) is False

        # List validation
        assert self.engine._validate_list([1, 2, 3]) is True
        assert self.engine._validate_list("not a list") is False

        # Dict validation
        assert self.engine._validate_dict({"key": "value"}) is True
        assert self.engine._validate_dict("not a dict") is False

    def test_optional_type_validators(self) -> None:
        """Test optional type validators."""
        # Optional string
        assert self.engine._validate_optional_string(None) is True
        assert self.engine._validate_optional_string("test") is True
        assert self.engine._validate_optional_string(123) is False

        # Optional integer
        assert self.engine._validate_optional_integer(None) is True
        assert self.engine._validate_optional_integer(123) is True
        assert self.engine._validate_optional_integer("123") is False

        # Optional list
        assert self.engine._validate_optional_list(None) is True
        assert self.engine._validate_optional_list([1, 2, 3]) is True
        assert self.engine._validate_optional_list("not a list") is False

    def test_constraint_validators(self) -> None:
        """Test constraint validators."""
        # UUID validation
        valid_uuid = "12345678-1234-1234-1234-123456789abc"
        invalid_uuid = "not-a-uuid"
        assert self.engine._validate_uuid_format(valid_uuid) is True
        assert self.engine._validate_uuid_format(invalid_uuid) is False

        # Status validation
        assert self.engine._validate_status_format("todo") is True
        assert self.engine._validate_status_format("in_progress") is True
        assert self.engine._validate_status_format("invalid_status") is False

        # Complexity validation
        assert self.engine._validate_complexity_format("low") is True
        assert self.engine._validate_complexity_format("medium") is True
        assert self.engine._validate_complexity_format("invalid") is False

        # Length validation
        assert self.engine._validate_min_length("test", 3) is True
        assert self.engine._validate_min_length("te", 3) is False
        assert self.engine._validate_max_length("test", 5) is True
        assert self.engine._validate_max_length("toolong", 5) is False

        # Pattern validation
        assert self.engine._validate_pattern("test123", r"^[a-z0-9]+$") is True
        assert self.engine._validate_pattern("Test123", r"^[a-z0-9]+$") is False

        # Range validation
        range_spec = {"min": 1, "max": 10}
        assert self.engine._validate_range(5, range_spec) is True
        assert self.engine._validate_range(0, range_spec) is False
        assert self.engine._validate_range(11, range_spec) is False

    def test_complex_validation_scenario(self) -> None:
        """Test complex validation scenario with multiple error types."""
        complex_schema = {
            "required": ["id", "name", "config"],
            "optional": {"metadata": None},
            "types": {
                "id": "str",
                "name": "str",
                "config": "dict",
                "metadata": "optional[dict]",
            },
            "constraints": {
                "id": {"validator": "validate_uuid"},
                "name": {"min_length": 1, "max_length": 50},
                "config": {"min_length": 1},
            },
        }

        # Invalid parameters with multiple errors
        parameters = {
            "id": "invalid-uuid",  # Constraint violation
            "name": "",  # Length constraint violation
            "config": {},  # Length constraint violation
            "extra_field": "value",  # Unexpected field
            # Missing required field would be another error
        }

        errors = self.engine.validate_parameters(parameters, complex_schema)
        assert len(errors) >= 3  # At least 3 different types of errors

    def test_global_validator_instance(self) -> None:
        """Test that global validator instance works correctly."""
        parameters = {
            "task_id": "12345678-1234-1234-1234-123456789abc",
            "title": "Test Task",
        }

        errors = schema_validator.validate_parameters(parameters, self.sample_schema)
        assert len(errors) == 0

    def test_validation_error_dataclass(self) -> None:
        """Test ValidationError dataclass functionality."""
        error = ValidationError(
            field="test_field",
            error_type=ValidationResult.TYPE_MISMATCH,
            message="Test error message",
            path="root.nested",
        )

        assert error.field == "test_field"
        assert error.error_type == ValidationResult.TYPE_MISMATCH
        assert error.message == "Test error message"
        assert error.path == "root.nested"

    def test_schema_field_dataclass(self) -> None:
        """Test SchemaField dataclass functionality."""
        field = SchemaField(
            name="test_field",
            field_type="str",
            required=True,
            constraints={"min_length": 1},
        )

        assert field.name == "test_field"
        assert field.field_type == "str"
        assert field.required is True
        assert field.constraints == {"min_length": 1}
        assert field.nested_schema is None

    def test_empty_schema_validation(self) -> None:
        """Test validation with empty schema."""
        empty_schema: dict[str, Any] = {
            "required": [],
            "optional": {},
            "types": {},
            "constraints": {},
        }

        parameters = {"any_field": "any_value"}
        errors = self.engine.validate_parameters(parameters, empty_schema)

        # Should have error for unexpected field
        assert len(errors) == 1
        assert errors[0].error_type == ValidationResult.INVALID

    def test_note_type_validation(self) -> None:
        """Test note type validation."""
        valid_types = [
            "user",
            "system",
            "status_change",
            "assignment",
            "progress",
            "dependency",
            "archive",
        ]

        for note_type in valid_types:
            assert self.engine._validate_note_type_format(note_type) is True

        assert self.engine._validate_note_type_format("invalid_type") is False
        assert self.engine._validate_note_type_format(123) is False

    def test_edge_cases(self) -> None:
        """Test edge cases and boundary conditions."""
        # Test with None values
        assert self.engine._validate_type(None, "optional[str]") is True
        assert self.engine._validate_type(None, "str") is False

        # Test with empty strings
        assert self.engine._validate_min_length("", 1) is False
        assert self.engine._validate_max_length("", 0) is True

        # Test with empty collections
        assert self.engine._validate_min_length([], 1) is False
        assert self.engine._validate_min_length({}, 1) is False

        # Test unknown type validation
        assert self.engine._validate_type("any_value", "unknown_type") is True
