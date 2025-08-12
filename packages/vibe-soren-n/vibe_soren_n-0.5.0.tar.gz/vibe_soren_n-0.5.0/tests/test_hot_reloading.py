"""Tests for hot reloading functionality."""

import tempfile
from pathlib import Path

import pytest
import yaml

from vibe.workflows.loader import WorkflowLoader


def test_hot_reloading_basic_functionality() -> None:
    """Test basic hot reloading start/stop functionality."""
    loader = WorkflowLoader()

    # Initially not watching
    assert not loader.is_watching()

    # Start watching
    loader.start_watching()
    assert loader.is_watching()

    # Stop watching
    loader.stop_watching()
    assert not loader.is_watching()


def test_hot_reloading_callback_registration() -> None:
    """Test callback registration and removal."""
    loader = WorkflowLoader()

    callback_called = []

    def test_callback() -> None:
        callback_called.append(True)

    # Add callback
    loader.add_reload_callback(test_callback)
    assert test_callback in loader._reload_callbacks

    # Remove callback
    loader.remove_reload_callback(test_callback)
    assert test_callback not in loader._reload_callbacks


def test_hot_reloading_cache_invalidation() -> None:
    """Test that cache invalidation works correctly."""
    loader = WorkflowLoader()

    # Load initial workflows
    initial_workflows = loader.get_all_workflows()
    assert len(initial_workflows) > 0

    # Cache should be populated
    assert loader._cache
    assert loader._loaded

    # Trigger cache invalidation
    loader._on_file_change()

    # Cache should be cleared
    assert not loader._cache
    assert not loader._loaded


def test_hot_reloading_with_temporary_directory() -> None:
    """Test hot reloading with a temporary workflow directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a temporary workflow loader with custom directory
        loader = WorkflowLoader()
        loader.data_dir = temp_path

        # Create a test workflow file
        test_workflow = {
            "name": "test_workflow",
            "description": "Test workflow for hot reloading",
            "triggers": ["test"],
            "steps": ["echo 'test'"],
        }

        workflow_file = temp_path / "test.yaml"
        with open(workflow_file, "w") as f:
            yaml.dump(test_workflow, f)

        # Load initial workflows
        workflows = loader.get_all_workflows()
        assert "test_workflow" in workflows

        # Test cache invalidation
        loader._on_file_change()

        # Cache should be cleared
        assert not loader._cache
        assert not loader._loaded

        # Reload should work
        workflows = loader.get_all_workflows()
        assert "test_workflow" in workflows


def test_hot_reloading_callback_execution() -> None:
    """Test that callbacks are executed on file changes."""
    loader = WorkflowLoader()

    callback_count = [0]

    def test_callback() -> None:
        callback_count[0] += 1

    # Add callback
    loader.add_reload_callback(test_callback)

    # Trigger file change
    loader._on_file_change()

    # Callback should have been called
    assert callback_count[0] == 1

    # Trigger again
    loader._on_file_change()
    assert callback_count[0] == 2


def test_hot_reloading_multiple_callbacks() -> None:
    """Test multiple callbacks are all executed."""
    loader = WorkflowLoader()

    results = []

    def callback1() -> None:
        results.append("callback1")

    def callback2() -> None:
        results.append("callback2")

    # Add both callbacks
    loader.add_reload_callback(callback1)
    loader.add_reload_callback(callback2)

    # Trigger file change
    loader._on_file_change()

    # Both callbacks should have been called
    assert "callback1" in results
    assert "callback2" in results
    assert len(results) == 2


def test_hot_reloading_graceful_degradation() -> None:
    """Test that hot reloading degrades gracefully when watchdog is unavailable."""
    # This test ensures the code doesn't crash when watchdog is not available
    loader = WorkflowLoader()

    # These should not raise exceptions even if watchdog is unavailable
    loader.start_watching()  # May print warning but shouldn't crash
    loader.stop_watching()  # Should handle None observer gracefully

    # Callback registration should work regardless
    def dummy_callback() -> None:
        pass

    loader.add_reload_callback(dummy_callback)
    loader.remove_reload_callback(dummy_callback)

    # Cache invalidation should work
    loader._on_file_change()


if __name__ == "__main__":
    pytest.main([__file__])
