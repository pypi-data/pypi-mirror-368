"""Workflow loader for YAML-based workflow definitions."""

from pathlib import Path

import yaml

from .models import Workflow


class WorkflowLoader:
    """Loads workflows from YAML files with dynamic discovery and caching."""

    def __init__(self) -> None:
        self.data_dir = Path(__file__).parent / "data"
        self._cache: dict[str, Workflow] = {}
        self._file_timestamps: dict[Path, float] = {}
        self._loaded = False

    def _get_file_timestamp(self, file_path: Path) -> float:
        """Get the modification timestamp of a file."""
        try:
            return file_path.stat().st_mtime
        except OSError:
            return 0.0

    def _is_cache_valid(self) -> bool:
        """Check if the cache is still valid by comparing file timestamps."""
        if not self._loaded:
            return False

        # Check if any workflow files have been modified, added, or removed
        current_files = set(self.data_dir.rglob("*.yaml"))
        cached_files = set(self._file_timestamps.keys())

        # If file set changed, cache is invalid
        if current_files != cached_files:
            return False

        # Check if any existing files have been modified
        for file_path in current_files:
            current_timestamp = self._get_file_timestamp(file_path)
            cached_timestamp = self._file_timestamps.get(file_path, 0.0)
            if current_timestamp > cached_timestamp:
                return False

        return True

    def load_workflows(self, force_reload: bool = False) -> dict[str, Workflow]:
        """Load all workflows from YAML files with dynamic discovery.

        Args:
            force_reload: Force reload even if cache appears valid
        """
        if not force_reload and self._is_cache_valid():
            return self._cache

        workflows = {}
        new_timestamps = {}

        # Load YAML workflows from data directory (recursively scan subdirectories)
        if self.data_dir.exists():
            for yaml_file in self.data_dir.rglob("*.yaml"):
                try:
                    workflow = self._load_workflow_from_yaml(yaml_file)
                    if workflow:
                        workflows[workflow.name] = workflow
                        new_timestamps[yaml_file] = self._get_file_timestamp(yaml_file)
                except Exception as e:
                    print(f"Warning: Failed to load workflow from {yaml_file}: {e}")

        self._cache = workflows
        self._file_timestamps = new_timestamps
        self._loaded = True
        return workflows

    def _load_workflow_from_yaml(self, yaml_file: Path) -> Workflow | None:
        """Load a single workflow from a YAML file."""
        with open(yaml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data:
            return None

        # Convert YAML data to Workflow instance
        # Support both 'steps' (preferred format) and 'commands' (legacy format)
        # 'steps' reflects that these are guidance suggestions,
        # not just executable commands
        steps = data.get("steps") or data.get("commands", [])

        return Workflow(
            name=data["name"],
            description=data["description"],
            triggers=data.get("triggers", []),
            steps=steps,
            dependencies=data.get("dependencies"),
            project_types=data.get("project_types"),
            conditions=data.get("conditions"),
        )

    def get_workflow(self, name: str) -> Workflow | None:
        """Get a specific workflow by name with automatic discovery."""
        workflows = self.load_workflows()
        return workflows.get(name)

    def load_workflow(self, name: str) -> Workflow | None:
        """Load a specific workflow by name (alias for get_workflow)."""
        return self.get_workflow(name)

    def reload(self) -> dict[str, Workflow]:
        """Force cache clear and reload all workflows."""
        self._cache.clear()
        self._file_timestamps.clear()
        self._loaded = False
        return self.load_workflows(force_reload=True)

    def get_all_workflows(self) -> dict[str, Workflow]:
        """Get all available workflows with automatic discovery."""
        return self.load_workflows()


# Global loader instance
_loader = WorkflowLoader()


def get_workflows() -> dict[str, Workflow]:
    """Get all available workflows with automatic discovery."""
    return _loader.load_workflows()


def get_workflow(name: str) -> Workflow | None:
    """Get a specific workflow by name with automatic discovery."""
    return _loader.get_workflow(name)


def reload_workflows() -> dict[str, Workflow]:
    """Force reload all workflows from disk."""
    return _loader.reload()
