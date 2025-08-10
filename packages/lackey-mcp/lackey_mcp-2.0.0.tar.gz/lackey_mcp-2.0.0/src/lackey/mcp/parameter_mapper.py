"""Advanced parameter mapping engine for gateway routing optimization.

This module implements enhanced parameter mapping with:
- Schema-based validation and transformation
- Dynamic parameter inference from context
- Type conversion and normalization
- Advanced mapping rules for complex scenarios
- Performance optimization for <50ms validation
"""

import asyncio
import logging
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class ParameterType(Enum):
    """Parameter type definitions for validation and conversion."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    UUID = "uuid"
    DATETIME = "datetime"
    ENUM = "enum"


class ValidationSeverity(Enum):
    """Validation error severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ParameterSchema:
    """Schema definition for parameter validation."""

    name: str
    param_type: ParameterType
    required: bool = False
    default: Any = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    description: str = ""
    transform_func: Optional[Callable] = None
    enum_class: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of parameter validation."""

    is_valid: bool
    validated_value: Any
    errors: List[str]
    warnings: List[str]
    transformations_applied: List[str]


@dataclass
class MappingRule:
    """Rule for mapping gateway parameters to tool parameters."""

    source_path: str
    target_param: str
    transform_func: Optional[Callable] = None
    condition: Optional[Callable] = None
    default_value: Any = None
    required: bool = False


class AdvancedParameterMapper:
    """Advanced parameter mapping with validation and transformation."""

    def __init__(self) -> None:
        """Initialize the parameter mapper."""
        self.type_converters = self._load_type_converters()
        self.validation_cache: Dict[str, Any] = {}
        self.transformation_stats: Dict[str, int] = {}
        self.common_patterns = self._load_common_patterns()

    def _load_type_converters(self) -> Dict[ParameterType, Callable]:
        """Load type conversion functions."""
        return {
            ParameterType.STRING: self._convert_to_string,
            ParameterType.INTEGER: self._convert_to_integer,
            ParameterType.FLOAT: self._convert_to_float,
            ParameterType.BOOLEAN: self._convert_to_boolean,
            ParameterType.LIST: self._convert_to_list,
            ParameterType.DICT: self._convert_to_dict,
            ParameterType.UUID: self._convert_to_uuid,
            ParameterType.DATETIME: self._convert_to_datetime,
            ParameterType.ENUM: self._convert_to_enum,
        }

    def _load_common_patterns(self) -> Dict[str, str]:
        """Load common regex patterns for parameter extraction."""
        return {
            "project_id": r"(?:project|proj)\s+([a-zA-Z0-9_-]+)",
            "task_id": r"(?:task|t)\s+([a-zA-Z0-9_-]+)",
            "user_id": r"(?:user|@)([a-zA-Z0-9_-]+)",
            "status": r"(?:status|as|to)\s+(todo|in-progress|blocked|done)",
            "complexity": r"(?:complexity|priority)\s+(low|medium|high)",
            "assignee": r"(?:assign|to|for)\s+([a-zA-Z0-9_-]+)",
            "assigned_to": r"(?:assigned?\s+to|for)\s+([a-zA-Z0-9_-]+)",
            "title": r"(?:task|create)\s+['\"]([^'\"]+)['\"]",
            "objective": r"(?:objective|goal|purpose):\s*([^,\n]+)",
            "number": r"(\d+)",
            "quoted_string": r'["\']([^"\']+)["\']',
            "boolean": r"\b(true|false|yes|no|on|off)\b",
            # Enhanced filtering patterns
            "complexity_filter": (
                r"\b(low|medium|high)\s+complexity\b|"
                r"\b(low|medium|high)\s+priority\b|"
                r"\blist\s+(low|medium|high)\b"
            ),
            "assignee_filter": (
                r"assigned\s+to\s+([a-zA-Z0-9_-]+)|"
                r"for\s+([a-zA-Z0-9_-]+)|@([a-zA-Z0-9_-]+)"
            ),
            "tag_filter": (
                r"(?:with|tagged|tag)\s+([a-zA-Z0-9_-]+)(?:\s+tag)?|"
                r"([a-zA-Z0-9_-]+)\s+tag"
            ),
            "status_filter": r"\b(todo|in-progress|blocked|done)\s+(?:tasks|status)\b",
        }

    async def map_parameters(
        self,
        request: Dict[str, Any],
        mapping_rules: List[MappingRule],
        parameter_schemas: Dict[str, ParameterSchema],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Map and validate parameters using advanced rules and schemas.

        Args:
            request: The incoming request data
            mapping_rules: Rules for mapping parameters
            parameter_schemas: Validation schemas for parameters
            context: Optional context for dynamic inference

        Returns:
            Dictionary of validated and transformed parameters
        """
        start_time = asyncio.get_event_loop().time()

        try:
            mapped_params = {}
            validation_errors = []
            warnings = []

            # Apply mapping rules
            for rule in mapping_rules:
                try:
                    value = await self._apply_mapping_rule(request, rule, context)
                    if value is not None:
                        mapped_params[rule.target_param] = value
                except Exception as e:
                    if rule.required:
                        validation_errors.append(
                            f"Failed to map required parameter {rule.target_param}: {e}"
                        )
                    else:
                        warnings.append(
                            f"Failed to map optional parameter {rule.target_param}: {e}"
                        )

            # Apply dynamic inference for missing parameters
            inferred_params = await self._infer_missing_parameters(
                request, mapped_params, parameter_schemas, context
            )
            mapped_params.update(inferred_params)

            # Validate and transform parameters
            validated_params = {}
            for param_name, schema in parameter_schemas.items():
                if (
                    param_name in mapped_params
                    and mapped_params[param_name] is not None
                ):
                    validation_result = await self._validate_parameter(
                        param_name, mapped_params[param_name], schema
                    )

                    if validation_result.is_valid:
                        validated_params[param_name] = validation_result.validated_value
                    else:
                        validation_errors.extend(validation_result.errors)

                    warnings.extend(validation_result.warnings)

                elif schema.required:
                    if schema.default is not None:
                        # Validate and convert default value
                        validation_result = await self._validate_parameter(
                            param_name, schema.default, schema
                        )
                        if validation_result.is_valid:
                            validated_params[param_name] = (
                                validation_result.validated_value
                            )
                        else:
                            validation_errors.extend(validation_result.errors)
                    else:
                        validation_errors.append(
                            f"Required parameter '{param_name}' is missing"
                        )
                elif schema.default is not None:
                    # Validate and convert default value
                    validation_result = await self._validate_parameter(
                        param_name, schema.default, schema
                    )
                    if validation_result.is_valid:
                        validated_params[param_name] = validation_result.validated_value
                    else:
                        warnings.extend(validation_result.warnings)

            # Record performance metrics
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000

            if validation_errors:
                error_msg = "; ".join(validation_errors)
                logger.error(f"Parameter mapping failed: {error_msg}")
                raise ValueError(f"Parameter validation failed: {error_msg}")

            if warnings:
                logger.warning(f"Parameter mapping warnings: {'; '.join(warnings)}")

            logger.debug(f"Parameter mapping completed in {execution_time:.2f}ms")

            return validated_params

        except Exception as e:
            logger.error(f"Parameter mapping failed: {e}")
            raise

    async def _apply_mapping_rule(
        self,
        request: Dict[str, Any],
        rule: MappingRule,
        context: Optional[Dict[str, Any]],
    ) -> Any:
        """Apply a single mapping rule to extract parameter value."""
        # Check condition if specified
        if rule.condition and not rule.condition(request, context):
            return rule.default_value

        # Special handling for "infer" source path - trigger parameter inference
        if rule.source_path == "infer":
            text_content = self._extract_text_content(request)
            value = await self._infer_common_parameter(rule.target_param, text_content)
            return value if value is not None else rule.default_value

        # Extract value using source path
        value = self._extract_nested_value(request, rule.source_path)

        # If value not found, try pattern extraction
        if value is None:
            value = await self._extract_using_patterns(request, rule.target_param)

        # Apply transformation if specified
        if value is not None and rule.transform_func:
            try:
                value = rule.transform_func(value)
            except Exception as e:
                logger.warning(f"Transformation failed for {rule.target_param}: {e}")
                value = None

        # Return default if no value found
        return value if value is not None else rule.default_value

    def _extract_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Extract value from nested dictionary using dot notation.

        Supports multiple fallback paths separated by commas.
        """
        if not path:
            return None

        # Handle multiple fallback paths
        paths = [p.strip() for p in path.split(",")]

        for single_path in paths:
            if not single_path:
                continue

            keys = single_path.split(".")
            current = data

            # Try to traverse this path
            success = True
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    success = False
                    break

            # If we successfully traversed this path, return the value
            if success:
                return current

        # None of the paths worked
        return None

    async def _extract_using_patterns(
        self, request: Dict[str, Any], param_name: str
    ) -> Any:
        """Extract parameter value using regex patterns."""
        # Get all text content from request
        text_content = self._extract_text_content(request)

        if not text_content:
            return None

        # Enhanced filtering parameter extraction
        if param_name in ["complexity", "complexity_filter"]:
            return self._extract_complexity_filter(text_content)
        elif param_name in ["assigned_to", "assignee_filter", "assignee"]:
            return self._extract_assignee_filter(text_content)
        elif param_name in ["tags", "tag_filter"]:
            return self._extract_tag_filter(text_content)
        elif param_name in ["status", "status_filter"]:
            return self._extract_status_filter(text_content)

        # Try parameter-specific pattern first
        if param_name in self.common_patterns:
            pattern = self.common_patterns[param_name]
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                # Return first non-None group
                for group in match.groups():
                    if group:
                        return group

        # Try generic patterns based on parameter name
        generic_patterns = self._get_generic_patterns(param_name)
        for pattern in generic_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _extract_complexity_filter(self, text_content: str) -> Optional[str]:
        """Extract complexity filter from text content."""
        # Pattern: "high complexity", "low priority", "list high", etc.
        patterns = [
            r"\b(low|medium|high)\s+complexity\b",
            r"\b(low|medium|high)\s+priority\b",
            r"\blist\s+(low|medium|high)\b",
            r"\b(low|medium|high)\s+tasks\b",
        ]

        for pattern in patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                return match.group(1).lower()

        return None

    def _extract_assignee_filter(self, text_content: str) -> Optional[str]:
        """Extract assignee filter from text content."""
        # Patterns for assignee filtering - made specific to avoid false matches
        patterns = [
            # Direct assignment patterns
            r"assigned\s+to\s+([a-zA-Z0-9_-]+)",
            r"assign\s+(?:task\s+)?[a-zA-Z0-9_-]+\s+to\s+([a-zA-Z0-9_-]+)",
            # Ownership patterns
            r"owned\s+by\s+([a-zA-Z0-9_-]+)",
            r"belongs\s+to\s+([a-zA-Z0-9_-]+)",
            # Task listing with specific assignee context
            r"(?:show|list|get|find)\s+tasks\s+(?:assigned\s+to|for|owned\s+by)\s+"
            r"([a-zA-Z0-9_-]+)",
            r"(?:tasks\s+assigned\s+to|assigned\s+tasks\s+for)\s+" r"([a-zA-Z0-9_-]+)",
            r"tasks\s+owned\s+by\s+([a-zA-Z0-9_-]+)",
            # @ mentions
            r"@([a-zA-Z0-9_-]+)",
            # "for user" but only in specific contexts (not generic "for tasks")
            r"(?:show|list|get|find)\s+.*\s+for\s+([a-zA-Z0-9_-]+)"
            r"(?:\s+in|\s+with|\s*$)",
            # Possessive forms
            r"([a-zA-Z0-9_-]+)'s\s+tasks",
            r"tasks\s+of\s+([a-zA-Z0-9_-]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                assignee = match.group(1)
                # Filter out common words that aren't usernames
                if assignee.lower() not in [
                    "tasks",
                    "task",
                    "all",
                    "any",
                    "some",
                    "with",
                    "that",
                    "which",
                    "what",
                ]:
                    return assignee

        return None

    def _extract_tag_filter(self, text_content: str) -> Optional[List[str]]:
        """Extract tag filter from text content."""
        # Pattern: "with frontend tag", "tagged backend", "database tag"
        patterns = [
            r"with\s+([a-zA-Z0-9_-]+)\s+tag",
            r"tagged\s+([a-zA-Z0-9_-]+)",
            r"tag\s+([a-zA-Z0-9_-]+)",
        ]

        tags = []
        for pattern in patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                tag = match.group(1)
                # Skip common project-related terms, UUIDs, and assignment-related words
                if (
                    tag not in tags
                    and not re.match(r"^[a-f0-9-]{36}$", tag)
                    and tag
                    not in [
                        "project",
                        "in",
                        "with",
                        "tasks",
                        "task",
                        "assigned",
                        "to",
                        "for",
                    ]
                ):
                    tags.append(tag)

        return tags if tags else None

    def _extract_status_filter(self, text_content: str) -> Optional[str]:
        """Extract status filter from text content.

        Note: Extraction layer returns raw string values. The validation layer
        handles type conversion and enum validation to maintain clean separation.
        """
        patterns = [
            r"\b(todo|in_progress|blocked|done)\s+(?:tasks|status)\b",
            r"status\s+(?:to\s+)?(todo|in_progress|blocked|done)",
            r"list\s+(todo|in_progress|blocked|done)",
            r"(?:update|change|set)\s+(?:task\s+)?[a-zA-Z0-9_-]+\s+status\s+to\s+"
            r"(todo|in_progress|blocked|done)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                status = match.group(1).lower()
                # Basic validation - full enum validation happens in validation layer
                valid_statuses = ["todo", "in_progress", "blocked", "done"]
                if status in valid_statuses:
                    return status
                else:
                    logger.warning(f"Invalid status value: {status}")
                    return None

        return None

    def _extract_search_terms(self, text_content: str) -> Optional[str]:
        """Extract search terms from natural language text search queries."""
        # Patterns for text search queries - updated to capture multi-word phrases
        search_patterns = [
            # "tasks that mention X", "tasks mentioning X" - capture multi-word phrases
            r"tasks?\s+that\s+mention(?:s?|ing)\s+([a-zA-Z0-9_\s-]+?)"
            r"(?:\s+(?:in|from|for|with|and|or|but)|$)",
            # "tasks that contain X", "tasks containing X"
            r"tasks?\s+that\s+contain(?:s?|ing)\s+([a-zA-Z0-9_\s-]+?)"
            r"(?:\s+(?:in|from|for|with|and|or|but)|$)",
            # "tasks about X"
            r"tasks?\s+about\s+([a-zA-Z0-9_\s-]+?)"
            r"(?:\s+(?:in|from|for|with|and|or|but)|$)",
            # "find tasks that X", "search for tasks that X"
            r"(?:find|search\s+for)\s+tasks?\s+that\s+(?:mention|contain|have)\s+"
            r"([a-zA-Z0-9_\s-]+?)(?:\s+(?:in|from|for|with|and|or|but)|$)",
            # "show me tasks with X", "tasks with text X"
            r"(?:show\s+me\s+)?tasks?\s+with\s+(?:text\s+)?"
            r"([a-zA-Z0-9_\s-]+?)(?:\s+(?:in|from|for|with|and|or|but)|$)",
            # "tasks with word X", "containing word X"
            r"(?:tasks?\s+with\s+(?:the\s+)?word|containing\s+(?:the\s+)?word)\s+"
            r"['\"]?([a-zA-Z0-9_\s-]+?)['\"]?"
            r"(?:\s+(?:in|from|for|with|and|or|but)|$)",
            # Quoted search terms: "database", 'API', etc.
            r"(?:mention|contain|about|with|having)\s+['\"]([^'\"]+)['\"]",
            # Simple patterns: "mention X", "containing X" - capture
            # multi-word phrases
            r"(?:mention|mentioning|contain|containing)\s+"
            r"([a-zA-Z0-9_\s-]+?)(?:\s+(?:in|from|for|with|and|or|but)|$)",
            # "search for tasks with X" - more specific pattern
            r"search\s+for\s+tasks\s+with\s+([a-zA-Z0-9_\s-]+?)(?:\s*$)",
        ]

        for pattern in search_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                search_term = match.group(1).strip()
                # Filter out common words that aren't useful search terms
                if search_term.lower() not in [
                    "the",
                    "a",
                    "an",
                    "and",
                    "or",
                    "but",
                    "in",
                    "on",
                    "at",
                    "to",
                    "for",
                    "of",
                    "with",
                    "by",
                ]:
                    return search_term

        return None

    def _extract_text_content(self, request: Dict[str, Any]) -> str:
        """Extract all text content from request for pattern matching."""
        text_parts = []

        # Extract from main request, but exclude context to avoid false matches
        for key, value in request.items():
            if key == "context":
                continue  # Skip context to avoid extracting project IDs as tags
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, dict):
                text_parts.append(self._extract_text_content(value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        text_parts.append(item)
                    elif isinstance(item, dict):
                        text_parts.append(self._extract_text_content(item))

        return " ".join(filter(None, text_parts))

    def _get_generic_patterns(self, param_name: str) -> List[str]:
        """Get generic patterns based on parameter name."""
        patterns = []

        # ID patterns
        if param_name.endswith("_id"):
            base_name = param_name[:-3]
            patterns.append(rf"{base_name}\s+([a-zA-Z0-9_-]+)")
            patterns.append(rf"([a-zA-Z0-9_-]+)\s+{base_name}")

        # Status/enum patterns
        if param_name in ["status", "complexity", "priority"]:
            patterns.append(rf"{param_name}\s+(\w+)")
            patterns.append(rf"(\w+)\s+{param_name}")

        # User/assignee patterns
        if param_name in ["assignee", "assigned_to", "user", "owner"]:
            patterns.append(r"@([a-zA-Z0-9_-]+)")
            patterns.append(rf"{param_name}\s+([a-zA-Z0-9_-]+)")

        return patterns

    async def _infer_missing_parameters(
        self,
        request: Dict[str, Any],
        mapped_params: Dict[str, Any],
        schemas: Dict[str, ParameterSchema],
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Infer missing parameters from context and request content."""
        inferred = {}

        # Get the gateway configuration to determine which parameters are
        # actually mapped
        gateway_config = context.get("gateway_config", {}) if context else {}
        mapped_param_names = set(gateway_config.keys()) if gateway_config else set()

        # If we have a gateway config, ONLY infer parameters that are explicitly mapped
        # This prevents auto-extraction of unwanted filter parameters
        if mapped_param_names:
            # Infer from context - only for mapped parameters
            if context:
                for param_name in mapped_param_names:
                    if param_name in schemas and param_name not in mapped_params:
                        inferred_value = self._infer_from_context(param_name, context)
                        if inferred_value is not None:
                            inferred[param_name] = inferred_value

            # Infer from text content - only for mapped parameters
            text_content = self._extract_text_content(request)
            for param_name in mapped_param_names:
                if (
                    param_name in schemas
                    and param_name not in mapped_params
                    and param_name not in inferred
                ):
                    inferred_value = await self._infer_common_parameter(
                        param_name, text_content
                    )
                    if inferred_value is not None:
                        inferred[param_name] = inferred_value
        else:
            # Fallback: infer all schema parameters (legacy behavior)
            if context:
                for param_name, schema in schemas.items():
                    if param_name not in mapped_params:
                        inferred_value = self._infer_from_context(param_name, context)
                        if inferred_value is not None:
                            inferred[param_name] = inferred_value

            text_content = self._extract_text_content(request)
            for param_name, schema in schemas.items():
                if param_name not in mapped_params and param_name not in inferred:
                    inferred_value = await self._infer_common_parameter(
                        param_name, text_content
                    )
                    if inferred_value is not None:
                        inferred[param_name] = inferred_value

        return inferred

    def _infer_from_context(self, param_name: str, context: Dict[str, Any]) -> Any:
        """Infer parameter value from context."""
        # Direct context mapping
        if param_name in context:
            return context[param_name]

        # Common context mappings
        context_mappings = {
            "project_id": ["current_project", "project", "project_context"],
            "task_id": ["current_task", "task", "task_context"],
            "assignee": ["current_user", "user", "user_id"],
            "assigned_to": ["current_user", "user", "user_id"],
        }

        if param_name in context_mappings:
            for context_key in context_mappings[param_name]:
                if context_key in context:
                    return context[context_key]

        # Provide sensible defaults for common parameters when no context is available
        if param_name == "project_id":
            return "default"  # Default project for ambiguous queries

        return None

    async def _infer_common_parameter(self, param_name: str, text_content: str) -> Any:
        """Infer common parameter values from text content."""
        # Enhanced search query extraction for text search
        if param_name == "query":
            return self._extract_search_terms(text_content)

        # Enhanced filtering parameter inference
        if param_name in ["complexity", "complexity_filter"]:
            return self._extract_complexity_filter(text_content)
        elif param_name in ["assigned_to", "assignee_filter", "assignee"]:
            return self._extract_assignee_filter(text_content)
        elif param_name in ["tags", "tag_filter"]:
            return self._extract_tag_filter(text_content)
        elif param_name in ["status", "status_filter", "new_status"]:
            return self._extract_status_filter(text_content)

        # Enhanced task assignment compound operation parsing
        if param_name == "task_id":
            # Extract task ID from "assign task {task_id}" pattern
            task_match = re.search(
                r"assign\s+task\s+([a-f0-9-]+)", text_content, re.IGNORECASE
            )
            if task_match:
                return task_match.group(1)

        if param_name == "assignee":
            # Extract assignee from "to {assignee}" pattern
            assignee_match = re.search(r"\s+to\s+(\w+)", text_content, re.IGNORECASE)
            if assignee_match:
                return assignee_match.group(1)

        if param_name == "note":
            # Extract note from "with note 'text'" pattern
            note_match = re.search(
                r'with\s+note\s+[\'"]([^\'"]+)[\'"]', text_content, re.IGNORECASE
            )
            if note_match:
                return note_match.group(1)

        # Enhanced title extraction
        if param_name == "title":
            # Try quoted strings first
            quoted_match = re.search(r'["\']([^"\']+)["\']', text_content)
            if quoted_match:
                return quoted_match.group(1)

            # Try "create task X" pattern
            create_match = re.search(
                r'create\s+(?:task|new\s+task)\s+["\']?([^"\']+?)["\']?'
                r"(?:\s+for|\s+in|\s*$)",
                text_content,
                re.IGNORECASE,
            )
            if create_match:
                return create_match.group(1).strip()

            # Try "task X" pattern
            task_match = re.search(
                r'task\s+["\']?([^"\']+?)["\']?(?:\s+for|\s+in|\s*$)',
                text_content,
                re.IGNORECASE,
            )
            if task_match:
                return task_match.group(1).strip()

        # Enhanced objective extraction
        if param_name == "objective":
            # Try explicit objective patterns
            obj_match = re.search(
                r"(?:objective|goal|purpose):\s*([^,\n]+)", text_content, re.IGNORECASE
            )
            if obj_match:
                return obj_match.group(1).strip()

            # Infer from action context
            action_match = re.search(
                r"(?:create|implement|fix|build)\s+([^,\n]+)",
                text_content,
                re.IGNORECASE,
            )
            if action_match:
                return f"Complete: {action_match.group(1).strip()}"

        # Enhanced project_id extraction
        if param_name == "project_id":
            # Try "for X project" pattern
            project_match = re.search(
                r"for\s+([a-zA-Z0-9_-]+)\s+project", text_content, re.IGNORECASE
            )
            if project_match:
                return project_match.group(1)

            # Try "in X project" pattern
            in_project_match = re.search(
                r"in\s+([a-zA-Z0-9_-]+)\s+project", text_content, re.IGNORECASE
            )
            if in_project_match:
                return in_project_match.group(1)

            # Try "in X" pattern (more general)
            in_match = re.search(r"in\s+([a-zA-Z0-9_-]+)", text_content, re.IGNORECASE)
            if in_match:
                return in_match.group(1)

        # Enhanced note extraction
        if param_name == "note":
            # Try quoted note patterns
            note_patterns = [
                r"with\s+note\s+['\"]([^'\"]+)['\"]",
                r"note\s+['\"]([^'\"]+)['\"]",
                r"comment\s+['\"]([^'\"]+)['\"]",
            ]

            for pattern in note_patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    return match.group(1)

        # Generate UUID for ID parameters if not found
        if param_name.endswith("_id") and param_name.startswith("new_"):
            return str(uuid.uuid4())

        # Infer boolean parameters
        if param_name in ["force", "recursive", "dry_run", "verbose"]:
            if any(
                word in text_content.lower()
                for word in ["force", "recursive", "dry", "verbose"]
            ):
                return True

        # Infer timestamps
        if param_name in ["created", "updated", "timestamp"]:
            return datetime.now().isoformat()

        return None

    async def _validate_parameter(
        self, param_name: str, value: Any, schema: ParameterSchema
    ) -> ValidationResult:
        """Validate and transform a single parameter.

        Note: Validation layer handles all type conversion from raw extracted values.
        This maintains clean separation: Extraction → Validation → Tool execution.
        """
        errors = []
        warnings: List[str] = []
        transformations = []

        try:
            # Type conversion
            if schema.param_type in self.type_converters:
                converter = self.type_converters[schema.param_type]
                converted_value = converter(value, schema)
                if converted_value != value:
                    transformations.append(
                        f"Converted {param_name} from {type(value).__name__} "
                        f"to {schema.param_type.value}"
                    )
                value = converted_value

            # Apply custom transformation
            if schema.transform_func:
                transformed_value = schema.transform_func(value)
                if transformed_value != value:
                    transformations.append(
                        f"Applied custom transformation to {param_name}"
                    )
                value = transformed_value

            # Validate constraints
            validation_errors = self._validate_constraints(param_name, value, schema)
            errors.extend(validation_errors)

            is_valid = len(errors) == 0

            return ValidationResult(
                is_valid=is_valid,
                validated_value=value,
                errors=errors,
                warnings=warnings,
                transformations_applied=transformations,
            )

        except Exception as e:
            errors.append(f"Validation failed for {param_name}: {str(e)}")
            return ValidationResult(
                is_valid=False,
                validated_value=value,
                errors=errors,
                warnings=warnings,
                transformations_applied=transformations,
            )

    def _validate_constraints(
        self, param_name: str, value: Any, schema: ParameterSchema
    ) -> List[str]:
        """Validate parameter constraints."""
        errors = []

        # Length constraints for strings and lists
        if schema.min_length is not None:
            if hasattr(value, "__len__") and len(value) < schema.min_length:
                errors.append(
                    f"{param_name} must be at least {schema.min_length} "
                    f"characters/items long"
                )

        if schema.max_length is not None:
            if hasattr(value, "__len__") and len(value) > schema.max_length:
                errors.append(
                    f"{param_name} must be at most {schema.max_length} "
                    f"characters/items long"
                )

        # Value constraints for numbers
        if schema.min_value is not None:
            if isinstance(value, (int, float)) and value < schema.min_value:
                errors.append(f"{param_name} must be at least {schema.min_value}")

        if schema.max_value is not None:
            if isinstance(value, (int, float)) and value > schema.max_value:
                errors.append(f"{param_name} must be at most {schema.max_value}")

        # Pattern validation for strings
        if schema.pattern and isinstance(value, str):
            if not re.match(schema.pattern, value):
                errors.append(f"{param_name} does not match required pattern")

        # Allowed values validation
        if schema.allowed_values:
            # Handle enum objects - compare their values against allowed values
            if hasattr(value, "value") and hasattr(value, "name"):  # It's an enum
                if value.value not in schema.allowed_values:
                    errors.append(
                        f"{param_name} must be one of: "
                        f"{', '.join(map(str, schema.allowed_values))}"
                    )
            elif value not in schema.allowed_values:
                errors.append(
                    f"{param_name} must be one of: "
                    f"{', '.join(map(str, schema.allowed_values))}"
                )

        return errors

    # Type conversion methods
    def _convert_to_string(self, value: Any, schema: ParameterSchema) -> str:
        """Convert value to string."""
        if isinstance(value, str):
            return value
        return str(value)

    def _convert_to_integer(self, value: Any, schema: ParameterSchema) -> int:
        """Convert value to integer."""
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return int(value)
        if isinstance(value, float):
            return int(value)
        raise ValueError(f"Cannot convert {type(value).__name__} to integer")

    def _convert_to_float(self, value: Any, schema: ParameterSchema) -> float:
        """Convert value to float."""
        if isinstance(value, float):
            return value
        if isinstance(value, (int, str)):
            return float(value)
        raise ValueError(f"Cannot convert {type(value).__name__} to float")

    def _convert_to_boolean(self, value: Any, schema: ParameterSchema) -> bool:
        """Convert value to boolean."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ["true", "yes", "on", "1"]
        if isinstance(value, int):
            return bool(value)
        raise ValueError(f"Cannot convert {type(value).__name__} to boolean")

    def _convert_to_list(self, value: Any, schema: ParameterSchema) -> List[Any]:
        """Convert value to list."""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            # Try to parse as comma-separated values
            return [item.strip() for item in value.split(",")]
        if hasattr(value, "__iter__") and not isinstance(value, (str, dict)):
            return list(value)
        return [value]

    def _convert_to_dict(self, value: Any, schema: ParameterSchema) -> Dict[str, Any]:
        """Convert value to dictionary."""
        if isinstance(value, dict):
            return value
        raise ValueError(f"Cannot convert {type(value).__name__} to dictionary")

    def _convert_to_uuid(self, value: Any, schema: ParameterSchema) -> str:
        """Convert value to UUID string."""
        if isinstance(value, str):
            # Validate UUID format
            try:
                uuid.UUID(value)
                return value
            except ValueError:
                raise ValueError(f"Invalid UUID format: {value}")
        raise ValueError(f"Cannot convert {type(value).__name__} to UUID")

    def _convert_to_datetime(self, value: Any, schema: ParameterSchema) -> str:
        """Convert value to ISO datetime string."""
        if isinstance(value, str):
            # Try to parse and reformat
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return dt.isoformat()
            except ValueError:
                raise ValueError(f"Invalid datetime format: {value}")
        if isinstance(value, datetime):
            return value.isoformat()
        raise ValueError(f"Cannot convert {type(value).__name__} to datetime")

    def _convert_to_enum(self, value: Any, schema: ParameterSchema) -> Any:
        """Convert value to enum (validated against allowed values)."""
        if isinstance(value, str):
            # Handle TaskStatus enum conversion
            if schema.name in ["new_status", "status"]:
                from ..models import TaskStatus

                try:
                    # Convert string to TaskStatus enum
                    status_mapping = {
                        "todo": TaskStatus.TODO,
                        "in_progress": TaskStatus.IN_PROGRESS,
                        "blocked": TaskStatus.BLOCKED,
                        "done": TaskStatus.DONE,
                    }
                    if value.lower() in status_mapping:
                        return status_mapping[value.lower()]
                    else:
                        raise ValueError(f"Invalid status: {value}")
                except (AttributeError, ValueError):
                    pass

            # Handle NoteType enum conversion
            if schema.name == "note_type":
                from ..notes import NoteType

                try:
                    # Convert string to NoteType enum
                    note_type_mapping = {
                        "user": NoteType.USER,
                        "system": NoteType.SYSTEM,
                        "status_change": NoteType.STATUS_CHANGE,
                        "assignment": NoteType.ASSIGNMENT,
                        "progress": NoteType.PROGRESS,
                        "dependency": NoteType.DEPENDENCY,
                        "archive": NoteType.ARCHIVE,
                    }
                    if value.lower() in note_type_mapping:
                        return note_type_mapping[value.lower()]
                    else:
                        raise ValueError(f"Invalid note_type: {value}")
                except (AttributeError, ValueError):
                    pass

            if schema.allowed_values and value in schema.allowed_values:
                return value
            # Try case-insensitive match
            if schema.allowed_values:
                for allowed in schema.allowed_values:
                    if isinstance(allowed, str) and allowed.lower() == value.lower():
                        return allowed
            raise ValueError(
                f"Invalid enum value: {value}, must be one of {schema.allowed_values}"
            )
        raise ValueError(f"Cannot convert {type(value).__name__} to enum")

    def _convert_parameter_type(self, value: Any, target_type: type) -> Any:
        """Convert parameter to target type."""
        if isinstance(value, target_type):
            return value

        if target_type == bool:
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "on")
            return bool(value)
        elif target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)
        elif target_type == str:
            return str(value)
        elif target_type == list:
            if isinstance(value, list):
                return value
            return [value]
        elif target_type == dict:
            if isinstance(value, dict):
                return value
            return {"value": value}
        else:
            return value

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for monitoring."""
        return {
            "cache_size": len(self.validation_cache),
            "transformation_stats": dict(self.transformation_stats),
        }

    def clear_cache(self) -> None:
        """Clear validation cache for memory management."""
        self.validation_cache.clear()
        logger.debug("Parameter validation cache cleared")
