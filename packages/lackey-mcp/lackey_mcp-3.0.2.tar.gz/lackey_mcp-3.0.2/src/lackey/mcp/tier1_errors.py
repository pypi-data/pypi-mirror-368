"""Tier 1 error response system with minimal schema disclosure.

Provides basic error responses that identify missing required parameters
while maintaining minimal information disclosure for security.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class DisclosureLevel(Enum):
    """Schema disclosure levels for error responses."""

    TIER1 = 1  # Minimal: required params only
    TIER2 = 2  # Standard: required + optional
    TIER3 = 3  # Full: complete schema with constraints


@dataclass
class Tier1ErrorResponse:
    """Minimal error response with basic parameter information."""

    error_type: str
    message: str
    missing_required: List[str]
    parameter_hints: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "error": self.error_type,
            "message": self.message,
            "missing_required": self.missing_required,
            "parameter_hints": self.parameter_hints,
        }


class Tier1ErrorGenerator:
    """Generates Tier 1 error responses with minimal disclosure."""

    def __init__(self) -> None:
        """Initialize with basic type mappings."""
        self._basic_types = {
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

    def generate_missing_parameter_error(
        self, tool_name: str, missing_params: List[str], schema: Dict[str, Any]
    ) -> Tier1ErrorResponse:
        """Generate error for missing required parameters."""
        # Get basic type hints for missing parameters
        types = schema.get("types", {})
        hints = {}

        for param in missing_params:
            param_type = types.get(param, "any")
            hints[param] = self._simplify_type(param_type)

        message = (
            f"Missing required parameters for {tool_name}: {', '.join(missing_params)}"
        )

        return Tier1ErrorResponse(
            error_type="missing_parameters",
            message=message,
            missing_required=missing_params,
            parameter_hints=hints,
        )

    def generate_invalid_parameter_error(
        self, tool_name: str, invalid_param: str, schema: Dict[str, Any]
    ) -> Tier1ErrorResponse:
        """Generate error for invalid parameter value."""
        types = schema.get("types", {})
        param_type = types.get(invalid_param, "any")
        hint = self._simplify_type(param_type)

        message = f"Invalid value for parameter '{invalid_param}' in {tool_name}"

        return Tier1ErrorResponse(
            error_type="invalid_parameter",
            message=message,
            missing_required=[],
            parameter_hints={invalid_param: hint},
        )

    def _simplify_type(self, type_info: Any) -> str:
        """Simplify type information for Tier 1 disclosure."""
        if isinstance(type_info, str):
            return self._basic_types.get(type_info.lower(), "value")
        elif isinstance(type_info, dict):
            return "object"
        elif isinstance(type_info, list):
            return "list"
        else:
            return "value"


def validate_required_parameters(
    parameters: Dict[str, Any], schema: Dict[str, Any]
) -> Optional[List[str]]:
    """Validate required parameters and return missing ones."""
    required = schema.get("required", [])
    missing = []

    for param in required:
        if param not in parameters or parameters[param] is None:
            missing.append(param)

    return missing if missing else None


def generate_tier1_error_response(
    tool_name: str, error_type: str, parameters: Dict[str, Any], schema: Dict[str, Any]
) -> str:
    """Generate a formatted Tier 1 error response."""
    generator = Tier1ErrorGenerator()

    if error_type == "missing_parameters":
        missing = validate_required_parameters(parameters, schema)
        if missing:
            error_response = generator.generate_missing_parameter_error(
                tool_name, missing, schema
            )
            missing_params = ", ".join(
                f"{p} ({error_response.parameter_hints[p]})" for p in missing
            )
            return f"❌ {error_response.message}\nRequired: {missing_params}"

    elif error_type == "invalid_parameter":
        # Find first invalid parameter (simplified)
        for param, value in parameters.items():
            if value is not None:  # Basic validation
                error_response = generator.generate_invalid_parameter_error(
                    tool_name, param, schema
                )
                hint = error_response.parameter_hints.get(param, "value")
                return f"❌ {error_response.message}\nExpected: {param} ({hint})"

    return f"❌ Error in {tool_name}: Please check your parameters"
