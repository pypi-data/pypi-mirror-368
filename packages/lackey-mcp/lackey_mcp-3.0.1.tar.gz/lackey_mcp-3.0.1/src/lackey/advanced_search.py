"""Advanced search system with filtering, sorting, and faceted search capabilities."""

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .indexing import IndexManager
from .models import Complexity, Task, TaskStatus

logger = logging.getLogger(__name__)


class SearchOperator(Enum):
    """Search operators for advanced queries."""

    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    CONTAINS = "CONTAINS"
    EQUALS = "EQUALS"
    GREATER_THAN = "GT"
    LESS_THAN = "LT"
    STARTS_WITH = "STARTS_WITH"
    ENDS_WITH = "ENDS_WITH"
    REGEX = "REGEX"


class SortOrder(Enum):
    """Sort order enumeration."""

    ASC = "asc"
    DESC = "desc"


class SearchField(Enum):
    """Searchable fields enumeration."""

    TITLE = "title"
    OBJECTIVE = "objective"
    CONTEXT = "context"
    STEPS = "steps"
    SUCCESS_CRITERIA = "success_criteria"
    NOTES = "notes"
    TAGS = "tags"
    STATUS = "status"
    COMPLEXITY = "complexity"
    ASSIGNED_TO = "assigned_to"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    PROGRESS = "progress"
    DEPENDENCIES = "dependencies"
    ALL = "all"


@dataclass
class SearchFilter:
    """Represents a search filter condition."""

    field: SearchField
    operator: SearchOperator
    value: Any
    case_sensitive: bool = False

    def to_index_filter(self) -> Tuple[str, str, Any]:
        """Convert to index filter format.

        Returns:
            Tuple of (filter_type, field, value)
        """
        if self.field in [
            SearchField.STATUS,
            SearchField.COMPLEXITY,
            SearchField.ASSIGNED_TO,
            SearchField.TAGS,
        ]:
            return ("field", self.field.value, str(self.value))
        elif self.field in [SearchField.CREATED_AT, SearchField.UPDATED_AT]:
            return ("date", self.field.value, self.value)
        elif self.field == SearchField.PROGRESS:
            return ("numeric", self.field.value, self.value)
        else:
            return ("text", self.field.value, self.value)


@dataclass
class SortCriteria:
    """Represents sorting criteria for search results."""

    field: SearchField
    order: SortOrder = SortOrder.ASC

    def get_sort_key(self, task: Task) -> Any:
        """Get the sort key value for a task.

        Args:
            task: Task to get sort key for

        Returns:
            Sort key value
        """
        field_map = {
            SearchField.TITLE: task.title.lower(),
            SearchField.STATUS: task.status.value,
            SearchField.COMPLEXITY: self._complexity_sort_value(task.complexity),
            SearchField.ASSIGNED_TO: (task.assigned_to or "").lower(),
            SearchField.CREATED_AT: task.created,
            SearchField.UPDATED_AT: task.updated,
            SearchField.PROGRESS: task.progress_percentage(),
        }
        return field_map.get(self.field, "")

    def _complexity_sort_value(self, complexity: Complexity) -> int:
        """Convert complexity to numeric value for sorting."""
        complexity_values = {
            Complexity.LOW: 1,
            Complexity.MEDIUM: 2,
            Complexity.HIGH: 3,
        }
        return complexity_values.get(complexity, 0)


@dataclass
class SearchQuery:
    """Represents a complete search query with filters, sorting, and pagination."""

    text: Optional[str] = None
    filters: List[SearchFilter] = field(default_factory=list)
    sort_criteria: List[SortCriteria] = field(default_factory=list)
    limit: Optional[int] = None
    offset: int = 0
    include_archived: bool = False

    def add_filter(
        self,
        field: SearchField,
        operator: SearchOperator,
        value: Any,
        case_sensitive: bool = False,
    ) -> "SearchQuery":
        """Add a filter to the search query.

        Args:
            field: Field to filter on
            operator: Comparison operator
            value: Value to compare against
            case_sensitive: Whether comparison is case sensitive

        Returns:
            Self for method chaining
        """
        self.filters.append(SearchFilter(field, operator, value, case_sensitive))
        return self

    def add_sort(
        self, field: SearchField, order: SortOrder = SortOrder.ASC
    ) -> "SearchQuery":
        """Add sorting criteria to the search query.

        Args:
            field: Field to sort by
            order: Sort order

        Returns:
            Self for method chaining
        """
        self.sort_criteria.append(SortCriteria(field, order))
        return self

    def to_index_query(self) -> Dict[str, Any]:
        """Convert to index query format.

        Returns:
            Dictionary suitable for IndexManager.search()
        """
        index_query: Dict[str, Any] = {}

        # Text query
        if self.text:
            index_query["text_query"] = self.text

        # Convert filters
        field_filters: Dict[str, Any] = {}
        date_filters: Dict[str, tuple] = {}
        numeric_filters: Dict[str, tuple] = {}

        for filter_obj in self.filters:
            filter_type, field, value = filter_obj.to_index_filter()

            if filter_type == "field":
                field_filters[field] = value
            elif filter_type == "date":
                # Handle date range filters
                if filter_obj.operator == SearchOperator.GREATER_THAN:
                    date_filters[field] = (value, None)
                elif filter_obj.operator == SearchOperator.LESS_THAN:
                    date_filters[field] = (None, value)
                else:
                    date_filters[field] = (value, value)
            elif filter_type == "numeric":
                # Handle numeric range filters
                if filter_obj.operator == SearchOperator.GREATER_THAN:
                    numeric_filters[field] = (value, None)
                elif filter_obj.operator == SearchOperator.LESS_THAN:
                    numeric_filters[field] = (None, value)
                else:
                    numeric_filters[field] = (value, value)

        if field_filters:
            index_query["filters"] = field_filters
        if date_filters:
            index_query["date_filters"] = date_filters
        if numeric_filters:
            index_query["numeric_filters"] = numeric_filters

        return index_query


