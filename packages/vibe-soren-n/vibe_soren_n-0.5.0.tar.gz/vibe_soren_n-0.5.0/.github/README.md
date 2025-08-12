# Vibe Project GitHub Configuration

This directory contains GitHub-specific configuration files for the Vibe project, including AI agent collaboration guidelines and VSCode Copilot chat modes.

## Structure

### 📄 copilot-instructions.md
Comprehensive AI agent collaboration guide for developing Vibe. This file contains:

- **Dogfooding Requirements**: Use Vibe to develop Vibe itself
- **Workflow-First Development**: All tasks should go through Vibe's workflow system
- **Natural Language Interface**: Primary interface for discovering and executing workflows
- **Quality Guidelines**: Validation patterns and development standards
- **Architecture Patterns**: Core system design and organization principles

**Key Principle**: This file enforces the self-improving nature of Vibe by requiring all AI agents to use Vibe workflows for development tasks.

### 📁 chatmodes/
VSCode Copilot chat mode configurations for project-specific AI assistance.

#### vibe-agent.chatmode.md
Custom VSCode Copilot chat mode that:

- **Enforces Dogfooding**: Requires using Vibe workflows for all development
- **Demonstrates Capabilities**: Shows natural language query processing in action
- **Supports Both Modes**: Works in both Chat and Agent modes
- **Provides Context**: Gives AI agents project-specific knowledge and constraints
- **Guides Workflow Usage**: Helps AI agents understand how to query and use Vibe workflows

## Usage

### For AI Agents
1. **Read copilot-instructions.md first** - Contains mandatory development patterns
2. **Use the vibe-agent chat mode** - Provides project-specific context and guidelines
3. **Always query Vibe workflows** - Demonstrate the system by using it
4. **Document new patterns** - Create workflows for successful development approaches

### For VSCode Users
1. **Install the vibe-agent chat mode** - Place in `.github/chatmodes/` directory
2. **Select vibe-agent mode** - Choose from the chat mode dropdown in VSCode
3. **Query naturally** - Ask questions about development tasks and let Vibe guide the workflow
4. **Follow recommendations** - Use Vibe's suggested workflows for development tasks

## Chat Mode Features

The vibe-agent chat mode provides:

- **Workflow Discovery**: Natural language queries to find appropriate workflows
- **Task Guidance**: Specific recommendations for Vibe development tasks
- **Quality Assurance**: Automated validation through Vibe's quality workflows
- **Pattern Documentation**: Helps create new workflows for successful patterns
- **Dogfooding Enforcement**: Ensures Vibe is used to develop itself

## Integration with Vibe Workflows

This configuration integrates with Vibe's workflow system:

- **Query Processing**: Maps natural language to appropriate workflow categories
- **Workflow Execution**: Guides execution of discovered workflows
- **Pattern Creation**: Helps document successful approaches as new workflows
- **Quality Validation**: Uses Vibe's validation workflows for all changes
- **Self-Improvement**: Creates a feedback loop for system enhancement

## Example Usage

```bash
# Query Vibe for development guidance
python main.py "what workflow should I use to add a new feature?"

# Follow Vibe's recommendations
python main.py "run Python quality checks"

# Validate changes through Vibe
python main.py "validate my recent changes"

# Document successful patterns
python main.py "create a workflow for the pattern I just used"
```

This configuration ensures that all AI interactions with the Vibe project follow the workflow-first, dogfooding approach that demonstrates the system's capabilities while improving its development processes.
