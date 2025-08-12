"""Tool usage analytics and tracking infrastructure for MCP tools."""

import json
import logging
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ToolUsageEvent:
    """Individual tool usage event."""

    tool_name: str
    timestamp: float
    execution_time_ms: float
    success: bool
    error_message: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    user_context: Optional[str] = None


@dataclass
class ToolUsageStats:
    """Aggregated statistics for a tool."""

    tool_name: str
    total_calls: int
    successful_calls: int
    failed_calls: int
    avg_execution_time_ms: float
    min_execution_time_ms: float
    max_execution_time_ms: float
    last_used: float
    error_rate: float
    common_parameters: Dict[str, int]
    common_errors: Dict[str, int]


class ToolAnalyticsManager:
    """Manages tool usage analytics and tracking."""

    def __init__(self, analytics_dir: Path):
        """Initialize analytics manager.

        Args:
            analytics_dir: Directory to store analytics data
        """
        self.analytics_dir = analytics_dir
        self.analytics_dir.mkdir(parents=True, exist_ok=True)

        self.events_file = self.analytics_dir / "tool_events.jsonl"
        self.stats_file = self.analytics_dir / "tool_stats.json"

        # In-memory cache for performance
        self._event_cache: List[ToolUsageEvent] = []
        self._stats_cache: Dict[str, ToolUsageStats] = {}
        self._cache_dirty = False

        # Load existing data
        self._load_existing_data()

    def _load_existing_data(self) -> None:
        """Load existing analytics data from disk."""
        try:
            # Load events from JSONL file
            if self.events_file.exists():
                with open(self.events_file, "r") as f:
                    for line in f:
                        if line.strip():
                            event_data = json.loads(line)
                            event = ToolUsageEvent(**event_data)
                            self._event_cache.append(event)

            # Load stats from JSON file
            if self.stats_file.exists():
                with open(self.stats_file, "r") as f:
                    stats_data = json.load(f)
                    for tool_name, stats in stats_data.items():
                        self._stats_cache[tool_name] = ToolUsageStats(**stats)

        except Exception as e:
            logger.warning(f"Failed to load existing analytics data: {e}")

    def record_tool_usage(
        self,
        tool_name: str,
        execution_time_ms: float,
        success: bool,
        error_message: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        user_context: Optional[str] = None,
    ) -> None:
        """Record a tool usage event.

        Args:
            tool_name: Name of the tool used
            execution_time_ms: Execution time in milliseconds
            success: Whether the tool execution was successful
            error_message: Error message if execution failed
            parameters: Tool parameters used
            user_context: Optional user context information
        """
        event = ToolUsageEvent(
            tool_name=tool_name,
            timestamp=time.time(),
            execution_time_ms=execution_time_ms,
            success=success,
            error_message=error_message,
            parameters=parameters,
            user_context=user_context,
        )

        self._event_cache.append(event)
        self._cache_dirty = True

        # Update stats cache
        self._update_stats_cache(event)

        # Periodic flush to disk
        if len(self._event_cache) % 100 == 0:
            self._flush_to_disk()

    def _update_stats_cache(self, event: ToolUsageEvent) -> None:
        """Update statistics cache with new event."""
        tool_name = event.tool_name

        if tool_name not in self._stats_cache:
            self._stats_cache[tool_name] = ToolUsageStats(
                tool_name=tool_name,
                total_calls=0,
                successful_calls=0,
                failed_calls=0,
                avg_execution_time_ms=0.0,
                min_execution_time_ms=float("inf"),
                max_execution_time_ms=0.0,
                last_used=0.0,
                error_rate=0.0,
                common_parameters={},
                common_errors={},
            )

        stats = self._stats_cache[tool_name]

        # Update counters
        stats.total_calls += 1
        if event.success:
            stats.successful_calls += 1
        else:
            stats.failed_calls += 1

        # Update timing statistics
        stats.avg_execution_time_ms = (
            stats.avg_execution_time_ms * (stats.total_calls - 1)
            + event.execution_time_ms
        ) / stats.total_calls
        stats.min_execution_time_ms = min(
            stats.min_execution_time_ms, event.execution_time_ms
        )
        stats.max_execution_time_ms = max(
            stats.max_execution_time_ms, event.execution_time_ms
        )
        stats.last_used = event.timestamp

        # Update error rate
        stats.error_rate = stats.failed_calls / stats.total_calls

        # Track common parameters
        if event.parameters:
            for key, value in event.parameters.items():
                param_key = f"{key}={str(value)[:50]}"  # Truncate long values
                stats.common_parameters[param_key] = (
                    stats.common_parameters.get(param_key, 0) + 1
                )

        # Track common errors
        if event.error_message:
            error_key = event.error_message[:100]  # Truncate long error messages
            stats.common_errors[error_key] = stats.common_errors.get(error_key, 0) + 1

    def get_tool_stats(self, tool_name: str) -> Optional[ToolUsageStats]:
        """Get statistics for a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool statistics or None if tool not found
        """
        return self._stats_cache.get(tool_name)

    def get_all_stats(self) -> Dict[str, ToolUsageStats]:
        """Get statistics for all tools.

        Returns:
            Dictionary mapping tool names to their statistics
        """
        return self._stats_cache.copy()

    def get_top_tools(self, limit: int = 10) -> List[ToolUsageStats]:
        """Get most frequently used tools.

        Args:
            limit: Maximum number of tools to return

        Returns:
            List of tool statistics sorted by usage frequency
        """
        return sorted(
            self._stats_cache.values(), key=lambda s: s.total_calls, reverse=True
        )[:limit]

    def get_recent_events(self, hours: int = 24) -> List[ToolUsageEvent]:
        """Get recent tool usage events.

        Args:
            hours: Number of hours to look back

        Returns:
            List of recent events
        """
        cutoff_time = time.time() - (hours * 3600)
        return [event for event in self._event_cache if event.timestamp >= cutoff_time]

    def get_error_analysis(self) -> Dict[str, Any]:
        """Get error analysis across all tools.

        Returns:
            Dictionary with error analysis data
        """
        total_calls = sum(stats.total_calls for stats in self._stats_cache.values())
        total_errors = sum(stats.failed_calls for stats in self._stats_cache.values())

        # Find tools with highest error rates
        high_error_tools = [
            stats
            for stats in self._stats_cache.values()
            if stats.error_rate > 0.1 and stats.total_calls > 10
        ]
        high_error_tools.sort(key=lambda s: s.error_rate, reverse=True)

        # Aggregate common errors
        all_errors: Dict[str, int] = defaultdict(int)
        for stats in self._stats_cache.values():
            for error, count in stats.common_errors.items():
                all_errors[error] += count

        return {
            "overall_error_rate": total_errors / total_calls if total_calls > 0 else 0,
            "total_calls": total_calls,
            "total_errors": total_errors,
            "high_error_tools": [
                {
                    "tool_name": stats.tool_name,
                    "error_rate": stats.error_rate,
                    "total_calls": stats.total_calls,
                    "failed_calls": stats.failed_calls,
                }
                for stats in high_error_tools[:5]
            ],
            "common_errors": dict(
                sorted(all_errors.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
        }

    def get_performance_analysis(self) -> Dict[str, Any]:
        """Get performance analysis across all tools.

        Returns:
            Dictionary with performance analysis data
        """
        if not self._stats_cache:
            return {"message": "No performance data available"}

        # Find slowest tools
        slow_tools = sorted(
            self._stats_cache.values(),
            key=lambda s: s.avg_execution_time_ms,
            reverse=True,
        )[:5]

        # Overall performance metrics
        all_times = [
            stats.avg_execution_time_ms for stats in self._stats_cache.values()
        ]
        avg_time = sum(all_times) / len(all_times)

        return {
            "overall_avg_execution_time_ms": avg_time,
            "slowest_tools": [
                {
                    "tool_name": stats.tool_name,
                    "avg_execution_time_ms": stats.avg_execution_time_ms,
                    "max_execution_time_ms": stats.max_execution_time_ms,
                    "total_calls": stats.total_calls,
                }
                for stats in slow_tools
            ],
            "performance_distribution": {
                "fast_tools": len(
                    [
                        s
                        for s in self._stats_cache.values()
                        if s.avg_execution_time_ms < 100
                    ]
                ),
                "medium_tools": len(
                    [
                        s
                        for s in self._stats_cache.values()
                        if 100 <= s.avg_execution_time_ms < 500
                    ]
                ),
                "slow_tools": len(
                    [
                        s
                        for s in self._stats_cache.values()
                        if s.avg_execution_time_ms >= 500
                    ]
                ),
            },
        }

    def _flush_to_disk(self) -> None:
        """Flush cached data to disk."""
        if not self._cache_dirty:
            return

        try:
            # Write events to JSONL file (append mode)
            with open(self.events_file, "w") as f:
                for event in self._event_cache:
                    f.write(json.dumps(asdict(event)) + "\n")

            # Write stats to JSON file
            stats_data = {
                tool_name: asdict(stats)
                for tool_name, stats in self._stats_cache.items()
            }
            with open(self.stats_file, "w") as f:
                json.dump(stats_data, f, indent=2)

            self._cache_dirty = False
            logger.debug("Analytics data flushed to disk")

        except Exception as e:
            logger.error(f"Failed to flush analytics data to disk: {e}")

    def cleanup_old_events(self, days: int = 30) -> int:
        """Clean up old events to manage disk space.

        Args:
            days: Number of days to keep events

        Returns:
            Number of events removed
        """
        cutoff_time = time.time() - (days * 24 * 3600)
        original_count = len(self._event_cache)

        self._event_cache = [
            event for event in self._event_cache if event.timestamp >= cutoff_time
        ]

        removed_count = original_count - len(self._event_cache)
        if removed_count > 0:
            self._cache_dirty = True
            self._flush_to_disk()
            logger.info(f"Cleaned up {removed_count} old analytics events")

        return removed_count

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report.

        Returns:
            Complete analytics report
        """
        return {
            "summary": {
                "total_tools": len(self._stats_cache),
                "total_events": len(self._event_cache),
                "report_generated": datetime.now().isoformat(),
            },
            "top_tools": [
                {
                    "tool_name": stats.tool_name,
                    "total_calls": stats.total_calls,
                    "success_rate": (
                        (stats.successful_calls / stats.total_calls)
                        if stats.total_calls > 0
                        else 0
                    ),
                    "avg_execution_time_ms": stats.avg_execution_time_ms,
                }
                for stats in self.get_top_tools(10)
            ],
            "error_analysis": self.get_error_analysis(),
            "performance_analysis": self.get_performance_analysis(),
            "recent_activity": {
                "last_24h_events": len(self.get_recent_events(24)),
                "last_7d_events": len(self.get_recent_events(24 * 7)),
            },
        }

    def __del__(self) -> None:
        """Ensure data is flushed when manager is destroyed."""
        try:
            self._flush_to_disk()
        except (OSError, IOError):
            pass  # Ignore file system errors during cleanup


# Global analytics manager instance
_analytics_manager: Optional[ToolAnalyticsManager] = None


def get_analytics_manager(analytics_dir: Optional[Path] = None) -> ToolAnalyticsManager:
    """Get or create the global analytics manager.

    Args:
        analytics_dir: Directory for analytics data (uses default if None)

    Returns:
        Analytics manager instance
    """
    global _analytics_manager

    if _analytics_manager is None:
        if analytics_dir is None:
            analytics_dir = Path.cwd() / ".lackey" / "analytics"
        _analytics_manager = ToolAnalyticsManager(analytics_dir)

    return _analytics_manager


def track_tool_usage(func: Callable[..., Any]) -> Callable[..., Any]:
    """Track tool usage automatically via decorator."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        success = False
        error_message = None

        try:
            result = func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            error_message = str(e)
            raise
        finally:
            execution_time_ms = (time.time() - start_time) * 1000

            analytics_manager = get_analytics_manager()
            analytics_manager.record_tool_usage(
                tool_name=func.__name__,
                execution_time_ms=execution_time_ms,
                success=success,
                error_message=error_message,
                parameters=kwargs,
            )

    return wrapper
