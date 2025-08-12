"""Workflow management commands for vibe."""

import sys
from pathlib import Path

import click
from rich.console import Console

from ..workflows.quality import (
    format_workflow_yamls,
    validate_workflow_yamls,
)

console = Console()


@click.group()
def workflows() -> None:
    """Operations for YAML-defined workflows (validate/format)."""


@workflows.command("validate")
@click.option(
    "--path",
    "path",
    type=click.Path(exists=True),
    default=None,
    help="Directory to scan (defaults to built-in workflows directory)",
)
def workflows_validate(path: Path | None) -> None:
    """Validate all YAML workflow files for schema and quality issues."""
    issues = validate_workflow_yamls(path)
    if not issues:
        console.print("[green]✅ All workflow YAML files look good[/green]")
        return

    console.print("[yellow]⚠️ Found workflow YAML issues:[/yellow]")
    for issue in issues:
        console.print(f" - {issue}")
    sys.exit(1)


@workflows.command("format")
@click.option(
    "--write/--no-write",
    default=False,
    help="Write normalized YAML back to files (default: dry-run)",
)
@click.option(
    "--path",
    "path",
    type=click.Path(exists=True),
    default=None,
    help="Directory to scan (defaults to built-in workflows directory)",
)
def workflows_format(write: bool, path: Path | None) -> None:
    """Normalize and optionally rewrite YAML workflow files for consistency."""
    changes = format_workflow_yamls(path, write=write)
    if not changes:
        console.print("[green]✅ No formatting changes needed[/green]")
        return

    console.print(
        "[bold]🧹 Workflow YAML normalization preview[/bold]"
        if not write
        else "[bold]🧹 Applied workflow YAML normalization[/bold]"
    )
    for c in changes:
        console.print(f" - {c}")
    if not write:
        console.print("\n[dim]Tip: re-run with --write to apply these changes[/dim]")
