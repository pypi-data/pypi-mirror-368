"""Notification system for Lackey task management."""

import logging
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from .models import Project, Task, TaskStatus
from .notes import Note

logger = logging.getLogger(__name__)


class NotificationEvent:
    """Represents a notification event."""

    def __init__(
        self,
        event_type: str,
        task: Task,
        project_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ):
        """Initialize a notification event.

        Args:
            event_type: Type of event (e.g., 'status_changed')
            task: Task associated with the event
            project_id: ID of the project containing the task
            metadata: Optional metadata about the event
            timestamp: Optional timestamp (defaults to current time)
        """
        self.event_type = event_type
        self.task = task
        self.project_id = project_id
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.now(UTC)


class NotificationHandler(ABC):
    """Abstract base class for notification handlers."""

    @abstractmethod
    def handle(self, event: NotificationEvent) -> None:
        """Handle a notification event."""
        pass


class LogNotificationHandler(NotificationHandler):
    """Logs notifications to the standard logger."""

    def handle(self, event: NotificationEvent) -> None:
        """Log the notification event."""
        if event.event_type == "status_changed":
            metadata = event.metadata
            old_status = metadata.get("old_status")
            new_status = metadata.get("new_status")
            note = metadata.get("note", "")

            message = (
                f"Task status changed: '{event.task.title}' "
                f"({old_status} → {new_status})"
            )
            if note:
                message += f" - {note}"
            logger.info(message)

            # Log dependent task effects
            dependent_tasks = metadata.get("dependent_tasks", [])
            if dependent_tasks:
                logger.info(
                    f"Status change affects {len(dependent_tasks)} dependent tasks"
                )

        elif event.event_type == "note_added":
            metadata = event.metadata
            note_type = metadata.get("note_type")
            author = metadata.get("author", "unknown")
            content_preview = metadata.get("content_preview", "")

            message = (
                f"Note added to task '{event.task.title}' "
                f"by {author} ({note_type}): {content_preview}"
            )
            logger.info(message)


class NotificationManager:
    """Manages notification handlers and event distribution."""

    def __init__(self) -> None:
        """Initialize the notification manager with default handlers."""
        self.handlers: List[NotificationHandler] = []
        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        """Register default notification handlers."""
        self.handlers.append(LogNotificationHandler())

    def notify_status_change(
        self,
        task: Task,
        project_id: str,
        old_status: TaskStatus,
        new_status: TaskStatus,
        note: Optional[str] = None,
        dependent_tasks: Optional[List[str]] = None,
    ) -> None:
        """
        Send a status change notification.

        Args:
            task: Task that changed status
            project_id: Project ID
            old_status: Previous status
            new_status: New status
            note: Optional note about the change
            dependent_tasks: List of dependent task IDs affected
        """
        event = NotificationEvent(
            event_type="status_changed",
            task=task,
            project_id=project_id,
            metadata={
                "old_status": old_status.value,
                "new_status": new_status.value,
                "note": note,
                "dependent_tasks": dependent_tasks or [],
            },
        )

        for handler in self.handlers:
            try:
                handler.handle(event)
            except Exception as e:
                logger.error(f"Error in notification handler {handler}: {e}")

    def send_task_note_added(
        self,
        project: Project,
        task: Task,
        note: Note,
    ) -> None:
        """
        Send a task note added notification.

        Args:
            project: Project containing the task
            task: Task that received the note
            note: Note that was added
        """
        event = NotificationEvent(
            event_type="note_added",
            task=task,
            project_id=project.id,
            metadata={
                "note_id": note.id,
                "note_type": note.note_type.value,
                "author": note.author,
                "content_preview": (
                    note.content[:100] + "..."
                    if len(note.content) > 100
                    else note.content
                ),
            },
        )

        for handler in self.handlers:
            try:
                handler.handle(event)
            except Exception as e:
                logger.error(f"Error in notification handler {handler}: {e}")
