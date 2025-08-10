"""lackey_get gateway for read operations."""

import logging
from typing import Any, Callable, Dict, List

from ..gateway_router import GatewayRouter

logger = logging.getLogger(__name__)


class LackeyGetGateway(GatewayRouter):
    """Gateway for all read operations."""

    def __init__(self, core_instance: Any = None) -> None:
        """Initialize the lackey_get gateway.

        Args:
            core_instance: Optional LackeyCore instance. If None, will get
                          from server or create new.
        """
        self._core_instance = core_instance
        super().__init__(gateway_name="lackey_get")

    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load intent classification patterns for read operations."""
        return {
            # Project queries
            "list_projects": [
                "list projects",
                "show projects",
                "all projects",
                "projects",
                "get projects",
                "project list",
                "show all projects",
            ],
            "get_project": [
                "get project",
                "show project",
                "project details",
                "project info",
                "project status",
                "describe project",
            ],
            # Task queries - simple listing without filters
            "list_project_tasks": [
                "list all tasks",
                "show all tasks",
                "get all tasks",
                "all tasks",
                "task list",
                "simple task list",
                "tasks in project",
                "project tasks",
                "what tasks",
                "tasks are there",
                "list tasks in",
                "tasks in the project",
                "what tasks are in",
                "tasks for project",
                "show tasks",
                "list tasks",
                "get tasks",
            ],
            "get_task": [
                "get task",
                "show task",
                "task details",
                "task info",
                "task status",
                "describe task",
            ],
            # Ready and blocked tasks
            "get_ready_tasks": [
                "ready tasks",
                "available tasks",
                "tasks ready",
                "ready to work",
                "unblocked tasks",
                "tasks I can do",
                "what tasks are ready",
                "tasks ready to work",
                "ready to work on",
                "tasks to work on",
            ],
            "get_blocked_tasks": [
                "blocked tasks",
                "tasks blocked",
                "dependencies blocking",
                "waiting tasks",
                "blocked by dependencies",
            ],
            # Progress and status
            "get_task_progress_summary": [
                "task progress",
                "progress",
                "how far",
                "completion status",
                "task status",
                "progress summary",
            ],
            # Notes
            "get_task_notes": [
                "task notes",
                "notes",
                "comments",
                "task comments",
                "show notes",
                "get notes",
            ],
            "search_task_notes": [
                "search notes",
                "find in notes",
                "search comments",
                "find notes",
                "note search",
            ],
            # Dependencies and validation
            "validate_project_dependencies": [
                "check dependencies",
                "validate deps",
                "dependency check",
                "validate dependencies",
                "check cycles",
            ],
            "validate_task_dependencies_integrity": [
                "integrity check",
                "validate integrity",
                "check integrity",
                "dependency integrity",
                "data integrity",
            ],
            # Analysis and stats
            "get_project_stats": [
                "project stats",
                "project statistics",
                "project summary",
                "project overview",
                "stats",
            ],
            # Search - filtered task queries
            "search_tasks": [
                "search tasks",
                "find tasks",
                "task search",
                "search for tasks",
                "find task",
                "show me all tasks that mention",
                "show me tasks that mention",
                "show all tasks that mention",
                "all tasks that mention",
                "list tasks with",
                "show tasks with",
                "get tasks with",
                "tasks with",
                "list high",
                "list low",
                "list medium",
                "list assigned",
                "list complexity",
                "list tagged",
                "filter tasks",
                "filtered tasks",
                "tasks assigned to",
                "tasks tagged",
                "complexity tasks",
                "assigned tasks",
                "tasks that mention",
                "tasks mentioning",
                "show me tasks",
                "find tasks that",
                "search for tasks that",
                "tasks containing",
                "tasks with text",
                "tasks about",
                "mention",
                "containing",
                "advanced search",
                "complex search",
                "filtered search",
                "search with filters",
                "detailed search",
                "multi-filter",
                "complex query",
                "advanced filter",
                "sophisticated search",
            ],
        }

    def _load_parameter_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load parameter mapping configurations for each tool."""
        return {
            "get_project": {"project_id": "context.project_id"},
            "list_projects": {"status_filter": "context.status_filter"},
            "list_project_tasks": {
                "project_id": (
                    "context.project_id,data.project_id,project_id,"
                    "context.project_name,data.project_name,project_name"
                ),
                "status_filter": "context.status_filter",
            },
            "get_task": {
                "task_id": "context.task_id",
            },
            "get_ready_tasks": {
                "project_id": "context.project_id",
                "assignee_filter": "context.assignee_filter",
            },
            "get_blocked_tasks": {
                "project_id": "context.project_id",
                "include_blocking_tasks": "context.include_blocking_tasks",
            },
            "get_task_progress_summary": {
                "project_id": "context.project_id",
                "task_id": "context.task_id",
            },
            "get_task_notes": {
                "project_id": "context.project_id",
                "task_id": "context.task_id",
                "author_filter": "context.author_filter",
            },
            "search_task_notes": {
                "project_id": "context.project_id",
                "query": "query",
                "author_filter": "context.author_filter",
            },
            "validate_project_dependencies": {
                "project_id": "context.project_id",
                "fix_cycles": "context.fix_cycles",
            },
            "validate_task_dependencies_integrity": {
                "project_id": "context.project_id"
            },
            "get_project_stats": {
                "project_id": "context.project_id",
                "include_tasks": "context.include_tasks",
            },
            "search_tasks": {
                "query": "query",
                "project_id": "context.project_id",
                "complexity": "infer",
                "assigned_to": "infer",
                "tags": "infer",
                "status": "infer",
            },
        }

    def _load_validation_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load validation schemas for each tool."""
        return {
            "get_project": {
                "type": "object",
                "properties": {"project_id": {"type": "string", "minLength": 1}},
                "required": ["project_id"],
            },
            "list_projects": {
                "type": "object",
                "properties": {
                    "status_filter": {
                        "type": "string",
                        "enum": ["active", "done", "archived"],
                    }
                },
            },
            "list_project_tasks": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "minLength": 1},
                    "status_filter": {
                        "type": "string",
                        "enum": ["todo", "in_progress", "blocked", "done"],
                    },
                },
                "required": ["project_id"],
            },
            "get_task": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "minLength": 1},
                },
                "required": ["task_id"],
            },
            "get_ready_tasks": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "minLength": 1},
                    "assignee_filter": {"type": "string"},
                },
                "required": ["project_id"],
            },
            "get_blocked_tasks": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "minLength": 1},
                    "include_blocking_tasks": {"type": "boolean"},
                },
                "required": ["project_id"],
            },
            "get_task_progress_summary": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "minLength": 1},
                    "task_id": {"type": "string", "minLength": 1},
                },
                "required": ["project_id", "task_id"],
            },
            "get_task_notes": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "minLength": 1},
                    "task_id": {"type": "string", "minLength": 1},
                    "author_filter": {"type": "string"},
                },
                "required": ["project_id", "task_id"],
            },
            "search_task_notes": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "minLength": 1},
                    "query": {"type": "string", "minLength": 1},
                    "author_filter": {"type": "string"},
                },
                "required": ["project_id", "query"],
            },
            "validate_project_dependencies": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "minLength": 1},
                    "fix_cycles": {"type": "boolean"},
                },
                "required": ["project_id"],
            },
            "validate_task_dependencies_integrity": {
                "type": "object",
                "properties": {"project_id": {"type": "string", "minLength": 1}},
                "required": ["project_id"],
            },
            "get_project_stats": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "minLength": 1},
                    "include_tasks": {"type": "boolean"},
                    "include_dependencies": {"type": "boolean"},
                },
                "required": ["project_id"],
            },
            "list_tasks": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "minLength": 1},
                    "status": {
                        "type": "string",
                        "enum": ["todo", "in_progress", "blocked", "done"],
                    },
                    "complexity": {"type": "string", "enum": ["low", "medium", "high"]},
                    "assigned_to": {"type": "string"},
                    "tag": {"type": "string"},
                },
            },
            "search_tasks": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "minLength": 1},
                    "project_id": {"type": "string", "minLength": 1},
                    "complexity": {"type": "string", "enum": ["low", "medium", "high"]},
                    "assigned_to": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "status": {
                        "type": "string",
                        "enum": ["todo", "in_progress", "blocked", "done"],
                    },
                    "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                },
                "required": ["query"],
            },
        }

    def _build_mapping_rules(self, intent: str) -> List[Any]:
        """Build parameter mapping rules with custom transformations."""
        from ..parameter_mapper import MappingRule

        # Get the base rules from parent
        rules = super()._build_mapping_rules(intent)

        # Add search term extraction for search_tasks query parameter
        if intent == "search_tasks":
            # Find and replace the query rule with one that has a transform function
            for i, rule in enumerate(rules):
                if rule.target_param == "query":
                    rules[i] = MappingRule(
                        source_path=rule.source_path,
                        target_param=rule.target_param,
                        transform_func=self._extract_search_terms_from_query,
                        condition=rule.condition,
                        default_value=rule.default_value,
                        required=rule.required,
                    )
                    break

        return rules

    def _extract_search_terms_from_query(self, query: str) -> str:
        """Extract search terms from natural language queries."""
        from ..parameter_mapper import AdvancedParameterMapper

        # Use the parameter mapper's search term extraction
        mapper = AdvancedParameterMapper()
        search_terms = mapper._extract_search_terms(query)

        # Return extracted terms or original query if no terms found
        return search_terms if search_terms else query

    def _load_tool_registry(self) -> Dict[str, Callable]:
        """Load registry of available tools for this gateway."""
        try:
            from lackey.core import LackeyCore

            # Use injected instance if provided
            if self._core_instance is not None:
                lackey_core = self._core_instance
            else:
                # Try to get core instance from server first
                lackey_core = None
                try:
                    from lackey.mcp.server import lackey_core as server_core

                    lackey_core = server_core
                except ImportError:
                    pass

                # If no server core, create a temporary one for testing
                if lackey_core is None:
                    logger.warning(
                        "LackeyCore not initialized in server, creating "
                        "temporary instance for testing"
                    )
                    lackey_core = LackeyCore()

            return {
                "list_projects": lackey_core.list_projects,
                "get_project": lackey_core.get_project,
                "list_project_tasks": lackey_core.list_project_tasks,
                "get_task": lackey_core.get_task,
                "get_ready_tasks": lackey_core.get_ready_tasks,
                "get_blocked_tasks": lackey_core.get_blocked_tasks,
                "get_task_progress_summary": lackey_core.get_task_progress_summary,
                "get_task_notes": lackey_core.get_task_notes,
                "search_task_notes": lackey_core.search_task_notes,
                "validate_project_dependencies": (
                    lackey_core.validate_project_dependencies
                ),
                "validate_task_dependencies_integrity": (
                    lackey_core.validate_task_dependencies_integrity
                ),
                "get_project_stats": lackey_core.get_project_stats,
                "search_tasks": lackey_core.search_tasks,
            }

        except Exception as e:
            logger.error(f"Failed to load tool registry: {e}")
            return {}
