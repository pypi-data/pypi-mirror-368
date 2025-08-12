"""Workflow management system with built-in intelligent workflows."""

from .core import get_core_workflows
from .models import Workflow


class WorkflowRegistry:
    """Central registry for all built-in workflows."""

    def __init__(self) -> None:
        """Initialize the workflow registry and load built-in workflows."""
        self.workflows: dict[str, Workflow] = {}
        self._load_built_in_workflows()

    def _load_built_in_workflows(self) -> None:
        """Load all built-in workflows from YAML files."""
        # Load all workflows from YAML files (includes core + language-specific)
        self.workflows.update(get_core_workflows())

    def get_workflows_for_project_type(self, project_type: str) -> dict[str, Workflow]:
        """Get workflows applicable to a specific project type."""
        applicable = {}

        for name, workflow in self.workflows.items():
            # Include if workflow is universal (empty project_types)
            # or if project_type matches workflow's project_types
            if not workflow.project_types or project_type in workflow.project_types:
                applicable[name] = workflow

        return applicable

    def get_all_workflows(self) -> dict[str, Workflow]:
        """Get all registered workflows."""
        return self.workflows.copy()

    def get_workflow(self, name: str) -> Workflow | None:
        """Get a specific workflow by name."""
        return self.workflows.get(name)

    def register_workflow(self, workflow: Workflow) -> None:
        """Register a custom workflow (for .vibe.yaml overrides)."""
        self.workflows[workflow.name] = workflow

    def get_workflows_by_triggers(self, prompt: str) -> list[Workflow]:
        """Find workflows that match the given prompt."""
        import re

        matching = []
        prompt_lower = prompt.lower()

        for workflow in self.workflows.values():
            for trigger in workflow.triggers:
                if re.search(trigger, prompt_lower):
                    matching.append(workflow)
                    break  # Don't add the same workflow multiple times

        return matching


# Global workflow registry instance
workflow_registry = WorkflowRegistry()


def get_workflow_registry() -> WorkflowRegistry:
    """Get the global workflow registry."""
    return workflow_registry


__all__ = ["Workflow", "WorkflowRegistry", "get_workflow_registry", "workflow_registry"]
