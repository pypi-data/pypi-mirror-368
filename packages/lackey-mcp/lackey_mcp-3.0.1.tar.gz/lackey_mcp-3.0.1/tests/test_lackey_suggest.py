#!/usr/bin/env python3
"""Test script for lackey_suggest tool implementation."""

import os
import sys

# Add src to path before other imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
# flake8: noqa: E402

from lackey.mcp.lackey_suggest import lackey_suggest


def test_suggest_parameters() -> None:
    """Test parameter suggestions for a tool."""
    print("=== Testing Parameter Suggestions ===")

    # Test with create_task tool
    result = lackey_suggest.suggest_parameters("create_task")

    print(f"Tool: {result['tool_name']}")
    print(f"Gateway: {result['gateway']}")
    print(f"Missing Required: {result['missing_required']}")
    print()

    print("Parameter Suggestions:")
    for suggestion in result["parameter_suggestions"][:3]:  # Show first 3
        print(
            f"  • {suggestion['name']} ({suggestion['type']}, {'required' if suggestion['required'] else 'optional'})"
        )
        print(f"    Description: {suggestion['description']}")
        print(f"    Examples: {suggestion['examples']}")
        print()


def test_suggest_next_parameter() -> None:
    """Test next parameter suggestion."""
    print("=== Testing Next Parameter Suggestion ===")

    # Test with partial parameters
    current_params = {"project_id": "123e4567-e89b-12d3-a456-426614174000"}
    result = lackey_suggest.suggest_next_parameter("create_task", current_params)

    print(f"Next Parameter: {result.get('next_parameter')}")
    print(f"Priority: {result.get('priority')}")
    print(f"Completion: {result.get('completion_percentage')}%")

    if "suggestion" in result:
        suggestion = result["suggestion"]
        print(f"Type: {suggestion['type']}")
        print(f"Description: {suggestion['description']}")
        print(f"Examples: {suggestion['examples']}")
    print()


def test_analyze_parameter_structure() -> None:
    """Test parameter structure analysis."""
    print("=== Testing Parameter Structure Analysis ===")

    result = lackey_suggest.analyze_parameter_structure("update_task_status")

    print(f"Tool: {result['tool_name']}")
    print(f"Gateway: {result['gateway']}")
    print(f"Parameter Count: {result['parameter_count']}")
    print(f"Parameter Types: {result['parameter_types']}")
    print(f"Complexity Score: {result['complexity_score']:.2f}")

    if result["parameter_groups"]:
        print(f"Parameter Groups: {result['parameter_groups']}")
    print()


def test_partial_parameter_completion() -> None:
    """Test completion suggestions for partial parameters."""
    print("=== Testing Partial Parameter Completion ===")

    # Test with partial UUID
    partial_params = {"project_id": "d1e10785"}
    result = lackey_suggest.suggest_parameters("create_task", partial_params)

    print("Completion Suggestions:")
    for completion in result["completion_suggestions"]:
        print(f"  • {completion['parameter']}: {completion['suggested_value']}")
        print(f"    Confidence: {completion['confidence']}")
        print(f"    Reasoning: {completion['reasoning']}")
    print()


def test_parameter_relationships() -> None:
    """Test parameter relationship analysis."""
    print("=== Testing Parameter Relationships ===")

    result = lackey_suggest.suggest_parameters("add_task_dependencies")

    print("Parameter Relationships:")
    for param, related in result["parameter_relationships"].items():
        print(f"  • {param} → {related}")
    print()

    print("Usage Examples:")
    for i, example in enumerate(result["usage_examples"], 1):
        print(f"  Example {i}: {example['description']}")
        print(f"    Parameters: {example['parameters']}")
    print()


def test_error_handling() -> None:
    """Test error handling for invalid tools."""
    print("=== Testing Error Handling ===")

    result = lackey_suggest.suggest_parameters("nonexistent_tool")

    if "error" in result:
        print(f"Error handled correctly: {result['error']}")
    else:
        print("Error handling failed!")
    print()


if __name__ == "__main__":
    test_suggest_parameters()
    test_suggest_next_parameter()
    test_analyze_parameter_structure()
    test_partial_parameter_completion()
    test_parameter_relationships()
    test_error_handling()
    print("✅ All lackey_suggest tests completed!")
