"""Enhanced note system for Lackey task management.

This module provides rich note functionality with timestamps, metadata,
markdown support, and search capabilities for coordinated agent workflows.
"""

from __future__ import annotations

import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, Iterator, List, Optional, Set


def _high_precision_utcnow() -> datetime:
    """Generate high-precision UTC timestamp to avoid collisions."""
    # Use time.time_ns() for nanosecond precision, then convert to datetime
    # This ensures unique timestamps even for rapid operations
    ns_timestamp = time.time_ns()
    return datetime.fromtimestamp(ns_timestamp / 1_000_000_000, UTC)


class NoteType(Enum):
    """Note type enumeration for categorization."""

    USER = "user"  # Manual user note
    SYSTEM = "system"  # System-generated note
    STATUS_CHANGE = "status_change"  # Status transition note
    ASSIGNMENT = "assignment"  # Task assignment note
    PROGRESS = "progress"  # Progress update note
    DEPENDENCY = "dependency"  # Dependency change note
    ARCHIVE = "archive"  # Archive/restore note


@dataclass
class Note:
    """
    Rich note model with metadata and markdown support.

    Notes provide context, communication, and audit trail for task management
    with support for categorization, search, and chronological ordering.
    """

    id: str
    content: str
    note_type: NoteType
    created: datetime
    author: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        """Validate note data after initialization."""
        if not self.id:
            self.id = str(uuid.uuid4())

        # Normalize tags to lowercase and strip whitespace
        if self.tags:
            self.tags = {tag.lower().strip() for tag in self.tags if tag.strip()}

    @classmethod
    def create_user_note(
        cls,
        content: str,
        author: Optional[str] = None,
        tags: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Note:
        """Create a new user note."""
        return cls(
            id=str(uuid.uuid4()),
            content=content.strip(),
            note_type=NoteType.USER,
            created=_high_precision_utcnow(),
            author=author,
            tags=tags or set(),
            metadata=metadata or {},
        )

    @classmethod
    def create_system_note(
        cls,
        content: str,
        note_type: NoteType = NoteType.SYSTEM,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Note:
        """Create a new system-generated note."""
        return cls(
            id=str(uuid.uuid4()),
            content=content.strip(),
            note_type=note_type,
            created=_high_precision_utcnow(),
            author="system",
            metadata=metadata or {},
        )

    def add_tag(self, tag: str) -> None:
        """Add a tag to the note."""
        self.tags.add(tag.lower().strip())

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the note."""
        self.tags.discard(tag.lower().strip())

    def has_tag(self, tag: str) -> bool:
        """Check if note has a specific tag."""
        return tag.lower().strip() in self.tags

    def get_plain_text(self) -> str:
        """Extract plain text from markdown content."""
        # Remove markdown formatting for search
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", self.content)  # Bold
        text = re.sub(r"\*(.*?)\*", r"\1", text)  # Italic
        text = re.sub(r"`(.*?)`", r"\1", text)  # Code
        text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)  # Links
        text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)  # Headers
        text = re.sub(r"^\s*[-*+]\s*", "", text, flags=re.MULTILINE)  # Lists
        return text.strip()

    def matches_search(self, query: str) -> bool:
        """Check if note matches search query."""
        query_lower = query.lower()

        # Search in content (both markdown and plain text)
        if query_lower in self.content.lower():
            return True
        if query_lower in self.get_plain_text().lower():
            return True

        # Search in tags
        if any(query_lower in tag for tag in self.tags):
            return True

        # Search in author
        if self.author and query_lower in self.author.lower():
            return True

        # Search in metadata values
        for value in self.metadata.values():
            if isinstance(value, str) and query_lower in value.lower():
                return True

        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert note to dictionary for serialization."""
        return {
            "id": self.id,
            "content": self.content,
            "note_type": self.note_type.value,
            "created": self.created.isoformat(),
            "author": self.author,
            "metadata": self.metadata,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Note:
        """Create note from dictionary."""
        created_dt = datetime.fromisoformat(data["created"])
        # Ensure timezone-aware datetime
        if created_dt.tzinfo is None:
            created_dt = created_dt.replace(tzinfo=UTC)

        return cls(
            id=data["id"],
            content=data["content"],
            note_type=NoteType(data["note_type"]),
            created=created_dt,
            author=data.get("author"),
            metadata=data.get("metadata", {}),
            tags=set(data.get("tags", [])),
        )

    def __str__(self) -> str:
        """Return string representation of note."""
        timestamp = self.created.strftime("%Y-%m-%d %H:%M")
        author_str = f" by {self.author}" if self.author else ""
        return f"[{timestamp}]{author_str}: {self.content}"


class NoteManager:
    """
    Manager for note operations with search and filtering capabilities.

    Provides high-level operations for managing task notes including
    chronological ordering, search, filtering, and history management.
    """

    def __init__(self, notes: Optional[List[Note]] = None):
        """Initialize note manager with optional existing notes."""
        self._notes: List[Note] = notes or []

    def add_note(
        self,
        content: str,
        note_type: NoteType = NoteType.USER,
        author: Optional[str] = None,
        tags: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Note:
        """Add a new note and return it."""
        if note_type == NoteType.USER:
            note = Note.create_user_note(content, author, tags, metadata)
        else:
            # For non-user notes, create manually to preserve author
            note = Note(
                id=str(uuid.uuid4()),
                content=content.strip(),
                note_type=note_type,
                created=_high_precision_utcnow(),
                author=author or "system",
                tags=tags or set(),
                metadata=metadata or {},
            )

        self._notes.append(note)
        return note

    def get_notes(
        self,
        note_type: Optional[NoteType] = None,
        author: Optional[str] = None,
        tag: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[Note]:
        """Get notes with optional filtering."""
        filtered_notes = self._notes.copy()

        # Filter by type
        if note_type:
            filtered_notes = [n for n in filtered_notes if n.note_type == note_type]

        # Filter by author
        if author:
            filtered_notes = [n for n in filtered_notes if n.author == author]

        # Filter by tag
        if tag:
            filtered_notes = [n for n in filtered_notes if n.has_tag(tag)]

        # Filter by date range
        if since:
            filtered_notes = [n for n in filtered_notes if n.created >= since]
        if until:
            filtered_notes = [n for n in filtered_notes if n.created <= until]

        # Sort chronologically (newest first)
        filtered_notes.sort(key=lambda n: n.created, reverse=True)

        # Apply limit
        if limit:
            filtered_notes = filtered_notes[:limit]

        return filtered_notes

    def search_notes(
        self,
        query: str,
        note_type: Optional[NoteType] = None,
        author: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Note]:
        """Search notes by content, tags, and metadata."""
        if not query.strip():
            return []

        # Get base filtered notes
        filtered_notes = self.get_notes(note_type=note_type, author=author)

        # Apply search filter
        matching_notes = [n for n in filtered_notes if n.matches_search(query)]

        # Apply limit
        if limit:
            matching_notes = matching_notes[:limit]

        return matching_notes

    def get_note_by_id(self, note_id: str) -> Optional[Note]:
        """Get a specific note by ID."""
        for note in self._notes:
            if note.id == note_id:
                return note
        return None

    def remove_note(self, note_id: str) -> bool:
        """Remove a note by ID. Returns True if removed."""
        for i, note in enumerate(self._notes):
            if note.id == note_id:
                del self._notes[i]
                return True
        return False

    def get_note_count(self) -> int:
        """Get total number of notes."""
        return len(self._notes)

    def get_note_count_by_type(self) -> Dict[str, int]:
        """Get note counts by type."""
        counts: Dict[str, int] = {}
        for note in self._notes:
            note_type = note.note_type.value
            counts[note_type] = counts.get(note_type, 0) + 1
        return counts

    def get_recent_notes(self, limit: int = 10) -> List[Note]:
        """Get most recent notes."""
        return self.get_notes(limit=limit)

    def clear_notes(self) -> None:
        """Remove all notes."""
        self._notes.clear()

    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert all notes to list of dictionaries."""
        return [note.to_dict() for note in self._notes]

    def __len__(self) -> int:
        """Return number of notes."""
        return len(self._notes)

    def __iter__(self) -> Iterator[Note]:
        """Iterate over notes in chronological order (oldest first)."""
        return iter(sorted(self._notes, key=lambda n: n.created))

    @classmethod
    def from_dict_list(cls, data: List[Dict[str, Any]]) -> NoteManager:
        """Create note manager from list of dictionaries."""
        notes = [Note.from_dict(note_data) for note_data in data]
        return cls(notes)
