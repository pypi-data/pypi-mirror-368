"""Enhanced gateway router with progressive schema disclosure and validation.

Integrates schema validation, progressive error responses, and pure schema discovery
while maintaining clean separation between schema and data operations.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .gateway_router import GatewayRouter, RoutingError, RoutingResult
from .gateway_schemas import get_schemas_for_gateway
from .lackey_suggest import lackey_suggest
from .lackey_validate import lackey_validate
from .tier1_errors import generate_tier1_error_response
from .tier2_errors import generate_tier2_error_response
from .tier3_errors import generate_tier3_error_response

logger = logging.getLogger(__name__)


class DisclosureLevel(Enum):
    """Schema disclosure levels for progressive responses."""

    TIER1 = "tier1"  # Minimal disclosure
    TIER2 = "tier2"  # Standard disclosure
    TIER3 = "tier3"  # Complete disclosure


@dataclass
class ValidationResult:
    """Result of schema validation."""

    valid: bool
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    disclosure_level: DisclosureLevel


@dataclass
class SchemaDiscoveryResult:
    """Result of pure schema discovery."""

    schema: Dict[str, Any]
    examples: List[Dict[str, Any]]
    relationships: Dict[str, List[str]]
    disclosure_level: DisclosureLevel


class EnhancedGatewayRouter(GatewayRouter):
    """Enhanced gateway router with schema validation and progressive disclosure."""

    def __init__(
        self,
        gateway_name: str,
        default_disclosure_level: DisclosureLevel = DisclosureLevel.TIER2,
        **kwargs: Any,
    ) -> None:
        """Initialize enhanced gateway router."""
        super().__init__(gateway_name, **kwargs)
        self.default_disclosure_level = default_disclosure_level
        self.gateway_schemas = get_schemas_for_gateway(gateway_name)

        # Schema validation layer
        self.schema_validator = lackey_validate
        self.schema_suggester = lackey_suggest

        logger.info(
            f"Enhanced {gateway_name} gateway initialized with schema validation"
        )

    async def route_request_with_validation(
        self,
        request: Dict[str, Any],
        disclosure_level: Optional[DisclosureLevel] = None,
    ) -> RoutingResult:
        """Route request with integrated schema validation."""
        disclosure_level = disclosure_level or self.default_disclosure_level

        try:
            # Extract tool and parameters
            tool_name = self._extract_tool_name(request)
            parameters = self._extract_parameters(request)

            # Schema validation layer
            validation_result = await self._validate_with_schema(
                tool_name, parameters, disclosure_level
            )

            if not validation_result.valid:
                return self._create_validation_error_result(
                    tool_name, validation_result, disclosure_level
                )

            # Proceed with normal routing if validation passes
            return await self.route_request(request)

        except Exception as e:
            logger.error(f"Enhanced routing failed: {e}", exc_info=True)
            return self._create_error_result(str(e), disclosure_level)

    async def discover_schema(
        self,
        tool_name: Optional[str] = None,
        disclosure_level: DisclosureLevel = DisclosureLevel.TIER2,
    ) -> SchemaDiscoveryResult:
        """Pure schema discovery without data contamination."""
        if tool_name:
            # Discover specific tool schema
            schema = self.gateway_schemas.get(tool_name, {})
            if not schema:
                raise RoutingError(
                    f"Tool '{tool_name}' not found in {self.gateway_name}"
                )

            # Generate examples and relationships
            examples = self._generate_schema_examples(
                tool_name, schema, disclosure_level
            )
            relationships = self._analyze_schema_relationships(schema)

            return SchemaDiscoveryResult(
                schema=self._apply_disclosure_filter(schema, disclosure_level),
                examples=examples,
                relationships=relationships,
                disclosure_level=disclosure_level,
            )
        else:
            # Discover all gateway schemas
            filtered_schemas = {}
            for name, schema in self.gateway_schemas.items():
                filtered_schemas[name] = self._apply_disclosure_filter(
                    schema, disclosure_level
                )

            return SchemaDiscoveryResult(
                schema=filtered_schemas,
                examples=[],
                relationships={},
                disclosure_level=disclosure_level,
            )

    async def suggest_parameters(
        self, tool_name: str, partial_parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Suggest parameters using integrated suggestion system."""
        return self.schema_suggester.suggest_parameters(
            tool_name, partial_parameters, self.gateway_name
        )

    async def validate_parameters(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        disclosure_level: DisclosureLevel = DisclosureLevel.TIER2,
    ) -> ValidationResult:
        """Validate parameters with progressive disclosure."""
        validation_result = self.schema_validator.validate_parameters(
            tool_name, parameters, self.gateway_name
        )

        # Convert to enhanced result with disclosure level
        return ValidationResult(
            valid=validation_result.get("valid", False),
            issues=validation_result.get("issues", []),
            suggestions=self._generate_progressive_suggestions(
                validation_result, disclosure_level
            ),
            disclosure_level=disclosure_level,
        )

    async def _validate_with_schema(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        disclosure_level: DisclosureLevel,
    ) -> ValidationResult:
        """Validate parameters using internal schema with disclosure level."""
        schema = self.gateway_schemas.get(tool_name)
        if not schema:
            return ValidationResult(
                valid=False,
                issues=[{"error": f"Tool '{tool_name}' not found"}],
                suggestions=[f"Available tools: {list(self.gateway_schemas.keys())}"],
                disclosure_level=disclosure_level,
            )

        # Use integrated validation
        validation_result = self.schema_validator.validate_parameters(
            tool_name, parameters, self.gateway_name
        )

        return ValidationResult(
            valid=validation_result.get("valid", False),
            issues=validation_result.get("issues", []),
            suggestions=self._generate_progressive_suggestions(
                validation_result, disclosure_level
            ),
            disclosure_level=disclosure_level,
        )

    def _create_validation_error_result(
        self,
        tool_name: str,
        validation_result: ValidationResult,
        disclosure_level: DisclosureLevel,
    ) -> RoutingResult:
        """Create routing result for validation errors with progressive disclosure."""
        schema = self.gateway_schemas.get(tool_name, {})

        # Generate progressive error response
        if disclosure_level == DisclosureLevel.TIER1:
            error_message = generate_tier1_error_response(
                tool_name, "missing_parameters", {}, schema
            )
        elif disclosure_level == DisclosureLevel.TIER2:
            error_message = generate_tier2_error_response(
                tool_name, "missing_parameters", {}, schema
            )
        else:  # TIER3
            error_message = generate_tier3_error_response(
                tool_name, "missing_parameters", {}, schema
            )

        return RoutingResult(
            success=False,
            content={"error": error_message, "validation_result": validation_result},
            tool_name=tool_name,
            execution_time_ms=0.0,
            confidence_score=0.0,
            error_message=error_message,
        )

    def _create_error_result(
        self, error_message: str, disclosure_level: DisclosureLevel
    ) -> RoutingResult:
        """Create error result with appropriate disclosure level."""
        return RoutingResult(
            success=False,
            content={
                "error": error_message,
                "disclosure_level": disclosure_level.value,
            },
            tool_name="unknown",
            execution_time_ms=0.0,
            confidence_score=0.0,
            error_message=error_message,
        )

    def _apply_disclosure_filter(
        self, schema: Dict[str, Any], disclosure_level: DisclosureLevel
    ) -> Dict[str, Any]:
        """Apply disclosure level filtering to schema."""
        if disclosure_level == DisclosureLevel.TIER1:
            # Minimal disclosure - only required parameters and basic types
            return {
                "required": schema.get("required", []),
                "types": {k: "any" for k in schema.get("required", [])},
            }
        elif disclosure_level == DisclosureLevel.TIER2:
            # Standard disclosure - required, optional, types, basic constraints
            return {
                "required": schema.get("required", []),
                "optional": schema.get("optional", {}),
                "types": schema.get("types", {}),
                "descriptions": schema.get("descriptions", {}),
            }
        else:  # TIER3
            # Complete disclosure - everything
            return schema.copy()

    def _generate_schema_examples(
        self, tool_name: str, schema: Dict[str, Any], disclosure_level: DisclosureLevel
    ) -> List[Dict[str, Any]]:
        """Generate schema examples based on disclosure level."""
        if disclosure_level == DisclosureLevel.TIER1:
            # Minimal examples
            required = schema.get("required", [])
            if required:
                return [
                    {
                        "description": "Basic usage",
                        "parameters": {p: "value" for p in required},
                    }
                ]
        elif disclosure_level == DisclosureLevel.TIER2:
            # Standard examples with suggestions
            suggestions = self.schema_suggester.suggest_parameters(
                tool_name, {}, self.gateway_name
            )
            examples = suggestions.get("usage_examples", [])
            return examples if isinstance(examples, list) else []
        else:  # TIER3
            # Comprehensive examples
            suggestions = self.schema_suggester.suggest_parameters(
                tool_name, {}, self.gateway_name
            )
            examples = suggestions.get("usage_examples", [])
            return examples if isinstance(examples, list) else []

        return []

    def _analyze_schema_relationships(
        self, schema: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Analyze parameter relationships in schema."""
        relationships = {}
        types = schema.get("types", {})

        # Simple relationship detection
        for param in types:
            if "project_id" in param:
                relationships[param] = ["task_id", "project_name"]
            elif "task_id" in param:
                relationships[param] = ["project_id"]

        return relationships

    def _generate_progressive_suggestions(
        self, validation_result: Dict[str, Any], disclosure_level: DisclosureLevel
    ) -> List[str]:
        """Generate suggestions based on disclosure level."""
        base_suggestions = validation_result.get("suggestions", [])
        if not isinstance(base_suggestions, list):
            base_suggestions = []

        if disclosure_level == DisclosureLevel.TIER1:
            return list(base_suggestions[:2])  # Limit to 2 suggestions
        elif disclosure_level == DisclosureLevel.TIER2:
            return list(base_suggestions[:5])  # Limit to 5 suggestions
        else:  # TIER3
            return list(base_suggestions)  # All suggestions

    def _extract_tool_name(self, request: Dict[str, Any]) -> str:
        """Extract tool name from request."""
        tool_name = request.get("tool", request.get("action", "unknown"))
        return str(tool_name) if tool_name else "unknown"

    def _extract_parameters(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Extract parameters from request."""
        params = request.get("data", request.get("parameters", {}))
        return params if isinstance(params, dict) else {}


class SchemaValidationLayer:
    """Dedicated schema validation layer for clean separation."""

    def __init__(self, gateway_name: str):
        """Initialize validation layer."""
        self.gateway_name = gateway_name
        self.schemas = get_schemas_for_gateway(gateway_name)
        self.validator = lackey_validate

    async def validate_request(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        disclosure_level: DisclosureLevel = DisclosureLevel.TIER2,
    ) -> Tuple[bool, Optional[str]]:
        """Validate request and return result with appropriate error message."""
        if tool_name not in self.schemas:
            return False, f"Tool '{tool_name}' not found in {self.gateway_name} gateway"

        validation_result = self.validator.validate_parameters(
            tool_name, parameters, self.gateway_name
        )

        if validation_result.get("valid", False):
            return True, None

        # Generate progressive error response
        schema = self.schemas[tool_name]

        if disclosure_level == DisclosureLevel.TIER1:
            error_msg = generate_tier1_error_response(
                tool_name, "missing_parameters", parameters, schema
            )
        elif disclosure_level == DisclosureLevel.TIER2:
            error_msg = generate_tier2_error_response(
                tool_name, "missing_parameters", parameters, schema
            )
        else:  # TIER3
            error_msg = generate_tier3_error_response(
                tool_name, "missing_parameters", parameters, schema
            )

        return False, error_msg

    def maintain_schema_data_separation(self) -> bool:
        """Verify clean separation between schema and data operations."""
        # This method ensures that schema operations never reference actual data
        # All schema operations work purely on structural definitions

        for tool_name, schema in self.schemas.items():
            # Verify schema contains no actual data references
            if self._contains_data_references(schema):
                logger.warning(f"Schema for {tool_name} may contain data references")
                return False

        return True

    def _contains_data_references(self, schema: Dict[str, Any]) -> bool:
        """Check if schema contains actual data references."""
        # Simple check for common data reference patterns
        schema_str = str(schema).lower()
        data_indicators = [
            "actual_",
            "real_",
            "current_",
            "existing_",
            "database",
            "table",
            "record",
            "row",
        ]

        return any(indicator in schema_str for indicator in data_indicators)
