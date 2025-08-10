"""Tests for advanced search and indexing functionality."""

import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from lackey.advanced_search import AdvancedSearchEngine, FacetCalculator, SortOrder
from lackey.indexing import IndexManager, TaskIndex, TextTokenizer
from lackey.models import Complexity, Project, Task, TaskStatus
from lackey.storage import LackeyStorage


@pytest.fixture
def temp_dir() -> Path:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def storage_manager(temp_dir: Path) -> LackeyStorage:
    """Create a storage manager for testing."""
    return LackeyStorage(str(temp_dir / ".lackey"))


@pytest.fixture
def lackey_core(temp_dir: Path) -> Any:
    """Create a LackeyCore instance for testing."""
    from lackey.core import LackeyCore

    return LackeyCore(str(temp_dir / ".lackey"))


@pytest.fixture
def sample_tasks() -> list[tuple[str, Task]]:
    """Create sample tasks for testing."""
    tasks = []

    # Task 1: Backend API development
    task1 = Task.create_new(
        title="Implement User Authentication API",
        objective="Create secure user authentication endpoints",
        steps=[
            "Design API schema",
            "Implement JWT tokens",
            "Add rate limiting",
            "Write tests",
        ],
        success_criteria=[
            "All endpoints working",
            "Security tests pass",
            "Documentation complete",
        ],
        complexity=Complexity.HIGH,
        context="Part of user management system",
        assigned_to="alice",
        tags=["backend", "api", "security", "authentication"],
    )
    task1.update_status(TaskStatus.IN_PROGRESS)
    task1.complete_step(0)  # Design API schema completed
    tasks.append(("project1", task1))

    # Task 2: Frontend UI development
    task2 = Task.create_new(
        title="Build Login UI Component",
        objective="Create responsive login interface",
        steps=[
            "Design mockups",
            "Implement React component",
            "Add form validation",
            "Style with CSS",
        ],
        success_criteria=[
            "Responsive design",
            "Form validation works",
            "Accessible UI",
        ],
        complexity=Complexity.MEDIUM,
        context="Frontend user interface",
        assigned_to="bob",
        tags=["frontend", "ui", "react", "authentication"],
    )
    task2.update_status(TaskStatus.TODO)
    tasks.append(("project1", task2))

    # Task 3: Database setup
    task3 = Task.create_new(
        title="Setup User Database Schema",
        objective="Design and implement user data storage",
        steps=["Design schema", "Create migrations", "Add indexes", "Setup backup"],
        success_criteria=["Schema deployed", "Performance optimized", "Backup working"],
        complexity=Complexity.MEDIUM,
        context="Database infrastructure",
        assigned_to="alice",
        tags=["database", "schema", "backend", "infrastructure"],
    )
    task3.update_status(TaskStatus.DONE)
    task3.complete_step(0)
    task3.complete_step(1)
    task3.complete_step(2)
    task3.complete_step(3)
    tasks.append(("project1", task3))

    # Task 4: Testing framework
    task4 = Task.create_new(
        title="Setup Automated Testing Pipeline",
        objective="Implement CI/CD testing infrastructure",
        steps=[
            "Configure Jest",
            "Setup GitHub Actions",
            "Add coverage reporting",
            "Create test data",
        ],
        success_criteria=["All tests automated", "Coverage > 90%", "Fast feedback"],
        complexity=Complexity.HIGH,
        context="Quality assurance and CI/CD",
        assigned_to="charlie",
        tags=["testing", "ci-cd", "automation", "quality"],
    )
    task4.update_status(TaskStatus.BLOCKED)
    tasks.append(("project2", task4))

    # Task 5: Documentation
    task5 = Task.create_new(
        title="Write API Documentation",
        objective="Create comprehensive API documentation",
        steps=[
            "Document endpoints",
            "Add examples",
            "Create tutorials",
            "Review content",
        ],
        success_criteria=["All endpoints documented", "Examples work", "User-friendly"],
        complexity=Complexity.LOW,
        context="Developer experience",
        assigned_to="bob",
        tags=["documentation", "api", "developer-experience"],
    )
    task5.update_status(TaskStatus.TODO)
    tasks.append(("project2", task5))

    return tasks


