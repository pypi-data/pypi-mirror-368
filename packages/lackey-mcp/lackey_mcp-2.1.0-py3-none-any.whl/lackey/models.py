"""Core data models for Lackey task management system."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .notes import Note, NoteManager, NoteType


class TaskStatus(Enum):
    """Task status enumeration."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


class Complexity(Enum):
    """Task complexity enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ProjectStatus(Enum):
    """Project status enumeration."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Task:
    """
    Core task model representing a single unit of work.

    Tasks are stored as markdown files with YAML frontmatter and support
    rich documentation, dependency tracking, and progress monitoring.
    """

    id: str
    title: str
    objective: str
    steps: List[str]
    success_criteria: List[str]
    status: TaskStatus
    complexity: Complexity
    created: datetime
    updated: datetime
    context: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    blocks: Set[str] = field(default_factory=set)
    completed_steps: List[int] = field(default_factory=list)
    note_manager: NoteManager = field(default_factory=NoteManager)
    results: Optional[str] = None
    status_history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate task data after initialization."""
        if not self.id:
            self.id = str(uuid.uuid4())

    @classmethod
    def create_new(
        cls,
        title: str,
        objective: str,
        steps: List[str],
        success_criteria: List[str],
        complexity: Complexity,
        context: Optional[str] = None,
        assigned_to: Optional[str] = None,
        tags: Optional[List[str]] = None,
        dependencies: Optional[Set[str]] = None,
    ) -> Task:
        """Create a new task with generated ID and timestamps."""
        now = datetime.now(UTC)

        return cls(
            id=str(uuid.uuid4()),
            title=title,
            objective=objective,
            steps=steps,
            success_criteria=success_criteria,
            status=TaskStatus.TODO,
            complexity=complexity,
            created=now,
            updated=now,
            context=context,
            assigned_to=assigned_to,
            tags=tags or [],
            dependencies=dependencies or set(),
        )

    def update_status(self, new_status: TaskStatus, note: Optional[str] = None) -> None:
        """Update task status and timestamp with history tracking."""
        old_status = self.status
        self.status = new_status
        self.updated = datetime.now(UTC)

        # Track status change in history
        if old_status != new_status:
            self.status_history.append(
                {
                    "timestamp": self.updated.isoformat(),
                    "from_status": old_status.value,
                    "to_status": new_status.value,
                    "note": note,
                }
            )

    def add_dependency(self, task_id: str) -> None:
        """Add a dependency to this task."""
        self.dependencies.add(task_id)
        self.updated = datetime.now(UTC)

    def remove_dependency(self, task_id: str) -> None:
        """Remove a dependency from this task."""
        self.dependencies.discard(task_id)
        self.updated = datetime.now(UTC)

    def add_note(
        self,
        content: str,
        note_type: NoteType = NoteType.USER,
        author: Optional[str] = None,
        tags: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Note:
        """Add a rich note to the task."""
        note = self.note_manager.add_note(
            content=content,
            note_type=note_type,
            author=author,
            tags=tags,
            metadata=metadata,
        )
        self.updated = datetime.now(UTC)
        return note

    def add_simple_note(self, note: str) -> Note:
        """Add a simple text note (for backward compatibility)."""
        return self.add_note(note, NoteType.USER)

    def complete_step(self, step_index: int) -> None:
        """Mark a step as completed."""
        if 0 <= step_index < len(self.steps):
            if step_index not in self.completed_steps:
                self.completed_steps.append(step_index)
                self.completed_steps.sort()
                self.updated = datetime.now(UTC)

    def uncomplete_step(self, step_index: int) -> None:
        """Mark a step as incomplete."""
        if step_index in self.completed_steps:
            self.completed_steps.remove(step_index)
            self.updated = datetime.now(UTC)

    def is_ready(self, completed_tasks: Set[str]) -> bool:
        """Check if task is ready to start (all dependencies completed)."""
        return self.status == TaskStatus.TODO and self.dependencies.issubset(
            completed_tasks
        )

    def is_blocked(self, completed_tasks: Set[str]) -> bool:
        """Check if task is blocked by incomplete dependencies."""
        return self.status in (
            TaskStatus.TODO,
            TaskStatus.IN_PROGRESS,
            TaskStatus.BLOCKED,
        ) and not self.dependencies.issubset(completed_tasks)

    def progress_percentage(self) -> float:
        """Calculate completion percentage based on completed steps."""
        if not self.steps:
            return 100.0 if self.status == TaskStatus.DONE else 0.0

        return (len(self.completed_steps) / len(self.steps)) * 100.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "objective": self.objective,
            "steps": self.steps,
            "success_criteria": self.success_criteria,
            "status": self.status.value,
            "complexity": self.complexity.value,
            "created": self.created.isoformat(),
            "updated": self.updated.isoformat(),
            "context": self.context,
            "assigned_to": self.assigned_to,
            "tags": self.tags,
            "dependencies": list(self.dependencies),
            "blocks": list(self.blocks),
            "completed_steps": self.completed_steps,
            "note_manager": self.note_manager.to_dict_list(),
            "results": self.results,
            "status_history": self.status_history,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Task:
        """Create task from dictionary."""
        # Handle notes using note manager system
        notes_data = data.get(
            "note_manager", data.get("notes", [])
        )  # Support both for backward compatibility
        note_manager = NoteManager.from_dict_list(notes_data)

        return cls(
            id=data["id"],
            title=data["title"],
            objective=data["objective"],
            steps=data["steps"],
            success_criteria=data["success_criteria"],
            status=TaskStatus(data["status"]),
            complexity=Complexity(data["complexity"]),
            created=datetime.fromisoformat(data["created"]),
            updated=datetime.fromisoformat(data["updated"]),
            context=data.get("context"),
            assigned_to=data.get("assigned_to"),
            tags=data.get("tags", []),
            dependencies=set(data.get("dependencies", [])),
            blocks=set(data.get("blocks", [])),
            completed_steps=data.get("completed_steps", []),
            note_manager=note_manager,
            results=data.get("results"),
            status_history=data.get("status_history", []),
        )


@dataclass
class Project:
    """
    Core project model representing a collection of related tasks.

    Projects provide organizational structure and context for task chains,
    including objectives, metadata, and agent configurations.
    """

    id: str
    name: str  # URL-safe name
    friendly_name: str
    description: str
    status: ProjectStatus
    created: datetime
    objectives: List[str]
    tags: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate project data after initialization."""
        if not self.id:
            self.id = str(uuid.uuid4())

    @classmethod
    def create_new(
        cls,
        friendly_name: str,
        description: str,
        objectives: List[str],
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Project:
        """Create a new project with generated ID and timestamps."""
        # Generate URL-safe name from friendly name
        name = friendly_name.lower().replace(" ", "-").replace("_", "-")
        # Remove non-alphanumeric characters except hyphens
        name = "".join(c for c in name if c.isalnum() or c == "-")
        # Remove consecutive hyphens
        while "--" in name:
            name = name.replace("--", "-")
        name = name.strip("-")

        return cls(
            id=str(uuid.uuid4()),
            name=name,
            friendly_name=friendly_name,
            description=description,
            status=ProjectStatus.ACTIVE,
            created=datetime.now(UTC),
            objectives=objectives,
            tags=tags or [],
            metadata=metadata or {},
        )

    def update_status(self, new_status: ProjectStatus) -> None:
        """Update project status."""
        self.status = new_status
        self.metadata["last_modified"] = datetime.now(UTC).isoformat()

    def add_objective(self, objective: str) -> None:
        """Add an objective to the project."""
        if objective not in self.objectives:
            self.objectives.append(objective)
            self.metadata["last_modified"] = datetime.now(UTC).isoformat()

    def remove_objective(self, objective: str) -> None:
        """Remove an objective from the project."""
        if objective in self.objectives:
            self.objectives.remove(objective)
            self.metadata["last_modified"] = datetime.now(UTC).isoformat()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the project."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.metadata["last_modified"] = datetime.now(UTC).isoformat()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the project."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.metadata["last_modified"] = datetime.now(UTC).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "friendly_name": self.friendly_name,
            "description": self.description,
            "status": self.status.value,
            "created": self.created.isoformat(),
            "objectives": self.objectives,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Project:
        """Create project from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            friendly_name=data["friendly_name"],
            description=data["description"],
            status=ProjectStatus(data["status"]),
            created=datetime.fromisoformat(data["created"]),
            objectives=data["objectives"],
            tags=data["tags"],
            metadata=data.get("metadata", {}),
        )


@dataclass
class ProjectIndex:
    """
    Index of all projects in the repository.

    Provides quick lookup and summary statistics for project management.
    """

    version: str = "1.0"
    projects: List[Dict[str, Any]] = field(default_factory=list)

    def add_project(
        self, project: Project, task_count: int = 0, completed_count: int = 0
    ) -> None:
        """Add a project to the index."""
        project_entry = {
            "id": project.id,
            "name": project.name,
            "friendly_name": project.friendly_name,
            "created": project.created.isoformat(),
            "status": project.status.value,
            "task_count": task_count,
            "completed_count": completed_count,
        }

        # Remove existing entry if present
        self.projects = [p for p in self.projects if p["id"] != project.id]
        self.projects.append(project_entry)

    def remove_project(self, project_id: str) -> None:
        """Remove a project from the index."""
        self.projects = [p for p in self.projects if p["id"] != project_id]

    def get_project_entry(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project entry by ID."""
        for project in self.projects:
            if project["id"] == project_id:
                return project
        return None

    def update_task_counts(
        self, project_id: str, task_count: int, completed_count: int
    ) -> None:
        """Update task counts for a project."""
        for project in self.projects:
            if project["id"] == project_id:
                project["task_count"] = task_count
                project["completed_count"] = completed_count
                break

    def to_dict(self) -> Dict[str, Any]:
        """Convert index to dictionary for serialization."""
        return {
            "version": self.version,
            "projects": self.projects,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProjectIndex:
        """Create index from dictionary."""
        return cls(
            version=data.get("version", "1.0"),
            projects=data.get("projects", []),
        )


@dataclass
class LackeyConfig:
    """
    Configuration settings for Lackey workspace.

    Controls validation rules, agent settings, and operational parameters.
    """

    version: str = "1.0"
    created: datetime = field(default_factory=lambda: datetime.now(UTC))
    workspace: Dict[str, Any] = field(
        default_factory=lambda: {
            "auto_validate_dag": True,
            "archive_completed_chains": True,
            "preserve_archive_days": 90,
            "max_task_file_size_kb": 100,
        }
    )
    ai_agents: Dict[str, Any] = field(
        default_factory=lambda: {
            "max_chain_depth": 10,
            "warn_on_circular_deps": True,
            "complexity_thresholds": {
                "low_max_steps": 5,
                "medium_max_steps": 10,
                "high_min_steps": 8,
            },
        }
    )
    validation: Dict[str, Any] = field(
        default_factory=lambda: {
            "require_objectives": True,
            "require_success_criteria": True,
            "require_complexity_rating": True,
            "max_title_length": 200,
            "max_dependencies": 20,
        }
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for serialization."""
        return {
            "version": self.version,
            "created": self.created.isoformat(),
            "workspace": self.workspace,
            "ai_agents": self.ai_agents,
            "validation": self.validation,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LackeyConfig:
        """Create config from dictionary."""
        return cls(
            version=data.get("version", "1.0"),
            created=(
                datetime.fromisoformat(data["created"])
                if "created" in data
                else datetime.now(UTC)
            ),
            workspace=data.get("workspace", {}),
            ai_agents=data.get("ai_agents", {}),
            validation=data.get("validation", {}),
        )
