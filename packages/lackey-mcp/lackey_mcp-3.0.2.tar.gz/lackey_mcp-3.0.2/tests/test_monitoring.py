"""Tests for monitoring and diagnostics functionality."""

import json
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Generator

import pytest

from lackey.monitoring import (
    LogEntry,
    LogLevel,
    MetricsCollector,
    MetricType,
    StructuredLogger,
    SystemMonitor,
    get_logger,
    get_monitor,
    initialize_monitoring,
)


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def monitor(temp_dir: Path) -> SystemMonitor:
    """Create a system monitor for testing."""
    return SystemMonitor(temp_dir / ".lackey")


@pytest.fixture
def metrics_collector() -> MetricsCollector:
    """Create a metrics collector for testing."""
    return MetricsCollector()


class TestLogEntry:
    """Test log entry functionality."""

    def test_log_entry_creation(self) -> None:
        """Test creating a log entry."""
        entry = LogEntry(
            timestamp=datetime.now(UTC),
            level=LogLevel.INFO,
            logger_name="test.logger",
            message="Test message",
            module="test_module",
            function="test_function",
            line_number=42,
            thread_id=12345,
            process_id=67890,
            context={"key": "value"},
            tags=["test", "example"],
        )

        assert entry.level == LogLevel.INFO
        assert entry.message == "Test message"
        assert entry.context["key"] == "value"
        assert "test" in entry.tags

    def test_log_entry_serialization(self) -> None:
        """Test log entry serialization."""
        entry = LogEntry(
            timestamp=datetime.now(UTC),
            level=LogLevel.ERROR,
            logger_name="test.logger",
            message="Error message",
            module="test_module",
            function="test_function",
            line_number=42,
            thread_id=12345,
            process_id=67890,
            error_type="ValueError",
            stack_trace="Stack trace here",
        )

        data = entry.to_dict()
        restored = LogEntry.from_dict(data)

        assert restored.level == entry.level
        assert restored.message == entry.message
        assert restored.error_type == entry.error_type
        assert restored.stack_trace == entry.stack_trace


class TestMetricsCollector:
    """Test metrics collection functionality."""

    def test_counter_metrics(self, metrics_collector: MetricsCollector) -> None:
        """Test counter metrics."""
        metrics_collector.increment_counter("test.counter", 5)
        metrics_collector.increment_counter("test.counter", 3)

        assert metrics_collector.counters["test.counter"] == 8

        metrics = metrics_collector.get_metrics("test.counter")
        assert len(metrics) == 2
        assert metrics[0].value == 5
        assert metrics[1].value == 8

    def test_gauge_metrics(self, metrics_collector: MetricsCollector) -> None:
        """Test gauge metrics."""
        metrics_collector.set_gauge("test.gauge", 42.5)
        metrics_collector.set_gauge("test.gauge", 37.2)

        assert metrics_collector.gauges["test.gauge"] == 37.2

        metrics = metrics_collector.get_metrics("test.gauge")
        assert len(metrics) == 2
        assert metrics[1].value == 37.2
        assert metrics[1].type == MetricType.GAUGE

    def test_histogram_metrics(self, metrics_collector: MetricsCollector) -> None:
        """Test histogram metrics."""
        values = [1.0, 2.5, 3.2, 1.8, 4.1]
        for value in values:
            metrics_collector.record_histogram("test.histogram", value)

        assert len(metrics_collector.histograms["test.histogram"]) == 5

        summary = metrics_collector.get_summary()
        hist_stats = summary["histograms"]["test.histogram"]
        assert hist_stats["count"] == 5
        assert hist_stats["min"] == 1.0
        assert hist_stats["max"] == 4.1
        assert abs(hist_stats["avg"] - 2.52) < 0.01

    def test_timer_metrics(self, metrics_collector: MetricsCollector) -> None:
        """Test timer metrics."""
        metrics_collector.record_timer("test.operation", 123.45, tags={"type": "test"})

        metrics = metrics_collector.get_metrics("test.operation")
        assert len(metrics) == 1
        assert metrics[0].value == 123.45
        assert metrics[0].type == MetricType.TIMER
        assert metrics[0].unit == "ms"
        assert metrics[0].tags["type"] == "test"

    def test_metrics_filtering(self, metrics_collector: MetricsCollector) -> None:
        """Test metrics filtering by time."""
        # Add some metrics
        metrics_collector.increment_counter("test.counter", 1)
        time.sleep(0.01)  # Small delay
        cutoff_time = datetime.now(UTC)
        time.sleep(0.01)
        metrics_collector.increment_counter("test.counter", 1)

        # Get all metrics
        all_metrics = metrics_collector.get_metrics("test.counter")
        assert len(all_metrics) == 2

        # Get metrics since cutoff
        recent_metrics = metrics_collector.get_metrics(
            "test.counter", since=cutoff_time
        )
        assert len(recent_metrics) == 1


