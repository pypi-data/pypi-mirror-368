"""Comprehensive logging, monitoring, and diagnostics system for Lackey."""

import json
import logging
import logging.handlers
import os
import time
from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Union, cast

from .file_ops import atomic_write


class LogLevel(Enum):
    """Log level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class MetricType(Enum):
    """Metric type enumeration."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class LogEntry:
    """Represents a structured log entry."""

    timestamp: datetime
    level: LogLevel
    logger_name: str
    message: str
    module: str
    function: str
    line_number: int
    thread_id: int
    process_id: int
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    duration_ms: Optional[float] = None
    error_type: Optional[str] = None
    stack_trace: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "logger_name": self.logger_name,
            "message": self.message,
            "module": self.module,
            "function": self.function,
            "line_number": self.line_number,
            "thread_id": self.thread_id,
            "process_id": self.process_id,
            "context": self.context,
            "tags": self.tags,
            "duration_ms": self.duration_ms,
            "error_type": self.error_type,
            "stack_trace": self.stack_trace,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LogEntry":
        """Create from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            level=LogLevel(data["level"]),
            logger_name=data["logger_name"],
            message=data["message"],
            module=data["module"],
            function=data["function"],
            line_number=data["line_number"],
            thread_id=data["thread_id"],
            process_id=data["process_id"],
            context=data.get("context", {}),
            tags=data.get("tags", []),
            duration_ms=data.get("duration_ms"),
            error_type=data.get("error_type"),
            stack_trace=data.get("stack_trace"),
        )


@dataclass
class Metric:
    """Represents a system metric."""

    name: str
    type: MetricType
    value: Union[int, float]
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    unit: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "type": self.type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "unit": self.unit,
        }


@dataclass
class PerformanceTimer:
    """Tracks performance timing for operations."""

    operation: str
    start_time: float
    end_time: Optional[float] = None
    context: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> Optional[float]:
        """Get duration in milliseconds."""
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000

    def finish(self) -> float:
        """Mark timer as finished and return duration."""
        self.end_time = time.perf_counter()
        duration = self.duration_ms
        if duration is None:
            return 0.0
        return duration


class StructuredLogger:
    """Enhanced logger with structured logging capabilities."""

    def __init__(self, name: str, monitor: "SystemMonitor"):
        """Initialize structured logger.

        Args:
            name: Logger name
            monitor: System monitor instance
        """
        self.name = name
        self.monitor = monitor
        self.logger = logging.getLogger(name)
        self._context: Dict[str, Any] = {}

    def with_context(self, **context: Any) -> "StructuredLogger":
        """Create logger with additional context.

        Args:
            **context: Context key-value pairs

        Returns:
            New logger instance with context
        """
        new_logger = StructuredLogger(self.name, self.monitor)
        new_logger._context = {**self._context, **context}
        return new_logger

    def debug(self, message: str, **context: Any) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, context)

    def info(self, message: str, **context: Any) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, message, context)

    def warning(self, message: str, **context: Any) -> None:
        """Log warning message."""
        self._log(LogLevel.WARNING, message, context)

    def error(
        self, message: str, error: Optional[Exception] = None, **context: Any
    ) -> None:
        """Log error message."""
        if error:
            context["error_type"] = type(error).__name__
            context["error_message"] = str(error)
        self._log(LogLevel.ERROR, message, context)

    def critical(
        self, message: str, error: Optional[Exception] = None, **context: Any
    ) -> None:
        """Log critical message."""
        if error:
            context["error_type"] = type(error).__name__
            context["error_message"] = str(error)
        self._log(LogLevel.CRITICAL, message, context)

    def _log(self, level: LogLevel, message: str, context: Dict[str, Any]) -> None:
        """Log internal monitoring data."""
        import inspect
        import threading

        # Get caller information
        current_frame = inspect.currentframe()
        if current_frame and current_frame.f_back and current_frame.f_back.f_back:
            frame = current_frame.f_back.f_back
            module = frame.f_globals.get("__name__", "unknown")
            function = frame.f_code.co_name
            line_number = frame.f_lineno
        else:
            module = "unknown"
            function = "unknown"
            line_number = 0

        # Create log entry
        entry = LogEntry(
            timestamp=datetime.now(UTC),
            level=level,
            logger_name=self.name,
            message=message,
            module=module,
            function=function,
            line_number=line_number,
            thread_id=threading.get_ident(),
            process_id=os.getpid(),
            context={**self._context, **context},
        )

        # Send to monitor
        self.monitor.record_log_entry(entry)

        # Also log to standard logger
        std_level = getattr(logging, level.value)
        self.logger.log(std_level, message, extra={"structured_entry": entry})


class MetricsCollector:
    """Collects and manages system metrics."""

    def __init__(self) -> None:
        """Initialize metrics collector."""
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()

    def increment_counter(
        self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name
            value: Value to increment by
            tags: Optional tags
        """
        with self._lock:
            self.counters[name] += value
            metric = Metric(
                name=name,
                type=MetricType.COUNTER,
                value=self.counters[name],
                timestamp=datetime.now(UTC),
                tags=tags or {},
            )
            self.metrics[name].append(metric)

    def set_gauge(
        self, name: str, value: float, tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name
            value: Gauge value
            tags: Optional tags
        """
        with self._lock:
            self.gauges[name] = value
            metric = Metric(
                name=name,
                type=MetricType.GAUGE,
                value=value,
                timestamp=datetime.now(UTC),
                tags=tags or {},
            )
            self.metrics[name].append(metric)

    def record_histogram(
        self, name: str, value: float, tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a histogram value.

        Args:
            name: Metric name
            value: Value to record
            tags: Optional tags
        """
        with self._lock:
            self.histograms[name].append(value)
            metric = Metric(
                name=name,
                type=MetricType.HISTOGRAM,
                value=value,
                timestamp=datetime.now(UTC),
                tags=tags or {},
            )
            self.metrics[name].append(metric)

    def record_timer(
        self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a timer metric.

        Args:
            name: Metric name
            duration_ms: Duration in milliseconds
            tags: Optional tags
        """
        with self._lock:
            metric = Metric(
                name=name,
                type=MetricType.TIMER,
                value=duration_ms,
                timestamp=datetime.now(UTC),
                tags=tags or {},
                unit="ms",
            )
            self.metrics[name].append(metric)

    def get_metrics(
        self, name: Optional[str] = None, since: Optional[datetime] = None
    ) -> List[Metric]:
        """Get metrics with optional filtering.

        Args:
            name: Optional metric name filter
            since: Optional time filter

        Returns:
            List of matching metrics
        """
        with self._lock:
            if name:
                metrics = self.metrics.get(name, [])
            else:
                metrics = []
                for metric_list in self.metrics.values():
                    metrics.extend(metric_list)

            if since:
                metrics = [m for m in metrics if m.timestamp >= since]

            return sorted(metrics, key=lambda m: m.timestamp)

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary.

        Returns:
            Dictionary with metrics summary
        """
        with self._lock:
            summary: Dict[str, Any] = {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histograms": {},
                "total_metrics": sum(len(metrics) for metrics in self.metrics.values()),
            }

            # Calculate histogram statistics
            for name, values in self.histograms.items():
                if values:
                    summary["histograms"][name] = {
                        "count": len(values),
                        "min": min(values),
                        "max": max(values),
                        "avg": sum(values) / len(values),
                    }

            return summary


class SystemMonitor:
    """Comprehensive system monitoring and diagnostics."""

    def __init__(self, lackey_dir: Path, max_log_entries: int = 10000):
        """Initialize system monitor.

        Args:
            lackey_dir: Lackey data directory
            max_log_entries: Maximum log entries to keep in memory
        """
        self.lackey_dir = Path(lackey_dir)
        self.logs_dir = self.lackey_dir / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self.max_log_entries = max_log_entries
        self.log_entries: deque = deque(maxlen=max_log_entries)
        self.metrics_collector = MetricsCollector()
        self.active_timers: Dict[str, PerformanceTimer] = {}

        self._lock = Lock()
        self._setup_file_logging()

        # Track system startup
        self.startup_time = datetime.now(UTC)
        self.metrics_collector.set_gauge("system.startup_timestamp", time.time())

    def _setup_file_logging(self) -> None:
        """Set up file-based logging."""
        # Create rotating file handler
        log_file = self.logs_dir / "lackey.log"
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )

        # JSON formatter for structured logs
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
            '"logger": "%(name)s", "message": "%(message)s"}'
        )
        handler.setFormatter(formatter)

        # Add to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)

    def get_logger(self, name: str) -> StructuredLogger:
        """Get a structured logger instance.

        Args:
            name: Logger name

        Returns:
            Structured logger instance
        """
        return StructuredLogger(name, self)

    def record_log_entry(self, entry: LogEntry) -> None:
        """Record a log entry.

        Args:
            entry: Log entry to record
        """
        with self._lock:
            self.log_entries.append(entry)

            # Update metrics
            self.metrics_collector.increment_counter(
                f"logs.{entry.level.value.lower()}",
                tags={"logger": entry.logger_name, "module": entry.module},
            )

            if entry.duration_ms is not None:
                self.metrics_collector.record_timer(
                    f"operation.{entry.function}",
                    entry.duration_ms,
                    tags={"module": entry.module},
                )

    @contextmanager
    def timer(self, operation: str, **context: Any) -> Any:
        """Context manager for timing operations.

        Args:
            operation: Operation name
            **context: Additional context

        Yields:
            Performance timer instance
        """
        timer = PerformanceTimer(
            operation=operation,
            start_time=time.perf_counter(),
            context=context,
        )

        timer_id = f"{operation}_{id(timer)}"
        self.active_timers[timer_id] = timer

        try:
            yield timer
        finally:
            duration = timer.finish()
            self.active_timers.pop(timer_id, None)

            # Record timing metric
            self.metrics_collector.record_timer(
                f"timer.{operation}",
                duration,
                tags=context,
            )

    def record_operation(
        self, operation: str, success: bool = True, **context: Any
    ) -> None:
        """Record an operation completion.

        Args:
            operation: Operation name
            success: Whether operation succeeded
            **context: Additional context
        """
        status = "success" if success else "failure"
        self.metrics_collector.increment_counter(
            f"operations.{operation}.{status}",
            tags=context,
        )

    def record_task_operation(
        self, operation: str, task_id: str, project_id: str, success: bool = True
    ) -> None:
        """Record a task-specific operation.

        Args:
            operation: Operation name
            task_id: Task ID
            project_id: Project ID
            success: Whether operation succeeded
        """
        self.record_operation(
            f"task.{operation}",
            success=success,
            task_id=task_id,
            project_id=project_id,
        )

    def record_project_operation(
        self, operation: str, project_id: str, success: bool = True
    ) -> None:
        """Record a project-specific operation.

        Args:
            operation: Operation name
            project_id: Project ID
            success: Whether operation succeeded
        """
        self.record_operation(
            f"project.{operation}",
            success=success,
            project_id=project_id,
        )

    def get_logs(
        self,
        level: Optional[LogLevel] = None,
        logger_name: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> List[LogEntry]:
        """Get log entries with filtering.

        Args:
            level: Optional log level filter
            logger_name: Optional logger name filter
            since: Optional time filter
            limit: Optional result limit

        Returns:
            List of matching log entries
        """
        with self._lock:
            entries = list(self.log_entries)

        # Apply filters
        if level:
            entries = [e for e in entries if e.level == level]

        if logger_name:
            entries = [e for e in entries if e.logger_name == logger_name]

        if since:
            entries = [e for e in entries if e.timestamp >= since]

        # Sort by timestamp (newest first)
        entries.sort(key=lambda e: e.timestamp, reverse=True)

        # Apply limit
        if limit:
            entries = entries[:limit]

        return entries

    def get_error_summary(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """Get error summary statistics.

        Args:
            since: Optional time filter

        Returns:
            Error summary dictionary
        """
        error_entries = self.get_logs(level=LogLevel.ERROR, since=since)
        warning_entries = self.get_logs(level=LogLevel.WARNING, since=since)

        # Group by error type
        error_types: Dict[str, int] = defaultdict(int)
        for entry in error_entries:
            error_type = entry.error_type or "Unknown"
            error_types[error_type] += 1

        # Group by module
        error_modules: Dict[str, int] = defaultdict(int)
        for entry in error_entries + warning_entries:
            error_modules[entry.logger_name] += 1

        return {
            "total_errors": len(error_entries),
            "total_warnings": len(warning_entries),
            "error_types": dict(error_types),
            "error_modules": dict(error_modules),
            "recent_errors": [e.to_dict() for e in error_entries[:10]],
        }

    def get_performance_summary(
        self, since: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get performance summary.

        Args:
            since: Optional time filter

        Returns:
            Performance summary dictionary
        """
        timer_metrics = [
            m
            for m in self.metrics_collector.get_metrics(since=since)
            if m.type == MetricType.TIMER
        ]

        # Group by operation
        operations = defaultdict(list)
        for metric in timer_metrics:
            operation = metric.name.replace("timer.", "")
            operations[operation].append(metric.value)

        # Calculate statistics
        operation_stats = {}
        for operation, durations in operations.items():
            if durations:
                operation_stats[operation] = {
                    "count": len(durations),
                    "min_ms": min(durations),
                    "max_ms": max(durations),
                    "avg_ms": sum(durations) / len(durations),
                    "total_ms": sum(durations),
                }

        return {
            "total_operations": len(timer_metrics),
            "operation_stats": operation_stats,
            "active_timers": len(self.active_timers),
        }

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status.

        Returns:
            System health dictionary
        """
        now = datetime.now(UTC)
        uptime = now - self.startup_time

        # Get recent errors (last hour)
        recent_errors = self.get_logs(
            level=LogLevel.ERROR, since=now - timedelta(hours=1)
        )

        # Calculate health score (0-100)
        health_score = 100
        if len(recent_errors) > 10:
            health_score -= min(50, len(recent_errors) * 2)

        # Check for critical errors
        critical_errors = self.get_logs(
            level=LogLevel.CRITICAL, since=now - timedelta(hours=24)
        )
        if critical_errors:
            health_score -= 30

        # Determine status
        if health_score >= 90:
            status = "healthy"
        elif health_score >= 70:
            status = "warning"
        else:
            status = "critical"

        return {
            "status": status,
            "health_score": max(0, health_score),
            "uptime_seconds": uptime.total_seconds(),
            "uptime_human": str(uptime),
            "recent_errors": len(recent_errors),
            "critical_errors": len(critical_errors),
            "total_log_entries": len(self.log_entries),
            "metrics_summary": self.metrics_collector.get_summary(),
        }

    def export_diagnostics(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Export comprehensive diagnostics data.

        Args:
            output_file: Optional file to write diagnostics to

        Returns:
            Diagnostics data dictionary
        """
        now = datetime.now(UTC)

        diagnostics = {
            "export_timestamp": now.isoformat(),
            "system_info": {
                "startup_time": self.startup_time.isoformat(),
                "uptime_seconds": (now - self.startup_time).total_seconds(),
                "lackey_dir": str(self.lackey_dir),
                "logs_dir": str(self.logs_dir),
            },
            "health": self.get_system_health(),
            "errors": self.get_error_summary(since=now - timedelta(days=1)),
            "performance": self.get_performance_summary(since=now - timedelta(hours=1)),
            "recent_logs": [e.to_dict() for e in self.get_logs(limit=100)],
            "metrics": [
                m.to_dict()
                for m in self.metrics_collector.get_metrics(
                    since=now - timedelta(hours=1)
                )
            ],
        }

        if output_file:
            with atomic_write(str(output_file)) as f:
                f.write_content(json.dumps(diagnostics, indent=2))

        return diagnostics

    def cleanup_old_data(self, days_to_keep: int = 7) -> Dict[str, Any]:
        """Clean up old monitoring data.

        Args:
            days_to_keep: Number of days of data to keep

        Returns:
            Cleanup statistics
        """
        cutoff_time = datetime.now(UTC) - timedelta(days=days_to_keep)

        # Clean up metrics
        cleaned_metrics = 0
        for name, metrics in self.metrics_collector.metrics.items():
            original_count = len(metrics)
            self.metrics_collector.metrics[name] = [
                m for m in metrics if m.timestamp >= cutoff_time
            ]
            cleaned_metrics += original_count - len(
                self.metrics_collector.metrics[name]
            )

        return {
            "cleaned_metrics": cleaned_metrics,
            "cutoff_time": cutoff_time.isoformat(),
        }


# Global monitor instance
_monitor: Optional[SystemMonitor] = None


def initialize_monitoring(lackey_dir: Path) -> SystemMonitor:
    """Initialize global monitoring system.

    Args:
        lackey_dir: Lackey data directory

    Returns:
        System monitor instance
    """
    global _monitor
    _monitor = SystemMonitor(lackey_dir)
    return _monitor


def get_monitor() -> Optional[SystemMonitor]:
    """Get global monitor instance.

    Returns:
        System monitor instance or None if not initialized
    """
    return _monitor


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name

    Returns:
        Structured logger instance
    """
    if _monitor is None:
        # Fallback to basic logger if monitoring not initialized
        class BasicLogger:
            def __init__(self, name: str):
                self.logger = logging.getLogger(name)

            def debug(self, message: str, **context: Any) -> None:
                self.logger.debug(message)

            def info(self, message: str, **context: Any) -> None:
                self.logger.info(message)

            def warning(self, message: str, **context: Any) -> None:
                self.logger.warning(message)

            def error(
                self, message: str, error: Optional[Exception] = None, **context: Any
            ) -> None:
                self.logger.error(message)

            def critical(
                self, message: str, error: Optional[Exception] = None, **context: Any
            ) -> None:
                self.logger.critical(message)

            def with_context(self, **context: Any) -> "BasicLogger":
                return self

        return cast(StructuredLogger, BasicLogger(name))

    return _monitor.get_logger(name)
