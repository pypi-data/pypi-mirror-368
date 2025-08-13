"""Test suite for API architecture fix - validates project-scoped operations."""

import pytest

from lackey.core import LackeyCore
from lackey.models import Complexity, Project, Task


class TestAPIArchitectureFix:
    """Test the 4-operation API architecture fix."""

    @pytest.fixture
    def core_with_multiple_projects(self, tmp_path):
        """Create core with multiple projects containing tasks."""
        core = LackeyCore(lackey_dir_path=str(tmp_path))

        # Create Project A with 2 tasks
        project_a = Project.create_new(
            friendly_name="Project A",
            description="First test project",
            objectives=["Test objective A"],
        )
        created_project_a = core.create_project(
            friendly_name=project_a.friendly_name,
            description=project_a.description,
            objectives=project_a.objectives,
        )

        task_a1 = Task.create_new(
            title="Task A1",
            objective="First task in project A",
            steps=["Step 1"],
            success_criteria=["Success 1"],
            complexity=Complexity.LOW,
        )
        task_a2 = Task.create_new(
            title="Task A2",
            objective="Second task in project A",
            steps=["Step 2"],
            success_criteria=["Success 2"],
            complexity=Complexity.MEDIUM,
        )
        created_task_a1 = core.create_task(
            project_id=created_project_a.id,
            title=task_a1.title,
            objective=task_a1.objective,
            steps=task_a1.steps,
            success_criteria=task_a1.success_criteria,
            complexity=task_a1.complexity.value,
        )
        created_task_a2 = core.create_task(
            project_id=created_project_a.id,
            title=task_a2.title,
            objective=task_a2.objective,
            steps=task_a2.steps,
            success_criteria=task_a2.success_criteria,
            complexity=task_a2.complexity.value,
        )

        # Create Project B with 1 task
        project_b = Project.create_new(
            friendly_name="Project B",
            description="Second test project",
            objectives=["Test objective B"],
        )
        created_project_b = core.create_project(
            friendly_name=project_b.friendly_name,
            description=project_b.description,
            objectives=project_b.objectives,
        )

        task_b1 = Task.create_new(
            title="Task B1",
            objective="First task in project B",
            steps=["Step B1"],
            success_criteria=["Success B1"],
            complexity=Complexity.HIGH,
        )
        created_task_b1 = core.create_task(
            project_id=created_project_b.id,
            title=task_b1.title,
            objective=task_b1.objective,
            steps=task_b1.steps,
            success_criteria=task_b1.success_criteria,
            complexity=task_b1.complexity.value,
        )

        return (
            core,
            created_project_a,
            created_project_b,
            [created_task_a1, created_task_a2],
            [created_task_b1],
        )

    def test_get_project_includes_only_own_tasks(self, core_with_multiple_projects):
        """Test get_project returns only tasks from the specified project."""
        core, project_a, project_b, tasks_a, tasks_b = core_with_multiple_projects

        # Get Project A - should only have 2 tasks
        result_a = core.get_project(project_a.id)
        assert len(result_a.tasks) == 2
        task_titles_a = [task.title for task in result_a.tasks]
        assert "Task A1" in task_titles_a
        assert "Task A2" in task_titles_a
        assert "Task B1" not in task_titles_a

        # Get Project B - should only have 1 task
        result_b = core.get_project(project_b.id)
        assert len(result_b.tasks) == 1
        task_titles_b = [task.title for task in result_b.tasks]
        assert "Task B1" in task_titles_b
        assert "Task A1" not in task_titles_b
        assert "Task A2" not in task_titles_b

    def test_get_task_includes_project_id(self, core_with_multiple_projects):
        """Test get_task returns task with correct project_id."""
        core, project_a, project_b, tasks_a, tasks_b = core_with_multiple_projects

        # Get task from Project A
        task_a = core.get_task(tasks_a[0].id)
        assert task_a.project_id == project_a.id
        assert task_a.title == "Task A1"

        # Get task from Project B
        task_b = core.get_task(tasks_b[0].id)
        assert task_b.project_id == project_b.id
        assert task_b.title == "Task B1"

    def test_list_projects_lightweight(self, core_with_multiple_projects):
        """Test list_projects returns lightweight project list."""
        core, project_a, project_b, tasks_a, tasks_b = core_with_multiple_projects

        projects = core.list_projects()
        assert len(projects) == 2

        # Verify structure is lightweight (dict, not Project objects)
        for project in projects:
            assert isinstance(project, dict)
            assert "id" in project
            assert "friendly_name" in project
            assert "status" in project
            # Should not contain task objects
            assert "tasks" not in project

    def test_list_tasks_requires_project_id_and_scoped(
        self, core_with_multiple_projects
    ):
        """Test list_tasks requires project_id and returns only project-scoped tasks."""
        core, project_a, project_b, tasks_a, tasks_b = core_with_multiple_projects

        # List tasks for Project A - should get 2 tasks
        tasks_from_a = core.list_tasks(project_a.id)
        assert len(tasks_from_a) == 2
        task_titles_a = [task.title for task in tasks_from_a]
        assert "Task A1" in task_titles_a
        assert "Task A2" in task_titles_a
        assert "Task B1" not in task_titles_a

        # List tasks for Project B - should get 1 task
        tasks_from_b = core.list_tasks(project_b.id)
        assert len(tasks_from_b) == 1
        task_titles_b = [task.title for task in tasks_from_b]
        assert "Task B1" in task_titles_b
        assert "Task A1" not in task_titles_b
        assert "Task A2" not in task_titles_b

    def test_cross_project_contamination_eliminated(self, core_with_multiple_projects):
        """Test that cross-project task contamination is completely eliminated."""
        core, project_a, project_b, tasks_a, tasks_b = core_with_multiple_projects

        # Verify no operation returns tasks from other projects

        # get_project should be isolated
        proj_a_result = core.get_project(project_a.id)
        proj_b_result = core.get_project(project_b.id)

        proj_a_task_ids = {task.id for task in proj_a_result.tasks}
        proj_b_task_ids = {task.id for task in proj_b_result.tasks}

        # No overlap between projects
        assert len(proj_a_task_ids.intersection(proj_b_task_ids)) == 0

        # list_tasks should be isolated
        list_a_result = core.list_tasks(project_a.id)
        list_b_result = core.list_tasks(project_b.id)

        list_a_task_ids = {task.id for task in list_a_result}
        list_b_task_ids = {task.id for task in list_b_result}

        # No overlap between projects
        assert len(list_a_task_ids.intersection(list_b_task_ids)) == 0

        # Verify each project only sees its own tasks
        expected_a_ids = {task.id for task in tasks_a}
        expected_b_ids = {task.id for task in tasks_b}

        assert proj_a_task_ids == expected_a_ids
        assert proj_b_task_ids == expected_b_ids
        assert list_a_task_ids == expected_a_ids
        assert list_b_task_ids == expected_b_ids
