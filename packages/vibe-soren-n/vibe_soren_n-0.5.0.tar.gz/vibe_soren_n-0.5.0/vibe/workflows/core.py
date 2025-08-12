"""Core workflows that apply to any project type."""

from .loader import WorkflowLoader
from .models import Workflow

# Initialize workflow loader for dynamic YAML-based workflows
_workflow_loader = WorkflowLoader()


def get_core_workflows() -> dict[str, Workflow]:
    """Get all core workflows from YAML files.

    This function loads workflows exclusively from YAML files in the data directory.
    All workflows should be defined as YAML files for consistency and maintainability.

    Returns:
        dict[str, Workflow]: Dictionary mapping workflow names to Workflow objects

    """
    try:
        # Load all workflows from YAML files
        yaml_workflows = _workflow_loader.load_workflows()
        return yaml_workflows

    except Exception as e:
        print(f"Error: Failed to load workflows from YAML files: {e}")
        print("Please ensure YAML workflow files exist in vibe/workflows/data/")
        return {}


# Core workflows - loaded dynamically from YAML files
CORE_WORKFLOWS = get_core_workflows()


def reload_workflows() -> dict[str, Workflow]:
    """Reload workflows from YAML files."""
    global CORE_WORKFLOWS
    CORE_WORKFLOWS = get_core_workflows()
    return CORE_WORKFLOWS
