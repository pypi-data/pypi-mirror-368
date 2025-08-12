# Vibe MCP Workflow Server

An MCP (Model Context Protocol) server that provides step-by-step workflow orchestration for AI agents, solving token throttling issues by delivering one workflow step at a time while maintaining session state.

## Overview

The Vibe MCP Workflow Server addresses the core problem of AI agents getting overwhelmed with large workflow outputs that lead to token throttling. Instead of receiving entire workflows at once, agents now interact with a stateful server that:

- Delivers one workflow step at a time
- Maintains session state across interactions
- Supports nested workflows with a call stack
- Provides JSON-formatted responses optimized for MCP consumption
- Leverages Vibe's existing workflow system without duplication

## Architecture

```
AI Agent (VSCode Copilot)
    ↓ MCP Protocol
Vibe MCP Server (Node.js)
    ↓ CLI calls
Vibe Core (Python)
    ↓ YAML workflows
Workflow System
```

## Key Features

### 🔄 Step-by-Step Execution
- AI agents receive only the current step, not entire workflows
- Dramatically reduces token usage
- Prevents context overflow and throttling

### 📚 Session State Management
- Each workflow session maintains its own state
- Sessions persist across multiple AI interactions
- Automatic session cleanup and management

### 🔁 Nested Workflow Support
- Workflows can trigger sub-workflows
- Call stack maintains parent workflow context
- Breaking out returns to parent workflow step

### 🎯 Token-Optimized Output
- JSON responses designed for MCP consumption
- Minimal overhead, maximum information
- Clear progress indicators and completion status

## Installation

### Prerequisites
- Node.js 18+
- Python 3.9+ with UV
- Vibe project installed and working

### Setup

1. **Install MCP Server Dependencies**:
```bash
cd /path/to/vibe/mcp-server
npm install
```

2. **Test MCP Server**:
```bash
node test.js
```

3. **Configure VSCode MCP**:
Add to your VSCode MCP settings:
```json
{
  "mcpServers": {
    "vibe-workflow": {
      "command": "node",
      "args": ["/path/to/vibe/mcp-server/index.js"],
      "env": {}
    }
  }
}
```

## Available Tools

### 1. `start_workflow`
Begins a new workflow session based on a natural language prompt.

**Input**:
```json
{
  "prompt": "create a new Python test file",
  "project_type": "python" // optional
}
```

**Output**:
```json
{
  "success": true,
  "session_id": "a1b2c3d4",
  "current_step": {
    "workflow": "implementation",
    "step_number": 1,
    "total_steps": 12,
    "step_text": "📋 **Plan your implementation**: Break down the task...",
    "is_command": false,
    "workflow_depth": 1
  },
  "workflow_stack": ["implementation"],
  "total_workflows": 1
}
```

### 2. `get_workflow_status`
Retrieves current session status and context.

**Input**:
```json
{
  "session_id": "a1b2c3d4"
}
```

**Output**:
```json
{
  "success": true,
  "session_id": "a1b2c3d4",
  "prompt": "create a new Python test file",
  "current_step": { /* step details */ },
  "workflow_stack": ["implementation"],
  "is_complete": false,
  "created_at": "2025-08-11T08:00:00.000Z",
  "last_accessed": "2025-08-11T08:05:00.000Z"
}
```

### 3. `advance_workflow`
Marks current step complete and advances to next step.

**Input**:
```json
{
  "session_id": "a1b2c3d4"
}
```

**Output**:
```json
{
  "success": true,
  "session_id": "a1b2c3d4",
  "current_step": { /* next step details */ },
  "workflow_stack": ["implementation"],
  "has_next": true
}
```

### 4. `break_workflow`
Breaks out of current workflow, returning to parent workflow if nested.

**Input**:
```json
{
  "session_id": "a1b2c3d4"
}
```

**Output**:
```json
{
  "success": true,
  "session_id": "a1b2c3d4",
  "current_step": { /* parent workflow step */ },
  "workflow_stack": ["parent_workflow"],
  "message": "Returned to parent workflow"
}
```

### 5. `list_workflow_sessions`
Lists all active workflow sessions.

