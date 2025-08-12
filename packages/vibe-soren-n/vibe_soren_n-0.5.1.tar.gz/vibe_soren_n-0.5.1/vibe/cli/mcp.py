"""MCP (Model Context Protocol) commands for step-by-step workflow execution."""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import click
import yaml

from ..config import VibeConfig
from ..orchestrator import WorkflowOrchestrator


@click.group()
def mcp() -> None:
    """MCP server commands for step-by-step workflow execution.

    These commands are designed to be called by MCP servers to provide
    token-efficient workflow orchestration for AI agents.
    """
    pass


@mcp.command("start")
@click.argument("prompt")
@click.option("--config", "-c", type=click.Path(exists=True), help="Config file path")
@click.option("--project-type", "-t", help="Override project type detection")
def mcp_start(prompt: str, config: str | None, project_type: str | None) -> None:
    """Start a new workflow session for step-by-step execution.

    Args:
        prompt: The original prompt that triggered workflows
        config: Optional path to configuration file
        project_type: Optional override for project type detection

    Returns JSON with session info and first step.

    """
    try:
        # Load configuration
        config_obj = VibeConfig.load_from_file(Path(config) if config else None)

        # Override project type if specified
        if project_type:
            config_obj.project_type = project_type

        # Start session
        orchestrator = WorkflowOrchestrator(config_obj)
        result = orchestrator.start_session(prompt)

        # Output JSON
        print(json.dumps(result, indent=2))

        if not result["success"]:
            sys.exit(1)

    except Exception as e:
        error_result = {"success": False, "error": f"Failed to start session: {str(e)}"}
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


@mcp.command("status")
@click.argument("session_id")
def mcp_status(session_id: str) -> None:
    """Get current status of a workflow session.

    Args:
        session_id: ID of the session to check

    Returns JSON with session status and current step.

    """
    try:
        # Use default config for session operations
        config = VibeConfig.load_from_file()
        orchestrator = WorkflowOrchestrator(config)
        result = orchestrator.get_session_status(session_id)

        # Output JSON
        print(json.dumps(result, indent=2))

        if not result["success"]:
            sys.exit(1)

    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Failed to get session status: {str(e)}",
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


@mcp.command("next")
@click.argument("session_id")
def mcp_next(session_id: str) -> None:
    """Mark current step as complete and advance to next step.

    Args:
        session_id: ID of the session to advance

    Returns JSON with next step info or completion status.

    """
    try:
        # Use default config for session operations
        config = VibeConfig.load_from_file()
        orchestrator = WorkflowOrchestrator(config)
        result = orchestrator.advance_session(session_id)

        # Output JSON
        print(json.dumps(result, indent=2))

        if not result["success"]:
            sys.exit(1)

    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Failed to advance session: {str(e)}",
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


@mcp.command("break")
@click.argument("session_id")
def mcp_break(session_id: str) -> None:
    """Break out of current workflow and return to parent workflow.

    Args:
        session_id: ID of the session

    Returns JSON with parent workflow step info.

    """
    try:
        # Use default config for session operations
        config = VibeConfig.load_from_file()
        orchestrator = WorkflowOrchestrator(config)
        result = orchestrator.break_session(session_id)

        # Output JSON
        print(json.dumps(result, indent=2))

        if not result["success"]:
            sys.exit(1)

    except Exception as e:
        error_result = {"success": False, "error": f"Failed to break session: {str(e)}"}
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


@mcp.command("back")
@click.argument("session_id")
def mcp_back(session_id: str) -> None:
    """Go back to the previous step in the current workflow.

    Args:
        session_id: ID of the session

    Returns JSON with previous step info.

    """
    try:
        # Use default config for session operations
        config = VibeConfig.load_from_file()
        orchestrator = WorkflowOrchestrator(config)
        result = orchestrator.back_session(session_id)

        # Output JSON
        print(json.dumps(result, indent=2))

        if not result["success"]:
            sys.exit(1)

    except Exception as e:
        error_result = {"success": False, "error": f"Failed to go back: {str(e)}"}
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


@mcp.command("restart")
@click.argument("session_id")
def mcp_restart(session_id: str) -> None:
    """Restart the session from the beginning.

    Args:
        session_id: ID of the session to restart

    Returns JSON with first step info.

    """
    try:
        # Use default config for session operations
        config = VibeConfig.load_from_file()
        orchestrator = WorkflowOrchestrator(config)
        result = orchestrator.restart_session(session_id)

        # Output JSON
        print(json.dumps(result, indent=2))

        if not result["success"]:
            sys.exit(1)

    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Failed to restart session: {str(e)}",
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


