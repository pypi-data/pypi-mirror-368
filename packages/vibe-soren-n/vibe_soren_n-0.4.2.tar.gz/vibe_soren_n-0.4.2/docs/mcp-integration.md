# Vibe MCP Integration Guide

## Overview

This guide explains how to integrate the Vibe MCP Workflow Server with VSCode to enable step-by-step workflow execution for AI agents.

## Architecture

The integration consists of three layers:

1. **Vibe Core (Python)** - Workflow analysis and session management
2. **MCP Server (Node.js)** - Protocol adapter for AI agents
3. **VSCode Extension** - Registration and configuration

```
AI Agent (GitHub Copilot)
    ↓ MCP Protocol
MCP Workflow Server (Node.js)
    ↓ Shell: `uv run python -m vibe.cli mcp ...`
Vibe Session Manager (Python)
    ↓ File I/O: ~/.vibe/sessions/
Workflow State Persistence
```

## Benefits

### Token Reduction
- **Before**: AI agents receive 50+ workflow steps (2000+ tokens per query)
- **After**: AI agents receive 1 step at a time (50-100 tokens per query)
- **Reduction**: 90%+ token usage decrease

### State Management
- **Persistent sessions**: Workflow progress saved across interactions
- **Resumable workflows**: Can continue after interruptions
- **Nested workflow support**: Sub-workflows with automatic return to parent

### Natural Language Interface
- **Prompt-driven**: "analyze project and run tests" → appropriate workflows
- **Project-aware**: Automatically detects project type and applies relevant workflows
- **Intelligent routing**: Vibe's analyzer selects optimal workflow combinations

## Installation

### 1. Vibe Core Setup

Already completed in this repository. The core components are:

- `vibe/session.py` - Session management classes
- `vibe/orchestrator.py` - Extended with session methods
- `vibe/cli.py` - MCP command group (`vibe mcp start|status|next|break|list`)

### 2. MCP Server Setup

```bash
cd vibe/mcp-server
npm install
node test.js  # Should show all tests passing
```

### 3. VSCode Configuration

Add to your VSCode `settings.json`:

```json
{
  "mcp.servers": {
    "vibe-workflow": {
      "command": "node",
      "args": ["/absolute/path/to/vibe/mcp-server/index.js"],
      "env": {}
    }
  }
}
```

## Usage

### Basic Workflow Execution

1. **Start a workflow**:
```javascript
await callTool('start_workflow', {
  prompt: 'implement user authentication'
});
```

2. **Get current step**:
```javascript
const status = await callTool('get_workflow_status', {
  session_id: 'a1b2c3d4'
});
// Execute the current step instructions
```

3. **Advance to next step**:
```javascript
await callTool('advance_workflow', {
  session_id: 'a1b2c3d4'
});
```

### Natural Language Examples

- "analyze this project and suggest improvements"
- "create a comprehensive test suite"
- "implement error handling and validation"
- "optimize performance and add monitoring"
- "create documentation and deployment guide"

## MCP Tools Available

### 1. `start_workflow`
Begins a new workflow session based on natural language prompt.

### 2. `get_workflow_status`
Retrieves current session status and step information.

### 3. `advance_workflow`
Marks current step complete and advances to next step.

### 4. `break_workflow`
Breaks out of current workflow, returning to parent if nested.

### 5. `list_workflow_sessions`
Lists all active workflow sessions.

## Workflow Categories

Vibe automatically routes prompts to appropriate workflow categories:

### Core Workflows
- **analysis** - Project analysis and assessment
- **implementation** - Feature development and coding
- **quality** - Testing, validation, and quality assurance
- **documentation** - Documentation creation and maintenance

### Language-Specific Workflows
- **python** - Python development workflows
- **javascript** - JavaScript/Node.js workflows
- **typescript** - TypeScript development workflows
- **frontend** - UI/UX development workflows

### Process Workflows
- **git** - Version control workflows
- **deployment** - Deployment and DevOps workflows
- **security** - Security assessment and implementation

## Advanced Configuration

### Custom Workflow Integration

Create project-specific workflows in `.vibe.yaml`:

```yaml
workflows:
  project_setup:
    description: "Project-specific setup workflow"
    triggers:
      - "setup project"
      - "initialize development"
    steps:
      - name: "Install dependencies"
        command: "npm install"
      - name: "Setup environment"
        command: "cp .env.example .env"
```

### Session Persistence

Sessions are automatically saved to `~/.vibe/sessions/` and can be resumed:

```bash
# List active sessions
uv run python main.py mcp list

# Resume specific session
uv run python main.py mcp status <session_id>
```

## Testing and Validation

### MCP Server Testing

```bash
cd vibe/mcp-server
node test.js
```

Expected output:
```
🎉 All tests completed successfully!
✅ MCP connection and initialization
✅ Tool discovery and listing
✅ Workflow session creation
✅ Session status retrieval
✅ Workflow step advancement
✅ Session listing
✅ Workflow breaking
```

### Vibe CLI Testing

```bash
cd vibe
uv run python main.py mcp start "test workflow"
uv run python main.py mcp status <session_id>
uv run python main.py mcp next <session_id>
```

## Troubleshooting

### Common Issues

**MCP Server Won't Start**:
- Check Node.js version (18+ required)
- Verify npm dependencies: `cd mcp-server && npm install`
- Test manually: `node index.js`

**Workflows Not Loading**:
- Verify Vibe installation: `uv run python main.py --help`
- Check workflow files: `ls vibe/workflows/data/`
- Test workflow loading: `uv run python main.py workflows`

**Session State Issues**:
- Sessions are in-memory (cleared on restart)
- Check session directory: `ls ~/.vibe/sessions/`
- Clear stale sessions: `rm ~/.vibe/sessions/*`

