"""Generate CLI documentation command."""

from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from gira.utils.console import console
from gira.utils.docs_generator import (
    generate_agent_docs,
    generate_all_docs,
    generate_cli_docs,
    generate_workflow_docs,
)
from gira.utils.project import get_gira_root
from gira.utils.project_context import gather_project_context


def generate(
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output", "-o",
            help="Output file path for the generated documentation (default: docs/cli-reference/)",
            exists=False,
            dir_okay=False,
            writable=True,
            resolve_path=True
        )
    ] = None,
    doc_type: Annotated[
        str,
        typer.Option(
            "--type",
            help="Type of documentation to generate (cli, agents, workflow, all)"
        )
    ] = "cli",
    command: Annotated[
        Optional[str],
        typer.Option(
            "--command", "-c",
            help="Generate documentation for a specific command (e.g., 'ticket create')"
        )
    ] = None,
    template: Annotated[
        str,
        typer.Option(
            "--template", "-t",
            help="Template to use for documentation generation"
        )
    ] = "cli_reference.md.j2",
    format: Annotated[
        str,
        typer.Option(
            "--format", "-f",
            help="Output format (currently only markdown is supported)"
        )
    ] = "markdown",
) -> None:
    """
    Generate documentation for Gira including CLI reference, AI agent guides, and workflow documentation.

    This command uses the documentation generator script to create
    comprehensive documentation based on the specified type.

    Documentation Types:
        - cli: Command line interface reference (default)
        - agents: AI agent documentation (Claude, Gemini, etc.)
        - workflow: Workflow guides (Kanban, Scrum, etc.)
        - all: Generate all documentation types

    Examples:
        # Generate full CLI reference (default)
        gira docs generate

        # Generate AI agent documentation
        gira docs generate --type agents

        # Generate workflow documentation
        gira docs generate --type workflow

        # Generate all documentation types
        gira docs generate --type all

        # Generate documentation for a specific command
        gira docs generate --command "ticket create"

        # Save to a specific file
        gira docs generate --output docs/cli-reference.md

        # Use a different template
        gira docs generate --template command.md.j2 --command "epic show"
    """
    try:
        # Get project root
        project_root = get_gira_root()
        if not project_root:
            # Try current directory as fallback
            project_root = Path.cwd()

        # Determine default output path if not specified
        if not output:
            if doc_type == "agents":
                output = project_root / ".gira" / "docs" / "CLAUDE.md"
            elif doc_type == "workflow":
                output = project_root / ".gira" / "docs" / "WORKFLOW.md"
            elif doc_type == "all":
                # For 'all', we'll use a directory instead of a single file
                output = project_root / ".gira" / "docs"
            else:  # cli
                if command:
                    # For individual commands, use the commands subdirectory
                    command_name = command.replace(" ", "-").lower()
                    if template == "command.md.j2":
                        output = project_root / "docs" / "cli-reference" / "commands" / f"{command_name}.md"
                    else:
                        output = project_root / "docs" / "cli-reference" / f"{command_name}.md"
                else:
                    # For full reference, use the main cli-reference.md
                    output = project_root / "docs" / "cli-reference" / "cli-reference.md"

        # Validate doc_type
        valid_types = ["cli", "agents", "workflow", "all"]
        if doc_type not in valid_types:
            console.print(
                f"[red]Error:[/red] Invalid documentation type '{doc_type}'. "
                f"Valid types are: {', '.join(valid_types)}"
            )
            raise typer.Exit(1)

        # Generate documentation based on type
        console.print(f"[cyan]Generating {doc_type} documentation...[/cyan]")
        
        if doc_type == "all":
            # Generate all documentation types
            context = gather_project_context("all")
            generate_all_docs(output, context)
            console.print(f"[green]✅[/green] All documentation written to {output}")
            
        elif doc_type == "agents":
            # Generate agent documentation
            context = gather_project_context("agents")
            template_name = None if template == "cli_reference.md.j2" else template
            generate_agent_docs(output, context, template_name)
            console.print(f"[green]✅[/green] Agent documentation written to {output}")
            
        elif doc_type == "workflow":
            # Generate workflow documentation
            context = gather_project_context("workflow")
            template_name = None if template == "cli_reference.md.j2" else template
            generate_workflow_docs(output, context, template_name)
            console.print(f"[green]✅[/green] Workflow documentation written to {output}")
            
        else:  # doc_type == "cli"
            # Generate CLI documentation
            command_list = command.split() if command else None
            generate_cli_docs(output, command_list, template)
            console.print(f"[green]✅[/green] CLI documentation written to {output}")

    except Exception as e:
        console.print(
            f"[red]Unexpected error:[/red] {e}"
        )
        raise typer.Exit(1) from e