class TestTextTokenizer:
    """Test the text tokenizer."""

    def test_basic_tokenization(self) -> None:
        """Test basic text tokenization."""
        tokenizer = TextTokenizer()

        text = "Implement user authentication with JWT tokens"
        tokens = tokenizer.tokenize(text)

        expected = ["implement", "user", "authentication", "jwt", "tokens"]
        assert tokens == expected

    def test_stop_words_filtered(self) -> None:
        """Test that stop words are filtered out."""
        tokenizer = TextTokenizer()

        text = "This is a test with the common stop words"
        tokens = tokenizer.tokenize(text)

        # Should not contain stop words like "this", "is", "a", "the", "with"
        assert "this" not in tokens
        assert "is" not in tokens
        assert "a" not in tokens
        assert "the" not in tokens
        assert "with" not in tokens
        assert "test" in tokens
        assert "common" in tokens
        assert "stop" in tokens
        assert "words" in tokens

    def test_phrase_extraction(self) -> None:
        """Test phrase extraction."""
        tokenizer = TextTokenizer()

        text = "user authentication system"
        phrases = tokenizer.extract_phrases(text)

        assert "user authentication" in phrases
        assert "authentication system" in phrases
        assert "user authentication system" in phrases


class TestTaskIndex:
    """Test the task indexing system."""

    def test_index_creation(self, temp_dir: Path) -> None:
        """Test creating a new index."""
        index = TaskIndex(temp_dir / "test_index")

        assert index.get_task_count() == 0
        assert index.get_project_count() == 0

    def test_add_task_to_index(
        self, temp_dir: Path, sample_tasks: list[tuple[str, Task]]
    ) -> None:
        """Test adding tasks to the index."""
        index = TaskIndex(temp_dir / "test_index")

        project_id, task = sample_tasks[0]
        index.add_task(project_id, task)

        assert index.get_task_count() == 1
        assert index.get_project_count() == 1
        assert task.id in index.indexed_tasks

    def test_text_search(
        self, temp_dir: Path, sample_tasks: list[tuple[str, Task]]
    ) -> None:
        """Test text search functionality."""
        index = TaskIndex(temp_dir / "test_index")

        # Add all sample tasks
        for project_id, task in sample_tasks:
            index.add_task(project_id, task)

        # Search for "authentication"
        results = index.search_text("authentication")
        assert len(results) >= 2  # Should find API and UI tasks

        # Search for "database"
        results = index.search_text("database")
        assert len(results) >= 1  # Should find database task

        # Search for non-existent term
        results = index.search_text("nonexistent")
        assert len(results) == 0

    def test_field_filtering(
        self, temp_dir: Path, sample_tasks: list[tuple[str, Task]]
    ) -> None:
        """Test field-based filtering."""
        index = TaskIndex(temp_dir / "test_index")

        # Add all sample tasks
        for project_id, task in sample_tasks:
            index.add_task(project_id, task)

        # Filter by status
        todo_tasks = index.filter_by_field("status", "todo")
        assert len(todo_tasks) >= 2

        done_tasks = index.filter_by_field("status", "done")
        assert len(done_tasks) >= 1

        # Filter by complexity
        high_tasks = index.filter_by_field("complexity", "high")
        assert len(high_tasks) >= 2

        # Filter by assignee
        alice_tasks = index.filter_by_field("assigned_to", "alice")
        assert len(alice_tasks) >= 2

    def test_remove_task(
        self, temp_dir: Path, sample_tasks: list[tuple[str, Task]]
    ) -> None:
        """Test removing tasks from index."""
        index = TaskIndex(temp_dir / "test_index")

        project_id, task = sample_tasks[0]
        index.add_task(project_id, task)

        assert index.get_task_count() == 1

        index.remove_task(task.id)

        assert index.get_task_count() == 0
        assert task.id not in index.indexed_tasks

    def test_persist_and_load(
        self, temp_dir: Path, sample_tasks: list[tuple[str, Task]]
    ) -> None:
        """Test persisting and loading indexes."""
        index = TaskIndex(temp_dir / "test_index")

        # Add tasks
        for project_id, task in sample_tasks[:3]:
            index.add_task(project_id, task)

        # Persist
        index.persist_indexes()

        # Create new index and load
        new_index = TaskIndex(temp_dir / "test_index")

        assert new_index.get_task_count() == 3

        # Test that search still works
        results = new_index.search_text("authentication")
        assert len(results) >= 1


