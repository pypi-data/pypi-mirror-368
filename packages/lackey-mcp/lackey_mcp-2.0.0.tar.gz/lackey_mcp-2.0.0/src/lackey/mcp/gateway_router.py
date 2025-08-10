"""Gateway routing infrastructure for semantic tool consolidation."""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .intent_classifier import (
    AdvancedIntentClassifier,
    ClassificationAlgorithm,
    ClassificationContext,
)
from .parameter_mapper import (
    AdvancedParameterMapper,
    MappingRule,
    ParameterSchema,
    ParameterType,
)

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Routing strategy for intent classification."""

    BEST_MATCH = "best_match"
    CONFIDENCE_THRESHOLD = "confidence_threshold"
    FALLBACK_CHAIN = "fallback_chain"


@dataclass
class IntentMatch:
    """Result of intent classification."""

    intent: str
    confidence: float
    tool_name: str
    parameters: Dict[str, Any]
    gateway_type: str
    validation_schema: Optional[Dict[str, Any]] = None
    parameter_mappings: Optional[Dict[str, str]] = None


@dataclass
class RoutingResult:
    """Result of gateway routing operation."""

    success: bool
    content: Any
    tool_name: str
    execution_time_ms: float
    confidence_score: float
    error_message: Optional[str] = None
    performance_metrics: Optional[Dict[str, Any]] = None


class RoutingError(Exception):
    """Exception raised when routing fails."""

    pass


class GatewayRouter(ABC):
    """Base class for gateway routing logic with comprehensive error handling.

    Provides advanced optimization capabilities for routing requests.
    """

    def __init__(
        self,
        gateway_name: str,
        routing_strategy: RoutingStrategy = RoutingStrategy.BEST_MATCH,
    ) -> None:
        """Initialize the gateway router."""
        self.gateway_name = gateway_name
        self.routing_strategy = routing_strategy
        self.intent_patterns = self._load_intent_patterns()
        self.parameter_mappings = self._load_parameter_mappings()
        self.validation_schemas = self._load_validation_schemas()
        self.tool_registry = self._load_tool_registry()

        # Initialize advanced components
        self.intent_classifier = AdvancedIntentClassifier()
        self.parameter_mapper = AdvancedParameterMapper()

        # Performance tracking
        self.routing_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "intent_classification_accuracy": 0.0,
        }

        logger.info(
            f"Initialized {gateway_name} gateway with {len(self.tool_registry)} "
            f"tools and advanced routing"
        )

    @abstractmethod
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load intent classification patterns for this gateway."""
        pass

    @abstractmethod
    def _load_parameter_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load parameter mapping configurations for each tool."""
        pass

    @abstractmethod
    def _load_validation_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load validation schemas for each tool."""
        pass

    @abstractmethod
    def _load_tool_registry(self) -> Dict[str, Callable]:
        """Load registry of available tools for this gateway."""
        pass

    async def route_request(self, request: Dict[str, Any]) -> RoutingResult:
        """Route gateway request to appropriate underlying tool.

        Provides advanced optimization for request routing.
        """
        start_time = asyncio.get_event_loop().time()

        try:
            self.routing_stats["total_requests"] += 1
            logger.debug(f"Routing request in {self.gateway_name}: {request}")

            # Stage 1: Advanced Intent Classification
            try:
                classification_context = self._build_classification_context(request)
                logger.debug(f"Built classification context: {classification_context}")
            except Exception as e:
                logger.error(
                    f"Failed to build classification context: {e}", exc_info=True
                )
                raise RoutingError(f"Context building failed: {e}")

            try:
                intent_candidates = await self.intent_classifier.classify_intent(
                    query_text=self._extract_query_text(request),
                    intent_patterns=self.intent_patterns,
                    context=classification_context,
                    algorithm=ClassificationAlgorithm.HYBRID,
                )
                logger.debug(
                    f"Intent candidates: {[c.intent for c in intent_candidates]}"
                )
            except Exception as e:
                logger.error(f"Intent classification failed: {e}", exc_info=True)
                raise RoutingError(f"Intent classification failed: {e}")

            if not intent_candidates:
                raise RoutingError("No intent candidates found")

            best_intent = intent_candidates[0]
            logger.debug(
                f"Intent classified: {best_intent.intent} "
                f"(confidence: {best_intent.confidence:.2f})"
            )

            # Stage 2: Advanced Parameter Mapping
            try:
                mapping_rules = self._build_mapping_rules(best_intent.intent)
                parameter_schemas = self._build_parameter_schemas(best_intent.tool_name)

                # Build context with mapping configuration
                context_dict = (
                    classification_context.__dict__ if classification_context else {}
                )
                context_dict["gateway_config"] = self.parameter_mappings.get(
                    best_intent.intent, {}
                )

                mapped_parameters = await self.parameter_mapper.map_parameters(
                    request=request,
                    mapping_rules=mapping_rules,
                    parameter_schemas=parameter_schemas,
                    context=context_dict,
                )
                logger.debug(
                    f"Parameters mapped for {best_intent.tool_name}: "
                    f"{list(mapped_parameters.keys())}"
                )
            except Exception as e:
                logger.error(f"Parameter mapping failed: {e}", exc_info=True)
                raise RoutingError(f"Parameter mapping failed: {e}")

            # Stage 3: Tool Execution with Performance Monitoring
            try:
                execution_start = asyncio.get_event_loop().time()
                result = await self._execute_tool(
                    best_intent.tool_name, mapped_parameters
                )
                execution_time = (
                    asyncio.get_event_loop().time() - execution_start
                ) * 1000
            except Exception as e:
                logger.error(f"Tool execution failed: {e}", exc_info=True)
                raise RoutingError(f"Tool execution failed: {e}")

            total_time = (asyncio.get_event_loop().time() - start_time) * 1000

            # Update performance statistics
            self.routing_stats["successful_requests"] += 1
            self._update_performance_stats(total_time, best_intent.confidence)

            logger.info(
                f"Successfully routed {best_intent.tool_name} in {total_time:.2f}ms"
            )

            return RoutingResult(
                success=True,
                content=result,
                tool_name=best_intent.tool_name,
                execution_time_ms=total_time,
                confidence_score=best_intent.confidence,
                performance_metrics={
                    "classification_time": total_time - execution_time,
                    "execution_time": execution_time,
                    "intent_candidates": len(intent_candidates),
                    "parameters_mapped": len(mapped_parameters),
                },
            )

        except Exception as e:
            total_time = (asyncio.get_event_loop().time() - start_time) * 1000
            error_msg = str(e)

            self.routing_stats["failed_requests"] += 1
            logger.error(
                f"Gateway routing failed in {self.gateway_name}: {error_msg}",
                exc_info=True,
            )

            return RoutingResult(
                success=False,
                content=f"Routing failed: {error_msg}",
                tool_name="error",
                execution_time_ms=total_time,
                confidence_score=0.0,
                error_message=error_msg,
                performance_metrics={
                    "error_type": type(e).__name__,
                    "failure_stage": self._determine_failure_stage(e),
                },
            )

    def _build_classification_context(
        self, request: Dict[str, Any]
    ) -> Optional[ClassificationContext]:
        """Build classification context from request and session data."""
        try:
            # Debug logging
            logger.debug(
                f"Building context from request type: {type(request)}, "
                f"content: {request}"
            )

            # Extract context information from request
            session_context = request.get("session_context", {})
            user_preferences = request.get("user_preferences", {})

            # Handle nested context (e.g., request.context.project_id)
            context_data = request.get("context", {})
            if isinstance(context_data, dict):
                session_context.update(context_data)

            # Build context
            context = ClassificationContext(
                gateway_type=self.gateway_name,
                previous_intents=session_context.get("previous_intents", []),
                user_preferences=user_preferences,
                session_context=session_context,
                project_context=request.get("project_id")
                or session_context.get("current_project")
                or context_data.get("project_id"),
                task_context=request.get("task_id")
                or session_context.get("current_task")
                or context_data.get("task_id"),
            )

            logger.debug(f"Built context: {context}")
            return context

        except Exception as e:
            logger.error(f"Failed to build classification context: {e}", exc_info=True)
            return None

    def _build_mapping_rules(self, intent: str) -> List[MappingRule]:
        """Build parameter mapping rules for the given intent."""
        rules = []

        # Get mapping configuration for this intent
        mapping_config = self.parameter_mappings.get(intent, {})

        for target_param, source_path in mapping_config.items():
            rule = MappingRule(
                source_path=source_path,
                target_param=target_param,
                required=target_param in self._get_required_params(intent),
            )
            rules.append(rule)

        return rules

    def _build_parameter_schemas(self, tool_name: str) -> Dict[str, ParameterSchema]:
        """Build parameter schemas for the given tool."""
        schemas = {}

        # Get validation schema for this tool
        tool_schema = self.validation_schemas.get(tool_name, {})

        # Check if the schema already contains ParameterSchema objects
        # (e.g., from lackey_do gateway's custom conversion)
        if tool_schema and isinstance(
            next(iter(tool_schema.values()), None), ParameterSchema
        ):
            return tool_schema

        # Handle JSON Schema format
        if "properties" in tool_schema:
            properties = tool_schema["properties"]
            required_params = tool_schema.get("required", [])

            for param_name, param_config in properties.items():
                # Handle both dict and string parameter configs
                if isinstance(param_config, dict):
                    # Convert string type to ParameterType enum
                    type_str = param_config.get("type", "string")
                    # Map JSON Schema types to ParameterType enum
                    type_mapping = {
                        "array": "list",
                        "object": "dict",
                        "number": "float",
                    }
                    type_str = type_mapping.get(type_str, type_str)

                    try:
                        param_type = ParameterType(type_str)
                    except ValueError:
                        param_type = ParameterType.STRING

                    schema = ParameterSchema(
                        name=param_name,
                        param_type=param_type,
                        required=param_name in required_params,
                        default=param_config.get("default"),
                        min_length=param_config.get("minLength"),
                        max_length=param_config.get("maxLength"),
                        pattern=param_config.get("pattern"),
                        allowed_values=param_config.get("enum"),
                        description=param_config.get("description", ""),
                    )
                else:
                    # Handle string parameter configs
                    schema = ParameterSchema(
                        name=param_name,
                        param_type=ParameterType.STRING,
                        required=param_name in required_params,
                        default=None,
                        min_length=None,
                        max_length=None,
                        pattern=None,
                        allowed_values=None,
                        description="",
                    )
                schemas[param_name] = schema
        else:
            # Handle simple format (direct parameter mapping)
            for param_name, param_config in tool_schema.items():
                if isinstance(param_config, dict):
                    # Convert string type to ParameterType enum
                    type_str = param_config.get("type", "string")
                    try:
                        param_type = ParameterType(type_str)
                    except ValueError:
                        param_type = ParameterType.STRING

                    schema = ParameterSchema(
                        name=param_name,
                        param_type=param_type,
                        required=param_config.get("required", False),
                        default=param_config.get("default"),
                        min_length=param_config.get("min_length"),
                        max_length=param_config.get("max_length"),
                        pattern=param_config.get("pattern"),
                        allowed_values=param_config.get("allowed_values"),
                        description=param_config.get("description", ""),
                    )
                else:
                    # Handle string parameter configs
                    schema = ParameterSchema(
                        name=param_name,
                        param_type=ParameterType.STRING,
                        required=False,
                        default=None,
                        min_length=None,
                        max_length=None,
                        pattern=None,
                        allowed_values=None,
                        description="",
                    )
                schemas[param_name] = schema

        return schemas

    def _get_required_params(self, intent: str) -> List[str]:
        """Get list of required parameters for the given intent."""
        tool_name = self._intent_to_tool(intent)
        tool_schema = self.validation_schemas.get(tool_name, {})

        # Handle JSON Schema format (with "required" array)
        if "required" in tool_schema and isinstance(tool_schema["required"], list):
            return tool_schema["required"]

        # Handle simple format (with individual required flags)
        required_params = []
        properties = tool_schema.get("properties", {})
        for param_name, param_config in properties.items():
            if isinstance(param_config, dict) and param_config.get("required", False):
                required_params.append(param_name)

        # Fallback: check top-level parameters
        if not required_params:
            for param_name, param_config in tool_schema.items():
                if isinstance(param_config, dict) and param_config.get(
                    "required", False
                ):
                    required_params.append(param_name)

        return required_params

    def _update_performance_stats(
        self, response_time: float, confidence: float
    ) -> None:
        """Update performance statistics."""
        total_requests = self.routing_stats["total_requests"]

        # Update average response time
        current_avg = self.routing_stats["avg_response_time"]
        self.routing_stats["avg_response_time"] = (
            current_avg * (total_requests - 1) + response_time
        ) / total_requests

        # Update intent classification accuracy (simplified)
        current_accuracy = self.routing_stats["intent_classification_accuracy"]
        self.routing_stats["intent_classification_accuracy"] = (
            current_accuracy * (total_requests - 1) + confidence
        ) / total_requests

    def _determine_failure_stage(self, error: Exception) -> str:
        """Determine which stage of routing failed."""
        error_msg = str(error).lower()

        if "intent" in error_msg or "classify" in error_msg:
            return "intent_classification"
        elif "parameter" in error_msg or "mapping" in error_msg:
            return "parameter_mapping"
        elif "validation" in error_msg:
            return "parameter_validation"
        elif "tool" in error_msg or "execute" in error_msg:
            return "tool_execution"
        else:
            return "unknown"

    async def _classify_intent(self, request: Dict[str, Any]) -> IntentMatch:
        """Legacy method for backward compatibility.

        Uses advanced classifier for intent classification.
        """
        context = self._build_classification_context(request)
        candidates = await self.intent_classifier.classify_intent(
            query_text=self._extract_query_text(request),
            intent_patterns=self.intent_patterns,
            context=context,
        )

        if not candidates:
            raise RoutingError("Unable to classify intent from request")

        best_candidate = candidates[0]

        return IntentMatch(
            intent=best_candidate.intent,
            confidence=best_candidate.confidence,
            tool_name=best_candidate.tool_name,
            parameters={},
            gateway_type=self.gateway_name,
            validation_schema=self.validation_schemas.get(best_candidate.tool_name),
            parameter_mappings=self.parameter_mappings.get(best_candidate.intent, {}),
        )

    def _extract_query_text(self, request: Dict[str, Any]) -> str:
        """Extract query text from request based on gateway type."""
        # Try query field first (common across all gateways)
        if "query" in request:
            return str(request["query"])

        if self.gateway_name == "lackey_do":
            action = request.get("action", "")
            target = request.get("target", "")
            return f"{action} {target}".strip()
        elif self.gateway_name == "lackey_analyze":
            analysis_type = request.get("analysis_type", "")
            return f"analyze {analysis_type}".strip()
        else:
            # Fallback: concatenate all string values
            text_parts = []
            for value in request.values():
                if isinstance(value, str):
                    text_parts.append(value)
            return " ".join(text_parts)

    async def _map_parameters(
        self, request: Dict[str, Any], intent_match: IntentMatch
    ) -> Dict[str, Any]:
        """Legacy method for backward compatibility.

        Uses advanced mapper internally for parameter mapping.
        """
        mapping_rules = self._build_mapping_rules(intent_match.intent)
        parameter_schemas = self._build_parameter_schemas(intent_match.tool_name)
        context = self._build_classification_context(request)

        return await self.parameter_mapper.map_parameters(
            request=request,
            mapping_rules=mapping_rules,
            parameter_schemas=parameter_schemas,
            context=context.__dict__ if context else None,
        )

    async def _validate_parameters(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Legacy method for backward compatibility.

        Validation is now handled in parameter mapping.
        """
        # Parameters are already validated in the advanced parameter mapper
        return parameters

    async def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute the specified tool with mapped parameters."""
        if tool_name not in self.tool_registry:
            available_tools = list(self.tool_registry.keys())
            raise RoutingError(
                f"Tool '{tool_name}' not found in {self.gateway_name} registry. "
                f"Available tools: {', '.join(available_tools)}"
            )

        tool_function = self.tool_registry[tool_name]

        try:
            # Execute the tool function
            if asyncio.iscoroutinefunction(tool_function):
                result = await tool_function(**parameters)
            else:
                result = tool_function(**parameters)

            return result

        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name}: {e}")
            raise RoutingError(f"Tool execution failed: {str(e)}")

    def _intent_to_tool(self, intent: str) -> str:
        """Map intent name to tool name (direct mapping by default)."""
        return intent

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics for monitoring."""
        base_metrics = {
            "routing_stats": self.routing_stats.copy(),
            "intent_classifier_stats": self.intent_classifier.get_performance_stats(),
            "parameter_mapper_stats": self.parameter_mapper.get_performance_stats(),
        }

        # Calculate derived metrics
        total_requests = self.routing_stats["total_requests"]
        if total_requests > 0:
            success_rate = self.routing_stats["successful_requests"] / total_requests
            failure_rate = self.routing_stats["failed_requests"] / total_requests
        else:
            success_rate = 0.0
            failure_rate = 0.0

        # Add calculated metrics
        result_metrics: Dict[str, Any] = base_metrics.copy()
        result_metrics.update(
            {"success_rate": success_rate, "failure_rate": failure_rate}
        )

        return result_metrics

    def clear_caches(self) -> None:
        """Clear all caches for memory management."""
        self.intent_classifier.clear_cache()
        self.parameter_mapper.clear_cache()
        logger.debug(f"Cleared caches for {self.gateway_name} gateway")

    def reset_performance_stats(self) -> None:
        """Reset performance statistics."""
        self.routing_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "intent_classification_accuracy": 0.0,
        }
        logger.debug(f"Reset performance stats for {self.gateway_name} gateway")
