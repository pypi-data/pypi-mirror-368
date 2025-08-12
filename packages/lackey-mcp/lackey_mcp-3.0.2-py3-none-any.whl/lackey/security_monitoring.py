"""Security logging and monitoring system for Lackey.

This module provides comprehensive security event logging, monitoring,
alerting, and analysis capabilities for detecting and responding to
security threats and anomalies.
"""

import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from lackey.security import SecurityEvent, get_security_manager


class AlertSeverity(Enum):
    """Alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MonitoringRule(Enum):
    """Predefined monitoring rules."""

    FAILED_LOGIN_THRESHOLD = "failed_login_threshold"
    RATE_LIMIT_VIOLATIONS = "rate_limit_violations"
    SUSPICIOUS_FILE_ACCESS = "suspicious_file_access"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    UNUSUAL_API_USAGE = "unusual_api_usage"
    BRUTE_FORCE_ATTACK = "brute_force_attack"
    DATA_EXFILTRATION = "data_exfiltration"
    CONFIGURATION_CHANGES = "configuration_changes"


@dataclass
class SecurityAlert:
    """Security alert information."""

    id: str
    rule_name: str
    severity: AlertSeverity
    title: str
    description: str
    timestamp: float = field(default_factory=time.time)

    # Event details
    triggering_events: List[SecurityEvent] = field(default_factory=list)
    affected_resources: List[str] = field(default_factory=list)
    source_ips: Set[str] = field(default_factory=set)
    user_ids: Set[str] = field(default_factory=set)

    # Alert status
    is_acknowledged: bool = False
    is_resolved: bool = False
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "id": self.id,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "timestamp": self.timestamp,
            "event_count": len(self.triggering_events),
            "affected_resources": self.affected_resources,
            "source_ips": list(self.source_ips),
            "user_ids": list(self.user_ids),
            "is_acknowledged": self.is_acknowledged,
            "is_resolved": self.is_resolved,
            "acknowledged_by": self.acknowledged_by,
            "resolved_by": self.resolved_by,
            "resolution_notes": self.resolution_notes,
            "metadata": self.metadata,
        }


@dataclass
class MonitoringMetrics:
    """Security monitoring metrics."""

    # Event counts by type
    event_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Event counts by severity
    severity_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Time-based metrics
    events_per_hour: Dict[int, int] = field(default_factory=lambda: defaultdict(int))
    events_per_day: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Source-based metrics
    events_by_ip: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    events_by_user: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # Alert metrics
    alerts_generated: int = 0
    alerts_acknowledged: int = 0
    alerts_resolved: int = 0

    # Performance metrics
    avg_response_time: float = 0.0
    peak_events_per_minute: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "event_counts": dict(self.event_counts),
            "severity_counts": dict(self.severity_counts),
            "events_per_hour": dict(self.events_per_hour),
            "events_per_day": dict(self.events_per_day),
            "top_source_ips": dict(
                sorted(self.events_by_ip.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            "top_users": dict(
                sorted(self.events_by_user.items(), key=lambda x: x[1], reverse=True)[
                    :10
                ]
            ),
            "alerts_generated": self.alerts_generated,
            "alerts_acknowledged": self.alerts_acknowledged,
            "alerts_resolved": self.alerts_resolved,
            "avg_response_time": self.avg_response_time,
            "peak_events_per_minute": self.peak_events_per_minute,
        }


class SecurityMonitor:
    """Comprehensive security monitoring and alerting system."""

    def __init__(self, log_dir: str = ".lackey/logs"):
        """Initialize security monitor."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.security_manager = get_security_manager()

        # Event storage
        self.recent_events: deque = deque(maxlen=10000)  # Keep last 10k events
        self.alerts: Dict[str, SecurityAlert] = {}
        self.metrics = MonitoringMetrics()

        # Monitoring rules configuration
        self.monitoring_rules = self._setup_monitoring_rules()

        # Alert handlers
        self.alert_handlers: List[Callable[[SecurityAlert], None]] = []

        # Setup logging
        self._setup_security_logging()

        # Event processing state
        self.last_metrics_update = time.time()
        self.event_buffer: List[SecurityEvent] = []

    def _setup_monitoring_rules(self) -> Dict[MonitoringRule, Dict[str, Any]]:
        """Set up default monitoring rules."""
        return {
            MonitoringRule.FAILED_LOGIN_THRESHOLD: {
                "threshold": 5,
                "time_window_minutes": 15,
                "severity": AlertSeverity.HIGH,
                "description": "Multiple failed login attempts detected",
            },
            MonitoringRule.RATE_LIMIT_VIOLATIONS: {
                "threshold": 10,
                "time_window_minutes": 5,
                "severity": AlertSeverity.MEDIUM,
                "description": "Excessive rate limit violations detected",
            },
            MonitoringRule.SUSPICIOUS_FILE_ACCESS: {
                "threshold": 3,
                "time_window_minutes": 10,
                "severity": AlertSeverity.HIGH,
                "description": "Suspicious file access patterns detected",
            },
            MonitoringRule.PRIVILEGE_ESCALATION: {
                "threshold": 1,
                "time_window_minutes": 60,
                "severity": AlertSeverity.CRITICAL,
                "description": "Potential privilege escalation attempt detected",
            },
            MonitoringRule.UNUSUAL_API_USAGE: {
                "threshold": 100,
                "time_window_minutes": 60,
                "severity": AlertSeverity.MEDIUM,
                "description": "Unusual API usage patterns detected",
            },
            MonitoringRule.BRUTE_FORCE_ATTACK: {
                "threshold": 20,
                "time_window_minutes": 30,
                "severity": AlertSeverity.CRITICAL,
                "description": "Potential brute force attack detected",
            },
            MonitoringRule.DATA_EXFILTRATION: {
                "threshold": 5,
                "time_window_minutes": 30,
                "severity": AlertSeverity.CRITICAL,
                "description": "Potential data exfiltration detected",
            },
            MonitoringRule.CONFIGURATION_CHANGES: {
                "threshold": 1,
                "time_window_minutes": 5,
                "severity": AlertSeverity.MEDIUM,
                "description": "Security configuration changes detected",
            },
        }

    def _setup_security_logging(self) -> None:
        """Set up security-specific logging."""
        # Create security log file
        security_log_file = self.log_dir / "security.log"

        # Configure security logger
        security_logger = logging.getLogger("lackey.security.monitor")
        security_logger.setLevel(logging.INFO)

        # Remove existing handlers
        security_logger.handlers.clear()

        # File handler for security events
        file_handler = logging.FileHandler(security_log_file)
        file_formatter = logging.Formatter(
            "%(asctime)s - SECURITY - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        security_logger.addHandler(file_handler)

        # Console handler for critical events
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            "🚨 SECURITY ALERT - %(asctime)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.ERROR)
        security_logger.addHandler(console_handler)

        self.security_logger = security_logger

    def process_security_event(self, event: SecurityEvent) -> None:
        """Process a security event and check for alerts."""
        # Add to recent events
        self.recent_events.append(event)

        # Update metrics
        self._update_metrics(event)

        # Log the event
        self._log_security_event(event)

        # Check monitoring rules
        self._check_monitoring_rules(event)

        # Add to buffer for batch processing
        self.event_buffer.append(event)

        # Process buffer if it's getting full
        if len(self.event_buffer) >= 100:
            self._process_event_buffer()

    def _update_metrics(self, event: SecurityEvent) -> None:
        """Update monitoring metrics with new event."""
        # Event type counts
        self.metrics.event_counts[event.event_type] += 1

        # Severity counts
        self.metrics.severity_counts[event.severity] += 1

        # Time-based metrics
        event_time = datetime.fromtimestamp(event.timestamp)
        hour_key = event_time.hour
        day_key = event_time.strftime("%Y-%m-%d")

        self.metrics.events_per_hour[hour_key] += 1
        self.metrics.events_per_day[day_key] += 1

        # Source-based metrics
        if event.source_ip:
            self.metrics.events_by_ip[event.source_ip] += 1

        if "user_id" in event.metadata:
            self.metrics.events_by_user[event.metadata["user_id"]] += 1

    def _log_security_event(self, event: SecurityEvent) -> None:
        """Log security event to file."""
        log_entry = {
            "timestamp": event.timestamp,
            "event_type": event.event_type,
            "severity": event.severity,
            "message": event.message,
            "source_ip": event.source_ip,
            "user_agent": event.user_agent,
            "metadata": event.metadata,
        }

        log_message = json.dumps(log_entry)

        if event.severity == "critical":
            self.security_logger.critical(log_message)
        elif event.severity == "high":
            self.security_logger.error(log_message)
        elif event.severity == "medium":
            self.security_logger.warning(log_message)
        else:
            self.security_logger.info(log_message)

    def _check_monitoring_rules(self, event: SecurityEvent) -> None:
        """Check if event triggers any monitoring rules."""
        current_time = time.time()

        for rule, config in self.monitoring_rules.items():
            if self._should_check_rule(rule, event):
                # Get relevant events within time window
                time_window_start = current_time - (config["time_window_minutes"] * 60)
                relevant_events = [
                    e
                    for e in self.recent_events
                    if e.timestamp >= time_window_start
                    and self._event_matches_rule(rule, e)
                ]

                # Check if threshold is exceeded
                if len(relevant_events) >= config["threshold"]:
                    self._generate_alert(rule, config, relevant_events)

    def _should_check_rule(self, rule: MonitoringRule, event: SecurityEvent) -> bool:
        """Check if a rule should be evaluated for this event."""
        rule_event_mappings = {
            MonitoringRule.FAILED_LOGIN_THRESHOLD: [
                "login_failed",
                "authentication_failed",
            ],
            MonitoringRule.RATE_LIMIT_VIOLATIONS: [
                "rate_limit_violation",
                "rate_limit_exceeded",
            ],
            MonitoringRule.SUSPICIOUS_FILE_ACCESS: [
                "file_access_denied",
                "path_traversal_attempt",
            ],
            MonitoringRule.PRIVILEGE_ESCALATION: [
                "authorization_denied",
                "permission_escalation",
            ],
            MonitoringRule.UNUSUAL_API_USAGE: ["api_request", "endpoint_access"],
            MonitoringRule.BRUTE_FORCE_ATTACK: [
                "login_failed",
                "api_key_authentication_failed",
            ],
            MonitoringRule.DATA_EXFILTRATION: [
                "bulk_data_access",
                "large_file_download",
            ],
            MonitoringRule.CONFIGURATION_CHANGES: [
                "config_saved",
                "config_deleted",
                "security_config_changed",
            ],
        }

        relevant_events = rule_event_mappings.get(rule, [])
        return event.event_type in relevant_events

    def _event_matches_rule(self, rule: MonitoringRule, event: SecurityEvent) -> bool:
        """Check if an event matches a specific monitoring rule."""
        return self._should_check_rule(rule, event)

    def _generate_alert(
        self,
        rule: MonitoringRule,
        config: Dict[str, Any],
        triggering_events: List[SecurityEvent],
    ) -> None:
        """Generate a security alert."""
        import secrets

        alert_id = secrets.token_urlsafe(16)

        # Extract metadata from events
        source_ips = {e.source_ip for e in triggering_events if e.source_ip}
        user_ids = {
            e.metadata.get("user_id")
            for e in triggering_events
            if e.metadata.get("user_id")
        }
        affected_resources = []

        for event in triggering_events:
            if "resource_id" in event.metadata:
                affected_resources.append(event.metadata["resource_id"])
            if "file_path" in event.metadata:
                affected_resources.append(event.metadata["file_path"])

        alert = SecurityAlert(
            id=alert_id,
            rule_name=rule.value,
            severity=config["severity"],
            title=f"Security Alert: {rule.value.replace('_', ' ').title()}",
            description=config["description"],
            triggering_events=triggering_events,
            affected_resources=list(set(affected_resources)),
            source_ips=source_ips,
            user_ids={uid for uid in user_ids if uid is not None},
            metadata={
                "threshold": config["threshold"],
                "time_window_minutes": config["time_window_minutes"],
                "event_count": len(triggering_events),
            },
        )

        self.alerts[alert_id] = alert
        self.metrics.alerts_generated += 1

        # Log alert generation
        self.security_logger.error(
            f"SECURITY ALERT GENERATED: {alert.title} - {alert.description}"
        )

        # Trigger alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.security_logger.error(f"Alert handler failed: {str(e)}")

    def _process_event_buffer(self) -> None:
        """Process buffered events for batch analysis."""
        if not self.event_buffer:
            return

        # Perform batch analysis
        self._analyze_event_patterns()
        self._detect_anomalies()

        # Clear buffer
        self.event_buffer.clear()

    def _analyze_event_patterns(self) -> None:
        """Analyze patterns in recent events."""
        # Group events by source IP
        ip_events = defaultdict(list)
        for event in self.event_buffer:
            if event.source_ip:
                ip_events[event.source_ip].append(event)

        # Look for suspicious patterns
        for ip, events in ip_events.items():
            if len(events) > 50:  # High activity from single IP
                self._generate_pattern_alert(
                    f"High activity from IP {ip}",
                    f"Detected {len(events)} events from IP {ip} in recent batch",
                    events,
                    AlertSeverity.MEDIUM,
                )

    def _detect_anomalies(self) -> None:
        """Detect anomalous behavior in event patterns."""
        current_time = time.time()

        # Check for unusual event frequency
        recent_count = len(
            [e for e in self.event_buffer if current_time - e.timestamp < 300]
        )  # Last 5 minutes

        if recent_count > self.metrics.peak_events_per_minute:
            self.metrics.peak_events_per_minute = recent_count

            if recent_count > 200:  # Anomalously high event rate
                self._generate_pattern_alert(
                    "Anomalous Event Rate",
                    (
                        f"Detected {recent_count} events in 5-minute window "
                        f"(peak: {self.metrics.peak_events_per_minute})"
                    ),
                    self.event_buffer[-recent_count:],
                    AlertSeverity.HIGH,
                )

    def _generate_pattern_alert(
        self,
        title: str,
        description: str,
        events: List[SecurityEvent],
        severity: AlertSeverity,
    ) -> None:
        """Generate an alert based on pattern analysis."""
        import secrets

        alert_id = secrets.token_urlsafe(16)

        alert = SecurityAlert(
            id=alert_id,
            rule_name="pattern_analysis",
            severity=severity,
            title=title,
            description=description,
            triggering_events=events,
            metadata={"analysis_type": "pattern_detection"},
        )

        self.alerts[alert_id] = alert
        self.metrics.alerts_generated += 1

        # Trigger alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.security_logger.error(f"Alert handler failed: {str(e)}")

    def add_alert_handler(self, handler: Callable[[SecurityAlert], None]) -> None:
        """Add an alert handler function."""
        self.alert_handlers.append(handler)

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> None:
        """Acknowledge a security alert."""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.is_acknowledged = True
            alert.acknowledged_by = acknowledged_by
            self.metrics.alerts_acknowledged += 1

            self.security_logger.info(
                f"Alert acknowledged: {alert_id} by {acknowledged_by}"
            )

    def resolve_alert(
        self, alert_id: str, resolved_by: str, resolution_notes: str = ""
    ) -> None:
        """Resolve a security alert."""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.is_resolved = True
            alert.resolved_by = resolved_by
            alert.resolution_notes = resolution_notes
            self.metrics.alerts_resolved += 1

            self.security_logger.info(f"Alert resolved: {alert_id} by {resolved_by}")

    def get_active_alerts(
        self, severity: Optional[AlertSeverity] = None
    ) -> List[SecurityAlert]:
        """Get active (unresolved) alerts."""
        active_alerts = [
            alert for alert in self.alerts.values() if not alert.is_resolved
        ]

        if severity:
            active_alerts = [
                alert for alert in active_alerts if alert.severity == severity
            ]

        return sorted(active_alerts, key=lambda a: a.timestamp, reverse=True)

    def get_security_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive security dashboard data."""
        current_time = time.time()

        # Recent events (last 24 hours)
        recent_events = [
            e for e in self.recent_events if current_time - e.timestamp < 86400
        ]

        # Active alerts by severity
        active_alerts = self.get_active_alerts()
        alerts_by_severity: Dict[str, int] = defaultdict(int)
        for alert in active_alerts:
            alerts_by_severity[alert.severity.value] += 1

        # Top threat sources
        threat_sources: Dict[str, int] = defaultdict(int)
        for event in recent_events:
            if event.severity in ["high", "critical"] and event.source_ip:
                threat_sources[event.source_ip] += 1

        return {
            "summary": {
                "total_events_24h": len(recent_events),
                "active_alerts": len(active_alerts),
                "critical_alerts": alerts_by_severity.get("critical", 0),
                "high_alerts": alerts_by_severity.get("high", 0),
                "threat_sources": len(threat_sources),
            },
            "metrics": self.metrics.to_dict(),
            "active_alerts": [
                alert.to_dict() for alert in active_alerts[:10]
            ],  # Top 10
            "top_threat_sources": dict(
                sorted(threat_sources.items(), key=lambda x: x[1], reverse=True)[:5]
            ),
            "recent_critical_events": [
                {
                    "timestamp": e.timestamp,
                    "event_type": e.event_type,
                    "message": e.message,
                    "source_ip": e.source_ip,
                }
                for e in recent_events
                if e.severity == "critical"
            ][
                -10:
            ],  # Last 10 critical events
        }

    def export_security_report(self, hours: int = 24) -> Dict[str, Any]:
        """Export comprehensive security report."""
        current_time = time.time()
        start_time = current_time - (hours * 3600)

        # Filter events by time range
        report_events = [e for e in self.recent_events if e.timestamp >= start_time]

        # Generate report
        report: Dict[str, Any] = {
            "report_period": {
                "start_time": start_time,
                "end_time": current_time,
                "duration_hours": hours,
            },
            "summary": {
                "total_events": len(report_events),
                "events_by_severity": defaultdict(int),
                "events_by_type": defaultdict(int),
                "unique_source_ips": len(
                    set(e.source_ip for e in report_events if e.source_ip)
                ),
                "alerts_generated": len(
                    [a for a in self.alerts.values() if a.timestamp >= start_time]
                ),
            },
            "top_events": defaultdict(int),
            "threat_analysis": {
                "high_risk_ips": [],
                "suspicious_patterns": [],
                "attack_vectors": defaultdict(int),
            },
            "recommendations": [],
        }

        # Analyze events
        for event in report_events:
            report["summary"]["events_by_severity"][event.severity] += 1
            report["summary"]["events_by_type"][event.event_type] += 1
            report["top_events"][event.event_type] += 1

        # Generate recommendations
        if report["summary"]["events_by_severity"]["critical"] > 0:
            report["recommendations"].append(
                "Immediate attention required for critical security events"
            )

        if report["summary"]["events_by_severity"]["high"] > 10:
            report["recommendations"].append(
                "Review high-severity events for potential security threats"
            )

        return report


# Global security monitor instance
_security_monitor: Optional[SecurityMonitor] = None


def get_security_monitor(log_dir: Optional[str] = None) -> SecurityMonitor:
    """Get or create global security monitor instance."""
    global _security_monitor
    if _security_monitor is None or log_dir:
        _security_monitor = SecurityMonitor(log_dir or ".lackey/logs")
    return _security_monitor


def log_security_event(event: SecurityEvent) -> None:
    """Log a security event."""
    monitor = get_security_monitor()
    monitor.process_security_event(event)


# Default alert handlers
def console_alert_handler(alert: SecurityAlert) -> None:
    """Handle console alerts."""
    print(f"🚨 SECURITY ALERT: {alert.title}")
    print(f"   Severity: {alert.severity.value.upper()}")
    print(f"   Description: {alert.description}")
    print(f"   Events: {len(alert.triggering_events)}")
    if alert.source_ips:
        print(f"   Source IPs: {', '.join(alert.source_ips)}")
    print()


def email_alert_handler(alert: SecurityAlert) -> None:
    """Email alert handler (placeholder - would need email configuration)."""
    # This would integrate with an email service
    pass


# Initialize default alert handlers
def initialize_default_handlers() -> None:
    """Initialize default alert handlers."""
    monitor = get_security_monitor()
    monitor.add_alert_handler(console_alert_handler)
