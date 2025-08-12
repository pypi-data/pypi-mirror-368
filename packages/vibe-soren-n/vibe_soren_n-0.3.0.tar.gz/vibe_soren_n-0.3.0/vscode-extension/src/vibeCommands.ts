import * as vscode from 'vscode';
import { McpServerManager } from './mcpServerManager';
import { WorkflowProvider, WorkflowItem } from './workflowProvider';

/**
 * Handles Vibe workflow commands
 */
export class VibeCommands {
    constructor(
        private context: vscode.ExtensionContext,
        private mcpServerManager: McpServerManager,
        private workflowProvider: WorkflowProvider
    ) {}

    /**
     * Start a workflow via input box
     */
    async startWorkflow(): Promise<void> {
        const input = await vscode.window.showInputBox({
            prompt: 'Enter your workflow request in natural language',
            placeHolder: 'e.g., "set up Python environment" or "run tests"',
            ignoreFocusOut: true
        });

        if (!input) {
            return;
        }

        // Check if MCP server is running
        if (!this.mcpServerManager.getStatus().running) {
            const startServer = await vscode.window.showInformationMessage(
                'Vibe MCP server is not running. Start it now?',
                'Yes',
                'No'
            );

            if (startServer === 'Yes') {
                const started = await this.mcpServerManager.start();
                if (!started) {
                    return;
                }
            } else {
                return;
            }
        }

        // Show progress
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Running Vibe workflow...',
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0, message: 'Processing request...' });

            try {
                // For now, simulate workflow execution
                // In a real implementation, this would communicate with the MCP server
                await this.simulateWorkflowExecution(input, progress);

                vscode.window.showInformationMessage(`Workflow completed: ${input}`);
            } catch (error) {
                vscode.window.showErrorMessage(`Workflow failed: ${error}`);
            }
        });
    }

    /**
     * List available workflows
     */
    async listWorkflows(): Promise<void> {
        const workflows = this.getAvailableWorkflows();

        const selected = await vscode.window.showQuickPick(
            workflows.map(w => ({
                label: w.name,
                description: w.category,
                detail: w.description,
                workflow: w
            })),
            {
                placeHolder: 'Select a workflow to run',
                ignoreFocusOut: true
            }
        );

        if (selected) {
            await this.runWorkflow(selected.workflow);
        }
    }

    /**
     * Open workflow guide
     */
    async openWorkflowGuide(): Promise<void> {
        const panel = vscode.window.createWebviewPanel(
            'vibeWorkflowGuide',
            'Vibe Workflow Guide',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        panel.webview.html = this.getWorkflowGuideHtml();
    }

    /**
     * Run a specific workflow
     */
    async runWorkflow(workflow: WorkflowItem): Promise<void> {
        // Check if MCP server is running
        if (!this.mcpServerManager.getStatus().running) {
            const startServer = await vscode.window.showInformationMessage(
                'Vibe MCP server is not running. Start it now?',
                'Yes',
                'No'
            );

            if (startServer === 'Yes') {
                const started = await this.mcpServerManager.start();
                if (!started) {
                    return;
                }
            } else {
                return;
            }
        }

        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `Running ${workflow.name}...`,
            cancellable: false
        }, async (progress) => {
            try {
                await this.executeWorkflow(workflow, progress);
                vscode.window.showInformationMessage(`Workflow '${workflow.name}' completed successfully`);
            } catch (error) {
                vscode.window.showErrorMessage(`Workflow '${workflow.name}' failed: ${error}`);
            }
        });
    }

    /**
     * Simulate workflow execution (placeholder)
     */
    private async simulateWorkflowExecution(
        input: string,
        progress: vscode.Progress<{ message?: string; increment?: number }>
    ): Promise<void> {
        const steps = [
            'Analyzing request...',
            'Finding matching workflows...',
            'Executing workflow steps...',
            'Finalizing results...'
        ];

        for (let i = 0; i < steps.length; i++) {
            progress.report({
                increment: (100 / steps.length),
                message: steps[i]
            });
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    }

    /**
     * Execute a specific workflow
     */
    private async executeWorkflow(
        workflow: WorkflowItem,
        progress: vscode.Progress<{ message?: string; increment?: number }>
    ): Promise<void> {
        progress.report({ increment: 0, message: `Starting ${workflow.name}...` });

        // In a real implementation, this would:
        // 1. Send the workflow request to the MCP server
        // 2. Handle the response and show results
        // 3. Update progress based on actual workflow steps

        // For now, simulate execution
        const steps = workflow.steps || ['Initializing...', 'Processing...', 'Completing...'];

        for (let i = 0; i < steps.length; i++) {
            progress.report({
                increment: (100 / steps.length),
                message: steps[i]
            });
            await new Promise(resolve => setTimeout(resolve, 800));
        }
    }

    /**
     * Get available workflows
     */
    private getAvailableWorkflows(): WorkflowItem[] {
        return [
            { name: 'analyze', description: 'Analyze project structure', category: 'core' },
            { name: 'quality', description: 'Run quality checks', category: 'core' },
            { name: 'python_test', description: 'Run Python tests', category: 'python' },
            { name: 'js_build', description: 'Build JavaScript project', category: 'frontend' },
            { name: 'docs_create', description: 'Create documentation', category: 'documentation' }
        ];
    }

    /**
     * Generate HTML for workflow guide
     */
    private getWorkflowGuideHtml(): string {
        return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Vibe Workflow Guide</title>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                    padding: 20px;
                    line-height: 1.6;
                }
                h1, h2 { color: var(--vscode-textLink-foreground); }
                .workflow-category {
                    margin: 20px 0;
                    padding: 15px;
                    border-left: 4px solid var(--vscode-textLink-foreground);
                    background-color: var(--vscode-textBlockQuote-background);
                }
                .workflow {
                    margin: 10px 0;
                    padding: 10px;
                    background-color: var(--vscode-editor-inactiveSelectionBackground);
                    border-radius: 4px;
                }
                code {
                    background-color: var(--vscode-textCodeBlock-background);
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            </style>
        </head>
        <body>
            <h1>🚀 Vibe AI Workflows Guide</h1>

            <p>Welcome to Vibe AI Workflows! This extension provides intelligent workflow orchestration for development tasks.</p>

            <h2>Getting Started</h2>
            <p>Use natural language to describe what you want to accomplish:</p>
            <ul>
                <li><code>Ctrl+Shift+P</code> → "Vibe: Start Workflow"</li>
                <li>Type: "set up Python environment"</li>
                <li>Or: "run tests and check code quality"</li>
            </ul>

            <h2>Available Workflow Categories</h2>

            <div class="workflow-category">
                <h3>🔧 Core Workflows</h3>
                <div class="workflow">
                    <strong>analyze</strong> - Analyze project structure and provide insights
                </div>
                <div class="workflow">
                    <strong>quality</strong> - Run comprehensive quality checks
                </div>
                <div class="workflow">
                    <strong>cleanup</strong> - Clean up temporary files and artifacts
                </div>
            </div>

            <div class="workflow-category">
                <h3>🐍 Python Workflows</h3>
                <div class="workflow">
                    <strong>python_test</strong> - Run Python tests with pytest
                </div>
                <div class="workflow">
                    <strong>python_quality</strong> - Check Python code quality
                </div>
                <div class="workflow">
                    <strong>python_env</strong> - Set up Python development environment
                </div>
            </div>

            <div class="workflow-category">
                <h3>🌐 Frontend Workflows</h3>
                <div class="workflow">
                    <strong>js_test</strong> - Run JavaScript/TypeScript tests
                </div>
                <div class="workflow">
                    <strong>react_dev</strong> - Set up React development environment
                </div>
                <div class="workflow">
                    <strong>vue_dev</strong> - Set up Vue.js development environment
                </div>
            </div>

            <h2>Configuration</h2>
            <p>Configure the extension in VS Code settings:</p>
            <ul>
                <li><strong>vibe.mcpServerPath</strong> - Path to Vibe MCP server</li>
                <li><strong>vibe.autoStartMcpServer</strong> - Auto-start server on activation</li>
                <li><strong>vibe.defaultWorkflowCategory</strong> - Default category to show</li>
            </ul>

            <h2>Troubleshooting</h2>
            <p>If workflows aren't working:</p>
            <ol>
                <li>Check that the MCP server is running (Output → Vibe MCP Server)</li>
                <li>Verify the server path in settings</li>
                <li>Ensure Node.js is installed and accessible</li>
            </ol>
        </body>
        </html>
        `;
    }
}
