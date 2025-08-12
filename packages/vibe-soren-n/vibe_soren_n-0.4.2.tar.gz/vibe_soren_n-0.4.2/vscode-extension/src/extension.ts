import * as vscode from 'vscode';
import { McpServerManager } from './mcpServerManager';
import { WorkflowProvider } from './workflowProvider';
import { VibeCommands } from './vibeCommands';

let mcpServerManager: McpServerManager;
let workflowProvider: WorkflowProvider;

/**
 * Extension activation function
 */
export function activate(context: vscode.ExtensionContext) {
    console.log('Vibe AI Workflows extension is now active!');

    // Initialize MCP server manager
    mcpServerManager = new McpServerManager(context);

    // Initialize workflow provider for tree view
    workflowProvider = new WorkflowProvider(context, mcpServerManager);

    // Initialize commands
    const vibeCommands = new VibeCommands(context, mcpServerManager, workflowProvider);

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
    if (config.get<boolean>('autoStartMcpServer', true)) {
        mcpServerManager.start();
    }
}

/**
 * Extension deactivation function
 */
export function deactivate() {
    if (mcpServerManager) {
        mcpServerManager.dispose();
    }
}

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
