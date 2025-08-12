"""lackey_suggest tool for schema-based parameter suggestions.

Provides intelligent parameter suggestions based on schema analysis without
referencing actual data, maintaining clean separation between structure and content.
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .gateway_schemas import ALL_SCHEMAS, get_schemas_for_gateway


@dataclass
class ParameterSuggestion:
    """Parameter suggestion with context and examples."""

    name: str
    type: str
    required: bool
    description: str
    examples: List[str]
    constraints: Optional[Dict[str, Any]] = None
    related_params: Optional[List[str]] = None


@dataclass
class CompletionSuggestion:
    """Completion suggestion for partial parameters."""

    parameter: str
    suggested_value: str
    confidence: float
    reasoning: str


class LackeySuggestTool:
    """Schema-based parameter suggestion tool."""

    def __init__(self) -> None:
        """Initialize the suggestion tool."""
        self.schemas = ALL_SCHEMAS
        self._type_examples = {
            "str": ["example_text", "sample_string"],
            "int": [42, 100, 1],
            "bool": [True, False],
            "list": [["item1", "item2"], ["example"]],
            "dict": [{"key": "value"}, {"example": "data"}],
            "uuid": ["123e4567-e89b-12d3-a456-426614174000"],
            "enum": ["option1", "option2"],
        }

    def suggest_parameters(
        self,
        tool_name: str,
        partial_params: Optional[Dict[str, Any]] = None,
        gateway: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Suggest parameters for a tool based on schema analysis."""
        # Find tool schema
        schema = self._find_tool_schema(tool_name, gateway)
        if not schema:
            return {"error": f"Tool '{tool_name}' not found"}

        partial_params = partial_params or {}

        # Generate parameter suggestions
        suggestions = []
        missing_required = []
        completion_suggestions = []

        required_params = schema.get("required", [])
        optional_params = schema.get("optional", {})
        properties = schema.get("properties", {})
        types = schema.get("types", {})
        constraints = schema.get("constraints", {})

        # Check required parameters
        for param in required_params:
            if param not in partial_params:
                missing_required.append(param)
                suggestion = self._create_parameter_suggestion(
                    param, properties, types, constraints, required=True
                )
                suggestions.append(suggestion)

        # Check optional parameters
        for param in optional_params:
            if param not in partial_params:
                suggestion = self._create_parameter_suggestion(
                    param, properties, types, constraints, required=False
                )
                suggestions.append(suggestion)

        # Generate completion suggestions for partial values
        for param, value in partial_params.items():
            if param in types and self._is_partial_value(value, types[param]):
                completion = self._suggest_completion(
                    param, value, types[param], constraints.get(param, {})
                )
                if completion:
                    completion_suggestions.append(completion)

        return {
            "tool_name": tool_name,
            "gateway": self._find_gateway_for_tool(tool_name),
            "missing_required": missing_required,
            "parameter_suggestions": [self._suggestion_to_dict(s) for s in suggestions],
            "completion_suggestions": [
                self._completion_to_dict(c) for c in completion_suggestions
            ],
            "parameter_relationships": self._analyze_parameter_relationships(schema),
            "usage_examples": self._generate_usage_examples(tool_name, schema),
        }

    def suggest_next_parameter(
        self,
        tool_name: str,
        current_params: Dict[str, Any],
        gateway: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Suggest the next most logical parameter to provide."""
        schema = self._find_tool_schema(tool_name, gateway)
        if not schema:
            return {"error": f"Tool '{tool_name}' not found"}

        required_params = schema.get("required", [])
        optional_params = schema.get("optional", {})
        types = schema.get("types", {})
        constraints = schema.get("constraints", {})

        # Find next required parameter
        for param in required_params:
            if param not in current_params:
                suggestion = self._create_parameter_suggestion(
                    param,
                    schema.get("properties", {}),
                    types,
                    constraints,
                    required=True,
                )
                return {
                    "next_parameter": param,
                    "suggestion": self._suggestion_to_dict(suggestion),
                    "priority": "required",
                    "completion_percentage": len(current_params)
                    / len(required_params)
                    * 100,
                }

        # Find most relevant optional parameter
        optional_priority = self._prioritize_optional_parameters(
            optional_params, current_params, schema
        )

        if optional_priority:
            param = optional_priority[0]
            suggestion = self._create_parameter_suggestion(
                param, schema.get("properties", {}), types, constraints, required=False
            )
            return {
                "next_parameter": param,
                "suggestion": self._suggestion_to_dict(suggestion),
                "priority": "optional",
                "completion_percentage": 100,  # All required params satisfied
            }

        return {"message": "All parameters provided", "completion_percentage": 100}

    def analyze_parameter_structure(
        self, tool_name: str, gateway: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze parameter structure without data references."""
        schema = self._find_tool_schema(tool_name, gateway)
        if not schema:
            return {"error": f"Tool '{tool_name}' not found"}

        required_params = schema.get("required", [])
        optional_params = schema.get("optional", {})
        types = schema.get("types", {})
        constraints = schema.get("constraints", {})

        structure = {
            "tool_name": tool_name,
            "gateway": self._find_gateway_for_tool(tool_name),
            "parameter_count": {
                "required": len(required_params),
                "optional": len(optional_params),
                "total": len(required_params) + len(optional_params),
            },
            "parameter_types": self._analyze_parameter_types(types),
            "validation_rules": self._analyze_validation_rules(constraints),
            "complexity_score": self._calculate_complexity_score(schema),
            "parameter_groups": self._group_related_parameters(schema),
        }

        return structure

    def _find_tool_schema(
        self, tool_name: str, gateway: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Find schema for a tool."""
        if gateway:
            gateway_schemas = get_schemas_for_gateway(gateway)
            return gateway_schemas.get(tool_name)

        return self.schemas.get(tool_name)

    def _find_gateway_for_tool(self, tool_name: str) -> Optional[str]:
        """Find which gateway contains a tool."""
        gateway_maps = {
            "lackey_get": get_schemas_for_gateway("lackey_get"),
            "lackey_do": get_schemas_for_gateway("lackey_do"),
            "lackey_analyze": get_schemas_for_gateway("lackey_analyze"),
        }

        for gateway, schemas in gateway_maps.items():
            if tool_name in schemas:
                return gateway
        return None

    def _create_parameter_suggestion(
        self,
        param_name: str,
        properties: Dict[str, Any],
        types: Dict[str, str],
        constraints: Dict[str, Any],
        required: bool,
    ) -> ParameterSuggestion:
        """Create a parameter suggestion."""
        param_type = types.get(param_name, "str")
        param_constraints = constraints.get(param_name, {})

        # Generate examples based on type and constraints
        examples = self._generate_parameter_examples(param_type, param_constraints)

        # Extract description from properties or generate one
        description = properties.get(param_name, {}).get(
            "description", f"Parameter {param_name}"
        )

        return ParameterSuggestion(
            name=param_name,
            type=param_type,
            required=required,
            description=description,
            examples=examples,
            constraints=param_constraints if param_constraints else None,
        )

    def _generate_parameter_examples(
        self, param_type: str, constraints: Dict[str, Any]
    ) -> List[str]:
        """Generate examples for a parameter type."""
        # Handle enum constraints
        if "allowed_values" in constraints:
            allowed_values = constraints["allowed_values"]
            if isinstance(allowed_values, list):
                return allowed_values[:3]  # First 3 options

        # Handle UUID type
        if "validator" in constraints and "uuid" in constraints["validator"]:
            return ["123e4567-e89b-12d3-a456-426614174000"]

        # Use type-based examples
        base_examples = self._type_examples.get(param_type.lower(), ["example_value"])

        # Apply constraints to examples
        if isinstance(base_examples, list) and len(base_examples) > 0:
            if isinstance(base_examples[0], str) and "min_length" in constraints:
                min_len = constraints["min_length"]
                return [f"example_{'x' * max(0, min_len - 8)}"]
            return base_examples[:2]  # Limit to 2 examples

        return ["example_value"]

    def _is_partial_value(self, value: Any, expected_type: str) -> bool:
        """Check if a value appears to be partial/incomplete."""
        if not isinstance(value, str):
            return False

        # Check for common partial patterns
        partial_patterns = [
            r"^[a-f0-9]{1,7}$",  # Partial UUID
            r"^\w{1,3}$",  # Very short strings
            r"^[A-Z][a-z]*$",  # Incomplete camelCase
        ]

        return any(re.match(pattern, value) for pattern in partial_patterns)

    def _suggest_completion(
        self,
        param_name: str,
        partial_value: Any,
        param_type: str,
        constraints: Dict[str, Any],
    ) -> Optional[CompletionSuggestion]:
        """Suggest completion for a partial value."""
        if not isinstance(partial_value, str):
            return None

        # UUID completion
        if "uuid" in constraints.get("validator", ""):
            if re.match(r"^[a-f0-9]{8}$", partial_value):
                completed = f"{partial_value}-1234-5678-9abc-123456789012"
                return CompletionSuggestion(
                    parameter=param_name,
                    suggested_value=completed,
                    confidence=0.8,
                    reasoning="Completed partial UUID format",
                )

        # String length completion
        if "min_length" in constraints:
            min_len = constraints["min_length"]
            if len(partial_value) < min_len:
                completed = partial_value + "_" * (min_len - len(partial_value))
                return CompletionSuggestion(
                    parameter=param_name,
                    suggested_value=completed,
                    confidence=0.6,
                    reasoning=f"Extended to meet minimum length of {min_len}",
                )

        return None

    def _analyze_parameter_relationships(
        self, schema: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Analyze relationships between parameters."""
        relationships = {}

        # Common parameter patterns
        param_patterns = {
            "project_id": ["task_id", "project_name"],
            "task_id": ["project_id", "task_name"],
            "user_id": ["username", "assignee"],
            "status": ["new_status", "old_status"],
        }

        for param, related in param_patterns.items():
            if param in schema.get("types", {}):
                found_related = [r for r in related if r in schema.get("types", {})]
                if found_related:
                    relationships[param] = found_related

        return relationships

    def _generate_usage_examples(
        self, tool_name: str, schema: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate usage examples for the tool."""
        required_params = schema.get("required", [])
        types = schema.get("types", {})

        examples = []

        # Basic example with required parameters only
        basic_example = {}
        for param in required_params:
            param_type = types.get(param, "str")
            basic_example[param] = self._get_example_value(param_type)

        if basic_example:
            examples.append(
                {
                    "description": "Basic usage with required parameters",
                    "parameters": basic_example,
                }
            )

        return examples[:2]  # Limit to 2 examples

    def _get_example_value(self, param_type: str) -> Any:
        """Get a single example value for a parameter type."""
        examples = self._type_examples.get(param_type.lower(), ["example"])
        if isinstance(examples, list) and len(examples) > 0:
            return examples[0]
        return "example"

    def _analyze_parameter_types(self, types: Dict[str, str]) -> Dict[str, int]:
        """Analyze distribution of parameter types."""
        type_counts: Dict[str, int] = {}
        for param_type in types.values():
            base_type = param_type.split("[")[0]  # Remove optional wrapper
            type_counts[base_type] = type_counts.get(base_type, 0) + 1
        return type_counts

    def _analyze_validation_rules(self, constraints: Dict[str, Any]) -> Dict[str, int]:
        """Analyze validation rule distribution."""
        rule_counts: Dict[str, int] = {}
        for param_constraints in constraints.values():
            for rule in param_constraints.keys():
                rule_counts[rule] = rule_counts.get(rule, 0) + 1
        return rule_counts

    def _calculate_complexity_score(self, schema: Dict[str, Any]) -> float:
        """Calculate complexity score for the tool."""
        required_count = len(schema.get("required", []))
        optional_count = len(schema.get("optional", {}))
        constraint_count = sum(len(c) for c in schema.get("constraints", {}).values())

        return (required_count * 2 + optional_count + constraint_count * 0.5) / 10

    def _group_related_parameters(self, schema: Dict[str, Any]) -> Dict[str, List[str]]:
        """Group related parameters by common prefixes or patterns."""
        all_params = list(schema.get("types", {}).keys())
        groups: Dict[str, List[str]] = {}

        # Group by common prefixes
        prefixes: Dict[str, List[str]] = {}
        for param in all_params:
            if "_" in param:
                prefix = param.split("_")[0]
                if prefix not in prefixes:
                    prefixes[prefix] = []
                prefixes[prefix].append(param)

        # Only include groups with multiple parameters
        for prefix, params in prefixes.items():
            if len(params) > 1:
                groups[f"{prefix}_group"] = params

        return groups

    def _prioritize_optional_parameters(
        self,
        optional_params: Dict[str, Any],
        current_params: Dict[str, Any],
        schema: Dict[str, Any],
    ) -> List[str]:
        """Prioritize optional parameters based on context."""
        # Simple priority based on common parameter importance
        priority_order = [
            "status",
            "assignee",
            "priority",
            "tags",
            "description",
            "note",
        ]

        available_optional = [p for p in optional_params if p not in current_params]

        # Sort by priority order
        prioritized = []
        for priority_param in priority_order:
            if priority_param in available_optional:
                prioritized.append(priority_param)

        # Add remaining parameters
        for param in available_optional:
            if param not in prioritized:
                prioritized.append(param)

        return prioritized

    def _suggestion_to_dict(self, suggestion: ParameterSuggestion) -> Dict[str, Any]:
        """Convert suggestion to dictionary."""
        return {
            "name": suggestion.name,
            "type": suggestion.type,
            "required": suggestion.required,
            "description": suggestion.description,
            "examples": suggestion.examples,
            "constraints": suggestion.constraints,
            "related_params": suggestion.related_params,
        }

    def _completion_to_dict(self, completion: CompletionSuggestion) -> Dict[str, Any]:
        """Convert completion to dictionary."""
        return {
            "parameter": completion.parameter,
            "suggested_value": completion.suggested_value,
            "confidence": completion.confidence,
            "reasoning": completion.reasoning,
        }


# Global instance for easy access
lackey_suggest = LackeySuggestTool()
