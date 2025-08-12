"""Archive all done tickets."""

from datetime import datetime, timedelta, timezone
from typing import Optional

import typer
from gira.utils.console import console
from rich.table import Table

from gira.utils.archive import archive_ticket as archive_ticket_util
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import load_tickets_by_status

def archive_done(
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview what would be archived"),
    before: Optional[str] = typer.Option(None, "--before", help="Archive tickets completed before this date (YYYY-MM-DD)"),
    older_than: Optional[int] = typer.Option(None, "--older-than", help="Archive tickets older than N days"),
    sprint: Optional[str] = typer.Option(None, "--sprint", help="Archive tickets from specific sprint"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt")
) -> None:
    """Archive all done tickets with optional filtering."""
    ensure_gira_project()

    try:
        # Load all done tickets
        done_tickets = load_tickets_by_status("done")

        if not done_tickets:
            console.print("[yellow]No done tickets to archive[/yellow]")
            return

        # Apply filters
        tickets_to_archive = []

        for ticket in done_tickets:
            # Check before date filter
            if before:
                before_date = datetime.strptime(before, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                ticket_date = ticket.updated_at
                if ticket_date.tzinfo is None:
                    ticket_date = ticket_date.replace(tzinfo=timezone.utc)
                if ticket_date > before_date:
                    continue

            # Check older_than filter
            if older_than is not None:
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=older_than)
                ticket_date = ticket.updated_at
                if ticket_date.tzinfo is None:
                    ticket_date = ticket_date.replace(tzinfo=timezone.utc)
                if ticket_date > cutoff_date:
                    continue

            # Check sprint filter
            if sprint and ticket.sprint_id != sprint:
                continue

            tickets_to_archive.append(ticket)

        if not tickets_to_archive:
            console.print("[yellow]No tickets match the archive criteria[/yellow]")
            return

        # Show preview
        table = Table(title=f"Tickets to Archive ({len(tickets_to_archive)})")
        table.add_column("ID", style="cyan")
        table.add_column("Title", max_width=50)
        table.add_column("Type", style="blue")
        table.add_column("Priority")
        table.add_column("Completed", style="green")

        for ticket in tickets_to_archive:
            priority_style = {
                "critical": "red",
                "high": "yellow",
                "medium": "blue",
                "low": "green"
            }.get(ticket.priority, "white")

            table.add_row(
                ticket.id,
                ticket.title,
                ticket.type,
                f"[{priority_style}]{ticket.priority}[/{priority_style}]",
                ticket.updated_at.strftime("%Y-%m-%d")
            )

        console.print(table)

        if dry_run:
            console.print("\n[yellow]DRY RUN:[/yellow] The following archive operations would be performed:")
            console.print(f"\nTotal tickets to archive: {len(tickets_to_archive)}")
            
            # Show archive destinations
            console.print("\n[dim]Tickets would be moved to:[/dim]")
            console.print("  .gira/.archive/done/")
            
            # Show summary by type
            type_counts = {}
            for ticket in tickets_to_archive:
                type_counts[ticket.type] = type_counts.get(ticket.type, 0) + 1
            
            console.print("\n[dim]Summary by type:[/dim]")
            for ticket_type, count in sorted(type_counts.items()):
                console.print(f"  • {ticket_type}: {count}")
            
            console.print("\n[dim]No changes were made (dry run)[/dim]")
            return

        # Confirm unless forced
        if not force:
            if not typer.confirm(f"\nArchive {len(tickets_to_archive)} tickets?"):
                console.print("[yellow]Archive cancelled[/yellow]")
                return

        # Archive tickets
        archived_count = 0
        for ticket in tickets_to_archive:
            try:
                archive_ticket_util(ticket)
                archived_count += 1
            except Exception as e:
                console.print(f"[red]Error archiving {ticket.id}:[/red] {e}")

        console.print(f"\n[green]✓[/green] Archived {archived_count} tickets")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
