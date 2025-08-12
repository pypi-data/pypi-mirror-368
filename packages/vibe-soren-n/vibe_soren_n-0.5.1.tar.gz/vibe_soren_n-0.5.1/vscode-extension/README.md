# Vibe AI Workflows - VS Code Extension

🚀 **AI-powered workflow orchestration for development tasks**

Vibe brings intelligent workflow automation directly into your VS Code environment through the Model Context Protocol (MCP), enabling natural language queries to discover and execute development workflows.

## Features

- **Natural Language Workflows**: Query workflows using plain English
- **MCP Integration**: Seamless Model Context Protocol server integration
- **Workflow Categories**: Organized workflows for different development needs:
  - Core operations (analysis, cleanup, help)
  - Python development (environment, testing, quality)
  - Frontend development (JavaScript, React, Vue)
  - Documentation (creation, review, ADRs)
  - Development process (git, branching, dependencies)
  - Session management (development lifecycle)

## Installation

Install from the VS Code Marketplace:

```bash
code --install-extension soren-n.vibe-workflows
```

Or install from VSIX:
1. Download the `.vsix` file
2. Run: `code --install-extension path/to/vibe-workflows.vsix`

## Usage

### Command Palette

Open the Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`) and search for:

- **Vibe: Start Workflow** - Begin a new workflow session
- **Vibe: List Available Workflows** - Browse all available workflows
- **Vibe: Open Workflow Guide** - Get help with workflow usage

### Workflow Examples

- "analyze this project"
- "set up Python environment"
- "run quality checks"
- "create documentation"
- "help with git workflow"

## Configuration

Configure the extension in VS Code settings:

- **Vibe: MCP Server Path** - Path to the Vibe MCP server executable
- **Vibe: Auto Start MCP Server** - Automatically start server on activation
- **Vibe: Default Workflow Category** - Default category to display

## Requirements

- VS Code 1.74.0 or higher
- Vibe MCP server (included with extension)
- Node.js (for MCP server runtime)

## Development

### Building from Source

```bash
# Clone and setup
git clone https://github.com/soren-n/vibe
cd vibe/vscode-extension

# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Package extension
npm run package
```

### Project Structure

```
vscode-extension/
├── src/                 # TypeScript source files
│   ├── extension.ts     # Main extension entry point
│   ├── mcpServerManager.ts  # MCP server lifecycle
│   ├── vibeCommands.ts  # Command implementations
│   └── workflowProvider.ts # Workflow tree provider
├── images/              # Extension icons and assets
├── out/                 # Compiled JavaScript output
└── package.json         # Extension manifest
```

### Available Scripts

- `npm run compile` - Compile TypeScript
- `npm run watch` - Watch mode compilation
- `npm run lint` - ESLint code quality checks
- `npm run clean` - Remove build artifacts
- `npm run rebuild` - Clean and recompile
- `npm run package` - Create VSIX package
- `npm run publish` - Publish to marketplace

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/soren-n/vibe/issues)
- **Documentation**: [Vibe Documentation](https://github.com/soren-n/vibe/docs)
- **Discussions**: [GitHub Discussions](https://github.com/soren-n/vibe/discussions)

---

Made with ❤️ by the Vibe development team
