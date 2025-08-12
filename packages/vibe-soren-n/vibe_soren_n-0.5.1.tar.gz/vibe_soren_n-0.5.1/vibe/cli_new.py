"""CLI interface for vibe - legacy compatibility wrapper.

This module provides backward compatibility for imports but delegates
to the new modular CLI structure in the cli/ package.
"""

# For backward compatibility, also import the individual functions
from .cli import (
    check,
    config_info,
    guide,
    init,
    list_workflows,
    mcp,
    run,
    run_workflow,
    workflows,
)

# Import the main CLI components from the new modular structure
from .cli.main import cli, main

# Export everything that was previously available
__all__ = [
    "cli",
    "main",
    "run",
    "run_workflow",
    "init",
    "check",
    "config_info",
    "list_workflows",
    "guide",
    "workflows",
    "mcp",
]
