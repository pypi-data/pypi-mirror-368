"""Dynamic template generation system.

This module provides functionality to generate templates programmatically
based on analysis of existing projects, user preferences, and best practices.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

import yaml

from .models import Project, Task
from .templates import (
    Template,
    TemplateManager,
    TemplateType,
    TemplateVariable,
    VariableType,
)


@dataclass
class TemplateGenerationConfig:
    """Configuration for dynamic template generation."""

    include_common_variables: bool = True
    analyze_existing_projects: bool = True
    include_best_practices: bool = True
    generate_documentation: bool = True
    include_validation_rules: bool = True
    min_usage_threshold: int = 2  # Minimum times a pattern must appear to be included


@dataclass
class PatternAnalysis:
    """Analysis of patterns found in existing projects/tasks."""

    pattern_type: str  # "variable", "step", "tag", "structure"
    pattern_value: str
    frequency: int
    confidence: float
    examples: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TemplateGenerator:
    """Generates templates dynamically based on analysis and patterns."""

    def __init__(self, template_manager: TemplateManager):
        """Initialize template generator."""
        self.template_manager = template_manager
        self.common_variables = self._get_common_variables()
        self.best_practices = self._get_best_practices()

    def _get_common_variables(self) -> List[TemplateVariable]:
        """Get commonly used template variables."""
        return [
            TemplateVariable(
                name="project_name",
                type=VariableType.STRING,
                description="Name of the project",
                required=True,
                validation_pattern=r"^[a-zA-Z0-9\s\-_]+$",
            ),
            TemplateVariable(
                name="description",
                type=VariableType.STRING,
                description="Project or agent description",
                required=True,
            ),
            TemplateVariable(
                name="author",
                type=VariableType.STRING,
                description="Author or creator name",
                required=False,
            ),
            TemplateVariable(
                name="priority",
                type=VariableType.CHOICE,
                description="Priority level",
                choices=["low", "medium", "high", "critical"],
                default="medium",
                required=False,
            ),
            TemplateVariable(
                name="complexity",
                type=VariableType.CHOICE,
                description="Complexity level",
                choices=["low", "medium", "high"],
                default="medium",
                required=False,
            ),
            TemplateVariable(
                name="estimated_duration",
                type=VariableType.STRING,
                description="Estimated duration",
                default="2 weeks",
                required=False,
            ),
        ]

    def _get_best_practices(self) -> Dict[str, Any]:
        """Get best practices for different template types."""
        return {
            "project": {
                "min_objectives": 3,
                "recommended_tags": ["planning", "implementation", "review"],
                "required_phases": ["planning", "execution", "closure"],
            },
            "agent": {
                "required_tools": ["fs_read", "fs_write", "@lackey"],
                "recommended_resources": ["file://*"],
                "prompt_min_length": 200,
            },
            "workflow": {
                "min_tasks": 3,
                "max_tasks": 10,
                "dependency_depth": 3,
            },
        }

    def generate_project_template(
        self,
        name: str,
        friendly_name: str,
        description: str,
        analysis_data: Optional[List[Project]] = None,
        config: Optional[TemplateGenerationConfig] = None,
    ) -> Template:
        """Generate a project template based on analysis of existing projects."""
        config = config or TemplateGenerationConfig()

        # Analyze existing projects if provided
        patterns = []
        if analysis_data and config.analyze_existing_projects:
            patterns = self._analyze_projects(analysis_data)

        # Generate template variables
        variables = self._generate_project_variables(patterns, config)

        # Generate project content
        content = self._generate_project_content(patterns, config)

        # Generate files
        files = self._generate_project_files(patterns, config)

        # Create template
        template = Template.create_new(
            name=name,
            friendly_name=friendly_name,
            description=description,
            template_type=TemplateType.PROJECT,
            version="1.0.0",
            author="Lackey Template Generator",
            tags=self._extract_common_tags(patterns),
            variables=variables,
            content=content,
            files=files,
            metadata={
                "generated": True,
                "generation_date": datetime.now(UTC).isoformat(),
                "patterns_analyzed": len(patterns),
            },
        )

        return template

    def generate_agent_template(
        self,
        name: str,
        friendly_name: str,
        description: str,
        agent_type: str = "general",
        specialization: Optional[str] = None,
        config: Optional[TemplateGenerationConfig] = None,
    ) -> Template:
        """Generate an agent template for specific roles or specializations."""
        config = config or TemplateGenerationConfig()

        # Generate agent-specific variables
        variables = self._generate_agent_variables(agent_type, specialization, config)

        # Generate agent content (tasks and project structure)
        content = self._generate_agent_content(agent_type, specialization, config)

        # Generate agent files (JSON agent file, documentation)
        files = self._generate_agent_files(agent_type, specialization, config)

        # Create template
        template = Template.create_new(
            name=name,
            friendly_name=friendly_name,
            description=description,
            template_type=TemplateType.AGENT,
            version="1.0.0",
            author="Lackey Template Generator",
            tags=self._get_agent_tags(agent_type, specialization),
            variables=variables,
            content=content,
            files=files,
            metadata={
                "generated": True,
                "agent_type": agent_type,
                "specialization": specialization,
                "generation_date": datetime.now(UTC).isoformat(),
            },
        )

        return template

    def generate_workflow_template(
        self,
        name: str,
        friendly_name: str,
        description: str,
        workflow_type: str = "general",
        task_analysis: Optional[List[Task]] = None,
        config: Optional[TemplateGenerationConfig] = None,
    ) -> Template:
        """Generate a workflow template based on task patterns."""
        config = config or TemplateGenerationConfig()

        # Analyze tasks if provided
        patterns = []
        if task_analysis and config.analyze_existing_projects:
            patterns = self._analyze_tasks(task_analysis)

        # Generate workflow variables
        variables = self._generate_workflow_variables(workflow_type, patterns, config)

        # Generate workflow content
        content = self._generate_workflow_content(workflow_type, patterns, config)

        # Generate workflow files
        files = self._generate_workflow_files(workflow_type, patterns, config)

        # Create template
        template = Template.create_new(
            name=name,
            friendly_name=friendly_name,
            description=description,
            template_type=TemplateType.WORKFLOW,
            version="1.0.0",
            author="Lackey Template Generator",
            tags=self._get_workflow_tags(workflow_type),
            variables=variables,
            content=content,
            files=files,
            metadata={
                "generated": True,
                "workflow_type": workflow_type,
                "generation_date": datetime.now(UTC).isoformat(),
                "patterns_analyzed": len(patterns),
            },
        )

        return template

    def _analyze_projects(self, projects: List[Project]) -> List[PatternAnalysis]:
        """Analyze existing projects to extract patterns."""
        patterns = []

        # Analyze common tags
        tag_frequency: Dict[str, int] = {}
        for project in projects:
            for tag in project.tags:
                tag_frequency[tag] = tag_frequency.get(tag, 0) + 1

        for tag, freq in tag_frequency.items():
            if freq >= 2:  # Minimum threshold
                patterns.append(
                    PatternAnalysis(
                        pattern_type="tag",
                        pattern_value=tag,
                        frequency=freq,
                        confidence=min(freq / len(projects), 1.0),
                    )
                )

        # Analyze common objectives
        objective_patterns: Dict[str, int] = {}
        for project in projects:
            for objective in project.objectives:
                # Extract key phrases from objectives
                key_phrases = self._extract_key_phrases(objective)
                for phrase in key_phrases:
                    objective_patterns[phrase] = objective_patterns.get(phrase, 0) + 1

        for phrase, freq in objective_patterns.items():
            if freq >= 2:
                patterns.append(
                    PatternAnalysis(
                        pattern_type="objective",
                        pattern_value=phrase,
                        frequency=freq,
                        confidence=min(freq / len(projects), 1.0),
                    )
                )

        return patterns

    def _analyze_tasks(self, tasks: List[Task]) -> List[PatternAnalysis]:
        """Analyze existing tasks to extract patterns."""
        patterns = []

        # Analyze common steps
        step_patterns: Dict[str, int] = {}
        for task in tasks:
            for step in task.steps:
                key_phrases = self._extract_key_phrases(step)
                for phrase in key_phrases:
                    step_patterns[phrase] = step_patterns.get(phrase, 0) + 1

        for phrase, freq in step_patterns.items():
            if freq >= 2:
                patterns.append(
                    PatternAnalysis(
                        pattern_type="step",
                        pattern_value=phrase,
                        frequency=freq,
                        confidence=min(freq / len(tasks), 1.0),
                    )
                )

        # Analyze complexity distribution
        complexity_freq: Dict[str, int] = {}
        for task in tasks:
            complexity = task.complexity.value
            complexity_freq[complexity] = complexity_freq.get(complexity, 0) + 1

        most_common_complexity = max(complexity_freq.items(), key=lambda x: x[1])
        patterns.append(
            PatternAnalysis(
                pattern_type="complexity",
                pattern_value=most_common_complexity[0],
                frequency=most_common_complexity[1],
                confidence=most_common_complexity[1] / len(tasks),
            )
        )

        return patterns

    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text for pattern analysis."""
        # Simple key phrase extraction
        # Remove common words and extract meaningful phrases
        common_words = {
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
            "from",
            "up",
            "about",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "among",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
        }

        # Split into words and filter
        words = re.findall(r"\b\w+\b", text.lower())
        meaningful_words = [w for w in words if w not in common_words and len(w) > 2]

        # Extract 2-3 word phrases
        phrases = []
        for i in range(len(meaningful_words)):
            if i < len(meaningful_words) - 1:
                phrases.append(f"{meaningful_words[i]} {meaningful_words[i+1]}")
            if i < len(meaningful_words) - 2:
                phrases.append(
                    f"{meaningful_words[i]} {meaningful_words[i+1]} "
                    f"{meaningful_words[i+2]}"
                )

        return phrases[:5]  # Return top 5 phrases

    def _generate_project_variables(
        self,
        patterns: List[PatternAnalysis],
        config: TemplateGenerationConfig,
    ) -> List[TemplateVariable]:
        """Generate variables for project template."""
        variables = []

        if config.include_common_variables:
            variables.extend(self.common_variables)

        # Add pattern-based variables
        tag_patterns = [p for p in patterns if p.pattern_type == "tag"]
        if tag_patterns:
            common_tags = [p.pattern_value for p in tag_patterns if p.confidence > 0.3]
            if common_tags:
                variables.append(
                    TemplateVariable(
                        name="project_tags",
                        type=VariableType.LIST,
                        description="Project tags for categorization",
                        default=common_tags[:3],
                        required=False,
                    )
                )

        return variables

    def _generate_project_content(
        self,
        patterns: List[PatternAnalysis],
        config: TemplateGenerationConfig,
    ) -> Dict[str, Any]:
        """Generate content for project template."""
        # Extract common objectives from patterns
        objective_patterns = [p for p in patterns if p.pattern_type == "objective"]
        common_objectives = [
            f"Complete {p.pattern_value}"
            for p in objective_patterns
            if p.confidence > 0.4
        ]

        if not common_objectives:
            common_objectives = [
                "Define project scope and requirements",
                "Execute project deliverables",
                "Review and document results",
            ]

        content = {
            "project": {
                "friendly_name": "{{project_name}}",
                "description": "{{description}}",
                "objectives": common_objectives[:5],  # Limit to 5 objectives
                "tags": (
                    "{{project_tags}}"
                    if any(p.pattern_type == "tag" for p in patterns)
                    else ["generated"]
                ),
                "metadata": {
                    "author": "{{author}}",
                    "priority": "{{priority}}",
                    "estimated_duration": "{{estimated_duration}}",
                    "template_generated": True,
                },
            }
        }

        return content

    def _generate_project_files(
        self,
        patterns: List[PatternAnalysis],
        config: TemplateGenerationConfig,
    ) -> Dict[str, str]:
        """Generate files for project template."""
        files = {}

        if config.generate_documentation:
            files[
                "README.md"
            ] = """# {{project_name}}

{{description}}

## Project Details

- **Author**: {{author}}
- **Priority**: {{priority}}
- **Estimated Duration**: {{estimated_duration}}

## Objectives

{% for objective in objectives %}
- {{ objective }}
{% endfor %}

## Getting Started

This project was generated using Lackey's dynamic template system.

## Status

Project is in planning phase.
"""

            files[
                "PLANNING.md"
            ] = """# {{project_name}} - Planning Document

## Project Overview

{{description}}

## Timeline

Estimated Duration: {{estimated_duration}}

## Team

- Author: {{author}}

## Next Steps

1. Define detailed project scope
2. Create timeline with milestones
3. Begin implementation
"""

        return files

    def _generate_agent_variables(
        self,
        agent_type: str,
        specialization: Optional[str],
        config: TemplateGenerationConfig,
    ) -> List[TemplateVariable]:
        """Generate variables for agent template."""
        variables = [
            TemplateVariable(
                name="agent_name",
                type=VariableType.STRING,
                description="Name of the agent",
                required=True,
                validation_pattern=r"^[a-zA-Z0-9\s\-_]+$",
            ),
            TemplateVariable(
                name="agent_description",
                type=VariableType.STRING,
                description="Description of the agent's role and capabilities",
                required=True,
            ),
        ]

        # Add type-specific variables
        if agent_type == "developer":
            variables.extend(
                [
                    TemplateVariable(
                        name="programming_languages",
                        type=VariableType.LIST,
                        description="Primary programming languages",
                        default=["Python", "JavaScript"],
                        required=False,
                    ),
                    TemplateVariable(
                        name="specialization",
                        type=VariableType.CHOICE,
                        description="Development specialization",
                        choices=[
                            "backend",
                            "frontend",
                            "fullstack",
                            "devops",
                            "mobile",
                            "data",
                            "ai",
                        ],
                        default="fullstack",
                        required=False,
                    ),
                ]
            )
        elif agent_type == "manager":
            variables.extend(
                [
                    TemplateVariable(
                        name="management_style",
                        type=VariableType.CHOICE,
                        description="Management methodology",
                        choices=["agile", "waterfall", "hybrid", "lean", "kanban"],
                        default="agile",
                        required=False,
                    ),
                    TemplateVariable(
                        name="team_size",
                        type=VariableType.INTEGER,
                        description="Expected team size",
                        default=5,
                        min_value=1,
                        max_value=50,
                        required=False,
                    ),
                ]
            )

        return variables

    def _generate_agent_content(
        self,
        agent_type: str,
        specialization: Optional[str],
        config: TemplateGenerationConfig,
    ) -> Dict[str, Any]:
        """Generate content for agent template."""
        return {
            "project": {
                "friendly_name": "{{agent_name}} Project",
                "description": "{{agent_description}}",
                "objectives": [
                    "Set up agent environment and tools",
                    "Execute agent-specific tasks",
                    "Maintain quality and documentation",
                ],
                "tags": [agent_type, "agent", "generated"],
                "metadata": {
                    "agent_type": agent_type,
                    "specialization": specialization,
                },
            }
        }

    def _generate_agent_files(
        self,
        agent_type: str,
        specialization: Optional[str],
        config: TemplateGenerationConfig,
    ) -> Dict[str, str]:
        """Generate files for agent template."""
        files = {}

        # Generate Amazon Q agent JSON file
        agent_json = {
            "name": "{{agent_name}}",
            "description": "{{agent_description}}",
            "prompt": (
                f"You are {{{{agent_name}}}}, a {agent_type} agent. "
                "{{agent_description}}"
            ),
            "mcpServers": {
                "lackey": {
                    "command": "lackey",
                    "args": ["serve", "--workspace", ".lackey"],
                    "disabled": False,
                    "autoApprove": [],
                }
            },
            "tools": [
                "fs_read",
                "fs_write",
                "execute_bash",
                "knowledge",
                "thinking",
                "@lackey",
            ],
            "toolAliases": {},
            "allowedTools": ["fs_read", "fs_write", "execute_bash", "@lackey"],
            "resources": [
                "file://.amazonq/rules/general-rules.md",
                f"file://.amazonq/rules/{agent_type}-rules.md",
            ],
            "hooks": {},
            "toolsSettings": {},
            "useLegacyMcpJson": True,
        }

        files["{{agent_name}}.json"] = yaml.dump(agent_json, default_flow_style=False)

        if config.generate_documentation:
            files[
                "agent-profile.md"
            ] = f"""# {{{{agent_name}}}} - {agent_type.title()} Agent Profile

## Agent Details

- **Name**: {{{{agent_name}}}}
- **Type**: {agent_type}
- **Specialization**: {specialization or 'General'}

## Description

{{{{agent_description}}}}

## Capabilities

This agent is specialized in {agent_type} tasks with focus on quality and efficiency.

## Usage

This agent was generated using Lackey's dynamic template system.
"""

        return files

    def _generate_workflow_variables(
        self,
        workflow_type: str,
        patterns: List[PatternAnalysis],
        config: TemplateGenerationConfig,
    ) -> List[TemplateVariable]:
        """Generate variables for workflow template."""
        variables = [
            TemplateVariable(
                name="workflow_name",
                type=VariableType.STRING,
                description="Name of the workflow",
                required=True,
            ),
            TemplateVariable(
                name="workflow_description",
                type=VariableType.STRING,
                description="Description of the workflow",
                required=True,
            ),
        ]

        # Add workflow-specific variables based on type
        if workflow_type == "development":
            variables.append(
                TemplateVariable(
                    name="technology_stack",
                    type=VariableType.STRING,
                    description="Technology stack for development",
                    default="Python/React",
                    required=False,
                )
            )

        return variables

    def _generate_workflow_content(
        self,
        workflow_type: str,
        patterns: List[PatternAnalysis],
        config: TemplateGenerationConfig,
    ) -> Dict[str, Any]:
        """Generate content for workflow template."""
        # Generate tasks based on workflow type and patterns
        tasks = self._generate_workflow_tasks(workflow_type, patterns)

        return {
            "project": {
                "friendly_name": "{{workflow_name}}",
                "description": "{{workflow_description}}",
                "objectives": [
                    "Complete workflow setup",
                    "Execute workflow steps",
                    "Review and optimize process",
                ],
                "tags": [workflow_type, "workflow", "generated"],
            },
            "tasks": tasks,
        }

    def _generate_workflow_tasks(
        self,
        workflow_type: str,
        patterns: List[PatternAnalysis],
    ) -> List[Dict[str, Any]]:
        """Generate tasks for workflow based on type and patterns."""
        if workflow_type == "development":
            return [
                {
                    "title": "Setup Development Environment",
                    "objective": "Prepare development environment and tools",
                    "steps": [
                        "Set up version control",
                        "Install dependencies",
                        "Configure development tools",
                    ],
                    "success_criteria": [
                        "Environment is functional",
                        "All tools configured",
                    ],
                    "complexity": "medium",
                    "tags": ["setup", "environment"],
                },
                {
                    "title": "Implement Core Features",
                    "objective": "Develop main application features",
                    "steps": [
                        "Design architecture",
                        "Implement core logic",
                        "Add user interface",
                    ],
                    "success_criteria": [
                        "Core features working",
                        "Architecture documented",
                    ],
                    "complexity": "high",
                    "dependencies": ["setup-development-environment"],
                    "tags": ["implementation", "core"],
                },
            ]
        else:
            # Generic workflow tasks
            return [
                {
                    "title": "Planning and Setup",
                    "objective": "Plan and set up the workflow",
                    "steps": [
                        "Define workflow requirements",
                        "Set up necessary tools",
                        "Create timeline",
                    ],
                    "success_criteria": [
                        "Requirements defined",
                        "Tools ready",
                        "Timeline created",
                    ],
                    "complexity": "medium",
                    "tags": ["planning", "setup"],
                },
                {
                    "title": "Execute Workflow",
                    "objective": "Execute the main workflow steps",
                    "steps": [
                        "Follow defined process",
                        "Monitor progress",
                        "Address issues",
                    ],
                    "success_criteria": [
                        "Process completed",
                        "Quality maintained",
                    ],
                    "complexity": "high",
                    "dependencies": ["planning-and-setup"],
                    "tags": ["execution", "main"],
                },
            ]

    def _generate_workflow_files(
        self,
        workflow_type: str,
        patterns: List[PatternAnalysis],
        config: TemplateGenerationConfig,
    ) -> Dict[str, str]:
        """Generate files for workflow template."""
        files = {}

        if config.generate_documentation:
            files[
                "workflow-guide.md"
            ] = f"""# {{{{workflow_name}}}} - {workflow_type.title()} Workflow

## Overview

{{{{workflow_description}}}}

## Workflow Type

{workflow_type.title()} workflow generated by Lackey template system.

## Steps

This workflow includes automated task generation based on best practices.

## Usage

Follow the generated tasks in sequence for optimal results.
"""

        return files

    def _extract_common_tags(self, patterns: List[PatternAnalysis]) -> List[str]:
        """Extract common tags from patterns."""
        tag_patterns = [
            p for p in patterns if p.pattern_type == "tag" and p.confidence > 0.3
        ]
        return [p.pattern_value for p in tag_patterns[:5]]  # Top 5 tags

    def _get_agent_tags(
        self, agent_type: str, specialization: Optional[str]
    ) -> List[str]:
        """Get tags for agent template."""
        tags = ["agent", agent_type, "generated"]
        if specialization:
            tags.append(specialization)
        return tags

    def _get_workflow_tags(self, workflow_type: str) -> List[str]:
        """Get tags for workflow template."""
        return ["workflow", workflow_type, "generated"]
