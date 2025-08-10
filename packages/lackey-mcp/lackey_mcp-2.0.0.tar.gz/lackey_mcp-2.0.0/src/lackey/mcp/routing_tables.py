"""Routing table mappings for all MCP tool operations.

This module defines the complete routing tables that map natural language intents
to specific tools across the three gateways, enabling semantic consolidation.
"""

from typing import Any, Callable, Dict, List, cast

# Intent patterns for lackey_get gateway (Information Retrieval - 10 tools)
LACKEY_GET_INTENT_PATTERNS = {
    "list_projects": [
        "list projects",
        "show projects",
        "get projects",
        "all projects",
        "project list",
        "projects",
        "show all projects",
        "list all projects",
        "what projects",
        "available projects",
        "existing projects",
    ],
    "get_project": [
        "get project",
        "show project",
        "project details",
        "project info",
        "project information",
        "describe project",
        "project description",
        "tell me about project",
        "project status",
        "project overview",
    ],
    "list_tasks": [
        "list tasks",
        "show tasks",
        "get tasks",
        "all tasks",
        "task list",
        "tasks",
        "show all tasks",
        "list all tasks",
        "what tasks",
        "available tasks",
        "existing tasks",
        "tasks in project",
        "project tasks",
        "find tasks",
        "search tasks",
    ],
    "get_task": [
        "get task",
        "show task",
        "task details",
        "task info",
        "task information",
        "describe task",
        "task description",
        "tell me about task",
        "task status",
        "task overview",
        "what is task",
        "task summary",
    ],
    "get_task_progress": [
        "task progress",
        "progress",
        "how far",
        "completion status",
        "progress status",
        "task completion",
        "steps completed",
        "progress report",
        "task advancement",
        "completion rate",
        "how much done",
        "progress update",
    ],
    "get_task_notes": [
        "task notes",
        "notes",
        "comments",
        "task comments",
        "show notes",
        "get notes",
        "note history",
        "task documentation",
        "notes for task",
        "task logs",
        "recorded notes",
    ],
    "search_task_notes": [
        "search notes",
        "find notes",
        "search comments",
        "find in notes",
        "search task notes",
        "look for",
        "find comment",
        "search documentation",
        "search logs",
        "find in comments",
        "note search",
    ],
    "get_ready_tasks": [
        "ready tasks",
        "available tasks",
        "tasks ready",
        "what can I work on",
        "ready to work",
        "available work",
        "unblocked tasks",
        "tasks I can do",
        "next tasks",
        "work available",
        "ready for work",
        "actionable tasks",
    ],
    "get_blocked_tasks": [
        "blocked tasks",
        "stuck tasks",
        "waiting tasks",
        "blocked work",
        "tasks blocked",
        "what's blocked",
        "bottlenecks",
        "dependencies blocking",
        "tasks waiting",
        "blocked items",
        "stuck work",
        "dependency issues",
    ],
}