@mcp.command("list")
def mcp_list() -> None:
    """List all active workflow sessions.

    Returns JSON with list of active sessions.
    """
    try:
        # Use default config for session operations
        config = VibeConfig.load_from_file()
        orchestrator = WorkflowOrchestrator(config)
        result = orchestrator.list_sessions()

        # Output JSON
        print(json.dumps(result, indent=2))

        if not result["success"]:
            sys.exit(1)

    except Exception as e:
        error_result = {"success": False, "error": f"Failed to list sessions: {str(e)}"}
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


@mcp.command("init")
@click.option(
    "--project-type",
    "-t",
    help="Project type (python, vue_typescript, generic)",
)
def mcp_init(project_type: str | None) -> None:
    """Initialize vibe project configuration with JSON output for MCP.

    Args:
        project_type: Optional project type override

    Returns JSON with initialization result.
    """
    try:
        from pathlib import Path

        # Check if .vibe.yaml already exists
        vibe_config_path = Path.cwd() / ".vibe.yaml"

        if vibe_config_path.exists():
            result = {
                "success": True,
                "already_initialized": True,
                "message": "Vibe project already initialized",
                "config_path": str(vibe_config_path),
                "next_steps": ["vibe check", 'vibe run "what can I do?"'],
            }
        else:
            # Initialize new project using the init workflow
            config = VibeConfig.load_from_file()
            if project_type:
                config.project_type = project_type

            orchestrator = WorkflowOrchestrator(config)
            result = orchestrator.plan_workflows(
                ["init"], "initialize vibe project", show_display=False
            )

        print(json.dumps(result, indent=2))

        if not result.get("success", True):
            sys.exit(1)

    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Failed to initialize project: {str(e)}",
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)


