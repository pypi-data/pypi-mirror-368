# vibe

A CLI tool that assists you in vibe coding, essentially a scripted workflow system guiding your agent.

## Overview

Vibe is an intelligent workflow orchestrator that analyzes your natural language prompts and automatically executes the appropriate development workflows. It's designed to make "vibe coding" - that flow state of rapid, intuitive development - more structured and productive.

## Key Features

- 🧠 **Intelligent Prompt Analysis**: Uses pattern matching to understand what you want to accomplish
- 🔄 **Workflow Orchestration**: Automatically executes workflows in the optimal order
- 🏗️ **Project Type Detection**: Supports multiple project types (Python, Vue/TypeScript, etc.)
- ⚙️ **Configurable**: Customize workflows and commands for your project needs
- 🎨 **Rich Output**: Beautiful, colored terminal output with progress indicators
- 🔌 **Extensible**: Plugin architecture for custom workflows and project types
- 🚀 **Automated Releases**: Full CI/CD pipeline with semantic versioning and marketplace publishing

## Installation

```bash
# Install with uv (recommended)
uv add vibe

# Or with pip
pip install vibe
```

## Quick Start

```bash
# Initialize vibe in your project
vibe init

# Run a workflow based on natural language
vibe "analyze the codebase structure"
vibe "implement user authentication"
vibe "run all tests and check quality"
vibe "create a pull request"
```

## Workflow YAML Quality Tools

Validate and normalize the built-in YAML workflows or your custom ones:

```bash
# Validate all workflow YAML files (schema, encoding, unknown keys)
vibe workflows validate

# Preview normalization changes (key order, legacy migrations)
vibe workflows format

# Apply normalization changes in-place
vibe workflows format --write
```

## Workflow Types

- 🔍 **Analysis**: Codebase exploration, pattern identification, research
- 🛠️ **Implementation**: Feature development, bug fixes, code changes
- 🧪 **Testing**: Test execution, validation, quality verification
- 📚 **Documentation**: Documentation updates, guides, explanations
- ✨ **Quality**: Code quality, linting, formatting, compliance
- 🔄 **Git**: Git operations, commits, PRs, repository management
- 🤖 **MCP**: MCP tools integration and AI-enhanced workflows
- 🎯 **Session**: Session management, completion, cleanup

## Documentation

For comprehensive documentation including philosophy, architecture, and guidelines:

📖 **[Full Documentation](docs/README.md)**

Key documents:
- **[Vibe Philosophy](docs/vibe-philosophy.md)**: Core principles of autonomous AI agent operation
- **[Workflow Architecture](docs/workflow-architecture.md)**: YAML-based workflow system design
- **[Development Guidelines](docs/development-guidelines.md)**: Project standards and best practices
- **[ADRs](docs/adr/)**: Architecture Decision Records for significant design decisions

## AI Agent Integration

🤖 **[GitHub Configuration](.github/README.md)**: AI agent collaboration setup

This project uses Vibe to develop itself (dogfooding). AI agents working on Vibe should:

- **Follow [copilot-instructions.md](.github/copilot-instructions.md)**: Comprehensive development guidelines
- **Use [vibe-agent.chatmode.md](.github/chatmodes/vibe-agent.chatmode.md)**: VSCode Copilot chat mode
- **Query Vibe workflows first**: Always use `python main.py "what should I do for [task]?"` before manual operations
- **Demonstrate capabilities**: Show Vibe's natural language interface by using it
- **Create new workflows**: Document successful patterns as YAML workflows

## Concise-by-default (TPS-aware)

Vibe is optimized to minimize tokens-per-second and overall token footprint:

- Always concise guidance: short summaries, delta updates, ≤6 bullets
- Quiet flags by default (e.g., `pytest -q --maxfail=1`, `mypy --hide-error-context --no-error-summary`)
- Sample large listings (e.g., `head`) and avoid dumping long outputs
- Prefer batched operations over many small calls; backoff + jitter on 429s
- Guidance steps are messages (not commands) and include inline command examples when needed

Downstream projects can keep their workflows token-thrifty by mirroring these patterns.

## Configuration

Create a `.vibe.yaml` file in your project root to customize workflows:

```yaml
project_type: "python"  # or "auto" for detection
workflows:
  testing:
    commands:
      - "uv run pytest"
      - "uv run ruff check"
  quality:
    commands:
      - "uv run mypy ."
      - "uv run ruff format"
```
