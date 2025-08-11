"""Indexing system for fast task search and filtering."""

import gzip
import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .file_ops import atomic_write, read_text_file
from .models import Task

logger = logging.getLogger(__name__)


@dataclass
class IndexMetadata:
    """Metadata about the search indexes."""

    version: str = "1.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_updated: datetime = field(default_factory=lambda: datetime.now(UTC))
    total_tasks: int = 0
    total_projects: int = 0
    index_size_bytes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "total_tasks": self.total_tasks,
            "total_projects": self.total_projects,
            "index_size_bytes": self.index_size_bytes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IndexMetadata":
        """Create from dictionary."""
        return cls(
            version=data.get("version", "1.0"),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            total_tasks=data.get("total_tasks", 0),
            total_projects=data.get("total_projects", 0),
            index_size_bytes=data.get("index_size_bytes", 0),
        )


class TextTokenizer:
    """Tokenizes text for full-text search indexing."""

    def __init__(self) -> None:
        """Initialize the tokenizer."""
        # Common stop words to exclude from indexing
        self.stop_words = {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "by",
            "for",
            "from",
            "has",
            "he",
            "in",
            "is",
            "it",
            "its",
            "of",
            "on",
            "that",
            "the",
            "to",
            "was",
            "will",
            "with",
            "the",
            "this",
            "but",
            "they",
            "have",
            "had",
            "what",
            "said",
            "each",
            "which",
            "she",
            "do",
            "how",
            "their",
            "if",
            "up",
            "out",
            "many",
            "then",
            "them",
            "these",
            "so",
            "some",
            "her",
            "would",
            "make",
            "like",
            "into",
            "him",
            "time",
            "two",
            "more",
            "go",
            "no",
            "way",
            "could",
            "my",
            "than",
            "first",
            "been",
            "call",
            "who",
            "oil",
            "sit",
            "now",
            "find",
            "down",
            "day",
            "did",
            "get",
            "come",
            "made",
            "may",
            "part",
        }

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into searchable terms.

        Args:
            text: Text to tokenize

        Returns:
            List of tokens
        """
        if not text:
            return []

        # Convert to lowercase and split on non-alphanumeric characters
        tokens = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())

        # Filter out stop words and short tokens
        filtered_tokens = [
            token
            for token in tokens
            if len(token) >= 2 and token not in self.stop_words
        ]

        return filtered_tokens

    def extract_phrases(self, text: str, max_phrase_length: int = 3) -> List[str]:
        """Extract phrases (n-grams) from text.

        Args:
            text: Text to extract phrases from
            max_phrase_length: Maximum phrase length in words

        Returns:
            List of phrases
        """
        tokens = self.tokenize(text)
        phrases = []

        for length in range(2, min(max_phrase_length + 1, len(tokens) + 1)):
            for i in range(len(tokens) - length + 1):
                phrase = " ".join(tokens[i : i + length])
                phrases.append(phrase)

        return phrases


class TaskIndex:
    """Maintains indexes for fast task searching and filtering."""

    def __init__(self, index_dir: Path):
        """Initialize the task index.

        Args:
            index_dir: Directory to store index files
        """
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.tokenizer = TextTokenizer()

        # In-memory indexes
        self.text_index: Dict[str, Dict[str, List[int]]] = defaultdict(
            lambda: defaultdict(list)
        )
        self.phrase_index: Dict[str, Set[str]] = defaultdict(set)
        self.field_indexes: Dict[str, Dict[str, Set[str]]] = {
            "status": defaultdict(set),
            "complexity": defaultdict(set),
            "assigned_to": defaultdict(set),
            "tags": defaultdict(set),
            "project_id": defaultdict(set),
        }
        self.date_indexes: Dict[str, List[Tuple[datetime, str]]] = {
            "created_at": [],
            "updated_at": [],
        }
        self.numeric_indexes: Dict[str, List[Tuple[float, str]]] = {
            "progress": [],
        }

        # Track which tasks are in the index
        self.indexed_tasks: Dict[str, str] = {}  # task_id -> project_id
        self.dirty_tasks: Set[str] = set()

        # Metadata
        self.metadata = IndexMetadata()

        # Load existing indexes
        self._load_indexes()

    def add_task(self, project_id: str, task: Task) -> None:
        """Add a task to the indexes.

        Args:
            project_id: Project ID the task belongs to
            task: Task to index
        """
        task_id = task.id

        # Remove existing entries if task was already indexed
        if task_id in self.indexed_tasks:
            self.remove_task(task_id)

        # Add to text index
        self._index_text_fields(task_id, task)

        # Add to field indexes
        self._index_structured_fields(task_id, project_id, task)

        # Add to date indexes
        self._index_date_fields(task_id, task)

        # Add to numeric indexes
        self._index_numeric_fields(task_id, task)

        # Track the task
        self.indexed_tasks[task_id] = project_id
        self.dirty_tasks.add(task_id)

        logger.debug(f"Indexed task {task_id} from project {project_id}")

    def remove_task(self, task_id: str) -> None:
        """Remove a task from all indexes.

        Args:
            task_id: Task ID to remove
        """
        if task_id not in self.indexed_tasks:
            return

        # Remove from text index
        for term_dict in self.text_index.values():
            term_dict.pop(task_id, None)

        # Remove from phrase index
        for task_set in self.phrase_index.values():
            task_set.discard(task_id)

        # Remove from field indexes
        for field_dict in self.field_indexes.values():
            for value_set in field_dict.values():
                value_set.discard(task_id)

        # Remove from date indexes
        for field_name, date_list in self.date_indexes.items():
            self.date_indexes[field_name] = [
                (date, tid) for date, tid in date_list if tid != task_id
            ]

        # Remove from numeric indexes
        for field_name, numeric_list in self.numeric_indexes.items():
            self.numeric_indexes[field_name] = [
                (value, tid) for value, tid in numeric_list if tid != task_id
            ]

        # Remove from tracking
        self.indexed_tasks.pop(task_id, None)
        self.dirty_tasks.discard(task_id)

        logger.debug(f"Removed task {task_id} from indexes")

    def search_text(self, query: str) -> Set[str]:
        """Search for tasks containing the given text.

        Args:
            query: Text query to search for

        Returns:
            Set of task IDs matching the query
        """
        if not query:
            return set(self.indexed_tasks.keys())

        query_lower = query.lower().strip()

        # Check for exact phrase match first
        if query_lower in self.phrase_index:
            return self.phrase_index[query_lower].copy()

        # Tokenize the query
        tokens = self.tokenizer.tokenize(query_lower)
        if not tokens:
            return set()

        # Find tasks containing all tokens (AND search)
        result_sets = []
        for token in tokens:
            if token in self.text_index:
                task_ids = set(self.text_index[token].keys())
                result_sets.append(task_ids)
            else:
                # If any token is not found, no results
                return set()

        # Intersection of all result sets
        if result_sets:
            return set.intersection(*result_sets)

        return set()

    def filter_by_field(self, field: str, value: str) -> Set[str]:
        """Filter tasks by a specific field value.

        Args:
            field: Field name to filter by
            value: Value to match

        Returns:
            Set of task IDs matching the filter
        """
        if field not in self.field_indexes:
            return set()

        return self.field_indexes[field].get(value, set()).copy()

    def filter_by_date_range(
        self,
        field: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Set[str]:
        """Filter tasks by date range.

        Args:
            field: Date field name
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)

        Returns:
            Set of task IDs in the date range
        """
        if field not in self.date_indexes:
            return set()

        date_list = self.date_indexes[field]
        result = set()

        for date, task_id in date_list:
            if start_date and date < start_date:
                continue
            if end_date and date > end_date:
                continue
            result.add(task_id)

        return result

    def filter_by_numeric_range(
        self,
        field: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
    ) -> Set[str]:
        """Filter tasks by numeric range.

        Args:
            field: Numeric field name
            min_value: Minimum value (inclusive)
            max_value: Maximum value (inclusive)

        Returns:
            Set of task IDs in the numeric range
        """
        if field not in self.numeric_indexes:
            return set()

        numeric_list = self.numeric_indexes[field]
        result = set()

        for value, task_id in numeric_list:
            if min_value is not None and value < min_value:
                continue
            if max_value is not None and value > max_value:
                continue
            result.add(task_id)

        return result

    def get_field_values(self, field: str) -> List[str]:
        """Get all unique values for a field.

        Args:
            field: Field name

        Returns:
            List of unique values
        """
        if field not in self.field_indexes:
            return []

        return list(self.field_indexes[field].keys())

    def get_task_count(self) -> int:
        """Get total number of indexed tasks."""
        return len(self.indexed_tasks)

    def get_project_count(self) -> int:
        """Get total number of projects with indexed tasks."""
        return len(set(self.indexed_tasks.values()))

    def rebuild_index(self, storage_manager: Any) -> None:
        """Rebuild the entire index from scratch.

        Args:
            storage_manager: Storage manager to get tasks from
        """
        logger.info("Starting full index rebuild...")

        # Clear existing indexes
        self._clear_indexes()

        # Get all projects and tasks
        try:
            projects = storage_manager.list_projects()
            for project in projects:
                try:
                    tasks = storage_manager.list_tasks(project.id)
                    for task in tasks:
                        self.add_task(project.id, task)
                except Exception as e:
                    logger.error(f"Failed to index tasks for project {project.id}: {e}")
                    continue
        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")
            raise

        # Update metadata
        self.metadata.last_updated = datetime.now(UTC)
        self.metadata.total_tasks = self.get_task_count()
        self.metadata.total_projects = self.get_project_count()

        # Persist the rebuilt index
        self.persist_indexes()

        logger.info(
            f"Index rebuild complete: {self.metadata.total_tasks} tasks indexed"
        )

    def persist_indexes(self) -> None:
        """Persist indexes to disk."""
        try:
            # Update metadata
            self.metadata.last_updated = datetime.now(UTC)
            self.metadata.total_tasks = self.get_task_count()
            self.metadata.total_projects = self.get_project_count()

            # Save metadata
            metadata_file = self.index_dir / "metadata.json"
            with atomic_write(str(metadata_file)) as writer:
                writer.write_json(self.metadata.to_dict())

            # Save text index (compressed)
            text_index_file = self.index_dir / "text_index.json.gz"
            text_data = json.dumps(dict(self.text_index)).encode("utf-8")
            with gzip.open(text_index_file, "wb") as f:
                f.write(text_data)

            # Save phrase index (compressed)
            phrase_index_file = self.index_dir / "phrase_index.json.gz"
            phrase_data = json.dumps(
                {
                    phrase: list(task_set)
                    for phrase, task_set in self.phrase_index.items()
                }
            ).encode("utf-8")
            with gzip.open(phrase_index_file, "wb") as f:
                f.write(phrase_data)

            # Save field indexes
            field_index_file = self.index_dir / "field_indexes.json"
            field_data = {}
            for field_name, field_dict in self.field_indexes.items():
                field_data[field_name] = {
                    value: list(task_set) for value, task_set in field_dict.items()
                }
            with atomic_write(str(field_index_file)) as writer:
                writer.write_json(field_data)

            # Save date indexes
            date_index_file = self.index_dir / "date_indexes.json"
            date_data = {}
            for field_name, date_list in self.date_indexes.items():
                date_data[field_name] = [
                    (date.isoformat(), task_id) for date, task_id in date_list
                ]
            with atomic_write(str(date_index_file)) as writer:
                writer.write_json(date_data)

            # Save numeric indexes
            numeric_index_file = self.index_dir / "numeric_indexes.json"
            with atomic_write(str(numeric_index_file)) as writer:
                writer.write_json(self.numeric_indexes)

            # Save task tracking
            tasks_file = self.index_dir / "indexed_tasks.json"
            with atomic_write(str(tasks_file)) as writer:
                writer.write_json(self.indexed_tasks)

            # Clear dirty flag
            self.dirty_tasks.clear()

            logger.debug("Indexes persisted to disk")

        except Exception as e:
            logger.error(f"Failed to persist indexes: {e}")
            raise

    def _load_indexes(self) -> None:
        """Load indexes from disk."""
        try:
            # Load metadata
            metadata_file = self.index_dir / "metadata.json"
            if metadata_file.exists():
                metadata_data = json.loads(read_text_file(str(metadata_file)))
                self.metadata = IndexMetadata.from_dict(metadata_data)

            # Load text index
            text_index_file = self.index_dir / "text_index.json.gz"
            if text_index_file.exists():
                with gzip.open(text_index_file, "rb") as f:
                    text_data = json.loads(f.read().decode("utf-8"))
                    # Properly reconstruct defaultdict structure
                    self.text_index = defaultdict(lambda: defaultdict(list))
                    for token, task_dict in text_data.items():
                        for task_id, positions in task_dict.items():
                            self.text_index[token][task_id] = positions

            # Load phrase index
            phrase_index_file = self.index_dir / "phrase_index.json.gz"
            if phrase_index_file.exists():
                with gzip.open(phrase_index_file, "rb") as f:
                    phrase_data = json.loads(f.read().decode("utf-8"))
                    self.phrase_index = defaultdict(set)
                    for phrase, task_list in phrase_data.items():
                        self.phrase_index[phrase] = set(task_list)

            # Load field indexes
            field_index_file = self.index_dir / "field_indexes.json"
            if field_index_file.exists():
                field_data = json.loads(read_text_file(str(field_index_file)))
                for field_name, field_dict in field_data.items():
                    self.field_indexes[field_name] = defaultdict(set)
                    for value, task_list in field_dict.items():
                        self.field_indexes[field_name][value] = set(task_list)

            # Load date indexes
            date_index_file = self.index_dir / "date_indexes.json"
            if date_index_file.exists():
                date_data = json.loads(read_text_file(str(date_index_file)))
                for field_name, date_list in date_data.items():
                    self.date_indexes[field_name] = [
                        (datetime.fromisoformat(date_str), task_id)
                        for date_str, task_id in date_list
                    ]

            # Load numeric indexes
            numeric_index_file = self.index_dir / "numeric_indexes.json"
            if numeric_index_file.exists():
                numeric_data = json.loads(read_text_file(str(numeric_index_file)))
                self.numeric_indexes = numeric_data

            # Load task tracking
            tasks_file = self.index_dir / "indexed_tasks.json"
            if tasks_file.exists():
                self.indexed_tasks = json.loads(read_text_file(str(tasks_file)))

            logger.debug(f"Loaded indexes: {len(self.indexed_tasks)} tasks")

        except Exception as e:
            logger.warning(f"Failed to load indexes, starting fresh: {e}")
            self._clear_indexes()

    def _clear_indexes(self) -> None:
        """Clear all in-memory indexes."""
        self.text_index.clear()
        self.phrase_index.clear()
        for field_dict in self.field_indexes.values():
            field_dict.clear()
        for date_list in self.date_indexes.values():
            date_list.clear()
        for numeric_list in self.numeric_indexes.values():
            numeric_list.clear()
        self.indexed_tasks.clear()
        self.dirty_tasks.clear()

    def _index_text_fields(self, task_id: str, task: Task) -> None:
        """Index text fields of a task.

        Args:
            task_id: Task ID
            task: Task to index
        """
        # Collect all text content
        text_fields = [
            task.title,
            task.objective,
            task.context or "",
            " ".join(task.steps),
            " ".join(task.success_criteria),
            task.results or "",
            " ".join(task.tags),  # Include tags in text search
        ]

        # Add notes content
        for note in task.note_manager.get_notes():
            text_fields.append(note.content)

        # Combine all text
        all_text = " ".join(text_fields)

        # Tokenize and index
        tokens = self.tokenizer.tokenize(all_text)
        for i, token in enumerate(tokens):
            self.text_index[token][task_id].append(i)

        # Index phrases
        phrases = self.tokenizer.extract_phrases(all_text)
        for phrase in phrases:
            self.phrase_index[phrase].add(task_id)

    def _index_structured_fields(
        self, task_id: str, project_id: str, task: Task
    ) -> None:
        """Index structured fields of a task.

        Args:
            task_id: Task ID
            project_id: Project ID
            task: Task to index
        """
        # Status
        self.field_indexes["status"][task.status.value].add(task_id)

        # Complexity
        self.field_indexes["complexity"][task.complexity.value].add(task_id)

        # Assigned to
        if task.assigned_to:
            self.field_indexes["assigned_to"][task.assigned_to].add(task_id)
        else:
            self.field_indexes["assigned_to"]["unassigned"].add(task_id)

        # Tags
        for tag in task.tags:
            self.field_indexes["tags"][tag].add(task_id)

        # Project
        self.field_indexes["project_id"][project_id].add(task_id)

    def _index_date_fields(self, task_id: str, task: Task) -> None:
        """Index date fields of a task.

        Args:
            task_id: Task ID
            task: Task to index
        """
        if task.created:
            self.date_indexes["created_at"].append((task.created, task_id))

        if task.updated:
            self.date_indexes["updated_at"].append((task.updated, task_id))

        # Sort date indexes to maintain order
        for date_list in self.date_indexes.values():
            date_list.sort(key=lambda x: x[0])

    def _index_numeric_fields(self, task_id: str, task: Task) -> None:
        """Index numeric fields of a task.

        Args:
            task_id: Task ID
            task: Task to index
        """
        # Progress percentage
        progress = task.progress_percentage()
        self.numeric_indexes["progress"].append((progress, task_id))

        # Sort numeric indexes to maintain order
        for numeric_list in self.numeric_indexes.values():
            numeric_list.sort(key=lambda x: x[0])


class IndexManager:
    """Manages the task indexing system."""

    def __init__(self, lackey_dir: Path):
        """Initialize the index manager.

        Args:
            lackey_dir: Lackey data directory
        """
        self.lackey_dir = Path(lackey_dir)
        self.index_dir = self.lackey_dir / "indexes"
        self.index = TaskIndex(self.index_dir)

        # Auto-persist settings
        self.auto_persist = True
        self.persist_threshold = 10  # Persist after this many changes
        self.changes_since_persist = 0

    def add_task(self, project_id: str, task: Task) -> None:
        """Add a task to the index.

        Args:
            project_id: Project ID
            task: Task to add
        """
        self.index.add_task(project_id, task)
        self._maybe_persist()

    def update_task(self, project_id: str, task: Task) -> None:
        """Update a task in the index.

        Args:
            project_id: Project ID
            task: Updated task
        """
        # Remove and re-add (simpler than selective updates)
        self.index.remove_task(task.id)
        self.index.add_task(project_id, task)
        self._maybe_persist()

    def remove_task(self, task_id: str) -> None:
        """Remove a task from the index.

        Args:
            task_id: Task ID to remove
        """
        self.index.remove_task(task_id)
        self._maybe_persist()

    def search(
        self,
        text_query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        date_filters: Optional[
            Dict[str, Tuple[Optional[datetime], Optional[datetime]]]
        ] = None,
        numeric_filters: Optional[
            Dict[str, Tuple[Optional[float], Optional[float]]]
        ] = None,
    ) -> Set[str]:
        """Search for tasks using the index.

        Args:
            text_query: Text to search for
            filters: Field filters (field -> value)
            date_filters: Date range filters (field -> (start, end))
            numeric_filters: Numeric range filters (field -> (min, max))

        Returns:
            Set of matching task IDs
        """
        result_sets = []

        # Text search
        if text_query:
            text_results = self.index.search_text(text_query)
            result_sets.append(text_results)

        # Field filters
        if filters:
            for field_name, value in filters.items():
                field_results = self.index.filter_by_field(field_name, value)
                result_sets.append(field_results)

        # Date filters
        if date_filters:
            for field_name, (start_date, end_date) in date_filters.items():
                date_results = self.index.filter_by_date_range(
                    field_name, start_date, end_date
                )
                result_sets.append(date_results)

        # Numeric filters
        if numeric_filters:
            for field_name, (min_val, max_val) in numeric_filters.items():
                numeric_results = self.index.filter_by_numeric_range(
                    field_name, min_val, max_val
                )
                result_sets.append(numeric_results)

        # Intersection of all result sets (AND logic)
        if result_sets:
            return set.intersection(*result_sets)
        else:
            # No filters, return all tasks
            return set(self.index.indexed_tasks.keys())

    def get_suggestions(
        self, field: str, partial_value: str, limit: int = 10
    ) -> List[str]:
        """Get autocomplete suggestions for a field.

        Args:
            field: Field name
            partial_value: Partial value to complete
            limit: Maximum suggestions to return

        Returns:
            List of suggestions
        """
        field_values = self.index.get_field_values(field)
        partial_lower = partial_value.lower()

        suggestions = [
            value for value in field_values if value.lower().startswith(partial_lower)
        ]

        return sorted(suggestions)[:limit]

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics.

        Returns:
            Dictionary of index statistics
        """
        return {
            "total_tasks": self.index.get_task_count(),
            "total_projects": self.index.get_project_count(),
            "index_size_mb": self._get_index_size_mb(),
            "last_updated": self.index.metadata.last_updated.isoformat(),
            "dirty_tasks": len(self.index.dirty_tasks),
        }

    def rebuild_index(self, storage_manager: Any) -> None:
        """Rebuild the entire index.

        Args:
            storage_manager: Storage manager to get data from
        """
        self.index.rebuild_index(storage_manager)

    def persist_indexes(self) -> None:
        """Force persist indexes to disk."""
        self.index.persist_indexes()
        self.changes_since_persist = 0

    def _maybe_persist(self) -> None:
        """Persist indexes if auto-persist is enabled and threshold is reached."""
        if not self.auto_persist:
            return

        self.changes_since_persist += 1
        if self.changes_since_persist >= self.persist_threshold:
            self.persist_indexes()

    def _get_index_size_mb(self) -> float:
        """Get total size of index files in MB."""
        total_size = 0
        try:
            for file_path in self.index_dir.glob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except (OSError, IOError):
            # Ignore file system errors when calculating size
            pass

        return total_size / (1024 * 1024)  # Convert to MB
