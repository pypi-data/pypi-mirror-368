# Workflow System Architecture

## Overview

The vibe project uses a YAML-based workflow system that separates workflow definitions from Python code, enabling independent updates and better maintainability.

## Architecture Components

### 1. Data Models (`vibe/workflows/models.py`)
- **Purpose**: Defines the `Workflow` dataclass structure
- **Key Elements**: name, description, triggers, commands, dependencies, project_types, conditions
- **Design Decision**: Separate module to resolve circular imports between loader and core

### 2. YAML Loader (`vibe/workflows/loader.py`)
- **Purpose**: Loads workflow definitions from YAML files with Python fallback
- **Key Features**:
  - Caching for performance
  - Error handling with graceful fallback
  - PyYAML integration for parsing
  - Validation of workflow structure

### 3. Integration Layer (`vibe/workflows/core.py`)
- **Purpose**: Bridges YAML workflows with existing Python workflow system
- **Key Features**:
  - Seamless fallback to hardcoded Python workflows
  - Maintains backward compatibility
  - Integration with workflow matching logic

### 4. YAML Workflow Definitions (`vibe/workflows/data/*.yaml`)
- **Purpose**: External workflow definitions independent of code
- **Current Workflows**:
  - `analysis.yaml`: Project structure analysis and improvement identification
  - `branch_strategy.yaml`: AI-guided branch selection and merge timing
  - `dependency_update.yaml`: Comprehensive dependency and tooling updates
  - `git_management.yaml`: Git repository management and semantic versioning

## Design Decisions

### Separation of Code and Data
**Problem**: Workflows were hardcoded in Python, making updates require code changes.

**Solution**: YAML-based external definitions with loader system.

**Benefits**:
- Independent workflow updates
- Non-technical users can modify workflows
- Version control for workflow changes
- Better maintainability

### Fallback Architecture
**Problem**: Need to maintain compatibility during transition.

**Solution**: Graceful fallback from YAML to Python workflows.

**Implementation**:
```python
# Try YAML first, fallback to Python
try:
    yaml_workflows = workflow_loader.load_workflows()
    if yaml_workflows:
        return yaml_workflows
except Exception:
    return get_hardcoded_workflows()
```

### Caching Strategy
**Problem**: YAML parsing on every workflow access impacts performance.

**Solution**: In-memory caching with invalidation.

**Benefits**:
- Faster subsequent access
- Reduced file I/O
- Maintained responsiveness

## File Structure

```
vibe/workflows/
├── __init__.py
├── models.py          # Workflow dataclass definitions
├── loader.py          # YAML loading and caching
├── core.py           # Integration and legacy workflows
└── data/             # YAML workflow definitions
    ├── analysis.yaml
    ├── branch_strategy.yaml
    ├── dependency_update.yaml
    └── git_management.yaml
```

## Workflow Definition Format

```yaml
name: "Workflow Name"
description: "Description of what this workflow does"
triggers:
  - "keyword patterns that trigger this workflow"
project_types:
  - "project types this applies to"
dependencies:
  - "required tools or conditions"
conditions:
  - "when this workflow should be used"
commands:
  - "shell command 1"
  - "shell command 2"
  - "echo 'Information for user'"
```

## Loading Process

1. **YAML Discovery**: Scan `data/` directory for `.yaml` files
2. **Parsing**: Use PyYAML to parse workflow definitions
3. **Validation**: Ensure required fields are present
4. **Caching**: Store parsed workflows in memory
5. **Fallback**: If YAML loading fails, use Python workflows

## Error Handling

- **File Not Found**: Log warning, continue with other workflows
- **Parse Error**: Log error details, skip malformed workflow
- **Missing Fields**: Log validation error, skip incomplete workflow
- **Complete Failure**: Fall back to hardcoded Python workflows

## Performance Considerations

- **Lazy Loading**: Workflows loaded on first access
- **Caching**: Parsed workflows cached in memory
- **Minimal Parsing**: Only parse when cache is empty
- **Fast Fallback**: Quick switch to Python workflows on failure

## Future Enhancements

- **Hot Reloading**: Detect file changes and reload workflows
- **Validation Schema**: JSON Schema validation for YAML structure
- **Workflow Dependencies**: Support for workflow composition
- **Conditional Logic**: More sophisticated condition evaluation
- **Template System**: Variable substitution in workflow commands