class TestStructuredLogger:
    """Test structured logging functionality."""

    def test_logger_creation(self, monitor: SystemMonitor) -> None:
        """Test creating a structured logger."""
        logger = monitor.get_logger("test.logger")

        assert isinstance(logger, StructuredLogger)
        assert logger.name == "test.logger"
        assert logger.monitor == monitor

    def test_logging_with_context(self, monitor: SystemMonitor) -> None:
        """Test logging with context."""
        logger = monitor.get_logger("test.logger")

        # Log with context
        logger.info("Test message", user_id="123", action="test")

        # Check that log was recorded
        logs = monitor.get_logs(limit=1)
        assert len(logs) == 1
        assert logs[0].message == "Test message"
        assert logs[0].context["user_id"] == "123"
        assert logs[0].context["action"] == "test"

    def test_logger_with_persistent_context(self, monitor: SystemMonitor) -> None:
        """Test logger with persistent context."""
        base_logger = monitor.get_logger("test.logger")
        context_logger = base_logger.with_context(service="test", version="1.0")

        context_logger.info("Test message", request_id="abc123")

        logs = monitor.get_logs(limit=1)
        assert len(logs) == 1
        assert logs[0].context["service"] == "test"
        assert logs[0].context["version"] == "1.0"
        assert logs[0].context["request_id"] == "abc123"

    def test_error_logging(self, monitor: SystemMonitor) -> None:
        """Test error logging with exception details."""
        logger = monitor.get_logger("test.logger")

        try:
            raise ValueError("Test error")
        except ValueError as e:
            logger.error("An error occurred", error=e, operation="test")

        logs = monitor.get_logs(level=LogLevel.ERROR, limit=1)
        assert len(logs) == 1
        assert logs[0].level == LogLevel.ERROR
        assert logs[0].context["error_type"] == "ValueError"
        assert logs[0].context["error_message"] == "Test error"
        assert logs[0].context["operation"] == "test"


class TestSystemMonitor:
    """Test system monitoring functionality."""

    def test_monitor_initialization(self, temp_dir: Path) -> None:
        """Test monitor initialization."""
        monitor = SystemMonitor(temp_dir / ".lackey")

        assert monitor.lackey_dir == temp_dir / ".lackey"
        assert monitor.logs_dir.exists()
        assert isinstance(monitor.metrics_collector, MetricsCollector)
        assert monitor.startup_time is not None

    def test_performance_timer(self, monitor: SystemMonitor) -> None:
        """Test performance timing."""
        with monitor.timer("test_operation", component="test") as timer:
            time.sleep(0.01)  # Small delay
            assert timer.operation == "test_operation"
            assert timer.context["component"] == "test"

        # Check that timing was recorded
        metrics = monitor.metrics_collector.get_metrics("timer.test_operation")
        assert len(metrics) == 1
        assert metrics[0].value > 0  # Should have some duration
        assert metrics[0].tags["component"] == "test"

    def test_operation_recording(self, monitor: SystemMonitor) -> None:
        """Test operation recording."""
        # Record successful operation
        monitor.record_operation("test_op", success=True, user="test_user")

        # Record failed operation
        monitor.record_operation("test_op", success=False, user="test_user")

        # Check metrics
        success_metrics = monitor.metrics_collector.get_metrics(
            "operations.test_op.success"
        )
        failure_metrics = monitor.metrics_collector.get_metrics(
            "operations.test_op.failure"
        )

        assert len(success_metrics) == 1
        assert len(failure_metrics) == 1
        assert success_metrics[0].tags["user"] == "test_user"

    def test_task_operation_recording(self, monitor: SystemMonitor) -> None:
        """Test task-specific operation recording."""
        monitor.record_task_operation("create", "task123", "project456", success=True)

        metrics = monitor.metrics_collector.get_metrics(
            "operations.task.create.success"
        )
        assert len(metrics) == 1
        assert metrics[0].tags["task_id"] == "task123"
        assert metrics[0].tags["project_id"] == "project456"

    def test_log_filtering(self, monitor: SystemMonitor) -> None:
        """Test log filtering functionality."""
        logger = monitor.get_logger("test.logger")

        # Add various log levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        # Test level filtering
        error_logs = monitor.get_logs(level=LogLevel.ERROR)
        assert len(error_logs) == 1
        assert error_logs[0].message == "Error message"

        # Test logger name filtering
        test_logs = monitor.get_logs(logger_name="test.logger")
        assert len(test_logs) == 4

        # Test limit
        limited_logs = monitor.get_logs(limit=2)
        assert len(limited_logs) == 2

    def test_error_summary(self, monitor: SystemMonitor) -> None:
        """Test error summary generation."""
        logger = monitor.get_logger("test.module")

        # Generate some errors
        logger.error("Database error", error_type="DatabaseError")
        logger.error("Network error", error_type="NetworkError")
        logger.warning("Performance warning")

        summary = monitor.get_error_summary()

        assert summary["total_errors"] == 2
        assert summary["total_warnings"] == 1
        assert "test.module" in summary["error_modules"]
        assert len(summary["recent_errors"]) == 2

    def test_performance_summary(self, monitor: SystemMonitor) -> None:
        """Test performance summary generation."""
        # Record some operations
        with monitor.timer("operation1"):
            time.sleep(0.01)

        with monitor.timer("operation2"):
            time.sleep(0.005)

        with monitor.timer("operation1"):
            time.sleep(0.015)

        summary = monitor.get_performance_summary()

        assert summary["total_operations"] == 3
        assert "operation1" in summary["operation_stats"]
        assert "operation2" in summary["operation_stats"]

        op1_stats = summary["operation_stats"]["operation1"]
        assert op1_stats["count"] == 2
        assert op1_stats["min_ms"] > 0
        assert op1_stats["max_ms"] > op1_stats["min_ms"]

    def test_system_health(self, monitor: SystemMonitor) -> None:
        """Test system health assessment."""
        health = monitor.get_system_health()

        assert "status" in health
        assert "health_score" in health
        assert "uptime_seconds" in health
        assert "uptime_human" in health
        assert health["health_score"] >= 0
        assert health["health_score"] <= 100

        # Should start healthy
        assert health["status"] in ["healthy", "warning", "critical"]

    def test_diagnostics_export(self, monitor: SystemMonitor, temp_dir: Path) -> None:
        """Test diagnostics export."""
        logger = monitor.get_logger("test.logger")
        logger.info("Test log entry")

        # Export diagnostics
        output_file = temp_dir / "diagnostics.json"
        diagnostics = monitor.export_diagnostics(output_file)

        # Check structure
        assert "export_timestamp" in diagnostics
        assert "system_info" in diagnostics
        assert "health" in diagnostics
        assert "errors" in diagnostics
        assert "performance" in diagnostics
        assert "recent_logs" in diagnostics
        assert "metrics" in diagnostics

        # Check file was created
        assert output_file.exists()

        # Verify file contents
        with open(output_file) as f:
            file_data = json.load(f)

        assert file_data == diagnostics

    def test_data_cleanup(self, monitor: SystemMonitor) -> None:
        """Test old data cleanup."""
        # Add some metrics
        monitor.metrics_collector.increment_counter("test.counter", 1)

        # Cleanup (should not remove recent data)
        stats = monitor.cleanup_old_data(days_to_keep=1)

        assert "cleaned_metrics" in stats
        assert "cutoff_time" in stats
        assert stats["cleaned_metrics"] >= 0


