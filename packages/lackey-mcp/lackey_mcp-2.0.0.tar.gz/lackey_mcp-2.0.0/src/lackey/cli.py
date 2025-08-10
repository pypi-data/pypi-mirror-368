#!/usr/bin/env python3
"""Main CLI entry point for Lackey task chain management engine."""

import asyncio
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict

import click

from . import __version__

if TYPE_CHECKING:
    from .templates import Template, TemplateManager


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and exit")
@click.pass_context
def main(ctx: click.Context, version: bool) -> None:
    """Lackey - Task chain management engine for AI agents.

    Lackey provides intelligent task dependency management with MCP server
    integration for AI agent collaboration.
    """
    if version:
        click.echo(f"Lackey {__version__}")
        sys.exit(0)

    # If no command provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command("serve")
@click.option(
    "--workspace",
    "-w",
    default=".lackey",
    help="Workspace directory for Lackey data (default: .lackey)",
)
@click.option(
    "--log-level",
    "-l",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    help="Logging level (default: INFO)",
)
def serve(workspace: str, log_level: str) -> None:
    """Start the Lackey MCP server.

    This starts the MCP (Model Context Protocol) server that enables
    AI agents to interact with Lackey for task management.
    """
    # Create workspace directory if it doesn't exist
    workspace_path = Path(workspace)
    workspace_path.mkdir(parents=True, exist_ok=True)

    click.echo("Starting Lackey MCP server...")
    click.echo(f"Workspace: {workspace_path.resolve()}")
    click.echo(f"Log level: {log_level}")
    click.echo("Server running in stdio mode for MCP compatibility")
    click.echo("Press Ctrl+C to stop")

    # Use the Gateway-based MCP server implementation
    import logging

    from .mcp.server import LackeyMCPServer

    # Set up logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )

    async def run_server() -> None:
        server = LackeyMCPServer(str(workspace_path))
        try:
            await server.run()
        except KeyboardInterrupt:
            logging.info("Received interrupt signal, shutting down...")
            await server.stop()
        except Exception as e:
            logging.error(f"Server error: {e}")
            sys.exit(1)

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        click.echo("\nServer stopped.")


@main.command("version")
def version() -> None:
    """Show version information."""
    click.echo(f"Lackey {__version__}")


@main.command("doctor")
@click.option("--workspace", "-w", default=".lackey", help="Workspace directory")
def doctor(workspace: str) -> None:
    """Check system requirements and configuration."""
    import platform
    import sys
    from pathlib import Path

    click.echo("🔍 Lackey System Check")
    click.echo("=" * 50)

    # Python version check
    python_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    if sys.version_info >= (3, 10):
        click.echo(f"✅ Python version: {python_version} (compatible)")
    else:
        click.echo(f"❌ Python version: {python_version} (requires 3.10+)")

    # Platform info
    click.echo(f"✅ Platform: {platform.system()} {platform.release()}")

    # Workspace check
    workspace_path = Path(workspace)
    if workspace_path.exists():
        click.echo(f"✅ Workspace exists: {workspace_path.resolve()}")

        # Check workspace structure
        config_file = workspace_path / "config.yaml"
        index_file = workspace_path / "index.yaml"

        if config_file.exists():
            click.echo("✅ Configuration file found")
        else:
            click.echo("⚠️  Configuration file missing (will be created on first use)")

        if index_file.exists():
            click.echo("✅ Project index found")
        else:
            click.echo("⚠️  Project index missing (will be created on first use)")
    else:
        click.echo(f"⚠️  Workspace directory missing: {workspace_path.resolve()}")
        click.echo("   (will be created when running 'lackey serve')")

    # Dependencies check
    try:
        import yaml

        click.echo("✅ PyYAML available")
        del yaml  # Clean up namespace
    except ImportError:
        click.echo("❌ PyYAML missing")

    try:
        import networkx

        click.echo("✅ NetworkX available")
        del networkx  # Clean up namespace
    except ImportError:
        click.echo("❌ NetworkX missing")

    try:
        import mcp

        click.echo("✅ MCP library available")
        del mcp  # Clean up namespace
    except ImportError:
        click.echo("❌ MCP library missing")

    click.echo("\n💡 To start using Lackey:")
    click.echo("   1. Run 'lackey serve' to start the MCP server")
    click.echo(
        "   2. In another terminal, use Q CLI: "
        "'q chat --mcp-server \"lackey serve --workspace .lackey\"'"
    )


