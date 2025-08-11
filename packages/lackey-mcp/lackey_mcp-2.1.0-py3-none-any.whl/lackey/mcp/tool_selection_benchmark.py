"""Tool selection accuracy benchmarking and baseline measurement system."""

import json
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class QueryTestCase:
    """Test case for tool selection accuracy."""

    query: str
    expected_tool: str
    category: str
    difficulty: str  # easy, medium, hard
    description: str
    parameters: Optional[Dict[str, Any]] = None


@dataclass
class SelectionResult:
    """Result of tool selection test."""

    query: str
    expected_tool: str
    selected_tool: Optional[str]
    confidence_score: float
    execution_time_ms: float
    correct: bool
    category: str
    difficulty: str


@dataclass
class BenchmarkResults:
    """Aggregated benchmark results."""

    total_tests: int
    correct_selections: int
    accuracy: float
    avg_confidence: float
    avg_execution_time_ms: float
    category_results: Dict[str, Dict[str, Any]]
    difficulty_results: Dict[str, Dict[str, Any]]
    timestamp: str


class ToolSelectionBenchmark:
    """Benchmarking system for tool selection accuracy."""

    def __init__(self, benchmark_dir: Path):
        """Initialize benchmark system.

        Args:
            benchmark_dir: Directory to store benchmark data
        """
        self.benchmark_dir = benchmark_dir
        self.benchmark_dir.mkdir(parents=True, exist_ok=True)

        self.test_cases_file = self.benchmark_dir / "test_cases.json"
        self.results_file = self.benchmark_dir / "benchmark_results.json"

        # Load or create test cases
        self.test_cases = self._load_or_create_test_cases()

    def _load_or_create_test_cases(self) -> List[QueryTestCase]:
        """Load existing test cases or create default ones."""
        if self.test_cases_file.exists():
            try:
                with open(self.test_cases_file, "r") as f:
                    data = json.load(f)
                    return [QueryTestCase(**case) for case in data]
            except Exception as e:
                logger.warning(f"Failed to load test cases: {e}")

        # Create default test cases
        test_cases = self._create_default_test_cases()
        self._save_test_cases(test_cases)
        return test_cases

    def _create_default_test_cases(self) -> List[QueryTestCase]:
        """Create comprehensive default test cases for tool selection."""
        return [
            # Project Management - Easy
            QueryTestCase(
                query="Create a new project for website development",
                expected_tool="create_project",
                category="project_management",
                difficulty="easy",
                description="Direct project creation request",
            ),
            QueryTestCase(
                query="Show me all projects",
                expected_tool="list_projects",
                category="project_management",
                difficulty="easy",
                description="Simple project listing request",
            ),
            QueryTestCase(
                query="Get details about the website project",
                expected_tool="get_project",
                category="project_management",
                difficulty="easy",
                description="Specific project information request",
            ),
            # Task Management - Easy
            QueryTestCase(
                query="Add a new task to implement user authentication",
                expected_tool="create_task",
                category="task_management",
                difficulty="easy",
                description="Direct task creation request",
            ),
            QueryTestCase(
                query="Show all tasks in the project",
                expected_tool="list_tasks",
                category="task_management",
                difficulty="easy",
                description="Simple task listing request",
            ),
            QueryTestCase(
                query="Get information about the authentication task",
                expected_tool="get_task",
                category="task_management",
                difficulty="easy",
                description="Specific task information request",
            ),
            # Task Status - Medium
            QueryTestCase(
                query="Mark the authentication task as completed",
                expected_tool="update_task_status",
                category="task_status",
                difficulty="medium",
                description="Status change with specific state",
            ),
            QueryTestCase(
                query="Set the database task to in-progress",
                expected_tool="update_task_status",
                category="task_status",
                difficulty="medium",
                description="Status change with different state",
            ),
            # Task Assignment - Medium
            QueryTestCase(
                query="Assign the frontend task to Sarah",
                expected_tool="assign_task",
                category="task_assignment",
                difficulty="medium",
                description="Task assignment to specific person",
            ),
            QueryTestCase(
                query="Give the API work to John",
                expected_tool="assign_task",
                category="task_assignment",
                difficulty="medium",
                description="Alternative phrasing for assignment",
            ),
            # Dependencies - Medium
            QueryTestCase(
                query="Make the API task depend on the database task",
                expected_tool="add_task_dependencies",
                category="dependencies",
                difficulty="medium",
                description="Dependency creation request",
            ),
            QueryTestCase(
                query="Remove the dependency between frontend and backend tasks",
                expected_tool="remove_task_dependencies",
                category="dependencies",
                difficulty="medium",
                description="Dependency removal request",
            ),
            # Analysis - Medium
            QueryTestCase(
                query="What tasks can I work on right now?",
                expected_tool="get_ready_tasks",
                category="analysis",
                difficulty="medium",
                description="Available work inquiry",
            ),
            QueryTestCase(
                query="Show me tasks that are blocked",
                expected_tool="get_blocked_tasks",
                category="analysis",
                difficulty="medium",
                description="Blocked tasks inquiry",
            ),
            # Notes - Medium
            QueryTestCase(
                query="Add a progress update to the authentication task",
                expected_tool="add_task_note",
                category="notes",
                difficulty="medium",
                description="Note addition request",
            ),
            QueryTestCase(
                query="Show me all notes for the database task",
                expected_tool="get_task_notes",
                category="notes",
                difficulty="medium",
                description="Note retrieval request",
            ),
            # Complex Queries - Hard
            QueryTestCase(
                query=(
                    "Find all high-priority tasks assigned to John that are "
                    "currently blocked"
                ),
                expected_tool="list_tasks",
                category="complex_filtering",
                difficulty="hard",
                description="Multi-criteria filtering query",
                parameters={"assigned_to": "John", "status": "blocked"},
            ),
            QueryTestCase(
                query=(
                    "I need to see the progress on all frontend tasks that "
                    "are in progress"
                ),
                expected_tool="list_tasks",
                category="complex_filtering",
                difficulty="hard",
                description="Category and status filtering",
                parameters={"tag": "frontend", "status": "in_progress"},
            ),
            # Ambiguous Queries - Hard
            QueryTestCase(
                query="Update the task",
                expected_tool="update_task_status",
                category="ambiguous",
                difficulty="hard",
                description=(
                    "Ambiguous update request (could be status, assignment, " "etc.)"
                ),
            ),
            QueryTestCase(
                query="Check the dependencies",
                expected_tool="validate_dependencies",
                category="ambiguous",
                difficulty="hard",
                description="Ambiguous validation request",
            ),
            # Bulk Operations - Hard
            QueryTestCase(
                query="Assign all frontend tasks to the UI team",
                expected_tool="bulk_assign_tasks",
                category="bulk_operations",
                difficulty="hard",
                description="Bulk assignment operation",
            ),
            QueryTestCase(
                query="Mark all completed tasks as done",
                expected_tool="bulk_update_task_status",
                category="bulk_operations",
                difficulty="hard",
                description="Bulk status update operation",
            ),
            # Natural Language Variations - Hard
            QueryTestCase(
                query="I want to start working on something, what's available?",
                expected_tool="get_ready_tasks",
                category="natural_language",
                difficulty="hard",
                description="Conversational inquiry about available work",
            ),
            QueryTestCase(
                query="Can you help me understand what's blocking the deployment?",
                expected_tool="get_blocked_tasks",
                category="natural_language",
                difficulty="hard",
                description="Conversational inquiry about blockers",
            ),
        ]

    def _save_test_cases(self, test_cases: List[QueryTestCase]) -> None:
        """Save test cases to file."""
        try:
            with open(self.test_cases_file, "w") as f:
                json.dump([asdict(case) for case in test_cases], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save test cases: {e}")

    def add_test_case(self, test_case: QueryTestCase) -> None:
        """Add a new test case."""
        self.test_cases.append(test_case)
        self._save_test_cases(self.test_cases)

    def simulate_tool_selection(self, query: str) -> Tuple[Optional[str], float]:
        """Simulate tool selection based on query analysis.

        This is a simplified simulation that would be replaced with actual
        agent tool selection logic in a real implementation.

        Args:
            query: User query

        Returns:
            Tuple of (selected_tool, confidence_score)
        """
        query_lower = query.lower()

        # Simple keyword-based selection (placeholder for real ML/NLP)
        tool_keywords = {
            "create_project": [
                "create project",
                "new project",
                "start project",
                "initialize project",
            ],
            "list_projects": [
                "show projects",
                "list projects",
                "all projects",
                "projects",
            ],
            "get_project": [
                "get project",
                "project details",
                "about project",
                "project info",
            ],
            "create_task": ["create task", "add task", "new task", "task for"],
            "list_tasks": [
                "show tasks",
                "list tasks",
                "all tasks",
                "tasks",
                "find tasks",
            ],
            "get_task": ["get task", "task details", "about task", "task info"],
            "update_task_status": [
                "mark task",
                "set task",
                "update status",
                "change status",
                "task as",
                "task to",
            ],
            "assign_task": ["assign task", "give task", "task to", "assign to"],
            "add_task_dependencies": [
                "depend on",
                "dependency",
                "make task depend",
                "prerequisite",
            ],
            "remove_task_dependencies": ["remove dependency", "remove prerequisite"],
            "get_ready_tasks": [
                "ready tasks",
                "available tasks",
                "can work on",
                "what tasks",
                "work on",
            ],
            "get_blocked_tasks": ["blocked tasks", "blocked", "what's blocking"],
            "add_task_note": [
                "add note",
                "note to task",
                "update task",
                "progress update",
            ],
            "get_task_notes": ["show notes", "task notes", "notes for"],
            "validate_dependencies": [
                "check dependencies",
                "validate",
                "dependency issues",
            ],
            "bulk_assign_tasks": ["assign all", "bulk assign", "all tasks to"],
            "bulk_update_task_status": ["mark all", "bulk update", "all tasks as"],
        }

        best_match = None
        best_score = 0.0

        for tool, keywords in tool_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    # Simple scoring based on keyword match length and position
                    score = len(keyword) / len(query_lower)
                    if query_lower.startswith(keyword):
                        score *= 1.2  # Boost for starting matches

                    if score > best_score:
                        best_score = score
                        best_match = tool

        # Add some randomness to simulate real-world uncertainty
        import secrets

        # Use cryptographically secure random for confidence adjustment
        confidence = min(best_score + (secrets.randbelow(21) - 10) / 100.0, 1.0)

        return best_match, max(confidence, 0.0)

    def run_benchmark(self) -> BenchmarkResults:
        """Run the complete benchmark suite."""
        results = []

        for test_case in self.test_cases:
            case_start = time.time()

            # Simulate tool selection
            selected_tool, confidence = self.simulate_tool_selection(test_case.query)

            case_time = (time.time() - case_start) * 1000

            result = SelectionResult(
                query=test_case.query,
                expected_tool=test_case.expected_tool,
                selected_tool=selected_tool,
                confidence_score=confidence,
                execution_time_ms=case_time,
                correct=(selected_tool == test_case.expected_tool),
                category=test_case.category,
                difficulty=test_case.difficulty,
            )

            results.append(result)

        # Calculate aggregate metrics
        total_tests = len(results)
        correct_selections = sum(1 for r in results if r.correct)
        accuracy = correct_selections / total_tests if total_tests > 0 else 0
        avg_confidence = (
            sum(r.confidence_score for r in results) / total_tests
            if total_tests > 0
            else 0
        )
        avg_execution_time = (
            sum(r.execution_time_ms for r in results) / total_tests
            if total_tests > 0
            else 0
        )

        # Category breakdown
        category_results = {}
        for category in set(r.category for r in results):
            category_tests = [r for r in results if r.category == category]
            category_correct = sum(1 for r in category_tests if r.correct)
            category_results[category] = {
                "total": len(category_tests),
                "correct": category_correct,
                "accuracy": (
                    category_correct / len(category_tests) if category_tests else 0
                ),
                "avg_confidence": (
                    sum(r.confidence_score for r in category_tests)
                    / len(category_tests)
                    if category_tests
                    else 0
                ),
            }

        # Difficulty breakdown
        difficulty_results = {}
        for difficulty in set(r.difficulty for r in results):
            difficulty_tests = [r for r in results if r.difficulty == difficulty]
            difficulty_correct = sum(1 for r in difficulty_tests if r.correct)
            difficulty_results[difficulty] = {
                "total": len(difficulty_tests),
                "correct": difficulty_correct,
                "accuracy": (
                    difficulty_correct / len(difficulty_tests)
                    if difficulty_tests
                    else 0
                ),
                "avg_confidence": (
                    sum(r.confidence_score for r in difficulty_tests)
                    / len(difficulty_tests)
                    if difficulty_tests
                    else 0
                ),
            }

        benchmark_results = BenchmarkResults(
            total_tests=total_tests,
            correct_selections=correct_selections,
            accuracy=accuracy,
            avg_confidence=avg_confidence,
            avg_execution_time_ms=avg_execution_time,
            category_results=category_results,
            difficulty_results=difficulty_results,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

        # Save results
        self._save_results(benchmark_results, results)

        return benchmark_results

    def _save_results(
        self,
        benchmark_results: BenchmarkResults,
        detailed_results: List[SelectionResult],
    ) -> None:
        """Save benchmark results to file."""
        try:
            results_data = {
                "summary": asdict(benchmark_results),
                "detailed_results": [asdict(r) for r in detailed_results],
            }

            with open(self.results_file, "w") as f:
                json.dump(results_data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save benchmark results: {e}")

    def generate_report(self) -> str:
        """Generate a formatted benchmark report."""
        if not self.results_file.exists():
            return "No benchmark results available. Run benchmark first."

        try:
            with open(self.results_file, "r") as f:
                data = json.load(f)
                results = BenchmarkResults(**data["summary"])
        except Exception as e:
            return f"Error loading benchmark results: {e}"

        lines = [
            "# Tool Selection Accuracy Benchmark Report",
            "",
            f"**Generated:** {results.timestamp}",
            f"**Total Test Cases:** {results.total_tests}",
            f"**Correct Selections:** {results.correct_selections}",
            f"**Overall Accuracy:** {results.accuracy * 100:.1f}%",
            f"**Average Confidence:** {results.avg_confidence * 100:.1f}%",
            f"**Average Selection Time:** {results.avg_execution_time_ms:.1f}ms",
            "",
            "## Results by Category",
            "",
        ]

        for category, stats in results.category_results.items():
            lines.extend(
                [
                    f"### {category.replace('_', ' ').title()}",
                    f"- **Tests:** {stats['total']}",
                    f"- **Correct:** {stats['correct']}",
                    f"- **Accuracy:** {stats['accuracy'] * 100:.1f}%",
                    f"- **Avg Confidence:** {stats['avg_confidence'] * 100:.1f}%",
                    "",
                ]
            )

        lines.extend(["## Results by Difficulty", ""])

        for difficulty, stats in results.difficulty_results.items():
            lines.extend(
                [
                    f"### {difficulty.title()}",
                    f"- **Tests:** {stats['total']}",
                    f"- **Correct:** {stats['correct']}",
                    f"- **Accuracy:** {stats['accuracy'] * 100:.1f}%",
                    f"- **Avg Confidence:** {stats['avg_confidence'] * 100:.1f}%",
                    "",
                ]
            )

        return "\n".join(lines)


# Global benchmark instance
_benchmark_instance: Optional[ToolSelectionBenchmark] = None


def get_benchmark_instance(
    benchmark_dir: Optional[Path] = None,
) -> ToolSelectionBenchmark:
    """Get or create the global benchmark instance."""
    global _benchmark_instance

    if _benchmark_instance is None:
        if benchmark_dir is None:
            benchmark_dir = Path.cwd() / ".lackey" / "benchmarks"
        _benchmark_instance = ToolSelectionBenchmark(benchmark_dir)

    return _benchmark_instance
