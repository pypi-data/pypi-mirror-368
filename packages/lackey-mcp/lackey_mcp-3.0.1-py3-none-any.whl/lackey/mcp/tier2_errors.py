"""Tier 2 error response system with standard schema disclosure.

Provides detailed error responses that include both required and optional parameters
with descriptions while maintaining standard disclosure level for security.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ParameterInfo:
    """Detailed parameter information for Tier 2 responses."""

    name: str
    type: str
    required: bool
    description: str
    default: Optional[Any] = None
    constraints: Optional[Dict[str, Any]] = None


@dataclass
class Tier2ErrorResponse:
    """Standard error response with detailed parameter information."""

    error_type: str
    message: str
    missing_required: List[str]
    parameter_details: Dict[str, ParameterInfo]
    optional_parameters: List[str]
    suggestions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "error": self.error_type,
            "message": self.message,
            "missing_required": self.missing_required,
            "parameter_details": {
                name: {
                    "type": info.type,
                    "required": info.required,
                    "description": info.description,
                    "default": info.default,
                    "constraints": info.constraints,
                }
                for name, info in self.parameter_details.items()
            },
            "optional_parameters": self.optional_parameters,
            "suggestions": self.suggestions,
        }


class Tier2ErrorGenerator:
    """Generates Tier 2 error responses with standard disclosure."""

    def __init__(self) -> None:
        """Initialize with enhanced type mappings and descriptions."""
        self._type_descriptions = {
            "str": "text string",
            "string": "text string",
            "int": "integer number",
            "integer": "integer number",
            "float": "decimal number",
            "bool": "true or false",
            "boolean": "true or false",
            "list": "array of values",
            "dict": "object with key-value pairs",
            "uuid": "unique identifier",
            "datetime": "date and time",
            "date": "date (YYYY-MM-DD)",
            "time": "time (HH:MM:SS)",
            "email": "email address",
            "url": "web address",
        }

        self._constraint_descriptions = {
            "min_length": "minimum {value} characters",
            "max_length": "maximum {value} characters",
            "min_value": "minimum value {value}",
            "max_value": "maximum value {value}",
            "pattern": "must match pattern: {value}",
            "enum": "must be one of: {value}",
            "format": "must be in {value} format",
        }

    def generate_missing_parameter_error(
        self, tool_name: str, missing_params: List[str], schema: Dict[str, Any]
    ) -> Tier2ErrorResponse:
        """Generate detailed error for missing required parameters."""
        # Extract parameter details from schema
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        parameter_details = {}
        optional_parameters = []
        suggestions = []

        # Process all parameters to provide comprehensive information
        for param_name, param_schema in properties.items():
            is_required = param_name in required
            param_info = self._extract_parameter_info(
                param_name, param_schema, is_required
            )
            parameter_details[param_name] = param_info

            if not is_required:
                optional_parameters.append(param_name)

        # Generate helpful suggestions
        if missing_params:
            suggestions.append(f"Provide values for: {', '.join(missing_params)}")

        if optional_parameters:
            suggestions.append(
                f"Optional parameters available: {', '.join(optional_parameters[:3])}"
                + ("..." if len(optional_parameters) > 3 else "")
            )

        message = (
            f"Missing required parameters for {tool_name}: "
            f"{', '.join(missing_params)}. "
            f"See parameter_details for type information and descriptions."
        )

        return Tier2ErrorResponse(
            error_type="missing_parameters",
            message=message,
            missing_required=missing_params,
            parameter_details=parameter_details,
            optional_parameters=optional_parameters,
            suggestions=suggestions,
        )

    def generate_invalid_parameter_error(
        self,
        tool_name: str,
        invalid_param: str,
        invalid_value: Any,
        schema: Dict[str, Any],
    ) -> Tier2ErrorResponse:
        """Generate detailed error for invalid parameter value."""
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        param_schema = properties.get(invalid_param, {})

        is_required = invalid_param in required
        param_info = self._extract_parameter_info(
            invalid_param, param_schema, is_required
        )

        # Generate specific error message based on constraint violation
        constraint_msg = self._get_constraint_violation_message(
            invalid_param, invalid_value, param_schema
        )

        message = (
            f"Invalid value for parameter '{invalid_param}' in {tool_name}: "
            f"{constraint_msg}"
        )

        suggestions = [
            f"Expected type: {param_info.type}",
            f"Description: {param_info.description}",
        ]

        if param_info.constraints:
            suggestions.extend(
                self._format_constraint_suggestions(param_info.constraints)
            )

        return Tier2ErrorResponse(
            error_type="invalid_parameter",
            message=message,
            missing_required=[],
            parameter_details={invalid_param: param_info},
            optional_parameters=[],
            suggestions=suggestions,
        )

    def generate_type_mismatch_error(
        self,
        tool_name: str,
        param_name: str,
        expected_type: str,
        actual_value: Any,
        schema: Dict[str, Any],
    ) -> Tier2ErrorResponse:
        """Generate error for parameter type mismatch."""
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        param_schema = properties.get(param_name, {})

        is_required = param_name in required
        param_info = self._extract_parameter_info(param_name, param_schema, is_required)

        actual_type = type(actual_value).__name__

        message = (
            f"Type mismatch for parameter '{param_name}' in {tool_name}: "
            f"expected {expected_type}, got {actual_type}"
        )

        suggestions = [
            f"Convert value to {expected_type}",
            f"Example: {self._get_type_example(expected_type)}",
            f"Description: {param_info.description}",
        ]

        return Tier2ErrorResponse(
            error_type="type_mismatch",
            message=message,
            missing_required=[],
            parameter_details={param_name: param_info},
            optional_parameters=[],
            suggestions=suggestions,
        )

    def _extract_parameter_info(
        self, param_name: str, param_schema: Dict[str, Any], is_required: bool
    ) -> ParameterInfo:
        """Extract detailed parameter information from schema."""
        param_type = param_schema.get("type", "any")
        description = param_schema.get("description", f"Parameter {param_name}")
        default = param_schema.get("default")

        # Extract constraints
        constraints = {}
        for key in [
            "minLength",
            "maxLength",
            "minimum",
            "maximum",
            "pattern",
            "enum",
            "format",
        ]:
            if key in param_schema:
                constraints[key] = param_schema[key]

        # Enhance type description
        type_desc = self._type_descriptions.get(param_type.lower(), param_type)

        return ParameterInfo(
            name=param_name,
            type=type_desc,
            required=is_required,
            description=description,
            default=default,
            constraints=constraints if constraints else None,
        )

    def _get_constraint_violation_message(
        self, param_name: str, value: Any, param_schema: Dict[str, Any]
    ) -> str:
        """Generate specific constraint violation message."""
        # Check various constraint types
        if "minLength" in param_schema and len(str(value)) < param_schema["minLength"]:
            return f"too short (minimum {param_schema['minLength']} characters)"

        if "maxLength" in param_schema and len(str(value)) > param_schema["maxLength"]:
            return f"too long (maximum {param_schema['maxLength']} characters)"

        if (
            "minimum" in param_schema
            and isinstance(value, (int, float))
            and value < param_schema["minimum"]
        ):
            return f"too small (minimum {param_schema['minimum']})"

        if (
            "maximum" in param_schema
            and isinstance(value, (int, float))
            and value > param_schema["maximum"]
        ):
            return f"too large (maximum {param_schema['maximum']})"

        if "enum" in param_schema and value not in param_schema["enum"]:
            return (
                f"invalid choice (must be one of: "
                f"{', '.join(map(str, param_schema['enum']))})"
            )

        return f"invalid value '{value}'"

    def _format_constraint_suggestions(self, constraints: Dict[str, Any]) -> List[str]:
        """Format constraint information as helpful suggestions."""
        suggestions = []
        for constraint, value in constraints.items():
            if constraint in self._constraint_descriptions:
                template = self._constraint_descriptions[constraint]
                suggestions.append(template.format(value=value))

        return suggestions

    def _get_type_example(self, type_name: str) -> str:
        """Get example value for a given type."""
        examples = {
            "string": '"example text"',
            "integer": "42",
            "number": "3.14",
            "boolean": "true",
            "array": '["item1", "item2"]',
            "object": '{"key": "value"}',
            "uuid": '"123e4567-e89b-12d3-a456-426614174000"',
            "email": '"user@example.com"',
            "url": '"https://example.com"',
        }

        return examples.get(type_name.lower(), f"<{type_name} value>")


def generate_tier2_error_response(
    tool_name: str,
    error_type: str,
    parameters: Dict[str, Any],
    schema: Dict[str, Any],
    invalid_param: Optional[str] = None,
    invalid_value: Optional[Any] = None,
) -> str:
    """Generate a formatted Tier 2 error response."""
    generator = Tier2ErrorGenerator()

    if error_type == "missing_parameters":
        required = schema.get("required", [])
        missing = [
            param
            for param in required
            if param not in parameters or parameters[param] is None
        ]

        if missing:
            error_response = generator.generate_missing_parameter_error(
                tool_name, missing, schema
            )

            # Format detailed response
            response_lines = [f"❌ {error_response.message}"]

            # Add missing parameter details
            for param in missing:
                if param in error_response.parameter_details:
                    info = error_response.parameter_details[param]
                    response_lines.append(
                        f"  • {param} ({info.type}): {info.description}"
                    )

            # Add suggestions
            if error_response.suggestions:
                response_lines.append("\n💡 Suggestions:")
                for suggestion in error_response.suggestions:
                    response_lines.append(f"  • {suggestion}")

            return "\n".join(response_lines)

    elif error_type == "invalid_parameter" and invalid_param:
        error_response = generator.generate_invalid_parameter_error(
            tool_name, invalid_param, invalid_value, schema
        )

        response_lines = [f"❌ {error_response.message}"]

        # Add parameter details
        if invalid_param in error_response.parameter_details:
            info = error_response.parameter_details[invalid_param]
            response_lines.append(f"  Parameter: {info.name} ({info.type})")
            response_lines.append(f"  Description: {info.description}")

            if info.constraints:
                response_lines.append("  Constraints:")
                for constraint, value in info.constraints.items():
                    response_lines.append(f"    - {constraint}: {value}")

        # Add suggestions
        if error_response.suggestions:
            response_lines.append("\n💡 Suggestions:")
            for suggestion in error_response.suggestions:
                response_lines.append(f"  • {suggestion}")

        return "\n".join(response_lines)

    elif error_type == "type_mismatch" and invalid_param:
        expected_type = (
            schema.get("properties", {}).get(invalid_param, {}).get("type", "unknown")
        )
        error_response = generator.generate_type_mismatch_error(
            tool_name, invalid_param, expected_type, invalid_value, schema
        )

        response_lines = [f"❌ {error_response.message}"]

        # Add suggestions
        if error_response.suggestions:
            response_lines.append("\n💡 Suggestions:")
            for suggestion in error_response.suggestions:
                response_lines.append(f"  • {suggestion}")

        return "\n".join(response_lines)

    return f"❌ Error in {tool_name}: Please check your parameters and try again"
