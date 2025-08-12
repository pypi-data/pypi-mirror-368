"""Core CLI commands for vibe workflow execution."""

import sys
from pathlib import Path

import click
from rich.console import Console

from ..analyzer import PromptAnalyzer
from ..config import VibeConfig
from ..orchestrator import WorkflowOrchestrator

console = Console()


def run_workflow(
    prompt: str,
    workflow: str | None = None,
    config_path: str | None = None,
    project_type: str | None = None,
    quiet: bool = False,
) -> None:
    """Run workflow based on prompt analysis."""
    try:
        # Load configuration
        config = VibeConfig.load_from_file(Path(config_path) if config_path else None)

        # Override project type if specified
        if project_type:
            config.project_type = project_type

        # Analyze prompt or use forced workflow
        if workflow:
            workflows = [workflow]
            if not quiet:
                console.print(f"[blue]🎯 Using forced workflow: {workflow}[/blue]")
                console.print()
        else:
            analyzer = PromptAnalyzer(config)
            workflows = analyzer.analyze(prompt, show_analysis=not quiet)

        # Plan workflows and provide guidance
        orchestrator = WorkflowOrchestrator(config)
        result = orchestrator.plan_workflows(workflows, prompt)

        if not result["success"]:
            sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]🛑 Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)


@click.command()
@click.option("--workflow", "-w", help="Force specific workflow")
@click.option("--config", "-c", type=click.Path(exists=True), help="Config file path")
@click.option("--project-type", "-t", help="Override project type detection")
@click.option("--quiet", "-q", is_flag=True, help="Suppress analysis output")
@click.argument("prompt")
def run(
    workflow: str | None,
    config: str | None,
    project_type: str | None,
    quiet: bool,
    prompt: str,
) -> None:
    """Run workflow based on prompt analysis.

    Examples:
        vibe run "analyze the codebase structure"
        vibe run "implement user authentication"
        vibe run --workflow testing "validate everything"

    """
    run_workflow(prompt, workflow, config, project_type, quiet)


@click.command()
@click.option(
    "--project-type",
    "-t",
    help="Project type (python, vue_typescript, generic)",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results in JSON format for MCP",
)
def init(project_type: str | None, output_json: bool = False) -> None:
    """Initialize vibe configuration and provide setup guidance."""
    # Check if .vibe.yaml already exists in current working directory
    vibe_config_path = Path.cwd() / ".vibe.yaml"

    if vibe_config_path.exists():
        if output_json:
            import json

            result = {
                "success": True,
                "already_initialized": True,
                "message": "Vibe project already initialized",
                "config_path": str(vibe_config_path),
                "next_steps": ["vibe check", 'vibe run "what can I do?"'],
            }
            print(json.dumps(result, indent=2))
            return

        console.print("[yellow]📋 Vibe project already initialized![/yellow]")
        console.print()
        console.print("Found existing [blue].vibe.yaml[/blue] file.")
        console.print("To validate your current configuration, run:")
        console.print()
        console.print("  [bold cyan]vibe check[/bold cyan]")
        console.print()
        console.print("To see available workflows for this project:")
        console.print()
        console.print('  [bold cyan]vibe run "what can I do?"[/bold cyan]')
        return

    # Use the init workflow for guidance instead of creating files
    if output_json:
        # For JSON output, we need to capture the workflow result
        try:
            config = VibeConfig.load_from_file()
            if project_type:
                config.project_type = project_type

            orchestrator = WorkflowOrchestrator(config)
            result = orchestrator.plan_workflows(
                ["init"],
                "initialize vibe project",
                show_display=False,
            )

            print(json.dumps(result, indent=2))
        except Exception as e:
            import json

            error_result = {
                "success": False,
                "error": f"Failed to initialize project: {str(e)}",
            }
            print(json.dumps(error_result, indent=2))
            sys.exit(1)
    else:
        run_workflow("initialize vibe project", "init", quiet=False)


@click.command()
@click.argument("prompt", required=True)
@click.option("--config", "-c", "config_path", help="Path to config file")
@click.option(
    "--project-type", "-t", help="Project type (python, vue_typescript, generic)"
)
def guide(
    prompt: str,
    config_path: str | None = None,
    project_type: str | None = None,
) -> None:
    """Get plain text guidance for AI agents (no rich formatting).

    This command outputs structured guidance that AI agents can easily
    parse and execute.

    Examples:
        vibe guide "implement authentication"
        vibe guide "prepare for release"
        vibe guide "fix code quality issues"

    """
    try:
        # Load configuration
        config = VibeConfig.load_from_file(Path(config_path) if config_path else None)

        # Override project type if specified
        if project_type:
            config.project_type = project_type

        # Analyze prompt
        analyzer = PromptAnalyzer(config)
        workflows = analyzer.analyze(prompt, show_analysis=False)

        # Plan workflows
        orchestrator = WorkflowOrchestrator(config)
        result = orchestrator.plan_workflows(workflows, prompt, show_display=False)

        if result["success"]:
            # Output plain text guidance for AI agents
            print(result["guidance"])
        else:
            print("ERROR: Unable to generate workflow guidance")
            sys.exit(1)

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
