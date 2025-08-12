"""Add dependency command for Gira tickets."""

import typer
from gira.utils.console import console
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket
from gira.utils.typer_completion import complete_ticket_ids

def add_dep(
    ticket_id: str = typer.Argument(..., help="Ticket ID to add dependency to", autocompletion=complete_ticket_ids),
    dependency_id: str = typer.Argument(..., help="Ticket ID that this ticket depends on (blocks this ticket)", autocompletion=complete_ticket_ids),
    no_reciprocal: bool = typer.Option(False, "--no-reciprocal", help="Don't add reciprocal relationship"),
) -> None:
    """Add a dependency relationship between tickets.
    
    This creates a 'blocked by' relationship where DEPENDENCY_ID blocks TICKET_ID.
    By default, also adds the reciprocal 'blocks' relationship.
    """
    root = ensure_gira_project()

    # Normalize ticket IDs
    ticket_id = ticket_id.upper()
    dependency_id = dependency_id.upper()

    # Validate different tickets
    if ticket_id == dependency_id:
        console.print("❌ A ticket cannot depend on itself.", style="red")
        raise typer.Exit(1)

    # Find both tickets
    ticket, ticket_path = find_ticket(ticket_id, root)
    if not ticket:
        console.print(f"❌ Ticket '{ticket_id}' not found.", style="red")
        raise typer.Exit(1)

    dependency_ticket, dependency_path = find_ticket(dependency_id, root)
    if not dependency_ticket:
        console.print(f"❌ Dependency ticket '{dependency_id}' not found.", style="red")
        raise typer.Exit(1)

    # Check if dependency already exists
    if dependency_id in ticket.blocked_by:
        console.print(f"❌ Ticket '{ticket_id}' is already blocked by '{dependency_id}'.", style="red")
        raise typer.Exit(1)

    # Add the dependency
    ticket.blocked_by.append(dependency_id)
    ticket.blocked_by.sort()  # Keep sorted for consistency

    # Update timestamp
    from datetime import datetime, timezone
    ticket.updated_at = datetime.now(timezone.utc)

    # Save the ticket
    ticket.save_to_json_file(str(ticket_path))

    # Add reciprocal relationship if requested
    if not no_reciprocal:
        if ticket_id not in dependency_ticket.blocks:
            dependency_ticket.blocks.append(ticket_id)
            dependency_ticket.blocks.sort()
            dependency_ticket.updated_at = datetime.now(timezone.utc)
            dependency_ticket.save_to_json_file(str(dependency_path))

    # Success message
    console.print(f"✅ Added dependency: '{ticket_id}' is now blocked by '{dependency_id}'", style="green")
    if not no_reciprocal:
        console.print(f"✅ Added reciprocal: '{dependency_id}' now blocks '{ticket_id}'", style="green")
