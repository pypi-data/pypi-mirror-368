"""lackey_validate tool for schema validation without execution.

Provides structural validation and guidance based on schema analysis without
executing operations, maintaining clean separation between validation and execution.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from .gateway_schemas import ALL_SCHEMAS, SchemaValidator, get_schemas_for_gateway


class ValidationSeverity(Enum):
    """Validation issue severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Validation issue with details and suggestions."""

    parameter: str
    severity: ValidationSeverity
    message: str
    expected: str
    actual: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Complete validation result."""

    valid: bool
    tool_name: str
    gateway: str
    issues: List[ValidationIssue]
    missing_required: List[str]
    unexpected_params: List[str]
    validation_score: float


class LackeyValidateTool:
    """Schema validation tool without execution."""

    def __init__(self) -> None:
        """Initialize the validation tool."""
        self.schemas = ALL_SCHEMAS
        self.validator = SchemaValidator()

    def validate_parameters(
        self, tool_name: str, parameters: Dict[str, Any], gateway: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate parameters against tool schema without execution."""
        schema = self._find_tool_schema(tool_name, gateway)
        if not schema:
            return {"error": f"Tool '{tool_name}' not found"}

        issues = []
        missing_required = []
        unexpected_params = []

        required_params = schema.get("required", [])
        optional_params = schema.get("optional", {})
        types = schema.get("types", {})
        constraints = schema.get("constraints", {})

        all_valid_params = set(required_params) | set(optional_params.keys())

        # Check required parameters
        for param in required_params:
            if param not in parameters:
                missing_required.append(param)
                issues.append(
                    ValidationIssue(
                        parameter=param,
                        severity=ValidationSeverity.ERROR,
                        message=f"Required parameter '{param}' is missing",
                        expected=types.get(param, "any"),
                        suggestion=f"Add {param} parameter",
                    )
                )

        # Check unexpected parameters
        for param in parameters:
            if param not in all_valid_params:
                unexpected_params.append(param)
                issues.append(
                    ValidationIssue(
                        parameter=param,
                        severity=ValidationSeverity.WARNING,
                        message=f"Unexpected parameter '{param}'",
                        expected="not present",
                        actual=str(type(parameters[param]).__name__),
                        suggestion=f"Remove {param} or check spelling",
                    )
                )

        # Validate parameter types and constraints
        for param, value in parameters.items():
            if param in all_valid_params:
                param_issues = self._validate_parameter(
                    param, value, types.get(param), constraints.get(param, {})
                )
                issues.extend(param_issues)

        # Calculate validation score
        total_checks = len(required_params) + len(parameters)
        error_count = sum(
            1 for issue in issues if issue.severity == ValidationSeverity.ERROR
        )
        warning_count = sum(
            1 for issue in issues if issue.severity == ValidationSeverity.WARNING
        )

        score = (
            max(0, (total_checks - error_count - warning_count * 0.5) / total_checks)
            if total_checks > 0
            else 1.0
        )

        result = ValidationResult(
            valid=len(missing_required) == 0 and error_count == 0,
            tool_name=tool_name,
            gateway=self._find_gateway_for_tool(tool_name) or gateway or "unknown",
            issues=issues,
            missing_required=missing_required,
            unexpected_params=unexpected_params,
            validation_score=score,
        )

        return self._result_to_dict(result)

    def validate_structure(
        self, tool_name: str, parameters: Dict[str, Any], gateway: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate parameter structure and relationships."""
        schema = self._find_tool_schema(tool_name, gateway)
        if not schema:
            return {"error": f"Tool '{tool_name}' not found"}

        structure_issues = []

        # Check parameter relationships
        relationship_issues = self._validate_parameter_relationships(parameters, schema)
        structure_issues.extend(relationship_issues)

        # Check parameter combinations
        combination_issues = self._validate_parameter_combinations(parameters, schema)
        structure_issues.extend(combination_issues)

        # Check data consistency
        consistency_issues = self._validate_data_consistency(parameters, schema)
        structure_issues.extend(consistency_issues)

        return {
            "tool_name": tool_name,
            "gateway": self._find_gateway_for_tool(tool_name),
            "structure_valid": len(structure_issues) == 0,
            "structure_issues": [
                self._issue_to_dict(issue) for issue in structure_issues
            ],
            "parameter_count": len(parameters),
            "relationship_analysis": self._analyze_relationships(parameters, schema),
        }

    def get_validation_guidance(
        self, tool_name: str, parameters: Dict[str, Any], gateway: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get comprehensive validation guidance without execution."""
        schema = self._find_tool_schema(tool_name, gateway)
        if not schema:
            return {"error": f"Tool '{tool_name}' not found"}

        # Get basic validation
        validation_result = self.validate_parameters(tool_name, parameters, gateway)

        # Get structure validation
        structure_result = self.validate_structure(tool_name, parameters, gateway)

        # Generate guidance
        guidance = self._generate_guidance(
            parameters, schema, validation_result, structure_result
        )

        return {
            "tool_name": tool_name,
            "gateway": self._find_gateway_for_tool(tool_name),
            "validation_summary": {
                "parameter_valid": validation_result.get("valid", False),
                "structure_valid": structure_result.get("structure_valid", False),
                "validation_score": validation_result.get("validation_score", 0.0),
            },
            "guidance": guidance,
            "next_steps": self._suggest_next_steps(
                parameters, schema, validation_result
            ),
            "examples": self._generate_fix_examples(
                parameters, schema, validation_result
            ),
        }

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

    def _validate_parameter(
        self,
        param_name: str,
        value: Any,
        expected_type: Optional[str],
        constraints: Dict[str, Any],
    ) -> List[ValidationIssue]:
        """Validate a single parameter."""
        issues = []

        # Type validation
        if expected_type:
            type_issue = self._validate_type(param_name, value, expected_type)
            if type_issue:
                issues.append(type_issue)

        # Constraint validation
        constraint_issues = self._validate_constraints(param_name, value, constraints)
        issues.extend(constraint_issues)

        return issues

    def _validate_type(
        self, param_name: str, value: Any, expected_type: str
    ) -> Optional[ValidationIssue]:
        """Validate parameter type."""
        actual_type = type(value).__name__

        # Handle optional types
        if expected_type.startswith("optional["):
            if value is None:
                return None
            expected_type = expected_type[9:-1]  # Remove optional wrapper

        # Type mapping
        type_map: dict[str, type | tuple[type, ...]] = {
            "str": str,
            "string": str,
            "int": int,
            "integer": int,
            "float": float,
            "number": (int, float),
            "bool": bool,
            "boolean": bool,
            "list": list,
            "array": list,
            "dict": dict,
            "object": dict,
        }

        expected_python_type = type_map.get(expected_type.lower())
        if expected_python_type and not isinstance(value, expected_python_type):
            return ValidationIssue(
                parameter=param_name,
                severity=ValidationSeverity.ERROR,
                message=f"Type mismatch: expected {expected_type}, got {actual_type}",
                expected=expected_type,
                actual=actual_type,
                suggestion=f"Convert to {expected_type}",
            )

        return None

    def _validate_constraints(
        self, param_name: str, value: Any, constraints: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Validate parameter constraints."""
        issues = []

        # String length constraints
        if isinstance(value, str):
            if "min_length" in constraints and len(value) < constraints["min_length"]:
                issues.append(
                    ValidationIssue(
                        parameter=param_name,
                        severity=ValidationSeverity.ERROR,
                        message=f"String too short: {len(value)} < "
                        f"{constraints['min_length']}",
                        expected=f"min {constraints['min_length']} characters",
                        actual=f"{len(value)} characters",
                        suggestion=f"Add {constraints['min_length'] - len(value)} "
                        f"more characters",
                    )
                )

            if "max_length" in constraints and len(value) > constraints["max_length"]:
                issues.append(
                    ValidationIssue(
                        parameter=param_name,
                        severity=ValidationSeverity.ERROR,
                        message=f"String too long: {len(value)} > "
                        f"{constraints['max_length']}",
                        expected=f"max {constraints['max_length']} characters",
                        actual=f"{len(value)} characters",
                        suggestion=f"Remove {len(value) - constraints['max_length']} "
                        f"characters",
                    )
                )

        # Numeric constraints
        if isinstance(value, (int, float)):
            if "minimum" in constraints and value < constraints["minimum"]:
                issues.append(
                    ValidationIssue(
                        parameter=param_name,
                        severity=ValidationSeverity.ERROR,
                        message=f"Value too small: {value} < {constraints['minimum']}",
                        expected=f"min {constraints['minimum']}",
                        actual=str(value),
                        suggestion=f"Use value >= {constraints['minimum']}",
                    )
                )

            if "maximum" in constraints and value > constraints["maximum"]:
                issues.append(
                    ValidationIssue(
                        parameter=param_name,
                        severity=ValidationSeverity.ERROR,
                        message=f"Value too large: {value} > {constraints['maximum']}",
                        expected=f"max {constraints['maximum']}",
                        actual=str(value),
                        suggestion=f"Use value <= {constraints['maximum']}",
                    )
                )

        # Enum constraints
        if (
            "allowed_values" in constraints
            and value not in constraints["allowed_values"]
        ):
            issues.append(
                ValidationIssue(
                    parameter=param_name,
                    severity=ValidationSeverity.ERROR,
                    message=f"Invalid value: {value} not in allowed values",
                    expected=f"one of {constraints['allowed_values']}",
                    actual=str(value),
                    suggestion=f"Use one of: "
                    f"{', '.join(map(str, constraints['allowed_values']))}",
                )
            )

        # UUID validation
        if "validator" in constraints and "uuid" in constraints["validator"]:
            if not self.validator.validate_uuid(str(value)):
                issues.append(
                    ValidationIssue(
                        parameter=param_name,
                        severity=ValidationSeverity.ERROR,
                        message=f"Invalid UUID format: {value}",
                        expected="valid UUID format",
                        actual=str(value),
                        suggestion="Use format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                    )
                )

        return issues

    def _validate_parameter_relationships(
        self, parameters: Dict[str, Any], schema: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Validate parameter relationships."""
        issues = []

        # Common relationship patterns
        if "project_id" in parameters and "task_id" in parameters:
            # Both present - good relationship
            pass
        elif "task_id" in parameters and "project_id" not in parameters:
            issues.append(
                ValidationIssue(
                    parameter="project_id",
                    severity=ValidationSeverity.WARNING,
                    message="task_id provided without project_id",
                    expected="project_id when task_id is present",
                    suggestion="Add project_id parameter",
                )
            )

        return issues

    def _validate_parameter_combinations(
        self, parameters: Dict[str, Any], schema: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Validate parameter combinations."""
        issues = []

        # Check if we have a valid combination of parameters
        required = schema.get("required", [])
        provided_required = [p for p in required if p in parameters]

        if len(provided_required) < len(required):
            missing = [p for p in required if p not in parameters]
            issues.append(
                ValidationIssue(
                    parameter="combination",
                    severity=ValidationSeverity.ERROR,
                    message="Incomplete required parameter combination",
                    expected=f"all required: {required}",
                    actual=f"provided: {provided_required}",
                    suggestion=f"Add missing: {missing}",
                )
            )

        return issues

    def _validate_data_consistency(
        self, parameters: Dict[str, Any], schema: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """Validate data consistency without referencing actual data."""
        issues = []

        # Check for obviously inconsistent values
        if "status" in parameters and "new_status" in parameters:
            if parameters["status"] == parameters["new_status"]:
                issues.append(
                    ValidationIssue(
                        parameter="new_status",
                        severity=ValidationSeverity.WARNING,
                        message="new_status same as current status",
                        expected="different status value",
                        actual=str(parameters["new_status"]),
                        suggestion="Use a different status value",
                    )
                )

        return issues

    def _analyze_relationships(
        self, parameters: Dict[str, Any], schema: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Analyze parameter relationships."""
        relationships = {}

        # Find related parameters that are present
        param_groups = {
            "project_task": ["project_id", "task_id"],
            "status_change": ["status", "new_status"],
            "assignment": ["assignee", "assigned_to"],
        }

        for group_name, group_params in param_groups.items():
            present_params = [p for p in group_params if p in parameters]
            if len(present_params) > 1:
                relationships[group_name] = present_params

        return relationships

    def _generate_guidance(
        self,
        parameters: Dict[str, Any],
        schema: Dict[str, Any],
        validation_result: Dict[str, Any],
        structure_result: Dict[str, Any],
    ) -> List[str]:
        """Generate validation guidance."""
        guidance = []

        if not validation_result.get("valid", False):
            guidance.append("Fix parameter validation errors before proceeding")

        if validation_result.get("missing_required"):
            missing = validation_result["missing_required"]
            guidance.append(f"Add required parameters: {', '.join(missing)}")

        if validation_result.get("unexpected_params"):
            unexpected = validation_result["unexpected_params"]
            guidance.append(f"Remove unexpected parameters: {', '.join(unexpected)}")

        if validation_result.get("validation_score", 0) < 0.8:
            guidance.append("Consider reviewing parameter values for accuracy")

        return guidance

    def _suggest_next_steps(
        self,
        parameters: Dict[str, Any],
        schema: Dict[str, Any],
        validation_result: Dict[str, Any],
    ) -> List[str]:
        """Suggest next steps for fixing validation issues."""
        steps = []

        # Priority order for fixes
        if validation_result.get("missing_required"):
            steps.append("1. Add missing required parameters")

        error_issues = [
            issue
            for issue in validation_result.get("issues", [])
            if issue.get("severity") == "error"
        ]
        if error_issues:
            steps.append("2. Fix parameter type and constraint errors")

        warning_issues = [
            issue
            for issue in validation_result.get("issues", [])
            if issue.get("severity") == "warning"
        ]
        if warning_issues:
            steps.append("3. Address parameter warnings")

        if validation_result.get("valid", False):
            steps.append("✅ Parameters are valid - ready for execution")

        return steps

    def _generate_fix_examples(
        self,
        parameters: Dict[str, Any],
        schema: Dict[str, Any],
        validation_result: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate examples of how to fix validation issues."""
        examples = []

        for issue in validation_result.get("issues", [])[:3]:  # Limit to 3 examples
            if issue.get("suggestion"):
                examples.append(
                    {
                        "parameter": issue["parameter"],
                        "problem": issue["message"],
                        "fix": issue["suggestion"],
                        "example": self._get_fix_example(
                            issue["parameter"], issue.get("expected", "")
                        ),
                    }
                )

        return examples

    def _get_fix_example(self, param_name: str, expected_type: str) -> str:
        """Get a fix example for a parameter."""
        examples = {
            "str": '"example_string"',
            "int": "42",
            "bool": "true",
            "list": '["item1", "item2"]',
            "dict": '{"key": "value"}',
            "uuid": '"123e4567-e89b-12d3-a456-426614174000"',
        }

        return examples.get(expected_type.lower(), f'"{param_name}_value"')

    def _result_to_dict(self, result: ValidationResult) -> Dict[str, Any]:
        """Convert validation result to dictionary."""
        return {
            "valid": result.valid,
            "tool_name": result.tool_name,
            "gateway": result.gateway,
            "issues": [self._issue_to_dict(issue) for issue in result.issues],
            "missing_required": result.missing_required,
            "unexpected_params": result.unexpected_params,
            "validation_score": result.validation_score,
        }

    def _issue_to_dict(self, issue: ValidationIssue) -> Dict[str, Any]:
        """Convert validation issue to dictionary."""
        return {
            "parameter": issue.parameter,
            "severity": issue.severity.value,
            "message": issue.message,
            "expected": issue.expected,
            "actual": issue.actual,
            "suggestion": issue.suggestion,
        }


# Global instance for easy access
lackey_validate = LackeyValidateTool()
