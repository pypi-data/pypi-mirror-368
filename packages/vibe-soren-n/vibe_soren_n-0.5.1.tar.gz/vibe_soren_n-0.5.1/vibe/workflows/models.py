"""Workflow data structures for vibe CLI.

This module contains the core dataclass definitions for workflows,
separated to avoid circular imports between core.py and loader.py.
"""

from dataclasses import dataclass


@dataclass
class Workflow:
    """Represents a complete workflow with triggers, guidance steps, and metadata.

    A workflow consists of:
    - name: Unique identifier for the workflow
    - description: Human-readable description of what the workflow does
    - triggers: List of patterns that should activate this workflow
    - steps: List of guidance text/suggestions (may contain commands,
      but not limited to commands)
    - dependencies: Optional list of required tools/packages
    - project_types: Optional list of project types this applies to
    - conditions: Optional list of conditions that must be met

    Note: Steps are textual guidance, not executable commands. They provide suggestions,
    reminders, and directions that humans can follow. Commands may be included within
    the guidance text when appropriate.
    """

    name: str
    description: str
    triggers: list[str]
    steps: list[str]
    dependencies: list[str] | None = None
    project_types: list[str] | None = None
    conditions: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.dependencies is None:
            self.dependencies = []
        if self.project_types is None:
            self.project_types = []
        if self.conditions is None:
            self.conditions = []
