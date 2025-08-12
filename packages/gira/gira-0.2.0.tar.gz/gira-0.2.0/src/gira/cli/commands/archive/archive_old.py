"""Archive old tickets based on age."""

from datetime import datetime, timedelta, timezone

import typer
from gira.utils.console import console
from rich.table import Table

from gira.utils.archive import archive_ticket as archive_ticket_util
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import load_all_tickets

def archive_old(
    days: int = typer.Option(30, "--days", "-d", help="Archive tickets older than N days"),
    status: str = typer.Option("done", "--status", "-s", help="Only archive tickets with this status"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview what would be archived"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt")
) -> None:
    """Archive tickets older than specified number of days."""
    ensure_gira_project()

    try:
        # Calculate cutoff date (make it timezone aware)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Load all tickets
        all_tickets = load_all_tickets()

        # Filter old tickets
        tickets_to_archive = []
        for ticket in all_tickets:
            # Check status filter
            if status and ticket.status != status:
                continue

            # Check age (make ticket datetime timezone aware if needed)
            ticket_date = ticket.updated_at
            if ticket_date.tzinfo is None:
                ticket_date = ticket_date.replace(tzinfo=timezone.utc)

            if ticket_date < cutoff_date:
                tickets_to_archive.append(ticket)

        if not tickets_to_archive:
            console.print(f"[yellow]No tickets older than {days} days found[/yellow]")
            return

        # Show preview
        table = Table(title=f"Old Tickets to Archive ({len(tickets_to_archive)})")
        table.add_column("ID", style="cyan")
        table.add_column("Title", max_width=40)
        table.add_column("Status")
        table.add_column("Type", style="blue")
        table.add_column("Last Updated", style="yellow")
        table.add_column("Age (days)", style="red")

        for ticket in tickets_to_archive:
            ticket_date = ticket.updated_at
            if ticket_date.tzinfo is None:
                ticket_date = ticket_date.replace(tzinfo=timezone.utc)
            age_days = (datetime.now(timezone.utc) - ticket_date).days

            status_style = {
                "todo": "yellow",
                "in_progress": "blue",
                "review": "magenta",
                "done": "green",
                "backlog": "dim"
            }.get(ticket.status, "white")

            table.add_row(
                ticket.id,
                ticket.title,
                f"[{status_style}]{ticket.status}[/{status_style}]",
                ticket.type,
                ticket.updated_at.strftime("%Y-%m-%d"),
                str(age_days)
            )

        console.print(table)

        if dry_run:
            console.print("\n[yellow]DRY RUN:[/yellow] The following archive operations would be performed:")
            console.print(f"\nTotal tickets to archive: {len(tickets_to_archive)}")
            console.print(f"Age threshold: {days} days")
            
            # Show archive destinations by status
            status_counts = {}
            for ticket in tickets_to_archive:
                status_counts[ticket.status] = status_counts.get(ticket.status, 0) + 1
            
            console.print("\n[dim]Tickets would be moved to:[/dim]")
            for ticket_status in sorted(status_counts.keys()):
                console.print(f"  • .gira/.archive/{ticket_status}/ ({status_counts[ticket_status]} tickets)")
            
            # Show age distribution
            age_ranges = {"0-30": 0, "31-60": 0, "61-90": 0, "90+": 0}
            for ticket in tickets_to_archive:
                ticket_date = ticket.updated_at
                if ticket_date.tzinfo is None:
                    ticket_date = ticket_date.replace(tzinfo=timezone.utc)
                age_days = (datetime.now(timezone.utc) - ticket_date).days
                
                if age_days <= 30:
                    age_ranges["0-30"] += 1
                elif age_days <= 60:
                    age_ranges["31-60"] += 1
                elif age_days <= 90:
                    age_ranges["61-90"] += 1
                else:
                    age_ranges["90+"] += 1
            
            console.print("\n[dim]Age distribution:[/dim]")
            for range_key, count in age_ranges.items():
                if count > 0:
                    console.print(f"  • {range_key} days: {count}")
            
            console.print("\n[dim]No changes were made (dry run)[/dim]")
            return

        # Confirm unless forced
        if not force:
            if not typer.confirm(f"\nArchive {len(tickets_to_archive)} old tickets?"):
                console.print("[yellow]Archive cancelled[/yellow]")
                return

        # Archive tickets
        archived_count = 0
        by_status = {}

        for ticket in tickets_to_archive:
            try:
                archive_ticket_util(ticket)
                archived_count += 1
                by_status[ticket.status] = by_status.get(ticket.status, 0) + 1
            except Exception as e:
                console.print(f"[red]Error archiving {ticket.id}:[/red] {e}")

        console.print(f"\n[green]✓[/green] Archived {archived_count} tickets:")
        for status, count in sorted(by_status.items()):
            console.print(f"  - {status}: {count}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