# Intent patterns for lackey_do gateway (State Modification - 12 tools)
LACKEY_DO_INTENT_PATTERNS = {
    "create_project": [
        "create project",
        "new project",
        "start project",
        "make project",
        "initialize project",
        "begin project",
        "setup project",
        "add project",
        "project creation",
        "start new project",
    ],
    "delete_project": [
        "delete project",
        "remove project",
        "destroy project",
        "eliminate project",
        "drop project",
        "erase project",
        "project deletion",
        "get rid of project",
    ],
    "update_project": [
        "update project",
        "modify project",
        "change project",
        "edit project",
        "alter project",
        "revise project",
        "project update",
        "change project details",
        "modify project info",
    ],
    "create_task": [
        "create task",
        "new task",
        "add task",
        "make task",
        "define task",
        "setup task",
        "initialize task",
        "task creation",
        "start task",
        "begin task",
    ],
    "update_task_status": [
        "update status",
        "change status",
        "mark as",
        "set status",
        "status to",
        "make it",
        "mark task",
        "update task status",
        "change task status",
        "set task status",
        "task status",
        "mark done",
        "mark complete",
        "mark in progress",
        "mark todo",
    ],
    "complete_task_steps": [
        "complete step",
        "finish step",
        "mark step done",
        "step complete",
        "done with step",
        "finished step",
        "complete steps",
        "step completion",
        "mark steps complete",
        "finish steps",
    ],
    "assign_task": [
        "assign task",
        "assign to",
        "give task to",
        "task for",
        "allocate task",
        "delegate task",
        "hand task to",
        "task assignment",
        "assign work",
        "give work to",
    ],
    "reassign_task": [
        "reassign task",
        "move task to",
        "transfer task",
        "change assignee",
        "reassign to",
        "switch assignment",
        "task reassignment",
        "change task owner",
        "transfer work",
    ],
    "bulk_assign_tasks": [
        "assign multiple",
        "bulk assign",
        "assign all",
        "assign tasks to",
        "mass assign",
        "assign several",
        "batch assign",
        "assign many tasks",
        "multiple assignment",
    ],
    "bulk_update_task_status": [
        "update multiple",
        "bulk update",
        "change all",
        "mass update",
        "update several",
        "batch update",
        "bulk status update",
        "update many tasks",
        "multiple status change",
    ],
    "add_task_dependencies": [
        "add dependency",
        "depends on",
        "requires",
        "needs",
        "blocked by",
        "prerequisite",
        "add prerequisite",
        "task depends",
        "dependency",
        "add requirement",
        "task requires",
    ],
    "remove_task_dependencies": [
        "remove dependency",
        "unblock",
        "no longer depends",
        "remove prerequisite",
        "delete dependency",
        "clear dependency",
        "remove requirement",
        "dependency removal",
        "unblock task",
    ],
    "add_task_note": [
        "add note",
        "note that",
        "comment",
        "add comment",
        "write note",
        "document",
        "record",
        "log note",
        "task note",
        "add documentation",
        "record note",
    ],
    "clone_task": [
        "clone task",
        "copy task",
        "duplicate task",
        "replicate task",
        "make copy",
        "duplicate",
        "task copy",
        "copy work",
        "replicate work",
        "task duplication",
    ],
    "archive_task": [
        "archive task",
        "remove task",
        "delete task",
        "hide task",
        "retire task",
        "close task",
        "task archive",
        "put away task",
        "finish task permanently",
    ],
}

# Intent patterns for lackey_analyze gateway (Analysis and Validation - 3 tools)
LACKEY_ANALYZE_INTENT_PATTERNS = {
    "validate_dependencies": [
        "validate dependencies",
        "check dependencies",
        "dependency check",
        "validate deps",
        "check deps",
        "dependency validation",
        "verify dependencies",
        "dependency analysis",
        "check for cycles",
        "validate workflow",
        "dependency issues",
    ],
    "validate_task_dependencies_integrity": [
        "validate integrity",
        "check integrity",
        "integrity check",
        "dependency integrity",
        "validate task integrity",
        "check task dependencies",
        "verify task deps",
        "task dependency check",
        "integrity validation",
    ],
}

