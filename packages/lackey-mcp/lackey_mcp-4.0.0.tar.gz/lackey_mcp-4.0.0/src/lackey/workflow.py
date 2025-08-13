"""Task status workflow management for Lackey."""

import logging
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from .models import Task, TaskStatus

logger = logging.getLogger(__name__)


class StatusTransitionError(Exception):
    """Raised when an invalid status transition is attempted."""

    def __init__(self, current: TaskStatus, target: TaskStatus, reason: str):
        """Initialize a status transition error.

        Args:
            current: Current task status
            target: Target task status
            reason: Reason why the transition is invalid
        """
        self.current = current
        self.target = target
        self.reason = reason

        # Handle both enum and string values
        current_val = current.value if hasattr(current, "value") else str(current)
        target_val = target.value if hasattr(target, "value") else str(target)

        super().__init__(
            f"Invalid transition from {current_val} to {target_val}: {reason}"
        )


class StatusWorkflow:
    """
    Manages task status transitions and workflow validation.

    Defines valid status transitions and enforces workflow rules
    to maintain task chain integrity.
    """

    # Define valid status transitions
    VALID_TRANSITIONS: Dict[TaskStatus, Set[TaskStatus]] = {
        TaskStatus.TODO: {
            TaskStatus.IN_PROGRESS,
            TaskStatus.BLOCKED,
            TaskStatus.DONE,  # Allow direct completion for simple tasks
        },
        TaskStatus.IN_PROGRESS: {
            TaskStatus.BLOCKED,
            TaskStatus.DONE,
            TaskStatus.TODO,  # Allow reverting to todo if needed
        },
        TaskStatus.BLOCKED: {
            TaskStatus.TODO,
            TaskStatus.IN_PROGRESS,
            TaskStatus.DONE,  # Allow completion if blocking resolved
        },
        TaskStatus.DONE: {
            TaskStatus.TODO,  # Allow reopening completed tasks
            TaskStatus.IN_PROGRESS,  # Allow resuming if issues found
        },
    }

    @classmethod
    def validate_transition(
        cls, current: TaskStatus, target: TaskStatus, task: Optional[Task] = None
    ) -> None:
        """
        Validate if a status transition is allowed.

        Args:
            current: Current task status
            target: Target task status
            task: Optional task object for additional validation

        Raises:
            StatusTransitionError: If transition is invalid
        """
        if current == target:
            return  # No transition needed

        valid_targets = cls.VALID_TRANSITIONS.get(current, set())
        if target not in valid_targets:
            raise StatusTransitionError(
                current,
                target,
                "Transition not allowed by workflow rules",
            )

        # Additional validation based on task state
        if task:
            cls._validate_task_constraints(current, target, task)

    @classmethod
    def _validate_task_constraints(
        cls, current: TaskStatus, target: TaskStatus, task: Task
    ) -> None:
        """
        Validate task-specific constraints for status transitions.

        Args:
            current: Current status
            target: Target status
            task: Task being transitioned

        Raises:
            StatusTransitionError: If task constraints prevent transition
        """
        # Cannot mark as done if dependencies are not complete
        if target == TaskStatus.DONE and task.dependencies:
            # This would require checking dependency status
            # For now, we'll implement this in the core service
            pass

        # Cannot start work if blocked by dependencies
        if target == TaskStatus.IN_PROGRESS and current == TaskStatus.BLOCKED:
            # Additional validation could be added here
            pass

    @classmethod
    def get_valid_transitions(self, current: TaskStatus) -> Set[TaskStatus]:
        """
        Get all valid transitions from the current status.

        Args:
            current: Current task status

        Returns:
            Set of valid target statuses
        """
        return self.VALID_TRANSITIONS.get(current, set()).copy()

    @classmethod
    def is_terminal_status(self, status: TaskStatus) -> bool:
        """
        Check if a status is terminal (typically done).

        Args:
            status: Status to check

        Returns:
            True if status is terminal
        """
        return status == TaskStatus.DONE

    @classmethod
    def should_auto_block(
        cls, task: Task, dependency_statuses: Dict[str, TaskStatus]
    ) -> bool:
        """
        Determine if a task should be automatically blocked based on dependencies.

        Args:
            task: Task to check
            dependency_statuses: Map of dependency IDs to their statuses

        Returns:
            True if task should be blocked
        """
        if not task.dependencies:
            return False

        # Block if any dependency is not done
        for dep_id in task.dependencies:
            dep_status = dependency_statuses.get(dep_id)
            if dep_status != TaskStatus.DONE:
                return True

        return False

    @classmethod
    def should_auto_unblock(
        cls, task: Task, dependency_statuses: Dict[str, TaskStatus]
    ) -> bool:
        """
        Determine if a blocked task should be automatically unblocked.

        Args:
            task: Task to check
            dependency_statuses: Map of dependency IDs to their statuses

        Returns:
            True if task should be unblocked
        """
        if task.status != TaskStatus.BLOCKED:
            return False

        if not task.dependencies:
            return True  # No dependencies, should not be blocked

        # Unblock if all dependencies are done
        for dep_id in task.dependencies:
            dep_status = dependency_statuses.get(dep_id)
            if dep_status != TaskStatus.DONE:
                return False

        return True


class StatusHistory:
    """Tracks status change history for audit purposes."""

    def __init__(self) -> None:
        """Initialize an empty status history."""
        self.changes: List[Tuple[datetime, TaskStatus, TaskStatus, Optional[str]]] = []

    def add_change(
        self,
        from_status: TaskStatus,
        to_status: TaskStatus,
        note: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """
        Record a status change.

        Args:
            from_status: Previous status
            to_status: New status
            note: Optional note about the change
            timestamp: Optional timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now(UTC)

        self.changes.append((timestamp, from_status, to_status, note))

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get status change history.

        Returns:
            List of status change records
        """
        return [
            {
                "timestamp": timestamp.isoformat(),
                "from_status": from_status.value,
                "to_status": to_status.value,
                "note": note,
            }
            for timestamp, from_status, to_status, note in self.changes
        ]

    def get_latest_change(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent status change.

        Returns:
            Latest status change record or None
        """
        if not self.changes:
            return None

        timestamp, from_status, to_status, note = self.changes[-1]
        return {
            "timestamp": timestamp.isoformat(),
            "from_status": from_status.value,
            "to_status": to_status.value,
            "note": note,
        }
