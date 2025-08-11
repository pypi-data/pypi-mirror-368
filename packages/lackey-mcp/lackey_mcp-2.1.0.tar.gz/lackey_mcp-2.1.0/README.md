# Lackey

## AI agents that actually get things done. Task chain management with intelligent dependency handling

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

## 🎯 What is Lackey

Lackey turns AI agents from chatbots into __project managers__.
Instead of endless back-and-forth, your AI agent breaks down complex goals into manageable task chains,
tracks dependencies, and keeps everything organized—all stored directly in your repository.

### 30-second demo

```bash

# Install and initialize

python3 -m venv .venv && source .venv/bin/activate
pip install lackey-mcp && lackey init

# Launch Q chat with developer agent

q chat --agent developer

# Then in Q chat, tell the agent

# > "Build a REST API for user management with authentication"

# Watch it create a complete task chain

# ✅ Setup development environment

# ✅ Design database schema

# ⏳ Implement user model (depends on schema)

# ⏳ Add authentication (depends on user model)

# ⏳ Create API endpoints (depends on auth)

# ⏳ Write tests (depends on endpoints)

```text

## 🚀 Quick Start

### 1. Install Lackey

```bash

# Create virtual environment

python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Lackey

pip install lackey-mcp

```

### 2. Initialize Your Project

```bash

# Initialize project (creates Q chat agent configurations)

lackey init

# This creates

# - .lackey/ directory with project data

# - .amazonq/ directory with Q chat agent configurations

```text

### 3. Start Working with AI Agents

```bash

# Launch Q chat with a specific agent role

q chat --agent manager

# Then interact within Q chat

# > "Let's plan our first project"

# > "Create a web development project for user management"

# Or use other agent roles

q chat --agent developer

# > "Get all ready tasks and start implementing authentication"

q chat --agent architect

# > "Design the database schema for our user system"

```

### 4. Watch the Magic

Your AI agent can now:

- Break down complex projects into task chains
- Manage dependencies automatically (no circular references!)
- Track progress and identify blockers
- Take notes and document decisions
- Keep everything in your git repository

## ✨ Why Lackey

| Problem | Lackey Solution |
|---------|----------------|
| 🔄 __Repetitive AI conversations__ | AI agents create persistent task chains |
| 🧠 __Agents forget context__ | All data stored in your repository |
| 🔗 __Complex dependencies__ | Automatic DAG validation prevents cycles |
| 📊 __No project visibility__ | Clear task status and progress tracking |
| 🏢 __Vendor lock-in__ | File-based storage, works with any AI agent |

## 🛠️ Core Features

- __🤖 AI-First Design__: Built specifically for AI agent workflows
- __📁 Repository Storage__: All data lives in your project (no cloud required)
- __🔗 Smart Dependencies__: Prevents circular dependencies with DAG validation
- __📝 Rich Notes__: Comprehensive documentation with search
- __🎯 Zero Global State__: Each project is completely self-contained
- __🔧 Extensible__: Template system for different project types

## 📖 Documentation

__New to Lackey?__ Start here:

- 📚 [Getting Started Tutorial](docs/tutorials/getting-started.md) - Your first project in 5 minutes
- 🔧 [AI Agent Integration](docs/tutorials/getting-started.md) - Connect different AI agents

### Need specific help

- 🆘 [Troubleshooting Guide](docs/tutorials/getting-started.md#troubleshooting) - Common issues and solutions
- 📋 [Task Patterns](docs/tutorials/getting-started.md#best-practices) - Best practices and workflows

### Looking up information

- 📖 [API Reference](docs/reference/api-reference.md) - Complete API documentation
- 🛠️ [CLI Commands](docs/reference/api-reference.md) - All command-line options
- 🔌 [MCP Tools](docs/reference/mcp-tools.md) - All 25 tools + 3 gateways

### Want to understand how it works

- 🏗️ [Architecture Overview](docs/explanation/architecture.md) - System design principles
- 🚪 [Gateway Pattern](docs/explanation/architecture.md) - Why we use gateways
- 🧠 [Cognitive Load Management](docs/explanation/cognitive-load.md) - AI optimization

[📑 __Full Documentation Index__](docs/index.md)

## 🎬 Real-World Examples

### Web Development Project

```bash

lackey init
q chat --agent manager

# > "Create an e-commerce website with user authentication, product catalog, shopping cart, and payment processing"

```text

### Data Science Pipeline

```bash

lackey init
q chat --agent manager

# > "Build a customer segmentation ML pipeline with data processing, model training, and deployment"

```

### Content Creation

```bash

lackey init
q chat --agent writer

# > "Plan a 5-part technical blog series on microservices architecture with code examples"

```text

## 🔌 MCP Integration

Lackey provides __3 semantic gateways__ that consolidate 25 individual tools:

- __`lackey_get`__ - Retrieve information (projects, tasks, notes)
- __`lackey_do`__ - Perform actions (create, update, manage)
- __`lackey_analyze`__ - Analyze and optimize (dependencies, progress, bottlenecks)

This reduces AI agent cognitive load by 89% while maintaining full functionality.

## 🏗️ How It Works

```

your-project/
├── .lackey/                 # All Lackey data
│   ├── projects/           # Project definitions
│   ├── tasks/             # Task chains and metadata
│   ├── notes/             # Documentation and decisions
│   └── config.yaml        # Configuration
├── src/                   # Your actual code
├── docs/                  # Your documentation
└── README.md             # This file

```text

__Key principle__: Your repository, your data. Delete `.lackey/` anytime to remove all traces.

## ⚡ Advanced Features

### Intelligent Dependencies

```python

# Lackey prevents circular dependencies automatically

task_a.depends_on(task_b)
task_b.depends_on(task_c)
task_c.depends_on(task_a)  # ❌ Circular dependency detected and prevented

```

### Rich Notes System

```python

# AI agents can document their decisions

lackey.add_task_note(
    content="## API Design Decision\nUsing REST over GraphQL for simplicity",
    tags=["architecture", "api", "decision"]
)

```text

### Bulk Operations

```python

# Efficiently manage multiple tasks

lackey.bulk_update_status(
    task_ids=[1, 2, 3, 4],
    status="in_progress",
    note="Starting sprint 2"
)

```

## 🚦 System Requirements

- __Python__: 3.10 or higher
- __Storage__: File-based (no database required)
- __Platform__: Windows, macOS, Linux
- __AI Agent__: Any MCP-compatible agent

## 🔧 Installation Options

### Standard Installation

```bash

pip install lackey-mcp

```bash

### Development Installation

```bash

git clone https://github.com/lackey-ai/lackey
cd lackey
pip install -e ".[dev]"
pre-commit install

```

### With All Features

```bash

pip install lackey-mcp[docs,security]

```bash

## 🤝 Contributing

We welcome contributions! See our [Development Guide](DEVELOPMENT.md) for setup instructions.

```bash

# Quick development setup

git clone https://github.com/lackey-ai/lackey
cd lackey
pip install -e ".[dev]"
pytest  # Run tests

```

## 📄 License

Proprietary License - See [LICENSE](LICENSE) for details.

---

### Ready to turn your AI agent into a project manager

```bash

pip install lackey-mcp && lackey serve

```text

[📚 __Get Started →__](docs/tutorials/getting-started.md) | [🆘 __Get Help
→__](docs/tutorials/getting-started.md#troubleshooting) | [🏗️ __Learn More →__](docs/explanation/architecture.md)