# Parameter mappings for each tool
PARAMETER_MAPPINGS = {
    # lackey_get mappings
    "list_projects": {},
    "get_project": {"project_id": "extract_project_id"},
    "list_tasks": {
        "project_id": "extract_project_id",
        "status": "extract_status",
        "complexity": "extract_complexity",
        "assigned_to": "extract_assignee",
        "tag": "extract_tag",
    },
    "get_task": {"project_id": "extract_project_id", "task_id": "extract_task_id"},
    "get_task_progress": {
        "project_id": "extract_project_id",
        "task_id": "extract_task_id",
    },
    "get_task_notes": {
        "project_id": "extract_project_id",
        "task_id": "extract_task_id",
        "note_type": "extract_note_type",
        "author": "extract_author",
        "tag": "extract_tag",
        "limit": "extract_limit",
    },
    "search_task_notes": {
        "project_id": "extract_project_id",
        "task_id": "extract_task_id",
        "query": "extract_search_query",
        "note_type": "extract_note_type",
        "author": "extract_author",
        "limit": "extract_limit",
    },
    "get_ready_tasks": {"project_id": "extract_project_id"},
    "get_blocked_tasks": {"project_id": "extract_project_id"},
    # lackey_do mappings
    "create_project": {
        "friendly_name": "extract_project_name",
        "description": "extract_description",
        "objectives": "extract_objectives",
        "tags": "extract_tags",
    },
    "delete_project": {"project_id": "extract_project_id"},
    "update_project": {
        "project_id": "extract_project_id",
        "friendly_name": "extract_project_name",
        "description": "extract_description",
        "status": "extract_status",
        "objectives": "extract_objectives",
        "tags": "extract_tags",
    },
    "create_task": {
        "project_id": "extract_project_id",
        "title": "extract_task_title",
        "objective": "extract_objective",
        "steps": "extract_steps",
        "success_criteria": "extract_success_criteria",
        "complexity": "extract_complexity",
        "context": "extract_context",
        "assigned_to": "extract_assignee",
        "tags": "extract_tags",
        "dependencies": "extract_dependencies",
    },
    "update_task_status": {
        "project_id": "extract_project_id",
        "task_id": "extract_task_id",
        "status": "extract_status",
        "note": "extract_note",
    },
    "complete_task_steps": {
        "project_id": "extract_project_id",
        "task_id": "extract_task_id",
        "step_indices": "extract_step_indices",
        "note": "extract_note",
        "auto_complete": "extract_auto_complete",
    },
    "assign_task": {
        "project_id": "extract_project_id",
        "task_id": "extract_task_id",
        "assignee": "extract_assignee",
        "note": "extract_note",
    },
    "reassign_task": {
        "project_id": "extract_project_id",
        "task_id": "extract_task_id",
        "new_assignee": "extract_assignee",
        "note": "extract_note",
    },
    "bulk_assign_tasks": {
        "project_id": "extract_project_id",
        "task_ids": "extract_task_ids",
        "assignee": "extract_assignee",
        "note": "extract_note",
    },
    "bulk_update_task_status": {
        "project_id": "extract_project_id",
        "task_ids": "extract_task_ids",
        "status": "extract_status",
        "note": "extract_note",
    },
    "add_task_dependencies": {
        "project_id": "extract_project_id",
        "task_id": "extract_task_id",
        "dependency_ids": "extract_dependency_ids",
        "validate": "extract_validate",
    },
    "remove_task_dependencies": {
        "project_id": "extract_project_id",
        "task_id": "extract_task_id",
        "dependency_ids": "extract_dependency_ids",
    },
    "add_task_note": {
        "project_id": "extract_project_id",
        "task_id": "extract_task_id",
        "content": "extract_note_content",
        "note_type": "extract_note_type",
        "author": "extract_author",
        "tags": "extract_tags",
    },
    "clone_task": {
        "project_id": "extract_project_id",
        "task_id": "extract_task_id",
        "new_title": "extract_new_title",
        "copy_dependencies": "extract_copy_dependencies",
        "copy_progress": "extract_copy_progress",
    },
    "archive_task": {
        "project_id": "extract_project_id",
        "task_id": "extract_task_id",
        "reason": "extract_reason",
    },
    # lackey_analyze mappings
    "validate_dependencies": {"project_id": "extract_project_id"},
    "validate_task_dependencies_integrity": {"project_id": "extract_project_id"},
}

# Tool registry mappings (will be populated by gateway implementations)
TOOL_REGISTRIES: Dict[str, Dict[str, Any]] = {"GET": {}, "DO": {}, "ANALYZE": {}}

# Gateway-specific routing configurations
GATEWAY_CONFIGS = {
    "GET": {
        "name": "lackey_get",
        "description": "Information retrieval and querying operations",
        "tool_count": 10,
        "intent_patterns": LACKEY_GET_INTENT_PATTERNS,
        "parameter_mappings": {
            k: v
            for k, v in PARAMETER_MAPPINGS.items()
            if k in LACKEY_GET_INTENT_PATTERNS
        },
        "default_confidence_threshold": 0.6,
        "cache_ttl_seconds": 300,
        "rate_limit_rule": "lenient",
    },
    "DO": {
        "name": "lackey_do",
        "description": "State modification and action operations",
        "tool_count": 12,
        "intent_patterns": LACKEY_DO_INTENT_PATTERNS,
        "parameter_mappings": {
            k: v
            for k, v in PARAMETER_MAPPINGS.items()
            if k in LACKEY_DO_INTENT_PATTERNS
        },
        "default_confidence_threshold": 0.7,
        "cache_ttl_seconds": 60,
        "rate_limit_rule": "default",
    },
    "ANALYZE": {
        "name": "lackey_analyze",
        "description": "Analysis and validation operations",
        "tool_count": 3,
        "intent_patterns": LACKEY_ANALYZE_INTENT_PATTERNS,
        "parameter_mappings": {
            k: v
            for k, v in PARAMETER_MAPPINGS.items()
            if k in LACKEY_ANALYZE_INTENT_PATTERNS
        },
        "default_confidence_threshold": 0.8,
        "cache_ttl_seconds": 600,
        "rate_limit_rule": "default",
    },
}

