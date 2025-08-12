# Vibe MCP Workflow Server - Project Integration Guide

This guide shows how to integrate the Vibe MCP Workflow Server with any development project for token-efficient AI development.

## Quick Setup

### 1. Verify Vibe MCP Server is Working

```bash
cd /path/to/vibe/mcp-server
node test.js
```

You should see: `🎉 All tests completed successfully!`

### 2. Configure VSCode MCP Settings

Add to your VSCode settings.json:

```json
{
  "mcp.servers": {
    "vibe-workflow": {
      "command": "node",
      "args": ["/path/to/vibe/mcp-server/index.js"],
      "env": {}
    }
  }
}
```

### 3. Test Integration

In VSCode, open your project and use Copilot:

```
@vibe-workflow Start a workflow to "implement a new feature"
```

## Usage Examples for Development

### Creating New Components

```javascript
// Start component creation workflow
const session = await startWorkflow("create a new component");

// The agent will receive step-by-step guidance:
// Step 1: "Plan the component structure and interface"
// Step 2: "Create the appropriate files"
// Step 3: "Implement the component logic"
// etc.
```

### Quality Assurance Workflows

```javascript
// Start QA workflow for code changes
const session = await startWorkflow("run quality checks on my recent changes");

// Agent receives targeted steps:
// Step 1: "Run type checking"
// Step 2: "Run linting validation"
// Step 3: "Execute tests"
// etc.
```

### Feature Development

```javascript
// Start feature enhancement workflow
const session = await startWorkflow("implement user authentication");

// Agent gets focused steps:
// Step 1: "Analyze current architecture"
// Step 2: "Design authentication flow"
// Step 3: "Implement security measures"
// etc.
```

## Benefits for Development

### Token Efficiency
- **Before**: Agent gets 2000+ token workflow descriptions
- **After**: Agent gets 50-100 token focused steps
- **Result**: No more throttling, smoother development flow

### Workflow Adherence
- Ensures agents follow established project patterns
- Prevents deviation from coding conventions
- Maintains code quality through structured guidance

### Context Preservation
- Session state maintains workflow context across interruptions
- Nested workflows for complex features
- Consistent progress tracking and completion validation

## Project-Specific Workflows

The Vibe MCP server automatically accesses project-relevant workflows:

### Core Development
- `implementation` - Adding new features/components
- `quality` - Running validation and testing
- `documentation` - Creating/updating docs

### Frontend Specific
- `component` - Creating UI components
- `styling` - CSS/styling implementations
- `responsive` - Mobile-responsive design

### Backend Specific
- `api` - API development workflows
- `database` - Database operations
- `security` - Security implementations

### Testing Workflows
- `testing` - Unit and integration test creation
- `validation` - Quality assurance pipelines

## Integration Commands

Add these npm scripts to your project's package.json:

```json
{
  "scripts": {
    "vibe:start": "cd /path/to/vibe/mcp-server && node index.js",
    "vibe:test": "cd /path/to/vibe/mcp-server && node test.js",
    "vibe:workflow": "cd /path/to/vibe && uv run python main.py"
  }
}
```

## Troubleshooting

### MCP Server Not Found
1. Verify the Vibe project path in VSCode settings
2. Ensure Node.js dependencies are installed in vibe/mcp-server/
3. Test the server manually: `node /path/to/vibe/mcp-server/index.js`

### Workflows Not Loading
1. Check that Vibe YAML workflows are present in vibe/workflows/data/
2. Verify UV and Python are working: `cd vibe && uv run python main.py --help`
3. Test Vibe MCP commands: `uv run python main.py mcp list`

### Session State Issues
1. Sessions are currently in-memory (cleared on restart)
2. Use `list_workflow_sessions` to see active sessions
3. Break out of workflows cleanly to avoid orphaned sessions

---

With this integration, development becomes much more efficient, with AI agents receiving focused, step-by-step guidance while respecting the project's architecture and quality standards.
