#!/usr/bin/env python3
"""Test script for lackey_validate tool implementation."""

import os
import sys

# Add src to path before other imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
# flake8: noqa: E402

from lackey.mcp.lackey_validate import lackey_validate


def test_validate_parameters_valid() -> None:
    """Test parameter validation with valid parameters."""
    print("=== Testing Valid Parameters ===")

    # Test with valid create_task parameters
    parameters = {
        "project_id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Test Task",
        "objective": "Complete testing",
    }

    result = lackey_validate.validate_parameters("create_task", parameters)

    print(f"Tool: {result['tool_name']}")
    print(f"Valid: {result['valid']}")
    print(f"Validation Score: {result['validation_score']:.2f}")
    print(f"Issues: {len(result['issues'])}")
    print()


def test_validate_parameters_invalid() -> None:
    """Test parameter validation with invalid parameters."""
    print("=== Testing Invalid Parameters ===")

    # Test with missing required and invalid types
    parameters = {
        "project_id": "invalid-uuid",  # Invalid UUID
        "title": "",  # Too short
        "complexity": "extreme",  # Invalid enum value
    }

    result = lackey_validate.validate_parameters("create_task", parameters)

    print(f"Tool: {result['tool_name']}")
    print(f"Valid: {result['valid']}")
    print(f"Validation Score: {result['validation_score']:.2f}")
    print(f"Missing Required: {result['missing_required']}")

    print("Issues:")
    for issue in result["issues"][:3]:  # Show first 3 issues
        print(f"  • {issue['parameter']} ({issue['severity']}): {issue['message']}")
        if issue["suggestion"]:
            print(f"    Suggestion: {issue['suggestion']}")
    print()


def test_validate_structure() -> None:
    """Test structure validation."""
    print("=== Testing Structure Validation ===")

    # Test with parameter relationship issues
    parameters = {
        "task_id": "123e4567-e89b-12d3-a456-426614174000",
        # Missing project_id - relationship issue
        "new_status": "in_progress",
    }

    result = lackey_validate.validate_structure("update_task_status", parameters)

    print(f"Tool: {result['tool_name']}")
    print(f"Structure Valid: {result['structure_valid']}")
    print(f"Parameter Count: {result['parameter_count']}")

    if result["structure_issues"]:
        print("Structure Issues:")
        for issue in result["structure_issues"]:
            print(f"  • {issue['parameter']}: {issue['message']}")

    print(f"Relationship Analysis: {result['relationship_analysis']}")
    print()


def test_validation_guidance() -> None:
    """Test comprehensive validation guidance."""
    print("=== Testing Validation Guidance ===")

    # Test with multiple issues
    parameters = {
        "project_id": "short",  # Invalid UUID
        "title": "x",  # Too short
        "unexpected_param": "value",  # Unexpected parameter
    }

    result = lackey_validate.get_validation_guidance("create_task", parameters)

    print(f"Tool: {result['tool_name']}")
    print(f"Validation Summary: {result['validation_summary']}")

    print("Guidance:")
    for guidance in result["guidance"]:
        print(f"  • {guidance}")

    print("Next Steps:")
    for step in result["next_steps"]:
        print(f"  {step}")

    print("Fix Examples:")
    for example in result["examples"]:
        print(f"  • {example['parameter']}: {example['problem']}")
        print(f"    Fix: {example['fix']}")
        print(f"    Example: {example['example']}")
    print()


def test_constraint_validation() -> None:
    """Test constraint validation."""
    print("=== Testing Constraint Validation ===")

    # Test with various constraint violations
    parameters = {
        "project_id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "x" * 250,  # Too long
        "objective": "Test",
        "complexity": "invalid",  # Invalid enum
    }

    result = lackey_validate.validate_parameters("create_task", parameters)

    print(f"Validation Score: {result['validation_score']:.2f}")

    print("Constraint Issues:")
    for issue in result["issues"]:
        if issue["severity"] == "error":
            print(f"  • {issue['parameter']}: {issue['message']}")
            print(f"    Expected: {issue['expected']}")
            print(f"    Actual: {issue['actual']}")
    print()


def test_error_handling() -> None:
    """Test error handling for invalid tools."""
    print("=== Testing Error Handling ===")

    result = lackey_validate.validate_parameters("nonexistent_tool", {})

    if "error" in result:
        print(f"Error handled correctly: {result['error']}")
    else:
        print("Error handling failed!")
    print()


if __name__ == "__main__":
    test_validate_parameters_valid()
    test_validate_parameters_invalid()
    test_validate_structure()
    test_validation_guidance()
    test_constraint_validation()
    test_error_handling()
    print("✅ All lackey_validate tests completed!")
