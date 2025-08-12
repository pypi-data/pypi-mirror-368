"""Vibe: Intelligent workflow orchestrator for vibe coding."""

from .version import __version__

__author__ = "Soren N"
__description__ = "A CLI tool for vibe coding with intelligent workflow orchestration"

from .analyzer import PromptAnalyzer
from .config import VibeConfig
from .orchestrator import WorkflowOrchestrator

__all__ = ["__version__", "PromptAnalyzer", "VibeConfig", "WorkflowOrchestrator"]

__all__ = ["PromptAnalyzer", "VibeConfig", "WorkflowOrchestrator"]