# Consolidated intent patterns for cross-gateway routing
ALL_INTENT_PATTERNS = {
    **LACKEY_GET_INTENT_PATTERNS,
    **LACKEY_DO_INTENT_PATTERNS,
    **LACKEY_ANALYZE_INTENT_PATTERNS,
}

# Intent to gateway mapping for routing decisions
INTENT_TO_GATEWAY: Dict[str, str] = {}
for gateway_type, config in GATEWAY_CONFIGS.items():
    if isinstance(config, dict) and "intent_patterns" in config:
        intent_patterns = config["intent_patterns"]
        if isinstance(intent_patterns, dict):
            for intent in intent_patterns:
                INTENT_TO_GATEWAY[intent] = gateway_type

# Tool to gateway mapping
TOOL_TO_GATEWAY: Dict[str, str] = {}
for gateway_type, config in GATEWAY_CONFIGS.items():
    if isinstance(config, dict) and "intent_patterns" in config:
        intent_patterns = config["intent_patterns"]
        if isinstance(intent_patterns, dict):
            for tool_name in intent_patterns:
                TOOL_TO_GATEWAY[tool_name] = gateway_type


# Common parameter extraction patterns
EXTRACTION_PATTERNS = {
    "project_id": [
        r"project\s+([a-f0-9-]{36})",
        r"project\s+id\s+([a-f0-9-]{36})",
        r"in\s+project\s+([a-f0-9-]{36})",
        r"for\s+project\s+([a-f0-9-]{36})",
    ],
    "task_id": [
        r"task\s+([a-f0-9-]{36})",
        r"task\s+id\s+([a-f0-9-]{36})",
        r"task\s+([a-f0-9-]{8})",  # Short form
        r"for\s+task\s+([a-f0-9-]{36})",
    ],
    "status": [
        r"status\s+to\s+(\w+)",
        r"mark\s+as\s+(\w+)",
        r"set\s+status\s+(\w+)",
        r"change\s+to\s+(\w+)",
        r"make\s+it\s+(\w+)",
    ],
    "assignee": [
        r"assign\s+to\s+([a-zA-Z\s]+)",
        r"for\s+([a-zA-Z\s]+)",
        r"assignee\s+([a-zA-Z\s]+)",
        r"give\s+to\s+([a-zA-Z\s]+)",
    ],
    "complexity": [
        r"complexity\s+(\w+)",
        r"make\s+it\s+(\w+)\s+complexity",
        r"set\s+complexity\s+(\w+)",
    ],
    "note_type": [r"note\s+type\s+(\w+)", r"type\s+(\w+)\s+note", r"(\w+)\s+note"],
}

# Usage examples for each tool (for documentation and testing)
TOOL_USAGE_EXAMPLES = {
    # lackey_get examples
    "list_projects": [
        "list all projects",
        "show me the projects",
        "what projects are available?",
    ],
    "get_project": [
        "get project 13e4054f-861e-49a7-8d2e-a9eb33bfb300",
        "show me project details for lackey project",
        "tell me about this project",
    ],
    "list_tasks": [
        "list tasks in project 13e4054f-861e-49a7-8d2e-a9eb33bfb300",
        "show all tasks",
        "what tasks are in progress?",
    ],
    "get_task": [
        "get task fe49a9e3-2fa5-41db-a729-1b5fa799c445",
        "show task details",
        "tell me about this task",
    ],
    "get_task_progress": [
        "what's the progress on task fe49a9e3-2fa5-41db-a729-1b5fa799c445?",
        "show task progress",
        "how far along is this task?",
    ],
    # lackey_do examples
    "create_project": [
        "create a new project called 'Website Redesign'",
        "start project for mobile app development",
        "make a project for the Q4 initiative",
    ],
    "create_task": [
        (
            "create task 'Implement user authentication' in project "
            "13e4054f-861e-49a7-8d2e-a9eb33bfb300"
        ),
        "add a new task for database optimization",
        "make a task to review the code",
    ],
    "update_task_status": [
        "mark task fe49a9e3-2fa5-41db-a729-1b5fa799c445 as in-progress",
        "set status to done",
        "change task status to blocked",
    ],
    "assign_task": [
        "assign task fe49a9e3-2fa5-41db-a729-1b5fa799c445 to John",
        "give this task to Sarah",
        "assign work to the backend team",
    ],
    # lackey_analyze examples
    "validate_dependencies": [
        "check dependencies in project 13e4054f-861e-49a7-8d2e-a9eb33bfb300",
        "validate the dependency graph",
        "are there any circular dependencies?",
    ],
}


