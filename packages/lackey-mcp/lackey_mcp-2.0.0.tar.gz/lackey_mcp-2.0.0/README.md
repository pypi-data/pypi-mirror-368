# Lackey

**Task chain management engine for AI agents with MCP integration**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

## Overview

Lackey is a sophisticated task chain management engine designed specifically for AI agents. It provides intelligent dependency management, DAG validation, and comprehensive workflow automation while storing all data directly in your project repository. This design enables AI agents to work within consistent, structured workflows while maintaining full human visibility and control.

### Key Features

🤖 **AI-First Design**: Built specifically for AI agent workflows with MCP integration
📁 **Repository-Based Storage**: All task data lives in your project repository
🔗 **Intelligent Dependencies**: Advanced DAG validation prevents circular dependencies
📝 **Rich Notes System**: Comprehensive note-taking with search and categorization
🔄 **Workflow Automation**: Bulk operations and status management
🎯 **Zero Global State**: Each project is completely self-contained
🔧 **Extensible Architecture**: Template system for domain-specific customization

## Quick Start

### Installation

```bash
pip install lackey-mcp
```

### Initialize Your First Project

```bash
# Initialize a new project
lackey init --domain web-development --name "My Web Project"

# Start the MCP server
lackey serve
```

### Connect with AI Agents

```bash
# Using Amazon Q
q chat --agent manager "Let's plan the first sprint for our web project"

# Or connect any MCP-compatible AI agent to localhost:3000
```

### Basic Usage

```python
from lackey import LackeyCore

# Initialize Lackey in your project
lackey = LackeyCore()

# Create a project
project = lackey.create_project(
    friendly_name="My Project",
    description="A sample project",
    objectives=["Build MVP", "Deploy to production"]
)

# Create tasks with dependencies
task1 = lackey.create_task(
    project_id=project.id,
    title="Setup Development Environment",
    objective="Configure development tools and dependencies",
    steps=["Install Python", "Setup virtual environment", "Install dependencies"],
    success_criteria=["All tests pass", "Development server runs"]
)

task2 = lackey.create_task(
    project_id=project.id,
    title="Implement Core Features",
    objective="Build the main application features",
    steps=["Design API", "Implement endpoints", "Add tests"],
    success_criteria=["API documented", "Tests pass", "Code reviewed"],
    dependencies=[task1.id]  # This task depends on task1
)
```

## MCP Integration

Lackey provides 25 comprehensive MCP tools for AI agents:

### Project Management
- `create_project` - Create new projects with objectives and metadata
- `list_projects` - List and filter projects by status or tags
- `get_project` - Get detailed project information
- `update_project` - Update project details and status

### Task Management
- `create_task` - Create tasks with dependencies and success criteria
- `get_task` - Get detailed task information
- `list_tasks` - List and filter tasks by various criteria
- `update_task_status` - Update task status with notes
- `complete_task_steps` - Mark specific task steps as complete
- `get_task_progress` - Get detailed progress information

### Assignment & Collaboration
- `assign_task` - Assign tasks to team members
- `reassign_task` - Reassign tasks with notes
- `bulk_assign_tasks` - Assign multiple tasks at once
- `bulk_update_task_status` - Update status for multiple tasks

### Dependency Management
- `add_task_dependencies` - Add dependencies with cycle validation
- `remove_task_dependencies` - Remove task dependencies
- `validate_dependencies` - Check for dependency cycles
- `validate_task_dependencies_integrity` - Comprehensive dependency validation
- `get_ready_tasks` - Get tasks ready to work on
- `get_blocked_tasks` - Get tasks blocked by dependencies

### Notes & Documentation
- `add_task_note` - Add rich notes with markdown support
- `get_task_notes` - Retrieve task notes with filtering
- `search_task_notes` - Search notes by content and metadata

### Advanced Operations
- `clone_task` - Clone tasks with optional modifications
- `archive_task` - Archive completed or obsolete tasks

## Architecture

Lackey uses a file-based storage system that keeps all data in your repository:

