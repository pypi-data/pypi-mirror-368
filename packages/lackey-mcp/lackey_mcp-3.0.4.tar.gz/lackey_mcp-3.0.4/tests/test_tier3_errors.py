#!/usr/bin/env python3
"""Test script for Tier 3 error response implementation."""

import os
import sys
from typing import Any, Dict

# Add src to path before other imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
# flake8: noqa: E402

from lackey.mcp.error_handling import ErrorMessageGenerator
from lackey.mcp.tier3_errors import Tier3ErrorGenerator, generate_tier3_error_response


def test_missing_parameters_tier3() -> None:
    """Test Tier 3 error response for missing parameters."""
    print("=== Testing Tier 3 Missing Parameters ===")

    schema = {
        "required": ["project_id", "title", "objective"],
        "optional": {"complexity": "medium", "tags": None},
        "properties": {
            "project_id": {"description": "Unique project identifier"},
            "title": {"description": "Task title"},
            "objective": {"description": "Task objective"},
            "complexity": {"description": "Task complexity level"},
            "tags": {"description": "Task tags"},
        },
        "types": {
            "project_id": "str",
            "title": "str",
            "objective": "str",
            "complexity": "enum",
            "tags": "optional[list]",
        },
        "constraints": {
            "project_id": {"validator": "validate_uuid"},
            "complexity": {"allowed_values": ["low", "medium", "high"]},
        },
    }

    parameters = {"complexity": "medium"}  # Missing required params

    response = generate_tier3_error_response(
        "create_task", "missing_parameters", parameters, schema
    )

    print(response)
    print()


def test_invalid_parameter_tier3() -> None:
    """Test Tier 3 error response for invalid parameter."""
    print("=== Testing Tier 3 Invalid Parameter ===")

    schema = {
        "required": ["project_id"],
        "properties": {"project_id": {"description": "Valid UUID format required"}},
        "types": {"project_id": "str"},
        "constraints": {"project_id": {"validator": "validate_uuid"}},
    }

    parameters = {"project_id": "invalid-uuid-format"}

    response = generate_tier3_error_response(
        "get_project",
        "invalid_parameter",
        parameters,
        schema,
        invalid_param="project_id",
        invalid_value="invalid-uuid-format",
    )

    print(response)
    print()


def test_structure_error_tier3() -> None:
    """Test Tier 3 error response for structure issues."""
    print("=== Testing Tier 3 Structure Error ===")

    schema = {
        "required": ["project_id", "task_id", "new_status"],
        "properties": {
            "project_id": {"description": "Project containing the task"},
            "task_id": {"description": "Task to update"},
            "new_status": {"description": "New status value"},
        },
        "types": {"project_id": "str", "task_id": "str", "new_status": "enum"},
        "constraints": {
            "project_id": {"validator": "validate_uuid"},
            "task_id": {"validator": "validate_uuid"},
            "new_status": {"allowed_values": ["todo", "in_progress", "done"]},
        },
    }

    parameters = {"task_id": "123e4567-e89b-12d3-a456-426614174000"}
    structure_issues = [
        "missing project_id context",
        "incomplete parameter combination",
    ]

    response = generate_tier3_error_response(
        "update_task_status",
        "structure_error",
        parameters,
        schema,
        structure_issues=structure_issues,
    )

    print(response)
    print()


def test_tier3_generator_direct() -> None:
    """Test Tier3ErrorGenerator directly."""
    print("=== Testing Tier3ErrorGenerator Direct ===")

    generator = Tier3ErrorGenerator()

    schema = {
        "required": ["name"],
        "optional": {"email": None, "age": None},
        "properties": {
            "name": {"description": "User's full name"},
            "email": {"description": "User's email address"},
            "age": {"description": "User's age"},
        },
        "types": {"name": "str", "email": "optional[str]", "age": "optional[int]"},
        "constraints": {
            "name": {"min_length": 2, "max_length": 50},
            "age": {"minimum": 0, "maximum": 150},
        },
    }

    result = generator.generate_missing_parameter_error("create_user", ["name"], schema)

    print(f"Error Type: {result.error_type}")
    print(f"Message: {result.message}")
    print(f"Missing Required: {result.missing_required}")

    print("\nSchema Examples:")
    for example in result.schema_examples:
        print(f"  • {example.description}: {example.parameters}")
        print(f"    → {example.explanation}")

    print("\nParameter Dependencies:")
    for dep in result.parameter_dependencies:
        print(f"  • {dep.parameter}: {dep.description}")

    print(f"\nComplete Schema Keys: {list(result.complete_schema.keys())}")
    print()


def test_error_message_generator_tier3() -> None:
    """Test ErrorMessageGenerator with Tier 3 support."""
    print("=== Testing ErrorMessageGenerator Tier 3 ===")

    generator = ErrorMessageGenerator()

    schema = {
        "required": ["tool_name", "parameters"],
        "properties": {
            "tool_name": {"description": "Name of the tool to validate"},
            "parameters": {"description": "Parameters to validate"},
        },
        "types": {"tool_name": "str", "parameters": "dict"},
        "constraints": {"tool_name": {"min_length": 1}},
    }

    parameters: Dict[str, Any] = {}  # Missing required parameters

    response = generator.generate_tier3_validation_error(
        "validate_parameters", parameters, schema
    )

    print(response)
    print()


if __name__ == "__main__":
    test_missing_parameters_tier3()
    test_invalid_parameter_tier3()
    test_structure_error_tier3()
    test_tier3_generator_direct()
    test_error_message_generator_tier3()
    print("✅ All Tier 3 error response tests completed!")
