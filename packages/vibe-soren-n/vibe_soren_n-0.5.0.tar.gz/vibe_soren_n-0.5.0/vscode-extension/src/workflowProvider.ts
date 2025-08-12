import * as vscode from 'vscode';
import { McpServerManager } from './mcpServerManager';

export interface WorkflowItem {
    name: string;
    description: string;
    category: string;
    steps?: string[];
}

/**
 * Tree data provider for Vibe workflows
 */
export class WorkflowProvider implements vscode.TreeDataProvider<WorkflowTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<WorkflowTreeItem | undefined | null | void> = new vscode.EventEmitter<WorkflowTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<WorkflowTreeItem | undefined | null | void> = this._onDidChangeTreeData.event;

    private workflows: WorkflowItem[] = [];

    constructor(
        private context: vscode.ExtensionContext,
        private mcpServerManager: McpServerManager
    ) {
        this.loadDefaultWorkflows();
    }

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: WorkflowTreeItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: WorkflowTreeItem): Thenable<WorkflowTreeItem[]> {
        if (!element) {
            // Return categories
            const categories = [...new Set(this.workflows.map(w => w.category))];
            return Promise.resolve(categories.map(category =>
                new WorkflowTreeItem(
                    category,
                    `${category.charAt(0).toUpperCase() + category.slice(1)} Workflows`,
                    vscode.TreeItemCollapsibleState.Collapsed,
                    'category'
                )
            ));
        } else if (element.contextValue === 'category') {
            // Return workflows in this category
            const categoryWorkflows = this.workflows.filter(w => w.category === element.label);
            return Promise.resolve(categoryWorkflows.map(workflow =>
                new WorkflowTreeItem(
                    workflow.name,
                    workflow.description,
                    vscode.TreeItemCollapsibleState.None,
                    'workflow',
                    {
                        command: 'vibe.runWorkflow',
                        title: 'Run Workflow',
                        arguments: [workflow]
                    }
                )
            ));
        }

        return Promise.resolve([]);
    }

    private loadDefaultWorkflows(): void {
        this.workflows = [
            {
                name: 'analyze',
                description: 'Analyze project structure and provide insights',
                category: 'core'
            },
            {
                name: 'quality',
                description: 'Run comprehensive quality checks',
                category: 'core'
            },
            {
                name: 'cleanup',
                description: 'Clean up temporary files and artifacts',
                category: 'core'
            },
            {
                name: 'python_test',
                description: 'Run Python tests with pytest',
                category: 'python'
            },
            {
                name: 'python_quality',
                description: 'Check Python code quality (linting, formatting)',
                category: 'python'
            },
            {
                name: 'python_env',
                description: 'Set up Python development environment',
                category: 'python'
            },
            {
                name: 'js_test',
                description: 'Run JavaScript/TypeScript tests',
                category: 'frontend'
            },
            {
                name: 'js_build',
                description: 'Build JavaScript/TypeScript project',
                category: 'frontend'
            },
            {
                name: 'react_dev',
                description: 'Set up React development environment',
                category: 'frontend'
            },
            {
                name: 'vue_dev',
                description: 'Set up Vue.js development environment',
                category: 'frontend'
            },
            {
                name: 'docs_create',
                description: 'Create project documentation',
                category: 'documentation'
            },
            {
                name: 'docs_review',
                description: 'Review documentation quality',
                category: 'documentation'
            },
            {
                name: 'git_workflow',
                description: 'Set up Git workflow and branching strategy',
                category: 'development'
            },
            {
                name: 'dependencies',
                description: 'Update and manage project dependencies',
                category: 'development'
            },
            {
                name: 'session_start',
                description: 'Start a development session',
                category: 'session'
            },
            {
                name: 'session_retrospective',
                description: 'Conduct session retrospective',
                category: 'session'
            }
        ];
    }
}

export class WorkflowTreeItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly tooltip: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly contextValue: string,
        public readonly command?: vscode.Command
    ) {
        super(label, collapsibleState);
        this.tooltip = tooltip;
        this.description = contextValue === 'workflow' ? '' : `(${this.getWorkflowCount()} workflows)`;
    }

    private getWorkflowCount(): number {
        // This would be updated by the provider, but for now return a placeholder
        return 0;
    }

    iconPath = {
        light: this.contextValue === 'category' ?
            vscode.Uri.file(this.getResourcePath('light', 'folder.svg')) :
            vscode.Uri.file(this.getResourcePath('light', 'workflow.svg')),
        dark: this.contextValue === 'category' ?
            vscode.Uri.file(this.getResourcePath('dark', 'folder.svg')) :
            vscode.Uri.file(this.getResourcePath('dark', 'workflow.svg'))
    };

    private getResourcePath(theme: string, icon: string): string {
        // For now, use VS Code's built-in icons
        return '';
    }
}
