"""Dependency validation and graph analysis for Lackey tasks."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx

from .models import Task, TaskStatus


class DependencyError(Exception):
    """Raised when dependency validation fails."""

    pass


class CircularDependencyError(DependencyError):
    """Raised when circular dependencies are detected."""

    pass


@dataclass
class DependencyAnalysis:
    """Results of dependency graph analysis."""

    is_valid: bool
    cycles: List[List[str]]
    critical_path: List[str]
    ready_tasks: List[str]
    blocked_tasks: List[str]
    orphaned_tasks: List[str]
    max_depth: int
    total_tasks: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis to dictionary."""
        return {
            "is_valid": self.is_valid,
            "cycles": self.cycles,
            "critical_path": self.critical_path,
            "ready_tasks": self.ready_tasks,
            "blocked_tasks": self.blocked_tasks,
            "orphaned_tasks": self.orphaned_tasks,
            "max_depth": self.max_depth,
            "total_tasks": self.total_tasks,
        }


@dataclass
class TaskChainInfo:
    """Information about a task's position in dependency chains."""

    task_id: str
    upstream_tasks: List[str]  # Tasks this depends on
    downstream_tasks: List[str]  # Tasks that depend on this
    depth_from_root: int
    depth_to_leaf: int
    is_critical_path: bool
    blocking_count: int  # Number of tasks this blocks

    def to_dict(self) -> Dict[str, Any]:
        """Convert chain info to dictionary."""
        return {
            "task_id": self.task_id,
            "upstream_tasks": self.upstream_tasks,
            "downstream_tasks": self.downstream_tasks,
            "depth_from_root": self.depth_from_root,
            "depth_to_leaf": self.depth_to_leaf,
            "is_critical_path": self.is_critical_path,
            "blocking_count": self.blocking_count,
        }