```
your-project/
├── .lackey/
│   ├── projects/           # Project definitions
│   ├── tasks/             # Task data and metadata
│   ├── notes/             # Rich notes and documentation
│   └── config.yaml        # Workspace configuration
├── your-code/             # Your actual project files
└── README.md
```

### Core Components

- **LackeyCore**: Main engine for task and project management
- **MCP Server**: FastMCP-based server providing 25 tools for AI agents
- **DAG Validator**: NetworkX-based dependency validation
- **Notes System**: Rich note-taking with search and categorization
- **File Operations**: Atomic operations with rollback capabilities

## Use Cases

### Software Development
```bash
lackey init --domain software-development --name "API Service"
# Creates tasks for: planning, development, testing, deployment
```

### Data Science Projects
```bash
lackey init --domain data-science --name "ML Pipeline"
# Creates tasks for: data collection, analysis, modeling, validation
```

### Content Creation
```bash
lackey init --domain content-creation --name "Blog Series"
# Creates tasks for: research, writing, editing, publishing
```

## Advanced Features

### Rich Notes System
Add comprehensive notes to any task with markdown support:

```python
lackey.add_task_note(
    project_id=project.id,
    task_id=task.id,
    content="## Progress Update\n\nCompleted API design. Next: implementation.",
    note_type="progress",
    tags="api,design,milestone"
)
```

### Bulk Operations
Efficiently manage multiple tasks:

```python
# Update multiple task statuses
lackey.bulk_update_task_status(
    project_id=project.id,
    task_ids=[task1.id, task2.id, task3.id],
    status="in-progress",
    note="Starting sprint 2"
)
```

### Dependency Validation
Automatic cycle detection and validation:

```python
# Lackey automatically prevents circular dependencies
lackey.add_task_dependencies(
    project_id=project.id,
    task_id=task1.id,
    dependency_ids=[task2.id]  # Will fail if this creates a cycle
)
```

## Configuration

### MCP Server Configuration

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "lackey": {
      "command": "lackey",
      "args": ["serve"],
      "env": {}
    }
  }
}
```

### Agent Templates

Lackey includes templates for different agent roles:

- **Manager**: Project planning and coordination
- **Developer**: Code implementation and technical tasks
- **Architect**: System design and technical decisions
- **Writer**: Documentation and content creation

## Documentation

- **[User Guide](docs/basic-usage-guide.md)** - Comprehensive usage examples
- **[Design Specification](docs/design-spec.md)** - System architecture and design
- **[Development Guide](docs/development-spec.md)** - API reference and implementation details
- **[Notes System](docs/notes_system.md)** - Rich note-taking features

## Requirements

- **Python**: 3.10 or higher
- **Dependencies**: PyYAML, NetworkX, Click, MCP SDK
- **Storage**: File-based (no database required)
- **Platform**: Cross-platform (Windows, macOS, Linux)

## Installation Options

### Standard Installation
```bash
pip install lackey-mcp
```

### Development Installation
```bash
git clone https://github.com/lackey-ai/lackey
cd lackey
pip install -e ".[dev,security]"
```

### With Documentation Tools
```bash
pip install lackey-mcp[docs]
```

## CLI Commands

```bash
# Initialize new project
lackey init [--domain DOMAIN] [--name NAME]

# Start MCP server
lackey serve [--port PORT] [--host HOST]

# Check system health
lackey doctor

# Show version information
lackey version
```

## Contributing

We welcome contributions! Please see our [Development Guide](DEVELOPMENT.md) for setup instructions and coding standards.

### Development Setup

```bash
# Clone and setup
git clone https://github.com/lackey-ai/lackey
cd lackey
pip install -e ".[dev,security]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest --cov=lackey

# Format code
black src tests
```

### Testing

Lackey maintains high test coverage with comprehensive test suites:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lackey --cov-report=html

# Run specific test categories
pytest tests/test_core/
pytest tests/test_mcp/
```

## License

This project is licensed under a Proprietary License. See [LICENSE](LICENSE) for details.

---

**Built for AI agents, designed for humans.** 🤖✨
