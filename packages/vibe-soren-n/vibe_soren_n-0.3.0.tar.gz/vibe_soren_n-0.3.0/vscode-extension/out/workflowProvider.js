"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WorkflowTreeItem = exports.WorkflowProvider = void 0;
const vscode = require("vscode");
/**
 * Tree data provider for Vibe workflows
 */
class WorkflowProvider {
    constructor(context, mcpServerManager) {
        this.context = context;
        this.mcpServerManager = mcpServerManager;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        this.workflows = [];
        this.loadDefaultWorkflows();
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        return element;
    }
    getChildren(element) {
        if (!element) {
            // Return categories
            const categories = [...new Set(this.workflows.map(w => w.category))];
            return Promise.resolve(categories.map(category => new WorkflowTreeItem(category, `${category.charAt(0).toUpperCase() + category.slice(1)} Workflows`, vscode.TreeItemCollapsibleState.Collapsed, 'category')));
        }
        else if (element.contextValue === 'category') {
            // Return workflows in this category
            const categoryWorkflows = this.workflows.filter(w => w.category === element.label);
            return Promise.resolve(categoryWorkflows.map(workflow => new WorkflowTreeItem(workflow.name, workflow.description, vscode.TreeItemCollapsibleState.None, 'workflow', {
                command: 'vibe.runWorkflow',
                title: 'Run Workflow',
                arguments: [workflow]
            })));
        }
        return Promise.resolve([]);
    }
    loadDefaultWorkflows() {
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
exports.WorkflowProvider = WorkflowProvider;
class WorkflowTreeItem extends vscode.TreeItem {
    constructor(label, tooltip, collapsibleState, contextValue, command) {
        super(label, collapsibleState);
        this.label = label;
        this.tooltip = tooltip;
        this.collapsibleState = collapsibleState;
        this.contextValue = contextValue;
        this.command = command;
        this.iconPath = {
            light: this.contextValue === 'category' ?
                vscode.Uri.file(this.getResourcePath('light', 'folder.svg')) :
                vscode.Uri.file(this.getResourcePath('light', 'workflow.svg')),
            dark: this.contextValue === 'category' ?
                vscode.Uri.file(this.getResourcePath('dark', 'folder.svg')) :
                vscode.Uri.file(this.getResourcePath('dark', 'workflow.svg'))
        };
        this.tooltip = tooltip;
        this.description = contextValue === 'workflow' ? '' : `(${this.getWorkflowCount()} workflows)`;
    }
    getWorkflowCount() {
        // This would be updated by the provider, but for now return a placeholder
        return 0;
    }
    getResourcePath(theme, icon) {
        // For now, use VS Code's built-in icons
        return '';
    }
}
exports.WorkflowTreeItem = WorkflowTreeItem;
//# sourceMappingURL=workflowProvider.js.map