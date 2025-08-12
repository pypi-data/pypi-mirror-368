"""Ticket prefix rename functionality."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from gira.models.config import ProjectConfig
from gira.models.epic import Epic
from gira.models.sprint import Sprint
from gira.models.ticket import Ticket
from gira.utils.console import console
from gira.utils.prefix_history import PrefixHistory


@dataclass
class RenameImpact:
    """Analysis of what will be affected by a prefix rename."""

    tickets: List[Ticket]
    epics: List[Epic]
    sprints: List[Sprint]
    dependencies: Dict[str, List[str]]  # ticket_id -> [dependency_ids]
    blockers: Dict[str, List[str]]  # ticket_id -> [blocker_ids]
    subtask_relationships: Dict[str, str]  # subtask_id -> parent_id
    epic_tickets: Dict[str, List[str]]  # epic_id -> [ticket_ids]
    sprint_tickets: Dict[str, List[str]]  # sprint_id -> [ticket_ids]

    @property
    def total_items(self) -> int:
        """Total number of items to rename."""
        return len(self.tickets) + len(self.epics) + len(self.sprints)


def analyze_rename_impact(root: Path, old_prefix: str, new_prefix: str) -> RenameImpact:
    """Analyze what will be affected by a prefix rename.
    
    Args:
        root: Project root directory
        old_prefix: Current ticket prefix
        new_prefix: New ticket prefix
        
    Returns:
        RenameImpact object with all affected items
    """
    gira_dir = root / ".gira"

    # Collect all tickets
    tickets = []
    board_dir = gira_dir / "board"
    archive_dir = gira_dir / "archive" / "tickets"

    for status_dir in board_dir.iterdir():
        if status_dir.is_dir():
            for ticket_file in status_dir.glob("*.json"):
                try:
                    ticket = Ticket.from_json_file(str(ticket_file))
                    if ticket.id.startswith(f"{old_prefix}-"):
                        tickets.append(ticket)
                except Exception:
                    pass

    # Check archived tickets too
    if archive_dir.exists():
        for ticket_file in archive_dir.glob("*.json"):
            try:
                ticket = Ticket.from_json_file(str(ticket_file))
                if ticket.id.startswith(f"{old_prefix}-"):
                    tickets.append(ticket)
            except Exception:
                pass

    # Collect all epics
    epics = []
    epics_dir = gira_dir / "epics"
    if epics_dir.exists():
        for epic_file in epics_dir.glob("*.json"):
            try:
                epic = Epic.from_json_file(str(epic_file))
                if epic.id.startswith(f"{old_prefix}-") or epic.id.startswith("EPIC-"):
                    epics.append(epic)
            except Exception:
                pass

    # Collect all sprints
    sprints = []
    sprints_dir = gira_dir / "sprints"
    if sprints_dir.exists():
        for sprint_file in sprints_dir.glob("*.json"):
            try:
                sprint = Sprint.from_json_file(str(sprint_file))
                sprints.append(sprint)
            except Exception:
                pass

    # Analyze relationships
    dependencies = {}
    blockers = {}
    subtask_relationships = {}
    epic_tickets = {}
    sprint_tickets = {}

    # Analyze ticket relationships
    for ticket in tickets:
        if ticket.blocked_by:
            dependencies[ticket.id] = ticket.blocked_by
        if ticket.blocks:
            blockers[ticket.id] = ticket.blocks
        if ticket.parent_id:
            subtask_relationships[ticket.id] = ticket.parent_id

    # Analyze epic relationships
    for epic in epics:
        if epic.tickets:
            epic_tickets[epic.id] = epic.tickets

    # Analyze sprint relationships
    for sprint in sprints:
        if sprint.tickets:
            sprint_tickets[sprint.id] = sprint.tickets

    return RenameImpact(
        tickets=tickets,
        epics=epics,
        sprints=sprints,
        dependencies=dependencies,
        blockers=blockers,
        subtask_relationships=subtask_relationships,
        epic_tickets=epic_tickets,
        sprint_tickets=sprint_tickets
    )


def rename_id(old_id: str, old_prefix: str, new_prefix: str) -> str:
    """Rename a single ID from old prefix to new prefix.
    
    Args:
        old_id: The ID to rename (e.g., "GCM-123")
        old_prefix: Current prefix (e.g., "GCM")
        new_prefix: New prefix (e.g., "NEW")
        
    Returns:
        The renamed ID (e.g., "NEW-123")
    """
    if old_id.startswith(f"{old_prefix}-"):
        number = old_id[len(old_prefix) + 1:]
        return f"{new_prefix}-{number}"
    return old_id


def rename_id_list(ids: List[str], old_prefix: str, new_prefix: str) -> List[str]:
    """Rename a list of IDs."""
    return [rename_id(id, old_prefix, new_prefix) for id in ids]


def execute_rename(root: Path, old_prefix: str, new_prefix: str, impact: RenameImpact) -> bool:
    """Execute the rename operation for all affected items.
    
    Args:
        root: Project root directory
        old_prefix: Current ticket prefix
        new_prefix: New ticket prefix
        impact: The analyzed impact
        
    Returns:
        True if successful, False otherwise
    """
    gira_dir = root / ".gira"

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            # Check if .gira is tracked by git
            from gira.utils.git_utils import run_git_command
            git_tracked = run_git_command(['git', 'ls-files', '.gira']) is not None

            backup_dir = None
            if not git_tracked:
                # Create backup only if .gira is not tracked
                task = progress.add_task("Creating backup (untracked .gira)...", total=None)
                backup_dir = gira_dir / f"backup_{old_prefix}_to_{new_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copytree(gira_dir, backup_dir)
                progress.update(task, completed=True)
            else:
                # Skip backup for git-tracked .gira
                task = progress.add_task("Skipping backup (git-tracked)...", total=None)
                progress.update(task, completed=True)

            # Update tickets
            task = progress.add_task(f"Renaming {len(impact.tickets)} tickets...", total=len(impact.tickets))
            for ticket in impact.tickets:
                old_id = ticket.id
                new_id = rename_id(old_id, old_prefix, new_prefix)

                # Update ticket ID and relationships
                ticket.id = new_id
                if ticket.blocked_by:
                    ticket.blocked_by = rename_id_list(ticket.blocked_by, old_prefix, new_prefix)
                if ticket.blocks:
                    ticket.blocks = rename_id_list(ticket.blocks, old_prefix, new_prefix)
                if ticket.parent_id:
                    ticket.parent_id = rename_id(ticket.parent_id, old_prefix, new_prefix)
                if ticket.epic_id and ticket.epic_id.startswith(f"{old_prefix}-"):
                    ticket.epic_id = rename_id(ticket.epic_id, old_prefix, new_prefix)

                # Move file to new location
                old_path = _find_ticket_file(gira_dir, old_id)
                if old_path:
                    new_path = old_path.parent / f"{new_id}.json"
                    ticket.save_to_json_file(str(new_path))
                    if old_path != new_path:
                        old_path.unlink()

                progress.update(task, advance=1)

            # Update epics
            task = progress.add_task(f"Renaming {len(impact.epics)} epics...", total=len(impact.epics))
            for epic in impact.epics:
                # Only rename if it uses the project prefix (not EPIC- prefix)
                if epic.id.startswith(f"{old_prefix}-"):
                    old_id = epic.id
                    new_id = rename_id(old_id, old_prefix, new_prefix)
                    epic.id = new_id

                # Update ticket references
                if epic.tickets:
                    epic.tickets = rename_id_list(epic.tickets, old_prefix, new_prefix)

                # Save epic
                epic_path = gira_dir / "epics" / f"{epic.id}.json"
                epic.save_to_json_file(str(epic_path))

                progress.update(task, advance=1)

            # Update sprints
            task = progress.add_task(f"Updating {len(impact.sprints)} sprints...", total=len(impact.sprints))
            for sprint in impact.sprints:
                # Update ticket references in sprints
                if sprint.tickets:
                    sprint.tickets = rename_id_list(sprint.tickets, old_prefix, new_prefix)

                # Save sprint
                sprint_path = gira_dir / "sprints" / f"{sprint.id}.json"
                sprint.save_to_json_file(str(sprint_path))

                progress.update(task, advance=1)

            # Update configuration
            task = progress.add_task("Updating configuration...", total=None)
            config_path = gira_dir / "config.json"
            config = ProjectConfig.from_json_file(str(config_path))
            config.ticket_id_prefix = new_prefix

            # Update commit patterns if they reference the old prefix
            updated_patterns = []
            for pattern in config.commit_id_patterns:
                # Replace hardcoded prefix references
                if old_prefix in pattern:
                    pattern = pattern.replace(old_prefix, new_prefix)
                updated_patterns.append(pattern)
            config.commit_id_patterns = updated_patterns

            config.save_to_json_file(str(config_path))
            progress.update(task, completed=True)

            # Update prefix history
            task = progress.add_task("Updating prefix history...", total=None)
            history = PrefixHistory(root)
            history.add_prefix(new_prefix)
            progress.update(task, completed=True)

            # Invalidate git caches since patterns have changed
            from gira.utils.git_utils import invalidate_git_caches
            invalidate_git_caches()

        return True

    except Exception as e:
        console.print(f"[red]Error during rename:[/red] {e}")
        if backup_dir:
            console.print(f"[yellow]Backup created at:[/yellow] {backup_dir}")
        else:
            console.print("[yellow]No backup was created (git-tracked). Use git to revert changes if needed.[/yellow]")
        return False


def _find_ticket_file(gira_dir: Path, ticket_id: str) -> Optional[Path]:
    """Find the file path for a ticket."""
    # Check board directories
    board_dir = gira_dir / "board"
    for status_dir in board_dir.iterdir():
        if status_dir.is_dir():
            ticket_file = status_dir / f"{ticket_id}.json"
            if ticket_file.exists():
                return ticket_file

    # Check archive
    archive_file = gira_dir / "archive" / "tickets" / f"{ticket_id}.json"
    if archive_file.exists():
        return archive_file

    return None


def show_rename_impact(impact: RenameImpact, old_prefix: str, new_prefix: str) -> None:
    """Display the impact analysis to the user."""
    console.print("\n[bold cyan]Rename Impact Analysis[/bold cyan]")
    console.print(f"Changing prefix from '[bold]{old_prefix}[/bold]' to '[bold]{new_prefix}[/bold]'")

    # Summary table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Item Type", style="cyan")
    table.add_column("Count", justify="right")

    table.add_row("Tickets", str(len(impact.tickets)))
    table.add_row("Epics", str(len(impact.epics)))
    table.add_row("Sprints (with ticket refs)", str(len([s for s in impact.sprints if s.tickets])))
    table.add_row("Dependencies", str(sum(len(deps) for deps in impact.dependencies.values())))
    table.add_row("Blockers", str(sum(len(blocks) for blocks in impact.blockers.values())))
    table.add_row("Subtask relationships", str(len(impact.subtask_relationships)))

    console.print(table)

    # Show example renames
    console.print("\n[bold]Example renames:[/bold]")
    examples = []
    for ticket in impact.tickets[:3]:
        old_id = ticket.id
        new_id = rename_id(old_id, old_prefix, new_prefix)
        examples.append(f"  • {old_id} → {new_id}")

    for example in examples:
        console.print(example)

    if len(impact.tickets) > 3:
        console.print(f"  • ... and {len(impact.tickets) - 3} more tickets")

    # Warnings
    if impact.total_items > 100:
        console.print(f"\n[yellow]⚠ Warning:[/yellow] This will rename {impact.total_items} items.")
        console.print("A backup will be created before making changes.")


def run_rename_wizard(root: Path, old_prefix: str, new_prefix: str) -> bool:
    """Run the interactive rename wizard.
    
    Args:
        root: Project root directory
        old_prefix: Current ticket prefix
        new_prefix: New ticket prefix
        
    Returns:
        True if rename was successful, False otherwise
    """
    console.print("\n[bold cyan]Ticket Prefix Rename Wizard[/bold cyan]")

    # Initialize prefix history
    history = PrefixHistory(root)
    if not history.get_current_prefix():
        # Initialize with current prefix if no history exists
        history.add_prefix(old_prefix)

    # Analyze impact
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Analyzing rename impact...", total=None)
        impact = analyze_rename_impact(root, old_prefix, new_prefix)
        progress.update(task, completed=True)

    # Show impact
    show_rename_impact(impact, old_prefix, new_prefix)

    # Check if .gira is tracked by git
    from gira.utils.git_utils import run_git_command
    git_tracked = run_git_command(['git', 'ls-files', '.gira']) is not None

    # Confirm
    console.print("\n[bold]This operation will:[/bold]")
    if git_tracked:
        console.print("  1. [dim](Skip backup - .gira is git-tracked)[/dim]")
    else:
        console.print("  1. Create a backup of all data")
    console.print("  2. Rename all ticket/epic IDs")
    console.print("  3. Update all references and relationships")
    console.print("  4. Update configuration and prefix history")
    console.print("  5. Generate new commit patterns for git integration")

    if git_tracked:
        console.print("\n[dim]Note: Since .gira is tracked by git, you can revert changes with git if needed.[/dim]")

    if not typer.confirm("\nDo you want to proceed with the rename?"):
        console.print("[yellow]Rename cancelled[/yellow]")
        return False

    # Execute rename
    success = execute_rename(root, old_prefix, new_prefix, impact)

    if success:
        console.print(f"\n[green]✓[/green] Successfully renamed prefix from '{old_prefix}' to '{new_prefix}'")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("  • All existing tickets have been renamed")
        console.print("  • Git history is preserved (old commit references will still work)")
        console.print("  • New commits should use the new prefix")
        console.print(f"  • You can still search for tickets using the old '{old_prefix}-' prefix")

        if git_tracked:
            console.print("\n[dim]Tip: Use 'git diff' to review changes and 'git commit' to save them.[/dim]")
    else:
        if git_tracked:
            console.print("\n[red]✗[/red] Rename failed. Use git to check/revert any partial changes.")
        else:
            console.print("\n[red]✗[/red] Rename failed. Check the backup directory for recovery.")

    return success
