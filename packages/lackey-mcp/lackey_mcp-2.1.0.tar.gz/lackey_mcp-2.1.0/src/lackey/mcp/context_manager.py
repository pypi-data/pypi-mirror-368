"""Context management system for intelligent parameter inference and defaults.

This module provides contextual awareness for gateway operations, enabling
intelligent parameter inference, default value management, and context-aware
routing decisions.
"""

import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ProjectContext:
    """Context information about the current project."""

    project_id: Optional[str] = None
    project_name: Optional[str] = None
    project_path: Optional[str] = None
    last_accessed: Optional[float] = None
    task_count: int = 0
    active_tasks: List[str] = field(default_factory=list)
    recent_tasks: List[str] = field(default_factory=list)
    common_assignees: Set[str] = field(default_factory=set)
    default_complexity: str = "medium"


@dataclass
class UserContext:
    """Context information about the current user."""

    user_id: Optional[str] = None
    preferred_assignee: Optional[str] = None
    recent_projects: List[str] = field(default_factory=list)
    recent_tasks: List[str] = field(default_factory=list)
    common_statuses: Dict[str, int] = field(default_factory=dict)
    working_directory: Optional[str] = None
    session_start: float = field(default_factory=time.time)


@dataclass
class SessionContext:
    """Context information about the current session."""

    session_id: str
    start_time: float
    last_activity: float
    operation_history: List[Dict[str, Any]] = field(default_factory=list)
    parameter_cache: Dict[str, Any] = field(default_factory=dict)
    inference_patterns: Dict[str, int] = field(default_factory=dict)
    error_patterns: Dict[str, int] = field(default_factory=dict)