### Debug Mode

Enable debug logging:

```bash
DEBUG=1 node mcp-server/index.js
```

View MCP server logs in VSCode:
1. Open Command Palette (`Cmd+Shift+P`)
2. Search "MCP: Show Server Logs"
3. Select "vibe-workflow"

## Integration Patterns

### VSCode Extension Development

For creating custom VSCode extensions that integrate with Vibe:

```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';

const server = new Server({
  name: 'project-vibe-integration',
  version: '1.0.0'
});

// Register tools that call Vibe MCP server
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  // Proxy to Vibe MCP server
});
```

### CI/CD Integration

Integrate Vibe workflows with CI/CD pipelines:

```yaml
# .github/workflows/vibe-integration.yml
name: Vibe Workflow Integration
on: [push, pull_request]

jobs:
  vibe-analysis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Vibe Analysis
        run: |
          cd vibe
          uv run python main.py "analyze this project and generate report"
```

---

The Vibe MCP integration provides a powerful foundation for AI-assisted development with token-efficient, step-by-step workflow execution while maintaining full compatibility with existing development tools and processes.

## Architecture

The integration consists of three layers:

1. **Vibe Core (Python)** - Workflow analysis and session management
2. **MCP Server (Node.js)** - Protocol adapter for AI agents
3. **VSCode Extension** - Registration and configuration

```
AI Agent (GitHub Copilot)
    ↓ MCP Protocol
MCP Workflow Server (Node.js)
    ↓ Shell: `uv run python -m vibe.cli mcp ...`
Vibe Session Manager (Python)
    ↓ File I/O: ~/.vibe/sessions/
Workflow State Persistence
```

## Benefits

### Token Reduction
- **Before**: AI agents receive 50+ workflow steps (2000+ tokens per query)
- **After**: AI agents receive 1 step at a time (50-100 tokens per query)
- **Reduction**: 90%+ token usage decrease

### State Management
- **Persistent sessions**: Workflow progress saved across interactions
- **Resumable workflows**: Can continue after interruptions
- **Nested workflow support**: Sub-workflows with automatic return to parent

### Natural Language Interface
- **Prompt-driven**: "analyze project and run tests" → appropriate workflows
- **Project-aware**: Automatically detects project type and applies relevant workflows
- **Intelligent routing**: Vibe's analyzer selects optimal workflow combinations

## Installation

### 1. Vibe Core Setup

Already completed in this repository. The core components are:

- `vibe/session.py` - Session management classes
- `vibe/orchestrator.py` - Extended with session methods
- `vibe/cli.py` - MCP command group (`vibe mcp start|status|next|break|list`)

### 2. MCP Server Setup

```bash
cd mcp-server
npm install
```

### 3. VSCode Configuration

#### Option A: Manual Configuration

Add to VSCode `settings.json`:

```json
{
  "mcp.servers": {
    "vibe-workflow": {
      "command": "node",
      "args": ["/Users/soren-n/Documents/workspace/vibe/mcp-server/index.js"],
      "env": {
        "PATH": "/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

#### Option B: VSCode Extension (Future)

Create a VSCode extension that automatically:
- Detects Vibe installation
- Registers the MCP server
- Provides configuration UI

## Usage Examples

### Basic Workflow Execution

```javascript
// AI Agent perspective
const session = await callTool('start_workflow', {
  prompt: 'analyze the project structure and run quality checks'
});

// Response:
{
  "session_id": "abc12345",
  "current_step": {
    "workflow": "analysis",
    "step_number": 1,
    "step_text": "📄 **Discover project files**: `find . -name '*.py'`",
    "is_command": true
  }
}

// Execute the current step, then advance
await callTool('advance_workflow', { session_id: "abc12345" });
```

### Nested Workflow Example

```javascript
// Main workflow calls sub-workflow
const session = await callTool('start_workflow', {
  prompt: 'implement feature with tests and documentation'
});

// Workflow stack: ["implementation", "testing", "documentation"]
// Agent executes step by step:
// 1. Implementation steps
// 2. Testing sub-workflow (nested)
// 3. Return to main workflow
// 4. Documentation steps
```

### Error Recovery

```javascript
// If agent gets confused, break out of current workflow
await callTool('break_workflow', { session_id: "abc12345" });

// Or list all sessions to understand context
const sessions = await callTool('list_workflow_sessions', {});
```



# Check status
uv run python -m vibe.cli mcp status abc12345

# Advance step
uv run python -m vibe.cli mcp next abc12345
```

## Future Enhancements

### VSCode Extension

Create a dedicated VSCode extension with:
- Automatic Vibe detection and setup
- Workflow progress visualization
- Session management UI
- Configuration wizard

### Enhanced Workflow Features

- **Conditional steps**: Skip steps based on project state
- **Parallel workflows**: Execute multiple workflows simultaneously
- **Workflow templates**: Pre-built workflows for common tasks
- **Progress visualization**: Show workflow progress in VSCode

### Integration Improvements

- **Smart workflow suggestions**: AI-powered workflow recommendations
- **Context awareness**: Workflows that adapt to current file/selection
- **Automated validation**: Verify step completion automatically
- **Error recovery**: Automatic retry and fallback strategies

## Conclusion

The Vibe MCP integration provides a powerful foundation for token-efficient AI agent workflows. By combining Vibe's intelligent workflow analysis with MCP's step-by-step execution model, we achieve:

- **90%+ token reduction** through step-by-step execution
- **Persistent workflow state** that survives interruptions
- **Natural language interface** for workflow initiation
- **Nested workflow support** for complex task orchestration

This system scales AI agent capabilities while staying within token limits, enabling much more sophisticated development assistance.