@mcp.command("check")
def mcp_check() -> None:
    """Validate vibe environment and configuration with JSON output for MCP.

    Returns JSON with validation results.
    """
    try:
        # Collect results for JSON output
        check_results: dict[str, Any] = {
            "success": True,
            "issues_found": [],
            "checks": {
                "configuration": {},
                "environment": {},
                "tools": {},
                "github_integration": {},
            },
        }

        issues_found: list[str] = []

        # Check 1: Configuration file validation
        vibe_config_path = Path.cwd() / ".vibe.yaml"

        if not vibe_config_path.exists():
            check_results["checks"]["configuration"]["config_file"] = {
                "status": "missing",
                "message": ".vibe.yaml not found",
            }
            issues_found.append("missing_config")
        else:
            check_results["checks"]["configuration"]["config_file"] = {
                "status": "found",
                "message": ".vibe.yaml found",
            }

            # Validate config content
            try:
                with open(vibe_config_path) as f:
                    config_data = yaml.safe_load(f) or {}

                # Check protocol version
                protocol_version = config_data.get("protocol_version")
                current_version = 1

                if not protocol_version:
                    check_results["checks"]["configuration"]["protocol_version"] = {
                        "status": "missing",
                        "message": "Protocol version missing",
                    }
                    issues_found.append("missing_protocol_version")
                else:
                    try:
                        if isinstance(protocol_version, str):
                            normalized_version = int(float(protocol_version))
                        else:
                            normalized_version = int(protocol_version)

                        if normalized_version != current_version:
                            check_results["checks"]["configuration"][
                                "protocol_version"
                            ] = {
                                "status": "outdated",
                                "current": normalized_version,
                                "expected": current_version,
                                "message": (
                                    f"Protocol version {protocol_version} "
                                    f"!= current {current_version}"
                                ),
                            }
                            issues_found.append("outdated_protocol")
                        else:
                            check_results["checks"]["configuration"][
                                "protocol_version"
                            ] = {
                                "status": "current",
                                "version": protocol_version,
                                "message": (
                                    f"Protocol version {protocol_version} (current)"
                                ),
                            }
                    except (ValueError, TypeError):
                        check_results["checks"]["configuration"]["protocol_version"] = {
                            "status": "invalid",
                            "value": protocol_version,
                            "message": (
                                f"Invalid protocol version format: {protocol_version}"
                            ),
                        }
                        issues_found.append("invalid_protocol_version")

                # Check project type
                if "project_type" not in config_data:
                    check_results["checks"]["configuration"]["project_type"] = {
                        "status": "missing",
                        "message": "Project type missing",
                    }
                    issues_found.append("missing_project_type")
                else:
                    check_results["checks"]["configuration"]["project_type"] = {
                        "status": "found",
                        "value": config_data["project_type"],
                        "message": f"Project type: {config_data['project_type']}",
                    }

            except yaml.YAMLError as e:
                check_results["checks"]["configuration"]["yaml_syntax"] = {
                    "status": "invalid",
                    "error": str(e),
                    "message": f"Invalid YAML syntax: {e}",
                }
                issues_found.append("invalid_yaml")
            except Exception as e:
                check_results["checks"]["configuration"]["read_error"] = {
                    "status": "error",
                    "error": str(e),
                    "message": f"Error reading config: {e}",
                }
                issues_found.append("config_read_error")

        # Check 2: Environment validation
        check_results["checks"]["environment"]["python"] = {}
        try:
            result = subprocess.run(
                ["python", "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                check_results["checks"]["environment"]["python"] = {
                    "status": "found",
                    "version": result.stdout.strip(),
                    "message": f"Python: {result.stdout.strip()}",
                }
            else:
                check_results["checks"]["environment"]["python"] = {
                    "status": "missing",
                    "message": "Python not available",
                }
                issues_found.append("missing_python")
        except FileNotFoundError:
            check_results["checks"]["environment"]["python"] = {
                "status": "not_found",
                "message": "Python not found in PATH",
            }
            issues_found.append("missing_python")

        # Check vibe CLI
        vibe_path = shutil.which("vibe")
        if vibe_path:
            check_results["checks"]["environment"]["vibe_cli"] = {
                "status": "found",
                "path": vibe_path,
                "message": f"Vibe CLI: {vibe_path}",
            }
        else:
            check_results["checks"]["environment"]["vibe_cli"] = {
                "status": "missing",
                "message": "Vibe CLI not in PATH",
            }
            issues_found.append("missing_vibe_cli")

        # Check 3: GitHub AI Integration
        github_dir = Path.cwd() / ".github"
        if github_dir.exists():
            check_results["checks"]["github_integration"]["github_dir"] = {
                "status": "found",
                "message": ".github directory found",
            }

            # Check for copilot-instructions.md
            instructions_file = github_dir / "copilot-instructions.md"
            if instructions_file.exists():
                check_results["checks"]["github_integration"][
                    "copilot_instructions"
                ] = {
                    "status": "found",
                    "message": "copilot-instructions.md found",
                }
            else:
                check_results["checks"]["github_integration"][
                    "copilot_instructions"
                ] = {
                    "status": "missing",
                    "message": "copilot-instructions.md not found",
                }
                issues_found.append("missing_copilot_instructions")

            # Check for chatmodes directory
            chatmodes_dir = github_dir / "chatmodes"
            if chatmodes_dir.exists():
                check_results["checks"]["github_integration"]["chatmodes_dir"] = {
                    "status": "found",
                    "message": ".github/chatmodes directory found",
                }

                chatmode_file = chatmodes_dir / "vibe-agent.chatmode.md"
                if chatmode_file.exists():
                    check_results["checks"]["github_integration"]["chatmode_file"] = {
                        "status": "found",
                        "message": "vibe-agent.chatmode.md found",
                    }
                else:
                    check_results["checks"]["github_integration"]["chatmode_file"] = {
                        "status": "missing",
                        "message": "vibe-agent.chatmode.md not found",
                    }
                    issues_found.append("missing_chatmode_file")
            else:
                check_results["checks"]["github_integration"]["chatmodes_dir"] = {
                    "status": "missing",
                    "message": ".github/chatmodes directory not found",
                }
                issues_found.append("missing_chatmodes_dir")
        else:
            check_results["checks"]["github_integration"]["github_dir"] = {
                "status": "missing",
                "message": ".github directory not found",
            }
            issues_found.append("missing_github_dir")

        # Final results
        check_results["issues_found"] = issues_found
        check_results["success"] = len(issues_found) == 0

        print(json.dumps(check_results, indent=2))

        if not check_results["success"]:
            sys.exit(1)

    except Exception as e:
        error_result = {
            "success": False,
            "error": f"Failed to validate environment: {str(e)}",
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)
