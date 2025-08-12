"""Initialize command for Gira."""

import json
import os
from pathlib import Path
from typing import Optional

import typer

from gira.constants import GIRA_BASE_DIRECTORIES
from gira.models import Board, ProjectConfig
from gira.utils.console import console
from gira.utils.templates import (
    create_board_from_template,
    create_workflow_guide,
    get_workflow_config,
    get_workflow_templates,
)


def init(
    name: str = typer.Argument(None, help="Project name"),
    description: str = typer.Option("", "--description", "-d", help="Project description"),
    prefix: str = typer.Option(
        None,
        "--prefix", "-p",
        help="Ticket ID prefix (2-4 uppercase letters)",
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Overwrite existing project",
    ),
    strict_workflow: bool = typer.Option(
        False,
        "--strict-workflow",
        help="Use traditional linear workflow instead of flexible transitions",
    ),
    workflow: Optional[str] = typer.Option(
        None,
        "--workflow", "-w",
        help="Workflow template: scrum, kanban, support-desk, bug-tracking, minimal, custom",
    ),
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive", "--no-input",
        help="Run without prompts (all required options must be provided)",
    ),
) -> None:
    """Initialize a new Gira project in the current directory."""
    gira_dir = Path.cwd() / ".gira"

    # Check for environment variables that indicate non-interactive mode
    non_interactive = non_interactive or bool(
        os.environ.get('CI') or 
        os.environ.get('GIRA_NON_INTERACTIVE')
    )

    # Check if already initialized
    if gira_dir.exists() and not force:
        console.print("[red]Error:[/red] Directory already contains a Gira project.")
        console.print("Use --force to overwrite.")
        raise typer.Exit(1)

    # Validate required parameters for non-interactive mode
    if non_interactive:
        if not name:
            console.print("[red]Error:[/red] --non-interactive requires project name to be specified")
            console.print("Usage: gira init 'Project Name' --non-interactive")
            raise typer.Exit(1)

    # Prompt for project name if not provided
    if not name and not non_interactive:
        name = typer.prompt("Project name")

    # Generate prefix if not provided
    if not prefix:
        if non_interactive:
            # Generate prefix automatically from name
            prefix = ProjectConfig.generate_prefix_from_name(name).upper()
        else:
            suggested_prefix = ProjectConfig.generate_prefix_from_name(name)
            prefix = typer.prompt(
                "Ticket ID prefix",
                default=suggested_prefix,
            ).upper()
    else:
        # Normalize prefix to uppercase
        prefix = prefix.upper()

    # Validate prefix
    if not (2 <= len(prefix) <= 4 and prefix.isalpha()):
        console.print(
            "[red]Error:[/red] Prefix must be 2-4 uppercase letters."
        )
        raise typer.Exit(1)

    # Handle workflow selection
    if not workflow:
        if non_interactive:
            # Default to 'minimal' workflow in non-interactive mode
            workflow = "minimal"
        else:
            # Interactive workflow selection
            templates = get_workflow_templates()
            console.print("\n[bold]Choose workflow template:[/bold]")
            choices = []
            for key, info in templates.items():
                console.print(f"  [{len(choices) + 1}] {info['name']} - {info['description']}")
                choices.append(key)

            while True:
                choice = typer.prompt("\nSelect workflow (1-6)", default="5")  # Default to minimal
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(choices):
                        workflow = choices[idx]
                        break
                    else:
                        console.print("[red]Invalid choice. Please enter a number between 1 and 6.[/red]")
                except ValueError:
                    console.print("[red]Invalid choice. Please enter a number.[/red]")

    # Validate workflow choice
    valid_workflows = list(get_workflow_templates().keys())
    if workflow not in valid_workflows:
        console.print(f"[red]Error:[/red] Invalid workflow '{workflow}'")
        console.print(f"Valid options: {', '.join(valid_workflows)}")
        raise typer.Exit(1)

    # Get workflow configuration
    workflow_config = get_workflow_config(workflow)

    # Create project config with workflow settings
    config = ProjectConfig(
        name=name,
        description=description,
        ticket_id_prefix=prefix,
        strict_workflow=strict_workflow,  # Only set if explicitly requested
        workflow_type=workflow,
    )

    # Create directory structure
    console.print(f"\n[bold]Initializing Gira project:[/bold] {name}")

    try:
        # Ensure we can write to the project directory when it already exists
        if gira_dir.exists():
            mode = gira_dir.stat().st_mode
            if mode & 0o222 == 0:
                raise PermissionError("project directory is not writable")

        # Create base directories
        for dir_path in GIRA_BASE_DIRECTORIES:
            (Path.cwd() / dir_path).mkdir(parents=True, exist_ok=True)

        # Create board config based on workflow template
        board = create_board_from_template(workflow)
        if not board:
            # Fallback to default if template not found
            board = Board.create_default(strict_workflow=config.strict_workflow)

        # Create board swimlane directories dynamically based on config
        for swimlane in board.swimlanes:
            swimlane_dir = Path.cwd() / ".gira" / "board" / swimlane.id
            swimlane_dir.mkdir(parents=True, exist_ok=True)

        # Update config with workflow-specific settings
        # Note: We could store workflow features as metadata later if needed

        # Update statuses based on board swimlanes
        config.statuses = [sl.id for sl in board.swimlanes]

        # Save config
        config_path = gira_dir / "config.json"
        config.save_to_json_file(str(config_path))

        # Save board config
        board_path = gira_dir / ".board.json"
        board.save_to_json_file(str(board_path))

        # Create initial state file
        state = {
            "next_ticket_number": 1,
            "active_sprint": None,
        }
        state_path = gira_dir / ".state.json"
        state_path.write_text(json.dumps(state, indent=2))

        # If scrum workflow, create initial sprint
        if workflow == "scrum" and workflow_config.get("sprint_settings", {}).get("auto_create"):
            from datetime import datetime, timedelta
            sprint_name = workflow_config["sprint_settings"]["naming_pattern"].format(number=1)
            duration = workflow_config["sprint_settings"]["duration_days"]

            sprint_data = {
                "id": f"SPRINT-{datetime.now().strftime('%Y-%m-%d')}",
                "name": sprint_name,
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=duration)).isoformat(),
                "status": "active",
                "tickets": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            sprint_file = gira_dir / "sprints" / "active" / f"{sprint_data['id']}.json"
            sprint_file.parent.mkdir(parents=True, exist_ok=True)
            sprint_file.write_text(json.dumps(sprint_data, indent=2))

            # Update state with active sprint
            state["active_sprint"] = sprint_data["id"]
            state_path.write_text(json.dumps(state, indent=2))

        # Create .gitignore for .gira directory
        gitignore_path = gira_dir / ".gitignore"
        gitignore_content = """# Gira internal files
.index.json
*.tmp

# Cache directory
cache/
"""
        gitignore_path.write_text(gitignore_content)

        # Create workflow guide
        docs_dir = gira_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        workflow_guide_path = docs_dir / "WORKFLOW.md"
        workflow_guide = create_workflow_guide(workflow, name, prefix)
        workflow_guide_path.write_text(workflow_guide)

        # Generate AI agent documentation
        try:
            from gira.utils.docs_generator import generate_agent_docs
            from gira.utils.project_context import gather_project_context
            
            console.print("\n[dim]Generating AI agent documentation...[/dim]")
            
            # Gather context with project-specific information
            context = gather_project_context(
                doc_type="agents",
                project_name=name,
                project_description=description,
                ticket_prefix=prefix,
                workflow_type=workflow
            )
            
            # Generate agent documentation
            generate_agent_docs(docs_dir, context)
            
            # Check for existing AI documentation in project root
            if not non_interactive:
                from gira.utils.ai_integration import AIDocumentationDetector
                detector = AIDocumentationDetector(Path.cwd())
                ai_files = detector.detect_ai_files()
                
                if ai_files:
                    console.print("\n[dim]Found existing AI documentation files.[/dim]")
                    console.print("Run [cyan]gira ai setup[/cyan] to integrate Gira with your AI docs.")
            
        except Exception as e:
            # Don't fail init if docs generation fails
            console.print(f"[yellow]Warning:[/yellow] Could not generate agent docs: {e}")

        # Success message
        console.print("\n✅ Gira project initialized successfully!")
        console.print(f"   Name: [cyan]{name}[/cyan]")
        console.print(f"   Prefix: [cyan]{prefix}[/cyan]")
        console.print(f"   Workflow: [cyan]{workflow}[/cyan]")
        console.print(f"   Location: [cyan]{Path.cwd()}[/cyan]")
        console.print("\n[dim]Next steps:[/dim]")
        console.print("  • Create your first ticket: [cyan]gira ticket create[/cyan]")
        console.print("  • View the board: [cyan]gira board[/cyan]")
        console.print("  • Read workflow guide: [cyan]cat .gira/docs/WORKFLOW.md[/cyan]")
        console.print("  • See all commands: [cyan]gira --help[/cyan]")

    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to initialize project: {e}")
        raise typer.Exit(1) from e
