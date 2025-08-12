"""Remove dependency command for Gira tickets."""

import typer
from gira.utils.console import console
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket
from gira.utils.typer_completion import complete_ticket_ids

def remove_dep(
    ticket_id: str = typer.Argument(..., help="Ticket ID to remove dependency from", autocompletion=complete_ticket_ids),
    dependency_id: str = typer.Argument(..., help="Ticket ID to remove as dependency", autocompletion=complete_ticket_ids),
    no_reciprocal: bool = typer.Option(False, "--no-reciprocal", help="Don't remove reciprocal relationship"),
) -> None:
    """Remove a dependency relationship between tickets.
    
    This removes the 'blocked by' relationship where DEPENDENCY_ID blocks TICKET_ID.
    By default, also removes the reciprocal 'blocks' relationship.
    """
    root = ensure_gira_project()

    # Normalize ticket IDs
    ticket_id = ticket_id.upper()
    dependency_id = dependency_id.upper()

    # Find both tickets
    ticket, ticket_path = find_ticket(ticket_id, root)
    if not ticket:
        console.print(f"❌ Ticket '{ticket_id}' not found.", style="red")
        raise typer.Exit(1)

    dependency_ticket, dependency_path = find_ticket(dependency_id, root)
    if not dependency_ticket:
        console.print(f"❌ Dependency ticket '{dependency_id}' not found.", style="red")
        raise typer.Exit(1)

    # Check if dependency exists
    if dependency_id not in ticket.blocked_by:
        console.print(f"❌ Ticket '{ticket_id}' is not blocked by '{dependency_id}'.", style="red")
        raise typer.Exit(1)

    # Remove the dependency
    ticket.blocked_by.remove(dependency_id)

    # Update timestamp
    from datetime import datetime, timezone
    ticket.updated_at = datetime.now(timezone.utc)

    # Save the ticket
    ticket.save_to_json_file(str(ticket_path))

    # Remove reciprocal relationship if requested
    if not no_reciprocal:
        if ticket_id in dependency_ticket.blocks:
            dependency_ticket.blocks.remove(ticket_id)
            dependency_ticket.updated_at = datetime.now(timezone.utc)
            dependency_ticket.save_to_json_file(str(dependency_path))

    # Success message
    console.print(f"✅ Removed dependency: '{ticket_id}' is no longer blocked by '{dependency_id}'", style="green")
    if not no_reciprocal:
        console.print(f"✅ Removed reciprocal: '{dependency_id}' no longer blocks '{ticket_id}'", style="green")
