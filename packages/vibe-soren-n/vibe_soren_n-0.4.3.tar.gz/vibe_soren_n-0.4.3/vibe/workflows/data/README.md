# Workflow Organization

This directory contains 29 YAML workflow definitions organized into logical categories for better maintainability and discoverability.

**Conceptual Note**: Vibe workflows provide **guidance steps** rather than automated commands. Each workflow step is textual guidance that can include command suggestions, reminders, best practices, or any helpful advice. Users follow the guidance manually, maintaining full control over their development process.

## Workflow Structure

Each YAML workflow contains:
- `name`: Unique identifier
- `description`: What the workflow helps with
- `triggers`: Patterns that activate this workflow
- `steps`: Guidance text (may include suggested commands, but not limited to commands)
- `dependencies`: Optional workflow dependencies
- `project_types`: Optional project type constraints
- `conditions`: Optional activation conditions

## Directory Structure

### 📁 core/ (6 workflows)
Core project operations and general functionality:
- `analysis.yaml` - Project analysis and context understanding
- `check.yaml` - Validation and quality checks
- `cleanup.yaml` - Project hygiene and temporary file management
- `help.yaml` - User assistance and guidance
- `next_steps.yaml` - Workflow continuation and suggestions
- `refactor.yaml` - Code refactoring operations

### 📁 session/ (2 workflows)
Session management and workflow orchestration:
- `session.yaml` - Development session management
- `session_retrospective.yaml` - Session completion and retrospectives

### 📁 documentation/ (4 workflows)
Documentation creation, maintenance, and quality:
- `adr_management.yaml` - Architecture Decision Records
- `documentation.yaml` - General documentation tasks
- `documentation_driven_development.yaml` - DDD workflow support
- `documentation_review.yaml` - Documentation quality and updates

### 📁 development/ (3 workflows)
Development process and Git workflow management:
- `branch_strategy.yaml` - Git branching strategies
- `dependency_update.yaml` - Dependency management
- `git_management.yaml` - Git operations and workflow

### 📁 python/ (6 workflows)
Python-specific development workflows:
- `python_build.yaml` - Python project building
- `python_env.yaml` - Python environment management
- `python_install.yaml` - Python dependency installation
- `python_quality.yaml` - Python code quality checks
- `python_test.yaml` - Python testing workflows
- `python_type_check.yaml` - Python type checking

### 📁 frontend/ (8 workflows)
Frontend development and JavaScript/Node.js workflows:
- `js_build.yaml` - JavaScript/Node.js building
- `js_dev.yaml` - JavaScript development server
- `js_install.yaml` - JavaScript dependency installation
- `js_quality.yaml` - JavaScript code quality
- `js_test.yaml` - JavaScript testing
- `js_type_check.yaml` - JavaScript/TypeScript type checking
- `react_dev.yaml` - React development workflow
- `vue_dev.yaml` - Vue.js development workflow

## Loading Architecture

The workflows are loaded recursively from all subdirectories using the updated `WorkflowLoader` in `loader.py`. The loader uses `Path.rglob("*.yaml")` to scan all subdirectories automatically.

## Workflow Naming Convention

Workflows follow a consistent naming pattern:
- **Category prefix**: `python_`, `js_`, etc. for language-specific workflows
- **Action suffix**: `_build`, `_test`, `_quality`, etc. for operation type
- **Framework specific**: `react_dev`, `vue_dev` for framework workflows
- **Generic names**: Core workflows use descriptive names without prefixes

## Adding New Workflows

When adding new workflows:
1. Choose the appropriate category folder
2. Follow the existing naming conventions
3. Use YAML format with required fields (name, description, triggers, commands)
4. Test loading with the workflow system
5. Update this README if adding new categories

## Migration Notes

This organized structure was created from a flat directory containing 29 workflows. The migration included:
- Converting legacy Python/JavaScript hardcoded workflows to YAML
- Creating logical category folders
- Updating the loader to handle recursive directory scanning
- Maintaining all existing workflow functionality while improving organization
