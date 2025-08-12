"""Test Tier 1 error response implementation."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
# flake8: noqa: E402
# Add src to path before other imports

from lackey.mcp.tier1_errors import (
    Tier1ErrorGenerator,
    generate_tier1_error_response,
    validate_required_parameters,
)


def test_missing_parameters() -> None:
    """Test missing required parameters error."""
    schema = {
        "required": ["project_id", "task_id"],
        "types": {"project_id": "uuid", "task_id": "uuid"},
    }

    parameters = {"project_id": "123"}  # Missing task_id

    missing = validate_required_parameters(parameters, schema)
    assert missing == ["task_id"]

    error_msg = generate_tier1_error_response(
        "update_task", "missing_parameters", parameters, schema
    )

    print("Missing parameter error:")
    print(error_msg)
    assert "task_id" in error_msg
    assert "id" in error_msg  # Type hint


def test_tier1_generator() -> None:
    """Test Tier 1 error generator."""
    generator = Tier1ErrorGenerator()

    schema = {
        "required": ["name", "status"],
        "types": {"name": "string", "status": "string"},
    }

    error = generator.generate_missing_parameter_error(
        "create_task", ["name", "status"], schema
    )

    print("\nTier 1 error response:")
    print(error.to_dict())

    assert error.error_type == "missing_parameters"
    assert "name" in error.missing_required
    assert "status" in error.missing_required
    assert error.parameter_hints["name"] == "text"


if __name__ == "__main__":
    test_missing_parameters()
    test_tier1_generator()
    print("\n✅ All Tier 1 error tests passed!")
