"""Template system for agent instantiation and project setup.

This module provides a flexible template system that enables quick project
setup and agent instantiation with customizable templates.
"""

from __future__ import annotations

import os
import re
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from .models import Complexity, Project, Task
from .path_security import validate_path
from .validation import ValidationError


class TemplateType(Enum):
    """Template type enumeration."""

    PROJECT = "project"
    AGENT = "agent"
    TASK_CHAIN = "task_chain"
    WORKFLOW = "workflow"


class VariableType(Enum):
    """Template variable type enumeration."""

    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    CHOICE = "choice"


@dataclass
class TemplateVariable:
    """Template variable definition."""

    name: str
    type: VariableType
    description: str
    default: Optional[Any] = None
    required: bool = True
    choices: Optional[List[str]] = None
    validation_pattern: Optional[str] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None

    def validate_value(self, value: Any) -> bool:
        """Validate a value against this variable's constraints."""
        if value is None:
            return not self.required

        # Type validation
        if self.type == VariableType.STRING and not isinstance(value, str):
            return False
        elif self.type == VariableType.INTEGER and not isinstance(value, int):
            return False
        elif self.type == VariableType.BOOLEAN and not isinstance(value, bool):
            return False
        elif self.type == VariableType.LIST and not isinstance(value, list):
            return False
        elif self.type == VariableType.DICT and not isinstance(value, dict):
            return False

        # Choice validation
        if self.choices and value not in self.choices:
            return False

        # Pattern validation for strings
        if (
            self.validation_pattern
            and isinstance(value, str)
            and not re.match(self.validation_pattern, value)
        ):
            return False

        # Range validation for numbers
        if isinstance(value, (int, float)):
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "default": self.default,
            "required": self.required,
            "choices": self.choices,
            "validation_pattern": self.validation_pattern,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TemplateVariable:
        """Create from dictionary."""
        return cls(
            name=data["name"],
            type=VariableType(data["type"]),
            description=data["description"],
            default=data.get("default"),
            required=data.get("required", True),
            choices=data.get("choices"),
            validation_pattern=data.get("validation_pattern"),
            min_value=data.get("min_value"),
            max_value=data.get("max_value"),
        )


