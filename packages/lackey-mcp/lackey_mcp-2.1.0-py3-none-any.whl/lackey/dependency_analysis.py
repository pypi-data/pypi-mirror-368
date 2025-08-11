"""Advanced dependency analysis and visualization tools for Lackey."""

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx

from .models import Complexity, Task, TaskStatus


class AnalysisType(Enum):
    """Types of dependency analysis."""

    CRITICAL_PATH = "critical_path"
    BOTTLENECK = "bottleneck"
    PARALLEL_CHAINS = "parallel_chains"
    IMPACT_ANALYSIS = "impact_analysis"
    WORKLOAD_DISTRIBUTION = "workload_distribution"


class VisualizationFormat(Enum):
    """Supported visualization formats."""

    DOT = "dot"  # Graphviz DOT format
    MERMAID = "mermaid"  # Mermaid diagram format
    JSON_GRAPH = "json_graph"  # JSON graph format
    ADJACENCY_LIST = "adjacency_list"  # Simple adjacency list


@dataclass
class TaskNode:
    """Enhanced task node with analysis metadata."""

    task_id: str
    title: str
    status: TaskStatus
    complexity: Complexity
    assigned_to: Optional[str]
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    progress_percentage: float = 0.0

    # Analysis metadata
    depth_from_root: int = 0
    depth_to_leaf: int = 0
    is_critical_path: bool = False
    is_bottleneck: bool = False
    blocking_count: int = 0
    parallel_chains: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "status": self.status.value,
            "complexity": self.complexity.value,
            "assigned_to": self.assigned_to,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "progress_percentage": self.progress_percentage,
            "depth_from_root": self.depth_from_root,
            "depth_to_leaf": self.depth_to_leaf,
            "is_critical_path": self.is_critical_path,
            "is_bottleneck": self.is_bottleneck,
            "blocking_count": self.blocking_count,
            "parallel_chains": self.parallel_chains,
        }


@dataclass
class DependencyEdge:
    """Enhanced dependency edge with relationship metadata."""

    from_task: str
    to_task: str
    edge_type: str = "depends_on"  # depends_on, blocks, related
    strength: float = 1.0  # Dependency strength (0.0 to 1.0)
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "from_task": self.from_task,
            "to_task": self.to_task,
            "edge_type": self.edge_type,
            "strength": self.strength,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass
class CriticalPathAnalysis:
    """Results of critical path analysis."""

    path: List[str]
    total_duration_hours: float
    bottleneck_tasks: List[str]
    parallel_opportunities: List[List[str]]
    completion_probability: float
    risk_factors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "path": self.path,
            "total_duration_hours": self.total_duration_hours,
            "bottleneck_tasks": self.bottleneck_tasks,
            "parallel_opportunities": self.parallel_opportunities,
            "completion_probability": self.completion_probability,
            "risk_factors": self.risk_factors,
        }


@dataclass
class ImpactAnalysis:
    """Results of task impact analysis."""

    task_id: str
    directly_affected: List[str]
    indirectly_affected: List[str]
    total_impact_score: float
    cascade_depth: int
    affected_assignees: Set[str]
    estimated_delay_hours: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "directly_affected": self.directly_affected,
            "indirectly_affected": self.indirectly_affected,
            "total_impact_score": self.total_impact_score,
            "cascade_depth": self.cascade_depth,
            "affected_assignees": list(self.affected_assignees),
            "estimated_delay_hours": self.estimated_delay_hours,
        }


@dataclass
class WorkloadAnalysis:
    """Results of workload distribution analysis."""

    assignee_workloads: Dict[str, float]  # assignee -> total hours
    assignee_task_counts: Dict[str, int]  # assignee -> task count
    critical_path_workloads: Dict[str, float]  # assignee -> critical path hours
    bottleneck_assignees: List[str]
    workload_balance_score: float  # 0.0 (unbalanced) to 1.0 (perfectly balanced)
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "assignee_workloads": self.assignee_workloads,
            "assignee_task_counts": self.assignee_task_counts,
            "critical_path_workloads": self.critical_path_workloads,
            "bottleneck_assignees": self.bottleneck_assignees,
            "workload_balance_score": self.workload_balance_score,
            "recommendations": self.recommendations,
        }


