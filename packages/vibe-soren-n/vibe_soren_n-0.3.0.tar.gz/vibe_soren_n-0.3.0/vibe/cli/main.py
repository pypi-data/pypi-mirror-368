"""Main CLI entry point for vibe."""

import sys

import click
from rich.console import Console

from .. import __version__
from .commands import guide, init, run
from .mcp import mcp
from .validation import check, config_info, list_workflows
from .workflows import workflows

console = Console()


@click.group()
@click.option("--version", "-v", is_flag=True, help="Show version and exit")
@click.pass_context
def cli(ctx: click.Context, version: bool) -> None:
    """Vibe: Intelligent workflow orchestrator for vibe coding.

    Analyzes your prompts and executes appropriate development workflows.
    """
    if version:
        console.print(f"vibe version {__version__}")
        sys.exit(0)


# Add commands to the main CLI group
cli.add_command(run)
cli.add_command(init)
cli.add_command(guide)
cli.add_command(check)
cli.add_command(config_info)
cli.add_command(list_workflows)

# Add command groups
cli.add_command(workflows)
cli.add_command(mcp)


def main() -> None:
    """Main entry point with smart command detection."""
    args = sys.argv[1:]

    # If no args, show help
    if not args:
        cli(["--help"])
        return

    # If first arg is a known command, use normal CLI
    known_commands = [
        "run",
        "init",
        "check",
        "config-info",
        "list-workflows",
        "guide",
        "workflows",
        "mcp",
    ]
    if args[0] in known_commands or args[0].startswith("-"):
        cli()
        return

    # Otherwise, treat as a prompt for run command
    # Extract options first
    prompt_args = []
    options = []
    i = 0
    while i < len(args):
        if args[i].startswith("--"):
            options.append(args[i])
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                options.append(args[i + 1])
                i += 2
            else:
                i += 1
        elif args[i].startswith("-") and args[i] != "-":
            options.append(args[i])
            if i + 1 < len(args) and not args[i + 1].startswith("-"):
                options.append(args[i + 1])
                i += 2
            else:
                i += 1
        else:
            prompt_args.append(args[i])
            i += 1

    # Join all non-option args as prompt
    prompt = " ".join(prompt_args)

    # Run the command
    sys.argv = ["vibe", "run"] + options + [prompt]
    cli()


if __name__ == "__main__":
    main()
