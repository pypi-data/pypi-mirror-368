"""Schema-Only Context Intelligence System.

Provides parameter relationship mapping and structural guidance based purely
on schema information without any data contamination.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from .gateway_schemas import ALL_SCHEMAS


class RelationshipType(Enum):
    """Types of parameter relationships."""

    PARENT_CHILD = "parent_child"
    MUTUAL_EXCLUSIVE = "mutual_exclusive"
    CONDITIONAL = "conditional"
    COMPLEMENTARY = "complementary"
    HIERARCHICAL = "hierarchical"


@dataclass
class ParameterRelationship:
    """Schema-based parameter relationship."""

    source_param: str
    target_param: str
    relationship_type: RelationshipType
    description: str
    conditions: Optional[Dict[str, Any]] = None


@dataclass
class StructuralGuidance:
    """Structural guidance based on schema analysis."""

    parameter: str
    guidance_type: str
    message: str
    related_parameters: List[str]
    schema_context: Dict[str, Any]


@dataclass
class ContextIntelligence:
    """Complete context intelligence for a parameter set."""

    relationships: List[ParameterRelationship]
    guidance: List[StructuralGuidance]
    parameter_groups: Dict[str, List[str]]
    completion_suggestions: List[str]


class SchemaContextIntelligence:
    """Schema-only context intelligence engine."""

    def __init__(self) -> None:
        """Initialize with schema-only patterns."""
        self.schemas = ALL_SCHEMAS

        # Schema-based relationship patterns
        self._relationship_patterns = {
            # Parent-child relationships
            ("project_id", "task_id"): RelationshipType.PARENT_CHILD,
            ("task_id", "step_id"): RelationshipType.PARENT_CHILD,
            ("project_id", "project_name"): RelationshipType.COMPLEMENTARY,
            # Status relationships
            ("status", "new_status"): RelationshipType.CONDITIONAL,
            ("current_status", "new_status"): RelationshipType.CONDITIONAL,
            # Mutual exclusions
            ("task_id", "all_tasks"): RelationshipType.MUTUAL_EXCLUSIVE,
            ("project_id", "all_projects"): RelationshipType.MUTUAL_EXCLUSIVE,
            # Hierarchical relationships
            ("complexity", "priority"): RelationshipType.HIERARCHICAL,
            ("start_date", "end_date"): RelationshipType.HIERARCHICAL,
        }

        # Parameter groupings based on schema structure
        self._parameter_groups = {
            "identification": ["project_id", "task_id", "step_id", "note_id"],
            "status_management": ["status", "new_status", "current_status"],
            "metadata": ["title", "description", "objective", "tags"],
            "temporal": ["created", "updated", "start_date", "end_date"],
            "classification": ["complexity", "priority", "category"],
            "content": ["note", "content", "message", "text"],
            "filtering": ["limit", "offset", "filter", "search_term"],
            "options": ["include_completed", "recursive", "force"],
        }

    def analyze_parameter_relationships(
        self, tool_name: str, parameters: Dict[str, Any], schema: Dict[str, Any]
    ) -> List[ParameterRelationship]:
        """Analyze parameter relationships based on schema structure."""
        relationships = []
        param_names = set(parameters.keys())
        schema_params = set(schema.get("types", {}).keys())

        # Find relationships between provided parameters
        for param1 in param_names:
            for param2 in param_names:
                if param1 != param2:
                    relationship = self._detect_relationship(param1, param2, schema)
                    if relationship:
                        relationships.append(relationship)

        # Find relationships with missing schema parameters
        missing_params = schema_params - param_names
        for provided_param in param_names:
            for missing_param in missing_params:
                relationship = self._detect_relationship(
                    provided_param, missing_param, schema
                )
                if relationship:
                    relationships.append(relationship)

        return relationships

    def generate_structural_guidance(
        self, tool_name: str, parameters: Dict[str, Any], schema: Dict[str, Any]
    ) -> List[StructuralGuidance]:
        """Generate structural guidance based on schema analysis."""
        guidance = []
        param_names = set(parameters.keys())
        schema_params = schema.get("types", {})
        required_params = set(schema.get("required", []))

        # Guidance for missing required parameters
        missing_required = required_params - param_names
        for param in missing_required:
            guidance.append(
                StructuralGuidance(
                    parameter=param,
                    guidance_type="missing_required",
                    message=f"Required parameter '{param}' is missing",
                    related_parameters=self._find_related_parameters(
                        param, schema_params
                    ),
                    schema_context={"type": schema_params.get(param, "unknown")},
                )
            )

        # Guidance for parameter combinations
        for param in param_names:
            related = self._find_related_parameters(param, schema_params)
            if related:
                missing_related = [p for p in related if p not in param_names]
                if missing_related:
                    guidance.append(
                        StructuralGuidance(
                            parameter=param,
                            guidance_type="related_missing",
                            message=(
                                f"Parameter '{param}' often used with: "
                                f"{', '.join(missing_related)}"
                            ),
                            related_parameters=missing_related,
                            schema_context={"group": self._get_parameter_group(param)},
                        )
                    )

        # Guidance for parameter groups
        for group_name, group_params in self._parameter_groups.items():
            provided_in_group = [p for p in group_params if p in param_names]
            missing_in_group = [
                p for p in group_params if p in schema_params and p not in param_names
            ]

            if provided_in_group and missing_in_group:
                guidance.append(
                    StructuralGuidance(
                        parameter=group_name,
                        guidance_type="group_completion",
                        message=(
                            f"Consider adding {group_name} parameters: "
                            f"{', '.join(missing_in_group[:2])}"
                        ),
                        related_parameters=missing_in_group,
                        schema_context={
                            "group": group_name,
                            "provided": provided_in_group,
                        },
                    )
                )

        return guidance

    def generate_context_intelligence(
        self, tool_name: str, parameters: Dict[str, Any], schema: Dict[str, Any]
    ) -> ContextIntelligence:
        """Generate complete context intelligence."""
        relationships = self.analyze_parameter_relationships(
            tool_name, parameters, schema
        )
        guidance = self.generate_structural_guidance(tool_name, parameters, schema)

        # Group parameters by function
        parameter_groups = {}
        for group_name, group_params in self._parameter_groups.items():
            provided_in_group = [p for p in group_params if p in parameters]
            if provided_in_group:
                parameter_groups[group_name] = provided_in_group

        # Generate completion suggestions
        completion_suggestions = self._generate_completion_suggestions(
            parameters, schema, relationships, guidance
        )

        return ContextIntelligence(
            relationships=relationships,
            guidance=guidance,
            parameter_groups=parameter_groups,
            completion_suggestions=completion_suggestions,
        )

    def _detect_relationship(
        self, param1: str, param2: str, schema: Dict[str, Any]
    ) -> Optional[ParameterRelationship]:
        """Detect relationship between two parameters."""
        # Check direct pattern matches
        pattern_key = (param1, param2)
        reverse_key = (param2, param1)

        if pattern_key in self._relationship_patterns:
            return ParameterRelationship(
                source_param=param1,
                target_param=param2,
                relationship_type=self._relationship_patterns[pattern_key],
                description=self._get_relationship_description(
                    param1, param2, self._relationship_patterns[pattern_key]
                ),
            )
        elif reverse_key in self._relationship_patterns:
            return ParameterRelationship(
                source_param=param2,
                target_param=param1,
                relationship_type=self._relationship_patterns[reverse_key],
                description=self._get_relationship_description(
                    param2, param1, self._relationship_patterns[reverse_key]
                ),
            )

        # Check semantic relationships
        return self._detect_semantic_relationship(param1, param2, schema)

    def _detect_semantic_relationship(
        self, param1: str, param2: str, schema: Dict[str, Any]
    ) -> Optional[ParameterRelationship]:
        """Detect semantic relationships between parameters."""
        # ID-based relationships
        if param1.endswith("_id") and param2.startswith(param1[:-3]):
            return ParameterRelationship(
                source_param=param1,
                target_param=param2,
                relationship_type=RelationshipType.PARENT_CHILD,
                description=f"{param1} identifies the context for {param2}",
            )

        # Status relationships
        if "status" in param1 and "status" in param2 and param1 != param2:
            return ParameterRelationship(
                source_param=param1,
                target_param=param2,
                relationship_type=RelationshipType.CONDITIONAL,
                description=f"{param1} and {param2} represent status transition",
            )

        # Temporal relationships
        if param1 in ["start_date", "created"] and param2 in ["end_date", "updated"]:
            return ParameterRelationship(
                source_param=param1,
                target_param=param2,
                relationship_type=RelationshipType.HIERARCHICAL,
                description=f"{param1} precedes {param2} temporally",
            )

        return None

    def _find_related_parameters(
        self, param: str, schema_params: Dict[str, Any]
    ) -> List[str]:
        """Find parameters related to the given parameter."""
        related = []

        # Find parameters in the same group
        for group_params in self._parameter_groups.values():
            if param in group_params:
                related.extend(
                    [p for p in group_params if p != param and p in schema_params]
                )

        # Find parameters with semantic relationships
        for other_param in schema_params:
            if other_param != param:
                # ID-based relationships
                if param.endswith("_id") and other_param.startswith(param[:-3]):
                    related.append(other_param)
                elif other_param.endswith("_id") and param.startswith(other_param[:-3]):
                    related.append(other_param)

                # Status relationships
                if "status" in param and "status" in other_param:
                    related.append(other_param)

        return list(set(related))

    def _get_parameter_group(self, param: str) -> Optional[str]:
        """Get the group name for a parameter."""
        for group_name, group_params in self._parameter_groups.items():
            if param in group_params:
                return group_name
        return None

    def _get_relationship_description(
        self, param1: str, param2: str, relationship_type: RelationshipType
    ) -> str:
        """Get description for a relationship type."""
        descriptions = {
            RelationshipType.PARENT_CHILD: (
                f"{param1} is the parent context for {param2}"
            ),
            RelationshipType.MUTUAL_EXCLUSIVE: (
                f"{param1} and {param2} cannot be used together"
            ),
            RelationshipType.CONDITIONAL: f"{param2} depends on the value of {param1}",
            RelationshipType.COMPLEMENTARY: f"{param1} and {param2} work together",
            RelationshipType.HIERARCHICAL: f"{param1} has precedence over {param2}",
        }

        return descriptions.get(relationship_type, f"{param1} relates to {param2}")

    def _generate_completion_suggestions(
        self,
        parameters: Dict[str, Any],
        schema: Dict[str, Any],
        relationships: List[ParameterRelationship],
        guidance: List[StructuralGuidance],
    ) -> List[str]:
        """Generate parameter completion suggestions."""
        suggestions = []
        param_names = set(parameters.keys())
        schema_params = set(schema.get("types", {}).keys())

        # Suggestions from relationships
        for rel in relationships:
            if rel.source_param in param_names and rel.target_param not in param_names:
                if rel.target_param in schema_params:
                    suggestions.append(
                        (
                            f"Consider adding '{rel.target_param}' "
                            f"(related to '{rel.source_param}')"
                        )
                    )

        # Suggestions from guidance
        for guide in guidance:
            if guide.guidance_type == "related_missing":
                for related_param in guide.related_parameters[:2]:  # Limit to 2
                    suggestions.append(
                        f"Add '{related_param}' to complement '{guide.parameter}'"
                    )

        # Group completion suggestions
        for group_name, group_params in self._parameter_groups.items():
            provided_in_group = [p for p in group_params if p in param_names]
            missing_in_group = [
                p for p in group_params if p in schema_params and p not in param_names
            ]

            if len(provided_in_group) == 1 and missing_in_group:
                suggestions.append(
                    f"Complete {group_name} group by adding: {missing_in_group[0]}"
                )

        return suggestions[:5]  # Limit to 5 suggestions


def analyze_schema_context(
    tool_name: str, parameters: Dict[str, Any], schema: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyze schema context and return intelligence."""
    intelligence = SchemaContextIntelligence()
    context = intelligence.generate_context_intelligence(tool_name, parameters, schema)

    return {
        "relationships": [
            {
                "source": rel.source_param,
                "target": rel.target_param,
                "type": rel.relationship_type.value,
                "description": rel.description,
            }
            for rel in context.relationships
        ],
        "guidance": [
            {
                "parameter": guide.parameter,
                "type": guide.guidance_type,
                "message": guide.message,
                "related": guide.related_parameters,
                "context": guide.schema_context,
            }
            for guide in context.guidance
        ],
        "parameter_groups": context.parameter_groups,
        "suggestions": context.completion_suggestions,
    }


def get_parameter_relationships(
    parameters: Dict[str, Any], schema: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Get parameter relationships without data contamination."""
    intelligence = SchemaContextIntelligence()
    relationships = intelligence.analyze_parameter_relationships("", parameters, schema)

    return [
        {
            "source": rel.source_param,
            "target": rel.target_param,
            "type": rel.relationship_type.value,
            "description": rel.description,
        }
        for rel in relationships
    ]


def get_structural_guidance(
    parameters: Dict[str, Any], schema: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Get structural guidance based on schema analysis."""
    intelligence = SchemaContextIntelligence()
    guidance = intelligence.generate_structural_guidance("", parameters, schema)

    return [
        {
            "parameter": guide.parameter,
            "type": guide.guidance_type,
            "message": guide.message,
            "related": guide.related_parameters,
            "context": guide.schema_context,
        }
        for guide in guidance
    ]
