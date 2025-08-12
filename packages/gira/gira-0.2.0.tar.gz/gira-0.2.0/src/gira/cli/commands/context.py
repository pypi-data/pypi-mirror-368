"""Context command for displaying comprehensive ticket information."""

import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from collections import defaultdict

import typer
from rich import box
from gira.utils.console import console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.columns import Columns
from rich.text import Text

from gira.models import Ticket, Epic, Sprint, Comment
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket, load_all_tickets, is_ticket_archived
from gira.utils.git_integration import find_ticket_references_in_commits

def format_datetime(dt) -> str:
    """Format a datetime for display."""
    if dt:
        if hasattr(dt, 'strftime'):
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return str(dt)
    return "-"


# Create context app for subcommands
context_app = typer.Typer(
    name="context",
    help="Display comprehensive ticket context and relationships",
    add_completion=True,
    rich_markup_mode="markdown"
)


@context_app.callback(invoke_without_command=True)
def context_callback(
    ctx: typer.Context,
    ticket_id: Optional[str] = typer.Argument(None, help="Ticket ID to show context for"),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
    fields: Optional[str] = typer.Option(None, "--fields", "-f", help="Comma-separated list of fields to include"),
    include_archived: bool = typer.Option(False, "--include-archived", help="Include archived tickets in related items"),
):
    """Display comprehensive ticket context and relationships."""
    if ctx.invoked_subcommand is None:
        if ticket_id is None:
            console.print("[red]Error:[/red] Ticket ID is required")
            raise typer.Exit(2)
        # This is the default behavior - show context for the ticket
        show_context(ticket_id, output, fields, include_archived)


@context_app.command("show")
def show_command(
    ticket_id: str = typer.Argument(..., help="Ticket ID to show context for"),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
    fields: Optional[str] = typer.Option(None, "--fields", "-f", help="Comma-separated list of fields to include"),
    include_archived: bool = typer.Option(False, "--include-archived", help="Include archived tickets in related items"),
):
    """Display comprehensive context for a ticket (explicit show subcommand)."""
    show_context(ticket_id, output, fields, include_archived)


def show_context(
    ticket_id: str,
    output: str = "text",
    fields: Optional[str] = None,
    include_archived: bool = False,
) -> None:
    """Display comprehensive context for a ticket including all related information.
    
    Shows:
    - Ticket details and metadata
    - Epic information (if linked)
    - All comments and discussions
    - Dependencies (blocked_by, blocks)
    - Parent/child relationships
    - Sprint information
    - Related tickets (same epic, dependencies)
    """
    root = ensure_gira_project()
    
    # Find the ticket
    ticket, _ = find_ticket(ticket_id, root, include_archived=True)
    if not ticket:
        console.print(f"[red]Error:[/red] Ticket {ticket_id} not found")
        raise typer.Exit(1)
    
    # Gather all context data
    context_data = _gather_ticket_context(ticket, root, include_archived)
    
    # Output based on format
    if output == "json":
        # Filter fields if specified
        if fields:
            context_data = _filter_fields(context_data, fields.split(","))
        print(json.dumps(context_data, indent=2, default=str))
    else:
        _display_ticket_context(ticket, context_data)


