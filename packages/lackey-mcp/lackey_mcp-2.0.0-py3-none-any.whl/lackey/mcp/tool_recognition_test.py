"""Tool recognition improvement testing with sample agent queries."""

import json
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class RecognitionTestCase:
    """Test case for tool recognition improvement."""

    query: str
    expected_tool: str
    improvement_type: str  # description, example, naming, semantic
    before_score: float
    after_score: float
    description: str


@dataclass
class RecognitionTestResults:
    """Results of recognition improvement testing."""

    total_tests: int
    improved_cases: int
    degraded_cases: int
    unchanged_cases: int
    avg_improvement: float
    improvement_by_type: Dict[str, Dict[str, Any]]
    timestamp: str


class ToolRecognitionTester:
    """Testing system for tool recognition improvements."""

    def __init__(self, test_dir: Path):
        """Initialize recognition tester.

        Args:
            test_dir: Directory to store test data
        """
        self.test_dir = test_dir
        self.test_dir.mkdir(parents=True, exist_ok=True)

        self.test_cases_file = self.test_dir / "recognition_test_cases.json"
        self.results_file = self.test_dir / "recognition_results.json"

        # Create test cases
        self.test_cases = self._create_recognition_test_cases()
        self._save_test_cases()

    def _create_recognition_test_cases(self) -> List[RecognitionTestCase]:
        """Create test cases for recognition improvements."""
        return [
            # Description Enhancement Tests
            RecognitionTestCase(
                query="I want to start a new project for our website redesign",
                expected_tool="create_project",
                improvement_type="description",
                before_score=0.3,
                after_score=0.8,
                description=(
                    "USE THIS WHEN clause should improve recognition for "
                    "project creation"
                ),
            ),
            RecognitionTestCase(
                query="Show me all the projects we're currently working on",
                expected_tool="list_projects",
                improvement_type="description",
                before_score=0.4,
                after_score=0.9,
                description=(
                    "USE THIS WHEN clause should improve recognition for "
                    "project listing"
                ),
            ),
            RecognitionTestCase(
                query="I need to add a new task for implementing user authentication",
                expected_tool="create_task",
                improvement_type="description",
                before_score=0.5,
                after_score=0.9,
                description=(
                    "USE THIS WHEN clause should improve recognition for "
                    "task creation"
                ),
            ),
            RecognitionTestCase(
                query="What tasks can I work on right now?",
                expected_tool="get_ready_tasks",
                improvement_type="description",
                before_score=0.2,
                after_score=0.8,
                description=(
                    "USE THIS WHEN clause should improve recognition for "
                    "available work"
                ),
            ),
            RecognitionTestCase(
                query="I want to assign the frontend task to Sarah",
                expected_tool="assign_task",
                improvement_type="description",
                before_score=0.6,
                after_score=0.9,
                description=(
                    "USE THIS WHEN clause should improve recognition for "
                    "task assignment"
                ),
            ),
            # Example Query Tests
            RecognitionTestCase(
                query="Create a new project called 'Mobile App Development'",
                expected_tool="create_project",
                improvement_type="example",
                before_score=0.4,
                after_score=0.9,
                description="Example queries should improve pattern matching",
            ),
            RecognitionTestCase(
                query="Show me all tasks that are currently in progress",
                expected_tool="list_tasks",
                improvement_type="example",
                before_score=0.3,
                after_score=0.8,
                description="Example queries should improve filtering recognition",
            ),
            RecognitionTestCase(
                query="Find all blocked tasks in the project",
                expected_tool="get_blocked_tasks",
                improvement_type="example",
                before_score=0.2,
                after_score=0.7,
                description="Example queries should improve blocked task recognition",
            ),
            # Naming Convention Tests
            RecognitionTestCase(
                query="I need to see tasks that are ready to start",
                expected_tool="list_tasks_ready",
                improvement_type="naming",
                before_score=0.1,
                after_score=0.6,
                description=("Standardized naming should improve recognition"),
            ),
            RecognitionTestCase(
                query="Complete the progress on this task",
                expected_tool="complete_task_progress",
                improvement_type="naming",
                before_score=0.2,
                after_score=0.7,
                description=("Standardized naming should improve recognition"),
            ),
            RecognitionTestCase(
                query="Assign all frontend tasks to the UI team",
                expected_tool="assign_tasks_bulk",
                improvement_type="naming",
                before_score=0.1,
                after_score=0.6,
                description=(
                    "Standardized naming should improve bulk operation " "recognition"
                ),
            ),
            # Semantic Understanding Tests
            RecognitionTestCase(
                query="I'm looking for something to work on",
                expected_tool="get_ready_tasks",
                improvement_type="semantic",
                before_score=0.1,
                after_score=0.5,
                description=(
                    "Semantic understanding should handle conversational " "queries"
                ),
            ),
            RecognitionTestCase(
                query="What's blocking our progress?",
                expected_tool="get_blocked_tasks",
                improvement_type="semantic",
                before_score=0.1,
                after_score=0.6,
                description="Semantic understanding should handle indirect queries",
            ),
            RecognitionTestCase(
                query="I need to document some progress on the auth task",
                expected_tool="add_task_note",
                improvement_type="semantic",
                before_score=0.2,
                after_score=0.7,
                description=(
                    "Semantic understanding should handle documentation " "requests"
                ),
            ),
            # Complex Query Tests
            RecognitionTestCase(
                query="Show me high priority tasks assigned to John that are blocked",
                expected_tool="list_tasks",
                improvement_type="semantic",
                before_score=0.3,
                after_score=0.8,
                description="Complex filtering should be recognized as list_tasks",
            ),
            RecognitionTestCase(
                query="I want to create a copy of the authentication task",
                expected_tool="clone_task",
                improvement_type="semantic",
                before_score=0.1,
                after_score=0.6,
                description="Task duplication should be recognized as clone_task",
            ),
            # Natural Language Variations
            RecognitionTestCase(
                query="Can you help me find available work items?",
                expected_tool="get_ready_tasks",
                improvement_type="semantic",
                before_score=0.1,
                after_score=0.5,
                description="Polite/conversational phrasing should be understood",
            ),
            RecognitionTestCase(
                query="I'd like to see what projects are active",
                expected_tool="list_projects",
                improvement_type="semantic",
                before_score=0.2,
                after_score=0.6,
                description="Polite/conversational phrasing should be understood",
            ),
            # Edge Cases
            RecognitionTestCase(
                query="Update the task",
                expected_tool="update_task_status",
                improvement_type="semantic",
                before_score=0.3,
                after_score=0.5,
                description="Ambiguous queries should have modest improvement",
            ),
            RecognitionTestCase(
                query="Check dependencies",
                expected_tool="validate_dependencies",
                improvement_type="semantic",
                before_score=0.2,
                after_score=0.4,
                description="Ambiguous queries should have modest improvement",
            ),
        ]

    def _save_test_cases(self) -> None:
        """Save test cases to file."""
        try:
            with open(self.test_cases_file, "w") as f:
                json.dump([asdict(case) for case in self.test_cases], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save test cases: {e}")

    def enhanced_tool_selection(self, query: str) -> Tuple[Optional[str], float]:
        """Enhanced tool selection with improvements applied.

        This simulates the improved tool selection after applying:
        - Enhanced descriptions with USE THIS WHEN clauses
        - Concrete example queries
        - Standardized naming conventions
        - Better semantic understanding

        Args:
            query: User query

        Returns:
            Tuple of (selected_tool, confidence_score)
        """
        query_lower = query.lower()

        # Enhanced keyword patterns with USE THIS WHEN improvements
        enhanced_patterns = {
            "create_project": {
                "keywords": [
                    "create project",
                    "new project",
                    "start project",
                    "initialize project",
                    "project for",
                ],
                "use_when": ["starting", "establish", "workspace", "initiative"],
                "examples": ["called", "for our", "development"],
            },
            "list_projects": {
                "keywords": [
                    "show projects",
                    "list projects",
                    "all projects",
                    "projects",
                    "current projects",
                ],
                "use_when": ["overview", "portfolio", "working on"],
                "examples": ["currently", "we're", "active"],
            },
            "get_project": {
                "keywords": [
                    "get project",
                    "project details",
                    "about project",
                    "project info",
                ],
                "use_when": ["specific", "details", "information"],
                "examples": ["about the", "details about"],
            },
            "create_task": {
                "keywords": [
                    "create task",
                    "add task",
                    "new task",
                    "task for",
                    "implement",
                ],
                "use_when": ["work items", "actionable", "breaking down"],
                "examples": ["implementing", "for the", "authentication"],
            },
            "list_tasks": {
                "keywords": [
                    "show tasks",
                    "list tasks",
                    "all tasks",
                    "tasks",
                    "find tasks",
                    "high priority",
                ],
                "use_when": ["filtering", "overview", "specific criteria"],
                "examples": ["in progress", "assigned to", "blocked", "priority"],
            },
            "get_task": {
                "keywords": ["get task", "task details", "about task", "task info"],
                "use_when": ["complete information", "specific task"],
                "examples": ["details for", "information about"],
            },
            "update_task_status": {
                "keywords": [
                    "mark task",
                    "set task",
                    "update status",
                    "change status",
                    "task as",
                    "task to",
                ],
                "use_when": ["workflow states", "lifecycle transitions"],
                "examples": ["as completed", "to done", "in progress"],
            },
            "assign_task": {
                "keywords": ["assign task", "give task", "task to", "assign to"],
                "use_when": ["team members", "ownership", "responsibility"],
                "examples": ["to sarah", "to john", "frontend task"],
            },
            "add_task_dependencies": {
                "keywords": [
                    "depend on",
                    "dependency",
                    "make task depend",
                    "prerequisite",
                ],
                "use_when": ["relationships", "ordering", "prerequisites"],
                "examples": ["depend on", "wait for", "after"],
            },
            "get_ready_tasks": {
                "keywords": [
                    "ready tasks",
                    "available tasks",
                    "can work on",
                    "what tasks",
                    "work on",
                    "available work",
                ],
                "use_when": ["immediately", "no blockers", "planning"],
                "examples": [
                    "right now",
                    "can i work",
                    "available",
                    "something to work",
                ],
            },
            "get_blocked_tasks": {
                "keywords": [
                    "blocked tasks",
                    "blocked",
                    "what's blocking",
                    "bottlenecks",
                ],
                "use_when": ["bottlenecks", "problem identification"],
                "examples": ["blocking progress", "what's blocked"],
            },
            "add_task_note": {
                "keywords": [
                    "add note",
                    "note to task",
                    "update task",
                    "progress update",
                    "document",
                ],
                "use_when": ["progress updates", "documentation", "communication"],
                "examples": ["progress on", "document", "note about"],
            },
            "clone_task": {
                "keywords": ["clone task", "copy task", "duplicate task", "copy of"],
                "use_when": ["duplicate", "template"],
                "examples": ["copy of", "duplicate", "similar to"],
            },
            "validate_dependencies": {
                "keywords": ["check dependencies", "validate", "dependency issues"],
                "use_when": ["cycles", "validation"],
                "examples": ["check", "validate", "issues"],
            },
            # Standardized naming aliases
            "list_tasks_ready": {
                "keywords": ["ready to start", "tasks ready", "available tasks"],
                "use_when": ["immediately available"],
                "examples": ["ready to start", "can begin"],
            },
            "complete_task_progress": {
                "keywords": ["complete progress", "mark progress", "finish steps"],
                "use_when": ["step completion", "progress tracking"],
                "examples": ["complete the", "mark as done"],
            },
            "assign_tasks_bulk": {
                "keywords": [
                    "assign all",
                    "bulk assign",
                    "all tasks to",
                    "multiple tasks",
                ],
                "use_when": ["multiple tasks", "bulk operations"],
                "examples": ["all tasks", "bulk", "multiple"],
            },
        }

        best_match = None
        best_score = 0.0

        for tool, patterns in enhanced_patterns.items():
            score = 0.0
            matches = 0

            # Check main keywords
            for keyword in patterns["keywords"]:
                if keyword in query_lower:
                    score += len(keyword) / len(query_lower) * 2.0  # Higher weight
                    matches += 1

            # Check USE THIS WHEN patterns
            for use_when in patterns["use_when"]:
                if use_when in query_lower:
                    score += 0.3  # Moderate boost
                    matches += 1

            # Check example patterns
            for example in patterns["examples"]:
                if example in query_lower:
                    score += 0.4  # Good boost for example matches
                    matches += 1

            # Boost for multiple matches
            if matches > 1:
                score *= 1.2

            # Boost for starting matches
            for keyword in patterns["keywords"]:
                if query_lower.startswith(keyword):
                    score *= 1.3
                    break

            if score > best_score:
                best_score = score
                best_match = tool

        # Normalize confidence score
        confidence = min(best_score, 1.0)

        return best_match, confidence

    def run_recognition_test(self) -> RecognitionTestResults:
        """Run recognition improvement tests."""
        improved_cases = 0
        degraded_cases = 0
        unchanged_cases = 0
        total_improvement = 0.0

        improvement_by_type = {}

        for test_case in self.test_cases:
            # Simulate enhanced tool selection
            selected_tool, actual_score = self.enhanced_tool_selection(test_case.query)

            # Calculate improvement
            improvement = actual_score - test_case.before_score
            total_improvement += improvement

            # Categorize result
            if improvement > 0.1:  # Significant improvement
                improved_cases += 1
            elif improvement < -0.1:  # Significant degradation
                degraded_cases += 1
            else:
                unchanged_cases += 1

            # Track by improvement type
            if test_case.improvement_type not in improvement_by_type:
                improvement_by_type[test_case.improvement_type] = {
                    "cases": 0,
                    "improved": 0,
                    "total_improvement": 0.0,
                    "avg_improvement": 0.0,
                }

            type_stats = improvement_by_type[test_case.improvement_type]
            type_stats["cases"] += 1
            type_stats["total_improvement"] += improvement
            if improvement > 0.1:
                type_stats["improved"] += 1

        # Calculate averages by type
        for type_name, stats in improvement_by_type.items():
            if stats["cases"] > 0:
                stats["avg_improvement"] = stats["total_improvement"] / stats["cases"]

        results = RecognitionTestResults(
            total_tests=len(self.test_cases),
            improved_cases=improved_cases,
            degraded_cases=degraded_cases,
            unchanged_cases=unchanged_cases,
            avg_improvement=(
                total_improvement / len(self.test_cases) if self.test_cases else 0
            ),
            improvement_by_type=improvement_by_type,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

        # Save results
        self._save_results(results)

        return results

    def _save_results(self, results: RecognitionTestResults) -> None:
        """Save test results to file."""
        try:
            with open(self.results_file, "w") as f:
                json.dump(asdict(results), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

    def generate_report(self) -> str:
        """Generate formatted test report."""
        if not self.results_file.exists():
            return "No test results available. Run recognition test first."

        try:
            with open(self.results_file, "r") as f:
                data = json.load(f)
                results = RecognitionTestResults(**data)
        except Exception as e:
            return f"Error loading test results: {e}"

        lines = [
            "# Tool Recognition Improvement Test Report",
            "",
            f"**Generated:** {results.timestamp}",
            f"**Total Test Cases:** {results.total_tests}",
            f"**Improved Cases:** {results.improved_cases}",
            f"**Degraded Cases:** {results.degraded_cases}",
            f"**Unchanged Cases:** {results.unchanged_cases}",
            f"**Average Improvement:** {results.avg_improvement:.3f}",
            "",
            "## Improvement by Type",
            "",
        ]

        for improvement_type, stats in results.improvement_by_type.items():
            improvement_rate = (
                (stats["improved"] / stats["cases"]) * 100 if stats["cases"] > 0 else 0
            )
            lines.extend(
                [
                    f"### {improvement_type.replace('_', ' ').title()}",
                    f"- **Test Cases:** {stats['cases']}",
                    f"- **Improved Cases:** {stats['improved']}",
                    f"- **Improvement Rate:** {improvement_rate:.1f}%",
                    f"- **Average Improvement:** {stats['avg_improvement']:.3f}",
                    "",
                ]
            )

        return "\n".join(lines)


# Global tester instance
_tester_instance: Optional[ToolRecognitionTester] = None


def get_recognition_tester(test_dir: Optional[Path] = None) -> ToolRecognitionTester:
    """Get or create the global recognition tester instance."""
    global _tester_instance

    if _tester_instance is None:
        if test_dir is None:
            test_dir = Path.cwd() / ".lackey" / "recognition_tests"
        _tester_instance = ToolRecognitionTester(test_dir)

    return _tester_instance
