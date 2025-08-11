"""Comprehensive gateway schema definitions and documentation.

This module provides detailed documentation of all gateway schemas, parameter
structures, relationships, and validation rules for the Lackey MCP system.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class ParameterType(Enum):
    """Parameter type classifications."""

    STRING = "str"
    INTEGER = "int"
    BOOLEAN = "bool"
    LIST = "list"
    DICT = "dict"
    UUID = "uuid"
    ENUM = "enum"
    OPTIONAL = "optional"


class ValidationRule(Enum):
    """Validation rule types."""

    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    PATTERN = "pattern"
    ENUM_VALUES = "enum_values"
    UUID_FORMAT = "uuid_format"
    SANITIZE = "sanitize"


@dataclass
class ParameterDefinition:
    """Complete parameter definition with validation and relationships."""

    name: str
    type: ParameterType
    required: bool
    description: str
    default: Optional[Any] = None
    validation_rules: Optional[Dict[ValidationRule, Any]] = None
    relationships: Optional[List[str]] = None
    examples: Optional[List[str]] = None


@dataclass
class ActionSchema:
    """Complete action schema definition."""

    action_name: str
    description: str
    gateway: str
    parameters: List[ParameterDefinition]
    parameter_combinations: Optional[List[List[str]]] = None
    success_criteria: Optional[List[str]] = None
    error_conditions: Optional[List[str]] = None


class LackeyDoGatewaySchemas:
    """Complete schema definitions for LackeyDoGateway actions."""

    @staticmethod
    def get_project_management_schemas() -> List[ActionSchema]:
        """Get project management action schemas."""
        return [
            ActionSchema(
                action_name="create_project",
                description="Create a new project with specified parameters",
                gateway="lackey_do",
                parameters=[
                    ParameterDefinition(
                        name="friendly_name",
                        type=ParameterType.STRING,
                        required=True,
                        description="Human-readable project name",
                        validation_rules={
                            ValidationRule.MIN_LENGTH: 1,
                            ValidationRule.MAX_LENGTH: 200,
                            ValidationRule.SANITIZE: True,
                        },
                        examples=["Web Development Project", "Data Analysis Task"],
                    ),
                    ParameterDefinition(
                        name="description",
                        type=ParameterType.OPTIONAL,
                        required=False,
                        description="Detailed project description",
                        validation_rules={
                            ValidationRule.MAX_LENGTH: 2000,
                            ValidationRule.SANITIZE: True,
                        },
                        examples=["A comprehensive web development project"],
                    ),
                    ParameterDefinition(
                        name="objectives",
                        type=ParameterType.OPTIONAL,
                        required=False,
                        description="Project objectives and goals",
                        validation_rules={
                            ValidationRule.MAX_LENGTH: 1000,
                            ValidationRule.SANITIZE: True,
                        },
                    ),
                    ParameterDefinition(
                        name="tags",
                        type=ParameterType.OPTIONAL,
                        required=False,
                        description="Project tags for categorization",
                        validation_rules={
                            ValidationRule.MAX_LENGTH: 500,
                            ValidationRule.SANITIZE: True,
                        },
                        examples=["web,development,frontend"],
                    ),
                ],
                success_criteria=[
                    "Project created with unique ID",
                    "All parameters validated",
                ],
                error_conditions=["Invalid friendly_name", "Description too long"],
            ),
            ActionSchema(
                action_name="update_project",
                description="Update existing project properties",
                gateway="lackey_do",
                parameters=[
                    ParameterDefinition(
                        name="project_id",
                        type=ParameterType.UUID,
                        required=True,
                        description="Unique project identifier",
                        validation_rules={ValidationRule.UUID_FORMAT: True},
                        examples=["d1e10785-84bd-42f7-9e2e-536496c4509a"],
                    ),
                    ParameterDefinition(
                        name="friendly_name",
                        type=ParameterType.OPTIONAL,
                        required=False,
                        description="Updated project name",
                        validation_rules={
                            ValidationRule.MIN_LENGTH: 1,
                            ValidationRule.MAX_LENGTH: 200,
                            ValidationRule.SANITIZE: True,
                        },
                    ),
                    ParameterDefinition(
                        name="status",
                        type=ParameterType.ENUM,
                        required=False,
                        description="Project status",
                        validation_rules={
                            ValidationRule.ENUM_VALUES: ["active", "done", "archived"]
                        },
                    ),
                ],
                parameter_combinations=[
                    ["project_id", "friendly_name"],
                    ["project_id", "status"],
                ],
                success_criteria=["Project updated successfully", "Changes persisted"],
                error_conditions=["Project not found", "Invalid status value"],
            ),
            ActionSchema(
                action_name="delete_project",
                description="Permanently delete a project and all its tasks",
                gateway="lackey_do",
                parameters=[
                    ParameterDefinition(
                        name="project_id",
                        type=ParameterType.UUID,
                        required=True,
                        description="Unique project identifier to delete",
                        validation_rules={ValidationRule.UUID_FORMAT: True},
                    )
                ],
                success_criteria=[
                    "Project and all tasks deleted",
                    "Dependencies cleaned up",
                ],
                error_conditions=[
                    "Project not found",
                    "Project has active dependencies",
                ],
            ),
        ]

    @staticmethod
    def get_task_management_schemas() -> List[ActionSchema]:
        """Get task management action schemas."""
        return [
            ActionSchema(
                action_name="create_task",
                description="Create a new task within a project",
                gateway="lackey_do",
                parameters=[
                    ParameterDefinition(
                        name="project_id",
                        type=ParameterType.UUID,
                        required=True,
                        description="Parent project identifier",
                        validation_rules={ValidationRule.UUID_FORMAT: True},
                        relationships=["Must reference existing project"],
                    ),
                    ParameterDefinition(
                        name="title",
                        type=ParameterType.STRING,
                        required=True,
                        description="Task title or summary",
                        validation_rules={
                            ValidationRule.MIN_LENGTH: 1,
                            ValidationRule.MAX_LENGTH: 200,
                            ValidationRule.SANITIZE: True,
                        },
                        examples=[
                            "Implement user authentication",
                            "Fix database connection",
                        ],
                    ),
                    ParameterDefinition(
                        name="objective",
                        type=ParameterType.STRING,
                        required=True,
                        description="Detailed task objective and requirements",
                        validation_rules={
                            ValidationRule.MIN_LENGTH: 1,
                            ValidationRule.MAX_LENGTH: 1000,
                            ValidationRule.SANITIZE: True,
                        },
                    ),
                    ParameterDefinition(
                        name="steps",
                        type=ParameterType.LIST,
                        required=False,
                        description="List of task steps to complete",
                        default=["Complete the task"],
                        validation_rules={
                            ValidationRule.MIN_VALUE: 1,
                            ValidationRule.MAX_VALUE: 50,
                        },
                    ),
                    ParameterDefinition(
                        name="success_criteria",
                        type=ParameterType.LIST,
                        required=False,
                        description="Criteria for task completion",
                        default=["Task completed successfully"],
                        validation_rules={
                            ValidationRule.MIN_VALUE: 1,
                            ValidationRule.MAX_VALUE: 20,
                        },
                    ),
                    ParameterDefinition(
                        name="complexity",
                        type=ParameterType.ENUM,
                        required=False,
                        description="Task complexity level",
                        default="medium",
                        validation_rules={
                            ValidationRule.ENUM_VALUES: ["low", "medium", "high"]
                        },
                    ),
                    ParameterDefinition(
                        name="dependencies",
                        type=ParameterType.LIST,
                        required=False,
                        description="List of task IDs this task depends on",
                        relationships=[
                            "Must reference existing tasks",
                            "Cannot create cycles",
                        ],
                    ),
                ],
                parameter_combinations=[
                    ["project_id", "title", "objective"],
                    ["project_id", "title", "objective", "complexity"],
                    ["project_id", "title", "objective", "dependencies"],
                ],
                success_criteria=[
                    "Task created with unique ID",
                    "Dependencies validated",
                ],
                error_conditions=["Project not found", "Circular dependency detected"],
            ),
            ActionSchema(
                action_name="update_task_status",
                description="Update the status of an existing task",
                gateway="lackey_do",
                parameters=[
                    ParameterDefinition(
                        name="project_id",
                        type=ParameterType.UUID,
                        required=True,
                        description="Project containing the task",
                        validation_rules={ValidationRule.UUID_FORMAT: True},
                    ),
                    ParameterDefinition(
                        name="task_id",
                        type=ParameterType.UUID,
                        required=True,
                        description="Task to update",
                        validation_rules={ValidationRule.UUID_FORMAT: True},
                        relationships=["Must exist in specified project"],
                    ),
                    ParameterDefinition(
                        name="new_status",
                        type=ParameterType.ENUM,
                        required=True,
                        description="New task status",
                        validation_rules={
                            ValidationRule.ENUM_VALUES: [
                                "todo",
                                "in_progress",
                                "blocked",
                                "done",
                            ]
                        },
                    ),
                    ParameterDefinition(
                        name="note",
                        type=ParameterType.OPTIONAL,
                        required=False,
                        description="Optional note about the status change",
                        validation_rules={
                            ValidationRule.MAX_LENGTH: 1000,
                            ValidationRule.SANITIZE: True,
                        },
                    ),
                ],
                parameter_combinations=[
                    ["project_id", "task_id", "new_status"],
                    ["project_id", "task_id", "new_status", "note"],
                ],
                success_criteria=["Status updated", "Status history recorded"],
                error_conditions=["Task not found", "Invalid status transition"],
            ),
        ]

    @staticmethod
    def get_dependency_management_schemas() -> List[ActionSchema]:
        """Get dependency management action schemas."""
        return [
            ActionSchema(
                action_name="add_task_dependencies",
                description="Add dependencies to a task",
                gateway="lackey_do",
                parameters=[
                    ParameterDefinition(
                        name="project_id",
                        type=ParameterType.UUID,
                        required=True,
                        description="Project containing the task",
                        validation_rules={ValidationRule.UUID_FORMAT: True},
                    ),
                    ParameterDefinition(
                        name="task_id",
                        type=ParameterType.UUID,
                        required=True,
                        description="Task to add dependencies to",
                        validation_rules={ValidationRule.UUID_FORMAT: True},
                    ),
                    ParameterDefinition(
                        name="dependency_ids",
                        type=ParameterType.LIST,
                        required=True,
                        description="List of task IDs to depend on",
                        validation_rules={
                            ValidationRule.MIN_VALUE: 1,
                            ValidationRule.MAX_VALUE: 50,
                        },
                        relationships=[
                            "All IDs must reference existing tasks",
                            "Cannot create cycles",
                        ],
                    ),
                    ParameterDefinition(
                        name="validate",
                        type=ParameterType.BOOLEAN,
                        required=False,
                        description="Whether to validate dependency graph",
                        default=True,
                    ),
                ],
                success_criteria=["Dependencies added", "No cycles created"],
                error_conditions=[
                    "Circular dependency detected",
                    "Dependency task not found",
                ],
            ),
            ActionSchema(
                action_name="remove_task_dependencies",
                description="Remove dependencies from a task",
                gateway="lackey_do",
                parameters=[
                    ParameterDefinition(
                        name="project_id",
                        type=ParameterType.UUID,
                        required=True,
                        description="Project containing the task",
                        validation_rules={ValidationRule.UUID_FORMAT: True},
                    ),
                    ParameterDefinition(
                        name="task_id",
                        type=ParameterType.UUID,
                        required=True,
                        description="Task to remove dependencies from",
                        validation_rules={ValidationRule.UUID_FORMAT: True},
                    ),
                    ParameterDefinition(
                        name="dependency_ids",
                        type=ParameterType.LIST,
                        required=True,
                        description="List of dependency IDs to remove",
                        validation_rules={
                            ValidationRule.MIN_VALUE: 1,
                            ValidationRule.MAX_VALUE: 50,
                        },
                    ),
                ],
                success_criteria=[
                    "Dependencies removed",
                    "Task unblocked if applicable",
                ],
                error_conditions=["Task not found", "Dependency not found"],
            ),
        ]

    @staticmethod
    def get_bulk_operation_schemas() -> List[ActionSchema]:
        """Get bulk operation action schemas."""
        return [
            ActionSchema(
                action_name="bulk_assign_tasks",
                description="Assign multiple tasks to a user",
                gateway="lackey_do",
                parameters=[
                    ParameterDefinition(
                        name="project_id",
                        type=ParameterType.UUID,
                        required=True,
                        description="Project containing the tasks",
                        validation_rules={ValidationRule.UUID_FORMAT: True},
                    ),
                    ParameterDefinition(
                        name="task_ids",
                        type=ParameterType.LIST,
                        required=True,
                        description="List of task IDs to assign",
                        validation_rules={
                            ValidationRule.MIN_VALUE: 1,
                            ValidationRule.MAX_VALUE: 100,
                        },
                        relationships=[
                            "All IDs must reference existing tasks in project"
                        ],
                    ),
                    ParameterDefinition(
                        name="assignee",
                        type=ParameterType.STRING,
                        required=True,
                        description="User to assign tasks to",
                        validation_rules={
                            ValidationRule.MIN_LENGTH: 1,
                            ValidationRule.MAX_LENGTH: 100,
                            ValidationRule.SANITIZE: True,
                        },
                    ),
                ],
                success_criteria=["All tasks assigned", "Assignment history recorded"],
                error_conditions=["Some tasks not found", "Invalid assignee"],
            ),
            ActionSchema(
                action_name="bulk_update_task_status",
                description="Update status of multiple tasks",
                gateway="lackey_do",
                parameters=[
                    ParameterDefinition(
                        name="project_id",
                        type=ParameterType.UUID,
                        required=True,
                        description="Project containing the tasks",
                        validation_rules={ValidationRule.UUID_FORMAT: True},
                    ),
                    ParameterDefinition(
                        name="task_ids",
                        type=ParameterType.LIST,
                        required=True,
                        description="List of task IDs to update",
                        validation_rules={
                            ValidationRule.MIN_VALUE: 1,
                            ValidationRule.MAX_VALUE: 100,
                        },
                    ),
                    ParameterDefinition(
                        name="new_status",
                        type=ParameterType.ENUM,
                        required=True,
                        description="New status for all tasks",
                        validation_rules={
                            ValidationRule.ENUM_VALUES: [
                                "todo",
                                "in_progress",
                                "blocked",
                                "done",
                            ]
                        },
                    ),
                ],
                success_criteria=[
                    "All task statuses updated",
                    "Status history recorded",
                ],
                error_conditions=["Some tasks not found", "Invalid status value"],
            ),
        ]


class SchemaRelationshipMapper:
    """Maps parameter relationships and constraints across actions."""

    @staticmethod
    def get_parameter_relationships() -> Dict[str, Dict[str, List[str]]]:
        """Get parameter relationship mappings."""
        return {
            "project_id": {
                "must_exist": ["create_task", "update_task_status", "delete_task"],
                "references": ["projects table"],
                "cascade_delete": ["all tasks in project"],
            },
            "task_id": {
                "must_exist": ["update_task_status", "add_task_dependencies"],
                "references": ["tasks table"],
                "relationships": ["belongs to project_id"],
            },
            "dependency_ids": {
                "must_exist": ["add_task_dependencies", "remove_task_dependencies"],
                "constraints": ["no circular dependencies", "same project only"],
                "validation": ["cycle detection required"],
            },
            "assignee": {
                "format": ["string identifier"],
                "constraints": ["valid user reference"],
                "relationships": ["can be reassigned"],
            },
        }

    @staticmethod
    def get_required_parameter_combinations() -> Dict[str, List[List[str]]]:
        """Get valid parameter combinations for each action."""
        return {
            "create_task": [
                ["project_id", "title", "objective"],
                ["project_id", "title", "objective", "complexity"],
                ["project_id", "title", "objective", "steps", "success_criteria"],
            ],
            "update_task_status": [
                ["project_id", "task_id", "new_status"],
                ["project_id", "task_id", "new_status", "note"],
            ],
            "add_task_dependencies": [
                ["project_id", "task_id", "dependency_ids"],
                ["project_id", "task_id", "dependency_ids", "validate"],
            ],
            "bulk_assign_tasks": [
                ["project_id", "task_ids", "assignee"],
                ["project_id", "task_ids", "assignee", "note"],
            ],
        }


def get_complete_lackey_do_schema_documentation() -> Dict[str, Any]:
    """Get complete schema documentation for LackeyDoGateway."""
    schemas = LackeyDoGatewaySchemas()
    mapper = SchemaRelationshipMapper()

    all_schemas = []
    all_schemas.extend(schemas.get_project_management_schemas())
    all_schemas.extend(schemas.get_task_management_schemas())
    all_schemas.extend(schemas.get_dependency_management_schemas())
    all_schemas.extend(schemas.get_bulk_operation_schemas())

    return {
        "gateway_name": "lackey_do",
        "description": "State modification operations for projects and tasks",
        "total_actions": len(all_schemas),
        "action_schemas": {schema.action_name: schema for schema in all_schemas},
        "parameter_relationships": mapper.get_parameter_relationships(),
        "required_combinations": mapper.get_required_parameter_combinations(),
        "validation_summary": {
            "uuid_parameters": ["project_id", "task_id", "dependency_ids"],
            "enum_parameters": ["new_status", "complexity", "note_type"],
            "list_parameters": [
                "task_ids",
                "dependency_ids",
                "steps",
                "success_criteria",
            ],
            "sanitized_parameters": ["title", "objective", "description", "note"],
        },
    }


# Export the complete documentation
LACKEY_DO_GATEWAY_DOCUMENTATION = get_complete_lackey_do_schema_documentation()
