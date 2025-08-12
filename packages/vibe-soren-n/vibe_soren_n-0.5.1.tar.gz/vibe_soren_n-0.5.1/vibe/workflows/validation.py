"""JSON Schema validation for YAML workflows."""

from typing import Any

from jsonschema import Draft7Validator, ValidationError

# JSON Schema for workflow YAML files
WORKFLOW_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Vibe Workflow Schema",
    "description": "Schema for validating Vibe workflow YAML files",
    "type": "object",
    "required": ["name", "description", "triggers"],
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200,
            "description": "Unique identifier for the workflow",
        },
        "description": {
            "type": "string",
            "minLength": 1,
            "maxLength": 500,
            "description": "Human-readable description of the workflow",
        },
        "triggers": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
            "minItems": 1,
            "description": "List of patterns that activate this workflow",
        },
        "steps": {
            "type": "array",
            "items": {
                "anyOf": [
                    {"type": "string", "minLength": 1},
                    {
                        "type": "object",
                        "properties": {
                            "step_text": {"type": "string", "minLength": 1},
                            "command": {"type": "string"},
                            "working_dir": {"type": "string"},
                        },
                        "required": ["step_text"],
                    },
                ]
            },
            "minItems": 1,
            "description": "List of guidance steps for the workflow",
        },
        "dependencies": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
            "description": "Optional list of required tools/packages",
        },
        "project_types": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
            "description": "Optional list of project types this applies to",
        },
        "conditions": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
            "description": "Optional list of conditions that must be met",
        },
        # Legacy field support
        "commands": {
            "type": "array",
            "items": {
                "anyOf": [
                    {"type": "string", "minLength": 1},
                    {
                        "type": "object",
                        "properties": {
                            "step_text": {"type": "string", "minLength": 1},
                            "command": {"type": "string"},
                            "working_dir": {"type": "string"},
                        },
                        "required": ["step_text"],
                    },
                ]
            },
            "description": "Legacy field - use 'steps' instead",
        },
        # Metadata fields
        "display_name": {
            "type": "string",
            "description": "Optional display name for UI",
        },
        "category": {
            "type": "string",
            "description": "Optional category for organization",
        },
        "guidance": {
            "type": "string",
            "description": "Optional additional guidance text",
        },
    },
    "additionalProperties": False,
    # Ensure either steps or commands is provided (but prefer steps)
    "anyOf": [{"required": ["steps"]}, {"required": ["commands"]}],
}


class WorkflowValidationError(Exception):
    """Exception raised when workflow validation fails."""

    def __init__(self, message: str, errors: list[ValidationError]) -> None:
        super().__init__(message)
        self.errors = errors


def validate_workflow_data(data: dict[str, Any]) -> None:
    """Validate workflow data against the JSON schema.

    Args:
        data: The workflow data to validate

    Raises:
        WorkflowValidationError: If validation fails
    """
    validator = Draft7Validator(WORKFLOW_SCHEMA)
    errors = list(validator.iter_errors(data))

    if errors:
        error_messages = []
        for error in errors:
            # Create a readable error message
            path = (
                " -> ".join(str(p) for p in error.absolute_path)
                if error.absolute_path
                else "root"
            )
            error_messages.append(f"{path}: {error.message}")

        raise WorkflowValidationError(
            "Workflow validation failed:\n"
            + "\n".join(f"  - {msg}" for msg in error_messages),
            errors,
        )


def validate_workflow_structure(data: dict[str, Any]) -> bool:
    """Check if workflow data is structurally valid without raising exceptions.

    Args:
        data: The workflow data to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        validate_workflow_data(data)
        return True
    except WorkflowValidationError:
        return False


def get_validation_errors(data: dict[str, Any]) -> list[str]:
    """Get a list of validation error messages for workflow data.

    Args:
        data: The workflow data to validate

    Returns:
        List of human-readable error messages
    """
    try:
        validate_workflow_data(data)
        return []
    except WorkflowValidationError as e:
        return [str(error) for error in e.errors]


def create_example_workflow() -> dict[str, Any]:
    """Create an example workflow that passes validation.

    Returns:
        A valid workflow dictionary
    """
    return {
        "name": "example_workflow",
        "description": "An example workflow demonstrating the schema",
        "triggers": ["example", "demo"],
        "steps": [
            "Step 1: Analyze the requirements",
            "Step 2: Plan the implementation",
            "Step 3: Execute the plan",
            "Step 4: Validate the results",
        ],
        "dependencies": ["python", "git"],
        "project_types": ["python", "web"],
        "conditions": ["git_repo_exists"],
    }
