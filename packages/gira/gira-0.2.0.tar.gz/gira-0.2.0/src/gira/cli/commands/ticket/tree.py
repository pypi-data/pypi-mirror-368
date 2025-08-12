"""Ticket tree visualization command."""

import typer
from gira.utils.console import console
from rich.text import Text

from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket, load_all_tickets
from gira.utils.typer_completion import complete_ticket_ids

def tree(
    ticket_id: str = typer.Argument(..., help="Ticket ID to display tree for", autocompletion=complete_ticket_ids),
) -> None:
    """Display parent ticket and all subtasks in a hierarchical tree view."""
    # Find project root and validate
    project_root = ensure_gira_project()

    # Find the requested ticket (including archived)
    target_ticket, ticket_path = find_ticket(ticket_id, project_root, include_archived=True)

    if not target_ticket:
        console.print(f"❌ Ticket '{ticket_id}' not found.", style="red")
        raise typer.Exit(1)

    # Load all tickets (including archived)
    tickets = load_all_tickets(project_root, include_archived=True)

    # Build and display the tree
    _display_tree(target_ticket, tickets, target_ticket.id.upper())




def _display_tree(target_ticket, all_tickets, display_id):
    """Display the ticket tree with ASCII formatting."""
    # Find the root ticket (either the target or its ultimate parent)
    root_ticket = _find_root_ticket(target_ticket, all_tickets)

    # Build the tree structure
    tree_structure = _build_tree_structure(root_ticket, all_tickets)

    # Display the tree
    console.print(f"\n📋 Ticket Tree for {display_id}", style="bold blue")
    console.print()
    _print_tree_node(tree_structure, "", True)


def _find_root_ticket(ticket, all_tickets):
    """Find the root ticket (topmost parent) for a given ticket."""
    current = ticket

    # Keep going up the parent chain until we find a ticket with no parent
    while current.parent_id:
        parent = None
        for t in all_tickets:
            if t.id == current.parent_id:
                parent = t
                break

        if parent:
            current = parent
        else:
            # Parent not found, current ticket is the root
            break

    return current


def _build_tree_structure(root_ticket, all_tickets):
    """Build a nested tree structure starting from the root ticket."""
    def build_node(ticket):
        # Find all direct children of this ticket
        children = []
        for t in all_tickets:
            if t.parent_id == ticket.id:
                children.append(build_node(t))

        return {
            'ticket': ticket,
            'children': sorted(children, key=lambda x: x['ticket'].id)
        }

    return build_node(root_ticket)


def _print_tree_node(node, prefix, is_last):
    """Recursively print a tree node with ASCII formatting."""
    ticket = node['ticket']
    children = node['children']

    # Format ticket info
    ticket_info = _format_ticket_info(ticket)

    # Print current node
    console.print(f"{prefix}{ticket_info}")

    # Print children with proper tree structure
    for i, child in enumerate(children):
        is_last_child = i == len(children) - 1
        child_symbol = "└── " if is_last_child else "├── "
        child_prefix = prefix + ("    " if is_last_child else "│   ")

        # Print child with symbol
        child_info = _format_ticket_info(child['ticket'])
        console.print(f"{prefix}{child_symbol}{child_info}")

        # Recursively print grandchildren with proper structure
        if child['children']:
            for j, grandchild in enumerate(child['children']):
                is_last_grandchild = j == len(child['children']) - 1
                grandchild_symbol = "└── " if is_last_grandchild else "├── "
                grandchild_prefix = child_prefix + ("    " if is_last_grandchild else "│   ")

                grandchild_info = _format_ticket_info(grandchild['ticket'])
                console.print(f"{child_prefix}{grandchild_symbol}{grandchild_info}")

                # Continue recursively for deeper levels (rarely needed but supported)
                for k, great_grandchild in enumerate(grandchild['children']):
                    is_last_ggc = k == len(grandchild['children']) - 1
                    ggc_symbol = "└── " if is_last_ggc else "├── "
                    ggc_info = _format_ticket_info(great_grandchild['ticket'])
                    console.print(f"{grandchild_prefix}{ggc_symbol}{ggc_info}")


def _format_ticket_info(ticket):
    """Format ticket information for display in the tree."""
    from gira.utils.project import get_gira_root
    from gira.utils.ticket_utils import find_ticket, is_ticket_archived

    # Check if ticket is archived
    root = get_gira_root()
    _, ticket_path = find_ticket(ticket.id, root, include_archived=True)
    is_archived = is_ticket_archived(ticket_path) if ticket_path else False

    # Status color mapping
    status_colors = {
        "todo": "yellow",
        "in_progress": "blue",
        "review": "magenta",
        "done": "green",
        "blocked": "red"
    }

    # Priority symbols
    priority_symbols = {
        "low": "🔵",
        "medium": "🟡",
        "high": "🔴",
        "critical": "⚠️"
    }

    status_color = status_colors.get(ticket.status, "white")
    priority_symbol = priority_symbols.get(ticket.priority, "⚪")

    # Build the formatted string
    ticket_text = Text()
    ticket_text.append(f"{ticket.id}", style="bold")
    ticket_text.append(f" {priority_symbol}")
    ticket_text.append(f" [{ticket.status.replace('_', ' ').title()}]", style=status_color)
    ticket_text.append(f" {ticket.title}")

    if ticket.assignee:
        ticket_text.append(f" (@{ticket.assignee.split('@')[0]})", style="dim")

    if is_archived:
        ticket_text.append(" [ARCHIVED]", style="dim red")

    return ticket_text
