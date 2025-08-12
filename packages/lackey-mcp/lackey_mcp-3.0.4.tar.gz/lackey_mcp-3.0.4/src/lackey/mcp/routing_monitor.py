"""Logging and monitoring system for gateway routing operations.

This module provides comprehensive monitoring, logging, and performance tracking
for the gateway routing infrastructure.
"""

import json
import logging
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Log levels for routing events."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventType(Enum):
    """Types of routing events to monitor."""

    ROUTING_START = "routing_start"
    ROUTING_SUCCESS = "routing_success"
    ROUTING_FAILURE = "routing_failure"
    INTENT_CLASSIFICATION = "intent_classification"
    PARAMETER_EXTRACTION = "parameter_extraction"
    PARAMETER_VALIDATION = "parameter_validation"
    TOOL_EXECUTION = "tool_execution"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    ERROR_RECOVERY = "error_recovery"
    PERFORMANCE_THRESHOLD = "performance_threshold"


@dataclass
class RoutingEvent:
    """Represents a routing event for monitoring."""

    event_id: str
    event_type: EventType
    timestamp: float
    gateway_type: str
    operation: str
    user_query: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class PerformanceMetrics:
    """Performance metrics for routing operations."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    min_response_time_ms: float = float("inf")
    max_response_time_ms: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    intent_classification_accuracy: float = 0.0
    parameter_extraction_success_rate: float = 0.0
    error_recovery_success_rate: float = 0.0


@dataclass
class GatewayMetrics:
    """Metrics specific to a gateway."""

    gateway_type: str
    performance: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    tool_usage_counts: Dict[str, int] = field(default_factory=dict)
    intent_confidence_scores: List[float] = field(default_factory=list)
    common_errors: Dict[str, int] = field(default_factory=dict)
    response_time_history: deque = field(default_factory=lambda: deque(maxlen=1000))


class RoutingLogger:
    """Structured logging for routing operations."""

    def __init__(self, log_file_path: Optional[str] = None) -> None:
        """Initialize the routing event logger."""
        self.log_file_path = log_file_path
        self.structured_logger = self._setup_structured_logger()
        self.event_buffer: deque = deque(maxlen=10000)  # Keep last 10k events

    def _setup_structured_logger(self) -> logging.Logger:
        """Set up structured logger for routing events."""
        structured_logger = logging.getLogger("lackey.routing")
        structured_logger.setLevel(logging.DEBUG)

        # Create formatter for structured logging
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        structured_logger.addHandler(console_handler)

        # File handler if path provided
        if self.log_file_path:
            try:
                file_handler = logging.FileHandler(self.log_file_path)
                file_handler.setFormatter(formatter)
                structured_logger.addHandler(file_handler)
            except Exception as e:
                logger.warning(f"Failed to setup file logging: {e}")

        return structured_logger

    def log_event(self, event: RoutingEvent) -> None:
        """Log a routing event with structured data."""
        # Add to event buffer
        self.event_buffer.append(event)

        # Create structured log message
        log_data = {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp,
            "gateway_type": event.gateway_type,
            "operation": event.operation,
            "user_query": event.user_query[:100],  # Truncate long queries
            "success": event.success,
            "performance_metrics": event.performance_metrics,
            "metadata": event.metadata,
        }

        if event.error_message:
            log_data["error_message"] = event.error_message

        # Log with appropriate level
        log_message = f"Routing Event: {json.dumps(log_data, default=str)}"

        if event.event_type in [EventType.ROUTING_FAILURE, EventType.ERROR_RECOVERY]:
            self.structured_logger.error(log_message)
        elif event.event_type == EventType.PERFORMANCE_THRESHOLD:
            self.structured_logger.warning(log_message)
        elif event.event_type in [EventType.ROUTING_SUCCESS, EventType.TOOL_EXECUTION]:
            self.structured_logger.info(log_message)
        else:
            self.structured_logger.debug(log_message)

    def log_routing_start(
        self,
        event_id: str,
        gateway_type: str,
        user_query: str,
        parameters: Dict[str, Any],
    ) -> None:
        """Log the start of a routing operation."""
        event = RoutingEvent(
            event_id=event_id,
            event_type=EventType.ROUTING_START,
            timestamp=time.time(),
            gateway_type=gateway_type,
            operation="routing",
            user_query=user_query,
            parameters=parameters,
        )
        self.log_event(event)

    def log_routing_success(
        self,
        event_id: str,
        gateway_type: str,
        operation: str,
        user_query: str,
        parameters: Dict[str, Any],
        performance_metrics: Dict[str, float],
    ) -> None:
        """Log successful routing operation."""
        event = RoutingEvent(
            event_id=event_id,
            event_type=EventType.ROUTING_SUCCESS,
            timestamp=time.time(),
            gateway_type=gateway_type,
            operation=operation,
            user_query=user_query,
            parameters=parameters,
            performance_metrics=performance_metrics,
            success=True,
        )
        self.log_event(event)

    def log_routing_failure(
        self,
        event_id: str,
        gateway_type: str,
        user_query: str,
        parameters: Dict[str, Any],
        error_message: str,
        performance_metrics: Dict[str, float],
    ) -> None:
        """Log failed routing operation."""
        event = RoutingEvent(
            event_id=event_id,
            event_type=EventType.ROUTING_FAILURE,
            timestamp=time.time(),
            gateway_type=gateway_type,
            operation="unknown",
            user_query=user_query,
            parameters=parameters,
            performance_metrics=performance_metrics,
            success=False,
            error_message=error_message,
        )
        self.log_event(event)

    def log_intent_classification(
        self,
        event_id: str,
        gateway_type: str,
        user_query: str,
        intent: str,
        confidence: float,
        alternatives: List[Tuple[str, float]],
    ) -> None:
        """Log intent classification results."""
        event = RoutingEvent(
            event_id=event_id,
            event_type=EventType.INTENT_CLASSIFICATION,
            timestamp=time.time(),
            gateway_type=gateway_type,
            operation=intent,
            user_query=user_query,
            parameters={},
            metadata={
                "intent": intent,
                "confidence": confidence,
                "alternatives": alternatives,
            },
        )
        self.log_event(event)

    def log_parameter_extraction(
        self,
        event_id: str,
        gateway_type: str,
        operation: str,
        extracted_params: Dict[str, Any],
        inferred_params: Dict[str, Any],
        missing_params: List[str],
    ) -> None:
        """Log parameter extraction results."""
        event = RoutingEvent(
            event_id=event_id,
            event_type=EventType.PARAMETER_EXTRACTION,
            timestamp=time.time(),
            gateway_type=gateway_type,
            operation=operation,
            user_query="",
            parameters=extracted_params,
            metadata={
                "inferred_params": inferred_params,
                "missing_params": missing_params,
                "extraction_success": len(missing_params) == 0,
            },
        )
        self.log_event(event)

    def log_cache_event(
        self,
        event_id: str,
        gateway_type: str,
        operation: str,
        cache_key: str,
        hit: bool,
    ) -> None:
        """Log cache hit/miss events."""
        event = RoutingEvent(
            event_id=event_id,
            event_type=EventType.CACHE_HIT if hit else EventType.CACHE_MISS,
            timestamp=time.time(),
            gateway_type=gateway_type,
            operation=operation,
            user_query="",
            parameters={},
            metadata={"cache_key": cache_key, "cache_hit": hit},
        )
        self.log_event(event)

    def get_recent_events(
        self, limit: int = 100, event_type: Optional[EventType] = None
    ) -> List[RoutingEvent]:
        """Get recent routing events."""
        events = list(self.event_buffer)

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events[-limit:] if events else []


class PerformanceMonitor:
    """Monitors performance metrics for routing operations."""

    def __init__(self, alert_thresholds: Optional[Dict[str, float]] = None) -> None:
        """Initialize the performance monitor."""
        self.gateway_metrics: Dict[str, GatewayMetrics] = {}
        self.global_metrics = PerformanceMetrics()
        self.alert_thresholds = alert_thresholds or {
            "max_response_time_ms": 5000.0,
            "min_success_rate": 0.95,
            "max_error_rate": 0.05,
        }
        self.alerts_triggered: List[Dict[str, Any]] = []

    def record_routing_operation(
        self,
        gateway_type: str,
        operation: str,
        response_time_ms: float,
        success: bool,
        intent_confidence: Optional[float] = None,
        error_type: Optional[str] = None,
    ) -> None:
        """Record metrics for a routing operation."""
        # Initialize gateway metrics if needed
        if gateway_type not in self.gateway_metrics:
            self.gateway_metrics[gateway_type] = GatewayMetrics(
                gateway_type=gateway_type
            )

        gateway_metrics = self.gateway_metrics[gateway_type]

        # Update global metrics
        self.global_metrics.total_requests += 1
        if success:
            self.global_metrics.successful_requests += 1
        else:
            self.global_metrics.failed_requests += 1

        # Update response time metrics
        self._update_response_time_metrics(self.global_metrics, response_time_ms)
        self._update_response_time_metrics(
            gateway_metrics.performance, response_time_ms
        )

        # Update gateway-specific metrics
        gateway_metrics.performance.total_requests += 1
        if success:
            gateway_metrics.performance.successful_requests += 1
        else:
            gateway_metrics.performance.failed_requests += 1

        # Track tool usage
        if operation in gateway_metrics.tool_usage_counts:
            gateway_metrics.tool_usage_counts[operation] += 1
        else:
            gateway_metrics.tool_usage_counts[operation] = 1

        # Track intent confidence
        if intent_confidence is not None:
            gateway_metrics.intent_confidence_scores.append(intent_confidence)
            if len(gateway_metrics.intent_confidence_scores) > 1000:
                gateway_metrics.intent_confidence_scores = (
                    gateway_metrics.intent_confidence_scores[-1000:]
                )

        # Track errors
        if error_type:
            if error_type in gateway_metrics.common_errors:
                gateway_metrics.common_errors[error_type] += 1
            else:
                gateway_metrics.common_errors[error_type] = 1

        # Add to response time history
        gateway_metrics.response_time_history.append(response_time_ms)

        # Check for alerts
        self._check_performance_alerts(gateway_type)

    def _update_response_time_metrics(
        self, metrics: PerformanceMetrics, response_time_ms: float
    ) -> None:
        """Update response time metrics."""
        # Update min/max
        metrics.min_response_time_ms = min(
            metrics.min_response_time_ms, response_time_ms
        )
        metrics.max_response_time_ms = max(
            metrics.max_response_time_ms, response_time_ms
        )

        # Update average (running average)
        if metrics.total_requests > 0:
            current_avg = metrics.average_response_time_ms
            total_requests = metrics.total_requests
            new_avg = (
                (current_avg * (total_requests - 1)) + response_time_ms
            ) / total_requests
            metrics.average_response_time_ms = new_avg
        else:
            metrics.average_response_time_ms = response_time_ms

    def record_cache_event(self, gateway_type: str, hit: bool) -> None:
        """Record cache hit/miss event."""
        if gateway_type not in self.gateway_metrics:
            self.gateway_metrics[gateway_type] = GatewayMetrics(
                gateway_type=gateway_type
            )

        gateway_metrics = self.gateway_metrics[gateway_type]

        if hit:
            self.global_metrics.cache_hits += 1
            gateway_metrics.performance.cache_hits += 1
        else:
            self.global_metrics.cache_misses += 1
            gateway_metrics.performance.cache_misses += 1

    def _check_performance_alerts(self, gateway_type: str) -> None:
        """Check if performance metrics exceed alert thresholds."""
        gateway_metrics = self.gateway_metrics[gateway_type]

        # Check response time threshold
        if (
            gateway_metrics.performance.average_response_time_ms
            > self.alert_thresholds["max_response_time_ms"]
        ):
            alert = {
                "timestamp": time.time(),
                "gateway_type": gateway_type,
                "alert_type": "high_response_time",
                "value": gateway_metrics.performance.average_response_time_ms,
                "threshold": self.alert_thresholds["max_response_time_ms"],
            }
            self.alerts_triggered.append(alert)
            logger.warning(f"Performance alert: {alert}")

        # Check success rate threshold
        total_requests = gateway_metrics.performance.total_requests
        if total_requests > 10:  # Only check after sufficient requests
            success_rate = (
                gateway_metrics.performance.successful_requests / total_requests
            )
            if success_rate < self.alert_thresholds["min_success_rate"]:
                alert = {
                    "timestamp": time.time(),
                    "gateway_type": gateway_type,
                    "alert_type": "low_success_rate",
                    "value": success_rate,
                    "threshold": self.alert_thresholds["min_success_rate"],
                }
                self.alerts_triggered.append(alert)
                logger.warning(f"Performance alert: {alert}")

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        summary: Dict[str, Any] = {
            "global_metrics": asdict(self.global_metrics),
            "gateway_metrics": {},
            "alerts": self.alerts_triggered[-10:],  # Last 10 alerts
            "summary_timestamp": time.time(),
        }

        # Add calculated rates
        if self.global_metrics.total_requests > 0:
            summary["global_metrics"]["success_rate"] = (
                self.global_metrics.successful_requests
                / self.global_metrics.total_requests
            )
            summary["global_metrics"]["error_rate"] = (
                self.global_metrics.failed_requests / self.global_metrics.total_requests
            )

            total_cache_operations = (
                self.global_metrics.cache_hits + self.global_metrics.cache_misses
            )
            if total_cache_operations > 0:
                summary["global_metrics"]["cache_hit_rate"] = (
                    self.global_metrics.cache_hits / total_cache_operations
                )

        # Add gateway-specific summaries
        for gateway_type, metrics in self.gateway_metrics.items():
            gateway_summary: Dict[str, Any] = {
                "performance": asdict(metrics.performance),
                "top_tools": sorted(
                    metrics.tool_usage_counts.items(), key=lambda x: x[1], reverse=True
                )[:5],
                "average_intent_confidence": (
                    sum(metrics.intent_confidence_scores)
                    / len(metrics.intent_confidence_scores)
                    if metrics.intent_confidence_scores
                    else 0.0
                ),
                "top_errors": sorted(
                    metrics.common_errors.items(), key=lambda x: x[1], reverse=True
                )[:3],
            }

            # Add calculated rates
            if metrics.performance.total_requests > 0:
                gateway_summary["performance"]["success_rate"] = (
                    metrics.performance.successful_requests
                    / metrics.performance.total_requests
                )
                gateway_summary["performance"]["error_rate"] = (
                    metrics.performance.failed_requests
                    / metrics.performance.total_requests
                )

            summary["gateway_metrics"][gateway_type] = gateway_summary

        return summary

    def get_performance_trends(
        self, gateway_type: str, window_minutes: int = 60
    ) -> Dict[str, Any]:
        """Get performance trends for a specific time window."""
        if gateway_type not in self.gateway_metrics:
            return {}

        gateway_metrics = self.gateway_metrics[gateway_type]
        response_times = list(gateway_metrics.response_time_history)

        if not response_times:
            return {}

        # Calculate trends
        recent_times = response_times[
            -min(100, len(response_times)) :
        ]  # Last 100 operations

        return {
            "gateway_type": gateway_type,
            "recent_average_ms": sum(recent_times) / len(recent_times),
            "recent_min_ms": min(recent_times),
            "recent_max_ms": max(recent_times),
            "trend_direction": self._calculate_trend_direction(response_times),
            "sample_size": len(recent_times),
            "window_minutes": window_minutes,
        }

    def _calculate_trend_direction(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values."""
        if len(values) < 10:
            return "insufficient_data"

        # Compare first and last quarters
        quarter_size = len(values) // 4
        first_quarter_avg = sum(values[:quarter_size]) / quarter_size
        last_quarter_avg = sum(values[-quarter_size:]) / quarter_size

        diff_percent = (
            (last_quarter_avg - first_quarter_avg) / first_quarter_avg
        ) * 100

        if diff_percent > 10:
            return "increasing"
        elif diff_percent < -10:
            return "decreasing"
        else:
            return "stable"

    def reset_metrics(self) -> None:
        """Reset all performance metrics."""
        self.gateway_metrics.clear()
        self.global_metrics = PerformanceMetrics()
        self.alerts_triggered.clear()
        logger.info("Performance metrics reset")


