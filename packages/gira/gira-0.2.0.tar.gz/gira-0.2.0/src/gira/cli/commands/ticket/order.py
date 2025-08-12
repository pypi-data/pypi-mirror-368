"""Order tickets within their status column."""

from typing import Optional

import typer
from gira.utils.console import console
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import get_ticket_path, load_ticket, save_ticket

def order(
    ticket_id: str = typer.Argument(..., help="Ticket ID to reorder"),
    position: Optional[int] = typer.Argument(None, help="New position (1-based)"),
    before: Optional[str] = typer.Option(None, "--before", help="Place before this ticket ID"),
    after: Optional[str] = typer.Option(None, "--after", help="Place after this ticket ID"),
) -> None:
    """Set the order of a ticket within its status column.
    
    Ordering only affects tickets within the same status/swimlane. When you move
    a ticket to a different status, it maintains its relative order if possible.
    
    Examples:
        # Position-based ordering (1 is top, 2 is second, etc.)
        gira ticket order GCM-123 1        # Move to top of column
        gira ticket order GCM-123 3        # Move to third position
        gira ticket order GCM-123 999      # Move to end (if position > ticket count)
        
        # Relative ordering
        gira ticket order GCM-123 --before GCM-456  # Place above GCM-456
        gira ticket order GCM-123 --after GCM-789   # Place below GCM-789
        
        # View current order
        gira board                         # Shows tickets in order
        gira ticket list --status todo     # Lists tickets in order
        
    Notes:
        - Position numbering starts at 1 (not 0)
        - Cannot combine position with --before/--after options
        - Tickets without explicit order appear at the bottom
        - Order values are automatically rebalanced when needed
        
    Error Handling:
        - Invalid position: Must be >= 1
        - Out of range position: Automatically places at end
        - Reference ticket not found: Shows error with ticket status
        - Multiple ordering options: Only one allowed per command
    """
    root = ensure_gira_project()

    # Validate inputs
    if position is None and before is None and after is None:
        console.print("[red]Error:[/red] Must specify position, --before, or --after")
        raise typer.Exit(1)

    if sum(x is not None for x in [position, before, after]) > 1:
        console.print("[red]Error:[/red] Can only specify one of: position, --before, --after")
        raise typer.Exit(1)

    # Load the ticket
    ticket = load_ticket(ticket_id.upper())
    if not ticket:
        console.print(f"[red]Error:[/red] Ticket {ticket_id} not found")
        raise typer.Exit(1)

    # Load all tickets in the same status using the utility function
    from gira.utils.ticket_utils import load_tickets_by_status
    
    all_tickets_in_status = load_tickets_by_status(ticket.status)
    tickets_in_status = [t for t in all_tickets_in_status if t.id != ticket.id]

    # Sort existing tickets by current order (and ID for stability)
    tickets_in_status.sort(key=lambda t: (t.order if t.order > 0 else float('inf'), t.id))

    # Determine new order value
    if position is not None:
        # Direct position specified
        if position < 1:
            console.print("[red]Error:[/red] Position must be >= 1")
            raise typer.Exit(1)

        # Maximum position is number of tickets plus 1 (to append at end)
        max_position = len(tickets_in_status) + 1
        if position > max_position:
            console.print(f"[red]Error:[/red] Position {position} is out of range (max: {max_position})")
            raise typer.Exit(1)

        # Calculate order value for the position
        if position == 1:
            # First position
            new_order = 10
        elif position > len(tickets_in_status):
            # Last position
            last_order = max((t.order for t in tickets_in_status if t.order > 0), default=0)
            new_order = last_order + 10
        else:
            # Middle position - find the gap
            sorted_orders = [t.order for t in tickets_in_status[:position-1] if t.order > 0]
            if sorted_orders:
                prev_order = sorted_orders[-1]
            else:
                prev_order = 0

            if position <= len(tickets_in_status):
                next_ticket = tickets_in_status[position-1]
                next_order = next_ticket.order if next_ticket.order > 0 else prev_order + 20
            else:
                next_order = prev_order + 20

            new_order = (prev_order + next_order) // 2

            # If no space, renumber all tickets
            if new_order <= prev_order:
                renumber_tickets(root, ticket.status, tickets_in_status + [ticket])
                # Reload ticket to get new order
                ticket = load_ticket(ticket_id.upper())
                console.print(f"✅ Moved ticket {ticket.id} to position {position}")
                return

    elif before:
        # Place before another ticket
        before_ticket = next((t for t in tickets_in_status if t.id == before.upper()), None)
        if not before_ticket:
            console.print(f"[red]Error:[/red] Ticket {before} not found in {ticket.status} status")
            raise typer.Exit(1)

        # Find the ticket that comes before the target
        before_idx = tickets_in_status.index(before_ticket)
        if before_idx == 0:
            new_order = max(1, before_ticket.order - 10)
        else:
            prev_ticket = tickets_in_status[before_idx - 1]
            prev_order = prev_ticket.order if prev_ticket.order > 0 else 0
            target_order = before_ticket.order if before_ticket.order > 0 else prev_order + 20
            new_order = (prev_order + target_order) // 2

            if new_order <= prev_order:
                renumber_tickets(root, ticket.status, tickets_in_status + [ticket])
                ticket = load_ticket(ticket_id.upper())
                console.print(f"✅ Moved ticket {ticket.id} before {before}")
                return

    else:  # after
        # Place after another ticket
        after_ticket = next((t for t in tickets_in_status if t.id == after.upper()), None)
        if not after_ticket:
            console.print(f"[red]Error:[/red] Ticket {after} not found in {ticket.status} status")
            raise typer.Exit(1)

        # Find the ticket that comes after the target
        after_idx = tickets_in_status.index(after_ticket)
        after_order = after_ticket.order if after_ticket.order > 0 else 10

        if after_idx == len(tickets_in_status) - 1:
            new_order = after_order + 10
        else:
            next_ticket = tickets_in_status[after_idx + 1]
            next_order = next_ticket.order if next_ticket.order > 0 else after_order + 20
            new_order = (after_order + next_order) // 2

            if new_order <= after_order:
                renumber_tickets(root, ticket.status, tickets_in_status + [ticket])
                ticket = load_ticket(ticket_id.upper())
                console.print(f"✅ Moved ticket {ticket.id} after {after}")
                return

    # Update ticket order
    ticket.order = new_order
    ticket_path = get_ticket_path(ticket.id, ticket.status, root)
    save_ticket(ticket, ticket_path)

    # Show success message
    if position:
        console.print(f"✅ Moved ticket {ticket.id} to position {position}")
    elif before:
        console.print(f"✅ Moved ticket {ticket.id} before {before}")
    else:
        console.print(f"✅ Moved ticket {ticket.id} after {after}")


def renumber_tickets(root, status: str, tickets: list) -> None:
    """Renumber all tickets in a status column with proper spacing."""
    # Sort by current order and ID
    tickets.sort(key=lambda t: (t.order if t.order > 0 else float('inf'), t.id))

    # Assign new order values with spacing
    for i, ticket in enumerate(tickets):
        ticket.order = (i + 1) * 10
        ticket_path = get_ticket_path(ticket.id, ticket.status, root)
        save_ticket(ticket, ticket_path)