@main.command("init")
@click.option("--name", help="Project name")
@click.option("--description", help="Project description")
@click.option("--template", "-t", help="Template to use for initialization")
@click.option("--list-templates", is_flag=True, help="List available templates")
@click.option("--agent-name", help="Name for agent (when using agent templates)")
@click.option("--workspace", "-w", default=".lackey", help="Workspace directory")
@click.option(
    "--interactive", "-i", is_flag=True, help="Interactive template selection"
)
def init(
    name: str,
    description: str,
    template: str,
    list_templates: bool,
    agent_name: str,
    workspace: str,
    interactive: bool,
) -> None:
    """Initialize a new Lackey workspace with optional template support."""
    from .template_registry import TemplateDistributor, create_builtin_templates
    from .templates import TemplateManager, TemplateType

    workspace_path = Path(workspace)
    workspace_path.mkdir(parents=True, exist_ok=True)

    # Initialize template system
    templates_dir = workspace_path / "templates"
    template_manager = TemplateManager(templates_dir)
    # Initialize template distributor for potential future use
    TemplateDistributor(workspace_path)

    # Load built-in templates
    create_builtin_templates(template_manager)

    # Handle template listing
    if list_templates:
        click.echo("📋 Available Templates:")
        click.echo("=" * 50)

        templates = template_manager.list_templates()
        if not templates:
            click.echo("No templates available.")
            return

        for tmpl in templates:
            icon = {
                "project": "📁",
                "agent": "🤖",
                "workflow": "⚡",
                "task_chain": "🔗",
            }.get(tmpl.template_type.value, "📄")
            click.echo(f"{icon} {tmpl.name}")
            click.echo(f"   {tmpl.friendly_name}")
            click.echo(f"   {tmpl.description}")
            click.echo(f"   Type: {tmpl.template_type.value} | Version: {tmpl.version}")
            if tmpl.tags:
                click.echo(f"   Tags: {', '.join(tmpl.tags)}")
            click.echo()
        return

    # Interactive template selection
    if interactive and not template:
        templates = template_manager.list_templates()
        if templates:
            click.echo("🎯 Select a template:")
            for i, tmpl in enumerate(templates, 1):
                icon = {
                    "project": "📁",
                    "agent": "🤖",
                    "workflow": "⚡",
                    "task_chain": "🔗",
                }.get(tmpl.template_type.value, "📄")
                click.echo(
                    f"{i}. {icon} {tmpl.friendly_name} ({tmpl.template_type.value})"
                )

            choice = click.prompt(
                "Enter template number (or 0 for basic setup)", type=int, default="0"
            )
            if 1 <= choice <= len(templates):
                template = templates[choice - 1].name

    click.echo(f"🚀 Initializing Lackey workspace at {workspace_path.resolve()}")

    # Use template if specified
    if template:
        try:
            template_obj = template_manager.get_template_by_name(template)
            if not template_obj:
                click.echo(f"❌ Template '{template}' not found")
                click.echo("Use --list-templates to see available templates")
                return

            click.echo(f"📋 Using template: {template_obj.friendly_name}")

            # Collect template variables
            values = {}

            # Get values from command line options
            if name:
                values["project_name"] = name
                values["agent_name"] = name  # For agent templates
            if description:
                values["description"] = description
                values["project_description"] = description
                values["agent_description"] = description
            if agent_name:
                values["agent_name"] = agent_name

            # Prompt for missing required variables
            for var in template_obj.variables:
                if var.name not in values:
                    if var.required:
                        prompt_text = f"{var.description}"
                        if var.default:
                            prompt_text += f" (default: {var.default})"

                        if var.type.value == "choice" and var.choices:
                            click.echo(
                                f"Choices for {var.name}: {', '.join(var.choices)}"
                            )

                        value = click.prompt(prompt_text, default=var.default, type=str)
                        values[var.name] = value
                    elif var.default is not None:
                        values[var.name] = var.default

            # Initialize based on template type
            if template_obj.template_type == TemplateType.PROJECT:
                _init_with_project_template(
                    template_obj, values, workspace_path, template_manager
                )
            elif template_obj.template_type == TemplateType.AGENT:
                _init_with_agent_template(
                    template_obj, values, workspace_path, template_manager
                )
            elif template_obj.template_type in (
                TemplateType.WORKFLOW,
                TemplateType.TASK_CHAIN,
            ):
                _init_with_workflow_template(
                    template_obj, values, workspace_path, template_manager
                )

            click.echo(
                f"✅ Initialized workspace using {template_obj.friendly_name} template"
            )

        except Exception as e:
            click.echo(f"❌ Error using template: {e}")
            click.echo("Falling back to basic initialization...")
            _init_basic_workspace(name, description, workspace_path)
    else:
        # Basic initialization without template
        _init_basic_workspace(name, description, workspace_path)

    click.echo("\n🎉 Workspace initialized successfully!")
    click.echo("\nNext steps:")
    click.echo("1. Run 'lackey serve' to start the MCP server")
    click.echo("2. Use Q CLI to interact with Lackey:")
    click.echo(f'   q chat --mcp-server "lackey serve --workspace {workspace}"')
    if template:
        click.echo("3. Check the generated files and customize as needed")


