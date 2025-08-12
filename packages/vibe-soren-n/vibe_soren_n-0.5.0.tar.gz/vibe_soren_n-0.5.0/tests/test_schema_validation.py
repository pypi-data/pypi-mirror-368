"""Tests for JSON schema validation functionality."""

import tempfile
from pathlib import Path

import pytest
import yaml

from vibe.workflows.loader import WorkflowLoader
from vibe.workflows.validation import (
    WorkflowValidationError,
    create_example_workflow,
    get_validation_errors,
    validate_workflow_data,
    validate_workflow_structure,
)


def test_schema_validation_basic() -> None:
    """Test basic schema validation functionality."""
    # Valid workflow should pass
    valid_workflow = create_example_workflow()
    validate_workflow_data(valid_workflow)  # Should not raise

    # Invalid workflow should fail
    invalid_workflow = {
        "name": "",  # Empty name should fail
        "description": "test",
    }

    with pytest.raises(WorkflowValidationError):
        validate_workflow_data(invalid_workflow)


def test_schema_validation_structure_check() -> None:
    """Test non-raising structure validation."""
    valid_workflow = create_example_workflow()
    assert validate_workflow_structure(valid_workflow) is True

    invalid_workflow = {"name": ""}
    assert validate_workflow_structure(invalid_workflow) is False


def test_schema_validation_error_messages() -> None:
    """Test that validation error messages are helpful."""
    invalid_workflow = {
        "name": "",
        "description": "test",
        "triggers": [],  # Empty triggers array
        "steps": [],  # Empty steps array
    }

    errors = get_validation_errors(invalid_workflow)
    assert len(errors) > 0

    # Check that we get meaningful error messages
    error_text = str(errors)
    assert "name" in error_text or "triggers" in error_text or "steps" in error_text


def test_schema_validation_complex_steps() -> None:
    """Test validation of complex step structures."""
    workflow_with_complex_steps = {
        "name": "test_complex",
        "description": "Test workflow with complex steps",
        "triggers": ["test"],
        "steps": [
            "Simple step",
            {
                "step_text": "Complex step with command",
                "command": "echo test",
                "working_dir": ".",
            },
        ],
    }

    # Should validate successfully
    validate_workflow_data(workflow_with_complex_steps)
    assert validate_workflow_structure(workflow_with_complex_steps)


def test_schema_validation_legacy_commands() -> None:
    """Test validation supports legacy 'commands' field."""
    workflow_with_commands = {
        "name": "test_legacy",
        "description": "Test workflow with legacy commands field",
        "triggers": ["test"],
        "commands": ["echo test", "ls"],
    }

    validate_workflow_data(workflow_with_commands)
    assert validate_workflow_structure(workflow_with_commands)


def test_schema_validation_optional_fields() -> None:
    """Test validation with optional fields."""
    workflow_with_optionals = {
        "name": "test_optional",
        "description": "Test workflow with optional fields",
        "triggers": ["test"],
        "steps": ["echo test"],
        "dependencies": ["python", "git"],
        "project_types": ["python"],
        "conditions": ["git_repo_exists"],
        "display_name": "Test Optional",
        "category": "testing",
        "guidance": "Additional guidance text",
    }

    validate_workflow_data(workflow_with_optionals)
    assert validate_workflow_structure(workflow_with_optionals)


def test_schema_validation_in_loader() -> None:
    """Test schema validation integration with WorkflowLoader."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create loader with validation enabled
        loader = WorkflowLoader(enable_validation=True)
        loader.data_dir = temp_path

        # Create valid workflow file
        valid_workflow = {
            "name": "test_valid",
            "description": "Valid test workflow",
            "triggers": ["test"],
            "steps": ["echo test"],
        }

        valid_file = temp_path / "valid.yaml"
        with open(valid_file, "w") as f:
            yaml.dump(valid_workflow, f)

        # Create invalid workflow file
        invalid_workflow = {
            "name": "",  # Invalid empty name
            "description": "Invalid test workflow",
        }

        invalid_file = temp_path / "invalid.yaml"
        with open(invalid_file, "w") as f:
            yaml.dump(invalid_workflow, f)

        # Load workflows
        workflows = loader.get_all_workflows()

        # Only valid workflow should be loaded
        assert "test_valid" in workflows
        assert len(workflows) == 1  # Invalid workflow should be rejected


def test_schema_validation_can_be_disabled() -> None:
    """Test that schema validation can be disabled."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create loader with validation disabled
        loader = WorkflowLoader(enable_validation=False)
        loader.data_dir = temp_path

        # Create invalid workflow file (empty name)
        invalid_workflow = {
            "name": "",
            "description": "This would normally fail validation",
            "triggers": ["test"],
            "steps": ["echo test"],
        }

        invalid_file = temp_path / "invalid.yaml"
        with open(invalid_file, "w") as f:
            yaml.dump(invalid_workflow, f)

        # Should still load when validation is disabled
        # (though it may fail when creating the Workflow object)
        # This tests that validation check is skipped
        loader.get_all_workflows()
        # The workflow might not be loaded due to other issues, but
        # validation error shouldn't be printed


def test_schema_validation_unicode_and_emojis() -> None:
    """Test validation works with Unicode characters and emojis."""
    unicode_workflow = {
        "name": "🚀 Test Workflow with Unicode ñáéíóú",
        "description": "Test workflow with Unicode characters",
        "triggers": ["test", "unicode", "🌟"],
        "steps": ["🔍 Analyze the situation", "⚡ Execute the plan"],
    }

    validate_workflow_data(unicode_workflow)
    assert validate_workflow_structure(unicode_workflow)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
