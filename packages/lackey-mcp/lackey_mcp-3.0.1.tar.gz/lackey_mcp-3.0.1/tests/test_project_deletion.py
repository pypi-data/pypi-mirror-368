"""Tests for project deletion operations."""

from unittest.mock import Mock, patch

import pytest

from lackey.core import LackeyCore
from lackey.models import Complexity, Project, Task


class TestProjectDeletion:
    """Test project deletion operations."""

    def test_delete_empty_project(self) -> None:
        """Test deleting a project with no tasks."""
        mock_storage = Mock()
        project = Project.create_new(
            friendly_name="Empty Project",
            description="Project with no tasks",
            objectives=["Test objective"],
        )

        mock_storage.get_project.return_value = project
        mock_storage.list_project_tasks.return_value = []
        mock_storage.delete_project.return_value = None

        with patch("lackey.core.LackeyStorage") as mock_storage_class:
            mock_storage_class.return_value = mock_storage
            core = LackeyCore()

            core.delete_project(project.id)

            mock_storage.get_project.assert_called_once_with(project.id)
            mock_storage.list_project_tasks.assert_called_once_with(project.id)
            mock_storage.delete_project.assert_called_once_with(project.id)

    def test_delete_project_with_tasks_fails(self) -> None:
        """Test that deleting a project with tasks raises an error."""
        mock_storage = Mock()
        project = Project.create_new(
            friendly_name="Project With Tasks",
            description="Project containing tasks",
            objectives=["Test objective"],
        )

        tasks = [
            Task.create_new(
                title="Task 1",
                objective="Do something",
                steps=["Step 1"],
                success_criteria=["Success"],
                complexity=Complexity.LOW,
            ),
            Task.create_new(
                title="Task 2",
                objective="Do something else",
                steps=["Step 1"],
                success_criteria=["Success"],
                complexity=Complexity.MEDIUM,
            ),
        ]

        mock_storage.get_project.return_value = project
        mock_storage.list_project_tasks.return_value = tasks

        with patch("lackey.core.LackeyStorage") as mock_storage_class:
            mock_storage_class.return_value = mock_storage
            core = LackeyCore()

            with pytest.raises(
                ValueError, match="Cannot delete project.*contains 2 task"
            ):
                core.delete_project(project.id)

            mock_storage.get_project.assert_called_once_with(project.id)
            mock_storage.list_project_tasks.assert_called_once_with(project.id)
            mock_storage.delete_project.assert_not_called()