def _init_basic_workspace(name: str, description: str, workspace_path: Path) -> None:
    """Initialize a basic workspace without templates."""
    # Create basic config
    config_content = f"""# Lackey Configuration
version: "0.1.0"
workspace_name: "{name or 'Lackey Workspace'}"
description: "{description or 'A Lackey task management workspace'}"
created_at: "{workspace_path.resolve()}"

# Task management settings
task_settings:
  auto_assign_ids: true
  require_success_criteria: true
  default_complexity: "medium"

# Agent settings
agent_settings:
  create_agents: true
  default_roles: ["manager", "developer"]

# Validation settings
validation:
  level: "basic"
  strict_mode: false
"""

    config_file = workspace_path / "config.yaml"
    with open(config_file, "w") as f:
        f.write(config_content)

    # Create basic index
    index_content = """# Project Index
projects: []
"""

    index_file = workspace_path / "index.yaml"
    with open(index_file, "w") as f:
        f.write(index_content)

    # Create Amazon Q rules directory and files
    rules_dir = workspace_path.parent / ".amazonq" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    # Copy rule files from builtin templates
    builtin_rules_dir = Path(__file__).parent / "builtin_templates" / "rules"
    if builtin_rules_dir.exists():
        for rule_file in builtin_rules_dir.glob("*.md"):
            target_file = rules_dir / rule_file.name
            with open(rule_file, "r", encoding="utf-8") as src:
                content = src.read()
            with open(target_file, "w", encoding="utf-8") as dst:
                dst.write(content)

    click.echo("✅ Created workspace configuration")
    click.echo("✅ Created project index")
    click.echo("✅ Created Amazon Q agent rules")


def _init_with_project_template(
    template: "Template",
    values: Dict[str, Any],
    workspace_path: Path,
    template_manager: "TemplateManager",
) -> None:
    """Initialize workspace with a project template."""
    from .core import LackeyCore

    # Initialize basic workspace first
    _init_basic_workspace(
        values.get("project_name", "Project"),
        values.get("description", ""),
        workspace_path,
    )

    # Create Lackey core instance
    core = LackeyCore(str(workspace_path))

    # Create project from template
    project = template_manager.instantiate_project(template.id, values)
    core.create_project(
        friendly_name=project.friendly_name,
        description=project.description,
        objectives=project.objectives,
        tags=project.tags,
    )

    # Create template files
    files = template_manager.create_files_from_template(
        template.id, values, workspace_path
    )

    click.echo(f"✅ Created project: {project.friendly_name}")
    click.echo(f"✅ Generated {len(files)} template files")


def _init_with_agent_template(
    template: "Template",
    values: Dict[str, Any],
    workspace_path: Path,
    template_manager: "TemplateManager",
) -> None:
    """Initialize workspace with an agent template."""
    # Initialize basic workspace first
    _init_basic_workspace(
        values.get("agent_name", "Agent"), values.get("description", ""), workspace_path
    )

    # Create .amazonq directory for agent files
    amazonq_dir = workspace_path.parent / ".amazonq" / "cli-agents"
    amazonq_dir.mkdir(parents=True, exist_ok=True)

    # Create agent file
    agent_file = template_manager.instantiate_agent(template.id, values, amazonq_dir)

    # Create other template files in workspace
    files = template_manager.create_files_from_template(
        template.id, values, workspace_path
    )

    click.echo(f"✅ Created agent: {agent_file.name}")
    click.echo(f"✅ Generated {len(files)} template files")
    click.echo(f"✅ Agent file created at: {agent_file}")