class DependencyValidator:
    """
    Validates and analyzes task dependency graphs.

    Uses NetworkX to perform graph algorithms including cycle detection,
    topological sorting, and critical path analysis.
    """

    def __init__(self) -> None:
        """Initialize dependency validator."""
        self.max_chain_depth = 20  # Configurable limit
        self.max_dependencies_per_task = 50

    def validate_dag(self, tasks: List[Task]) -> DependencyAnalysis:
        """
        Validate that tasks form a directed acyclic graph.

        Returns comprehensive analysis including cycles, critical path,
        and task readiness information.
        """
        if not tasks:
            return DependencyAnalysis(
                is_valid=True,
                cycles=[],
                critical_path=[],
                ready_tasks=[],
                blocked_tasks=[],
                orphaned_tasks=[],
                max_depth=0,
                total_tasks=0,
            )

        # Build dependency graph
        graph = self._build_dependency_graph(tasks)

        # Detect cycles
        cycles = self._find_cycles(graph)
        is_valid = len(cycles) == 0

        # Find critical path
        critical_path = self._find_critical_path(graph, tasks) if is_valid else []

        # Analyze task readiness
        completed_tasks = {t.id for t in tasks if t.status == TaskStatus.DONE}
        ready_tasks = self._find_ready_tasks(tasks, completed_tasks)
        blocked_tasks = self._find_blocked_tasks(tasks, completed_tasks)

        # Find orphaned tasks (no dependencies and no dependents)
        orphaned_tasks = self._find_orphaned_tasks(graph, tasks)

        # Calculate maximum depth
        max_depth = self._calculate_max_depth(graph) if is_valid else 0

        return DependencyAnalysis(
            is_valid=is_valid,
            cycles=cycles,
            critical_path=critical_path,
            ready_tasks=ready_tasks,
            blocked_tasks=blocked_tasks,
            orphaned_tasks=orphaned_tasks,
            max_depth=max_depth,
            total_tasks=len(tasks),
        )

    def get_task_chain_info(self, task_id: str, tasks: List[Task]) -> TaskChainInfo:
        """Get detailed information about a task's position in dependency chains."""
        graph = self._build_dependency_graph(tasks)

        if task_id not in graph:
            raise DependencyError(f"Task {task_id} not found in graph")

        # Get upstream and downstream tasks
        upstream_tasks = list(graph.predecessors(task_id))
        downstream_tasks = list(graph.successors(task_id))

        # Calculate depths
        depth_from_root = self._calculate_depth_from_root(graph, task_id)
        depth_to_leaf = self._calculate_depth_to_leaf(graph, task_id)

        # Check if on critical path
        critical_path = self._find_critical_path(graph, tasks)
        is_critical_path = task_id in critical_path

        # Count blocking tasks
        blocking_count = len(downstream_tasks)

        return TaskChainInfo(
            task_id=task_id,
            upstream_tasks=upstream_tasks,
            downstream_tasks=downstream_tasks,
            depth_from_root=depth_from_root,
            depth_to_leaf=depth_to_leaf,
            is_critical_path=is_critical_path,
            blocking_count=blocking_count,
        )

    def can_add_dependency(
        self, task_id: str, dependency_id: str, tasks: List[Task]
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if adding a dependency would create a cycle.

        Returns (can_add, error_message).
        """
        if task_id == dependency_id:
            return False, "Task cannot depend on itself"

        # Find the tasks
        task = next((t for t in tasks if t.id == task_id), None)
        dependency_task = next((t for t in tasks if t.id == dependency_id), None)

        if not task:
            return False, f"Task {task_id} not found"

        if not dependency_task:
            return False, f"Dependency task {dependency_id} not found"

        # Check dependency limit
        if len(task.dependencies) >= self.max_dependencies_per_task:
            return (
                False,
                f"Maximum {self.max_dependencies_per_task} dependencies allowed",
            )

        # Create temporary graph with new dependency
        graph = self._build_dependency_graph(tasks)
        graph.add_edge(dependency_id, task_id)

        # Check for cycles
        try:
            cycles = list(nx.simple_cycles(graph))
            if cycles:
                cycle_str = " -> ".join(cycles[0] + [cycles[0][0]])
                return False, f"Would create cycle: {cycle_str}"
        except nx.NetworkXError:
            return False, "Graph analysis failed"

        # Check depth limit
        max_depth = self._calculate_max_depth(graph)
        if max_depth > self.max_chain_depth:
            return False, f"Would exceed maximum chain depth of {self.max_chain_depth}"

        return True, None

    def suggest_dependency_removal(
        self, tasks: List[Task]
    ) -> List[Tuple[str, str, str]]:
        """
        Suggest dependency removals to break cycles.

        Returns list of (task_id, dependency_id, reason) tuples.
        """
        graph = self._build_dependency_graph(tasks)
        cycles = self._find_cycles(graph)

        if not cycles:
            return []

        suggestions = []

        for cycle in cycles:
            # Find the newest dependency in the cycle to suggest removal
            newest_edge: Optional[Tuple[str, str]] = None
            newest_time: Optional[datetime] = None

            for i in range(len(cycle)):
                task_id = cycle[i]
                next_task_id = cycle[(i + 1) % len(cycle)]

                task = next((t for t in tasks if t.id == task_id), None)
                if task and next_task_id in task.dependencies:
                    if newest_time is None or task.updated > newest_time:
                        newest_time = task.updated
                        newest_edge = (task_id, next_task_id)

            if newest_edge:
                task_id, dep_id = newest_edge
                cycle_str = " -> ".join(cycle + [cycle[0]])
                reason = f"Breaks cycle: {cycle_str}"
                suggestions.append((task_id, dep_id, reason))

        return suggestions

    def get_topological_order(self, tasks: List[Task]) -> List[str]:
        """
        Get topological ordering of tasks.

        Returns task IDs in an order where dependencies come before dependents.
        Raises CircularDependencyError if cycles exist.
        """
        graph = self._build_dependency_graph(tasks)

        # Check for cycles first
        cycles = self._find_cycles(graph)
        if cycles:
            cycle_str = " -> ".join(cycles[0] + [cycles[0][0]])
            raise CircularDependencyError(f"Cannot order tasks with cycle: {cycle_str}")

        try:
            return list(nx.topological_sort(graph))
        except nx.NetworkXError as e:
            raise DependencyError(f"Topological sort failed: {e}")

    def _build_dependency_graph(self, tasks: List[Task]) -> nx.DiGraph:
        """Build NetworkX directed graph from tasks."""
        graph = nx.DiGraph()

        # Add all tasks as nodes
        for task in tasks:
            graph.add_node(task.id, task=task)

        # Add dependency edges
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id in [t.id for t in tasks]:  # Only add if dependency exists
                    graph.add_edge(dep_id, task.id)

        return graph

    def _find_cycles(self, graph: nx.DiGraph) -> List[List[str]]:
        """Find all cycles in the dependency graph."""
        try:
            return list(nx.simple_cycles(graph))
        except nx.NetworkXError:
            return []

    def _find_critical_path(self, graph: nx.DiGraph, tasks: List[Task]) -> List[str]:
        """
        Find the critical path (longest path) through the dependency graph.

        Uses complexity as edge weights to find the most complex path.
        """
        if not graph.nodes():
            return []

        # Add weights based on task complexity
        complexity_weights = {"low": 1, "medium": 3, "high": 5}

        for node in graph.nodes():
            task = next((t for t in tasks if t.id == node), None)
            if task:
                weight = complexity_weights.get(task.complexity.value, 1)
                graph.nodes[node]["weight"] = weight

        # Find longest path using DAG longest path algorithm
        try:
            # Use the correct NetworkX function
            longest_path = nx.dag_longest_path(graph, weight="weight")
            return list(longest_path)

        except nx.NetworkXError:
            return []

    def _find_ready_tasks(
        self, tasks: List[Task], completed_tasks: Set[str]
    ) -> List[str]:
        """Find tasks that are ready to start (all dependencies completed)."""
        ready = []

        for task in tasks:
            if task.status == TaskStatus.TODO and task.dependencies.issubset(
                completed_tasks
            ):
                ready.append(task.id)

        return ready

    def _find_blocked_tasks(
        self, tasks: List[Task], completed_tasks: Set[str]
    ) -> List[str]:
        """Find tasks that are blocked by incomplete dependencies."""
        blocked = []

        for task in tasks:
            if task.status in (
                TaskStatus.TODO,
                TaskStatus.IN_PROGRESS,
            ) and not task.dependencies.issubset(completed_tasks):
                blocked.append(task.id)

        return blocked

    def _find_orphaned_tasks(self, graph: nx.DiGraph, tasks: List[Task]) -> List[str]:
        """Find tasks with no dependencies and no dependents."""
        orphaned = []

        for task in tasks:
            if graph.in_degree(task.id) == 0 and graph.out_degree(task.id) == 0:
                orphaned.append(task.id)

        return orphaned

    def _calculate_max_depth(self, graph: nx.DiGraph) -> int:
        """Calculate maximum depth of the dependency graph."""
        if not graph.nodes():
            return 0

        try:
            # Find longest path length
            longest_path = nx.dag_longest_path(graph)
            return len(longest_path) - 1 if longest_path else 0
        except nx.NetworkXError:
            return 0

    def _calculate_depth_from_root(self, graph: nx.DiGraph, task_id: str) -> int:
        """Calculate depth of task from root nodes."""
        try:
            # Find all root nodes
            root_nodes = [n for n in graph.nodes() if graph.in_degree(n) == 0]

            if not root_nodes:
                return 0

            min_depth = float("inf")

            for root in root_nodes:
                try:
                    if nx.has_path(graph, root, task_id):
                        path = nx.shortest_path(graph, root, task_id)
                        depth = len(path) - 1
                        min_depth = min(min_depth, depth)
                except nx.NetworkXError:
                    continue

            return int(min_depth) if min_depth != float("inf") else 0

        except nx.NetworkXError:
            return 0

    def _calculate_depth_to_leaf(self, graph: nx.DiGraph, task_id: str) -> int:
        """Calculate depth from task to leaf nodes."""
        try:
            # Find all leaf nodes reachable from this task
            leaf_nodes = [n for n in graph.nodes() if graph.out_degree(n) == 0]

            if not leaf_nodes:
                return 0

            max_depth = 0

            for leaf in leaf_nodes:
                try:
                    if nx.has_path(graph, task_id, leaf):
                        path = nx.shortest_path(graph, task_id, leaf)
                        depth = len(path) - 1
                        max_depth = max(max_depth, depth)
                except nx.NetworkXError:
                    continue

            return max_depth

        except nx.NetworkXError:
            return 0


# Global validator instance
dependency_validator = DependencyValidator()
