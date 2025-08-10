"""Comprehensive error handling system for gateway operations.

This module provides detailed error classification, actionable error messages,
recovery strategies, and error tracking for the gateway routing infrastructure.
"""

import asyncio
import logging
import time
import traceback
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""

    VALIDATION = "validation"
    ROUTING = "routing"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RESOURCE_NOT_FOUND = "resource_not_found"
    DEPENDENCY = "dependency"
    SYSTEM = "system"
    NETWORK = "network"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    CONFIGURATION = "configuration"
    DATA_INTEGRITY = "data_integrity"


class RecoveryStrategy(Enum):
    """Recovery strategies for different error types."""

    RETRY = "retry"
    FALLBACK = "fallback"
    USER_INPUT = "user_input"
    ESCALATE = "escalate"
    IGNORE = "ignore"
    ABORT = "abort"


@dataclass
class ErrorContext:
    """Context information for error analysis."""

    operation: str
    parameters: Dict[str, Any]
    user_query: str
    gateway_type: str
    timestamp: float = field(default_factory=time.time)
    session_id: Optional[str] = None
    request_id: Optional[str] = None


@dataclass
class ErrorDetails:
    """Detailed error information."""

    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    technical_details: str
    user_message: str
    suggested_actions: List[str]
    recovery_strategy: RecoveryStrategy
    context: ErrorContext
    stack_trace: Optional[str] = None
    related_errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ErrorMessageGenerator:
    """Generates user-friendly and actionable error messages."""

    def __init__(self) -> None:
        """Initialize the error message formatter."""
        self.message_templates = self._load_message_templates()
        self.action_templates = self._load_action_templates()

    def _load_message_templates(self) -> Dict[str, Dict[str, str]]:
        """Load error message templates by category."""
        return {
            ErrorCategory.VALIDATION.value: {
                "missing_parameter": (
                    "The required parameter '{parameter}' is missing. {description}"
                ),
                "invalid_format": (
                    "The parameter '{parameter}' has an invalid format. "
                    "Expected: {expected}, got: {actual}"
                ),
                "invalid_value": (
                    "The parameter '{parameter}' has an invalid value '{value}'. "
                    "{constraint_description}"
                ),
                "type_mismatch": (
                    "The parameter '{parameter}' must be of type {expected_type}, "
                    "but received {actual_type}"
                ),
                "constraint_violation": (
                    "The parameter '{parameter}' violates the constraint: "
                    "{constraint}"
                ),
            },
            ErrorCategory.ROUTING.value: {
                "intent_not_found": (
                    "Could not understand the request '{query}'. "
                    "Please try rephrasing or use more specific terms"
                ),
                "ambiguous_intent": (
                    "The request '{query}' matches multiple operations. "
                    "Please be more specific"
                ),
                "tool_not_found": (
                    "The operation '{tool_name}' is not available in the "
                    "{gateway_type} gateway"
                ),
                "low_confidence": (
                    "The request '{query}' was unclear (confidence: {confidence}%). "
                    "Please provide more details"
                ),
            },
            ErrorCategory.RESOURCE_NOT_FOUND.value: {
                "project_not_found": (
                    "Project '{project_id}' was not found. "
                    "Please check the project ID or create the project first"
                ),
                "task_not_found": (
                    "Task '{task_id}' was not found in project '{project_id}'. "
                    "Please verify the task ID"
                ),
                "note_not_found": "Note not found for the specified criteria",
                "user_not_found": "User '{user_id}' was not found in the system",
            },
            ErrorCategory.DEPENDENCY.value: {
                "circular_dependency": (
                    "Cannot add dependency - it would create a circular "
                    "dependency: {cycle_path}"
                ),
                "dependency_not_found": (
                    "Dependency task '{dependency_id}' was not found"
                ),
                "invalid_dependency": "Cannot add dependency: {reason}",
                "dependency_violation": (
                    "Operation violates dependency constraints: {details}"
                ),
            },
            ErrorCategory.AUTHENTICATION.value: {
                "not_authenticated": (
                    "Authentication required. Please provide valid credentials"
                ),
                "invalid_credentials": "Invalid credentials provided",
                "session_expired": (
                    "Your session has expired. Please authenticate again"
                ),
            },
            ErrorCategory.AUTHORIZATION.value: {
                "insufficient_permissions": (
                    "You don't have permission to perform this operation on "
                    "{resource_type} '{resource_id}'"
                ),
                "role_required": (
                    "This operation requires {required_role} role or higher"
                ),
                "access_denied": "Access denied to {resource_type} '{resource_id}'",
            },
            ErrorCategory.RATE_LIMIT.value: {
                "rate_limit_exceeded": (
                    "Rate limit exceeded. Please wait {retry_after} seconds "
                    "before trying again"
                ),
                "quota_exceeded": (
                    "Daily quota exceeded for {operation_type} operations"
                ),
                "concurrent_limit": (
                    "Too many concurrent operations. Please wait and try again"
                ),
            },
            ErrorCategory.SYSTEM.value: {
                "internal_error": (
                    "An internal system error occurred. Please try again later"
                ),
                "service_unavailable": (
                    "The service is temporarily unavailable. "
                    "Please try again in a few minutes"
                ),
                "database_error": "Database operation failed. Please try again",
                "file_system_error": "File system operation failed: {details}",
            },
            ErrorCategory.NETWORK.value: {
                "connection_failed": (
                    "Failed to connect to the service. "
                    "Please check your network connection"
                ),
                "timeout": (
                    "The operation timed out. Please try again with a "
                    "smaller request"
                ),
                "network_error": "Network error occurred: {details}",
            },
            ErrorCategory.CONFIGURATION.value: {
                "invalid_config": ("Invalid configuration: {config_issue}"),
                "missing_config": ("Required configuration is missing: {config_key}"),
                "config_error": "Configuration error: {details}",
            },
            ErrorCategory.DATA_INTEGRITY.value: {
                "data_corruption": "Data integrity issue detected: {details}",
                "version_conflict": (
                    "Version conflict detected. Please refresh and try again"
                ),
                "consistency_error": "Data consistency error: {details}",
            },
        }

    def _load_action_templates(self) -> Dict[str, List[str]]:
        """Load suggested action templates by category."""
        return {
            ErrorCategory.VALIDATION.value: [
                "Check the parameter format and try again",
                "Refer to the documentation for valid parameter values",
                "Use the parameter suggestions if available",
                "Contact support if the error persists",
            ],
            ErrorCategory.ROUTING.value: [
                "Try rephrasing your request with more specific terms",
                "Use explicit parameter names instead of natural language",
                "Check the available operations for this gateway",
                "Refer to the usage examples in the documentation",
            ],
            ErrorCategory.RESOURCE_NOT_FOUND.value: [
                "Verify the resource ID is correct",
                "Check if the resource exists using list operations",
                "Ensure you have access to the resource",
                "Create the resource if it doesn't exist",
            ],
            ErrorCategory.DEPENDENCY.value: [
                "Review the dependency graph to identify cycles",
                "Remove conflicting dependencies before adding new ones",
                "Use the validate_dependencies tool to check for issues",
                "Consider restructuring the task dependencies",
            ],
            ErrorCategory.AUTHENTICATION.value: [
                "Provide valid authentication credentials",
                "Check if your session has expired",
                "Verify your user account is active",
                "Contact your administrator for access",
            ],
            ErrorCategory.AUTHORIZATION.value: [
                "Request the necessary permissions from your administrator",
                "Check if you're using the correct user account",
                "Verify the resource exists and you have access",
                "Contact support for permission issues",
            ],
            ErrorCategory.RATE_LIMIT.value: [
                "Wait for the specified time before retrying",
                "Reduce the frequency of your requests",
                "Use bulk operations when available",
                "Contact support to increase your rate limits",
            ],
            ErrorCategory.SYSTEM.value: [
                "Try the operation again in a few minutes",
                "Check the system status page",
                "Contact support if the issue persists",
                "Use alternative operations if available",
            ],
            ErrorCategory.NETWORK.value: [
                "Check your internet connection",
                "Try again with a smaller request",
                "Verify the service endpoint is accessible",
                "Contact your network administrator",
            ],
            ErrorCategory.CONFIGURATION.value: [
                "Check the configuration file for errors",
                "Verify all required settings are present",
                "Refer to the configuration documentation",
                "Reset to default configuration if needed",
            ],
            ErrorCategory.DATA_INTEGRITY.value: [
                "Refresh your data and try again",
                "Check for concurrent modifications",
                "Verify data consistency using validation tools",
                "Contact support for data recovery",
            ],
        }

    def generate_error_message(
        self, error_type: str, category: ErrorCategory, context: Dict[str, Any]
    ) -> Tuple[str, List[str]]:
        """Generate user-friendly error message and suggested actions."""
        category_templates = self.message_templates.get(category.value, {})
        template = category_templates.get(error_type, "An error occurred: {error}")

        try:
            message = template.format(**context)
        except KeyError as e:
            message = f"An error occurred. Missing context: {e}"

        # Get suggested actions
        actions = self.action_templates.get(
            category.value,
            [
                "Try the operation again",
                "Check your input parameters",
                "Contact support if the issue persists",
            ],
        )

        return message, actions