def _init_with_workflow_template(
    template: "Template",
    values: Dict[str, Any],
    workspace_path: Path,
    template_manager: "TemplateManager",
) -> None:
    """Initialize workspace with a workflow template."""
    from .core import LackeyCore

    # Initialize basic workspace first
    _init_basic_workspace(
        values.get("workflow_name", "Workflow"),
        values.get("description", ""),
        workspace_path,
    )

    # Create Lackey core instance
    core = LackeyCore(str(workspace_path))

    # Create project from template
    project = template_manager.instantiate_project(template.id, values)
    project_id = core.create_project(
        friendly_name=project.friendly_name,
        description=project.description,
        objectives=project.objectives,
        tags=project.tags,
    )

    # Create tasks from template
    tasks = template_manager.instantiate_tasks(template.id, values)
    for task in tasks:
        core.create_task(
            project_id=project_id.id,
            title=task.title,
            objective=task.objective,
            steps=task.steps,
            success_criteria=task.success_criteria,
            complexity=task.complexity.value,
            context=task.context,
            assigned_to=task.assigned_to,
            tags=task.tags,
            dependencies=list(task.dependencies),
        )

    # Create template files
    files = template_manager.create_files_from_template(
        template.id, values, workspace_path
    )

    click.echo(f"✅ Created project: {project.friendly_name}")
    click.echo(f"✅ Created {len(tasks)} tasks from workflow")
    click.echo(f"✅ Generated {len(files)} template files")


# Add template management commands
@main.group("template")
def template_group() -> None:
    """Template management commands."""
    pass


@template_group.command("list")
@click.option("--type", "-t", help="Filter by template type")
@click.option("--tag", help="Filter by tag")
@click.option("--workspace", "-w", default=".lackey", help="Workspace directory")
def list_templates(type: str, tag: str, workspace: str) -> None:
    """List available templates."""
    from .template_registry import create_builtin_templates
    from .templates import TemplateManager, TemplateType

    workspace_path = Path(workspace)
    templates_dir = workspace_path / "templates"
    template_manager = TemplateManager(templates_dir)

    # Load built-in templates
    create_builtin_templates(template_manager)

    # Apply filters
    template_type = None
    if type:
        try:
            template_type = TemplateType(type.lower())
        except ValueError:
            click.echo(f"❌ Invalid template type: {type}")
            return

    templates = template_manager.list_templates(template_type=template_type, tag=tag)

    if not templates:
        click.echo("No templates found matching criteria.")
        return

    click.echo(f"Found {len(templates)} template(s):")
    click.echo("=" * 50)

    for tmpl in templates:
        icon = {
            "project": "📁",
            "agent": "🤖",
            "workflow": "⚡",
            "task_chain": "🔗",
        }.get(tmpl.template_type.value, "📄")
        click.echo(f"{icon} {tmpl.name}")
        click.echo(f"   {tmpl.friendly_name}")
        click.echo(f"   {tmpl.description}")
        click.echo(f"   Type: {tmpl.template_type.value} | Version: {tmpl.version}")
        if tmpl.author:
            click.echo(f"   Author: {tmpl.author}")
        if tmpl.tags:
            click.echo(f"   Tags: {', '.join(tmpl.tags)}")
        click.echo()


@template_group.command("info")
@click.argument("template_name")
@click.option("--workspace", "-w", default=".lackey", help="Workspace directory")
def template_info(template_name: str, workspace: str) -> None:
    """Show detailed information about a template."""
    from .template_registry import create_builtin_templates
    from .templates import TemplateManager

    workspace_path = Path(workspace)
    templates_dir = workspace_path / "templates"
    template_manager = TemplateManager(templates_dir)

    # Load built-in templates
    create_builtin_templates(template_manager)

    template = template_manager.get_template_by_name(template_name)
    if not template:
        click.echo(f"❌ Template '{template_name}' not found")
        return

    icon = {"project": "📁", "agent": "🤖", "workflow": "⚡", "task_chain": "🔗"}.get(
        template.template_type.value, "📄"
    )

    click.echo(f"{icon} {template.friendly_name}")
    click.echo("=" * 50)
    click.echo(f"Name: {template.name}")
    click.echo(f"Description: {template.description}")
    click.echo(f"Type: {template.template_type.value}")
    click.echo(f"Version: {template.version}")
    if template.author:
        click.echo(f"Author: {template.author}")
    if template.tags:
        click.echo(f"Tags: {', '.join(template.tags)}")

    if template.variables:
        click.echo(f"\nVariables ({len(template.variables)}):")
        for var in template.variables:
            required = "required" if var.required else "optional"
            default = f" (default: {var.default})" if var.default else ""
            click.echo(f"  • {var.name} ({var.type.value}, {required}){default}")
            click.echo(f"    {var.description}")

    if template.files:
        click.echo(f"\nFiles ({len(template.files)}):")
        for filename in template.files.keys():
            click.echo(f"  • {filename}")


if __name__ == "__main__":
    main()
