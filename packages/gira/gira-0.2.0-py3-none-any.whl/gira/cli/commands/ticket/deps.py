"""List dependencies command for Gira tickets."""

import typer
from gira.utils.console import console
from rich.table import Table

from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket, load_all_tickets
from gira.utils.typer_completion import complete_ticket_ids

def deps(
    ticket_id: str = typer.Argument(..., help="Ticket ID to show dependencies for", autocompletion=complete_ticket_ids),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table, json"),
) -> None:
    """Show dependency relationships for a ticket.
    
    Displays both dependencies (tickets this ticket is blocked by) and dependents 
    (tickets that are blocked by this ticket).
    """
    root = ensure_gira_project()

    # Find the ticket (including archived)
    ticket, ticket_path = find_ticket(ticket_id, root, include_archived=True)
    if not ticket:
        console.print(f"❌ Ticket '{ticket_id}' not found.", style="red")
        raise typer.Exit(1)

    # Check if archived
    from gira.utils.ticket_utils import is_ticket_archived
    is_archived = is_ticket_archived(ticket_path) if ticket_path else False

    # Load all tickets to get details for dependencies (include archived)
    all_tickets = load_all_tickets(root, include_archived=True)
    ticket_map = {t.id: t for t in all_tickets}

    if output_format == "json":
        import json
        result = {
            "ticket_id": ticket.id,
            "blocked_by": ticket.blocked_by,
            "blocks": ticket.blocks
        }
        print(json.dumps(result, indent=2))
        return

    # Create table display
    title = f"\n🔗 Dependencies for {ticket.id}: {ticket.title}"
    if is_archived:
        from gira.utils.display import format_archived_indicator
        title += f" {format_archived_indicator(is_archived)}"
    console.print(title, style="bold blue")

    # Show what this ticket is blocked by
    if ticket.blocked_by:
        console.print(f"\n📥 Blocked by ({len(ticket.blocked_by)} tickets):", style="bold yellow")

        blocked_table = Table(show_header=True, header_style="bold magenta")
        blocked_table.add_column("ID", style="cyan", width=10)
        blocked_table.add_column("Title", style="white")
        blocked_table.add_column("Status", style="green", width=12)
        blocked_table.add_column("Priority", style="yellow", width=10)

        for dep_id in sorted(ticket.blocked_by):
            dep_ticket = ticket_map.get(dep_id)
            if dep_ticket:
                # Check if dependency is archived
                dep_ticket_obj, dep_path = find_ticket(dep_id, root, include_archived=True)
                dep_archived = is_ticket_archived(dep_path) if dep_path else False

                status = dep_ticket.status.replace('_', ' ').title()
                priority = dep_ticket.priority.title()
                dep_id_display = dep_id
                if dep_archived:
                    dep_id_display = f"{dep_id} [dim red][ARCHIVED][/dim red]"
                blocked_table.add_row(dep_id_display, dep_ticket.title, status, priority)
            else:
                blocked_table.add_row(dep_id, "[red]Not found[/red]", "-", "-")

        console.print(blocked_table)
    else:
        console.print("\n📥 Not blocked by any tickets", style="dim")

    # Show what this ticket blocks
    if ticket.blocks:
        console.print(f"\n📤 Blocking ({len(ticket.blocks)} tickets):", style="bold red")

        blocks_table = Table(show_header=True, header_style="bold magenta")
        blocks_table.add_column("ID", style="cyan", width=10)
        blocks_table.add_column("Title", style="white")
        blocks_table.add_column("Status", style="green", width=12)
        blocks_table.add_column("Priority", style="yellow", width=10)

        for blocked_id in sorted(ticket.blocks):
            blocked_ticket = ticket_map.get(blocked_id)
            if blocked_ticket:
                # Check if blocked ticket is archived
                blocked_ticket_obj, blocked_path = find_ticket(blocked_id, root, include_archived=True)
                blocked_archived = is_ticket_archived(blocked_path) if blocked_path else False

                status = blocked_ticket.status.replace('_', ' ').title()
                priority = blocked_ticket.priority.title()
                blocked_id_display = blocked_id
                if blocked_archived:
                    blocked_id_display = f"{blocked_id} [dim red][ARCHIVED][/dim red]"
                blocks_table.add_row(blocked_id_display, blocked_ticket.title, status, priority)
            else:
                blocks_table.add_row(blocked_id, "[red]Not found[/red]", "-", "-")

        console.print(blocks_table)
    else:
        console.print("\n📤 Not blocking any tickets", style="dim")

    # Summary
    total_deps = len(ticket.blocked_by) + len(ticket.blocks)
    if total_deps > 0:
        console.print(f"\n📊 Total dependency relationships: {total_deps}", style="bold")
    else:
        console.print("\n📊 No dependency relationships", style="dim")