class ErrorClassifier:
    """Classifies errors into categories and determines severity."""

    def __init__(self) -> None:
        """Initialize the error classifier."""
        self.classification_rules = self._load_classification_rules()

    def _load_classification_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load error classification rules."""
        return {
            # Validation errors
            "ValidationError": {
                "category": ErrorCategory.VALIDATION,
                "severity": ErrorSeverity.MEDIUM,
                "recovery": RecoveryStrategy.USER_INPUT,
            },
            "TypeError": {
                "category": ErrorCategory.VALIDATION,
                "severity": ErrorSeverity.MEDIUM,
                "recovery": RecoveryStrategy.USER_INPUT,
            },
            "ValueError": {
                "category": ErrorCategory.VALIDATION,
                "severity": ErrorSeverity.MEDIUM,
                "recovery": RecoveryStrategy.USER_INPUT,
            },
            # Routing errors
            "RoutingError": {
                "category": ErrorCategory.ROUTING,
                "severity": ErrorSeverity.MEDIUM,
                "recovery": RecoveryStrategy.USER_INPUT,
            },
            "IntentNotFoundError": {
                "category": ErrorCategory.ROUTING,
                "severity": ErrorSeverity.MEDIUM,
                "recovery": RecoveryStrategy.USER_INPUT,
            },
            # Resource errors
            "FileNotFoundError": {
                "category": ErrorCategory.RESOURCE_NOT_FOUND,
                "severity": ErrorSeverity.MEDIUM,
                "recovery": RecoveryStrategy.USER_INPUT,
            },
            "KeyError": {
                "category": ErrorCategory.RESOURCE_NOT_FOUND,
                "severity": ErrorSeverity.MEDIUM,
                "recovery": RecoveryStrategy.USER_INPUT,
            },
            # System errors
            "OSError": {
                "category": ErrorCategory.SYSTEM,
                "severity": ErrorSeverity.HIGH,
                "recovery": RecoveryStrategy.RETRY,
            },
            "IOError": {
                "category": ErrorCategory.SYSTEM,
                "severity": ErrorSeverity.HIGH,
                "recovery": RecoveryStrategy.RETRY,
            },
            "MemoryError": {
                "category": ErrorCategory.SYSTEM,
                "severity": ErrorSeverity.CRITICAL,
                "recovery": RecoveryStrategy.ABORT,
            },
            # Network errors
            "ConnectionError": {
                "category": ErrorCategory.NETWORK,
                "severity": ErrorSeverity.HIGH,
                "recovery": RecoveryStrategy.RETRY,
            },
            "TimeoutError": {
                "category": ErrorCategory.TIMEOUT,
                "severity": ErrorSeverity.MEDIUM,
                "recovery": RecoveryStrategy.RETRY,
            },
            # Security errors
            "PermissionError": {
                "category": ErrorCategory.AUTHORIZATION,
                "severity": ErrorSeverity.HIGH,
                "recovery": RecoveryStrategy.ESCALATE,
            },
            "SecurityError": {
                "category": ErrorCategory.AUTHENTICATION,
                "severity": ErrorSeverity.HIGH,
                "recovery": RecoveryStrategy.ESCALATE,
            },
        }

    def classify_error(
        self, exception: Exception
    ) -> Tuple[ErrorCategory, ErrorSeverity, RecoveryStrategy]:
        """Classify an exception into category, severity, and recovery strategy."""
        exception_name = type(exception).__name__

        if exception_name in self.classification_rules:
            rule = self.classification_rules[exception_name]
            return rule["category"], rule["severity"], rule["recovery"]

        # Default classification for unknown errors
        return ErrorCategory.SYSTEM, ErrorSeverity.MEDIUM, RecoveryStrategy.RETRY


class ErrorRecoveryManager:
    """Manages error recovery strategies and retry logic."""

    def __init__(self) -> None:
        """Initialize the error recovery manager."""
        self.retry_config = {
            ErrorCategory.NETWORK: {"max_retries": 3, "backoff": 2.0},
            ErrorCategory.TIMEOUT: {"max_retries": 2, "backoff": 1.5},
            ErrorCategory.SYSTEM: {"max_retries": 2, "backoff": 3.0},
            ErrorCategory.RATE_LIMIT: {"max_retries": 1, "backoff": 5.0},
        }
        self.recovery_attempts: Dict[str, int] = {}

    async def attempt_recovery(
        self,
        error_details: ErrorDetails,
        operation_func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[bool, Any]:
        """Attempt to recover from an error using the appropriate strategy."""
        strategy = error_details.recovery_strategy

        if strategy == RecoveryStrategy.RETRY:
            return await self._retry_operation(
                error_details, operation_func, *args, **kwargs
            )
        elif strategy == RecoveryStrategy.FALLBACK:
            return await self._fallback_operation(
                error_details, operation_func, *args, **kwargs
            )
        elif strategy == RecoveryStrategy.USER_INPUT:
            return False, f"User input required: {error_details.user_message}"
        elif strategy == RecoveryStrategy.ESCALATE:
            return False, f"Error escalated: {error_details.user_message}"
        elif strategy == RecoveryStrategy.IGNORE:
            return True, None
        else:  # ABORT
            return False, f"Operation aborted: {error_details.user_message}"

    async def _retry_operation(
        self,
        error_details: ErrorDetails,
        operation_func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[bool, Any]:
        """Retry operation with exponential backoff."""
        category = error_details.category
        error_id = error_details.error_id

        if error_id not in self.recovery_attempts:
            self.recovery_attempts[error_id] = 0

        config = self.retry_config.get(category, {"max_retries": 1, "backoff": 1.0})
        max_retries = config["max_retries"]
        backoff = config["backoff"]

        if self.recovery_attempts[error_id] >= max_retries:
            return False, f"Max retries ({max_retries}) exceeded for operation"

        self.recovery_attempts[error_id] += 1
        retry_count = self.recovery_attempts[error_id]

        # Wait with exponential backoff
        wait_time = backoff**retry_count
        await asyncio.sleep(wait_time)

        try:
            result = await operation_func(*args, **kwargs)
            # Success - clear retry count
            del self.recovery_attempts[error_id]
            return True, result
        except Exception as e:
            logger.warning(f"Retry {retry_count} failed for {error_id}: {e}")
            return False, f"Retry {retry_count} failed: {str(e)}"

    async def _fallback_operation(
        self,
        error_details: ErrorDetails,
        operation_func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[bool, Any]:
        """Attempt fallback operation."""
        # This would implement fallback logic based on the operation type
        # For now, return failure
        return False, "No fallback operation available"


class GatewayErrorHandler:
    """Main error handling system for gateway operations."""

    def __init__(self) -> None:
        """Initialize the error handling system."""
        self.message_generator = ErrorMessageGenerator()
        self.classifier = ErrorClassifier()
        self.recovery_manager = ErrorRecoveryManager()
        self.error_history: List[ErrorDetails] = []
        self.error_counter = 0

    async def handle_error(
        self,
        exception: Exception,
        context: ErrorContext,
        operation_func: Optional[Callable[..., Any]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> ErrorDetails:
        """Handle an error with comprehensive analysis and recovery."""
        self.error_counter += 1
        error_id = f"error_{self.error_counter}_{int(time.time())}"

        # Classify the error
        category, severity, recovery_strategy = self.classifier.classify_error(
            exception
        )

        # Generate user-friendly message
        error_context = {
            "error": str(exception),
            "operation": context.operation,
            "gateway_type": context.gateway_type,
            "query": context.user_query,
        }

        # Add specific context based on error type
        if isinstance(exception, KeyError):
            error_context["missing_key"] = str(exception).strip("'\"")
        elif hasattr(exception, "args") and exception.args:
            error_context["details"] = exception.args[0]

        user_message, suggested_actions = self.message_generator.generate_error_message(
            type(exception).__name__.lower(), category, error_context
        )

        # Create error details
        error_details = ErrorDetails(
            error_id=error_id,
            category=category,
            severity=severity,
            message=str(exception),
            technical_details=traceback.format_exc(),
            user_message=user_message,
            suggested_actions=suggested_actions,
            recovery_strategy=recovery_strategy,
            context=context,
            stack_trace=traceback.format_exc(),
            metadata={
                "exception_type": type(exception).__name__,
                "exception_module": type(exception).__module__,
            },
        )

        # Log the error
        self._log_error(error_details)

        # Add to error history
        self.error_history.append(error_details)
        if len(self.error_history) > 1000:  # Keep last 1000 errors
            self.error_history = self.error_history[-1000:]

        # Attempt recovery if operation function is provided
        if operation_func:
            try:
                success, result = await self.recovery_manager.attempt_recovery(
                    error_details, operation_func, *args, **kwargs
                )
                if success:
                    error_details.metadata["recovery_successful"] = True
                    error_details.metadata["recovery_result"] = str(result)
                    logger.info(f"Successfully recovered from error {error_id}")
                else:
                    error_details.metadata["recovery_failed"] = True
                    error_details.metadata["recovery_message"] = str(result)
            except Exception as recovery_error:
                error_details.metadata["recovery_error"] = str(recovery_error)
                logger.error(f"Recovery failed for error {error_id}: {recovery_error}")

        return error_details

    def _log_error(self, error_details: ErrorDetails) -> None:
        """Log error with appropriate level based on severity."""
        log_message = (
            f"Gateway Error [{error_details.error_id}]: "
            f"{error_details.category.value} - {error_details.message}"
        )

        if error_details.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, extra={"error_details": error_details})
        elif error_details.severity == ErrorSeverity.HIGH:
            logger.error(log_message, extra={"error_details": error_details})
        elif error_details.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message, extra={"error_details": error_details})
        else:
            logger.info(log_message, extra={"error_details": error_details})

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        if not self.error_history:
            return {"total_errors": 0}

        # Count by category
        category_counts: Dict[str, int] = {}
        severity_counts: Dict[str, int] = {}
        recovery_success = 0

        for error in self.error_history:
            category = error.category.value
            severity = error.severity.value

            category_counts[category] = category_counts.get(category, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

            if error.metadata.get("recovery_successful"):
                recovery_success += 1

        return {
            "total_errors": len(self.error_history),
            "by_category": category_counts,
            "by_severity": severity_counts,
            "recovery_success_rate": (
                recovery_success / len(self.error_history) if self.error_history else 0
            ),
            "most_recent_error": (
                self.error_history[-1].error_id if self.error_history else None
            ),
        }

    def get_recent_errors(self, limit: int = 10) -> List[ErrorDetails]:
        """Get recent errors for debugging."""
        return self.error_history[-limit:] if self.error_history else []

    def clear_error_history(self) -> None:
        """Clear error history."""
        self.error_history.clear()
        logger.info("Error history cleared")


# Global error handler instance
_global_error_handler = None


def get_error_handler() -> GatewayErrorHandler:
    """Get global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = GatewayErrorHandler()
    return _global_error_handler


# Convenience functions for common error scenarios
def create_validation_error(parameter: str, expected: str, actual: str) -> ErrorDetails:
    """Create a validation error with standard formatting."""
    context = ErrorContext(
        operation="validation",
        parameters={"parameter": parameter, "expected": expected, "actual": actual},
        user_query="",
        gateway_type="unknown",
    )

    exception = ValueError(f"Invalid {parameter}: expected {expected}, got {actual}")
    handler = get_error_handler()

    # This would be called in an async context normally
    import asyncio

    return asyncio.run(handler.handle_error(exception, context))


def create_routing_error(
    query: str, gateway_type: str, confidence: float = 0.0
) -> ErrorDetails:
    """Create a routing error with standard formatting."""
    context = ErrorContext(
        operation="routing",
        parameters={"query": query, "confidence": confidence},
        user_query=query,
        gateway_type=gateway_type,
    )

    from lackey.mcp.gateway_router import RoutingError

    exception = RoutingError(f"Could not route query: {query}")
    handler = get_error_handler()

    # This would be called in an async context normally
    import asyncio

    return asyncio.run(handler.handle_error(exception, context))