@dataclass
class SearchResult:
    """Represents search results with metadata."""

    tasks: List[Tuple[str, Task]]  # (project_id, task) pairs
    total_count: int
    query: SearchQuery
    execution_time_ms: float
    facets: Dict[str, Dict[str, int]] = field(default_factory=dict)

    def get_tasks_only(self) -> List[Task]:
        """Get just the tasks from the results."""
        return [task for _, task in self.tasks]

    def get_project_ids(self) -> Set[str]:
        """Get unique project IDs from the results."""
        return {project_id for project_id, _ in self.tasks}


class FacetCalculator:
    """Calculates facets (aggregated counts) for search results."""

    @staticmethod
    def calculate_facets(tasks: List[Tuple[str, Task]]) -> Dict[str, Dict[str, int]]:
        """Calculate facets for a list of tasks.

        Args:
            tasks: List of (project_id, task) pairs

        Returns:
            Dictionary of facet counts
        """
        facets: Dict[str, Dict[str, int]] = {
            "status": {},
            "complexity": {},
            "assigned_to": {},
            "tags": {},
            "project": {},
        }

        for project_id, task in tasks:
            # Status facet
            status = task.status.value
            facets["status"][status] = facets["status"].get(status, 0) + 1

            # Complexity facet
            complexity = task.complexity.value
            facets["complexity"][complexity] = (
                facets["complexity"].get(complexity, 0) + 1
            )

            # Assigned to facet
            assignee = task.assigned_to or "Unassigned"
            facets["assigned_to"][assignee] = facets["assigned_to"].get(assignee, 0) + 1

            # Tags facet
            for tag in task.tags:
                facets["tags"][tag] = facets["tags"].get(tag, 0) + 1

            # Project facet
            facets["project"][project_id] = facets["project"].get(project_id, 0) + 1

        return facets