class ContextInferenceEngine:
    """Engine for intelligent parameter inference based on context."""

    def __init__(self) -> None:
        """Initialize the context inference engine."""
        self.inference_rules = self._load_inference_rules()
        self.pattern_weights = self._load_pattern_weights()

    def _load_inference_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load parameter inference rules."""
        return {
            "project_id": {
                "sources": [
                    "current_project_context",
                    "working_directory_analysis",
                    "recent_operation_history",
                    "environment_variables",
                ],
                "confidence_threshold": 0.7,
                "fallback_strategy": "prompt_user",
            },
            "task_id": {
                "sources": [
                    "recent_task_operations",
                    "current_task_context",
                    "partial_id_matching",
                    "task_title_similarity",
                ],
                "confidence_threshold": 0.8,
                "fallback_strategy": "list_recent_tasks",
            },
            "assignee": {
                "sources": [
                    "user_preference",
                    "project_team_members",
                    "recent_assignments",
                    "task_complexity_matching",
                ],
                "confidence_threshold": 0.6,
                "fallback_strategy": "use_current_user",
            },
            "complexity": {
                "sources": [
                    "task_description_analysis",
                    "step_count_analysis",
                    "keyword_analysis",
                    "project_defaults",
                ],
                "confidence_threshold": 0.5,
                "fallback_strategy": "use_medium",
            },
            "status": {
                "sources": [
                    "operation_intent_analysis",
                    "current_task_status",
                    "workflow_patterns",
                    "user_preferences",
                ],
                "confidence_threshold": 0.7,
                "fallback_strategy": "use_todo",
            },
        }

    def _load_pattern_weights(self) -> Dict[str, float]:
        """Load weights for different inference patterns."""
        return {
            "exact_match": 1.0,
            "partial_match": 0.8,
            "fuzzy_match": 0.6,
            "context_inference": 0.7,
            "historical_pattern": 0.5,
            "default_fallback": 0.3,
        }

    async def infer_parameter(
        self, param_name: str, current_value: Any, context: "ContextManager"
    ) -> Tuple[Any, float]:
        """Infer parameter value with confidence score."""
        if current_value is not None:
            return current_value, 1.0

        if param_name not in self.inference_rules:
            return None, 0.0

        rule = self.inference_rules[param_name]
        best_value = None
        best_confidence = 0.0

        for source in rule["sources"]:
            try:
                value, confidence = await self._apply_inference_source(
                    param_name, source, context
                )
                if confidence > best_confidence:
                    best_value = value
                    best_confidence = confidence
            except Exception as e:
                logger.debug(f"Inference source {source} failed for {param_name}: {e}")

        # Apply fallback strategy if confidence is too low
        if best_confidence < rule["confidence_threshold"]:
            fallback_value, fallback_confidence = await self._apply_fallback_strategy(
                param_name, rule["fallback_strategy"], context
            )
            if fallback_confidence > best_confidence:
                best_value = fallback_value
                best_confidence = fallback_confidence

        return best_value, best_confidence

    async def _apply_inference_source(
        self, param_name: str, source: str, context: "ContextManager"
    ) -> Tuple[Any, float]:
        """Apply specific inference source."""
        if source == "current_project_context":
            return await self._infer_from_project_context(param_name, context)
        elif source == "working_directory_analysis":
            return await self._infer_from_working_directory(param_name, context)
        elif source == "recent_operation_history":
            return await self._infer_from_operation_history(param_name, context)
        elif source == "environment_variables":
            return await self._infer_from_environment(param_name, context)
        elif source == "recent_task_operations":
            return await self._infer_from_recent_tasks(param_name, context)
        elif source == "user_preference":
            return await self._infer_from_user_preferences(param_name, context)
        elif source == "task_description_analysis":
            return await self._infer_from_task_description(param_name, context)
        elif source == "project_team_members":
            return await self._infer_from_team_members(param_name, context)
        else:
            return None, 0.0

    async def _infer_from_project_context(
        self, param_name: str, context: "ContextManager"
    ) -> Tuple[Any, float]:
        """Infer parameter from current project context."""
        if param_name == "project_id" and context.project_context.project_id:
            return context.project_context.project_id, 0.9
        elif param_name == "complexity" and context.project_context.default_complexity:
            return context.project_context.default_complexity, 0.6
        elif param_name == "assignee" and context.project_context.common_assignees:
            # Return most common assignee
            assignees = list(context.project_context.common_assignees)
            return assignees[0] if assignees else None, 0.7

        return None, 0.0

    async def _infer_from_working_directory(
        self, param_name: str, context: "ContextManager"
    ) -> Tuple[Any, float]:
        """Infer parameter from working directory analysis."""
        if param_name != "project_id":
            return None, 0.0

        working_dir = context.user_context.working_directory
        if not working_dir:
            working_dir = os.getcwd()

        # Look for .lackey directory or project indicators
        lackey_dir = Path(working_dir) / ".lackey"
        if lackey_dir.exists():
            try:
                # Try to read project configuration
                config_file = lackey_dir / "config.yaml"
                if config_file.exists():
                    # This would parse the config to get project ID
                    # For now, return None as we'd need to integrate with storage
                    return None, 0.0
            except (OSError, IOError, ValueError):
                # Ignore file system and parsing errors
                pass

        return None, 0.0

    async def _infer_from_operation_history(
        self, param_name: str, context: "ContextManager"
    ) -> Tuple[Any, float]:
        """Infer parameter from recent operation history."""
        history = context.session_context.operation_history
        if not history:
            return None, 0.0

        # Look for recent operations with the same parameter
        recent_values = []
        for operation in reversed(history[-10:]):  # Last 10 operations
            if param_name in operation.get("parameters", {}):
                recent_values.append(operation["parameters"][param_name])

        if recent_values:
            # Return most recent value
            return recent_values[0], 0.8

        return None, 0.0

    async def _infer_from_environment(
        self, param_name: str, context: "ContextManager"
    ) -> Tuple[Any, float]:
        """Infer parameter from environment variables."""
        env_mappings = {
            "project_id": ["LACKEY_PROJECT_ID", "CURRENT_PROJECT_ID"],
            "assignee": ["LACKEY_DEFAULT_ASSIGNEE", "USER", "USERNAME"],
        }

        if param_name in env_mappings:
            for env_var in env_mappings[param_name]:
                value = os.environ.get(env_var)
                if value:
                    return value, 0.6

        return None, 0.0

    async def _infer_from_recent_tasks(
        self, param_name: str, context: "ContextManager"
    ) -> Tuple[Any, float]:
        """Infer parameter from recent task operations."""
        if param_name == "task_id" and context.project_context.recent_tasks:
            # Return most recent task
            return context.project_context.recent_tasks[0], 0.7

        return None, 0.0

    async def _infer_from_user_preferences(
        self, param_name: str, context: "ContextManager"
    ) -> Tuple[Any, float]:
        """Infer parameter from user preferences."""
        if param_name == "assignee" and context.user_context.preferred_assignee:
            return context.user_context.preferred_assignee, 0.8

        return None, 0.0

    async def _infer_from_task_description(
        self, param_name: str, context: "ContextManager"
    ) -> Tuple[Any, float]:
        """Infer parameter from task description analysis."""
        if param_name != "complexity":
            return None, 0.0

        # This would analyze task description for complexity indicators
        # For now, return default
        return "medium", 0.4

    async def _infer_from_team_members(
        self, param_name: str, context: "ContextManager"
    ) -> Tuple[Any, float]:
        """Infer parameter from project team members."""
        if param_name == "assignee" and context.project_context.common_assignees:
            assignees = list(context.project_context.common_assignees)
            return assignees[0] if assignees else None, 0.6

        return None, 0.0

    async def _apply_fallback_strategy(
        self, param_name: str, strategy: str, context: "ContextManager"
    ) -> Tuple[Any, float]:
        """Apply fallback strategy for parameter inference."""
        if strategy == "prompt_user":
            # In a real implementation, this would prompt the user
            return None, 0.0
        elif strategy == "list_recent_tasks":
            # Return indication that recent tasks should be listed
            return "LIST_RECENT_TASKS", 0.5
        elif strategy == "use_current_user":
            user = os.environ.get("USER") or os.environ.get("USERNAME")
            return user, 0.5 if user else 0.0
        elif strategy == "use_medium":
            return "medium", 0.5
        elif strategy == "use_todo":
            return "todo", 0.5

        return None, 0.0


class ContextManager:
    """Main context management system for gateway operations."""

    def __init__(self, lackey_core: Any = None) -> None:
        """Initialize the context manager."""
        self.lackey_core = lackey_core
        self.project_context = ProjectContext()
        self.user_context = UserContext()
        self.session_context = SessionContext(
            session_id=f"session_{int(time.time())}",
            start_time=time.time(),
            last_activity=time.time(),
        )
        self.inference_engine = ContextInferenceEngine()

        # Initialize user context
        self._initialize_user_context()

    def _initialize_user_context(self) -> None:
        """Initialize user context from environment."""
        self.user_context.working_directory = os.getcwd()
        self.user_context.user_id = os.environ.get("USER") or os.environ.get("USERNAME")
        self.user_context.preferred_assignee = self.user_context.user_id

    async def update_project_context(self, project_id: str) -> None:
        """Update project context with current project information."""
        if not self.lackey_core:
            return

        try:
            # This would integrate with LackeyCore to get project info
            self.project_context.project_id = project_id
            self.project_context.last_accessed = time.time()

            # Update recent projects
            if project_id not in self.user_context.recent_projects:
                self.user_context.recent_projects.insert(0, project_id)
                self.user_context.recent_projects = self.user_context.recent_projects[
                    :10
                ]

            logger.debug(f"Updated project context for: {project_id}")

        except Exception as e:
            logger.warning(f"Failed to update project context: {e}")

    async def update_task_context(self, task_id: str) -> None:
        """Update task context with current task information."""
        if not self.lackey_core:
            return

        try:
            # Update recent tasks
            if task_id not in self.project_context.recent_tasks:
                self.project_context.recent_tasks.insert(0, task_id)
                self.project_context.recent_tasks = self.project_context.recent_tasks[
                    :20
                ]

            if task_id not in self.user_context.recent_tasks:
                self.user_context.recent_tasks.insert(0, task_id)
                self.user_context.recent_tasks = self.user_context.recent_tasks[:50]

            logger.debug(f"Updated task context for: {task_id}")

        except Exception as e:
            logger.warning(f"Failed to update task context: {e}")

    async def record_operation(
        self,
        operation: str,
        parameters: Dict[str, Any],
        result: Any = None,
        success: bool = True,
    ) -> None:
        """Record operation in session history for context learning."""
        operation_record = {
            "timestamp": time.time(),
            "operation": operation,
            "parameters": parameters.copy(),
            "success": success,
            "result_type": type(result).__name__ if result else None,
        }

        self.session_context.operation_history.append(operation_record)
        self.session_context.last_activity = time.time()

        # Keep only recent operations
        if len(self.session_context.operation_history) > 100:
            self.session_context.operation_history = (
                self.session_context.operation_history[-100:]
            )

        # Update parameter cache with successful parameters
        if success:
            for param, value in parameters.items():
                if value is not None:
                    self.session_context.parameter_cache[param] = value

        # Update context based on operation
        if "project_id" in parameters:
            await self.update_project_context(parameters["project_id"])

        if "task_id" in parameters:
            await self.update_task_context(parameters["task_id"])

        if "assignee" in parameters:
            self.project_context.common_assignees.add(parameters["assignee"])

    async def infer_missing_parameters(
        self, tool_name: str, current_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Infer missing parameters using context and intelligence."""
        inferred: Dict[str, Any] = {}

        # Get required parameters for this tool
        from lackey.mcp.gateway_schemas import get_schema_for_tool

        schema = get_schema_for_tool(tool_name)
        if not schema:
            return inferred

        required_params = schema.get("required", [])
        optional_params = schema.get("optional", {})

        # Infer missing required parameters
        for param in required_params:
            if param not in current_parameters or current_parameters[param] is None:
                value, confidence = await self.inference_engine.infer_parameter(
                    param, current_parameters.get(param), self
                )
                if value is not None and confidence > 0.5:
                    inferred[param] = value
                    logger.debug(
                        f"Inferred {param}={value} (confidence: {confidence:.2f})"
                    )

        # Infer useful optional parameters
        for param, default_value in optional_params.items():
            if param not in current_parameters:
                value, confidence = await self.inference_engine.infer_parameter(
                    param, None, self
                )
                if value is not None and confidence > 0.6:
                    inferred[param] = value
                    logger.debug(
                        f"Inferred optional {param}={value} "
                        f"(confidence: {confidence:.2f})"
                    )
                elif default_value is not None:
                    inferred[param] = default_value

        return inferred

    async def get_contextual_suggestions(
        self, tool_name: str, partial_parameters: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Get contextual suggestions for parameter completion."""
        suggestions = {}

        # Project ID suggestions
        if "project_id" in partial_parameters and not partial_parameters["project_id"]:
            suggestions["project_id"] = self.user_context.recent_projects[:5]

        # Task ID suggestions
        if "task_id" in partial_parameters and not partial_parameters["task_id"]:
            suggestions["task_id"] = self.project_context.recent_tasks[:10]

        # Assignee suggestions
        if "assignee" in partial_parameters and not partial_parameters["assignee"]:
            assignees = list(self.project_context.common_assignees)
            if self.user_context.preferred_assignee:
                assignees.insert(0, self.user_context.preferred_assignee)
            suggestions["assignee"] = assignees[:5]

        # Status suggestions based on current context
        if "status" in partial_parameters and not partial_parameters["status"]:
            common_statuses = sorted(
                self.user_context.common_statuses.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            suggestions["status"] = [status for status, _ in common_statuses[:4]]
            if not suggestions["status"]:
                suggestions["status"] = ["todo", "in_progress", "done", "blocked"]

        return suggestions

    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context state."""
        return {
            "project": {
                "current_project_id": self.project_context.project_id,
                "recent_projects": len(self.user_context.recent_projects),
                "active_tasks": len(self.project_context.active_tasks),
                "common_assignees": len(self.project_context.common_assignees),
            },
            "session": {
                "session_id": self.session_context.session_id,
                "duration_minutes": (time.time() - self.session_context.start_time)
                / 60,
                "operations_count": len(self.session_context.operation_history),
                "cached_parameters": len(self.session_context.parameter_cache),
            },
            "user": {
                "working_directory": self.user_context.working_directory,
                "preferred_assignee": self.user_context.preferred_assignee,
                "recent_tasks": len(self.user_context.recent_tasks),
            },
        }

    def clear_context(self) -> None:
        """Clear all context data."""
        self.project_context = ProjectContext()
        self.user_context = UserContext()
        self.session_context = SessionContext(
            session_id=f"session_{int(time.time())}",
            start_time=time.time(),
            last_activity=time.time(),
        )
        self._initialize_user_context()
        logger.info("Context cleared and reinitialized")
