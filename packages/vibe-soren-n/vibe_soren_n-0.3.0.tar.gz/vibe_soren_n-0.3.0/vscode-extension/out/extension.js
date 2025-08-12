"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = require("vscode");
const mcpServerManager_1 = require("./mcpServerManager");
const workflowProvider_1 = require("./workflowProvider");
const vibeCommands_1 = require("./vibeCommands");
let mcpServerManager;
let workflowProvider;
/**
 * Extension activation function
 */
function activate(context) {
    console.log('Vibe AI Workflows extension is now active!');
    // Initialize MCP server manager
    mcpServerManager = new mcpServerManager_1.McpServerManager(context);
    // Initialize workflow provider for tree view
    workflowProvider = new workflowProvider_1.WorkflowProvider(context, mcpServerManager);
    // Initialize commands
    const vibeCommands = new vibeCommands_1.VibeCommands(context, mcpServerManager, workflowProvider);
    // Register tree data provider
    vscode.window.registerTreeDataProvider('vibeWorkflows', workflowProvider);
    // Register commands
    const commands = [
        vscode.commands.registerCommand('vibe.startWorkflow', () => vibeCommands.startWorkflow()),
        vscode.commands.registerCommand('vibe.listWorkflows', () => vibeCommands.listWorkflows()),
        vscode.commands.registerCommand('vibe.openWorkflowGuide', () => vibeCommands.openWorkflowGuide()),
        vscode.commands.registerCommand('vibe.refreshWorkflows', () => workflowProvider.refresh()),
        vscode.commands.registerCommand('vibe.runWorkflow', (workflow) => vibeCommands.runWorkflow(workflow))
    ];
    // Register workspace context
    updateWorkspaceContext();
    const watcher = vscode.workspace.createFileSystemWatcher('**/.vibe.yaml');
    watcher.onDidChange(() => updateWorkspaceContext());
    watcher.onDidCreate(() => updateWorkspaceContext());
    watcher.onDidDelete(() => updateWorkspaceContext());
    // Add disposables to context
    context.subscriptions.push(...commands, watcher, mcpServerManager);
    // Auto-start MCP server if configured
    const config = vscode.workspace.getConfiguration('vibe');
    if (config.get('autoStartMcpServer', true)) {
        mcpServerManager.start();
    }
}
exports.activate = activate;
/**
 * Extension deactivation function
 */
function deactivate() {
    if (mcpServerManager) {
        mcpServerManager.dispose();
    }
}
exports.deactivate = deactivate;
/**
 * Update workspace context for conditional UI display
 */
function updateWorkspaceContext() {
    const hasVibeConfig = vscode.workspace.workspaceFolders?.some(folder => {
        const vibeConfigPath = vscode.Uri.joinPath(folder.uri, '.vibe.yaml');
        return vscode.workspace.fs.stat(vibeConfigPath).then(() => true, () => false);
    });
    vscode.commands.executeCommand('setContext', 'workspaceHasVibeConfig', hasVibeConfig);
}
//# sourceMappingURL=extension.js.map