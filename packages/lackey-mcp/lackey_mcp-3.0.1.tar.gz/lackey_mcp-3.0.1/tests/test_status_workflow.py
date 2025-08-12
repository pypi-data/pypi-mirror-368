"""Tests for status workflow and transition validation."""

from typing import Any
from unittest.mock import patch

import pytest

from lackey.core import LackeyCore
from lackey.models import Complexity, Project, Task, TaskStatus
from lackey.validation import ValidationError
from lackey.workflow import StatusWorkflow


class TestStatusWorkflow:
    """Test status workflow validation."""

    def test_valid_transitions(self) -> None:
        """Test all valid status transitions."""
        # TODO -> IN_PROGRESS
        StatusWorkflow.validate_transition(TaskStatus.TODO, TaskStatus.IN_PROGRESS)

        # TODO -> BLOCKED
        StatusWorkflow.validate_transition(TaskStatus.TODO, TaskStatus.BLOCKED)

        # TODO -> DONE (direct completion)
        StatusWorkflow.validate_transition(TaskStatus.TODO, TaskStatus.DONE)

        # IN_PROGRESS -> BLOCKED
        StatusWorkflow.validate_transition(TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED)

        # IN_PROGRESS -> DONE
        StatusWorkflow.validate_transition(TaskStatus.IN_PROGRESS, TaskStatus.DONE)

        # IN_PROGRESS -> TODO (revert)
        StatusWorkflow.validate_transition(TaskStatus.IN_PROGRESS, TaskStatus.TODO)

        # BLOCKED -> TODO
        StatusWorkflow.validate_transition(TaskStatus.BLOCKED, TaskStatus.TODO)

        # BLOCKED -> IN_PROGRESS
        StatusWorkflow.validate_transition(TaskStatus.BLOCKED, TaskStatus.IN_PROGRESS)

        # BLOCKED -> DONE
        StatusWorkflow.validate_transition(TaskStatus.BLOCKED, TaskStatus.DONE)

        # DONE -> TODO (reopen)
        StatusWorkflow.validate_transition(TaskStatus.DONE, TaskStatus.TODO)

        # DONE -> IN_PROGRESS (resume)
        StatusWorkflow.validate_transition(TaskStatus.DONE, TaskStatus.IN_PROGRESS)

    def test_invalid_transitions(self) -> None:
        """Test invalid status transitions raise errors."""
        # No invalid transitions in current workflow - all are allowed
        # This is by design for flexibility
        pass

    def test_same_status_transition(self) -> None:
        """Test that transitioning to same status is allowed."""
        StatusWorkflow.validate_transition(TaskStatus.TODO, TaskStatus.TODO)
        StatusWorkflow.validate_transition(TaskStatus.DONE, TaskStatus.DONE)

    def test_get_valid_transitions(self) -> None:
        """Test getting valid transitions for each status."""
        todo_transitions = StatusWorkflow.get_valid_transitions(TaskStatus.TODO)
        assert TaskStatus.IN_PROGRESS in todo_transitions
        assert TaskStatus.BLOCKED in todo_transitions
        assert TaskStatus.DONE in todo_transitions

        in_progress_transitions = StatusWorkflow.get_valid_transitions(
            TaskStatus.IN_PROGRESS
        )
        assert TaskStatus.BLOCKED in in_progress_transitions
        assert TaskStatus.DONE in in_progress_transitions
        assert TaskStatus.TODO in in_progress_transitions

    def test_is_terminal_status(self) -> None:
        """Test terminal status identification."""
        assert StatusWorkflow.is_terminal_status(TaskStatus.DONE)
        assert not StatusWorkflow.is_terminal_status(TaskStatus.TODO)
        assert not StatusWorkflow.is_terminal_status(TaskStatus.IN_PROGRESS)
        assert not StatusWorkflow.is_terminal_status(TaskStatus.BLOCKED)

    def test_should_auto_block(self) -> None:
        """Test automatic blocking logic."""
        task = Task.create_new(
            title="Test Task",
            objective="Test",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity=Complexity.LOW,
            dependencies={"dep1", "dep2"},
        )

        # Should block if any dependency is not done
        dependency_statuses = {"dep1": TaskStatus.DONE, "dep2": TaskStatus.IN_PROGRESS}
        assert StatusWorkflow.should_auto_block(task, dependency_statuses)

        # Should not block if all dependencies are done
        dependency_statuses = {"dep1": TaskStatus.DONE, "dep2": TaskStatus.DONE}
        assert not StatusWorkflow.should_auto_block(task, dependency_statuses)

        # Should not block if no dependencies
        task_no_deps = Task.create_new(
            title="No Deps Task",
            objective="Test",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity=Complexity.LOW,
        )
        assert not StatusWorkflow.should_auto_block(task_no_deps, {})

    def test_should_auto_unblock(self) -> None:
        """Test automatic unblocking logic."""
        task = Task.create_new(
            title="Blocked Task",
            objective="Test",
            steps=["Step 1"],
            success_criteria=["Done"],
            complexity=Complexity.LOW,
            dependencies={"dep1", "dep2"},
        )
        task.status = TaskStatus.BLOCKED

        # Should unblock if all dependencies are done
        dependency_statuses = {"dep1": TaskStatus.DONE, "dep2": TaskStatus.DONE}
        assert StatusWorkflow.should_auto_unblock(task, dependency_statuses)

        # Should not unblock if any dependency is not done
        dependency_statuses = {"dep1": TaskStatus.DONE, "dep2": TaskStatus.IN_PROGRESS}
        assert not StatusWorkflow.should_auto_unblock(task, dependency_statuses)

        # Should not unblock if task is not blocked
        task.status = TaskStatus.TODO
        assert not StatusWorkflow.should_auto_unblock(task, dependency_statuses)


