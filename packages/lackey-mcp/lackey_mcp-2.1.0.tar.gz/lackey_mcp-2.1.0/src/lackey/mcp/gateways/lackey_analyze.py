"""lackey_analyze gateway for analysis operations."""

import logging
from typing import Any, Callable, Dict, List

from ..gateway_router import GatewayRouter

logger = logging.getLogger(__name__)


class LackeyAnalyzeGateway(GatewayRouter):
    """Gateway for all analysis operations."""

    def __init__(self, lackey_core: Any = None) -> None:
        """Initialize the lackey_analyze gateway."""
        self._custom_core = lackey_core
        super().__init__(gateway_name="lackey_analyze")

    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load intent classification patterns for analysis operations."""
        return {
            # Dependency analysis patterns
            "analyze_project_dependencies": [
                "analyze dependencies",
                "dependency analysis",
                "check dependencies",
                "validate dependencies",
                "dependency check",
                "deps analysis",
            ],
            # Critical path analysis patterns
            "analyze_critical_path": [
                "critical path",
                "analyze critical path",
                "critical path analysis",
                "longest path",
                "path analysis",
            ],
            "get_critical_path_analysis": [
                "get critical path",
                "show critical path",
                "critical path details",
                "path analysis results",
                "critical path info",
            ],
            # Task impact analysis patterns
            "analyze_task_impact": [
                "task impact",
                "analyze impact",
                "impact analysis",
                "task dependencies impact",
                "dependency impact",
            ],
            # Workload analysis patterns
            "get_workload_analysis": [
                "workload analysis",
                "analyze workload",
                "capacity analysis",
                "resource analysis",
                "team workload",
                "assignment analysis",
            ],
            # Bottleneck analysis patterns
            "get_bottleneck_analysis": [
                "bottleneck analysis",
                "find bottlenecks",
                "analyze bottlenecks",
                "performance bottlenecks",
                "workflow bottlenecks",
            ],
            # Project statistics patterns
            "get_project_stats": [
                "project stats",
                "project statistics",
                "project metrics",
                "project summary",
                "stats",
                "metrics",
            ],
            # System health patterns
            "get_system_health": [
                "system health",
                "health check",
                "system status",
                "overall health",
            ],
            "get_system_diagnostics": [
                "system diagnostics",
                "diagnostics",
                "system info",
                "diagnostic report",
                "system analysis",
            ],
            # Performance metrics patterns
            "get_performance_metrics": [
                "performance metrics",
                "performance stats",
                "performance analysis",
                "system performance",
                "metrics",
                "performance data",
            ],
            # Visualization patterns
            "generate_dependency_visualization": [
                "dependency visualization",
                "visualize dependencies",
                "dependency graph",
                "dependency diagram",
                "visual dependencies",
            ],
        }

    def _load_parameter_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load parameter mapping configurations for each analysis tool."""
        return {
            "analyze_project_dependencies": {"project_id": "scope.project_id"},
            "analyze_critical_path": {"project_id": "scope.project_id"},
            "get_critical_path_analysis": {"project_id": "scope.project_id"},
            "analyze_task_impact": {
                "project_id": "scope.project_id",
                "task_id": "scope.task_id",
            },
            "get_workload_analysis": {
                "project_id": "scope.project_id",
                "assignee": "scope.assignee",
            },
            "get_bottleneck_analysis": {"project_id": "scope.project_id"},
            "get_project_stats": {"project_id": "scope.project_id"},
            "get_system_health": {},
            "get_system_diagnostics": {},
            "get_performance_metrics": {"hours": "scope.hours"},
            "generate_dependency_visualization": {
                "project_id": "scope.project_id",
                "format_type": "scope.format_type",
                "include_labels": "scope.include_labels",
            },
        }

    def _load_validation_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load validation schemas for each analysis tool."""
        return {
            "analyze_project_dependencies": {
                "project_id": {
                    "required": False,
                    "type": "string",
                    "default": "default",
                }
            },
            "analyze_critical_path": {
                "project_id": {
                    "required": False,
                    "type": "string",
                    "default": "default",
                }
            },
            "get_critical_path_analysis": {
                "project_id": {
                    "required": False,
                    "type": "string",
                    "default": "default",
                }
            },
            "analyze_task_impact": {
                "project_id": {
                    "required": False,
                    "type": "string",
                    "default": "default",
                },
                "task_id": {"required": True, "type": "string"},
            },
            "get_workload_analysis": {
                "project_id": {
                    "required": False,
                    "type": "string",
                    "default": "default",
                },
                "assignee": {"required": False, "type": "string"},
            },
            "get_bottleneck_analysis": {
                "project_id": {
                    "required": False,
                    "type": "string",
                    "default": "default",
                }
            },
            "get_project_stats": {
                "project_id": {
                    "required": False,
                    "type": "string",
                    "default": "default",
                }
            },
            "get_system_health": {},
            "get_system_diagnostics": {},
            "get_performance_metrics": {
                "hours": {
                    "required": False,
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 168,
                }
            },
            "generate_dependency_visualization": {
                "project_id": {
                    "required": False,
                    "type": "string",
                    "default": "default",
                },
                "format_type": {
                    "required": False,
                    "type": "string",
                    "enum": ["dot", "mermaid", "json_graph", "adjacency_list"],
                },
                "include_labels": {"required": False, "type": "boolean"},
            },
        }

    def _load_tool_registry(self) -> Dict[str, Callable]:
        """Load registry of available tools for this gateway."""
        try:
            from lackey.core import LackeyCore

            # Use custom core if provided
            if self._custom_core is not None:
                lackey_core = self._custom_core
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
                "analyze_project_dependencies": (
                    lackey_core.analyze_project_dependencies
                ),
                "analyze_critical_path": lackey_core.analyze_critical_path,
                "get_critical_path_analysis": (lackey_core.get_critical_path_analysis),
                "analyze_task_impact": lackey_core.analyze_task_impact,
                "get_workload_analysis": lackey_core.get_workload_analysis,
                "get_bottleneck_analysis": lackey_core.get_bottleneck_analysis,
                "get_project_stats": lackey_core.get_project_stats,
                "get_system_health": lackey_core.get_system_health,
                "get_system_diagnostics": lackey_core.get_system_diagnostics,
                "get_performance_metrics": lackey_core.get_performance_metrics,
                "generate_dependency_visualization": (
                    lackey_core.generate_dependency_visualization
                ),
            }

        except Exception as e:
            logger.error(f"Failed to load tool registry: {e}")
            return {}

    def _intent_to_tool(self, intent: str) -> str:
        """Map intent name to actual tool name."""
        # Handle intent-to-tool mappings for analyze gateway
        intent_mappings = {
            "analyze_dependencies": "analyze_project_dependencies",
            "analyze_health": "get_system_health",
            "analyze_performance": "get_performance_metrics",
            "analyze_bottlenecks": "get_bottleneck_analysis",
            "analyze_workload": "get_workload_analysis",
        }

        return intent_mappings.get(intent, intent)
