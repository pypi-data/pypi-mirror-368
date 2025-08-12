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
- **Hot Reloading**: File system watching with negligible performance impact

## Hot Reloading (✅ Implemented)

The workflow system now supports hot reloading of YAML files for improved developer experience:

### Features
- **File System Watching**: Automatic detection of YAML file changes using watchdog
- **Instant Cache Invalidation**: Modified workflows available immediately
- **Callback Support**: Register functions to be called on reload
- **Graceful Degradation**: Falls back gracefully if watchdog is unavailable

### Usage
```python
from vibe.workflows.loader import start_hot_reloading, stop_hot_reloading

# Enable hot reloading
start_hot_reloading()

# Your workflows will now automatically reload when YAML files change

# Disable when done (optional - handles cleanup automatically)
stop_hot_reloading()
```

### Implementation Details
- Watches `vibe/workflows/data/` directory recursively
- Triggers on `.yaml` file modifications, creations, and deletions
- Thread-safe cache invalidation
- Automatic cleanup on process exit

## Schema Validation (✅ Implemented)

The workflow system now includes JSON Schema validation for YAML workflow files:

### Features
- **Comprehensive Schema**: Validates workflow structure, field types, and required properties
- **Flexible Format Support**: Handles both simple string steps and complex step objects
- **Legacy Support**: Validates both `steps` (preferred) and `commands` (legacy) formats
- **Unicode Support**: Full support for emojis and international characters in workflow names
- **Optional Validation**: Can be enabled/disabled for different use cases

### Schema Structure
```yaml
name: "workflow_name"               # Required: Workflow identifier
description: "Description"          # Required: Human-readable description
triggers: ["trigger1", "trigger2"]  # Required: Activation patterns
steps:                              # Required: Guidance steps (preferred)
  - "Simple step"
  - step_text: "Complex step"       # Optional: Structured step format
    command: "echo test"            # Optional: Associated command
    working_dir: "."               # Optional: Working directory
dependencies: ["tool1", "tool2"]    # Optional: Required tools
project_types: ["python", "web"]    # Optional: Applicable project types
conditions: ["condition1"]          # Optional: Required conditions
```

### Usage
```python
from vibe.workflows.loader import set_validation_enabled, is_validation_enabled
from vibe.workflows.validation import validate_workflow_data

# Control validation
set_validation_enabled(True)   # Enable validation (default)
set_validation_enabled(False)  # Disable for development

# Direct validation
try:
    validate_workflow_data(workflow_dict)
    print("✅ Workflow is valid")
except WorkflowValidationError as e:
    print(f"❌ Validation failed: {e}")
```

### Benefits
- **Early Error Detection**: Catch malformed workflows before runtime
- **Consistency Enforcement**: Ensure all workflows follow expected structure
- **IDE Support**: JSON Schema enables autocomplete and validation in editors
- **Documentation**: Schema serves as formal specification for workflow format

## Future Enhancements

- **Workflow Dependencies**: Support for workflow composition
- **Conditional Logic**: More sophisticated condition evaluation
- **Template System**: Variable substitution in workflow commands