class TestIndexManager:
    """Test the index manager."""

    def test_manager_creation(self, temp_dir: Path) -> None:
        """Test creating an index manager."""
        manager = IndexManager(temp_dir)

        assert manager.index.get_task_count() == 0

    def test_search_integration(
        self, temp_dir: Path, sample_tasks: list[tuple[str, Task]]
    ) -> None:
        """Test search integration."""
        manager = IndexManager(temp_dir)

        # Add tasks
        for project_id, task in sample_tasks:
            manager.add_task(project_id, task)

        # Test text search
        results = manager.search(text_query="authentication")
        assert len(results) >= 2

        # Test field filters
        results = manager.search(filters={"status": "done"})
        assert len(results) >= 1

        # Test combined search
        results = manager.search(text_query="api", filters={"assigned_to": "alice"})
        assert len(results) >= 1

    def test_suggestions(
        self, temp_dir: Path, sample_tasks: list[tuple[str, Task]]
    ) -> None:
        """Test autocomplete suggestions."""
        manager = IndexManager(temp_dir)

        # Add tasks
        for project_id, task in sample_tasks:
            manager.add_task(project_id, task)

        # Test assignee suggestions
        suggestions = manager.get_suggestions("assigned_to", "a", 10)
        assert "alice" in suggestions

        # Test tag suggestions
        suggestions = manager.get_suggestions("tags", "back", 10)
        assert "backend" in suggestions


class TestAdvancedSearchEngine:
    """Test the advanced search engine."""

    def test_engine_creation(
        self, temp_dir: Path, storage_manager: LackeyStorage
    ) -> None:
        """Test creating a search engine."""
        engine = AdvancedSearchEngine(storage_manager, str(temp_dir))

        assert engine.storage == storage_manager
        assert engine.index_manager is not None

    def test_query_builder(
        self, temp_dir: Path, storage_manager: LackeyStorage
    ) -> None:
        """Test the query builder."""
        engine = AdvancedSearchEngine(storage_manager, str(temp_dir))

        query = (
            engine.create_query_builder()
            .text("authentication")
            .filter_by_status(TaskStatus.TODO)
            .filter_by_complexity(Complexity.HIGH)
            .sort_by_title()
            .limit(10)
            .build()
        )

        assert query.text == "authentication"
        assert len(query.filters) == 2
        assert len(query.sort_criteria) == 1
        assert query.limit == 10


class TestFacetCalculator:
    """Test facet calculation."""

    def test_calculate_facets(self, sample_tasks: list[tuple[str, Task]]) -> None:
        """Test facet calculation."""
        calculator = FacetCalculator()

        facets = calculator.calculate_facets(sample_tasks)

        # Check status facets
        assert "status" in facets
        assert facets["status"]["todo"] >= 2
        assert facets["status"]["done"] >= 1
        assert facets["status"]["in_progress"] >= 1
        assert facets["status"]["blocked"] >= 1

        # Check complexity facets
        assert "complexity" in facets
        assert facets["complexity"]["high"] >= 2
        assert facets["complexity"]["medium"] >= 2
        assert facets["complexity"]["low"] >= 1

        # Check assignee facets
        assert "assigned_to" in facets
        assert facets["assigned_to"]["alice"] >= 2
        assert facets["assigned_to"]["bob"] >= 2
        assert facets["assigned_to"]["charlie"] >= 1

        # Check tag facets
        assert "tags" in facets
        assert facets["tags"]["backend"] >= 2
        assert facets["tags"]["authentication"] >= 2

        # Check project facets
        assert "project" in facets
        assert facets["project"]["project1"] >= 3
        assert facets["project"]["project2"] >= 2


