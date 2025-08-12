#!/usr/bin/env python3
"""Test script for Tier 2 error response implementation."""

import os
import sys
from typing import Any, Dict

# Add src to path before other imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
# flake8: noqa: E402

from lackey.mcp.error_handling import ErrorMessageGenerator
from lackey.mcp.tier2_errors import generate_tier2_error_response


def test_missing_parameters() -> None:
    """Test Tier 2 error response for missing parameters."""
    print("=== Testing Missing Parameters ===")

    schema = {
        "required": ["task_id", "project_id"],
        "properties": {
            "task_id": {
                "type": "string",
                "description": "Unique identifier for the task",
            },
            "project_id": {
                "type": "string",
                "description": "Unique identifier for the project",
            },
            "status": {
                "type": "string",
                "description": "New status for the task",
                "enum": ["todo", "in_progress", "done"],
                "default": "todo",
            },
            "priority": {
                "type": "integer",
                "description": "Task priority level",
                "minimum": 1,
                "maximum": 5,
                "default": 3,
            },
        },
    }

    parameters = {"status": "in_progress"}  # Missing required params

    response = generate_tier2_error_response(
        "update_task", "missing_parameters", parameters, schema
    )

    print(response)
    print()


def test_invalid_parameter() -> None:
    """Test Tier 2 error response for invalid parameter."""
    print("=== Testing Invalid Parameter ===")

    schema = {
        "required": ["priority"],
        "properties": {
            "priority": {
                "type": "integer",
                "description": "Task priority level (1-5)",
                "minimum": 1,
                "maximum": 5,
            }
        },
    }

    parameters = {"priority": 10}  # Invalid value (too high)

    response = generate_tier2_error_response(
        "set_priority",
        "invalid_parameter",
        parameters,
        schema,
        invalid_param="priority",
        invalid_value=10,
    )

    print(response)
    print()


def test_type_mismatch() -> None:
    """Test Tier 2 error response for type mismatch."""
    print("=== Testing Type Mismatch ===")

    schema = {
        "required": ["count"],
        "properties": {
            "count": {"type": "integer", "description": "Number of items to process"}
        },
    }

    parameters = {"count": "five"}  # String instead of integer

    response = generate_tier2_error_response(
        "process_items",
        "type_mismatch",
        parameters,
        schema,
        invalid_param="count",
        invalid_value="five",
    )

    print(response)
    print()


def test_error_message_generator() -> None:
    """Test the ErrorMessageGenerator with Tier 2 support."""
    print("=== Testing ErrorMessageGenerator Tier 2 ===")

    generator = ErrorMessageGenerator()

    schema = {
        "required": ["name"],
        "properties": {
            "name": {
                "type": "string",
                "description": "User's full name",
                "minLength": 2,
                "maxLength": 50,
            },
            "email": {
                "type": "string",
                "description": "User's email address",
                "format": "email",
            },
        },
    }

    parameters: Dict[str, Any] = {}  # Missing required name

    response = generator.generate_tier2_validation_error(
        "create_user", parameters, schema
    )

    print(response)
    print()


if __name__ == "__main__":
    test_missing_parameters()
    test_invalid_parameter()
    test_type_mismatch()
    test_error_message_generator()
    print("✅ All Tier 2 error response tests completed!")
