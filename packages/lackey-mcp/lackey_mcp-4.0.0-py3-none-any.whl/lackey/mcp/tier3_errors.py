"""Tier 3 error response system with complete schema disclosure.

Provides comprehensive error responses with complete schema guidance, structure
examples, and parameter dependencies for maximum disclosure level.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .gateway_schemas import ALL_SCHEMAS
from .tier2_errors import ParameterInfo, Tier2ErrorGenerator


@dataclass
class SchemaExample:
    """Complete schema example with structure."""

    description: str
    parameters: Dict[str, Any]
    explanation: str


@dataclass
class ParameterDependency:
    """Parameter dependency mapping."""

    parameter: str
    depends_on: List[str]
    relationship_type: str
    description: str


@dataclass
class Tier3ErrorResponse:
    """Complete error response with full schema disclosure."""

    error_type: str
    message: str
    missing_required: List[str]
    parameter_details: Dict[str, ParameterInfo]
    optional_parameters: List[str]
    suggestions: List[str]
    schema_examples: List[SchemaExample]
    parameter_dependencies: List[ParameterDependency]
    complete_schema: Dict[str, Any]

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
            "schema_examples": [
                {
                    "description": ex.description,
                    "parameters": ex.parameters,
                    "explanation": ex.explanation,
                }
                for ex in self.schema_examples
            ],
            "parameter_dependencies": [
                {
                    "parameter": dep.parameter,
                    "depends_on": dep.depends_on,
                    "relationship_type": dep.relationship_type,
                    "description": dep.description,
                }
                for dep in self.parameter_dependencies
            ],
            "complete_schema": self.complete_schema,
        }


class Tier3ErrorGenerator:
    """Generates Tier 3 error responses with complete disclosure."""

    def __init__(self) -> None:
        """Initialize with complete schema access."""
        self.tier2_generator = Tier2ErrorGenerator()
        self.schemas = ALL_SCHEMAS

        self._example_values = {
            "str": "example_string",
            "int": 42,
            "bool": True,
            "list": ["item1", "item2"],
            "dict": {"key": "value"},
            "uuid": "123e4567-e89b-12d3-a456-426614174000",
            "enum": "valid_option",
        }

        self._dependency_patterns = {
            "project_id": {
                "enables": ["task_id", "project_name"],
                "type": "parent_reference",
                "description": "Project ID enables task operations within that project",
            },
            "task_id": {
                "requires": ["project_id"],
                "type": "child_reference",
                "description": "Task ID requires project context for validation",
            },
            "new_status": {
                "relates_to": ["current_status", "status"],
                "type": "state_transition",
                "description": "New status creates transition from current state",
            },
        }

    def generate_missing_parameter_error(
        self, tool_name: str, missing_params: List[str], schema: Dict[str, Any]
    ) -> Tier3ErrorResponse:
        """Generate comprehensive error for missing required parameters."""
        # Get Tier 2 base response
        tier2_response = self.tier2_generator.generate_missing_parameter_error(
            tool_name, missing_params, schema
        )

        # Generate complete schema examples
        schema_examples = self._generate_schema_examples(
            tool_name, schema, missing_params
        )

        # Map parameter dependencies
        parameter_dependencies = self._map_parameter_dependencies(schema)

        # Enhanced suggestions with complete guidance
        enhanced_suggestions = tier2_response.suggestions + [
            "See schema_examples for complete usage patterns",
            "Check parameter_dependencies for required relationships",
            "Use complete_schema for full parameter reference",
        ]

        return Tier3ErrorResponse(
            error_type=tier2_response.error_type,
            message=(
                f"{tier2_response.message} Complete schema guidance provided below."
            ),
            missing_required=tier2_response.missing_required,
            parameter_details=tier2_response.parameter_details,
            optional_parameters=tier2_response.optional_parameters,
            suggestions=enhanced_suggestions,
            schema_examples=schema_examples,
            parameter_dependencies=parameter_dependencies,
            complete_schema=schema,
        )

    def generate_invalid_parameter_error(
        self,
        tool_name: str,
        invalid_param: str,
        invalid_value: Any,
        schema: Dict[str, Any],
    ) -> Tier3ErrorResponse:
        """Generate comprehensive error for invalid parameter value."""
        # Get Tier 2 base response
        tier2_response = self.tier2_generator.generate_invalid_parameter_error(
            tool_name, invalid_param, invalid_value, schema
        )

        # Generate targeted examples for the invalid parameter
        schema_examples = self._generate_parameter_specific_examples(
            tool_name, invalid_param, schema
        )

        # Map dependencies for the invalid parameter
        parameter_dependencies = self._map_parameter_dependencies(
            schema, focus_param=invalid_param
        )

        # Enhanced suggestions
        enhanced_suggestions = tier2_response.suggestions + [
            f"See schema_examples for correct {invalid_param} usage",
            f"Check parameter_dependencies for {invalid_param} relationships",
            "Review complete_schema for all constraints and formats",
        ]

        return Tier3ErrorResponse(
            error_type=tier2_response.error_type,
            message=(
                f"{tier2_response.message} Complete parameter guidance provided below."
            ),
            missing_required=[],
            parameter_details=tier2_response.parameter_details,
            optional_parameters=[],
            suggestions=enhanced_suggestions,
            schema_examples=schema_examples,
            parameter_dependencies=parameter_dependencies,
            complete_schema=schema,
        )

    def generate_structure_guidance_error(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        schema: Dict[str, Any],
        structure_issues: List[str],
    ) -> Tier3ErrorResponse:
        """Generate comprehensive structure guidance error."""
        # Create comprehensive message
        message = f"Structure issues detected in {tool_name} parameters: " + (
            f"{', '.join(structure_issues)}. "
            f"Complete structural guidance provided below."
        )

        # Generate all possible schema examples
        schema_examples = self._generate_comprehensive_examples(tool_name, schema)

        # Map all parameter dependencies
        parameter_dependencies = self._map_parameter_dependencies(schema)

        # Extract parameter details
        parameter_details = {}
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        types = schema.get("types", {})

        for param_name in types.keys():
            is_required = param_name in required
            param_schema = properties.get(
                param_name, {"description": f"Parameter {param_name}"}
            )
            param_info = self.tier2_generator._extract_parameter_info(
                param_name, param_schema, is_required
            )
            parameter_details[param_name] = param_info

        # Comprehensive suggestions
        suggestions = [
            "Review schema_examples for correct parameter structures",
            "Check parameter_dependencies for required relationships",
            "Validate parameter combinations against complete_schema",
            "Ensure all required parameters are provided with correct types",
            "Follow the structure patterns shown in the examples",
        ]

        return Tier3ErrorResponse(
            error_type="structure_error",
            message=message,
            missing_required=[],
            parameter_details=parameter_details,
            optional_parameters=list(schema.get("optional", {}).keys()),
            suggestions=suggestions,
            schema_examples=schema_examples,
            parameter_dependencies=parameter_dependencies,
            complete_schema=schema,
        )

    def _generate_schema_examples(
        self, tool_name: str, schema: Dict[str, Any], missing_params: List[str]
    ) -> List[SchemaExample]:
        """Generate comprehensive schema examples."""
        examples = []
        required_params = schema.get("required", [])
        optional_params = schema.get("optional", {})
        types = schema.get("types", {})

        # Example 1: Minimal required parameters
        minimal_params = {}
        for param in required_params:
            minimal_params[param] = self._get_example_value(
                param, types.get(param, "str")
            )

        if minimal_params:
            examples.append(
                SchemaExample(
                    description="Minimal required parameters",
                    parameters=minimal_params,
                    explanation=(
                        (
                            f"This example shows the minimum parameters needed for "
                            f"{tool_name}"
                        )
                    ),
                )
            )

        # Example 2: Complete with optional parameters
        complete_params = minimal_params.copy()
        for param in list(optional_params.keys())[:3]:  # Limit to 3 optional
            complete_params[param] = self._get_example_value(
                param, types.get(param, "str")
            )

        if len(complete_params) > len(minimal_params):
            examples.append(
                SchemaExample(
                    description="Complete with optional parameters",
                    parameters=complete_params,
                    explanation=(
                        (
                            f"This example shows {tool_name} with commonly used "
                            f"optional parameters"
                        )
                    ),
                )
            )

        # Example 3: Focused on missing parameters
        if missing_params:
            missing_example = {}
            for param in missing_params:
                missing_example[param] = self._get_example_value(
                    param, types.get(param, "str")
                )

            examples.append(
                SchemaExample(
                    description="Missing parameters example",
                    parameters=missing_example,
                    explanation=(
                        f"This example shows the missing parameters: "
                        f"{', '.join(missing_params)}"
                    ),
                )
            )

        return examples

    def _generate_parameter_specific_examples(
        self, tool_name: str, focus_param: str, schema: Dict[str, Any]
    ) -> List[SchemaExample]:
        """Generate examples focused on a specific parameter."""
        examples = []
        types = schema.get("types", {})
        constraints = schema.get("constraints", {})

        param_type = types.get(focus_param, "str")
        param_constraints = constraints.get(focus_param, {})

        # Example with correct parameter value
        correct_params = {focus_param: self._get_example_value(focus_param, param_type)}

        examples.append(
            SchemaExample(
                description=f"Correct {focus_param} usage",
                parameters=correct_params,
                explanation=f"This shows the correct format and type for {focus_param}",
            )
        )

        # Example with constraint variations if applicable
        if "allowed_values" in param_constraints:
            for value in param_constraints["allowed_values"][:2]:  # Show 2 options
                examples.append(
                    SchemaExample(
                        description=f"{focus_param} option: {value}",
                        parameters={focus_param: value},
                        explanation=f"Valid option for {focus_param}: {value}",
                    )
                )

        return examples

    def _generate_comprehensive_examples(
        self, tool_name: str, schema: Dict[str, Any]
    ) -> List[SchemaExample]:
        """Generate comprehensive examples for structure guidance."""
        examples = []
        required_params = schema.get("required", [])
        optional_params = schema.get("optional", {})
        types = schema.get("types", {})

        # Example 1: Basic structure
        basic_params = {}
        for param in required_params:
            basic_params[param] = self._get_example_value(
                param, types.get(param, "str")
            )

        examples.append(
            SchemaExample(
                description="Basic parameter structure",
                parameters=basic_params,
                explanation=(
                    f"Basic structure for {tool_name} with all required parameters"
                ),
            )
        )

        # Example 2: Extended structure
        extended_params = basic_params.copy()
        for param in list(optional_params.keys())[:2]:
            extended_params[param] = self._get_example_value(
                param, types.get(param, "str")
            )

        if len(extended_params) > len(basic_params):
            examples.append(
                SchemaExample(
                    description="Extended parameter structure",
                    parameters=extended_params,
                    explanation=(
                        f"Extended structure for {tool_name} with optional parameters"
                    ),
                )
            )

        # Example 3: Common usage pattern
        if "project_id" in types and "task_id" in types:
            pattern_params = {
                "project_id": "123e4567-e89b-12d3-a456-426614174000",
                "task_id": "987fcdeb-51a2-43d1-b789-123456789abc",
            }
            examples.append(
                SchemaExample(
                    description="Common project-task pattern",
                    parameters=pattern_params,
                    explanation=(
                        "Common pattern for operations involving project and "
                        "task relationships"
                    ),
                )
            )

        return examples

    def _map_parameter_dependencies(
        self, schema: Dict[str, Any], focus_param: Optional[str] = None
    ) -> List[ParameterDependency]:
        """Map parameter dependencies and relationships."""
        dependencies = []
        types = schema.get("types", {})

        # Check each parameter for dependencies
        for param in types.keys():
            if focus_param and param != focus_param:
                continue

            if param in self._dependency_patterns:
                pattern = self._dependency_patterns[param]

                # Check for enabling relationships
                if "enables" in pattern:
                    enabled_params = [p for p in pattern["enables"] if p in types]
                    if enabled_params:
                        rel_type = pattern["type"]
                        if isinstance(rel_type, list):
                            rel_type = rel_type[0] if rel_type else "enables"
                        dependencies.append(
                            ParameterDependency(
                                parameter=param,
                                depends_on=[],
                                relationship_type=str(rel_type),
                                description=(
                                    f"{param} enables: {', '.join(enabled_params)}"
                                ),
                            )
                        )

                # Check for requirement relationships
                if "requires" in pattern:
                    required_params = [p for p in pattern["requires"] if p in types]
                    if required_params:
                        rel_type = pattern["type"]
                        if isinstance(rel_type, list):
                            rel_type = rel_type[0] if rel_type else "requires"
                        dependencies.append(
                            ParameterDependency(
                                parameter=param,
                                depends_on=required_params,
                                relationship_type=str(rel_type),
                                description=(
                                    f"{param} requires: {', '.join(required_params)}"
                                ),
                            )
                        )

                # Check for related relationships
                if "relates_to" in pattern:
                    related_params = [p for p in pattern["relates_to"] if p in types]
                    if related_params:
                        rel_type = pattern["type"]
                        if isinstance(rel_type, list):
                            rel_type = rel_type[0] if rel_type else "relates_to"
                        dependencies.append(
                            ParameterDependency(
                                parameter=param,
                                depends_on=related_params,
                                relationship_type=str(rel_type),
                                description=(
                                    f"{param} relates to: {', '.join(related_params)}"
                                ),
                            )
                        )

        return dependencies

    def _get_example_value(self, param_name: str, param_type: str) -> Any:
        """Get example value for a parameter."""
        # Special cases based on parameter name
        if "id" in param_name.lower():
            return "123e4567-e89b-12d3-a456-426614174000"
        elif "status" in param_name.lower():
            return "in_progress"
        elif "title" in param_name.lower():
            return "Example Task Title"
        elif "name" in param_name.lower():
            return "Example Name"
        elif "description" in param_name.lower():
            return "Example description text"

        # Type-based defaults
        base_type = param_type.lower().replace("optional[", "").replace("]", "")
        return self._example_values.get(base_type, f"example_{param_name}")


def generate_tier3_error_response(
    tool_name: str,
    error_type: str,
    parameters: Dict[str, Any],
    schema: Dict[str, Any],
    invalid_param: Optional[str] = None,
    invalid_value: Optional[Any] = None,
    structure_issues: Optional[List[str]] = None,
) -> str:
    """Generate a formatted Tier 3 error response."""
    generator = Tier3ErrorGenerator()

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

            # Format comprehensive response
            response_lines = [f"❌ {error_response.message}"]

            # Add missing parameter details
            response_lines.append("\n📋 Missing Required Parameters:")
            for param in missing:
                if param in error_response.parameter_details:
                    info = error_response.parameter_details[param]
                    response_lines.append(
                        f"  • {param} ({info.type}): {info.description}"
                    )

            # Add schema examples
            response_lines.append("\n📚 Schema Examples:")
            for example in error_response.schema_examples:
                response_lines.append(f"  • {example.description}:")
                response_lines.append(f"    {example.parameters}")
                response_lines.append(f"    → {example.explanation}")

            # Add parameter dependencies
            if error_response.parameter_dependencies:
                response_lines.append("\n🔗 Parameter Dependencies:")
                for dep in error_response.parameter_dependencies:
                    response_lines.append(f"  • {dep.parameter}: {dep.description}")

            return "\n".join(response_lines)

    elif error_type == "invalid_parameter" and invalid_param:
        error_response = generator.generate_invalid_parameter_error(
            tool_name, invalid_param, invalid_value, schema
        )

        response_lines = [f"❌ {error_response.message}"]

        # Add parameter details
        if invalid_param in error_response.parameter_details:
            info = error_response.parameter_details[invalid_param]
            response_lines.append("\n📋 Parameter Details:")
            response_lines.append(f"  • {info.name} ({info.type}): {info.description}")
            if info.constraints:
                response_lines.append(f"  • Constraints: {info.constraints}")

        # Add examples
        response_lines.append("\n📚 Correct Usage Examples:")
        for example in error_response.schema_examples:
            response_lines.append(f"  • {example.description}: {example.parameters}")

        return "\n".join(response_lines)

    elif error_type == "structure_error" and structure_issues:
        error_response = generator.generate_structure_guidance_error(
            tool_name, parameters, schema, structure_issues
        )

        response_lines = [f"❌ {error_response.message}"]

        # Add comprehensive guidance
        response_lines.append("\n📚 Complete Structure Examples:")
        for example in error_response.schema_examples:
            response_lines.append(f"  • {example.description}:")
            response_lines.append(f"    {example.parameters}")

        response_lines.append("\n🔗 Parameter Dependencies:")
        for dep in error_response.parameter_dependencies:
            response_lines.append(f"  • {dep.description}")

        return "\n".join(response_lines)

    return (
        f"❌ Error in {tool_name}: Complete schema guidance available in error details"
    )
