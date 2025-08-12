"""Environment validation and configuration checking for vibe."""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import click
import yaml
from rich.console import Console

from ..config import VibeConfig

console = Console()


def _get_migration_guide(from_version: int | str, to_version: int) -> str:
    """Get version-specific migration guidance."""
    # Convert string versions to int for comparison
    if isinstance(from_version, str):
        try:
            # Handle string versions like "1.0" -> 1, "0.9" -> 0
            from_version = int(float(from_version))
        except (ValueError, TypeError):
            from_version = 0

    migration_guides = {
        # Version migrations (from_version -> to_version)
        (0, 1): "Update to protocol_version: 1 and add VS Code chat mode support",
        # Future migrations can be added here
    }

    guide = migration_guides.get((from_version, to_version))
    if guide:
        return f"Migration: {guide}"
    else:
        return f"Update to 'protocol_version: {to_version}' in .vibe.yaml"


@click.command()
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results in JSON format for MCP",
)
def check(output_json: bool = False) -> None:
    """Validate vibe environment and configuration.

    Checks:
    - Environment compatibility (required tools, dependencies)
    - .vibe.yaml configuration validity and protocol version
    - Workflow dependencies and tool availability
    """
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

    if not output_json:
        console.print("[bold]🔍 Vibe Environment & Configuration Check[/bold]")
        console.print("=" * 45)
        console.print()

    issues_found: list[str] = []

    # Check 1: Configuration file validation
    if not output_json:
        console.print("[bold]📁 Configuration Status:[/bold]")
    vibe_config_path = Path.cwd() / ".vibe.yaml"

    if not vibe_config_path.exists():
        if not output_json:
            console.print("❌ .vibe.yaml not found")
        check_results["checks"]["configuration"]["config_file"] = {
            "status": "missing",
            "message": ".vibe.yaml not found",
        }
        issues_found.append("missing_config")
        if not output_json:
            console.print(
                "   💡 [dim]Create .vibe.yaml with: "
                'protocol_version: 1 and project_type: "auto"[/dim]'
            )
    else:
        if not output_json:
            console.print("✅ .vibe.yaml found")
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
            current_version = 1  # Current supported version (integer)

            if not protocol_version:
                console.print("⚠️  Protocol version missing")
                issues_found.append("missing_protocol_version")
                console.print(
                    "   💡 [dim]Add 'protocol_version: 1' to .vibe.yaml[/dim]"
                )
            else:
                # Normalize protocol version to integer
                try:
                    if isinstance(protocol_version, str):
                        # Handle string versions like "1.0" -> 1
                        normalized_version = int(float(protocol_version))
                    else:
                        normalized_version = int(protocol_version)

                    if normalized_version != current_version:
                        console.print(
                            f"⚠️  Protocol version {protocol_version} "
                            f"!= current {current_version}"
                        )
                        issues_found.append("outdated_protocol")

                        # Provide version-specific migration guidance
                        migration_guide = _get_migration_guide(
                            normalized_version, current_version
                        )
                        console.print(f"   💡 [dim]{migration_guide}[/dim]")
                    else:
                        console.print(
                            f"✅ Protocol version {protocol_version} (current)"
                        )
                except (ValueError, TypeError):
                    console.print(
                        f"⚠️  Invalid protocol version format: {protocol_version}"
                    )
                    issues_found.append("invalid_protocol_version")
                    console.print(
                        "   💡 [dim]Use integer format: protocol_version: 1[/dim]"
                    )

            # Check project type
            if "project_type" not in config_data:
                console.print("⚠️  Project type missing")
                issues_found.append("missing_project_type")
                console.print(
                    "   💡 [dim]Add 'project_type: \"auto\"' "
                    "or specific type to .vibe.yaml[/dim]"
                )
            else:
                console.print(f"✅ Project type: {config_data['project_type']}")

        except yaml.YAMLError as e:
            console.print(f"❌ Invalid YAML syntax: {e}")
            issues_found.append("invalid_yaml")
        except Exception as e:
            console.print(f"❌ Error reading config: {e}")
            issues_found.append("config_read_error")

    console.print()

    # Check 2: Environment validation
    console.print("[bold]🔧 Environment Compatibility:[/bold]")

    # Check Python
    try:
        result = subprocess.run(["python", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"✅ Python: {result.stdout.strip()}")
        else:
            console.print("❌ Python not available")
            issues_found.append("missing_python")
            console.print("   💡 [dim]Install Python 3.13+ from python.org[/dim]")
    except FileNotFoundError:
        console.print("❌ Python not found in PATH")
        issues_found.append("missing_python")
        console.print("   💡 [dim]Install Python 3.13+ and add to PATH[/dim]")

    # Check vibe CLI
    vibe_path = shutil.which("vibe")
    if vibe_path:
        console.print(f"✅ Vibe CLI: {vibe_path}")
    else:
        console.print("❌ Vibe CLI not in PATH")
        issues_found.append("missing_vibe_cli")
        console.print("   💡 [dim]Install vibe package: pip install vibe[/dim]")

    console.print()

    # Check 3: Workflow-specific tool validation
    console.print("[bold]🛠️  Workflow Tool Dependencies:[/bold]")

    # Load configuration to get available workflows
    try:
        config = VibeConfig.load_from_file()
        project_type = config.detect_project_type()

        # Collect all unique commands from workflow steps
        workflow_commands = set()

        # Get built-in workflows
        for workflow_name, workflow in config.workflows.items():
            for step in workflow.steps:
                # Extract tool commands from workflow steps
                # (first word of each step if it's a command)
                if step and not step.strip().startswith("echo"):
                    # Handle complex commands like "python -m pytest"
                    step_parts = step.strip().split()
                    if step_parts:
                        base_cmd = step_parts[0]
                        # Handle special cases
                        if (
                            base_cmd == "python"
                            and len(step_parts) > 2
                            and step_parts[1] == "-m"
                        ):
                            workflow_commands.add(
                                step_parts[2]
                            )  # e.g., pytest from "python -m pytest"
                        elif base_cmd not in [
                            "if",
                            "grep",
                            "find",
                            "ls",
                            "echo",
                            "which",
                        ]:
                            workflow_commands.add(base_cmd)

        # Get project-specific workflows
        project_config = config.project_types.get(project_type)
        if project_config:
            for workflow_name, workflow in project_config.workflows.items():
                for step in workflow.steps:
                    if step and not step.strip().startswith("echo"):
                        step_parts = step.strip().split()
                        if step_parts:
                            base_cmd = step_parts[0]
                            if (
                                base_cmd == "python"
                                and len(step_parts) > 2
                                and step_parts[1] == "-m"
                            ):
                                workflow_commands.add(step_parts[2])
                            elif base_cmd not in [
                                "if",
                                "grep",
                                "find",
                                "ls",
                                "echo",
                                "which",
                            ]:
                                workflow_commands.add(base_cmd)

        # Common tools to always check
        standard_tools = [
            ("git", "Git version control", "Install Git from git-scm.com"),
            ("python", "Python runtime", "Install Python 3.13+ from python.org"),
        ]

        # Project-specific tools based on detected type
        project_specific_tools = {
            "python": [
                ("pytest", "Python testing framework", "Install: pip install pytest"),
                ("ruff", "Python linter/formatter", "Install: pip install ruff"),
                ("black", "Python code formatter", "Install: pip install black"),
                ("mypy", "Python type checker", "Install: pip install mypy"),
            ],
            "vue_typescript": [
                ("node", "Node.js runtime", "Install Node.js from nodejs.org"),
                ("npm", "Node package manager", "Install Node.js (includes npm)"),
                (
                    "bun",
                    "Bun package manager",
                    "Install: curl -fsSL https://bun.sh/install | bash",
                ),
                ("vue", "Vue CLI", "Install: npm install -g @vue/cli"),
                ("tsc", "TypeScript compiler", "Install: npm install -g typescript"),
            ],
            "generic": [
                ("node", "Node.js runtime", "Install Node.js from nodejs.org"),
                ("npm", "Node package manager", "Install Node.js (includes npm)"),
            ],
        }

        # Combine standard tools with project-specific ones
        tools_to_check = standard_tools[:]
        if project_type in project_specific_tools:
            tools_to_check.extend(project_specific_tools[project_type])

        # Add workflow-detected commands
        for cmd in sorted(workflow_commands):
            if cmd not in [tool[0] for tool in tools_to_check]:
                tools_to_check.append(
                    (cmd, f"{cmd} command", f"Install {cmd} as required by workflows")
                )

        # Check each tool
        for tool, description, install_guide in tools_to_check:
            tool_path = shutil.which(tool)
            if tool_path:
                try:
                    result = subprocess.run(
                        [tool, "--version"], capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0 and result.stdout:
                        version_info = result.stdout.strip().split("\n")[0]
                        console.print(f"✅ {description}: {version_info}")
                    else:
                        console.print(f"✅ {description}: available")
                except Exception:
                    console.print(f"✅ {description}: available")
            else:
                console.print(f"⚠️  {description}: not found")
                console.print(f"   💡 [dim]{install_guide}[/dim]")
                if tool in ["python", "git"]:  # Critical tools
                    issues_found.append(f"missing_{tool}")

    except Exception as e:
        console.print(f"⚠️  Could not validate workflow tools: {e}")
        console.print("   💡 [dim]Ensure .vibe.yaml is valid and accessible[/dim]")

    console.print()

    # Check 4: GitHub AI Integration (if applicable)
    console.print("[bold]🤖 GitHub AI Integration:[/bold]")

    github_dir = Path.cwd() / ".github"
    if github_dir.exists():
        console.print("✅ .github directory found")

        # Check for copilot-instructions.md
        instructions_file = github_dir / "copilot-instructions.md"
        if instructions_file.exists():
            console.print("✅ copilot-instructions.md found")
        else:
            console.print("⚠️  copilot-instructions.md not found")
            issues_found.append("missing_copilot_instructions")
            console.print(
                "   💡 [dim]Create copilot-instructions.md in .github/ "
                "for AI agent guidance[/dim]"
            )

        # Check for chatmodes directory and vibe-agent.chatmode.md
        chatmodes_dir = github_dir / "chatmodes"
        if chatmodes_dir.exists():
            console.print("✅ .github/chatmodes directory found")

            chatmode_file = chatmodes_dir / "vibe-agent.chatmode.md"
            if chatmode_file.exists():
                console.print("✅ vibe-agent.chatmode.md found")
            else:
                console.print("⚠️  vibe-agent.chatmode.md not found")
                issues_found.append("missing_chatmode_file")
                console.print(
                    "   💡 [dim]Create vibe-agent.chatmode.md in "
                    ".github/chatmodes/ for VS Code chat mode[/dim]"
                )
        else:
            console.print("⚠️  .github/chatmodes directory not found")
            issues_found.append("missing_chatmodes_dir")
            console.print(
                "   💡 [dim]Create .github/chatmodes/ directory "
                "and vibe-agent.chatmode.md[/dim]"
            )
    else:
        console.print("⚠️  .github directory not found")
        issues_found.append("missing_github_dir")
        console.print(
            "   💡 [dim]Create .github directory with "
            "copilot-instructions.md and chatmodes/[/dim]"
        )

    console.print()

    # Summary
    if issues_found:
        console.print(
            f"[yellow]⚠️  Found {len(issues_found)} issue(s) that may affect "
            "vibe functionality[/yellow]"
        )
        console.print()
        console.print("[bold]🔧 Quick Fix Commands:[/bold]")

        if "missing_config" in issues_found:
            console.print("• Create .vibe.yaml with minimum content:")
            console.print("  [cyan]protocol_version: 1[/cyan]")
            console.print('  [cyan]project_type: "auto"[/cyan]')
            console.print(
                '• [cyan]vibe guide "setup vibe project configuration"[/cyan] '
                "- Get detailed setup steps"
            )
        if (
            "missing_protocol_version" in issues_found
            or "outdated_protocol" in issues_found
            or "invalid_protocol_version" in issues_found
        ):
            console.print(
                "• Edit .vibe.yaml and add/update: [cyan]protocol_version: 1[/cyan]"
            )
            console.print(
                '• [cyan]vibe guide "migrate protocol version"[/cyan] - Get '
                "migration guidance"
            )
        if "missing_project_type" in issues_found:
            console.print(
                '• Edit .vibe.yaml and add: [cyan]project_type: "auto"[/cyan]'
            )
        if "missing_python" in issues_found:
            console.print("• Install Python 3.13+ from [cyan]https://python.org[/cyan]")
            console.print(
                '• [cyan]vibe guide "setup python environment"[/cyan] - Get '
                "environment setup steps"
            )
        if "missing_vibe_cli" in issues_found:
            console.print("• Install vibe: [cyan]pip install vibe[/cyan]")
            console.print(
                '• [cyan]vibe guide "install vibe cli"[/cyan] - Get '
                "installation guidance"
            )

        # GitHub AI integration suggestions
        if (
            "missing_github_dir" in issues_found
            or "missing_copilot_instructions" in issues_found
            or "missing_chatmodes_dir" in issues_found
            or "missing_chatmode_file" in issues_found
        ):
            console.print(
                '• [cyan]vibe guide "setup github ai integration"[/cyan] - Get '
                "GitHub AI setup steps"
            )
            console.print(
                "• Create .github/copilot-instructions.md for AI agent guidance"
            )
            console.print(
                "• Create .github/chatmodes/vibe-agent.chatmode.md "
                "for VS Code integration"
            )

        console.print()
        console.print(
            'For detailed setup guidance: [cyan]vibe guide "setup vibe project"[/cyan]'
        )
        console.print("Run [cyan]vibe check[/cyan] again after applying fixes.")
    else:
        console.print("[green]✅ All checks passed! Vibe is ready for use.[/green]")
        console.print()
        console.print("Next steps:")
        console.print(
            '• [cyan]vibe run "what should I do?"[/cyan] - Get workflow recommendations'
        )
        console.print("• [cyan]vibe list-workflows[/cyan] - See available workflows")
        console.print(
            '• [cyan]vibe guide "setup development workflow"[/cyan] '
            "- Get development guidance"
        )
        console.print(
            '• [cyan]vibe guide "optimize vibe configuration"[/cyan] '
            "- Get configuration tips"
        )

    # Output JSON if requested
    if output_json:
        check_results["issues_found"] = issues_found
        check_results["success"] = len(issues_found) == 0
        import json

        print(json.dumps(check_results, indent=2))


@click.command("config-info")
def config_info() -> None:
    """Show current configuration information."""
    try:
        config = VibeConfig.load_from_file()
        project_type = config.detect_project_type()

        console.print("[bold]Vibe Configuration[/bold]")
        console.print(f"Project Type: [blue]{project_type}[/blue]")
        console.print(
            f"Config Source: [blue]{config._find_config_file() or 'defaults'}[/blue]"
        )

        console.print("\n[bold]Available Workflows:[/bold]")
        for name, workflow_config in config.workflows.items():
            console.print(f"  [green]{name}[/green]: {workflow_config.description}")

        # Show project-specific workflows
        project_config = config.project_types.get(project_type)
        if project_config and project_config.workflows:
            console.print("\n[bold]Project-Specific Workflows:[/bold]")
            for name, workflow_config in project_config.workflows.items():
                steps = workflow_config.steps or ["(no steps)"]
                console.print(f"  [cyan]{name}[/cyan]: {len(steps)} steps")

    except Exception as e:
        console.print(f"[red]❌ Error loading configuration: {e}[/red]")
        sys.exit(1)


@click.command("list-workflows")
@click.argument("workflows", nargs=-1)
def list_workflows(workflows: tuple[str, ...]) -> None:
    """List available workflows and their triggers."""
    try:
        config = VibeConfig.load_from_file()

        console.print("[bold]Available Workflows:[/bold]\n")

        target_workflows = workflows if workflows else config.workflows.keys()

        for workflow_name in target_workflows:
            workflow_config = config.workflows.get(workflow_name)
            if not workflow_config:
                console.print(f"[red]❌ Unknown workflow: {workflow_name}[/red]")
                continue

            console.print(f"[bold green]{workflow_name}[/bold green]")
            console.print(f"  {workflow_config.description}")

            if workflow_config.triggers:
                triggers_str = ", ".join(workflow_config.triggers)
                console.print(f"  [dim]Triggers: {triggers_str}[/dim]")

            if workflow_config.steps:
                console.print(
                    f"  [dim]Steps: {len(workflow_config.steps)} configured[/dim]"
                )

            console.print()

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)