def _gather_ticket_context(ticket: Ticket, root, include_archived: bool) -> Dict[str, Any]:
    """Gather all context data for a ticket."""
    context_data = {
        "ticket": ticket.model_dump(),
        "epic": None,
        "sprint": None,
        "comments": [],
        "parent": None,
        "children": [],
        "blocked_by": [],
        "blocks": [],
        "related_tickets": []
    }
    
    # Load epic if linked
    if ticket.epic_id:
        epic_path = root / ".gira" / "epics" / f"{ticket.epic_id}.json"
        if epic_path.exists():
            epic = Epic.from_json_file(str(epic_path))
            context_data["epic"] = epic.model_dump()
    
    # Load sprint if linked
    if ticket.sprint_id:
        # Check active sprints first
        sprint_path = root / ".gira" / "sprints" / "active" / f"{ticket.sprint_id}.json"
        if not sprint_path.exists():
            # Check completed sprints
            sprint_path = root / ".gira" / "sprints" / "completed" / f"{ticket.sprint_id}.json"
        if sprint_path.exists():
            sprint = Sprint.from_json_file(str(sprint_path))
            context_data["sprint"] = sprint.model_dump()
    
    # Load comments from separate files first
    comments_dir = root / ".gira" / "comments" / ticket.id
    if comments_dir.exists():
        for comment_file in sorted(comments_dir.glob("*.json")):
            comment = Comment.from_json_file(str(comment_file))
            context_data["comments"].append(comment.model_dump())
    
    # Also include comments stored directly in the ticket
    if ticket.comments:
        for comment in ticket.comments:
            # Convert Comment object to dict if needed
            if hasattr(comment, 'model_dump'):
                context_data["comments"].append(comment.model_dump())
            else:
                context_data["comments"].append(comment)
    
    # Load all tickets for relationship analysis
    all_tickets = load_all_tickets(include_archived=include_archived)
    
    # Find parent
    if ticket.parent_id:
        parent = next((t for t in all_tickets if t.id == ticket.parent_id), None)
        if parent:
            context_data["parent"] = parent.model_dump()
    
    # Find children
    children = [t for t in all_tickets if t.parent_id == ticket.id]
    context_data["children"] = [child.model_dump() for child in children]
    
    # Load blocked_by tickets
    for blocked_id in ticket.blocked_by:
        blocked_ticket = next((t for t in all_tickets if t.id == blocked_id), None)
        if blocked_ticket:
            context_data["blocked_by"].append(blocked_ticket.model_dump())
    
    # Load blocks tickets
    for blocks_id in ticket.blocks:
        blocks_ticket = next((t for t in all_tickets if t.id == blocks_id), None)
        if blocks_ticket:
            context_data["blocks"].append(blocks_ticket.model_dump())
    
    # Find related tickets (same epic, excluding current ticket)
    if ticket.epic_id and context_data["epic"]:
        # If not including archived, filter them out
        if not include_archived:
            # Need to check if tickets are archived by their file location
            epic_tickets = []
            for t in all_tickets:
                if t.epic_id == ticket.epic_id and t.id != ticket.id:
                    # Check if ticket is archived by finding it
                    _, t_path = find_ticket(t.id, root, include_archived=True)
                    if t_path and not is_ticket_archived(t_path):
                        epic_tickets.append(t)
        else:
            epic_tickets = [t for t in all_tickets 
                           if t.epic_id == ticket.epic_id and t.id != ticket.id]
        context_data["related_tickets"] = [t.model_dump() for t in epic_tickets]
    
    return context_data


