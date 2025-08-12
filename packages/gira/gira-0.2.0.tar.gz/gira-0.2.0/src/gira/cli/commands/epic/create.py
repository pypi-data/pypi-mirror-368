"""Create epic command for Gira."""

import json
import sys
from datetime import datetime
from typing import Optional

import typer
from pydantic.v1 import EmailStr
from gira.utils.console import console
from gira.models import Epic, EpicStatus
from gira.utils.config import get_default_reporter
from gira.utils.editor import launch_editor
from gira.utils.project import ensure_gira_project
from gira.utils.stdin import StdinReader, validate_bulk_items, process_bulk_operation

def create(
    title: Optional[str] = typer.Argument(None, help="Epic title (required unless using --stdin)"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Epic description (use '-' for stdin, 'editor' to open editor)"),
    description_file: Optional[str] = typer.Option(None, "--description-file", help="Read description from a file"),
    owner: Optional[str] = typer.Option(None, "--owner", "-o", help="Epic owner email (defaults to git user email)"),
    target_date: Optional[str] = typer.Option(None, "--target-date", "-t", help="Target completion date (YYYY-MM-DD)"),
    output: str = typer.Option("text", "--output", help="Output format: text, json"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only output epic ID"),
    stdin: bool = typer.Option(False, "--stdin", help="Read JSON array of epics from stdin for bulk creation"),
    jsonl: bool = typer.Option(False, "--jsonl", help="Read JSONL (JSON Lines) format for streaming large datasets"),
) -> None:
    """Create a new epic."""
    root = ensure_gira_project()
    
    # Handle stdin bulk creation
    if stdin:
        return _create_bulk_from_stdin(root, output, quiet, jsonl)
    
    # Check if jsonl is used without stdin
    if jsonl:
        console.print("[red]Error:[/red] --jsonl requires --stdin")
        raise typer.Exit(1)

    # Validate title is provided for single epic creation
    if title is None:
        console.print("[red]Error:[/red] Title is required when not using --stdin")
        raise typer.Exit(1)
    
    # Check for mutually exclusive description options
    if description and description not in ["", "-", "editor"] and description_file:
        console.print("[red]Error:[/red] Cannot use both --description and --description-file")
        raise typer.Exit(1)
    
    # Handle description input methods
    if description_file:
        # Read description from file
        from pathlib import Path
        try:
            file_path = Path(description_file)
            if not file_path.exists():
                console.print(f"[red]Error:[/red] File not found: {description_file}")
                raise typer.Exit(1)
            
            # Read the file with UTF-8 encoding, handling different encodings gracefully
            try:
                description = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                # Try with latin-1 as fallback
                try:
                    description = file_path.read_text(encoding='latin-1')
                    console.print("[yellow]Warning:[/yellow] File was read with latin-1 encoding")
                except Exception as e:
                    console.print(f"[red]Error:[/red] Failed to read file: {e}")
                    raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to read description file: {e}")
            raise typer.Exit(1)
    elif description == "editor":
        # Open editor for description
        instructions = (
            "Enter the epic description below.\n"
            "Lines starting with # will be ignored.\n"
            "Save and exit to create the epic, or exit without saving to cancel."
        )
        editor_content = launch_editor(
            initial_content="",
            instructions=instructions
        )
        if editor_content is None:
            console.print("[yellow]Cancelled:[/yellow] No description provided")
            description = ""
        else:
            description = editor_content
    elif description == "-":
        # Read from stdin
        description = sys.stdin.read().strip()
    elif description is None:
        description = ""

    # Load state to get next epic number
    state_path = root / ".gira" / ".state.json"
    with open(state_path) as f:
        state = json.load(f)

    # Initialize next_epic_number if it doesn't exist
    if "next_epic_number" not in state:
        state["next_epic_number"] = 1

    # Generate epic ID
    epic_id = f"EPIC-{state['next_epic_number']:03d}"

    # Get owner - use provided value or default to git user email
    if not owner:
        owner = get_default_reporter()

    # Parse target date if provided
    target_date_obj = None
    if target_date:
        try:
            target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            console.print(f"[red]Error:[/red] Invalid date format '{target_date}'. Use YYYY-MM-DD.")
            raise typer.Exit(1)

    # Create epic
    try:
        epic = Epic(
            id=epic_id,
            title=title,
            description=description,
            owner=EmailStr(owner),
            target_date=target_date_obj,
            status=EpicStatus.DRAFT,  # New epics start as draft
        )

        # Save epic to file
        epic_path = root / ".gira" / "epics" / f"{epic_id}.json"
        epic.save_to_json_file(str(epic_path))

        # Update state
        state["next_epic_number"] += 1
        with open(state_path, 'w') as f:
            json.dump(state, f, indent=2)

        # Output result
        if quiet:
            # Use plain print for quiet mode to avoid color codes
            print(epic_id)
        elif output == "json":
            # Use plain print for JSON to avoid color codes
            print(epic.model_dump_json())
        else:
            console.print(f"✅ Created epic [cyan]{epic_id}[/cyan]: {title}")
            if description:
                console.print(f"   Description: {description[:50]}{'...' if len(description) > 50 else ''}")
            console.print("   Status: [yellow]Draft[/yellow]")
            console.print(f"   Owner: [green]{owner}[/green]")
            if target_date:
                console.print(f"   Target Date: [blue]{target_date}[/blue]")

    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to create epic: {e}")
        raise typer.Exit(1) from e


def _create_bulk_from_stdin(root, output: str, quiet: bool, jsonl: bool = False) -> None:
    """Create multiple epics from JSON stdin input."""
    # Read and validate stdin
    stdin_reader = StdinReader()
    
    if not stdin_reader.is_available():
        console.print("[red]Error:[/red] No data available on stdin")
        raise typer.Exit(1)
    
    try:
        if jsonl:
            # Read JSONL format
            items = list(stdin_reader.read_json_lines())
        else:
            # Read JSON array format
            items = stdin_reader.read_json_array()
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    if not items:
        console.print("[yellow]Warning:[/yellow] No items to process")
        return
    
    # Validate bulk items
    required_fields = ["title"]
    optional_fields = ["description", "owner", "target_date"]
    
    validation_errors = validate_bulk_items(items, required_fields, optional_fields)
    if validation_errors:
        console.print("[red]Validation errors:[/red]")
        for error in validation_errors:
            console.print(f"  - {error}")
        raise typer.Exit(1)
    
    # Load state once
    state_path = root / ".gira" / ".state.json"
    with open(state_path) as f:
        state = json.load(f)
    
    # Initialize next_epic_number if it doesn't exist
    if "next_epic_number" not in state:
        state["next_epic_number"] = 1
    
    # Process bulk creation
    def create_single_epic(item):
        return _create_single_epic_from_dict(item, root, state)
    
    result = process_bulk_operation(
        items, 
        create_single_epic,
        "epic creation",
        show_progress=not quiet and len(items) > 1
    )
    
    # Save updated state
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)
    
    # Output results
    if output == "json":
        # Use plain print for JSON to avoid color codes
        print(json.dumps(result.to_dict(), indent=2))
    elif quiet:
        # Output only successful epic IDs
        for success in result.successful:
            print(success["result"]["id"])
    else:
        result.print_summary("epic creation")
        
        # Show successful epics
        if result.successful and len(result.successful) <= 10:
            console.print("\n✅ **Created Epics:**")
            for success in result.successful:
                epic_data = success["result"]
                console.print(f"  - [cyan]{epic_data['id']}[/cyan]: {epic_data['title']}")
        elif result.successful:
            console.print(f"\n✅ Created {len(result.successful)} epics")
    
    # Exit with error code if any failures
    if result.failure_count > 0:
        raise typer.Exit(1)


def _create_single_epic_from_dict(item, root, state):
    """Create a single epic from dictionary data."""
    from datetime import datetime
    
    # Extract values
    title = item["title"]
    description = item.get("description", "")
    owner = item.get("owner")
    target_date = item.get("target_date")
    
    # Generate epic ID
    epic_id = f"EPIC-{state['next_epic_number']:03d}"
    state['next_epic_number'] += 1
    
    # Get owner - use provided value or default to git user email
    if not owner:
        owner = get_default_reporter()
    
    # Parse target date if provided
    target_date_obj = None
    if target_date:
        try:
            target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid date format '{target_date}'. Use YYYY-MM-DD.")

    # Create epic
    epic = Epic(
        id=epic_id,
        title=title,
        description=description,
        owner=owner,
        target_date=target_date_obj,
        status=EpicStatus.DRAFT,
    )
    
    # Save epic
    epic_path = root / ".gira" / "epics" / f"{epic_id}.json"
    epic.save_to_json_file(str(epic_path))
    
    return {
        "id": epic_id,
        "title": title,
        "status": "draft",
        "owner": owner
    }