class TestGlobalMonitoring:
    """Test global monitoring functions."""

    def test_initialize_monitoring(self, temp_dir: Path) -> None:
        """Test global monitoring initialization."""
        monitor = initialize_monitoring(temp_dir / ".lackey")

        assert isinstance(monitor, SystemMonitor)
        assert get_monitor() == monitor

    def test_get_logger_with_monitoring(self, temp_dir: Path) -> None:
        """Test getting logger with monitoring initialized."""
        initialize_monitoring(temp_dir / ".lackey")

        logger = get_logger("test.logger")
        assert isinstance(logger, StructuredLogger)
        assert logger.name == "test.logger"

    def test_get_logger_without_monitoring(self) -> None:
        """Test getting logger without monitoring initialized."""
        # Reset global monitor
        import lackey.monitoring

        lackey.monitoring._monitor = None

        logger = get_logger("test.logger")

        # Should get basic logger fallback
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")


class TestMonitoringIntegration:
    """Test monitoring integration scenarios."""

    def test_high_error_rate_health_impact(self, monitor: SystemMonitor) -> None:
        """Test that high error rates impact health score."""
        logger = monitor.get_logger("test.logger")

        # Generate many errors
        for i in range(15):
            logger.error(f"Error {i}")

        health = monitor.get_system_health()

        # Health score should be reduced
        assert health["health_score"] < 100
        assert health["recent_errors"] == 15

    def test_critical_error_health_impact(self, monitor: SystemMonitor) -> None:
        """Test that critical errors severely impact health."""
        logger = monitor.get_logger("test.logger")

        logger.critical("Critical system error")

        health = monitor.get_system_health()

        # Health score should be significantly reduced
        assert health["health_score"] <= 70
        assert health["critical_errors"] == 1

    def test_concurrent_logging(self, monitor: SystemMonitor) -> None:
        """Test concurrent logging operations."""
        import threading
        from typing import Dict

        def log_worker(worker_id: int) -> None:
            logger = monitor.get_logger(f"worker.{worker_id}")
            for i in range(10):
                logger.info(
                    f"Worker {worker_id} message {i}", worker_id=worker_id, message_id=i
                )

        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=log_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Check that all logs were recorded
        logs = monitor.get_logs()
        assert len(logs) == 30  # 3 workers * 10 messages each

        # Check that logs from different workers are present
        worker_logs: Dict[int, int] = {}
        for log in logs:
            worker_id = log.context.get("worker_id")
            if worker_id is not None:
                worker_logs[worker_id] = worker_logs.get(worker_id, 0) + 1

        assert len(worker_logs) == 3
        for count in worker_logs.values():
            assert count == 10


if __name__ == "__main__":
    pytest.main([__file__])