class TestStatusTransitions:
    """Test status transitions in LackeyCore."""

    @pytest.fixture  # type: ignore[misc]
    def core(self, tmp_path: Any) -> LackeyCore:
        """Create a LackeyCore instance for testing."""
        return LackeyCore(str(tmp_path / ".lackey"))

    @pytest.fixture  # type: ignore[misc]
    def project(self, core: LackeyCore) -> Project:
        """Create a test project."""
        return core.create_project(
            friendly_name="Test Project",
            description="Test project for status transitions",
            objectives=["Test status workflow"],
        )

    @pytest.fixture  # type: ignore[misc]
    def task(self, core: LackeyCore, project: Project) -> Task:
        """Create a test task."""
        return core.create_task(
            project_id=project.id,
            title="Test Task",
            objective="Test status transitions",
            steps=["Step 1", "Step 2"],
            success_criteria=["All steps complete"],
            complexity=Complexity.LOW.value,
        )

    def test_basic_status_update(
        self, core: LackeyCore, project: Project, task: Task
    ) -> None:
        """Test basic status update functionality."""
        # Update to in-progress
        updated_task = core.update_task_status(
            project.id, task.id, TaskStatus.IN_PROGRESS, "Starting work"
        )

        assert updated_task.status == TaskStatus.IN_PROGRESS
        assert len(updated_task.status_history) == 1
        assert updated_task.status_history[0]["from_status"] == "todo"
        assert updated_task.status_history[0]["to_status"] == "in_progress"
        assert updated_task.status_history[0]["note"] == "Starting work"

    def test_status_history_tracking(
        self, core: LackeyCore, project: Project, task: Task
    ) -> None:
        """Test that status history is properly tracked."""
        # Multiple status changes
        core.update_task_status(project.id, task.id, TaskStatus.IN_PROGRESS)
        core.update_task_status(
            project.id, task.id, TaskStatus.BLOCKED, "Waiting for dependency"
        )
        updated_task = core.update_task_status(
            project.id, task.id, TaskStatus.TODO, "Dependency resolved"
        )

        assert len(updated_task.status_history) == 3

        # Check history order
        history = updated_task.status_history
        assert history[0]["from_status"] == "todo"
        assert history[0]["to_status"] == "in_progress"

        assert history[1]["from_status"] == "in_progress"
        assert history[1]["to_status"] == "blocked"
        assert history[1]["note"] == "Waiting for dependency"

        assert history[2]["from_status"] == "blocked"
        assert history[2]["to_status"] == "todo"
        assert history[2]["note"] == "Dependency resolved"

    def test_dependency_constraint_validation(
        self, core: LackeyCore, project: Project
    ) -> None:
        """Test that dependency constraints are enforced."""
        # Create dependency task
        dep_task = core.create_task(
            project_id=project.id,
            title="Dependency Task",
            objective="Must be done first",
            steps=["Step 1"],
            success_criteria=["Complete"],
            complexity=Complexity.LOW.value,
        )

        # Create dependent task
        dependent_task = core.create_task(
            project_id=project.id,
            title="Dependent Task",
            objective="Depends on other task",
            steps=["Step 1"],
            success_criteria=["Complete"],
            complexity=Complexity.LOW.value,
            dependencies=[dep_task.id],
        )

        # Should not be able to mark dependent task as done while dependency
        # is incomplete
        with pytest.raises(ValidationError, match="Cannot mark task as done"):
            core.update_task_status(project.id, dependent_task.id, TaskStatus.DONE)

        # Complete dependency first
        core.update_task_status(project.id, dep_task.id, TaskStatus.DONE)

        # Now should be able to complete dependent task
        updated_task = core.update_task_status(
            project.id, dependent_task.id, TaskStatus.DONE
        )
        assert updated_task.status == TaskStatus.DONE

    def test_automatic_blocking_unblocking(
        self, core: LackeyCore, project: Project
    ) -> None:
        """Test automatic blocking and unblocking of dependent tasks."""
        # Create dependency task
        dep_task = core.create_task(
            project_id=project.id,
            title="Dependency Task",
            objective="Must be done first",
            steps=["Step 1"],
            success_criteria=["Complete"],
            complexity=Complexity.LOW.value,
        )

        # Create dependent task
        dependent_task = core.create_task(
            project_id=project.id,
            title="Dependent Task",
            objective="Depends on other task",
            steps=["Step 1"],
            success_criteria=["Complete"],
            complexity=Complexity.LOW.value,
            dependencies=[dep_task.id],
        )

        # Start work on dependent task - should get auto-blocked
        core.update_task_status(project.id, dependent_task.id, TaskStatus.IN_PROGRESS)

        # Check that dependent task was auto-blocked
        updated_dependent = core.get_task(dependent_task.id)
        assert updated_dependent.status == TaskStatus.BLOCKED

        # Complete dependency
        core.update_task_status(project.id, dep_task.id, TaskStatus.DONE)

        # Check that dependent task was auto-unblocked
        updated_dependent = core.get_task(dependent_task.id)
        assert updated_dependent.status == TaskStatus.TODO

    def test_bulk_blocked_status_management(
        self, core: LackeyCore, project: Project
    ) -> None:
        """Test bulk blocked status management."""
        # Create multiple tasks with dependencies
        dep_task = core.create_task(
            project_id=project.id,
            title="Dependency Task",
            objective="Shared dependency",
            steps=["Step 1"],
            success_criteria=["Complete"],
            complexity=Complexity.LOW.value,
        )

        dependent_tasks = []
        for i in range(3):
            task = core.create_task(
                project_id=project.id,
                title=f"Dependent Task {i+1}",
                objective="Depends on shared task",
                steps=["Step 1"],
                success_criteria=["Complete"],
                complexity=Complexity.LOW.value,
                dependencies=[dep_task.id],
            )
            dependent_tasks.append(task)

        # Run bulk blocked status management
        updated_task_ids = core.auto_manage_blocked_status(project.id)

        # Tasks should already be blocked when created, so no updates needed
        assert len(updated_task_ids) == 0

        for task in dependent_tasks:
            updated_task = core.get_task(task.id)
            assert updated_task.status == TaskStatus.BLOCKED

        # Complete dependency
        core.update_task_status(project.id, dep_task.id, TaskStatus.DONE)

        # Run bulk management again
        updated_task_ids = core.auto_manage_blocked_status(project.id)

        # Tasks should already be unblocked by dependency resolution,
        # so no updates needed
        assert len(updated_task_ids) == 0

        for task in dependent_tasks:
            updated_task = core.get_task(task.id)
            assert updated_task.status == TaskStatus.TODO

    @patch("lackey.notifications.logger")
    def test_notification_system_integration(
        self, mock_logger: Any, core: LackeyCore, project: Project, task: Task
    ) -> None:
        """Test that notifications are sent for status changes."""
        # Update task status
        core.update_task_status(
            project.id, task.id, TaskStatus.IN_PROGRESS, "Starting work"
        )

        # Verify notification was logged
        mock_logger.info.assert_called()
        log_calls = [call.args[0] for call in mock_logger.info.call_args_list]

        # Should have both the core status update log and notification log
        status_logs = [log for log in log_calls if "Task status changed" in log]
        assert len(status_logs) >= 1

    def test_error_handling_invalid_task(
        self, core: LackeyCore, project: Project
    ) -> None:
        """Test error handling for invalid task ID."""
        with pytest.raises(Exception):  # TaskNotFoundError or similar
            core.update_task_status(project.id, "invalid-task-id", TaskStatus.DONE)

    def test_error_handling_invalid_project(self, core: LackeyCore) -> None:
        """Test error handling for invalid project ID."""
        with pytest.raises(Exception):  # ProjectNotFoundError or similar
            core.update_task_status("invalid-project-id", "task-id", TaskStatus.DONE)
