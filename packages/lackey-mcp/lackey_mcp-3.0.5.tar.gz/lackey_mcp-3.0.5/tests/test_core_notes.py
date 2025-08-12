"""Test suite for core note operations in LackeyCore."""

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from lackey.core import LackeyCore
from lackey.notes import NoteType
from lackey.storage import ProjectNotFoundError, TaskNotFoundError


class TestCoreNoteOperations:
    """Test core note operations through LackeyCore."""

    @pytest.fixture
    def core_with_project_and_task(self, tmp_path: Any) -> tuple:
        """Create a core instance with a project and task for testing."""
        core = LackeyCore(str(tmp_path / ".lackey"))

        # Create project
        project = core.create_project(
            friendly_name="Test Project",
            description="Test project for note operations",
            objectives=["Test note functionality"],
        )

        # Create task
        task = core.create_task(
            project_id=project.id,
            title="Test Task",
            objective="Test task for notes",
            steps=["Step 1", "Step 2"],
            success_criteria=["Task completed successfully"],
            complexity="low",
        )

        return core, project, task

    def test_add_task_note_basic(self, core_with_project_and_task: Any) -> None:
        """Test basic task note addition."""
        core, project, task = core_with_project_and_task

        result = core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="This is a test note",
            author="test_user",
        )

        # Check result structure
        assert "note" in result
        assert "task" in result

        note_data = result["note"]
        assert note_data["content"] == "This is a test note"
        assert note_data["note_type"] == "user"
        assert note_data["author"] == "test_user"
        assert "id" in note_data
        assert "created" in note_data

        task_data = result["task"]
        assert task_data["id"] == task.id
        assert task_data["title"] == task.title
        assert task_data["note_count"] == 1

    def test_add_task_note_with_metadata(self, core_with_project_and_task: Any) -> None:
        """Test adding task note with metadata and tags."""
        core, project, task = core_with_project_and_task

        result = core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="**Important note** with markdown",
            note_type=NoteType.PROGRESS,
            author="developer",
            tags={"important", "progress"},
            metadata={"priority": "high", "version": "1.0"},
        )

        note_data = result["note"]
        assert note_data["note_type"] == "progress"
        assert note_data["author"] == "developer"
        assert set(note_data["tags"]) == {"important", "progress"}
        assert note_data["metadata"]["priority"] == "high"
        assert note_data["metadata"]["version"] == "1.0"

    def test_add_task_note_system_type(self, core_with_project_and_task: Any) -> None:
        """Test adding system-generated notes."""
        core, project, task = core_with_project_and_task

        result = core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="Task status changed automatically",
            note_type=NoteType.STATUS_CHANGE,
            metadata={"from_status": "todo", "to_status": "in_progress"},
        )

        note_data = result["note"]
        assert note_data["note_type"] == "status_change"
        assert note_data["author"] == "system"
        assert note_data["metadata"]["from_status"] == "todo"

    def test_add_task_note_invalid_project(
        self, core_with_project_and_task: Any
    ) -> None:
        """Test adding note to non-existent project."""
        core, project, task = core_with_project_and_task

        with pytest.raises(ProjectNotFoundError):
            core.add_task_note(
                project_id="nonexistent-project",
                task_id=task.id,
                content="This should fail",
            )

    def test_add_task_note_invalid_task(self, core_with_project_and_task: Any) -> None:
        """Test adding note to non-existent task."""
        core, project, task = core_with_project_and_task

        with pytest.raises(TaskNotFoundError):
            core.add_task_note(
                project_id=project.id,
                task_id="nonexistent-task",
                content="This should fail",
            )

    def test_get_task_notes_basic(self, core_with_project_and_task: Any) -> None:
        """Test basic task note retrieval."""
        core, project, task = core_with_project_and_task

        # Add multiple notes
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="First note",
            author="alice",
        )
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="Second note",
            author="bob",
        )

        # Get all notes
        notes = core.get_task_notes(project_id=project.id, task_id=task.id)

        assert len(notes) == 2
        contents = [note["content"] for note in notes]
        assert "First note" in contents
        assert "Second note" in contents

    def test_get_task_notes_with_filters(self, core_with_project_and_task: Any) -> None:
        """Test task note retrieval with filters."""
        core, project, task = core_with_project_and_task

        # Add notes with different types and authors
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="User note 1",
            note_type=NoteType.USER,
            author="alice",
        )
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="User note 2",
            note_type=NoteType.USER,
            author="bob",
        )
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="System note",
            note_type=NoteType.SYSTEM,
        )

        # Test type filtering
        user_notes = core.get_task_notes(
            project_id=project.id, task_id=task.id, note_type=NoteType.USER
        )
        assert len(user_notes) == 2

        system_notes = core.get_task_notes(
            project_id=project.id, task_id=task.id, note_type=NoteType.SYSTEM
        )
        assert len(system_notes) == 1

        # Test author filtering
        alice_notes = core.get_task_notes(
            project_id=project.id, task_id=task.id, author="alice"
        )
        assert len(alice_notes) == 1
        assert alice_notes[0]["content"] == "User note 1"

        # Test limit
        limited_notes = core.get_task_notes(
            project_id=project.id, task_id=task.id, limit=2
        )
        assert len(limited_notes) == 2

    def test_get_task_notes_with_tags(self, core_with_project_and_task: Any) -> None:
        """Test task note retrieval with tag filtering."""
        core, project, task = core_with_project_and_task

        # Add notes with different tags
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="Important note",
            tags={"important", "urgent"},
        )
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="Regular note",
            tags={"regular"},
        )

        # Test tag filtering
        important_notes = core.get_task_notes(
            project_id=project.id, task_id=task.id, tag="important"
        )
        assert len(important_notes) == 1
        assert important_notes[0]["content"] == "Important note"

        urgent_notes = core.get_task_notes(
            project_id=project.id, task_id=task.id, tag="urgent"
        )
        assert len(urgent_notes) == 1

        regular_notes = core.get_task_notes(
            project_id=project.id, task_id=task.id, tag="regular"
        )
        assert len(regular_notes) == 1

    def test_get_task_notes_date_filtering(
        self, core_with_project_and_task: Any
    ) -> None:
        """Test task note retrieval with date filtering."""
        core, project, task = core_with_project_and_task

        now = datetime.now(UTC)
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        # Add a note
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="Recent note",
        )

        # Test since filtering (should include the note)
        recent_notes = core.get_task_notes(
            project_id=project.id, task_id=task.id, since=yesterday
        )
        assert len(recent_notes) == 1

        # Test since filtering (should exclude the note)
        future_notes = core.get_task_notes(
            project_id=project.id, task_id=task.id, since=tomorrow
        )
        assert len(future_notes) == 0

        # Test until filtering (should include the note)
        past_notes = core.get_task_notes(
            project_id=project.id, task_id=task.id, until=tomorrow
        )
        assert len(past_notes) == 1

    def test_search_task_notes_basic(self, core_with_project_and_task: Any) -> None:
        """Test basic task note searching."""
        core, project, task = core_with_project_and_task

        # Add notes with different content
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="This is about bug fixes",
            author="alice",
        )
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="Feature implementation notes",
            author="bob",
        )
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="Another bug report",
            author="alice",
        )

        # Test content search
        bug_notes = core.search_task_notes(
            project_id=project.id, task_id=task.id, query="bug"
        )
        assert len(bug_notes) == 2

        feature_notes = core.search_task_notes(
            project_id=project.id, task_id=task.id, query="feature"
        )
        assert len(feature_notes) == 1

        # Test case insensitive search
        case_notes = core.search_task_notes(
            project_id=project.id, task_id=task.id, query="BUG"
        )
        assert len(case_notes) == 2

    def test_search_task_notes_with_filters(
        self, core_with_project_and_task: Any
    ) -> None:
        """Test task note searching with additional filters."""
        core, project, task = core_with_project_and_task

        # Add notes
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="Bug fix by Alice",
            note_type=NoteType.USER,
            author="alice",
        )
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="Bug fix by Bob",
            note_type=NoteType.USER,
            author="bob",
        )
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="System bug detection",
            note_type=NoteType.SYSTEM,
        )

        # Test search with author filter
        alice_bug_notes = core.search_task_notes(
            project_id=project.id, task_id=task.id, query="bug", author="alice"
        )
        assert len(alice_bug_notes) == 1
        assert alice_bug_notes[0]["content"] == "Bug fix by Alice"

        # Test search with type filter
        system_bug_notes = core.search_task_notes(
            project_id=project.id,
            task_id=task.id,
            query="bug",
            note_type=NoteType.SYSTEM,
        )
        assert len(system_bug_notes) == 1
        assert system_bug_notes[0]["content"] == "System bug detection"

        # Test search with limit
        limited_notes = core.search_task_notes(
            project_id=project.id, task_id=task.id, query="bug", limit=2
        )
        assert len(limited_notes) == 2

    def test_search_task_notes_empty_results(
        self, core_with_project_and_task: Any
    ) -> None:
        """Test task note searching with no matches."""
        core, project, task = core_with_project_and_task

        # Add a note
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="This is a test note",
        )

        # Search for non-existent content
        results = core.search_task_notes(
            project_id=project.id, task_id=task.id, query="nonexistent"
        )
        assert len(results) == 0

    def test_search_task_notes_markdown_content(
        self, core_with_project_and_task: Any
    ) -> None:
        """Test searching notes with markdown content."""
        core, project, task = core_with_project_and_task

        # Add note with markdown
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="This is **important** and contains `code` snippets",
        )

        # Should find both markdown and plain text
        bold_notes = core.search_task_notes(
            project_id=project.id, task_id=task.id, query="important"
        )
        assert len(bold_notes) == 1

        code_notes = core.search_task_notes(
            project_id=project.id, task_id=task.id, query="code"
        )
        assert len(code_notes) == 1

    def test_note_operations_with_project_name(
        self, core_with_project_and_task: Any
    ) -> None:
        """Test note operations using project name instead of ID."""
        core, project, task = core_with_project_and_task

        # Use project name instead of ID
        result = core.add_task_note(
            project_id=project.name,  # Use name instead of ID
            task_id=task.id,
            content="Note added using project name",
        )

        assert result["note"]["content"] == "Note added using project name"

        # Test retrieval with project name
        notes = core.get_task_notes(project_id=project.name, task_id=task.id)
        assert len(notes) == 1

        # Test search with project name
        search_results = core.search_task_notes(
            project_id=project.name, task_id=task.id, query="project name"
        )
        assert len(search_results) == 1

    def test_multiple_notes_chronological_order(
        self, core_with_project_and_task: Any
    ) -> None:
        """Test that notes are returned in chronological order (newest first)."""
        core, project, task = core_with_project_and_task
        import time

        # Add notes in sequence with small delays to ensure different timestamps
        core.add_task_note(project_id=project.id, task_id=task.id, content="First note")
        time.sleep(0.01)  # Small delay to ensure different timestamps
        core.add_task_note(
            project_id=project.id, task_id=task.id, content="Second note"
        )
        time.sleep(0.01)
        core.add_task_note(project_id=project.id, task_id=task.id, content="Third note")

        notes = core.get_task_notes(project_id=project.id, task_id=task.id)

        # Should be in reverse chronological order (newest first)
        assert notes[0]["content"] == "Third note"
        assert notes[1]["content"] == "Second note"
        assert notes[2]["content"] == "First note"

    def test_note_persistence(self, core_with_project_and_task: Any) -> None:
        """Test that notes persist across core instance reloads."""
        core, project, task = core_with_project_and_task

        # Add a note
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="Persistent note",
            author="test_user",
            tags={"persistent"},
        )

        # Create new core instance (simulating restart)
        new_core = LackeyCore(str(core.storage.lackey_dir))

        # Retrieve notes with new instance
        notes = new_core.get_task_notes(project_id=project.id, task_id=task.id)

        assert len(notes) == 1
        assert notes[0]["content"] == "Persistent note"
        assert notes[0]["author"] == "test_user"
        assert "persistent" in notes[0]["tags"]

    def test_note_operations_error_handling(
        self, core_with_project_and_task: Any
    ) -> None:
        """Test error handling in note operations."""
        core, project, task = core_with_project_and_task

        # Test with invalid task ID (project_id is ignored since task IDs are
        # universally unique)
        with pytest.raises(TaskNotFoundError):
            core.get_task_notes(project_id=project.id, task_id="invalid-task")

        with pytest.raises(TaskNotFoundError):
            core.search_task_notes(
                project_id=project.id, task_id="invalid-task", query="test"
            )

        with pytest.raises(TaskNotFoundError):
            core.search_task_notes(
                project_id=project.id, task_id="invalid-task", query="test"
            )

    def test_note_integration_with_task_updates(
        self, core_with_project_and_task: Any
    ) -> None:
        """Test that notes are preserved during task updates."""
        core, project, task = core_with_project_and_task

        # Add notes
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="Note before update",
        )

        # Update task
        core.update_task(
            project_id=project.id,
            task_id=task.id,
            title="Updated Task Title",
        )

        # Check that notes are preserved
        notes = core.get_task_notes(project_id=project.id, task_id=task.id)
        assert len(notes) == 1
        assert notes[0]["content"] == "Note before update"

        # Add another note after update
        core.add_task_note(
            project_id=project.id,
            task_id=task.id,
            content="Note after update",
        )

        notes = core.get_task_notes(project_id=project.id, task_id=task.id)
        assert len(notes) == 2
