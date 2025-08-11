"""lackey_schema gateway for pure schema introspection."""

import logging
from typing import Any, Dict, List, Optional

from ..gateway_router import GatewayRouter
from ..gateway_schemas import (
    LACKEY_ANALYZE_SCHEMAS,
    LACKEY_DO_SCHEMAS,
    LACKEY_GET_SCHEMAS,
)
from ..lackey_suggest import lackey_suggest
from ..lackey_validate import lackey_validate

logger = logging.getLogger(__name__)


class LackeySchemaGateway(GatewayRouter):
    """Gateway for schema introspection operations."""

    def __init__(self, core_instance: Any = None) -> None:
        """Initialize the lackey_schema gateway."""
        self._core_instance = core_instance
        super().__init__(gateway_name="lackey_schema")

    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load intent classification patterns for schema operations."""
        return {
            "get_gateway_schema": [
                "get schema",
                "show schema",
                "gateway schema",
                "tool schema",
                "parameter schema",
                "schema info",
                "describe schema",
            ],
            "get_tool_schema": [
                "tool parameters",
                "parameter info",
                "tool schema",
                "parameter schema",
                "tool details",
            ],
            "list_available_tools": [
                "list tools",
                "available tools",
                "show tools",
                "tool list",
            ],
            "suggest_parameters": [
                "suggest parameters",
                "parameter suggestions",
                "help with parameters",
                "what parameters",
                "parameter help",
                "suggest params",
            ],
            "suggest_next_parameter": [
                "next parameter",
                "what's next",
                "next param",
                "suggest next",
                "what parameter next",
                "continue parameters",
            ],
            "analyze_parameter_structure": [
                "analyze parameters",
                "parameter structure",
                "parameter analysis",
                "structure analysis",
                "parameter info",
            ],
            "validate_parameters": [
                "validate parameters",
                "check parameters",
                "parameter validation",
                "validate",
                "check params",
                "verify parameters",
            ],
            "validate_structure": [
                "validate structure",
                "check structure",
                "structure validation",
                "verify structure",
                "structure check",
            ],
            "get_validation_guidance": [
                "validation guidance",
                "validation help",
                "parameter guidance",
                "validation advice",
                "help validate",
                "guide validation",
            ],
        }

    def _load_parameter_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load parameter mappings for schema operations."""
        return {
            "get_gateway_schema": {
                "gateway": "gateway_name",
                "level": "disclosure_level",
            },
            "get_tool_schema": {
                "tool": "tool_name",
                "gateway": "gateway_name",
                "level": "disclosure_level",
            },
            "suggest_parameters": {
                "tool": "tool_name",
                "gateway": "gateway_name",
                "params": "partial_params",
            },
            "suggest_next_parameter": {
                "tool": "tool_name",
                "gateway": "gateway_name",
                "current": "current_params",
            },
            "analyze_parameter_structure": {
                "tool": "tool_name",
                "gateway": "gateway_name",
            },
            "validate_parameters": {
                "tool": "tool_name",
                "params": "parameters",
                "gateway": "gateway_name",
            },
            "validate_structure": {
                "tool": "tool_name",
                "params": "parameters",
                "gateway": "gateway_name",
            },
            "get_validation_guidance": {
                "tool": "tool_name",
                "params": "parameters",
                "gateway": "gateway_name",
            },
        }

    def _load_validation_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load validation schemas for schema operations."""
        return {
            "get_gateway_schema": {
                "required": ["gateway_name"],
                "optional": {"disclosure_level": "tier2"},
                "types": {"gateway_name": "str", "disclosure_level": "str"},
            },
            "get_tool_schema": {
                "required": ["tool_name"],
                "optional": {"gateway_name": None, "disclosure_level": "tier2"},
                "types": {
                    "tool_name": "str",
                    "gateway_name": "optional[str]",
                    "disclosure_level": "str",
                },
            },
            "list_available_tools": {
                "required": [],
                "optional": {"gateway_name": None},
                "types": {"gateway_name": "optional[str]"},
            },
            "suggest_parameters": {
                "required": ["tool_name"],
                "optional": {"partial_params": None, "gateway": None},
                "types": {
                    "tool_name": "str",
                    "partial_params": "optional[dict]",
                    "gateway": "optional[str]",
                },
            },
            "suggest_next_parameter": {
                "required": ["tool_name", "current_params"],
                "optional": {"gateway": None},
                "types": {
                    "tool_name": "str",
                    "current_params": "dict",
                    "gateway": "optional[str]",
                },
            },
            "analyze_parameter_structure": {
                "required": ["tool_name"],
                "optional": {"gateway": None},
                "types": {"tool_name": "str", "gateway": "optional[str]"},
            },
            "validate_parameters": {
                "required": ["tool_name", "parameters"],
                "optional": {"gateway": None},
                "types": {
                    "tool_name": "str",
                    "parameters": "dict",
                    "gateway": "optional[str]",
                },
            },
            "validate_structure": {
                "required": ["tool_name", "parameters"],
                "optional": {"gateway": None},
                "types": {
                    "tool_name": "str",
                    "parameters": "dict",
                    "gateway": "optional[str]",
                },
            },
            "get_validation_guidance": {
                "required": ["tool_name", "parameters"],
                "optional": {"gateway": None},
                "types": {
                    "tool_name": "str",
                    "parameters": "dict",
                    "gateway": "optional[str]",
                },
            },
        }

    def _load_tool_registry(self) -> Dict[str, Any]:
        """Load tool registry for schema operations."""
        return {
            "get_gateway_schema": self.get_gateway_schema,
            "get_tool_schema": self.get_tool_schema,
            "list_available_tools": self.list_available_tools,
            "suggest_parameters": self.suggest_parameters,
            "suggest_next_parameter": self.suggest_next_parameter,
            "analyze_parameter_structure": self.analyze_parameter_structure,
            "validate_parameters": self.validate_parameters,
            "validate_structure": self.validate_structure,
            "get_validation_guidance": self.get_validation_guidance,
        }

    async def get_gateway_schema(
        self, gateway_name: str, disclosure_level: str = "tier2"
    ) -> Dict[str, Any]:
        """Get complete schema for a gateway at specified disclosure level."""
        schema_map = {
            "lackey_get": LACKEY_GET_SCHEMAS,
            "lackey_do": LACKEY_DO_SCHEMAS,
            "lackey_analyze": LACKEY_ANALYZE_SCHEMAS,
        }

        if gateway_name not in schema_map:
            raise ValueError(f"Unknown gateway: {gateway_name}")

        schemas = schema_map[gateway_name]
        filtered_schemas = {}
        for tool_name, schema in schemas.items():
            filtered_schemas[tool_name] = self._apply_disclosure_level(
                schema, disclosure_level
            )

        return {
            "gateway": gateway_name,
            "disclosure_level": disclosure_level,
            "tools": filtered_schemas,
            "tool_count": len(filtered_schemas),
        }

    async def get_tool_schema(
        self,
        tool_name: str,
        gateway_name: Optional[str] = None,
        disclosure_level: str = "tier2",
    ) -> Dict[str, Any]:
        """Get schema for a specific tool at specified disclosure level."""
        all_schemas = {
            "lackey_get": LACKEY_GET_SCHEMAS,
            "lackey_do": LACKEY_DO_SCHEMAS,
            "lackey_analyze": LACKEY_ANALYZE_SCHEMAS,
        }

        found_schema = None
        found_gateway = None

        if gateway_name:
            if gateway_name in all_schemas and tool_name in all_schemas[gateway_name]:
                found_schema = all_schemas[gateway_name][tool_name]
                found_gateway = gateway_name
        else:
            for gw_name, schemas in all_schemas.items():
                if tool_name in schemas:
                    found_schema = schemas[tool_name]
                    found_gateway = gw_name
                    break

        if not found_schema:
            available_tools = []
            for schemas in all_schemas.values():
                available_tools.extend(list(schemas.keys()))
            raise ValueError(
                f"Tool '{tool_name}' not found. Available: "
                f"{', '.join(sorted(available_tools))}"
            )

        filtered_schema = self._apply_disclosure_level(found_schema, disclosure_level)

        return {
            "tool_name": tool_name,
            "gateway": found_gateway,
            "disclosure_level": disclosure_level,
            "schema": filtered_schema,
        }

    async def list_available_tools(
        self, gateway_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """List all available tools, optionally filtered by gateway."""
        all_schemas = {
            "lackey_get": LACKEY_GET_SCHEMAS,
            "lackey_do": LACKEY_DO_SCHEMAS,
            "lackey_analyze": LACKEY_ANALYZE_SCHEMAS,
        }

        if gateway_name:
            if gateway_name not in all_schemas:
                raise ValueError(f"Unknown gateway: {gateway_name}")
            tools = list(all_schemas[gateway_name].keys())
            return {
                "gateway": gateway_name,
                "tools": sorted(tools),
                "tool_count": len(tools),
            }
        else:
            tools_by_gateway = {}
            total_count = 0
            for gw_name, schemas in all_schemas.items():
                tools = sorted(list(schemas.keys()))
                tools_by_gateway[gw_name] = tools
                total_count += len(tools)
            return {
                "tools_by_gateway": tools_by_gateway,
                "total_tool_count": total_count,
                "gateway_count": len(tools_by_gateway),
            }

    def _apply_disclosure_level(
        self, schema: Dict[str, Any], disclosure_level: str
    ) -> Dict[str, Any]:
        """Apply disclosure level filtering to schema."""
        if disclosure_level == "tier1":
            return {
                "required": schema.get("required", []),
                "types": {
                    param: self._simplify_type(param_type)
                    for param, param_type in schema.get("types", {}).items()
                    if param in schema.get("required", [])
                },
            }
        elif disclosure_level == "tier2":
            result = {
                "required": schema.get("required", []),
                "optional": schema.get("optional", {}),
                "types": schema.get("types", {}),
            }
            if "descriptions" in schema:
                result["descriptions"] = schema["descriptions"]
            return result
        elif disclosure_level == "tier3":
            return schema.copy()
        else:
            raise ValueError(f"Invalid disclosure level: {disclosure_level}")

    def _simplify_type(self, type_info: Any) -> str:
        """Simplify type information for Tier 1 disclosure."""
        basic_types = {
            "str": "text",
            "string": "text",
            "int": "number",
            "integer": "number",
            "float": "number",
            "bool": "true/false",
            "boolean": "true/false",
            "list": "list",
            "dict": "object",
            "uuid": "id",
        }
        if isinstance(type_info, str):
            return basic_types.get(type_info.lower(), "value")
        return "value"

    async def suggest_parameters(
        self,
        tool_name: str,
        partial_params: Optional[Dict[str, Any]] = None,
        gateway: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Suggest parameters for a tool based on schema analysis."""
        return lackey_suggest.suggest_parameters(tool_name, partial_params, gateway)

    async def suggest_next_parameter(
        self,
        tool_name: str,
        current_params: Dict[str, Any],
        gateway: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Suggest the next most logical parameter to provide."""
        return lackey_suggest.suggest_next_parameter(tool_name, current_params, gateway)

    async def analyze_parameter_structure(
        self, tool_name: str, gateway: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze parameter structure without data references."""
        return lackey_suggest.analyze_parameter_structure(tool_name, gateway)

    async def validate_parameters(
        self, tool_name: str, parameters: Dict[str, Any], gateway: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate parameters against tool schema without execution."""
        return lackey_validate.validate_parameters(tool_name, parameters, gateway)

    async def validate_structure(
        self, tool_name: str, parameters: Dict[str, Any], gateway: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate parameter structure and relationships."""
        return lackey_validate.validate_structure(tool_name, parameters, gateway)

    async def get_validation_guidance(
        self, tool_name: str, parameters: Dict[str, Any], gateway: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get comprehensive validation guidance without execution."""
        return lackey_validate.get_validation_guidance(tool_name, parameters, gateway)