@dataclass
class Template:
    """Template definition for projects, agents, or workflows."""

    id: str
    name: str
    friendly_name: str
    description: str
    template_type: TemplateType
    version: str
    author: Optional[str] = None
    created: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated: datetime = field(default_factory=lambda: datetime.now(UTC))
    tags: List[str] = field(default_factory=list)
    variables: List[TemplateVariable] = field(default_factory=list)
    extends: Optional[str] = None  # Template inheritance
    content: Dict[str, Any] = field(default_factory=dict)
    files: Dict[str, str] = field(default_factory=dict)  # File templates
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate template after initialization."""
        if not self.id:
            self.id = str(uuid.uuid4())

    @classmethod
    def create_new(
        cls,
        name: str,
        friendly_name: str,
        description: str,
        template_type: TemplateType,
        version: str = "1.0.0",
        author: Optional[str] = None,
        tags: Optional[List[str]] = None,
        variables: Optional[List[TemplateVariable]] = None,
        extends: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Template:
        """Create a new template."""
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            friendly_name=friendly_name,
            description=description,
            template_type=template_type,
            version=version,
            author=author,
            tags=tags or [],
            variables=variables or [],
            extends=extends,
            content=content or {},
            files=files or {},
            metadata=metadata or {},
        )

    def validate_variables(self, values: Dict[str, Any]) -> List[str]:
        """Validate variable values against template constraints."""
        errors = []

        # Check required variables
        for var in self.variables:
            if var.required and var.name not in values:
                errors.append(f"Required variable '{var.name}' is missing")
                continue

            if var.name in values and not var.validate_value(values[var.name]):
                errors.append(f"Invalid value for variable '{var.name}'")

        return errors

    def substitute_variables(self, template_str: str, values: Dict[str, Any]) -> str:
        """Substitute template variables in a string."""
        # Use default values for missing variables
        substitution_values = {}
        for var in self.variables:
            if var.name in values:
                substitution_values[var.name] = values[var.name]
            elif var.default is not None:
                substitution_values[var.name] = var.default

        # Simple variable substitution using {{variable_name}} syntax
        result = template_str
        for name, value in substitution_values.items():
            pattern = f"{{{{{name}}}}}"
            result = result.replace(pattern, str(value))

        return result

    def render_content(self, values: Dict[str, Any]) -> Dict[str, Any]:
        """Render template content with variable substitution."""
        # Validate variables first
        errors = self.validate_variables(values)
        if errors:
            raise ValidationError(f"Template validation failed: {'; '.join(errors)}")

        # Deep copy content and substitute variables
        def substitute_recursive(obj: Any) -> Any:
            if isinstance(obj, str):
                return self.substitute_variables(obj, values)
            elif isinstance(obj, dict):
                return {k: substitute_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [substitute_recursive(item) for item in obj]
            else:
                return obj

        result = substitute_recursive(self.content)
        # Ensure we return a Dict[str, Any] as promised
        if isinstance(result, dict):
            return result
        else:
            return {"content": result}

    def render_files(self, values: Dict[str, Any]) -> Dict[str, str]:
        """Render file templates with variable substitution."""
        rendered_files = {}
        for filename, content in self.files.items():
            rendered_filename = self.substitute_variables(filename, values)
            rendered_content = self.substitute_variables(content, values)
            rendered_files[rendered_filename] = rendered_content
        return rendered_files

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "friendly_name": self.friendly_name,
            "description": self.description,
            "template_type": self.template_type.value,
            "version": self.version,
            "author": self.author,
            "created": self.created.isoformat(),
            "updated": self.updated.isoformat(),
            "tags": self.tags,
            "variables": [var.to_dict() for var in self.variables],
            "extends": self.extends,
            "content": self.content,
            "files": self.files,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Template:
        """Create from dictionary."""
        variables = [
            TemplateVariable.from_dict(var_data)
            for var_data in data.get("variables", [])
        ]

        return cls(
            id=data["id"],
            name=data["name"],
            friendly_name=data["friendly_name"],
            description=data["description"],
            template_type=TemplateType(data["template_type"]),
            version=data["version"],
            author=data.get("author"),
            created=datetime.fromisoformat(data["created"]),
            updated=datetime.fromisoformat(data["updated"]),
            tags=data.get("tags", []),
            variables=variables,
            extends=data.get("extends"),
            content=data.get("content", {}),
            files=data.get("files", {}),
            metadata=data.get("metadata", {}),
        )


class TemplateManager:
    """Manager for template operations and storage."""

    def __init__(self, templates_dir: Path):
        """Initialize template manager."""
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._templates: Dict[str, Template] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """Load all templates from the templates directory."""
        self._templates.clear()

        for template_file in self.templates_dir.glob("*.yaml"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    template = Template.from_dict(data)
                    self._templates[template.id] = template
            except Exception as e:
                # Log error but continue loading other templates
                print(f"Warning: Failed to load template {template_file}: {e}")

    def _save_template(self, template: Template) -> None:
        """Save a template to disk."""
        template_file = self.templates_dir / f"{template.name}.yaml"

        # Validate path security
        validate_path(str(template_file), [str(self.templates_dir)])

        with open(template_file, "w", encoding="utf-8") as f:
            yaml.dump(template.to_dict(), f, default_flow_style=False, sort_keys=False)

    def create_template(
        self,
        name: str,
        friendly_name: str,
        description: str,
        template_type: TemplateType,
        version: str = "1.0.0",
        author: Optional[str] = None,
        tags: Optional[List[str]] = None,
        variables: Optional[List[TemplateVariable]] = None,
        extends: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Template:
        """Create and save a new template."""
        template = Template.create_new(
            name=name,
            friendly_name=friendly_name,
            description=description,
            template_type=template_type,
            version=version,
            author=author,
            tags=tags,
            variables=variables,
            extends=extends,
            content=content,
            files=files,
            metadata=metadata,
        )

        self._templates[template.id] = template
        self._save_template(template)
        return template

    def get_template(self, template_id: str) -> Optional[Template]:
        """Get a template by ID."""
        return self._templates.get(template_id)

    def get_template_by_name(self, name: str) -> Optional[Template]:
        """Get a template by name."""
        for template in self._templates.values():
            if template.name == name:
                return template
        return None

    def list_templates(
        self,
        template_type: Optional[TemplateType] = None,
        tag: Optional[str] = None,
    ) -> List[Template]:
        """List templates with optional filtering."""
        templates = list(self._templates.values())

        if template_type:
            templates = [t for t in templates if t.template_type == template_type]

        if tag:
            templates = [t for t in templates if tag in t.tags]

        return sorted(templates, key=lambda t: t.friendly_name)

    def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        template = self._templates.get(template_id)
        if not template:
            return False

        # Remove from memory
        del self._templates[template_id]

        # Remove file
        template_file = self.templates_dir / f"{template.name}.yaml"
        if template_file.exists():
            template_file.unlink()

        return True

    def instantiate_project(self, template_id: str, values: Dict[str, Any]) -> Project:
        """Instantiate a project from a template."""
        template = self.get_template(template_id)
        if not template:
            raise ValidationError(f"Template {template_id} not found")

        if template.template_type != TemplateType.PROJECT:
            raise ValidationError(f"Template {template_id} is not a project template")

        # Render template content
        rendered_content = template.render_content(values)

        # Create project from rendered content
        project_data = rendered_content.get("project", {})

        project = Project.create_new(
            friendly_name=project_data.get("friendly_name", template.friendly_name),
            description=project_data.get("description", template.description),
            objectives=project_data.get("objectives", []),
            tags=project_data.get("tags", template.tags),
            metadata=project_data.get("metadata", {}),
        )

        return project

    def instantiate_tasks(self, template_id: str, values: Dict[str, Any]) -> List[Task]:
        """Instantiate tasks from a template."""
        template = self.get_template(template_id)
        if not template:
            raise ValidationError(f"Template {template_id} not found")

        if template.template_type not in (
            TemplateType.TASK_CHAIN,
            TemplateType.WORKFLOW,
        ):
            raise ValidationError(
                f"Template {template_id} is not a task chain or workflow template"
            )

        # Render template content
        rendered_content = template.render_content(values)

        # Create tasks from rendered content
        tasks = []
        tasks_data = rendered_content.get("tasks", [])

        for task_data in tasks_data:
            task = Task.create_new(
                title=task_data["title"],
                objective=task_data["objective"],
                steps=task_data.get("steps", []),
                success_criteria=task_data.get("success_criteria", []),
                complexity=Complexity(task_data.get("complexity", "medium")),
                context=task_data.get("context"),
                assigned_to=task_data.get("assigned_to"),
                tags=task_data.get("tags", []),
                dependencies=set(task_data.get("dependencies", [])),
            )
            tasks.append(task)

        return tasks

    def instantiate_agent(
        self, template_id: str, values: Dict[str, Any], output_dir: Path
    ) -> Path:
        """Instantiate an Amazon Q agent from a template."""
        template = self.get_template(template_id)
        if not template:
            raise ValidationError(f"Template {template_id} not found")

        if template.template_type != TemplateType.AGENT:
            raise ValidationError(f"Template {template_id} is not an agent template")

        # Render file templates
        rendered_files = template.render_files(values)

        # Find the agent JSON file (should be the one with .json extension)
        agent_json_file = None

        for filename, content in rendered_files.items():
            if filename.endswith(".json"):
                agent_json_file = filename
                break

        if not agent_json_file:
            raise ValidationError("Agent template must include a JSON agent file")

        # Create the agent file
        agent_file_path = os.path.join(output_dir, agent_json_file)
        validate_path(agent_file_path, [str(output_dir)])
        agent_path = Path(agent_file_path)

        # Create parent directories if needed
        agent_path.parent.mkdir(parents=True, exist_ok=True)

        # Write agent JSON file
        with open(agent_path, "w", encoding="utf-8") as f:
            f.write(rendered_files[agent_json_file])

        # Create other files (documentation, etc.)
        for filename, content in rendered_files.items():
            if filename != agent_json_file:
                file_path = os.path.join(output_dir, filename)
                validate_path(file_path, [str(output_dir)])
                file_path_obj = Path(file_path)
                file_path_obj.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path_obj, "w", encoding="utf-8") as f:
                    f.write(content)

        return agent_path

    def create_files_from_template(
        self, template_id: str, values: Dict[str, Any], output_dir: Path
    ) -> List[Path]:
        """Create files from a template."""
        template = self.get_template(template_id)
        if not template:
            raise ValidationError(f"Template {template_id} not found")

        # Render file templates
        rendered_files = template.render_files(values)

        created_files = []
        for filename, content in rendered_files.items():
            file_path = os.path.join(output_dir, filename)
            validate_path(file_path, [str(output_dir)])
            file_path_obj = Path(file_path)

            # Create parent directories if needed
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)

            # Write file content
            with open(file_path_obj, "w", encoding="utf-8") as f:
                f.write(content)

            created_files.append(file_path_obj)

        return created_files
