"""Gateway-based MCP server implementation for Lackey task management."""

import functools
import logging
import time
from typing import Any, Callable, Dict, Optional

from mcp.server import FastMCP

from lackey import LackeyCore, __api_version__
from lackey.dependencies import DependencyValidator
from lackey.mcp.gateways.lackey_analyze import LackeyAnalyzeGateway

# Import gateway implementations
from lackey.mcp.gateways.lackey_do import LackeyDoGateway
from lackey.mcp.gateways.lackey_get import LackeyGetGateway
from lackey.mcp.tool_analytics import get_analytics_manager
from lackey.rate_limiting import get_rate_limit_manager

logger = logging.getLogger(__name__)


def mcp_analytics_tracking() -> Callable:
    """Analytics tracking decorator for MCP tools."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            success = False
            error_message = None

            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error_message = str(e)
                raise
            finally:
                execution_time_ms = (time.time() - start_time) * 1000

                try:
                    analytics_manager = get_analytics_manager()
                    analytics_manager.record_tool_usage(
                        tool_name=func.__name__,
                        execution_time_ms=execution_time_ms,
                        success=success,
                        error_message=error_message,
                        parameters={
                            k: str(v)[:100] for k, v in kwargs.items()
                        },  # Truncate long values
                        user_context="mcp_stdio",
                    )
                except Exception as analytics_error:
                    # Don't let analytics errors break tool execution
                    logger.warning(
                        f"Analytics tracking failed for {func.__name__}: "
                        f"{analytics_error}"
                    )

        return wrapper

    return decorator


def mcp_rate_limit(rule_name: str = "default") -> Callable:
    """Rate limiting decorator specifically for MCP stdio communication."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            manager = get_rate_limit_manager()

            # Use localhost IP as the identifier for MCP stdio communication
            identifier = "127.0.0.1"
            endpoint = func.__name__

            # Check rate limit
            is_allowed, rate_info = manager.check_rate_limit(
                identifier, endpoint, rule_name
            )

            if not is_allowed:
                from lackey.security import SecurityError

                error_msg = f"Rate limit exceeded. Status: {rate_info['status']}"
                if rate_info.get("retry_after", 0) > 0:
                    error_msg += f" Retry after {rate_info['retry_after']:.0f} seconds."
                raise SecurityError(error_msg)

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def mcp_security_required(
    validate_input: bool = True,
    validation_rules: Optional[Dict[str, str]] = None,
) -> Callable:
    """Security decorator specifically for MCP stdio communication."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            from lackey.security import SecurityEvent, get_security_manager
            from lackey.validation import SecurityError, ValidationError

            # Get security manager instance
            security_manager = get_security_manager()

            # Input validation
            if validate_input and validation_rules:
                try:
                    # Validate and sanitize kwargs
                    sanitized_kwargs = security_manager.validate_and_sanitize_input(
                        kwargs, validation_rules
                    )
                    kwargs.update(sanitized_kwargs)
                except (ValidationError, SecurityError) as e:
                    security_manager.log_security_event(
                        SecurityEvent(
                            event_type="endpoint_security_violation",
                            severity="medium",
                            message=f"Security violation in {func.__name__}: {str(e)}",
                            metadata={"function": func.__name__, "error": str(e)},
                        )
                    )
                    raise

            # Call original function
            return await func(*args, **kwargs)

        return wrapper

    return decorator


# MCP API Version (follows semantic versioning)
MCP_API_VERSION = __api_version__  # "1.0.0"

# Create the FastMCP server instance
mcp_server = FastMCP("lackey")

# Global variables for core components and gateways
lackey_core: Optional[LackeyCore] = None
validator: Optional[DependencyValidator] = None
do_gateway: Optional[LackeyDoGateway] = None
get_gateway: Optional[LackeyGetGateway] = None
analyze_gateway: Optional[LackeyAnalyzeGateway] = None


def create_server(lackey_dir_path: str = ".lackey") -> FastMCP:
    """Create and configure the Gateway-based Lackey MCP server.

    Args:
        lackey_dir_path: Path to the .lackey directory where files are stored

    Returns:
        Configured FastMCP server instance with 3 semantic gateways
    """
    global lackey_core, validator, do_gateway, get_gateway, analyze_gateway

    # Initialize core components first
    lackey_core = LackeyCore(lackey_dir_path)
    validator = DependencyValidator()

    # Now initialize the 3 gateways (they can access the global lackey_core)
    do_gateway = LackeyDoGateway()
    get_gateway = LackeyGetGateway()
    analyze_gateway = LackeyAnalyzeGateway()

    # Configure rate limiting for gateway endpoints
    _configure_gateway_rate_limiting()

    logger.info(
        f"Gateway-based Lackey MCP server initialized with lackey dir: "
        f"{lackey_dir_path}"
    )
    logger.info(
        "Server now exposes 3 semantic gateways instead of 25+ individual " "tools"
    )
    logger.info(
        f"Gateway tool counts: do={len(do_gateway.tool_registry)}, "
        f"get={len(get_gateway.tool_registry)}, "
        f"analyze={len(analyze_gateway.tool_registry)}"
    )
    return mcp_server


def _configure_gateway_rate_limiting() -> None:
    """Configure rate limiting rules for the 3 gateway endpoints."""
    rate_manager = get_rate_limit_manager()

    # lackey_get - read operations (lenient: 120 req/min, burst 20)
    rate_manager.assign_rule_to_endpoint("lackey_get", "lenient")

    # lackey_do - write operations (default: 60 req/min, burst 10)
    rate_manager.assign_rule_to_endpoint("lackey_do", "default")

    # lackey_analyze - analysis operations (adaptive: 60 req/min, adaptive behavior)
    rate_manager.assign_rule_to_endpoint("lackey_analyze", "adaptive")


def _ensure_initialized() -> tuple[LackeyCore, DependencyValidator]:
    """Ensure core components are initialized."""
    if lackey_core is None or validator is None:
        raise RuntimeError("Lackey core not initialized")
    return lackey_core, validator


def _ensure_gateways_initialized() -> (
    tuple[LackeyDoGateway, LackeyGetGateway, LackeyAnalyzeGateway]
):
    """Ensure gateway components are initialized."""
    if do_gateway is None or get_gateway is None or analyze_gateway is None:
        raise RuntimeError("Gateway components not initialized")
    return do_gateway, get_gateway, analyze_gateway


# Gateway Tool 1: lackey_do - All state-changing operations
@mcp_server.tool(description="Perform state-changing operations on tasks and projects")
@mcp_analytics_tracking()
@mcp_rate_limit(rule_name="default")
@mcp_security_required(validate_input=True)
async def lackey_do(
    action: str,
    target: str,
    data: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None,
) -> str:
    """Perform state-changing operations on tasks and projects.

    This gateway consolidates ALL state-changing operations into a single
    semantic interface:
    - Create projects, tasks, notes
    - Update project/task information and status
    - Complete tasks and task steps
    - Assign and reassign tasks
    - Archive tasks
    - Add/remove task dependencies
    - Bulk operations for efficiency

    Args:
        action: The action to perform (create, update, complete, assign,
                archive, add, remove, bulk)
        target: The target of the action (project, task, note, dependency,
                steps, status, assignment)
        data: Action-specific data and parameters
        options: Optional settings (atomic, validate, etc.)

    Returns:
        Result of the state-changing operation with confirmation details
    """
    try:
        do_gw, _, _ = _ensure_gateways_initialized()

        request = {
            "action": action,
            "target": target,
            "data": data,
            "options": options or {},
        }

        result = await do_gw.route_request(request)

        if result.success:
            return f"✅ {action} {target} completed successfully\n\n{result.content}"
        else:
            return f"❌ {action} {target} failed: {result.content}"

    except Exception as e:
        logger.error(f"lackey_do failed: {e}")
        return f"Error executing {action} {target}: {str(e)}"


# Gateway Tool 2: lackey_get - All read operations
@mcp_server.tool(
    description="Retrieve information about tasks, projects, and system status"
)
@mcp_analytics_tracking()
@mcp_rate_limit(rule_name="lenient")
@mcp_security_required(validate_input=True)
async def lackey_get(query: str, context: Optional[Dict[str, Any]] = None) -> str:
    """Retrieve information about tasks, projects, and system status.

    This gateway consolidates ALL read operations into a single semantic interface:
    - Get tasks, projects, status, progress, notes, dependencies
    - Advanced filtering by status, complexity, assignee, tags, date ranges
    - Search functionality with text indexing and ranking
    - Support for pagination and result limiting

    Args:
        query: Natural language query describing what information to retrieve
        context: Additional context for filtering and scoping

    Returns:
        Requested information formatted for readability
    """
    try:
        _, get_gw, _ = _ensure_gateways_initialized()

        request = {"query": query, "context": context or {}}

        result = await get_gw.route_request(request)

        if result.success:
            return f"📊 Query Results\n\n{result.content}"
        else:
            return f"❌ Query failed: {result.content}"

    except Exception as e:
        logger.error(f"lackey_get failed: {e}")
        return f"Error executing query: {str(e)}"


# Gateway Tool 3: lackey_analyze - All analysis operations
@mcp_server.tool(
    description=(
        "Perform analysis and provide insights on tasks, projects, " "and workflows"
    )
)
@mcp_analytics_tracking()
@mcp_rate_limit(rule_name="adaptive")
@mcp_security_required(validate_input=True)
async def lackey_analyze(
    analysis_type: str, scope: Optional[Dict[str, Any]] = None
) -> str:
    """Perform analysis and provide insights on tasks, projects, and workflows.

    This gateway consolidates ALL analysis operations into a single semantic interface:
    - Dependency analysis with cycle detection and critical path identification
    - Critical path analysis with bottleneck identification and optimization suggestions
    - Blocker analysis with impact assessment and resolution recommendations
    - Timeline analysis with scheduling and milestone identification
    - Workload analysis with capacity planning and resource allocation
    - Integrity analysis with data validation and automatic fixing
    - Health analysis combining multiple metrics
    - Performance analysis with benchmarking

    Args:
        analysis_type: Type of analysis (dependencies, critical_path,
                      blockers, timeline, workload, integrity, health,
                      performance)
        scope: Scope and parameters for the analysis

    Returns:
        Analysis results with insights and recommendations
    """
    try:
        _, _, analyze_gw = _ensure_gateways_initialized()

        request = {"analysis_type": analysis_type, "scope": scope or {}}

        result = await analyze_gw.route_request(request)

        if result.success:
            return f"🔍 Analysis Results\n\n{result.content}"
        else:
            return f"❌ Analysis failed: {result.content}"

    except Exception as e:
        logger.error(f"lackey_analyze failed: {e}")
        return f"Error executing analysis: {str(e)}"


class LackeyMCPServer:
    """Wrapper class for the Gateway-based Lackey MCP server."""

    def __init__(self, lackey_dir_path: str = ".lackey"):
        """Initialize the server wrapper.

        Args:
            lackey_dir_path: Path to the .lackey directory where files are stored
        """
        self.lackey_dir_path = lackey_dir_path
        self.server = create_server(lackey_dir_path)

        logger.info("MCP server initialized...")

    async def run(self) -> None:
        """Run the MCP server."""
        await self.server.run_stdio_async()

    async def stop(self) -> None:
        """Stop the MCP server."""
        # FastMCP handles cleanup automatically
        pass