class AdvancedDependencyAnalyzer:
    """
    Advanced dependency analysis engine with visualization capabilities.

    Provides sophisticated analysis of task dependencies including critical path
    analysis, bottleneck detection, impact analysis, and workload distribution.
    """

    def __init__(self) -> None:
        """Initialize the advanced dependency analyzer."""
        self.complexity_hours = {
            Complexity.LOW: 4.0,
            Complexity.MEDIUM: 16.0,
            Complexity.HIGH: 40.0,
        }

    def analyze_dependencies(
        self, tasks: List[Task], analysis_types: Optional[List[AnalysisType]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive dependency analysis.

        Args:
            tasks: List of tasks to analyze
            analysis_types: Types of analysis to perform (all if None)

        Returns:
            Dictionary with analysis results
        """
        if analysis_types is None:
            analysis_types = list(AnalysisType)

        # Build enhanced graph
        graph, nodes, edges = self._build_enhanced_graph(tasks)

        results = {
            "graph_summary": {
                "total_tasks": len(tasks),
                "total_dependencies": len(edges),
                "completed_tasks": len(
                    [t for t in tasks if t.status == TaskStatus.DONE]
                ),
                "in_progress_tasks": len(
                    [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
                ),
                "blocked_tasks": len(
                    [t for t in tasks if t.status == TaskStatus.BLOCKED]
                ),
            },
            "nodes": [node.to_dict() for node in nodes.values()],
            "edges": [edge.to_dict() for edge in edges],
        }

        # Perform requested analyses
        if AnalysisType.CRITICAL_PATH in analysis_types:
            results["critical_path"] = self._analyze_critical_path(
                graph, nodes
            ).to_dict()

        if AnalysisType.BOTTLENECK in analysis_types:
            results["bottlenecks"] = self._analyze_bottlenecks(graph, nodes)

        if AnalysisType.PARALLEL_CHAINS in analysis_types:
            results["parallel_chains"] = self._analyze_parallel_chains(graph, nodes)

        if AnalysisType.WORKLOAD_DISTRIBUTION in analysis_types:
            results["workload_analysis"] = self._analyze_workload_distribution(
                nodes
            ).to_dict()

        return results

    def analyze_task_impact(self, task_id: str, tasks: List[Task]) -> ImpactAnalysis:
        """
        Analyze the impact of delays or changes to a specific task.

        Args:
            task_id: ID of the task to analyze
            tasks: List of all tasks

        Returns:
            Impact analysis results
        """
        graph, nodes, edges = self._build_enhanced_graph(tasks)

        if task_id not in nodes:
            raise ValueError(f"Task {task_id} not found")

        # Find directly affected tasks (immediate dependents)
        directly_affected = list(graph.successors(task_id))

        # Find indirectly affected tasks (transitive dependents)
        indirectly_affected = []
        visited = set([task_id] + directly_affected)

        for direct_task in directly_affected:
            for indirect_task in nx.descendants(graph, direct_task):
                if indirect_task not in visited:
                    indirectly_affected.append(indirect_task)
                    visited.add(indirect_task)

        # Calculate impact score
        total_affected = len(directly_affected) + len(indirectly_affected)
        base_impact = nodes[task_id].blocking_count
        complexity_multiplier = self._get_complexity_multiplier(
            nodes[task_id].complexity
        )
        total_impact_score = (base_impact + total_affected) * complexity_multiplier

        # Calculate cascade depth
        cascade_depth = 0
        if directly_affected:
            cascade_depth = (
                max(
                    nx.shortest_path_length(graph, task_id, target)
                    for target in nx.descendants(graph, task_id)
                )
                if nx.descendants(graph, task_id)
                else 1
            )

        # Find affected assignees
        affected_assignees: set[str] = set()
        for affected_task_id in directly_affected + indirectly_affected:
            assignee = nodes[affected_task_id].assigned_to
            if assignee is not None:
                affected_assignees.add(assignee)

        # Estimate delay impact
        task_hours = self._estimate_task_hours(nodes[task_id])
        delay_multiplier = 0.3  # Assume 30% of task duration as delay impact
        estimated_delay_hours = task_hours * delay_multiplier

        return ImpactAnalysis(
            task_id=task_id,
            directly_affected=directly_affected,
            indirectly_affected=indirectly_affected,
            total_impact_score=total_impact_score,
            cascade_depth=cascade_depth,
            affected_assignees=affected_assignees,
            estimated_delay_hours=estimated_delay_hours,
        )

    def generate_visualization(
        self,
        tasks: List[Task],
        format_type: VisualizationFormat = VisualizationFormat.DOT,
        highlight_critical_path: bool = True,
        highlight_bottlenecks: bool = True,
    ) -> str:
        """
        Generate visualization of the dependency graph.

        Args:
            tasks: List of tasks to visualize
            format_type: Output format for visualization
            highlight_critical_path: Whether to highlight critical path
            highlight_bottlenecks: Whether to highlight bottlenecks

        Returns:
            Visualization string in requested format
        """
        graph, nodes, edges = self._build_enhanced_graph(tasks)

        if format_type == VisualizationFormat.DOT:
            return self._generate_dot_visualization(
                graph, nodes, highlight_critical_path, highlight_bottlenecks
            )
        elif format_type == VisualizationFormat.MERMAID:
            return self._generate_mermaid_visualization(
                graph, nodes, highlight_critical_path, highlight_bottlenecks
            )
        elif format_type == VisualizationFormat.JSON_GRAPH:
            return self._generate_json_graph_visualization(nodes, edges)
        elif format_type == VisualizationFormat.ADJACENCY_LIST:
            return self._generate_adjacency_list_visualization(graph, nodes)
        else:
            raise ValueError(f"Unsupported visualization format: {format_type}")

    def _build_enhanced_graph(
        self, tasks: List[Task]
    ) -> Tuple[nx.DiGraph, Dict[str, TaskNode], List[DependencyEdge]]:
        """Build enhanced graph with metadata."""
        graph = nx.DiGraph()
        nodes = {}
        edges = []

        # Create nodes
        for task in tasks:
            node = TaskNode(
                task_id=task.id,
                title=task.title,
                status=task.status,
                complexity=task.complexity,
                assigned_to=task.assigned_to,
                progress_percentage=task.progress_percentage(),
            )
            nodes[task.id] = node
            graph.add_node(task.id)

        # Create edges
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id in nodes:  # Only add edges for existing tasks
                    edge = DependencyEdge(
                        from_task=dep_id,
                        to_task=task.id,
                        created_at=datetime.now(UTC),
                    )
                    edges.append(edge)
                    graph.add_edge(dep_id, task.id)

        # Calculate enhanced metadata
        self._calculate_node_metadata(graph, nodes)

        return graph, nodes, edges

    def _calculate_node_metadata(
        self, graph: nx.DiGraph, nodes: Dict[str, TaskNode]
    ) -> None:
        """Calculate enhanced metadata for nodes."""
        # Calculate depths
        for node_id in graph.nodes():
            # Depth from root (longest path from any root)
            predecessors = list(graph.predecessors(node_id))
            if not predecessors:
                nodes[node_id].depth_from_root = 0
            else:
                nodes[node_id].depth_from_root = max(
                    nodes[pred].depth_from_root + 1 for pred in predecessors
                )

            # Blocking count
            nodes[node_id].blocking_count = len(list(graph.successors(node_id)))

        # Calculate depth to leaf (reverse pass)
        for node_id in reversed(list(nx.topological_sort(graph))):
            successors = list(graph.successors(node_id))
            if not successors:
                nodes[node_id].depth_to_leaf = 0
            else:
                nodes[node_id].depth_to_leaf = max(
                    nodes[succ].depth_to_leaf + 1 for succ in successors
                )

    def _analyze_critical_path(
        self, graph: nx.DiGraph, nodes: Dict[str, TaskNode]
    ) -> CriticalPathAnalysis:
        """Analyze critical path through the dependency graph."""
        # Find the longest path (critical path)
        try:
            critical_path = nx.dag_longest_path(
                graph, weight=lambda u, v, d: self._estimate_task_hours(nodes[v])
            )
        except nx.NetworkXError:
            # Graph has cycles, return empty analysis
            return CriticalPathAnalysis(
                path=[],
                total_duration_hours=0.0,
                bottleneck_tasks=[],
                parallel_opportunities=[],
                completion_probability=0.0,
                risk_factors=["Circular dependencies detected"],
            )

        # Mark critical path nodes
        for task_id in critical_path:
            nodes[task_id].is_critical_path = True

        # Calculate total duration
        total_duration = sum(
            self._estimate_task_hours(nodes[task_id]) for task_id in critical_path
        )

        # Find bottleneck tasks (high complexity on critical path)
        bottleneck_tasks = [
            task_id
            for task_id in critical_path
            if nodes[task_id].complexity == Complexity.HIGH
        ]

        # Find parallel opportunities
        parallel_opportunities = self._find_parallel_opportunities(graph, critical_path)

        # Calculate completion probability (simplified heuristic)
        completion_probability = self._calculate_completion_probability(
            critical_path, nodes
        )

        # Identify risk factors
        risk_factors = self._identify_risk_factors(critical_path, nodes)

        return CriticalPathAnalysis(
            path=critical_path,
            total_duration_hours=total_duration,
            bottleneck_tasks=bottleneck_tasks,
            parallel_opportunities=parallel_opportunities,
            completion_probability=completion_probability,
            risk_factors=risk_factors,
        )

    def _analyze_bottlenecks(
        self, graph: nx.DiGraph, nodes: Dict[str, TaskNode]
    ) -> List[Dict[str, Any]]:
        """Analyze bottleneck tasks in the dependency graph."""
        bottlenecks = []

        for task_id, node in nodes.items():
            # A task is a bottleneck if it has high blocking count and high complexity
            bottleneck_score = node.blocking_count * self._get_complexity_multiplier(
                node.complexity
            )

            if bottleneck_score > 2.0:  # Threshold for bottleneck detection
                node.is_bottleneck = True
                bottlenecks.append(
                    {
                        "task_id": task_id,
                        "title": node.title,
                        "blocking_count": node.blocking_count,
                        "complexity": node.complexity.value,
                        "bottleneck_score": bottleneck_score,
                        "assigned_to": node.assigned_to,
                        "status": node.status.value,
                    }
                )

        # Sort by bottleneck score
        def get_score(x: Dict[str, Any]) -> float:
            score = x.get("bottleneck_score", 0.0)
            return float(score) if score is not None else 0.0

        bottlenecks.sort(key=get_score, reverse=True)

        return bottlenecks

    def _analyze_parallel_chains(
        self, graph: nx.DiGraph, nodes: Dict[str, TaskNode]
    ) -> List[Dict[str, Any]]:
        """Analyze parallel execution chains."""
        # Find all paths from roots to leaves
        roots = [n for n in graph.nodes() if graph.in_degree(n) == 0]
        leaves = [n for n in graph.nodes() if graph.out_degree(n) == 0]

        parallel_chains = []

        for root in roots:
            for leaf in leaves:
                if nx.has_path(graph, root, leaf):
                    paths = list(nx.all_simple_paths(graph, root, leaf))
                    if len(paths) > 1:
                        # Multiple paths exist - potential for parallelization
                        chain_info = {
                            "root_task": root,
                            "leaf_task": leaf,
                            "parallel_paths": paths,
                            "path_count": len(paths),
                            "total_duration": sum(
                                sum(
                                    self._estimate_task_hours(nodes[task])
                                    for task in path
                                )
                                for path in paths
                            ),
                            "critical_path_duration": max(
                                sum(
                                    self._estimate_task_hours(nodes[task])
                                    for task in path
                                )
                                for path in paths
                            ),
                        }
                        parallel_chains.append(chain_info)

        return parallel_chains

    def _analyze_workload_distribution(
        self, nodes: Dict[str, TaskNode]
    ) -> WorkloadAnalysis:
        """Analyze workload distribution across assignees."""
        assignee_workloads: Dict[str, float] = defaultdict(float)
        assignee_task_counts: Dict[str, int] = defaultdict(int)
        critical_path_workloads: Dict[str, float] = defaultdict(float)

        for node in nodes.values():
            if node.assigned_to:
                hours = self._estimate_task_hours(node)
                assignee_workloads[node.assigned_to] += hours
                assignee_task_counts[node.assigned_to] += 1

                if node.is_critical_path:
                    critical_path_workloads[node.assigned_to] += hours

        # Calculate workload balance score
        if assignee_workloads:
            workloads = list(assignee_workloads.values())
            avg_workload = sum(workloads) / len(workloads)
            variance = sum((w - avg_workload) ** 2 for w in workloads) / len(workloads)
            balance_score = max(0.0, 1.0 - (variance / (avg_workload**2)))
        else:
            balance_score = 1.0

        # Identify bottleneck assignees
        bottleneck_assignees = []
        if assignee_workloads:
            avg_workload = sum(assignee_workloads.values()) / len(assignee_workloads)
            threshold = avg_workload * 1.5  # 50% above average
            bottleneck_assignees = [
                assignee
                for assignee, workload in assignee_workloads.items()
                if workload > threshold
            ]

        # Generate recommendations
        recommendations = []
        if balance_score < 0.7:
            recommendations.append("Consider redistributing tasks to balance workload")
        if bottleneck_assignees:
            recommendations.append(
                f"Assignees with high workload: {', '.join(bottleneck_assignees)}"
            )
        if critical_path_workloads:
            max_critical_assignee = max(
                critical_path_workloads.items(), key=lambda x: x[1]
            )
            recommendations.append(
                f"Critical path bottleneck: {max_critical_assignee[0]} "
                f"({max_critical_assignee[1]:.1f} hours)"
            )

        return WorkloadAnalysis(
            assignee_workloads=dict(assignee_workloads),
            assignee_task_counts=dict(assignee_task_counts),
            critical_path_workloads=dict(critical_path_workloads),
            bottleneck_assignees=bottleneck_assignees,
            workload_balance_score=balance_score,
            recommendations=recommendations,
        )

    def _estimate_task_hours(self, node: TaskNode) -> float:
        """Estimate hours for a task based on complexity and progress."""
        base_hours = self.complexity_hours.get(node.complexity, 16.0)

        # Adjust for actual hours if available
        if node.actual_hours is not None:
            return node.actual_hours
        elif node.estimated_hours is not None:
            return node.estimated_hours
        else:
            return base_hours

    def _get_complexity_multiplier(self, complexity: Complexity) -> float:
        """Get multiplier for complexity-based calculations."""
        multipliers = {
            Complexity.LOW: 1.0,
            Complexity.MEDIUM: 2.0,
            Complexity.HIGH: 3.0,
        }
        return multipliers.get(complexity, 2.0)

    def _find_parallel_opportunities(
        self, graph: nx.DiGraph, critical_path: List[str]
    ) -> List[List[str]]:
        """Find opportunities for parallel execution."""
        opportunities = []

        for i in range(len(critical_path) - 1):
            current_task = critical_path[i]
            next_task = critical_path[i + 1]

            # Find tasks that could run in parallel with the current critical
            # path segment
            parallel_tasks = []
            for node in graph.nodes():
                if (
                    node not in critical_path
                    and not nx.has_path(graph, node, current_task)
                    and not nx.has_path(graph, next_task, node)
                ):
                    parallel_tasks.append(node)

            if parallel_tasks:
                opportunities.append(parallel_tasks)

        return opportunities

    def _calculate_completion_probability(
        self, critical_path: List[str], nodes: Dict[str, TaskNode]
    ) -> float:
        """Calculate probability of on-time completion."""
        if not critical_path:
            return 1.0

        # Simple heuristic based on task status and complexity
        total_score = 0.0
        for task_id in critical_path:
            node = nodes[task_id]
            if node.status == TaskStatus.DONE:
                score = 1.0
            elif node.status == TaskStatus.IN_PROGRESS:
                score = 0.7 + (node.progress_percentage / 100.0) * 0.3
            elif node.status == TaskStatus.BLOCKED:
                score = 0.3
            else:  # TODO
                complexity_penalty = {
                    Complexity.LOW: 0.9,
                    Complexity.MEDIUM: 0.7,
                    Complexity.HIGH: 0.5,
                }
                score = complexity_penalty.get(node.complexity, 0.7)

            total_score += score

        return total_score / len(critical_path)

    def _identify_risk_factors(
        self, critical_path: List[str], nodes: Dict[str, TaskNode]
    ) -> List[str]:
        """Identify risk factors for project completion."""
        risks = []

        # Check for unassigned critical tasks
        unassigned_critical = [
            task_id for task_id in critical_path if not nodes[task_id].assigned_to
        ]
        if unassigned_critical:
            risks.append(f"{len(unassigned_critical)} critical tasks unassigned")

        # Check for blocked critical tasks
        blocked_critical = [
            task_id
            for task_id in critical_path
            if nodes[task_id].status == TaskStatus.BLOCKED
        ]
        if blocked_critical:
            risks.append(f"{len(blocked_critical)} critical tasks blocked")

        # Check for high complexity concentration
        high_complexity_critical = [
            task_id
            for task_id in critical_path
            if nodes[task_id].complexity == Complexity.HIGH
        ]
        if len(high_complexity_critical) > len(critical_path) * 0.5:
            risks.append("High concentration of complex tasks on critical path")

        # Check for single assignee dependency
        assignees = set(
            nodes[task_id].assigned_to
            for task_id in critical_path
            if nodes[task_id].assigned_to
        )
        if len(assignees) == 1:
            risks.append(
                f"Critical path depends on single assignee: {list(assignees)[0]}"
            )

        return risks

    def _generate_dot_visualization(
        self,
        graph: nx.DiGraph,
        nodes: Dict[str, TaskNode],
        highlight_critical_path: bool,
        highlight_bottlenecks: bool,
    ) -> str:
        """Generate Graphviz DOT format visualization."""
        lines = ["digraph TaskDependencies {"]
        lines.append("    rankdir=TB;")
        lines.append("    node [shape=box, style=rounded];")

        # Add nodes with styling
        for node_id, node in nodes.items():
            label = f"{node.title}\\n({node.status.value})"
            if node.assigned_to:
                label += f"\\n@{node.assigned_to}"

            # Determine node color
            if highlight_critical_path and node.is_critical_path:
                color = "red"
                style = "filled,bold"
            elif highlight_bottlenecks and node.is_bottleneck:
                color = "orange"
                style = "filled"
            elif node.status == TaskStatus.DONE:
                color = "lightgreen"
                style = "filled"
            elif node.status == TaskStatus.IN_PROGRESS:
                color = "lightblue"
                style = "filled"
            elif node.status == TaskStatus.BLOCKED:
                color = "lightcoral"
                style = "filled"
            else:
                color = "white"
                style = "solid"

            lines.append(
                f'    "{node_id}" [label="{label}", fillcolor={color}, '
                f'style="{style}"];'
            )

        # Add edges
        for edge in graph.edges():
            from_node, to_node = edge
            edge_style = (
                "bold"
                if (
                    highlight_critical_path
                    and nodes[from_node].is_critical_path
                    and nodes[to_node].is_critical_path
                )
                else "solid"
            )
            lines.append(f'    "{from_node}" -> "{to_node}" [style={edge_style}];')

        lines.append("}")
        return "\n".join(lines)

    def _generate_mermaid_visualization(
        self,
        graph: nx.DiGraph,
        nodes: Dict[str, TaskNode],
        highlight_critical_path: bool,
        highlight_bottlenecks: bool,
    ) -> str:
        """Generate Mermaid diagram format visualization."""
        lines = ["graph TD"]

        # Add nodes with styling
        for node_id, node in nodes.items():
            # Clean node ID for Mermaid (alphanumeric only)
            clean_id = "".join(c for c in node_id if c.isalnum())
            label = f"{node.title}<br/>({node.status.value})"
            if node.assigned_to:
                label += f"<br/>@{node.assigned_to}"

            # Determine node styling
            if highlight_critical_path and node.is_critical_path:
                lines.append(f'    {clean_id}["{label}"]')
                lines.append(f"    {clean_id} --> {clean_id}")
                lines.append(
                    f"    style {clean_id} fill:#ff6b6b,stroke:#d63031,stroke-width:3px"
                )
            elif highlight_bottlenecks and node.is_bottleneck:
                lines.append(f'    {clean_id}["{label}"]')
                lines.append(
                    f"    style {clean_id} fill:#fdcb6e,stroke:#e17055,stroke-width:2px"
                )
            elif node.status == TaskStatus.DONE:
                lines.append(f'    {clean_id}["{label}"]')
                lines.append(f"    style {clean_id} fill:#00b894,stroke:#00a085")
            elif node.status == TaskStatus.IN_PROGRESS:
                lines.append(f'    {clean_id}["{label}"]')
                lines.append(f"    style {clean_id} fill:#74b9ff,stroke:#0984e3")
            elif node.status == TaskStatus.BLOCKED:
                lines.append(f'    {clean_id}["{label}"]')
                lines.append(f"    style {clean_id} fill:#fab1a0,stroke:#e17055")
            else:
                lines.append(f'    {clean_id}["{label}"]')

        # Add edges
        for edge in graph.edges():
            from_node, to_node = edge
            clean_from = "".join(c for c in from_node if c.isalnum())
            clean_to = "".join(c for c in to_node if c.isalnum())

            if (
                highlight_critical_path
                and nodes[from_node].is_critical_path
                and nodes[to_node].is_critical_path
            ):
                lines.append(f"    {clean_from} ==> {clean_to}")
            else:
                lines.append(f"    {clean_from} --> {clean_to}")

        return "\n".join(lines)

    def _generate_json_graph_visualization(
        self, nodes: Dict[str, TaskNode], edges: List[DependencyEdge]
    ) -> str:
        """Generate JSON graph format visualization."""
        graph_data = {
            "nodes": [node.to_dict() for node in nodes.values()],
            "edges": [edge.to_dict() for edge in edges],
            "metadata": {
                "generated_at": datetime.now(UTC).isoformat(),
                "total_nodes": len(nodes),
                "total_edges": len(edges),
            },
        }
        return json.dumps(graph_data, indent=2)

    def _generate_adjacency_list_visualization(
        self, graph: nx.DiGraph, nodes: Dict[str, TaskNode]
    ) -> str:
        """Generate simple adjacency list visualization."""
        lines = ["Task Dependency Adjacency List", "=" * 40]

        for node_id in graph.nodes():
            node = nodes[node_id]
            successors = list(graph.successors(node_id))

            status_indicator = {
                TaskStatus.DONE: "✓",
                TaskStatus.IN_PROGRESS: "→",
                TaskStatus.BLOCKED: "⚠",
                TaskStatus.TODO: "○",
            }.get(node.status, "?")

            critical_indicator = " [CRITICAL]" if node.is_critical_path else ""
            bottleneck_indicator = " [BOTTLENECK]" if node.is_bottleneck else ""

            line = (
                f"{status_indicator} {node.title} ({node_id})"
                f"{critical_indicator}{bottleneck_indicator}"
            )
            if node.assigned_to:
                line += f" @{node.assigned_to}"

            lines.append(line)

            if successors:
                for successor in successors:
                    successor_node = nodes[successor]
                    lines.append(f"    └─→ {successor_node.title} ({successor})")
            else:
                lines.append("    └─→ (no dependencies)")

            lines.append("")

        return "\n".join(lines)