def get_gateway_config(gateway_type: str) -> Dict[str, Any]:
    """Get configuration for a specific gateway."""
    return GATEWAY_CONFIGS.get(gateway_type, {})


def get_intent_patterns_for_gateway(gateway_type: str) -> Dict[str, List[str]]:
    """Get intent patterns for a specific gateway."""
    config = get_gateway_config(gateway_type)
    patterns = config.get("intent_patterns", {})
    return patterns if isinstance(patterns, dict) else {}


def get_parameter_mappings_for_gateway(
    gateway_type: str,
) -> Dict[str, Dict[str, str]]:
    """Get parameter mappings for a specific gateway."""
    config = get_gateway_config(gateway_type)
    mappings = config.get("parameter_mappings", {})
    return mappings if isinstance(mappings, dict) else {}


def find_gateway_for_intent(intent: str) -> str:
    """Find which gateway handles a specific intent."""
    return INTENT_TO_GATEWAY.get(intent, "GET")  # Default to GET


def find_gateway_for_tool(tool_name: str) -> str:
    """Find which gateway handles a specific tool."""
    return TOOL_TO_GATEWAY.get(tool_name, "GET")  # Default to GET


def get_all_tools_for_gateway(gateway_type: str) -> List[str]:
    """Get all tool names for a specific gateway."""
    config = get_gateway_config(gateway_type)
    return list(config.get("intent_patterns", {}).keys())


def get_usage_examples_for_tool(tool_name: str) -> List[str]:
    """Get usage examples for a specific tool."""
    return TOOL_USAGE_EXAMPLES.get(tool_name, [])


def register_tool_function(
    gateway_type: str, tool_name: str, tool_function: Callable
) -> None:
    """Register a tool function with a gateway."""
    if gateway_type not in TOOL_REGISTRIES:
        TOOL_REGISTRIES[gateway_type] = {}

    TOOL_REGISTRIES[gateway_type][tool_name] = tool_function


def get_tool_registry_for_gateway(gateway_type: str) -> Dict[str, Callable]:
    """Get tool registry for a specific gateway."""
    return TOOL_REGISTRIES.get(gateway_type, {})


def get_routing_statistics() -> Dict[str, Any]:
    """Get statistics about the routing table configuration."""
    configs: List[Dict[str, Any]] = [
        c for c in GATEWAY_CONFIGS.values() if isinstance(c, dict)
    ]

    total_tools: int = sum(config.get("tool_count", 0) for config in configs)
    total_intents: int = sum(
        len(config.get("intent_patterns", {})) for config in configs
    )
    total_patterns: int = sum(
        len(config.get("intent_patterns", {})) for config in configs
    )

    return {
        "total_tools": total_tools,
        "total_intents": total_intents,
        "total_patterns": total_patterns,
        "gateways": {
            gateway_type: {
                "tool_count": config.get("tool_count", 0),
                "intent_count": len(
                    cast(Dict[str, Any], config.get("intent_patterns", {}))
                ),
                "pattern_count": sum(
                    len(patterns)
                    for patterns in cast(
                        Dict[str, Any], config.get("intent_patterns", {})
                    ).values()
                    if isinstance(patterns, list)
                ),
            }
            for gateway_type, config in GATEWAY_CONFIGS.items()
            if isinstance(config, dict)
        },
    }