class AdvancedSearchEngine:
    """
    Advanced search engine with filtering, sorting, and faceted search capabilities.

    Provides sophisticated search functionality beyond simple text matching,
    including field-specific filters, multiple sorting criteria, and faceted
    search results for better data exploration.
    """

    def __init__(self, storage_manager: Any, lackey_dir: str) -> None:
        """Initialize the advanced search engine.

        Args:
            storage_manager: Storage manager instance for data access
            lackey_dir: Lackey data directory for indexes
        """
        self.storage = storage_manager
        self.index_manager = IndexManager(Path(lackey_dir))
        self.facet_calculator = FacetCalculator()

    def search(
        self, query: SearchQuery, project_id: Optional[str] = None
    ) -> SearchResult:
        """Execute an advanced search query.

        Args:
            query: Search query with filters and sorting
            project_id: Optional project ID to limit search scope

        Returns:
            Search results with metadata
        """
        start_time = datetime.now(UTC)

        try:
            # Convert query to index format
            index_query = query.to_index_query()

            # Add project filter if specified
            if project_id:
                if "filters" not in index_query:
                    index_query["filters"] = {}
                index_query["filters"]["project_id"] = project_id

            # Execute search using index
            matching_task_ids = self.index_manager.search(**index_query)

            # Load the actual task objects
            matching_tasks = []
            for task_id in matching_task_ids:
                try:
                    # Get project ID for this task
                    task_project_id = self.index_manager.index.indexed_tasks.get(
                        task_id
                    )
                    if not task_project_id:
                        continue

                    # Load the task
                    task = self.storage.get_task(task_id)

                    # Tasks don't have archived status - all tasks are searchable
                    # (Projects can be archived, but tasks are just marked as done)

                    matching_tasks.append((task_project_id, task))

                except Exception as e:
                    logger.warning(f"Failed to load task {task_id}: {e}")
                    continue

            # Calculate total count before pagination
            total_count = len(matching_tasks)

            # Apply sorting
            if query.sort_criteria:
                matching_tasks = self._sort_tasks(matching_tasks, query.sort_criteria)

            # Apply pagination
            if query.offset > 0:
                matching_tasks = matching_tasks[query.offset :]
            if query.limit:
                matching_tasks = matching_tasks[: query.limit]

            # Calculate facets
            facets = self.facet_calculator.calculate_facets(matching_tasks)

            # Calculate execution time
            end_time = datetime.now(UTC)
            execution_time_ms = (end_time - start_time).total_seconds() * 1000

            return SearchResult(
                tasks=matching_tasks,
                total_count=total_count,
                query=query,
                execution_time_ms=execution_time_ms,
                facets=facets,
            )

        except Exception as e:
            logger.error(f"Search execution failed: {e}")
            raise

    def _sort_tasks(
        self,
        tasks: List[Tuple[str, Task]],
        sort_criteria: List[SortCriteria],
    ) -> List[Tuple[str, Task]]:
        """Sort tasks according to the provided criteria.

        Args:
            tasks: List of (project_id, task) pairs to sort
            sort_criteria: List of sorting criteria

        Returns:
            Sorted list of tasks
        """
        if not sort_criteria:
            return tasks

        def sort_key(item: Tuple[str, Task]) -> Tuple:
            """Generate sort key for a task."""
            _, task = item
            keys: List[Any] = []
            for criteria in sort_criteria:
                key_value = criteria.get_sort_key(task)
                # Handle None values
                if key_value is None:
                    key_value = ""
                # Reverse for descending order
                if criteria.order == SortOrder.DESC:
                    if isinstance(key_value, str):
                        # For strings, we can't negate, so we'll handle this differently
                        keys.append((1, key_value))  # Will be handled in reverse
                    else:
                        keys.append(
                            -key_value
                            if isinstance(key_value, (int, float))
                            else key_value
                        )
                else:
                    if isinstance(key_value, str):
                        keys.append((0, key_value))
                    else:
                        keys.append(key_value)
            return tuple(keys)

        # Sort with custom key
        sorted_tasks = sorted(tasks, key=sort_key)

        # Handle string descending order separately
        for i, criteria in enumerate(sort_criteria):
            if criteria.order == SortOrder.DESC and criteria.field in [
                SearchField.TITLE,
                SearchField.ASSIGNED_TO,
            ]:
                # Re-sort just this portion in reverse
                sorted_tasks = sorted(
                    sorted_tasks,
                    key=lambda x: criteria.get_sort_key(x[1]),
                    reverse=True,
                )
                break  # Only handle the first string desc field

        return sorted_tasks

    def create_query_builder(self) -> "QueryBuilder":
        """Create a query builder for fluent query construction.

        Returns:
            New query builder instance
        """
        return QueryBuilder()

    def suggest_completions(
        self, field: SearchField, partial_value: str, limit: int = 10
    ) -> List[str]:
        """Suggest completions for a field value.

        Args:
            field: Field to get suggestions for
            partial_value: Partial value to complete
            limit: Maximum number of suggestions

        Returns:
            List of suggested completions
        """
        return self.index_manager.get_suggestions(field.value, partial_value, limit)

    def get_search_stats(self) -> Dict[str, Any]:
        """Get search engine statistics.

        Returns:
            Dictionary of search statistics
        """
        index_stats = self.index_manager.get_stats()
        return {
            "indexed_tasks": index_stats["total_tasks"],
            "indexed_projects": index_stats["total_projects"],
            "index_size_mb": index_stats["index_size_mb"],
            "last_index_update": index_stats["last_updated"],
            "dirty_tasks": index_stats["dirty_tasks"],
        }

    def rebuild_search_index(self) -> None:
        """Rebuild the search index from scratch."""
        self.index_manager.rebuild_index(self.storage)

    def update_task_index(self, project_id: str, task: Task) -> None:
        """Update the index when a task changes.

        Args:
            project_id: Project ID
            task: Updated task
        """
        self.index_manager.update_task(project_id, task)

    def remove_task_from_index(self, task_id: str) -> None:
        """Remove a task from the index.

        Args:
            task_id: Task ID to remove
        """
        self.index_manager.remove_task(task_id)