class TestSearchIntegration:
    """Test full search integration."""

    def test_end_to_end_search(
        self, lackey_core: Any, sample_tasks: list[tuple[str, Task]]
    ) -> None:
        """Test complete search workflow."""
        # Create projects first
        project1 = Project.create_new(
            "Test Project 1", "Test project 1", ["Test objective 1"]
        )
        project2 = Project.create_new(
            "Test Project 2", "Test project 2", ["Test objective 2"]
        )
        lackey_core.storage.create_project(project1)
        lackey_core.storage.create_project(project2)

        # Add tasks using LackeyCore (which handles both storage and indexing)
        for project_id, task in sample_tasks:
            # Map project_id to actual project name
            actual_project_id = project1.id if project_id == "project1" else project2.id
            lackey_core.storage.create_task(actual_project_id, task)
            lackey_core.search_engine.update_task_index(actual_project_id, task)

        # Build complex query
        query = (
            lackey_core.search_engine.create_query_builder()
            .text("api")
            .filter_by_assignee("alice")
            .sort_by_created_date(SortOrder.DESC)
            .limit(5)
            .build()
        )

        # Execute search
        result = lackey_core.search_engine.search(query)

        # Verify results
        assert result.total_count >= 1
        assert len(result.tasks) <= 5
        assert result.execution_time_ms > 0
        assert "status" in result.facets

        # Verify all returned tasks contain "api" and are assigned to "alice"
        for project_id, task in result.tasks:
            # Should contain "api" in searchable text
            searchable_text = (
                f"{task.title} {task.objective} {task.context or ''}".lower()
            )
            assert "api" in searchable_text
            assert task.assigned_to == "alice"

    def test_performance_with_many_tasks(self, lackey_core: Any) -> None:
        """Test search performance with many tasks."""
        # Create projects first
        projects = {}
        for i in range(3):
            project = Project.create_new(
                f"Test Project {i}", f"Test project {i}", [f"Test objective {i}"]
            )
            lackey_core.storage.create_project(project)
            projects[f"project{i}"] = project.id

        # Create many tasks
        for i in range(100):
            task = Task.create_new(
                title=f"Task {i}",
                objective=f"Objective for task {i}",
                steps=[f"Step 1 for task {i}", f"Step 2 for task {i}"],
                success_criteria=[f"Success criteria for task {i}"],
                complexity=Complexity.MEDIUM,
                assigned_to=f"user{i % 5}",
                tags=[f"tag{i % 10}", "common"],
            )
            project_key = f"project{i % 3}"
            actual_project_id = projects[project_key]
            lackey_core.storage.create_task(actual_project_id, task)
            lackey_core.search_engine.update_task_index(actual_project_id, task)

        # Test search performance
        start_time = datetime.now(UTC)

        query = (
            lackey_core.search_engine.create_query_builder()
            .text("task")
            .filter_by_tag("common")
            .sort_by_title()
            .limit(20)
            .build()
        )

        result = lackey_core.search_engine.search(query)

        end_time = datetime.now(UTC)
        search_time_ms = (end_time - start_time).total_seconds() * 1000

        # Should be fast (under 500ms for 100 tasks)
        assert search_time_ms < 500
        assert result.total_count == 100
        assert len(result.tasks) == 20

    def test_search_stats(
        self, lackey_core: Any, sample_tasks: list[tuple[str, Task]]
    ) -> None:
        """Test search statistics."""
        # Create projects first
        project1 = Project.create_new(
            "Test Project 1", "Test project 1", ["Test objective 1"]
        )
        project2 = Project.create_new(
            "Test Project 2", "Test project 2", ["Test objective 2"]
        )
        lackey_core.storage.create_project(project1)
        lackey_core.storage.create_project(project2)

        # Add tasks
        for project_id, task in sample_tasks:
            # Map project_id to actual project name
            actual_project_id = project1.id if project_id == "project1" else project2.id
            lackey_core.storage.create_task(actual_project_id, task)
            lackey_core.search_engine.update_task_index(actual_project_id, task)

        # Get stats
        stats = lackey_core.search_engine.get_search_stats()

        assert stats["indexed_tasks"] == len(sample_tasks)
        assert stats["indexed_projects"] == 2  # project1 and project2
        assert "index_size_mb" in stats
        assert "last_index_update" in stats


if __name__ == "__main__":
    pytest.main([__file__])
