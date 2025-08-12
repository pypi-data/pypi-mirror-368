#!/usr/bin/env python3
"""Test script for gateway schema definitions."""

import os
import sys

# Add src to path before other imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
# flake8: noqa: E402

from lackey.mcp.gateway_schema_definitions import (
    LACKEY_DO_GATEWAY_DOCUMENTATION,
    LackeyDoGatewaySchemas,
    SchemaRelationshipMapper,
)


def test_schema_documentation() -> None:
    """Test the complete schema documentation."""
    print("=== Testing Gateway Schema Documentation ===")

    doc = LACKEY_DO_GATEWAY_DOCUMENTATION

    print(f"Gateway: {doc['gateway_name']}")
    print(f"Description: {doc['description']}")
    print(f"Total Actions: {doc['total_actions']}")
    print()

    # Test action schemas
    print("Available Actions:")
    for action_name in doc["action_schemas"].keys():
        print(f"  • {action_name}")
    print()

    # Test parameter relationships
    print("Parameter Relationships:")
    for param, relationships in doc["parameter_relationships"].items():
        print(f"  • {param}: {list(relationships.keys())}")
    print()


def test_project_management_schemas() -> None:
    """Test project management schemas."""
    print("=== Testing Project Management Schemas ===")

    schemas = LackeyDoGatewaySchemas.get_project_management_schemas()

    for schema in schemas:
        print(f"Action: {schema.action_name}")
        print(f"Description: {schema.description}")
        print("Parameters:")
        for param in schema.parameters:
            required = "required" if param.required else "optional"
            print(
                f"  • {param.name} ({param.type.value}, {required}): {param.description}"
            )
        print()


def test_task_management_schemas() -> None:
    """Test task management schemas."""
    print("=== Testing Task Management Schemas ===")

    schemas = LackeyDoGatewaySchemas.get_task_management_schemas()

    for schema in schemas[:2]:  # Show first 2 for brevity
        print(f"Action: {schema.action_name}")
        print("Required Parameters:")
        for param in schema.parameters:
            if param.required:
                print(f"  • {param.name}: {param.description}")
        print("Optional Parameters:")
        for param in schema.parameters:
            if not param.required:
                print(f"  • {param.name}: {param.description}")
        print()


def test_parameter_combinations() -> None:
    """Test parameter combination mappings."""
    print("=== Testing Parameter Combinations ===")

    mapper = SchemaRelationshipMapper()
    combinations = mapper.get_required_parameter_combinations()

    for action, combos in combinations.items():
        print(f"Action: {action}")
        for i, combo in enumerate(combos, 1):
            print(f"  Combination {i}: {', '.join(combo)}")
        print()


def test_validation_summary() -> None:
    """Test validation summary."""
    print("=== Testing Validation Summary ===")

    doc = LACKEY_DO_GATEWAY_DOCUMENTATION
    validation = doc["validation_summary"]

    for category, params in validation.items():
        print(f"{category.replace('_', ' ').title()}: {', '.join(params)}")
    print()


if __name__ == "__main__":
    test_schema_documentation()
    test_project_management_schemas()
    test_task_management_schemas()
    test_parameter_combinations()
    test_validation_summary()
    print("✅ All gateway schema tests completed!")
