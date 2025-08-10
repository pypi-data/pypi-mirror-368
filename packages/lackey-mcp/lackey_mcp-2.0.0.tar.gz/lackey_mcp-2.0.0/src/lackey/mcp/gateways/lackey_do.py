"""lackey_do gateway for state modification operations."""

import logging
from typing import Any, Callable, Dict, List

from ...models import TaskStatus
from ..gateway_router import GatewayRouter

logger = logging.getLogger(__name__)


class LackeyDoGateway(GatewayRouter):
    """Gateway for all state modification operations."""

    def __init__(self) -> None:
        """Initialize the lackey_do gateway."""
        super().__init__(gateway_name="lackey_do")

    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load intent classification patterns for state modification operations."""
        return {
            # Task creation patterns
            "create_task": [
                "create task",
                "new task",
                "make task",
                "create_task",
                "task create",
                "build task",
            ],
            # Project creation patterns
            "create_project": [
                "create project",
                "new project",
                "add project",
                "make project",
                "create_project",
                "project create",
                "build project",
            ],
            # Task status update patterns
            "update_task_status": [
                "update task status",
                "update status",
                "change status",
                "set status",
                "mark as",
                "update_task_status",
                "status update",
                "task status",
                "update task.*status",
                "change task status",
                "set task status",
                "status to",
                "mark task",
                "task.*status.*to",
            ],
            # Task assignment patterns
            "assign_task": [
                "assign task",
                "assign to",
                "give task to",
                "delegate task",
                "assign_task",
                "task assign",
                "set assignee",
            ],
            # Task reassignment patterns
            "reassign_task": [
                "reassign task",
                "reassign to",
                "change assignee",
                "move task to",
                "reassign_task",
                "task reassign",
                "transfer task",
            ],
            # Task completion patterns
            "complete_task_steps": [
                "complete steps",
                "finish steps",
                "mark steps done",
                "steps complete",
                "complete_task_steps",
                "step completion",
                "finish task steps",
            ],
            # Dependency management patterns
            "add_task_dependencies": [
                "add dependency",
                "depends on",
                "requires",
                "add dep",
                "add_task_dependencies",
                "dependency add",
                "task depends",
                "add dependencies",
                "add dependencies to task",
                "task dependencies",
            ],
            "remove_task_dependencies": [
                "remove dependency",
                "no longer depends",
                "remove dep",
                "unblock",
                "remove_task_dependencies",
                "dependency remove",
                "remove dep",
            ],
            # Task deletion patterns
            "delete_task": [
                "delete task",
                "remove task permanently",
                "destroy task",
                "eliminate task",
                "delete_task",
                "task deletion",
                "permanently remove",
            ],
            # Project deletion patterns
            "delete_project": [
                "delete project",
                "remove project",
                "destroy project",
                "eliminate project",
                "delete_project",
                "project deletion",
                "permanently remove project",
            ],
            # Task archival patterns
            "archive_task": [
                "archive task",
                "archive",
                "remove task",
                "delete task",
                "archive_task",
                "task archive",
                "put away",
            ],
            # Task cloning patterns
            "clone_task": [
                "clone task",
                "copy task",
                "duplicate task",
                "replicate task",
                "clone_task",
                "task clone",
                "task copy",
            ],
            # Bulk operations patterns
            "bulk_assign_tasks": [
                "bulk assign",
                "assign multiple",
                "batch assign",
                "mass assign",
                "bulk_assign_tasks",
                "assign all",
                "multiple assign",
            ],
            "bulk_update_task_status": [
                "bulk update",
                "update multiple",
                "batch update",
                "mass update",
                "bulk_update_task_status",
                "update all",
                "multiple update",
                "bulk update task status",
                "bulk update status",
                "update multiple tasks",
            ],
            # Note addition patterns
            "add_task_note": [
                "add note",
                "note",
                "comment on task",
                "add comment",
                "add_task_note",
                "task note",
                "note task",
            ],
            # Project update patterns
            "update_project": [
                "update project",
                "change project",
                "modify project",
                "edit project",
                "update_project",
                "project update",
                "project change",
            ],
        }

    def _load_parameter_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load parameter mapping configurations for each tool."""
        return {
            "create_task": {
                "project_id": "data.project_id,target.project_id,project_id",
                "title": "data.title,target.title,title",
                "objective": "data.objective,target.objective,objective",
                "steps": "data.steps,target.steps,steps",
                "success_criteria": (
                    "data.success_criteria,target.success_criteria,success_criteria"
                ),
                "complexity": "data.complexity,target.complexity,complexity",
                "context": "data.context,target.context,context",
                "assigned_to": "data.assigned_to,target.assigned_to,assigned_to",
                "tags": "data.tags,target.tags,tags",
                "dependencies": "data.dependencies,target.dependencies,dependencies",
            },
            "create_project": {
                "friendly_name": (
                    "data.friendly_name,target.friendly_name,"
                    "parameters.friendly_name,friendly_name"
                ),
                "description": (
                    "data.description,target.description,"
                    "parameters.description,description"
                ),
                "objectives": (
                    "data.objectives,target.objectives,"
                    "parameters.objectives,objectives"
                ),
                "tags": "data.tags,target.tags,parameters.tags,tags",
                "metadata": (
                    "data.metadata,target.metadata,parameters.metadata,metadata"
                ),
            },
            "update_task_status": {
                "project_id": (
                    "data.project_id,target.project_id,"
                    "parameters.project_id,project_id"
                ),
                "task_id": "data.task_id,parameters.task_id,task_id",
                "new_status": "data.new_status,parameters.new_status,new_status",
                "note": "data.note,parameters.note,note",
            },
            "assign_task": {
                "project_id": (
                    "data.project_id,target.project_id,"
                    "parameters.project_id,project_id"
                ),
                "task_id": "data.task_id,parameters.task_id,task_id",
                "assignee": (
                    "data.assignee,parameters.assignee,assignee,"
                    "data.assigned_to,parameters.assigned_to,assigned_to"
                ),
                "note": "data.note,parameters.note,note",
            },
            "reassign_task": {
                "project_id": ("data.project_id,parameters.project_id,project_id"),
                "task_id": "data.task_id,parameters.task_id,task_id",
                "assigned_to": (
                    "data.assignee,parameters.assignee,assignee,"
                    "data.assigned_to,parameters.assigned_to,assigned_to"
                ),
            },
            "complete_task_steps": {
                "project_id": "data.project_id,parameters.project_id,project_id",
                "task_id": "data.task_id,parameters.task_id,task_id",
                "step_indices": (
                    "data.step_indices,parameters.step_indices,step_indices"
                ),
                "note": "data.note,parameters.note,note",
                "auto_complete": (
                    "data.auto_complete,parameters.auto_complete,auto_complete"
                ),
            },
            "add_task_dependencies": {
                "project_id": "data.project_id,parameters.project_id,project_id",
                "task_id": "data.task_id,parameters.task_id,task_id",
                "dependency_ids": (
                    "data.dependency_ids,parameters.dependency_ids,dependency_ids"
                ),
            },
            "remove_task_dependencies": {
                "project_id": "data.project_id,parameters.project_id,project_id",
                "task_id": "data.task_id,parameters.task_id,task_id",
                "dependency_ids": (
                    "data.dependency_ids,parameters.dependency_ids,dependency_ids"
                ),
            },
            "delete_task": {
                "task_id": "data.task_id,parameters.task_id,task_id",
            },
            "delete_project": {
                "project_id": "data.project_id,parameters.project_id,project_id",
            },
            "archive_task": {
                "project_id": "data.project_id,parameters.project_id,project_id",
                "task_id": "data.task_id,parameters.task_id,task_id",
            },
            "clone_task": {
                "project_id": "data.project_id,parameters.project_id,project_id",
                "task_id": "data.task_id,parameters.task_id,task_id",
                "new_title": "data.new_title,parameters.new_title,new_title",
                "assigned_to": (
                    "data.assignee,parameters.assignee,assignee,"
                    "data.assigned_to,parameters.assigned_to,assigned_to"
                ),
            },
            "bulk_assign_tasks": {
                "project_id": "data.project_id,parameters.project_id,project_id",
                "task_ids": "data.task_ids,parameters.task_ids,task_ids",
                "assigned_to": (
                    "data.assignee,parameters.assignee,assignee,"
                    "data.assigned_to,parameters.assigned_to,assigned_to"
                ),
            },
            "bulk_update_task_status": {
                "project_id": ("data.project_id,parameters.project_id,project_id"),
                "task_ids": "data.task_ids,parameters.task_ids,task_ids",
                "new_status": ("data.new_status,parameters.new_status,new_status"),
                "note": "data.note,parameters.note,note",
            },
            "add_task_note": {
                "project_id": "data.project_id,parameters.project_id,project_id",
                "task_id": "data.task_id,parameters.task_id,task_id",
                "content": (
                    "data.content,parameters.content,content,"
                    "data.note,parameters.note,note"
                ),
                "note_type": "data.note_type,parameters.note_type,note_type",
            },
            "update_project": {
                "project_id": "data.project_id,parameters.project_id,project_id",
                "friendly_name": (
                    "data.friendly_name,parameters.friendly_name,friendly_name"
                ),
                "description": "data.description,parameters.description,description",
                "context": "data.context,parameters.context,context",
                "tags": "data.tags,parameters.tags,tags",
            },
        }

    def _load_validation_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load validation schemas for each tool."""
        from lackey.mcp.gateway_schemas import LACKEY_DO_SCHEMAS

        from ..parameter_mapper import ParameterSchema, ParameterType

        # Convert the centralized schema format to ParameterSchema objects
        converted_schemas: Dict[str, Dict[str, Any]] = {}
        for tool_name, schema_def in LACKEY_DO_SCHEMAS.items():
            schema_dict = schema_def
            converted_schemas[tool_name] = {}

            # Convert required parameters
            for param in schema_dict.get("required", []):
                param_type_str = schema_dict.get("types", {}).get(param, "string")

                # Map parameter type to ParameterType enum
                if param_type_str == "str":
                    param_type = ParameterType.STRING
                elif param_type_str == "enum":
                    param_type = ParameterType.ENUM
                elif param_type_str == "list[str]":
                    param_type = ParameterType.LIST
                elif param_type_str == "bool":
                    param_type = ParameterType.BOOLEAN
                else:
                    param_type = ParameterType.STRING

                # Special handling for status parameters - use enum type
                if param in ["new_status", "status"]:
                    param_type = ParameterType.ENUM
                    allowed_values = ["todo", "in_progress", "blocked", "done"]
                elif param == "note_type":
                    param_type = ParameterType.ENUM
                    allowed_values = [
                        "user",
                        "system",
                        "status_change",
                        "assignment",
                        "progress",
                        "dependency",
                        "archive",
                    ]
                else:
                    allowed_values = (
                        schema_dict.get("constraints", {})
                        .get(param, {})
                        .get("allowed_values")
                    )

                converted_schemas[tool_name][param] = ParameterSchema(
                    name=param,
                    param_type=param_type,
                    required=True,
                    allowed_values=allowed_values,
                )

            # Convert optional parameters
            for param, default in schema_dict.get("optional", {}).items():
                param_type_str = schema_dict.get("types", {}).get(param, "string")

                # Map parameter type to ParameterType enum
                if param_type_str.startswith("optional["):
                    inner_type = param_type_str[9:-1]  # Remove "optional[" and "]"
                    if inner_type == "str":
                        param_type = ParameterType.STRING
                    elif inner_type == "list[str]":
                        param_type = ParameterType.LIST
                    elif inner_type == "bool":
                        param_type = ParameterType.BOOLEAN
                    else:
                        param_type = ParameterType.STRING
                else:
                    param_type = ParameterType.STRING

                # Special handling for status parameters
                if param in ["new_status", "status"]:
                    param_type = ParameterType.ENUM
                    allowed_values = ["todo", "in_progress", "blocked", "done"]
                elif param == "note_type":
                    param_type = ParameterType.ENUM
                    allowed_values = [
                        "user",
                        "system",
                        "status_change",
                        "assignment",
                        "progress",
                        "dependency",
                        "archive",
                    ]
                else:
                    allowed_values = (
                        schema_dict.get("constraints", {})
                        .get(param, {})
                        .get("allowed_values")
                    )

                converted_schemas[tool_name][param] = ParameterSchema(
                    name=param,
                    param_type=param_type,
                    required=False,
                    default=default,
                    allowed_values=allowed_values,
                )

        return converted_schemas

    def _load_tool_registry(self) -> Dict[str, Callable]:
        """Load registry of available tools for this gateway."""
        # Import here to avoid circular imports
        from lackey.core import LackeyCore

        try:
            # Initialize LackeyCore - the MCP server will ensure proper initialization
            # with the correct lackey_dir_path before creating gateways
            core = LackeyCore()

            return {
                "create_task": core.create_task,
                "create_project": core.create_project,
                "update_task_status": core.update_task_status,
                "assign_task": core.assign_task,
                "reassign_task": core.reassign_task,
                "complete_task_steps": core.complete_task_steps,
                "add_task_dependencies": core.add_task_dependencies,
                "remove_task_dependencies": core.remove_task_dependencies,
                "archive_task": core.archive_task,
                "delete_task": core.delete_task,
                "delete_project": core.delete_project,
                "clone_task": core.clone_task,
                "bulk_assign_tasks": core.bulk_assign_tasks,
                "bulk_update_task_status": core.bulk_update_task_status,
                "add_task_note": core.add_task_note,
                "update_project": core.update_project,
            }

        except Exception as e:
            logger.error(f"Failed to initialize LackeyCore for tool registry: {e}")
            # Return empty registry - tools will fail with clear error messages
            return {}

    def _convert_status_to_enum(self, status_str: str) -> TaskStatus:
        """Convert string status to TaskStatus enum."""
        if isinstance(status_str, TaskStatus):
            return status_str

        # Handle common status string variations
        status_map = {
            "todo": TaskStatus.TODO,
            "in_progress": TaskStatus.IN_PROGRESS,
            "in-progress": TaskStatus.IN_PROGRESS,
            "inprogress": TaskStatus.IN_PROGRESS,
            "progress": TaskStatus.IN_PROGRESS,
            "active": TaskStatus.IN_PROGRESS,
            "done": TaskStatus.DONE,
            "completed": TaskStatus.DONE,
            "complete": TaskStatus.DONE,
            "blocked": TaskStatus.BLOCKED,
        }

        normalized = status_str.lower().strip()
        if normalized in status_map:
            return status_map[normalized]

        # Try direct enum lookup
        try:
            return TaskStatus(status_str.lower())
        except ValueError:
            raise ValueError(
                f"Invalid task status: {status_str}. "
                f"Valid options: {list(status_map.keys())}"
            )

    async def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute tool with standardized parameter handling."""
        # Call parent implementation directly - no special-case handling
        return await super()._execute_tool(tool_name, parameters)
