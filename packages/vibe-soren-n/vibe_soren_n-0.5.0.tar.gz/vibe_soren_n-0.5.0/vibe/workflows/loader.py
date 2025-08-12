"""Workflow loader for YAML-based workflow definitions."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

from .models import Workflow
from .validation import WorkflowValidationError, validate_workflow_data

# Try to import watchdog, gracefully handle if not available
try:
    from watchdog.events import FileSystemEvent, FileSystemEventHandler
    from watchdog.observers import Observer

    WATCHDOG_AVAILABLE = True
except ImportError:
    FileSystemEvent = None  # type: ignore
    FileSystemEventHandler = None  # type: ignore
    Observer = None  # type: ignore
    WATCHDOG_AVAILABLE = False


if WATCHDOG_AVAILABLE:

    class WorkflowFileHandler(FileSystemEventHandler):  # type: ignore
        """Handles file system events for workflow YAML files."""

        def __init__(self, callback: Callable[[], None]) -> None:
            self.callback = callback
            super().__init__()

        def on_modified(self, event: Any) -> None:
            if event.is_directory:
                return
            if str(event.src_path).endswith(".yaml"):
                self.callback()

        def on_created(self, event: Any) -> None:
            if event.is_directory:
                return
            if str(event.src_path).endswith(".yaml"):
                self.callback()

        def on_deleted(self, event: Any) -> None:
            if event.is_directory:
                return
            if str(event.src_path).endswith(".yaml"):
                self.callback()
else:
    # Fallback handler when watchdog is not available
    class WorkflowFileHandler:  # type: ignore[no-redef]
        def __init__(self, callback: Callable[[], None]) -> None:
            self.callback = callback


class WorkflowLoader:
    """Loads workflows from YAML files with dynamic discovery and caching."""

    def __init__(self, *, enable_validation: bool = True) -> None:
        self.data_dir = Path(__file__).parent / "data"
        self._cache: dict[str, Workflow] = {}
        self._file_timestamps: dict[Path, float] = {}
        self._loaded = False
        self.enable_validation = enable_validation
        # Hot reloading support
        self._observer = None
        self._watching = False
        self._reload_callbacks: list[Callable[[], None]] = []

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
        """Load a single workflow from a YAML file with schema validation."""
        with open(yaml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data:
            return None

        # Validate the workflow data against schema
        if self.enable_validation:
            try:
                validate_workflow_data(data)
            except WorkflowValidationError as e:
                print(f"Warning: Schema validation failed for {yaml_file}:")
                print(f"  {e}")
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

    def _on_file_change(self) -> None:
        """Internal callback for file system changes."""
        # Clear cache to force reload on next access
        self._cache.clear()
        self._file_timestamps.clear()
        self._loaded = False

        # Notify any registered callbacks
        for callback in self._reload_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Warning: Reload callback failed: {e}")

    def start_watching(self) -> None:
        """Start watching for file system changes for hot reloading."""
        if self._watching or not self.data_dir.exists():
            return

        if not WATCHDOG_AVAILABLE:
            print("Warning: watchdog not available, hot reloading disabled")
            return

        try:
            self._observer = Observer()  # type: ignore
            event_handler = WorkflowFileHandler(self._on_file_change)
            self._observer.schedule(event_handler, str(self.data_dir), recursive=True)  # type: ignore
            self._observer.start()  # type: ignore
            self._watching = True
        except Exception as e:
            print(f"Warning: Could not start file watching: {e}")

    def stop_watching(self) -> None:
        """Stop watching for file system changes."""
        if self._observer and self._watching:
            self._observer.stop()
            self._observer.join()
            self._observer = None
            self._watching = False

    def add_reload_callback(self, callback: Callable[[], None]) -> None:
        """Add a callback function to be called when workflows are reloaded."""
        self._reload_callbacks.append(callback)

    def remove_reload_callback(self, callback: Callable[[], None]) -> None:
        """Remove a previously added reload callback."""
        if callback in self._reload_callbacks:
            self._reload_callbacks.remove(callback)

    def is_watching(self) -> bool:
        """Check if file watching is currently active."""
        return self._watching


# Global loader instance
_loader = WorkflowLoader(enable_validation=True)


def get_workflows() -> dict[str, Workflow]:
    """Get all available workflows with automatic discovery."""
    return _loader.load_workflows()


def get_workflow(name: str) -> Workflow | None:
    """Get a specific workflow by name with automatic discovery."""
    return _loader.get_workflow(name)


def reload_workflows() -> dict[str, Workflow]:
    """Force reload all workflows from disk."""
    return _loader.reload()


def start_hot_reloading() -> None:
    """Enable hot reloading of workflow files."""
    _loader.start_watching()


def stop_hot_reloading() -> None:
    """Disable hot reloading of workflow files."""
    _loader.stop_watching()


def add_reload_callback(callback: Callable[[], None]) -> None:
    """Add a callback to be called when workflows are hot-reloaded."""
    _loader.add_reload_callback(callback)


def is_hot_reloading() -> bool:
    """Check if hot reloading is currently enabled."""
    return _loader.is_watching()


def set_validation_enabled(enabled: bool) -> None:
    """Enable or disable schema validation for workflows."""
    _loader.enable_validation = enabled


def is_validation_enabled() -> bool:
    """Check if schema validation is currently enabled."""
    return _loader.enable_validation
