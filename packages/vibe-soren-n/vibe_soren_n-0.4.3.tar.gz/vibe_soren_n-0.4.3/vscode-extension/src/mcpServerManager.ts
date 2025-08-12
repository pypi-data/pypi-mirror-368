import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn, ChildProcess } from 'child_process';

/**
 * Manages the Vibe MCP server lifecycle
 */
export class McpServerManager implements vscode.Disposable {
    private mcpProcess: ChildProcess | undefined;
    private outputChannel: vscode.OutputChannel;
    private context: vscode.ExtensionContext;
    private isRunning = false;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.outputChannel = vscode.window.createOutputChannel('Vibe MCP Server');
    }

    /**
     * Start the MCP server
     */
    async start(): Promise<boolean> {
        if (this.isRunning) {
            this.outputChannel.appendLine('MCP server is already running');
            return true;
        }

        try {
            const serverPath = this.getMcpServerPath();
            if (!serverPath) {
                vscode.window.showErrorMessage('Vibe MCP server path not configured');
                return false;
            }

            if (!fs.existsSync(serverPath)) {
                vscode.window.showErrorMessage(`Vibe MCP server not found at: ${serverPath}`);
                return false;
            }

            this.outputChannel.appendLine(`Starting Vibe MCP server: ${serverPath}`);
            this.outputChannel.show(true);

            this.mcpProcess = spawn('node', [serverPath], {
                stdio: ['pipe', 'pipe', 'pipe'],
                env: {
                    ...process.env,
                    VIBE_PROJECT_ROOT: this.getVibeProjectRoot()
                }
            });

            this.mcpProcess.stdout?.on('data', (data) => {
                this.outputChannel.append(data.toString());
            });

            this.mcpProcess.stderr?.on('data', (data) => {
                this.outputChannel.append(`[ERROR] ${data.toString()}`);
            });

            this.mcpProcess.on('close', (code) => {
                this.isRunning = false;
                this.outputChannel.appendLine(`MCP server exited with code ${code}`);
                if (code !== 0) {
                    vscode.window.showErrorMessage(`Vibe MCP server crashed with exit code ${code}`);
                }
            });

            this.mcpProcess.on('error', (error) => {
                this.isRunning = false;
                this.outputChannel.appendLine(`MCP server error: ${error.message}`);
                vscode.window.showErrorMessage(`Failed to start Vibe MCP server: ${error.message}`);
            });

            this.isRunning = true;
            vscode.window.showInformationMessage('Vibe MCP server started successfully');
            return true;

        } catch (error) {
            this.outputChannel.appendLine(`Failed to start MCP server: ${error}`);
            vscode.window.showErrorMessage(`Failed to start Vibe MCP server: ${error}`);
            return false;
        }
    }

    /**
     * Stop the MCP server
     */
    stop(): void {
        if (this.mcpProcess && this.isRunning) {
            this.outputChannel.appendLine('Stopping Vibe MCP server...');
            this.mcpProcess.kill();
            this.mcpProcess = undefined;
            this.isRunning = false;
            vscode.window.showInformationMessage('Vibe MCP server stopped');
        }
    }

    /**
     * Get the MCP server status
     */
    getStatus(): { running: boolean; pid?: number } {
        return {
            running: this.isRunning,
            pid: this.mcpProcess?.pid
        };
    }

    /**
     * Get MCP server path from configuration or detect automatically
     */
    private getMcpServerPath(): string | undefined {
        const config = vscode.workspace.getConfiguration('vibe');
        let serverPath = config.get<string>('mcpServerPath');

        if (!serverPath) {
            // Try to auto-detect based on workspace
            const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
            if (workspaceRoot) {
                // Check for Vibe project structure
                const potentialPaths = [
                    path.join(workspaceRoot, 'mcp-server', 'index.js'),
                    path.join(workspaceRoot, 'vibe', 'mcp-server', 'index.js'),
                    path.join(workspaceRoot, '..', 'vibe', 'mcp-server', 'index.js')
                ];

                for (const potentialPath of potentialPaths) {
                    if (fs.existsSync(potentialPath)) {
                        serverPath = potentialPath;
                        break;
                    }
                }
            }
        }

        return serverPath;
    }

    /**
     * Get Vibe project root directory
     */
    private getVibeProjectRoot(): string {
        const serverPath = this.getMcpServerPath();
        if (serverPath) {
            // Assume project root is two levels up from mcp-server/index.js
            return path.dirname(path.dirname(serverPath));
        }

        // Fallback to workspace root
        return vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || process.cwd();
    }

    /**
     * Dispose of resources
     */
    dispose(): void {
        this.stop();
        this.outputChannel.dispose();
    }
}