def _filter_fields(data: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """Filter context data to include only specified fields."""
    # Handle nested field access (e.g., "epic.title")
    result = {}
    
    for field in fields:
        if "." in field:
            # Nested field
            parts = field.split(".", 1)
            parent_field = parts[0]
            child_field = parts[1]
            
            if parent_field in data and data[parent_field]:
                if parent_field not in result:
                    result[parent_field] = {}
                
                if isinstance(data[parent_field], dict):
                    # Single nested object
                    if child_field in data[parent_field]:
                        result[parent_field][child_field] = data[parent_field][child_field]
                elif isinstance(data[parent_field], list):
                    # List of objects
                    result[parent_field] = []
                    for item in data[parent_field]:
                        if isinstance(item, dict) and child_field in item:
                            result[parent_field].append({child_field: item[child_field]})
        else:
            # Top-level field
            if field in data:
                result[field] = data[field]
    
    return result


def _display_ticket_context(ticket: Ticket, context: Dict[str, Any]) -> None:
    """Display ticket context in a rich text format."""
    # Main ticket panel
    ticket_info = Table(show_header=False, box=box.SIMPLE)
    ticket_info.add_column(style="dim")
    ticket_info.add_column()
    
    ticket_info.add_row("Status:", ticket.status.replace("_", " ").title())
    ticket_info.add_row("Priority:", ticket.priority.title())
    ticket_info.add_row("Type:", ticket.type.title())
    ticket_info.add_row("Reporter:", ticket.reporter or "Unknown")
    ticket_info.add_row("Assignee:", ticket.assignee or "Unassigned")
    
    if ticket.story_points:
        ticket_info.add_row("Story Points:", str(ticket.story_points))
    
    if ticket.labels:
        ticket_info.add_row("Labels:", ", ".join(ticket.labels))
    
    ticket_info.add_row("Created:", format_datetime(ticket.created_at))
    ticket_info.add_row("Updated:", format_datetime(ticket.updated_at))
    
    console.print(Panel(
        ticket_info,
        title=f"[bold]{ticket.id}[/bold] - {ticket.title}",
        title_align="left",
        border_style="green"
    ))
    
    if ticket.description:
        # Check if we should render markdown
        from gira.utils.display import render_markdown_content
        
        markdown_content = render_markdown_content(ticket.description)
        
        if markdown_content:
            # Use markdown rendering
            console.print(Panel(
                markdown_content,
                title="Description",
                title_align="left",
                border_style="dim"
            ))
        else:
            # Fall back to plain text
            console.print(Panel(
                ticket.description,
                title="Description",
                title_align="left",
                border_style="dim"
            ))
    
    # Epic information
    if context["epic"]:
        epic = context["epic"]
        epic_info = f"[bold]{epic['id']}[/bold] - {epic['title']}\n"
        epic_info += f"Status: {epic['status'].title()}\n"
        epic_info += f"Progress: {len([t for t in epic['tickets'] if t])} tickets"
        
        console.print(Panel(
            epic_info,
            title="Epic",
            title_align="left",
            border_style="blue"
        ))
    
    # Sprint information
    if context["sprint"]:
        sprint = context["sprint"]
        sprint_info = f"[bold]{sprint['name']}[/bold]\n"
        sprint_info += f"Status: {sprint['status'].title()}\n"
        sprint_info += f"Duration: {sprint['start_date']} to {sprint['end_date']}"
        
        console.print(Panel(
            sprint_info,
            title="Sprint",
            title_align="left",
            border_style="cyan"
        ))
    
    # Relationships tree
    if any([context["parent"], context["children"], context["blocked_by"], context["blocks"]]):
        tree = Tree("📊 Relationships")
        
        if context["parent"]:
            parent = context["parent"]
            tree.add(f"⬆️  Parent: [bold]{parent['id']}[/bold] - {parent['title']}")
        
        if context["children"]:
            children_branch = tree.add("⬇️  Children")
            for child in context["children"]:
                children_branch.add(f"[bold]{child['id']}[/bold] - {child['title']} ({child['status']})")
        
        if context["blocked_by"]:
            blocked_branch = tree.add("🚫 Blocked By")
            for blocker in context["blocked_by"]:
                blocked_branch.add(f"[bold]{blocker['id']}[/bold] - {blocker['title']} ({blocker['status']})")
        
        if context["blocks"]:
            blocks_branch = tree.add("⛔ Blocks")
            for blocked in context["blocks"]:
                blocks_branch.add(f"[bold]{blocked['id']}[/bold] - {blocked['title']} ({blocked['status']})")
        
        console.print(tree)
    
    # Comments
    if context["comments"]:
        console.print(f"\n💬 [bold]Comments ({len(context['comments'])})[/bold]")
        for i, comment in enumerate(context["comments"]):
            if i > 0:
                console.print("─" * 40, style="dim")
            
            header = f"[dim]{comment['author']} • {format_datetime(comment['created_at'])}[/dim]"
            if comment.get('edited_at'):
                header += f" [dim](edited {format_datetime(comment['edited_at'])})[/dim]"
            
            console.print(header)
            
            # Render comment content as markdown
            from gira.utils.display import render_markdown_content
            
            markdown_content = render_markdown_content(comment['content'])
            if markdown_content:
                console.print(markdown_content)
            else:
                console.print(comment['content'])
    
    # Related tickets
    if context["related_tickets"]:
        console.print(f"\n🔗 [bold]Related Tickets (Same Epic)[/bold]")
        
        related_table = Table(show_header=True, box=box.ROUNDED)
        related_table.add_column("ID", style="cyan")
        related_table.add_column("Title")
        related_table.add_column("Status", style="yellow")
        related_table.add_column("Priority")
        
        for related in context["related_tickets"]:
            priority_style = "red" if related["priority"] == "high" else "yellow" if related["priority"] == "medium" else "dim"
            related_table.add_row(
                related["id"],
                related["title"],
                related["status"].replace("_", " ").title(),
                f"[{priority_style}]{related['priority'].title()}[/{priority_style}]"
            )
        
        console.print(related_table)


@context_app.command("tree")
def tree_view(
    ticket_id: str = typer.Argument(..., help="Ticket ID to show dependency tree for"),
    max_depth: int = typer.Option(3, "--max-depth", "-d", help="Maximum tree depth"),
    include_archived: bool = typer.Option(False, "--include-archived", help="Include archived tickets"),
):
    """Show visual dependency tree for a ticket."""
    root = ensure_gira_project()
    
    # Find the ticket
    ticket, _ = find_ticket(ticket_id, root, include_archived=True)
    if not ticket:
        console.print(f"[red]Error:[/red] Ticket {ticket_id} not found")
        raise typer.Exit(1)
    
    # Load all tickets for dependency analysis
    all_tickets = load_all_tickets(include_archived=include_archived)
    tickets_by_id = {t.id: t for t in all_tickets}
    
    # Build and display dependency tree
    tree = Tree(f"[bold cyan]{ticket.id}[/bold cyan]: {ticket.title}")
    
    # Add blocks relationships
    if ticket.blocks:
        blocks_branch = tree.add("[green]→ blocks[/green]")
        for blocked_id in ticket.blocks:
            if blocked_id in tickets_by_id:
                blocked = tickets_by_id[blocked_id]
                _add_dependency_branch(blocks_branch, blocked, tickets_by_id, "blocks", 1, max_depth)
    
    # Add blocked_by relationships
    if ticket.blocked_by:
        blocked_by_branch = tree.add("[red]← blocked_by[/red]")
        for blocker_id in ticket.blocked_by:
            if blocker_id in tickets_by_id:
                blocker = tickets_by_id[blocker_id]
                _add_dependency_branch(blocked_by_branch, blocker, tickets_by_id, "blocked_by", 1, max_depth)
    
    console.print(tree)


def _add_dependency_branch(parent_branch, ticket: Ticket, tickets_by_id: Dict[str, Ticket], 
                          relation_type: str, current_depth: int, max_depth: int):
    """Recursively add dependency branches to tree."""
    status_color = {
        "done": "green",
        "in_progress": "yellow",
        "review": "blue",
        "todo": "dim"
    }.get(ticket.status, "white")
    
    node_text = f"[bold]{ticket.id}[/bold]: {ticket.title} [[{status_color}]{ticket.status}[/{status_color}]]"
    branch = parent_branch.add(node_text)
    
    if current_depth < max_depth:
        # Add nested dependencies
        if relation_type == "blocks" and ticket.blocks:
            for blocked_id in ticket.blocks:
                if blocked_id in tickets_by_id:
                    _add_dependency_branch(branch, tickets_by_id[blocked_id], tickets_by_id, 
                                         "blocks", current_depth + 1, max_depth)
        elif relation_type == "blocked_by" and ticket.blocked_by:
            for blocker_id in ticket.blocked_by:
                if blocker_id in tickets_by_id:
                    _add_dependency_branch(branch, tickets_by_id[blocker_id], tickets_by_id, 
                                         "blocked_by", current_depth + 1, max_depth)


@context_app.command("epic")
def epic_view(
    ticket_id: str = typer.Argument(..., help="Ticket ID to show in epic context"),
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all epic tickets, not just related"),
):
    """Show ticket in the context of its epic."""
    root = ensure_gira_project()
    
    # Find the ticket
    ticket, _ = find_ticket(ticket_id, root, include_archived=True)
    if not ticket:
        console.print(f"[red]Error:[/red] Ticket {ticket_id} not found")
        raise typer.Exit(1)
    
    if not ticket.epic_id:
        console.print(f"[yellow]Note:[/yellow] Ticket {ticket_id} is not linked to an epic")
        raise typer.Exit(0)
    
    # Load epic
    epic_path = root / ".gira" / "epics" / f"{ticket.epic_id}.json"
    if not epic_path.exists():
        console.print(f"[red]Error:[/red] Epic {ticket.epic_id} not found")
        raise typer.Exit(1)
    
    epic = Epic.from_json_file(str(epic_path))
    
    # Load all epic tickets
    all_tickets = load_all_tickets(include_archived=True)
    epic_tickets = [t for t in all_tickets if t.epic_id == epic.id]
    
    # Calculate completion
    done_count = len([t for t in epic_tickets if t.status == "done"])
    total_count = len(epic_tickets)
    completion = (done_count / total_count * 100) if total_count > 0 else 0
    
    # Display epic header
    console.print(Panel(
        f"[bold]{epic.id}[/bold]: {epic.title}\n"
        f"Status: {epic.status.title()}\n"
        f"Progress: {done_count}/{total_count} tickets ({completion:.0f}% complete)",
        title="Epic Overview",
        border_style="blue"
    ))
    
    # Build epic tree
    tree = Tree(f"[bold blue]{epic.id}[/bold blue]: {epic.title} ({completion:.0f}% complete)")
    
    # Group tickets by status
    tickets_by_status = defaultdict(list)
    for t in epic_tickets:
        tickets_by_status[t.status].append(t)
    
    # Display tickets by status
    status_order = ["done", "review", "in_progress", "todo"]
    status_symbols = {
        "done": "✓",
        "review": "⟳",
        "in_progress": "◐",
        "todo": "○"
    }
    
    for status in status_order:
        if status in tickets_by_status:
            for t in tickets_by_status[status]:
                symbol = status_symbols.get(status, "•")
                is_current = t.id == ticket_id
                node_text = f"{symbol} [bold]{t.id}[/bold]: {t.title} [{status}]"
                if is_current:
                    node_text += " [yellow]← YOU ARE HERE[/yellow]"
                tree.add(node_text)
    
    console.print(tree)


@context_app.command("timeline")
def timeline_view(
    ticket_id: str = typer.Argument(..., help="Ticket ID to show timeline for"),
    days: int = typer.Option(30, "--days", "-d", help="Number of days to show"),
):
    """Show activity timeline for a ticket."""
    root = ensure_gira_project()
    
    # Find the ticket
    ticket, ticket_path = find_ticket(ticket_id, root, include_archived=True)
    if not ticket:
        console.print(f"[red]Error:[/red] Ticket {ticket_id} not found")
        raise typer.Exit(1)
    
    # Gather timeline events
    events = []
    
    # Creation event
    events.append({
        "time": ticket.created_at,
        "type": "created",
        "description": f"Created by {ticket.reporter or 'unknown'}"
    })
    
    # Status changes (would need to parse from git history or audit log)
    # For now, just show current status
    if ticket.updated_at != ticket.created_at:
        events.append({
            "time": ticket.updated_at,
            "type": "updated",
            "description": f"Updated (current status: {ticket.status})"
        })
    
    # Comments
    context_data = _gather_ticket_context(ticket, root, True)
    for comment in context_data["comments"]:
        events.append({
            "time": comment["created_at"],
            "type": "comment",
            "description": f"Comment by {comment['author']}: \"{comment['content'][:50]}...\""
        })
    
    # Sort events by time
    events.sort(key=lambda e: e["time"] if isinstance(e["time"], str) else str(e["time"]))
    
    # Display timeline
    console.print(Panel(
        f"Activity timeline for [bold]{ticket_id}[/bold]: {ticket.title}",
        title="Timeline",
        border_style="cyan"
    ))
    
    table = Table(show_header=False, box=box.SIMPLE)
    table.add_column("Time", style="dim")
    table.add_column("Event")
    
    for event in events:
        time_str = format_datetime(event["time"])
        event_style = {
            "created": "green",
            "updated": "yellow",
            "comment": "blue"
        }.get(event["type"], "white")
        
        table.add_row(
            time_str,
            f"[{event_style}]{event['description']}[/{event_style}]"
        )
    
    console.print(table)


@context_app.command("related")
def related_view(
    ticket_id: str = typer.Argument(..., help="Ticket ID to find related tickets for"),
    max_results: int = typer.Option(10, "--max", "-m", help="Maximum results per category"),
):
    """Find tickets related by various criteria."""
    root = ensure_gira_project()
    
    # Find the ticket
    ticket, _ = find_ticket(ticket_id, root, include_archived=True)
    if not ticket:
        console.print(f"[red]Error:[/red] Ticket {ticket_id} not found")
        raise typer.Exit(1)
    
    # Load all tickets
    all_tickets = load_all_tickets(include_archived=False)
    
    # Find related tickets by different criteria
    related = {
        "same_author": [],
        "same_labels": [],
        "similar_title": []
    }
    
    for t in all_tickets:
        if t.id == ticket_id:
            continue
        
        # Same author
        if t.reporter == ticket.reporter and len(related["same_author"]) < max_results:
            related["same_author"].append(t)
        
        # Same labels
        if ticket.labels and t.labels:
            common_labels = set(ticket.labels) & set(t.labels)
            if common_labels and len(related["same_labels"]) < max_results:
                related["same_labels"].append((t, common_labels))
        
        # Similar title (simple word matching)
        if ticket.title and t.title:
            ticket_words = set(ticket.title.lower().split())
            t_words = set(t.title.lower().split())
            common_words = ticket_words & t_words
            # Ignore common words
            common_words -= {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
            if len(common_words) >= 2 and len(related["similar_title"]) < max_results:
                related["similar_title"].append(t)
    
    # Display results
    console.print(Panel(
        f"Related tickets for [bold]{ticket_id}[/bold]: {ticket.title}",
        title="Related Tickets",
        border_style="magenta"
    ))
    
    if related["same_author"]:
        console.print(f"\n[bold]Same Author ({ticket.reporter}):[/bold]")
        for t in related["same_author"]:
            console.print(f"  • [cyan]{t.id}[/cyan]: {t.title} [{t.status}]")
    
    if related["same_labels"]:
        console.print(f"\n[bold]Same Labels:[/bold]")
        for t, labels in related["same_labels"]:
            labels_str = ", ".join(labels)
            console.print(f"  • [cyan]{t.id}[/cyan]: {t.title} [dim]({labels_str})[/dim]")
    
    if related["similar_title"]:
        console.print(f"\n[bold]Similar Titles:[/bold]")
        for t in related["similar_title"]:
            console.print(f"  • [cyan]{t.id}[/cyan]: {t.title} [{t.status}]")


@context_app.command("references")
def references_view(
    ticket_id: str = typer.Argument(..., help="Ticket ID to find references for"),
):
    """Show where this ticket is referenced (comments, commits)."""
    root = ensure_gira_project()
    
    # Find the ticket
    ticket, _ = find_ticket(ticket_id, root, include_archived=True)
    if not ticket:
        console.print(f"[red]Error:[/red] Ticket {ticket_id} not found")
        raise typer.Exit(1)
    
    console.print(Panel(
        f"References to [bold]{ticket_id}[/bold]: {ticket.title}",
        title="Cross-References",
        border_style="yellow"
    ))
    
    # Find references in comments
    all_tickets = load_all_tickets(include_archived=True)
    comment_refs = []
    
    for t in all_tickets:
        if t.id == ticket_id:
            continue
        
        # Check ticket comments
        context_data = _gather_ticket_context(t, root, True)
        for comment in context_data["comments"]:
            if ticket_id in comment["content"]:
                comment_refs.append({
                    "ticket": t,
                    "comment": comment
                })
    
    if comment_refs:
        console.print("\n[bold]Referenced in Comments:[/bold]")
        for ref in comment_refs:
            console.print(f"  • [cyan]{ref['ticket'].id}[/cyan]: \"{ref['comment']['content'][:80]}...\"")
    
    # Find references in git commits
    try:
        commit_refs = find_ticket_references_in_commits(ticket_id, limit=10)
        if commit_refs:
            console.print("\n[bold]Referenced in Commits:[/bold]")
            for commit in commit_refs:
                message_first_line = commit['message'].split('\n')[0]
                console.print(f"  • [dim]{commit['sha'][:8]}[/dim]: {message_first_line}")
    except Exception:
        # Git integration might not be available
        pass


# Keep the original context function for backward compatibility
def context(
    ticket_id: str = typer.Argument(..., help="Ticket ID to show context for"),
    output: str = typer.Option("text", "--output", "-o", help="Output format: text, json"),
    fields: Optional[str] = typer.Option(None, "--fields", "-f", help="Comma-separated list of fields to include"),
    include_archived: bool = typer.Option(False, "--include-archived", help="Include archived tickets in related items"),
) -> None:
    """Display comprehensive context for a ticket including all related information."""
    show_context(ticket_id, output, fields, include_archived)