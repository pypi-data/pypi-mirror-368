"""Tests for core task operations API."""

from typing import Any
from unittest.mock import Mock, patch

import pytest

from lackey.core import LackeyCore
from lackey.dependencies import DependencyError
from lackey.models import Complexity, Project, Task, TaskStatus
from lackey.storage import TaskNotFoundError


class TestTaskStatusOperations:
    """Test task status update operations."""

    def test_update_task_status_valid_transition(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test updating task status with valid transition."""
        core, project, tasks = core_with_project_and_tasks
        task = tasks[0]

        # Capture original timestamp before update
        original_updated = task.updated

        # Update status from TODO to IN_PROGRESS
        updated_task = core.update_task_status(
            project.id, task.id, TaskStatus.IN_PROGRESS
        )

        assert updated_task.status == TaskStatus.IN_PROGRESS
        assert updated_task.updated >= original_updated

    def test_update_task_status_with_note(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test updating task status with a note."""
        core, project, tasks = core_with_project_and_tasks
        task = tasks[0]

        updated_task = core.update_task_status(
            project.id,
            task.id,
            TaskStatus.IN_PROGRESS,
            note="Started working on this task",
        )

        assert updated_task.status == TaskStatus.IN_PROGRESS
        assert len(updated_task.note_manager.get_notes()) == 1
        notes = updated_task.note_manager.get_notes()
        assert "Started working on this task" in notes[0].content

    def test_update_task_status_invalid_task(
        self, core_with_project: tuple[LackeyCore, Project]
    ) -> None:
        """Test updating status of non-existent task."""
        core, project = core_with_project

        with pytest.raises(TaskNotFoundError):
            core.update_task_status(
                project.id, "invalid-task-id", TaskStatus.IN_PROGRESS
            )

    def test_bulk_update_task_status(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test bulk status updates."""
        core, project, tasks = core_with_project_and_tasks
        task_ids = [task.id for task in tasks[:2]]

        results = core.bulk_update_task_status(
            project.id, task_ids, TaskStatus.IN_PROGRESS
        )

        assert len(results["updated"]) == 2
        assert len(results["failed"]) == 0

        # Verify tasks were updated
        for task_id in task_ids:
            updated_task = core.get_task(task_id)
            assert updated_task.status == TaskStatus.IN_PROGRESS


class TestStepCompletionOperations:
    """Test step completion tracking operations."""

    def test_complete_task_steps(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test completing multiple task steps."""
        core, project, tasks = core_with_project_and_tasks
        task = tasks[0]

        updated_task = core.complete_task_steps(
            project.id, task.id, [0, 1], note="Completed first two steps"
        )

        assert 0 in updated_task.completed_steps
        assert 1 in updated_task.completed_steps
        assert len(updated_task.note_manager.get_notes()) == 1

    def test_uncomplete_task_steps(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test uncompleting task steps."""
        core, project, tasks = core_with_project_and_tasks
        task = tasks[0]

        # First complete some steps
        core.complete_task_steps(project.id, task.id, [0, 1, 2])

        # Then uncomplete one
        updated_task = core.uncomplete_task_steps(
            project.id, task.id, [1], note="Need to redo step 2"
        )

        assert 0 in updated_task.completed_steps
        assert 1 not in updated_task.completed_steps
        assert 2 in updated_task.completed_steps

    def test_get_task_progress_summary(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test getting task progress summary."""
        core, project, tasks = core_with_project_and_tasks
        task = tasks[0]

        # Complete some steps
        core.complete_task_steps(project.id, task.id, [0, 1])

        progress = core.get_task_progress_summary(project.id, task.id)

        assert progress["completed_steps"] == 2
        assert progress["total_steps"] == len(task.steps)
        assert progress["completion_percentage"] == (2 / len(task.steps)) * 100
        assert progress["remaining_steps"] == len(task.steps) - 2

    def test_auto_status_update_on_completion(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test automatic status update when all steps completed."""
        core, project, tasks = core_with_project_and_tasks
        task = tasks[0]

        # Complete all steps
        all_step_indices = list(range(len(task.steps)))
        updated_task = core.complete_task_steps(
            project.id, task.id, all_step_indices, auto_complete=True
        )

        assert updated_task.status == TaskStatus.DONE
        assert len(updated_task.completed_steps) == len(task.steps)


class TestTaskAssignmentOperations:
    """Test task assignment and reassignment operations."""

    def test_assign_task(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test assigning a task to someone."""
        core, project, tasks = core_with_project_and_tasks
        task = tasks[0]

        updated_task = core.assign_task(
            project.id,
            task.id,
            "developer",
            note="Assigned to developer for implementation",
        )

        assert updated_task.assigned_to == "developer"
        assert len(updated_task.note_manager.get_notes()) == 1

    def test_reassign_task(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test reassigning a task."""
        core, project, tasks = core_with_project_and_tasks
        task = tasks[0]

        # First assign
        core.assign_task(project.id, task.id, "developer")

        # Then reassign
        updated_task = core.reassign_task(
            project.id,
            task.id,
            "senior-developer",
            note="Reassigned to senior developer",
        )

        assert updated_task.assigned_to == "senior-developer"
        assert len(updated_task.note_manager.get_notes()) == 2

    def test_unassign_task(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test unassigning a task."""
        core, project, tasks = core_with_project_and_tasks
        task = tasks[0]

        # First assign
        core.assign_task(project.id, task.id, "developer")

        # Then unassign
        updated_task = core.unassign_task(
            project.id, task.id, note="Unassigned for reassignment"
        )

        assert updated_task.assigned_to is None
        assert len(updated_task.note_manager.get_notes()) == 2

    def test_bulk_assign_tasks(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test bulk task assignment."""
        core, project, tasks = core_with_project_and_tasks
        task_ids = [task.id for task in tasks[:2]]

        results = core.bulk_assign_tasks(project.id, task_ids, "developer")

        assert len(results["assigned"]) == 2
        assert len(results["failed"]) == 0

        # Verify assignments
        for task_id in task_ids:
            updated_task = core.get_task(task_id)
            assert updated_task.assigned_to == "developer"


class TestDependencyManagementOperations:
    """Test dynamic dependency management operations."""

    def test_add_multiple_dependencies(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test adding multiple dependencies at once."""
        core, project, tasks = core_with_project_and_tasks
        target_task = tasks[0]
        dependency_ids = [tasks[1].id, tasks[2].id]

        updated_task = core.add_task_dependencies(
            project.id, target_task.id, dependency_ids
        )

        assert tasks[1].id in updated_task.dependencies
        assert tasks[2].id in updated_task.dependencies

    def test_remove_multiple_dependencies(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test removing multiple dependencies at once."""
        core, project, tasks = core_with_project_and_tasks
        target_task = tasks[0]
        dependency_ids = [tasks[1].id, tasks[2].id]

        # First add dependencies
        core.add_task_dependencies(project.id, target_task.id, dependency_ids)

        # Then remove them
        updated_task = core.remove_task_dependencies(
            project.id, target_task.id, dependency_ids
        )

        assert tasks[1].id not in updated_task.dependencies
        assert tasks[2].id not in updated_task.dependencies

    def test_replace_task_dependencies(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test replacing all task dependencies."""
        core, project, tasks = core_with_project_and_tasks
        target_task = tasks[0]

        # Add initial dependencies
        initial_deps = [tasks[1].id]
        core.add_task_dependencies(project.id, target_task.id, initial_deps)

        # Replace with new dependencies
        new_deps = [tasks[2].id, tasks[3].id]
        updated_task = core.replace_task_dependencies(
            project.id, target_task.id, new_deps
        )

        assert tasks[1].id not in updated_task.dependencies
        assert tasks[2].id in updated_task.dependencies
        assert tasks[3].id in updated_task.dependencies

    def test_dependency_cycle_prevention(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test that dependency cycles are prevented."""
        core, project, tasks = core_with_project_and_tasks

        # Create a potential cycle: A -> B -> C -> A
        core.add_task_dependency(project.id, tasks[0].id, tasks[1].id)
        core.add_task_dependency(project.id, tasks[1].id, tasks[2].id)

        # This should fail due to cycle detection
        with pytest.raises(DependencyError, match="cycle"):
            core.add_task_dependency(project.id, tasks[2].id, tasks[0].id)


class TestAdvancedTaskOperations:
    """Test advanced task operations."""

    def test_clone_task(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test cloning a task."""
        core, project, tasks = core_with_project_and_tasks
        original_task = tasks[0]

        cloned_task = core.clone_task(
            project.id,
            original_task.id,
            new_title="Cloned: " + original_task.title,
            copy_dependencies=False,
        )

        assert cloned_task.id != original_task.id
        assert cloned_task.title == "Cloned: " + original_task.title
        assert cloned_task.objective == original_task.objective
        assert cloned_task.steps == original_task.steps
        assert cloned_task.status == TaskStatus.TODO
        assert len(cloned_task.dependencies) == 0  # copy_dependencies=False

    def test_clone_task_with_dependencies(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test cloning a task with dependencies."""
        core, project, tasks = core_with_project_and_tasks
        original_task = tasks[0]

        # Add dependency to original
        core.add_task_dependency(project.id, original_task.id, tasks[1].id)

        cloned_task = core.clone_task(
            project.id,
            original_task.id,
            new_title="Cloned with deps",
            copy_dependencies=True,
        )

        assert tasks[1].id in cloned_task.dependencies

    def test_archive_task(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test archiving a task."""
        core, project, tasks = core_with_project_and_tasks
        task = tasks[0]

        archived_task = core.archive_task(
            project.id, task.id, reason="No longer needed"
        )

        assert len(archived_task.note_manager.get_notes()) == 1
        assert "No longer needed" in archived_task.note_manager.get_notes()[0].content

    def test_restore_task(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test restoring an archived task."""
        core, project, tasks = core_with_project_and_tasks
        task = tasks[0]

        # First archive
        core.archive_task(project.id, task.id, reason="Test archive")

        # Then restore
        restored_task = core.restore_task(
            project.id, task.id, note="Restored for continued work"
        )

        assert (
            len(restored_task.note_manager.get_notes()) == 2
        )  # Archive + restore notes

    def test_split_task(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test splitting a task into subtasks."""
        core, project, tasks = core_with_project_and_tasks
        original_task = tasks[0]

        # Define subtask specifications
        subtask_specs = [
            {
                "title": "Subtask 1",
                "objective": "First part of the work",
                "steps": original_task.steps[:2],
                "success_criteria": ["Criteria 1"],
            },
            {
                "title": "Subtask 2",
                "objective": "Second part of the work",
                "steps": original_task.steps[2:],
                "success_criteria": ["Criteria 2"],
            },
        ]

        result = core.split_task(
            project.id, original_task.id, subtask_specs, archive_original=True
        )

        assert len(result["subtasks"]) == 2
        assert result["original_archived"] is True

        # Verify subtasks were created
        for subtask_id in result["subtask_ids"]:
            subtask = core.get_task(subtask_id)
            assert subtask.complexity == original_task.complexity
            assert subtask.assigned_to == original_task.assigned_to


class TestTaskValidationOperations:
    """Test task validation operations."""

    def test_validate_task_data(
        self, core_with_project: tuple[LackeyCore, Project]
    ) -> None:
        """Test task data validation."""
        core, project = core_with_project

        # Valid task data
        valid_data = {
            "title": "Valid Task",
            "objective": "Do something useful",
            "steps": ["Step 1", "Step 2"],
            "success_criteria": ["Success 1"],
            "complexity": "medium",
        }

        validation_result = core.validate_task_data(valid_data)
        assert validation_result["is_valid"] is True
        assert len(validation_result["errors"]) == 0

    def test_validate_task_data_invalid(
        self, core_with_project: tuple[LackeyCore, Project]
    ) -> None:
        """Test task data validation with invalid data."""
        core, project = core_with_project

        # Invalid task data
        invalid_data = {
            "title": "",  # Empty title
            "objective": "Do something",
            "steps": [],  # No steps
            "success_criteria": [],  # No success criteria
            "complexity": "invalid",  # Invalid complexity
        }

        validation_result = core.validate_task_data(invalid_data)
        assert validation_result["is_valid"] is False
        assert len(validation_result["errors"]) > 0

    def test_validate_task_dependencies_integrity(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test validating task dependency integrity."""
        core, project, tasks = core_with_project_and_tasks

        # Add some dependencies
        core.add_task_dependency(project.id, tasks[0].id, tasks[1].id)
        core.add_task_dependency(project.id, tasks[1].id, tasks[2].id)

        integrity_result = core.validate_task_dependencies_integrity(project.id)

        assert integrity_result["is_valid"] is True
        assert len(integrity_result["orphaned_dependencies"]) == 0
        assert len(integrity_result["cycles"]) == 0


class TestBulkTaskOperations:
    """Test bulk task operations."""

    def test_bulk_delete_tasks(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test bulk task deletion."""
        core, project, tasks = core_with_project_and_tasks
        task_ids = [tasks[0].id, tasks[1].id]

        result = core.bulk_delete_tasks(project.id, task_ids)

        assert len(result["deleted"]) == 2
        assert len(result["failed"]) == 0

        # Verify tasks were deleted
        for task_id in task_ids:
            with pytest.raises(TaskNotFoundError):
                core.get_task(task_id)

    def test_bulk_update_task_properties(
        self, core_with_project_and_tasks: tuple[LackeyCore, Project, list[Task]]
    ) -> None:
        """Test bulk updating task properties."""
        core, project, tasks = core_with_project_and_tasks
        task_ids = [task.id for task in tasks[:2]]

        updates = {"complexity": "high", "tags": ["urgent", "priority"]}

        result = core.bulk_update_task_properties(project.id, task_ids, updates)

        assert len(result["updated"]) == 2
        assert len(result["failed"]) == 0

        # Verify updates
        for task_id in task_ids:
            updated_task = core.get_task(task_id)
            assert updated_task.complexity == Complexity.HIGH
            assert "urgent" in updated_task.tags
            assert "priority" in updated_task.tags


@pytest.fixture  # type: ignore[misc]
def core_with_project() -> tuple[LackeyCore, Project]:
    """Fixture providing core with a test project."""
    # Create a mock storage instance
    mock_storage = Mock()

    # Mock project
    from lackey.models import Project

    project = Project.create_new(
        friendly_name="Test Project",
        description="Test project description",
        objectives=["Objective 1", "Objective 2"],
    )

    # Mock get_task to raise TaskNotFoundError for invalid task IDs
    def mock_get_task(task_id: str) -> Task:
        raise TaskNotFoundError(f"Task {task_id} not found")

    mock_storage.get_project.return_value = project
    mock_storage.find_project_by_name.return_value = project
    mock_storage.get_config.return_value = {}
    mock_storage.get_task.side_effect = mock_get_task

    # Create core with mocked storage
    with patch("lackey.core.LackeyStorage") as mock_storage_class:
        mock_storage_class.return_value = mock_storage
        core = LackeyCore()

        return core, project


@pytest.fixture  # type: ignore[misc]
def core_with_project_and_tasks(
    core_with_project: tuple[LackeyCore, Project]
) -> tuple[LackeyCore, Project, list[Task]]:
    """Fixture providing core with project and test tasks."""
    core, project = core_with_project

    # Create test tasks
    tasks = []
    for i in range(5):
        task = Task.create_new(
            title=f"Test Task {i+1}",
            objective=f"Objective for task {i+1}",
            steps=[
                f"Step 1 for task {i+1}",
                f"Step 2 for task {i+1}",
                f"Step 3 for task {i+1}",
            ],
            success_criteria=[f"Success criteria for task {i+1}"],
            complexity=Complexity.MEDIUM,
        )
        tasks.append(task)

    # Mock storage methods
    def mock_get_task(task_id: str) -> Task:
        for task in tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(f"Task {task_id} not found")

    def mock_update_task(project_id: str, task: Task) -> Task:
        # Find and update the task in our list
        for i, existing_task in enumerate(tasks):
            if existing_task.id == task.id:
                tasks[i] = task
                break
        return task

    def mock_create_task(project_id: str, task: Task) -> Task:
        tasks.append(task)
        return task

    def mock_delete_task(project_id: str, task_id: str) -> None:
        for i, task in enumerate(tasks):
            if task.id == task_id:
                del tasks[i]
                break

    def mock_list_project_tasks(
        project_id: str, status_filter: Any = None
    ) -> list[Task]:
        if status_filter:
            return [t for t in tasks if t.status == status_filter]
        return tasks.copy()

    # Configure mock methods
    core.storage.get_task.side_effect = mock_get_task  # type: ignore[attr-defined]
    core.storage.update_task.side_effect = (  # type: ignore[attr-defined]
        mock_update_task
    )
    core.storage.create_task.side_effect = (  # type: ignore[attr-defined]
        mock_create_task
    )
    core.storage.delete_task.side_effect = (  # type: ignore[attr-defined]
        mock_delete_task
    )
    core.storage.list_project_tasks.side_effect = (  # type: ignore[attr-defined]
        mock_list_project_tasks
    )

    # Add missing mocks for delete_task method
    def mock_list_projects() -> list[dict]:
        return [{"id": project.id, "name": project.name}]

    def mock_find_project_id_by_task_id(task_id: str) -> str:
        return project.id

    core.storage.list_projects.side_effect = (  # type: ignore[attr-defined]
        mock_list_projects
    )
    core.storage.find_project_id_by_task_id.side_effect = (  # type: ignore
        mock_find_project_id_by_task_id
    )

    return core, project, tasks
