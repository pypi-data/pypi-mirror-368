"""AI integration commands for Gira."""

import os
from pathlib import Path
from typing import Optional, List
import typer
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.console import Console
from rich.prompt import Confirm, Prompt

from gira.utils.console import console
from gira.utils.errors import GiraError
from gira.utils.ai_integration import (
    AIDocumentationDetector,
    AIDocumentationGenerator,
    AIDocType,
    create_backup,
    inject_gira_section
)
from gira.utils.config import load_config
from gira.utils.command_suggestions import create_typer_with_suggestions


# Create AI app with command suggestions
ai_app = create_typer_with_suggestions(help="AI integration commands")


@ai_app.command("status")
def ai_status() -> None:
    """Show AI documentation files and integration status."""
    try:
        config = load_config()
        project_root = Path.cwd()
        
        detector = AIDocumentationDetector(project_root)
        ai_files = detector.detect_ai_files()
        
        # Create status table
        table = Table(title="AI Documentation Status", show_header=True)
        table.add_column("File", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Git Tracked", style="yellow")
        table.add_column("Has Gira Section", style="blue")
        
        for ai_file in ai_files:
            status = "✓ Exists" if ai_file.exists else "✗ Not Found"
            tracked = "Yes" if ai_file.is_tracked else "No"
            has_gira = "Yes" if ai_file.has_gira_section else "No"
            
            table.add_row(
                str(ai_file.path.relative_to(project_root)),
                ai_file.doc_type.value,
                status,
                tracked,
                has_gira
            )
            
        if not ai_files:
            table.add_row("No AI documentation files found", "-", "-", "-", "-")
            
        console.print(table)
        
        # Show Gira AI docs
        gira_docs_dir = Path(".gira/docs")
        if gira_docs_dir.exists():
            console.print("\n[bold]Gira AI Documentation:[/bold]")
            for doc in gira_docs_dir.glob("*.md"):
                if "claude" in doc.name.lower() or "gemini" in doc.name.lower() or "ai" in doc.name.lower():
                    console.print(f"  • {doc.relative_to(project_root)}")
                    
    except Exception as e:
        raise GiraError(f"Failed to check AI status: {e}")


@ai_app.command("setup")
def ai_setup(
    force: bool = typer.Option(False, "--force", "-f", help="Force setup even if files exist"),
    non_interactive: bool = typer.Option(False, "--non-interactive", help="Run without prompts")
) -> None:
    """Set up AI documentation for the project."""
    try:
        config = load_config()
        project_root = Path.cwd()
        
        detector = AIDocumentationDetector(project_root)
        ai_files = detector.detect_ai_files()
        
        if not ai_files and not non_interactive:
            # No existing AI files, ask what to create
            console.print("\n[yellow]No existing AI documentation found.[/yellow]")
            console.print("Which AI documentation would you like to create?")
            console.print("1. CLAUDE.md - For Claude AI")
            console.print("2. GEMINI.md - For Google Gemini")
            console.print("3. AI.md - Generic AI documentation")
            console.print("4. All of the above")
            console.print("5. Skip")
            
            choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"], default="3")
            
            generator = AIDocumentationGenerator()
            files_to_create = []
            
            if choice == "1":
                files_to_create = [AIDocType.CLAUDE]
            elif choice == "2":
                files_to_create = [AIDocType.GEMINI]
            elif choice == "3":
                files_to_create = [AIDocType.AI]
            elif choice == "4":
                files_to_create = [AIDocType.CLAUDE, AIDocType.GEMINI, AIDocType.AI]
            else:
                console.print("Skipping AI documentation setup.")
                return
                
            for doc_type in files_to_create:
                file_path = project_root / doc_type.value
                content = generator.generate_companion_file(
                    doc_type,
                    config.get("project_name", "My Project"),
                    config.get("ticket_id_prefix", "PROJ")
                )
                
                file_path.write_text(content)
                console.print(f"✅ Created {doc_type.value}")
                
        else:
            # Handle existing AI files
            for ai_file in ai_files:
                if ai_file.exists and not ai_file.has_gira_section:
                    if non_interactive:
                        console.print(f"[yellow]Skipping {ai_file.path.name} (non-interactive mode)[/yellow]")
                        continue
                        
                    console.print(f"\n[bold]Found {ai_file.path.name}[/bold]")
                    
                    if ai_file.is_tracked:
                        console.print("[yellow]⚠️  This file is tracked by git[/yellow]")
                        
                    action = Prompt.ask(
                        "What would you like to do?",
                        choices=["inject", "companion", "skip"],
                        default="skip"
                    )
                    
                    if action == "inject":
                        # Find insertion point
                        insertion_point = detector.find_safe_insertion_point(ai_file.content)
                        
                        # Show preview
                        preview_lines = ai_file.content.split('\n')
                        insert_line = len([l for l in ai_file.content[:insertion_point].split('\n')])
                        
                        console.print(f"\n[dim]Will insert Gira section around line {insert_line}[/dim]")
                        
                        if Confirm.ask("Create backup and proceed?", default=True):
                            backup_path = create_backup(ai_file.path)
                            if backup_path:
                                console.print(f"[dim]Backup created: {backup_path}[/dim]")
                                
                            new_content = inject_gira_section(
                                ai_file.path,
                                ai_file.content,
                                insertion_point
                            )
                            
                            ai_file.path.write_text(new_content)
                            console.print(f"✅ Updated {ai_file.path.name}")
                            
                    elif action == "companion":
                        # Create companion file
                        companion_name = f"{ai_file.path.stem}-GIRA{ai_file.path.suffix}"
                        companion_path = ai_file.path.parent / companion_name
                        
                        generator = AIDocumentationGenerator()
                        content = generator.generate_companion_file(
                            ai_file.doc_type,
                            config.get("project_name", "My Project"),
                            config.get("ticket_id_prefix", "PROJ")
                        )
                        
                        companion_path.write_text(content)
                        console.print(f"✅ Created {companion_name}")
                        
        console.print("\n[green]AI documentation setup complete![/green]")
        console.print("Run [cyan]gira ai-help[/cyan] for AI-specific command examples.")
        
    except Exception as e:
        raise GiraError(f"Failed to set up AI documentation: {e}")


@ai_app.command("ai-help")
def ai_help(
    agent: Optional[str] = typer.Argument(None, help="Specific AI agent (claude, gemini, etc.)")
) -> None:
    """Show AI-optimized command examples and patterns."""
    
    # Base examples that work for all agents
    base_examples = """
# Understanding Project State
gira board                          # Visual project overview
gira describe --format json         # AI-friendly project context
gira ticket list --format json      # List all tickets as JSON

# Working with Tickets
gira ticket show 123                # Show ticket details (number-only ID)
gira ticket create -t "Bug fix"     # Create a ticket
gira ticket move 123 in_progress    # Move ticket to in-progress
gira ticket update 123 -p high      # Update ticket priority

# Bulk Operations
gira ticket list --status todo | gira ticket move - in_progress
gira ticket list --assignee me --format id | xargs -I {} gira ticket show {}

# Context and Analysis
gira context                        # Show current working context
gira metrics overview               # Project metrics
gira query exec "status:todo"       # Query tickets
"""

    claude_examples = """
# Claude-Specific Patterns

## Structured Output for Tool Use
gira ticket list --format json | jq '.[] | {id, title, status}'
gira describe --format json > project_context.json

## Creating Detailed Tickets
gira ticket create \\
  --title "Implement user authentication" \\
  --description "Add JWT-based auth with refresh tokens" \\
  --type feature \\
  --priority high \\
  --labels security,backend

## Workflow Automation
# Get all tickets in review, format for processing
gira ticket list --status review --format json | \\
  jq -r '.[] | "\\(.id): \\(.title)"'
"""

    gemini_examples = """
# Gemini-Specific Patterns

## Project Understanding
gira describe --verbose              # Detailed project description
gira board --format json            # Board state as JSON

## Code-Ticket Correlation
gira ticket commits 123             # Show commits for a ticket
gira ticket blame file.py:45        # Find ticket that modified line

## Sprint Management
gira sprint show --current          # Current sprint details
gira sprint assign 123 124 125      # Assign tickets to sprint
"""

    examples = base_examples
    
    if agent:
        agent_lower = agent.lower()
        if agent_lower == "claude":
            examples += claude_examples
        elif agent_lower == "gemini":
            examples += gemini_examples
            
    console.print(Panel(
        Syntax(examples.strip(), "bash", theme="monokai", line_numbers=False),
        title=f"AI Command Examples{f' for {agent.title()}' if agent else ''}",
        border_style="blue"
    ))
    
    console.print("\n[dim]Tip: Use --format json with most commands for structured output[/dim]")
    console.print("[dim]Tip: Number-only IDs work everywhere (e.g., 'gira ticket show 123')[/dim]")


# Add alias for convenience
@ai_app.command("examples")
def ai_examples(
    agent: Optional[str] = typer.Argument(None, help="Specific AI agent (claude, gemini, etc.)")
) -> None:
    """Alias for ai-help command."""
    ai_help(agent)