class QueryBuilder:
    """Fluent interface for building search queries."""

    def __init__(self) -> None:
        """Initialize a new query builder."""
        self.query = SearchQuery()

    def text(self, search_text: str) -> "QueryBuilder":
        """Set the text search query.

        Args:
            search_text: Text to search for

        Returns:
            Self for method chaining
        """
        self.query.text = search_text
        return self

    def filter_by_status(self, status: TaskStatus) -> "QueryBuilder":
        """Add a status filter.

        Args:
            status: Task status to filter by

        Returns:
            Self for method chaining
        """
        self.query.add_filter(SearchField.STATUS, SearchOperator.EQUALS, status.value)
        return self

    def filter_by_complexity(self, complexity: Complexity) -> "QueryBuilder":
        """Add a complexity filter.

        Args:
            complexity: Task complexity to filter by

        Returns:
            Self for method chaining
        """
        self.query.add_filter(
            SearchField.COMPLEXITY, SearchOperator.EQUALS, complexity.value
        )
        return self

    def filter_by_assignee(self, assignee: str) -> "QueryBuilder":
        """Add an assignee filter.

        Args:
            assignee: Assignee to filter by

        Returns:
            Self for method chaining
        """
        self.query.add_filter(SearchField.ASSIGNED_TO, SearchOperator.EQUALS, assignee)
        return self

    def filter_by_tag(self, tag: str) -> "QueryBuilder":
        """Add a tag filter.

        Args:
            tag: Tag to filter by

        Returns:
            Self for method chaining
        """
        self.query.add_filter(SearchField.TAGS, SearchOperator.CONTAINS, tag)
        return self

    def filter_by_progress(
        self, min_progress: Optional[int] = None, max_progress: Optional[int] = None
    ) -> "QueryBuilder":
        """Add progress filters.

        Args:
            min_progress: Minimum progress percentage
            max_progress: Maximum progress percentage

        Returns:
            Self for method chaining
        """
        if min_progress is not None:
            self.query.add_filter(
                SearchField.PROGRESS, SearchOperator.GREATER_THAN, min_progress
            )
        if max_progress is not None:
            self.query.add_filter(
                SearchField.PROGRESS, SearchOperator.LESS_THAN, max_progress
            )
        return self

    def filter_by_date_range(
        self,
        field: SearchField,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> "QueryBuilder":
        """Add date range filter.

        Args:
            field: Date field to filter on
            start_date: Start of date range
            end_date: End of date range

        Returns:
            Self for method chaining
        """
        if start_date:
            self.query.add_filter(field, SearchOperator.GREATER_THAN, start_date)
        if end_date:
            self.query.add_filter(field, SearchOperator.LESS_THAN, end_date)
        return self

    def sort_by_title(self, order: SortOrder = SortOrder.ASC) -> "QueryBuilder":
        """Sort by title.

        Args:
            order: Sort order

        Returns:
            Self for method chaining
        """
        self.query.add_sort(SearchField.TITLE, order)
        return self

    def sort_by_created_date(self, order: SortOrder = SortOrder.DESC) -> "QueryBuilder":
        """Sort by creation date.

        Args:
            order: Sort order

        Returns:
            Self for method chaining
        """
        self.query.add_sort(SearchField.CREATED_AT, order)
        return self

    def sort_by_progress(self, order: SortOrder = SortOrder.DESC) -> "QueryBuilder":
        """Sort by progress.

        Args:
            order: Sort order

        Returns:
            Self for method chaining
        """
        self.query.add_sort(SearchField.PROGRESS, order)
        return self

    def sort_by_status(self, order: SortOrder = SortOrder.ASC) -> "QueryBuilder":
        """Sort by status.

        Args:
            order: Sort order

        Returns:
            Self for method chaining
        """
        self.query.add_sort(SearchField.STATUS, order)
        return self

    def sort_by_complexity(self, order: SortOrder = SortOrder.ASC) -> "QueryBuilder":
        """Sort by complexity.

        Args:
            order: Sort order

        Returns:
            Self for method chaining
        """
        self.query.add_sort(SearchField.COMPLEXITY, order)
        return self

    def limit(self, count: int) -> "QueryBuilder":
        """Set result limit.

        Args:
            count: Maximum number of results

        Returns:
            Self for method chaining
        """
        self.query.limit = count
        return self

    def offset(self, count: int) -> "QueryBuilder":
        """Set result offset.

        Args:
            count: Number of results to skip

        Returns:
            Self for method chaining
        """
        self.query.offset = count
        return self

    def include_archived(self, include: bool = True) -> "QueryBuilder":
        """Include archived tasks in results.

        Args:
            include: Whether to include archived tasks

        Returns:
            Self for method chaining
        """
        self.query.include_archived = include
        return self

    def build(self) -> SearchQuery:
        """Build the final search query.

        Returns:
            Constructed search query
        """
        return self.query