**Input**: `{}` (no parameters)

**Output**:
```json
{
  "success": true,
  "sessions": [
    {
      "session_id": "a1b2c3d4",
      "prompt": "create a new Python test file",
      "workflow": "implementation",
      "step_number": 3,
      "total_steps": 12,
      "created_at": "2025-08-11T08:00:00.000Z"
    }
  ],
  "total_sessions": 1
}
```

## Usage Patterns

### Basic Workflow Execution

1. **Start a workflow**:
```javascript
await callTool('start_workflow', {
  prompt: 'implement user authentication'
});
```

2. **Get current step and execute**:
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

4. **Repeat until workflow complete**

### Nested Workflow Handling

When a step triggers a sub-workflow, the system automatically:
- Pushes current workflow to call stack
- Starts sub-workflow execution
- Returns to parent when sub-workflow completes

Use `break_workflow` to manually exit nested workflows early.

### Session Management

- Sessions automatically persist during execution
- Use `list_workflow_sessions` to see all active sessions
- Sessions include timestamps for tracking and cleanup

## Integration with AI Agents

### Recommended Agent Pattern

```javascript
class VibeWorkflowAgent {
  async executeWorkflow(prompt) {
    // Start workflow
    const session = await this.startWorkflow(prompt);

    while (!session.is_complete) {
      // Get current step
      const status = await this.getStatus(session.session_id);

      // Execute step (agent implementation)
      await this.executeStep(status.current_step);

      // Advance to next step
      session = await this.advanceWorkflow(session.session_id);
    }
  }

  async executeStep(step) {
    if (step.is_command) {
      // Execute command steps automatically
      await this.runCommand(step.step_text);
    } else {
      // Handle analysis/planning steps
      await this.analyzeAndPlan(step.step_text);
    }
  }
}
```

### Token Efficiency Benefits

- **Before**: Agent receives 2000+ token workflows causing throttling
- **After**: Agent receives 50-100 token steps, maintaining flow
- **Result**: 95%+ reduction in context size per interaction

### Error Handling

All tools return `success: false` with error details on failure:

```json
{
  "success": false,
  "error": "Session not found: invalid_id",
  "session_id": "invalid_id"
}
```

## Development

### Testing

Run the full test suite:
```bash
cd mcp-server
node test.js
```

### Debugging

Enable debug output by setting environment variables:
```bash
DEBUG=vibe-mcp node index.js
```

### Extending

To add new workflow operations:

1. Add CLI command to `vibe/cli.py` in MCP group
2. Add corresponding tool to `mcp-server/index.js`
3. Update tool list and request handler
4. Add tests to `test.js`

## Architecture Benefits

### Separation of Concerns
- **Vibe Core**: Workflow logic and YAML management
- **MCP Server**: Lightweight protocol adapter
- **AI Agent**: Step execution and decision making

### Maintainability
- Single source of truth for workflows (Vibe YAML files)
- No duplication of workflow logic
- MCP server is just a thin protocol wrapper

### Scalability
- Session state managed efficiently
- Minimal memory footprint per session
- Supports concurrent workflow sessions

## Future Enhancements

- [ ] Workflow session persistence across server restarts
- [ ] Advanced workflow branching and conditional execution
- [ ] Integration with other AI agent platforms beyond VSCode
- [ ] Workflow analytics and performance monitoring
- [ ] Custom workflow templates and reusable patterns

## Troubleshooting

### Common Issues

**MCP Server won't start**:
- Check Node.js version (18+ required)
- Verify all npm dependencies installed
- Ensure Vibe project is working (`uv run python main.py --help`)

**Workflow sessions not persisting**:
- Sessions are currently in-memory only
- Restart MCP server clears all sessions
- This is expected behavior in current version

**VSCode not discovering MCP server**:
- Verify MCP configuration in VSCode settings
- Check server path is absolute and correct
- Restart VSCode after configuration changes

**Commands failing**:
- Ensure Vibe project is in working state
- Check that UV and Python dependencies are installed
- Verify working directory permissions

---

*The Vibe MCP Workflow Server transforms AI-assisted development by providing controlled, step-by-step workflow execution without token overload.*