class RoutingMonitor:
    """Main monitoring system for gateway routing operations."""

    def __init__(
        self,
        log_file_path: Optional[str] = None,
        enable_performance_monitoring: bool = True,
    ) -> None:
        """Initialize the routing monitor."""
        self.logger = RoutingLogger(log_file_path)
        self.performance_monitor = (
            PerformanceMonitor() if enable_performance_monitoring else None
        )
        self.monitoring_enabled = True
        self.event_counter = 0

    def generate_event_id(self) -> str:
        """Generate unique event ID."""
        self.event_counter += 1
        return f"routing_event_{self.event_counter}_{int(time.time())}"

    async def monitor_routing_operation(
        self,
        gateway_type: str,
        user_query: str,
        parameters: Dict[str, Any],
        operation_func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[Any, Dict[str, float]]:
        """Monitor a complete routing operation."""
        if not self.monitoring_enabled:
            return await operation_func(*args, **kwargs), {}

        event_id = self.generate_event_id()
        start_time = time.time()

        # Log routing start
        self.logger.log_routing_start(event_id, gateway_type, user_query, parameters)

        try:
            # Execute operation
            result = await operation_func(*args, **kwargs)

            # Calculate performance metrics
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            performance_metrics = {
                "response_time_ms": response_time_ms,
                "start_time": start_time,
                "end_time": end_time,
            }

            # Log success
            operation_name = getattr(operation_func, "__name__", "unknown")
            self.logger.log_routing_success(
                event_id,
                gateway_type,
                operation_name,
                user_query,
                parameters,
                performance_metrics,
            )

            # Record performance metrics
            if self.performance_monitor:
                self.performance_monitor.record_routing_operation(
                    gateway_type, operation_name, response_time_ms, True
                )

            return result, performance_metrics

        except Exception as e:
            # Calculate performance metrics for failed operation
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            performance_metrics = {
                "response_time_ms": response_time_ms,
                "start_time": start_time,
                "end_time": end_time,
            }

            # Log failure
            self.logger.log_routing_failure(
                event_id,
                gateway_type,
                user_query,
                parameters,
                str(e),
                performance_metrics,
            )

            # Record performance metrics
            if self.performance_monitor:
                self.performance_monitor.record_routing_operation(
                    gateway_type,
                    "unknown",
                    response_time_ms,
                    False,
                    error_type=type(e).__name__,
                )

            raise

    async def log_gateway_usage(
        self, gateway_type: str, operation: str, execution_time: float, success: bool
    ) -> None:
        """Log gateway usage following established monitoring patterns."""
        if not self.monitoring_enabled:
            return

        event_id = self.generate_event_id()
        response_time_ms = execution_time * 1000

        if success:
            # Log successful operation
            self.logger.log_routing_success(
                event_id,
                gateway_type,
                operation,
                f"Gateway dispatch: {operation}",
                {},
                {"response_time_ms": response_time_ms},
            )
        else:
            # Log failed operation
            self.logger.log_routing_failure(
                event_id,
                gateway_type,
                f"Gateway dispatch: {operation}",
                {},
                "Gateway dispatch failed",
                {"response_time_ms": response_time_ms},
            )

        # Record performance metrics
        if self.performance_monitor:
            self.performance_monitor.record_routing_operation(
                gateway_type, operation, response_time_ms, success
            )

    def log_intent_classification(
        self,
        gateway_type: str,
        user_query: str,
        intent: str,
        confidence: float,
        alternatives: Optional[List[Tuple[str, float]]] = None,
    ) -> None:
        """Log intent classification results."""
        if not self.monitoring_enabled:
            return

        event_id = self.generate_event_id()
        self.logger.log_intent_classification(
            event_id, gateway_type, user_query, intent, confidence, alternatives or []
        )

    def log_cache_event(
        self, gateway_type: str, operation: str, cache_key: str, hit: bool
    ) -> None:
        """Log cache hit/miss event."""
        if not self.monitoring_enabled:
            return

        event_id = self.generate_event_id()
        self.logger.log_cache_event(event_id, gateway_type, operation, cache_key, hit)

        if self.performance_monitor:
            self.performance_monitor.record_cache_event(gateway_type, hit)

    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get comprehensive monitoring summary."""
        summary: Dict[str, Any] = {
            "monitoring_enabled": self.monitoring_enabled,
            "total_events_logged": self.event_counter,
            "recent_events": len(self.logger.event_buffer),
            "timestamp": time.time(),
        }

        if self.performance_monitor:
            summary["performance"] = self.performance_monitor.get_performance_summary()

        return summary

    def disable_monitoring(self) -> None:
        """Disable monitoring temporarily."""
        self.monitoring_enabled = False
        logger.info("Routing monitoring disabled")

    def enable_monitoring(self) -> None:
        """Enable monitoring."""
        self.monitoring_enabled = True
        logger.info("Routing monitoring enabled")


# Global monitoring instance
_global_monitor = None


def get_routing_monitor() -> RoutingMonitor:
    """Get global routing monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = RoutingMonitor()
    return _global_monitor


def initialize_monitoring(
    log_file_path: Optional[str] = None, enable_performance_monitoring: bool = True
) -> RoutingMonitor:
    """Initialize global monitoring with custom configuration."""
    global _global_monitor
    _global_monitor = RoutingMonitor(log_file_path, enable_performance_monitoring)
    return _global_monitor
