"""Prompt analysis engine for determining appropriate workflows."""

import re

from rich.console import Console
from rich.panel import Panel

from .config import VibeConfig
from .workflows import get_workflow_registry


class PromptAnalyzer:
    """Analyzes prompts to determine appropriate workflows."""

    def __init__(self, config: VibeConfig):
        """Initialize the prompt analyzer with configuration."""
        self.config = config
        self.console = Console()
        self.workflow_registry = get_workflow_registry()

    def analyze(self, prompt: str, show_analysis: bool = True) -> list[str]:
        """Analyze prompt and return list of relevant workflows."""
        # First try built-in workflows
        built_in_workflows = self._match_built_in_workflows(prompt)

        # Then try config-based workflows
        config_workflows = self._match_config_workflows(prompt)

        # Combine and deduplicate
        all_workflows = list(dict.fromkeys(built_in_workflows + config_workflows))

        if show_analysis:
            self._display_analysis(
                prompt, all_workflows, built_in_workflows, config_workflows
            )

        return all_workflows

    def _match_built_in_workflows(self, prompt: str) -> list[str]:
        """Match prompt against built-in workflows in the registry."""
        matching_workflows = self.workflow_registry.get_workflows_by_triggers(prompt)
        return [workflow.name for workflow in matching_workflows]

    def _match_config_workflows(self, prompt: str) -> list[str]:
        """Match prompt against workflow trigger patterns."""
        prompt_lower = prompt.lower()
        matched_workflows: set[str] = set()

        # Get project-specific workflows first
        project_type = self.config.detect_project_type()
        project_config = self.config.project_types.get(project_type, None)

        # Check project-specific workflows
        if project_config:
            for workflow_name, workflow_config in project_config.workflows.items():
                if self._matches_triggers(prompt_lower, workflow_config.triggers):
                    matched_workflows.add(workflow_name)

        # Check global workflows
        for workflow_name, workflow_config in self.config.workflows.items():
            if self._matches_triggers(prompt_lower, workflow_config.triggers):
                matched_workflows.add(workflow_name)

        # Default to research guidance if no matches
        if not matched_workflows:
            matched_workflows.add("Research Guidance for Agents")

        return list(matched_workflows)

    def _matches_triggers(self, prompt: str, triggers: list[str]) -> bool:
        """Check if prompt matches any of the trigger patterns."""
        for trigger in triggers:
            # Support both simple word matching and regex patterns
            try:
                if re.search(r"\b" + trigger.replace("*", r"\w*") + r"\b", prompt):
                    return True
            except re.error:
                # Fallback to simple substring matching
                if trigger in prompt:
                    return True
        return False

    def _display_analysis(
        self,
        prompt: str,
        all_workflows: list[str],
        built_in_workflows: list[str],
        config_workflows: list[str],
    ) -> None:
        """Display analysis results with rich formatting."""
        self.console.print()

        # Show prompt
        self.console.print(
            Panel(
                f"[bold blue]{prompt}[/bold blue]",
                title="🤔 Analyzing Prompt",
                border_style="blue",
            )
        )

        # Show detected workflows
        if all_workflows:
            workflow_descriptions = []

            # Add built-in workflows with their descriptions
            for workflow_name in built_in_workflows:
                workflow = self.workflow_registry.get_workflow(workflow_name)
                if workflow:
                    description = workflow.description
                    workflow_descriptions.append(f"  ✓ [built-in] {description}")

            # Add config workflows
            for workflow_name in config_workflows:
                if workflow_name not in built_in_workflows:  # Avoid duplicates
                    workflow_config = self.config.workflows.get(workflow_name)
                    if workflow_config and workflow_config.description:
                        description = workflow_config.description
                    else:
                        description = f"📋 {workflow_name.title()} workflow"
                    workflow_descriptions.append(f"  ✓ [custom] {description}")

            self.console.print(
                Panel(
                    "\n".join(workflow_descriptions),
                    title="🎯 Detected Workflow Needs",
                    border_style="green",
                )
            )
        else:
            self.console.print(
                Panel(
                    "  → Defaulting to analysis workflow",
                    title="⚠️ No Specific Workflows Detected",
                    border_style="yellow",
                )
            )

        self.console.print()
