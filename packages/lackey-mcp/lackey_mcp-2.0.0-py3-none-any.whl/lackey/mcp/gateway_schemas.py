"""Parameter validation schemas for gateway operations.

This module defines comprehensive validation schemas for all tools across the three
gateways, ensuring type safety, security, and proper parameter handling.
"""

import re
from typing import Any, Dict, List, Optional, Tuple


class SchemaValidator:
    """Utility class for advanced parameter validation."""

    @staticmethod
    def validate_uuid(value: str) -> bool:
        """Validate UUID format."""
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            re.IGNORECASE,
        )
        return bool(uuid_pattern.match(value))

    @staticmethod
    def validate_short_id(value: str) -> bool:
        """Validate short ID format (8 characters)."""
        return bool(re.match(r"^[0-9a-f]{8}$", value, re.IGNORECASE))

    @staticmethod
    def validate_status(value: str) -> bool:
        """Validate task status values."""
        valid_statuses = {"todo", "in_progress", "blocked", "done"}
        return value.lower() in valid_statuses

    @staticmethod
    def validate_complexity(value: str) -> bool:
        """Validate complexity values."""
        valid_complexities = {"low", "medium", "high"}
        return value.lower() in valid_complexities

    @staticmethod
    def validate_note_type(value: str) -> bool:
        """Validate note type values."""
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

    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input for security."""
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', "", value)

        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized.strip()

    @staticmethod
    def validate_list_of_strings(value: List[str]) -> bool:
        """Validate list contains only strings."""
        return isinstance(value, list) and all(isinstance(x, str) for x in value)


# Gateway-specific validation schemas
LACKEY_GET_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "list_projects": {"required": [], "optional": {}, "types": {}, "constraints": {}},
    "get_project": {
        "required": ["project_id"],
        "optional": {},
        "types": {"project_id": "str"},
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            }
        },
    },
    "list_tasks": {
        "required": ["project_id"],
        "optional": {
            "status": None,
            "complexity": None,
            "assigned_to": None,
            "tag": None,
        },
        "types": {
            "project_id": "str",
            "status": "optional[str]",
            "complexity": "optional[str]",
            "assigned_to": "optional[str]",
            "tag": "optional[str]",
        },
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            },
            "status": {
                "validator": "validate_status",
                "error": "status must be one of: todo, in-progress, blocked, done",
            },
            "complexity": {
                "validator": "validate_complexity",
                "error": "complexity must be one of: low, medium, high",
            },
        },
    },
    "get_task": {
        "required": ["task_id"],
        "optional": {},
        "types": {"task_id": "str"},
        "constraints": {
            "task_id": {
                "validator": "validate_uuid",
                "error": "task_id must be a valid UUID",
            },
        },
    },
    "get_task_progress": {
        "required": ["project_id", "task_id"],
        "optional": {},
        "types": {"project_id": "str", "task_id": "str"},
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            },
            "task_id": {
                "validator": "validate_uuid",
                "error": "task_id must be a valid UUID",
            },
        },
    },
    "get_task_notes": {
        "required": ["project_id", "task_id"],
        "optional": {"note_type": None, "author": None, "tag": None, "limit": None},
        "types": {
            "project_id": "str",
            "task_id": "str",
            "note_type": "optional[str]",
            "author": "optional[str]",
            "tag": "optional[str]",
            "limit": "optional[int]",
        },
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            },
            "task_id": {
                "validator": "validate_uuid",
                "error": "task_id must be a valid UUID",
            },
            "note_type": {
                "validator": "validate_note_type",
                "error": "note_type must be valid note type",
            },
            "limit": {
                "min": 1,
                "max": 1000,
                "error": "limit must be between 1 and 1000",
            },
        },
    },
    "search_task_notes": {
        "required": ["project_id", "task_id", "query"],
        "optional": {"note_type": None, "author": None, "limit": None},
        "types": {
            "project_id": "str",
            "task_id": "str",
            "query": "str",
            "note_type": "optional[str]",
            "author": "optional[str]",
            "limit": "optional[int]",
        },
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            },
            "task_id": {
                "validator": "validate_uuid",
                "error": "task_id must be a valid UUID",
            },
            "query": {
                "min_length": 1,
                "max_length": 500,
                "error": "query must be 1-500 characters",
            },
            "limit": {
                "min": 1,
                "max": 1000,
                "error": "limit must be between 1 and 1000",
            },
        },
    },
    "get_ready_tasks": {
        "required": ["project_id"],
        "optional": {},
        "types": {"project_id": "str"},
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            }
        },
    },
    "get_blocked_tasks": {
        "required": ["project_id"],
        "optional": {},
        "types": {"project_id": "str"},
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            }
        },
    },
}

LACKEY_DO_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "create_project": {
        "required": ["friendly_name"],
        "optional": {"description": None, "objectives": None, "tags": None},
        "types": {
            "friendly_name": "str",
            "description": "optional[str]",
            "objectives": "optional[str]",
            "tags": "optional[str]",
        },
        "constraints": {
            "friendly_name": {
                "min_length": 1,
                "max_length": 200,
                "sanitize": True,
                "error": "friendly_name must be 1-200 characters",
            },
            "description": {
                "max_length": 2000,
                "sanitize": True,
                "error": "description must be under 2000 characters",
            },
            "objectives": {
                "max_length": 1000,
                "sanitize": True,
                "error": "objectives must be under 1000 characters",
            },
            "tags": {
                "max_length": 500,
                "sanitize": True,
                "error": "tags must be under 500 characters",
            },
        },
    },
    "update_project": {
        "required": ["project_id"],
        "optional": {
            "friendly_name": None,
            "description": None,
            "status": None,
            "objectives": None,
            "tags": None,
        },
        "types": {
            "project_id": "str",
            "friendly_name": "optional[str]",
            "description": "optional[str]",
            "status": "optional[str]",
            "objectives": "optional[str]",
            "tags": "optional[str]",
        },
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            },
            "friendly_name": {
                "min_length": 1,
                "max_length": 200,
                "sanitize": True,
                "error": "friendly_name must be 1-200 characters",
            },
            "status": {
                "allowed_values": ["active", "done", "archived"],
                "error": "status must be: active, completed, or archived",
            },
        },
    },
    "delete_project": {
        "required": ["project_id"],
        "optional": {},
        "types": {"project_id": "str"},
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            }
        },
    },
    "create_task": {
        "required": ["project_id", "title", "objective"],
        "optional": {
            "steps": ["Complete the task"],
            "success_criteria": ["Task completed successfully"],
            "complexity": "medium",
            "context": None,
            "assigned_to": None,
            "tags": None,
            "dependencies": None,
        },
        "types": {
            "project_id": "str",
            "title": "str",
            "objective": "str",
            "steps": "optional[list[str]]",
            "success_criteria": "optional[list[str]]",
            "complexity": "str",
            "context": "optional[str]",
            "assigned_to": "optional[str]",
            "tags": "optional[list[str]]",
            "dependencies": "optional[list[str]]",
        },
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            },
            "title": {
                "min_length": 1,
                "max_length": 200,
                "sanitize": True,
                "error": "title must be 1-200 characters",
            },
            "objective": {
                "min_length": 1,
                "max_length": 1000,
                "sanitize": True,
                "error": "objective must be 1-1000 characters",
            },
            "steps": {
                "min_items": 1,
                "max_items": 50,
                "item_max_length": 500,
                "error": "steps must contain 1-50 items, each under 500 characters",
            },
            "success_criteria": {
                "min_items": 1,
                "max_items": 20,
                "item_max_length": 500,
                "error": (
                    "success_criteria must contain 1-20 items, "
                    "each under 500 characters"
                ),
            },
            "complexity": {
                "validator": "validate_complexity",
                "error": "complexity must be: low, medium, or high",
            },
        },
    },
    "update_task_status": {
        "required": ["project_id", "task_id", "new_status"],
        "optional": {"note": None},
        "types": {
            "project_id": "str",
            "task_id": "str",
            "new_status": "enum",
            "note": "optional[str]",
        },
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            },
            "task_id": {
                "validator": "validate_uuid",
                "error": "task_id must be a valid UUID",
            },
            "new_status": {
                "validator": "validate_status",
                "error": "new_status must be: todo, in_progress, blocked, or done",
                "enum_class": "TaskStatus",
            },
            "note": {
                "max_length": 1000,
                "sanitize": True,
                "error": "note must be under 1000 characters",
            },
        },
    },
    "complete_task_steps": {
        "required": ["project_id", "task_id", "step_indices"],
        "optional": {"note": None, "auto_complete": False},
        "types": {
            "project_id": "str",
            "task_id": "str",
            "step_indices": "list[int]",
            "note": "optional[str]",
            "auto_complete": "bool",
        },
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            },
            "task_id": {
                "validator": "validate_uuid",
                "error": "task_id must be a valid UUID",
            },
            "step_indices": {
                "min_items": 1,
                "max_items": 50,
                "item_min": 0,
                "item_max": 49,
                "error": "step_indices must contain 1-50 valid indices (0-49)",
            },
        },
    },
    "assign_task": {
        "required": ["project_id", "task_id", "assignee"],
        "optional": {"note": None},
        "types": {
            "project_id": "str",
            "task_id": "str",
            "assignee": "str",
            "note": "optional[str]",
        },
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            },
            "task_id": {
                "validator": "validate_uuid",
                "error": "task_id must be a valid UUID",
            },
            "assignee": {
                "min_length": 1,
                "max_length": 100,
                "sanitize": True,
                "error": "assignee must be 1-100 characters",
            },
        },
    },
    "reassign_task": {
        "required": ["project_id", "task_id", "new_assignee"],
        "optional": {"note": None},
        "types": {
            "project_id": "str",
            "task_id": "str",
            "new_assignee": "str",
            "note": "optional[str]",
        },
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            },
            "task_id": {
                "validator": "validate_uuid",
                "error": "task_id must be a valid UUID",
            },
            "new_assignee": {
                "min_length": 1,
                "max_length": 100,
                "sanitize": True,
                "error": "new_assignee must be 1-100 characters",
            },
        },
    },
    "bulk_assign_tasks": {
        "required": ["project_id", "task_ids", "assignee"],
        "optional": {"note": None},
        "types": {
            "project_id": "str",
            "task_ids": "list[str]",
            "assignee": "str",
            "note": "optional[str]",
        },
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            },
            "task_ids": {
                "min_items": 1,
                "max_items": 100,
                "error": "task_ids must contain 1-100 task IDs",
            },
            "assignee": {
                "min_length": 1,
                "max_length": 100,
                "sanitize": True,
                "error": "assignee must be 1-100 characters",
            },
        },
    },
    "bulk_update_task_status": {
        "required": ["project_id", "task_ids", "new_status"],
        "optional": {"note": None},
        "types": {
            "project_id": "str",
            "task_ids": "list[str]",
            "new_status": "enum",
            "note": "optional[str]",
        },
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            },
            "task_ids": {
                "min_items": 1,
                "max_items": 100,
                "error": "task_ids must contain 1-100 task IDs",
            },
            "new_status": {
                "validator": "validate_status",
                "error": "new_status must be: todo, in_progress, blocked, or done",
            },
        },
    },
    "add_task_dependencies": {
        "required": ["project_id", "task_id", "dependency_ids"],
        "optional": {"validate": True},
        "types": {
            "project_id": "str",
            "task_id": "str",
            "dependency_ids": "list[str]",
            "validate": "bool",
        },
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            },
            "task_id": {
                "validator": "validate_uuid",
                "error": "task_id must be a valid UUID",
            },
            "dependency_ids": {
                "min_items": 1,
                "max_items": 50,
                "error": "dependency_ids must contain 1-50 dependency IDs",
            },
        },
    },
    "remove_task_dependencies": {
        "required": ["project_id", "task_id", "dependency_ids"],
        "optional": {},
        "types": {"project_id": "str", "task_id": "str", "dependency_ids": "list[str]"},
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            },
            "task_id": {
                "validator": "validate_uuid",
                "error": "task_id must be a valid UUID",
            },
            "dependency_ids": {
                "min_items": 1,
                "max_items": 50,
                "error": "dependency_ids must contain 1-50 dependency IDs",
            },
        },
    },
    "add_task_note": {
        "required": ["project_id", "task_id", "content"],
        "optional": {"note_type": "user", "author": None, "tags": None},
        "types": {
            "project_id": "str",
            "task_id": "str",
            "content": "str",
            "note_type": "enum",
            "author": "optional[str]",
            "tags": "optional[str]",
        },
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            },
            "task_id": {
                "validator": "validate_uuid",
                "error": "task_id must be a valid UUID",
            },
            "content": {
                "min_length": 1,
                "max_length": 5000,
                "sanitize": True,
                "error": "content must be 1-5000 characters",
            },
            "note_type": {
                "validator": "validate_note_type",
                "error": "note_type must be valid note type",
            },
        },
    },
    "delete_task": {
        "required": ["project_id", "task_id"],
        "optional": {},
        "types": {
            "project_id": "str",
            "task_id": "str",
        },
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            },
            "task_id": {
                "validator": "validate_uuid",
                "error": "task_id must be a valid UUID",
            },
        },
    },
    "clone_task": {
        "required": ["project_id", "task_id"],
        "optional": {
            "new_title": None,
            "copy_dependencies": False,
            "copy_progress": False,
        },
        "types": {
            "project_id": "str",
            "task_id": "str",
            "new_title": "optional[str]",
            "copy_dependencies": "bool",
            "copy_progress": "bool",
        },
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            },
            "task_id": {
                "validator": "validate_uuid",
                "error": "task_id must be a valid UUID",
            },
            "new_title": {
                "min_length": 1,
                "max_length": 200,
                "sanitize": True,
                "error": "new_title must be 1-200 characters",
            },
        },
    },
    "archive_task": {
        "required": ["project_id", "task_id"],
        "optional": {"reason": None},
        "types": {"project_id": "str", "task_id": "str", "reason": "optional[str]"},
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            },
            "task_id": {
                "validator": "validate_uuid",
                "error": "task_id must be a valid UUID",
            },
            "reason": {
                "max_length": 500,
                "sanitize": True,
                "error": "reason must be under 500 characters",
            },
        },
    },
}

LACKEY_ANALYZE_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "validate_dependencies": {
        "required": ["project_id"],
        "optional": {},
        "types": {"project_id": "str"},
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            }
        },
    },
    "validate_task_dependencies_integrity": {
        "required": ["project_id"],
        "optional": {},
        "types": {"project_id": "str"},
        "constraints": {
            "project_id": {
                "validator": "validate_uuid",
                "error": "project_id must be a valid UUID",
            }
        },
    },
}

# Combined schema registry
ALL_SCHEMAS: Dict[str, Dict[str, Any]] = {
    **LACKEY_GET_SCHEMAS,
    **LACKEY_DO_SCHEMAS,
    **LACKEY_ANALYZE_SCHEMAS,
}


def get_schema_for_tool(tool_name: str) -> Optional[Dict[str, Any]]:
    """Get validation schema for a specific tool."""
    return ALL_SCHEMAS.get(tool_name)


def get_schemas_for_gateway(gateway_type: str) -> Dict[str, Dict[str, Any]]:
    """Get all schemas for a specific gateway."""
    if gateway_type == "lackey_get":
        return LACKEY_GET_SCHEMAS
    elif gateway_type == "lackey_do":
        return LACKEY_DO_SCHEMAS
    elif gateway_type == "lackey_analyze":
        return LACKEY_ANALYZE_SCHEMAS
    else:
        return {}


def validate_parameter_value(
    value: Any, constraint: Dict[str, Any], validator_instance: SchemaValidator
) -> Tuple[bool, str]:
    """Validate a parameter value against its constraints."""
    # Check validator function
    if "validator" in constraint:
        validator_name = constraint["validator"]
        if hasattr(validator_instance, validator_name):
            validator_func = getattr(validator_instance, validator_name)
            if not validator_func(value):
                return False, constraint.get(
                    "error", f"Validation failed for {validator_name}"
                )

    # Check allowed values
    if "allowed_values" in constraint:
        if value not in constraint["allowed_values"]:
            return False, constraint.get(
                "error", f"Value must be one of: {constraint['allowed_values']}"
            )

    # Check string constraints
    if isinstance(value, str):
        if "min_length" in constraint and len(value) < constraint["min_length"]:
            return False, constraint.get(
                "error", f"Must be at least {constraint['min_length']} characters"
            )

        if "max_length" in constraint and len(value) > constraint["max_length"]:
            return False, constraint.get(
                "error", f"Must be at most {constraint['max_length']} characters"
            )

    # Check numeric constraints
    if isinstance(value, (int, float)):
        if "min" in constraint and value < constraint["min"]:
            return False, constraint.get(
                "error", f"Must be at least {constraint['min']}"
            )

        if "max" in constraint and value > constraint["max"]:
            return False, constraint.get(
                "error", f"Must be at most {constraint['max']}"
            )

    # Check list constraints
    if isinstance(value, list):
        if "min_items" in constraint and len(value) < constraint["min_items"]:
            return False, constraint.get(
                "error", f"Must contain at least {constraint['min_items']} items"
            )

        if "max_items" in constraint and len(value) > constraint["max_items"]:
            return False, constraint.get(
                "error", f"Must contain at most {constraint['max_items']} items"
            )

        # Check individual item constraints
        if "item_max_length" in constraint:
            for item in value:
                if isinstance(item, str) and len(item) > constraint["item_max_length"]:
                    return False, constraint.get(
                        "error",
                        f"List items must be under "
                        f"{constraint['item_max_length']} characters",
                    )

        if "item_min" in constraint or "item_max" in constraint:
            for item in value:
                if isinstance(item, (int, float)):
                    if "item_min" in constraint and item < constraint["item_min"]:
                        return False, constraint.get(
                            "error",
                            f"List items must be at least {constraint['item_min']}",
                        )
                    if "item_max" in constraint and item > constraint["item_max"]:
                        return False, constraint.get(
                            "error",
                            f"List items must be at most {constraint['item_max']}",
                        )

    return True, ""
