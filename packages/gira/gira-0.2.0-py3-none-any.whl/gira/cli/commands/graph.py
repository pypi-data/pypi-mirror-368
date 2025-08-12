"""Relationship graph visualization command."""

from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict

import typer
from gira.utils.console import console
from gira.utils.help_formatter import create_example, format_examples_simple
from rich.tree import Tree
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.layout import Layout
from rich import box

from gira.models import Ticket, Epic
# Removed format_ticket_id import as it doesn't exist
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket, load_all_tickets
from gira.utils.graph_visuals import GraphVisuals
from gira.utils.graph_export import GraphExporter


def load_all_epics(root) -> List[Epic]:
    """Load all epics from the project."""
    epics_dir = root / ".gira" / "epics"
    epics = []

    if epics_dir.exists():
        for epic_file in epics_dir.glob("EPIC-*.json"):
            try:
                epic = Epic.from_json_file(str(epic_file))
                epics.append(epic)
            except Exception as e:
                console.print(f"[yellow]Warning:[/yellow] Failed to load {epic_file.name}: {e}")

    return epics

def build_dependency_graph(
    ticket_id: str,
    gira_root,
    depth: int = 3,
    visited: Optional[Set[str]] = None
) -> Dict[str, Dict]:
    """Build a dependency graph starting from a ticket.
    
    Returns a dictionary with:
    - ticket: The ticket object
    - blocks: List of tickets this ticket blocks
    - blocked_by: List of tickets this ticket is blocked by
    - parent: Parent ticket if exists
    - children: List of child tickets
    - epic: Epic if ticket belongs to one
    """
    if visited is None:
        visited = set()
    
    if ticket_id in visited:
        return None
    
    visited.add(ticket_id)
    
    # Find the ticket
    ticket, _ = find_ticket(ticket_id, gira_root, include_archived=True)
    if not ticket:
        return None
    
    graph = {
        "ticket": ticket,
        "blocks": [],
        "blocked_by": [],
        "parent": None,
        "children": [],
        "epic": None
    }
    
    # Only fetch relationships if depth > 0
    if depth > 0:
        # Get blocking relationships
        if ticket.blocks:
            for blocked_id in ticket.blocks:
                blocked_ticket, _ = find_ticket(blocked_id, gira_root, include_archived=True)
                if blocked_ticket:
                    graph["blocks"].append(blocked_ticket)
        
        if ticket.blocked_by:
            for blocker_id in ticket.blocked_by:
                blocker_ticket, _ = find_ticket(blocker_id, gira_root, include_archived=True)
                if blocker_ticket:
                    graph["blocked_by"].append(blocker_ticket)
        
        # Get parent/child relationships
        if ticket.parent_id:
            parent_ticket, _ = find_ticket(ticket.parent_id, gira_root, include_archived=True)
            if parent_ticket:
                graph["parent"] = parent_ticket
        
        # Find children - need to search all tickets
        all_tickets = load_all_tickets(gira_root, include_archived=True)
        for t in all_tickets:
            if t.parent_id == ticket.id:
                graph["children"].append(t)
        
        # Get epic if exists
        if ticket.epic_id:
            from gira.models import Epic
            epic_file = gira_root / ".gira" / "epics" / f"{ticket.epic_id}.json"
            if epic_file.exists():
                try:
                    graph["epic"] = Epic.from_json_file(str(epic_file))
                except:
                    pass
    
    return graph


def create_tree_node(
    ticket: Ticket,
    relationship: str = "",
    status_color: bool = True,
    use_icons: bool = True
) -> str:
    """Create a formatted tree node for a ticket with enhanced visuals."""
    # Use the enhanced visual formatter
    return GraphVisuals.format_ticket_node(
        ticket,
        relationship=relationship,
        show_icons=use_icons,
        show_priority=True,
        truncate_title=50
    )


def add_relationships_to_tree(
    tree: Tree,
    graph: Dict,
    visited: Set[str],
    gira_root,
    depth: int,
    show_blockers: bool = True,
    show_blocks: bool = True,
    show_parent: bool = True,
    show_children: bool = True,
    show_epic: bool = True
) -> None:
    """Recursively add relationships to a Rich tree."""
    ticket = graph["ticket"]
    
    # Add epic relationship
    if show_epic and graph["epic"]:
        epic = graph["epic"]
        epic_node = tree.add(f"[magenta]Epic:[/magenta] {epic.id} - {epic.title}")
    
    # Add parent relationship
    if show_parent and graph["parent"]:
        parent = graph["parent"]
        parent_node = tree.add(create_tree_node(parent, "Parent:"))
        
        # Recursively add parent's relationships
        if depth > 1:
            parent_graph = build_dependency_graph(
                parent.id, gira_root, depth - 1, visited
            )
            if parent_graph:
                add_relationships_to_tree(
                    parent_node, parent_graph, visited, gira_root, depth - 1,
                    show_blockers, show_blocks, False, show_children, False
                )
    
    # Add blocking relationships
    if show_blockers and graph["blocked_by"]:
        blockers_node = tree.add("[red]Blocked by:[/red]")
        for blocker in graph["blocked_by"]:
            blocker_node = blockers_node.add(create_tree_node(blocker))
            
            # Recursively add blocker's relationships
            if depth > 1:
                blocker_graph = build_dependency_graph(
                    blocker.id, gira_root, depth - 1, visited
                )
                if blocker_graph:
                    add_relationships_to_tree(
                        blocker_node, blocker_graph, visited, gira_root, depth - 1,
                        show_blockers, False, False, False, False
                    )
    
    # Add tickets this blocks
    if show_blocks and graph["blocks"]:
        blocks_node = tree.add("[yellow]Blocks:[/yellow]")
        for blocked in graph["blocks"]:
            blocked_node = blocks_node.add(create_tree_node(blocked))
            
            # Recursively add blocked ticket's relationships
            if depth > 1:
                blocked_graph = build_dependency_graph(
                    blocked.id, gira_root, depth - 1, visited
                )
                if blocked_graph:
                    add_relationships_to_tree(
                        blocked_node, blocked_graph, visited, gira_root, depth - 1,
                        False, show_blocks, False, False, False
                    )
    
    # Add children
    if show_children and graph["children"]:
        children_node = tree.add("[green]Children:[/green]")
        for child in graph["children"]:
            child_node = children_node.add(create_tree_node(child))
            
            # Recursively add child's relationships
            if depth > 1:
                child_graph = build_dependency_graph(
                    child.id, gira_root, depth - 1, visited
                )
                if child_graph:
                    add_relationships_to_tree(
                        child_node, child_graph, visited, gira_root, depth - 1,
                        show_blockers, show_blocks, False, show_children, False
                    )


def graph_command(
    entity_args: Optional[List[str]] = typer.Argument(
        None, 
        help="Ticket ID (e.g., GCM-123) or epic command (e.g., epic EPIC-001)"
    ),
    depth: int = typer.Option(
        2,
        "--depth", "-d",
        help="Maximum depth to traverse relationships"
    ),
    show_blockers: bool = typer.Option(
        True,
        "--blockers/--no-blockers",
        help="Show tickets that block this ticket"
    ),
    show_blocks: bool = typer.Option(
        True,
        "--blocks/--no-blocks",
        help="Show tickets blocked by this ticket"
    ),
    show_parent: bool = typer.Option(
        True,
        "--parent/--no-parent",
        help="Show parent ticket relationship"
    ),
    show_children: bool = typer.Option(
        True,
        "--children/--no-children",
        help="Show child tickets"
    ),
    show_epic_rel: bool = typer.Option(
        True,
        "--epic/--no-epic",
        help="Show epic relationship"
    ),
    output_format: str = typer.Option(
        "tree",
        "--format", "-f",
        help="Output format: tree, json"
    ),
    # Epic-specific options
    epics: bool = typer.Option(
        False,
        "--epics",
        help="Show all epics overview"
    ),
    epic_deps: bool = typer.Option(
        False,
        "--epic-deps",
        help="Show dependencies between epics"
    ),
    mixed: bool = typer.Option(
        False,
        "--mixed",
        help="Show mixed view of epics and tickets"
    ),
    status: Optional[str] = typer.Option(
        None,
        "--status", "-s",
        help="Filter epics by status (for --epics mode)"
    ),
    owner: Optional[str] = typer.Option(
        None,
        "--owner", "-o",
        help="Filter epics by owner (for --epics mode)"
    ),
    min_progress: Optional[int] = typer.Option(
        None,
        "--min-progress",
        help="Filter epics by minimum progress percentage"
    ),
    all_tickets: bool = typer.Option(
        False,
        "--all-tickets",
        help="Show all tickets in epic view (default shows first 5 per status)"
    ),
    # Enhanced display options
    compact: bool = typer.Option(
        False,
        "--compact",
        help="Use compact mode for large graphs"
    ),
    show_stats: bool = typer.Option(
        False,
        "--stats",
        help="Show graph statistics panel"
    ),
    show_legend: bool = typer.Option(
        False,
        "--legend",
        help="Show legend for icons and colors"
    ),
    enhanced: bool = typer.Option(
        False,
        "--enhanced",
        help="Use enhanced visual display with panels"
    ),
    # Export options
    export: Optional[str] = typer.Option(
        None,
        "--export",
        help="Export graph to file (format determined by extension: .svg, .png, .html, .mermaid, .dot)"
    )
) -> None:
    f"""Visualize ticket and epic relationships and dependencies.
    
    Shows graphs for:
    - Ticket relationships (blocking/blocked by, parent/child, epic membership)
    - Epic overviews with progress and ticket breakdowns
    - Epic dependencies and cross-epic relationships
    - Mixed views showing both epics and tickets
    {format_examples_simple([
        create_example("Show relationships for a ticket", "gira graph GCM-123"),
        create_example("Show a specific epic", "gira graph epic EPIC-001"),
        create_example("Show all epics overview", "gira graph --epics"),
        create_example("Show epic dependencies", "gira graph --epic-deps"),
        create_example("Show mixed view", "gira graph --mixed"),
        create_example("Filter epics by status and progress", "gira graph --epics --status active --min-progress 50"),
        create_example("Show all tickets in epic (not just first 5)", "gira graph epic EPIC-001 --all-tickets")
    ])}"""
    gira_root = ensure_gira_project()
    
    # Handle epic-specific modes
    if epics:
        visualize_epic_overview(gira_root, show_progress=True, min_progress=min_progress,
                              status_filter=status, owner_filter=owner)
        return
    
    if epic_deps:
        visualize_epic_dependencies(gira_root)
        return
    
    if mixed:
        visualize_mixed_view(gira_root, max_depth=depth)
        return
    
    # Parse entity arguments
    entity_id = None
    if entity_args:
        # Check if it's an epic command
        if len(entity_args) == 2 and entity_args[0].lower() == "epic":
            epic_id = entity_args[1].upper()
            visualize_single_epic(epic_id, gira_root, show_all_tickets=all_tickets)
            return
        elif len(entity_args) == 1:
            # Check if it's a single string like "epic EPIC-001"
            if entity_args[0].lower().startswith("epic "):
                epic_id = entity_args[0][5:].strip().upper()
                visualize_single_epic(epic_id, gira_root, show_all_tickets=all_tickets)
                return
            else:
                # It's a ticket ID
                entity_id = entity_args[0]
        else:
            console.print("[red]Error:[/red] Invalid arguments. Use 'gira graph GCM-123' or 'gira graph epic EPIC-001'")
            raise typer.Exit(1)
    
    # Default help if no entity specified
    if not entity_id:
        # If no entity specified and no epic mode, show help
        console.print("[yellow]No entity specified. Use one of:[/yellow]")
        console.print("  gira graph GCM-123        # Show ticket relationships")
        console.print("  gira graph epic EPIC-001  # Show epic details")
        console.print("  gira graph --epics        # Show all epics")
        console.print("  gira graph --epic-deps    # Show epic dependencies")
        console.print("  gira graph --mixed        # Show mixed view")
        console.print("\n[dim]Enhanced options:[/dim]")
        console.print("  --enhanced                # Use rich visual display")
        console.print("  --compact                 # Compact mode for large graphs")
        console.print("  --stats                   # Show statistics panel")
        console.print("  --legend                  # Show icon/color legend")
        console.print("\n[dim]Export options:[/dim]")
        console.print("  --export graph.html       # Interactive HTML")
        console.print("  --export graph.mermaid    # Mermaid diagram")
        console.print("  --export graph.dot        # Graphviz DOT")
        raise typer.Exit(0)
    
    ticket_id = entity_id
    
    # Build the dependency graph
    graph = build_dependency_graph(ticket_id, gira_root, depth)
    
    if not graph:
        console.print(f"[red]Error:[/red] Ticket {ticket_id} not found")
        raise typer.Exit(1)
    
    ticket = graph["ticket"]
    
    # Handle export if requested
    if export:
        # Determine format from file extension
        export_format = None
        if export.endswith('.html'):
            export_format = 'html'
        elif export.endswith('.mermaid') or export.endswith('.md'):
            export_format = 'mermaid'
        elif export.endswith('.dot') or export.endswith('.gv'):
            export_format = 'dot'
        elif export.endswith('.json'):
            export_format = 'json'
        else:
            console.print(f"[red]Error:[/red] Unsupported export format. Use .html, .mermaid, .dot, or .json")
            raise typer.Exit(1)
        
        # Export the graph
        output_path = GraphExporter.export_graph(
            graph,
            format=export_format,
            output_path=export,
            title=f"Dependencies for {ticket.id}: {ticket.title}"
        )
        
        console.print(f"[green]✓[/green] Graph exported to: {output_path}")
        
        # For SVG/PNG, provide instructions
        if export.endswith('.svg') or export.endswith('.png'):
            console.print("\n[yellow]Note:[/yellow] To generate SVG/PNG from DOT file:")
            console.print(f"  dot -Tsvg {export}.dot -o {export}")
            console.print(f"  dot -Tpng {export}.dot -o {export}")
        
        return
    
    if output_format == "json":
        import json
        
        # Convert to JSON-serializable format
        def ticket_to_dict(t: Ticket) -> dict:
            return {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "type": t.type,
                "priority": t.priority,
                "assignee": t.assignee,
                "reporter": t.reporter
            }
        
        json_graph = {
            "ticket": ticket_to_dict(ticket),
            "relationships": {}
        }
        
        if show_blockers and graph["blocked_by"]:
            json_graph["relationships"]["blocked_by"] = [
                ticket_to_dict(t) for t in graph["blocked_by"]
            ]
        
        if show_blocks and graph["blocks"]:
            json_graph["relationships"]["blocks"] = [
                ticket_to_dict(t) for t in graph["blocks"]
            ]
        
        if show_parent and graph["parent"]:
            json_graph["relationships"]["parent"] = ticket_to_dict(graph["parent"])
        
        if show_children and graph["children"]:
            json_graph["relationships"]["children"] = [
                ticket_to_dict(t) for t in graph["children"]
            ]
        
        if show_epic_rel and graph["epic"]:
            epic = graph["epic"]
            json_graph["relationships"]["epic"] = {
                "id": epic.id,
                "title": epic.title,
                "status": epic.status
            }
        
        print(json.dumps(json_graph, indent=2))
    else:
        # Enhanced display mode
        if enhanced:
            # Create detailed panel display
            blocks = [t.id for t in graph["blocks"]] if graph["blocks"] else None
            blocked_by = [t.id for t in graph["blocked_by"]] if graph["blocked_by"] else None
            
            ticket_panel = GraphVisuals.create_ticket_panel(
                ticket,
                show_description=True,
                show_metadata=True,
                show_relationships=True,
                blocks=blocks,
                blocked_by=blocked_by
            )
            console.print(ticket_panel)
            
            # Show legend if requested
            if show_legend:
                console.print()
                console.print(GraphVisuals.create_legend_panel())
            
            # Show stats if requested
            if show_stats:
                # Calculate statistics
                all_related = set([ticket_id])
                dep_count = 0
                blocked_count = 0
                max_depth_found = 0
                
                def count_relationships(graph_data, current_depth=0):
                    nonlocal dep_count, blocked_count, max_depth_found
                    if current_depth > max_depth_found:
                        max_depth_found = current_depth
                    
                    if graph_data and "ticket" in graph_data:
                        t = graph_data["ticket"]
                        if t.id not in all_related:
                            all_related.add(t.id)
                        
                        if graph_data.get("blocks"):
                            dep_count += len(graph_data["blocks"])
                        if graph_data.get("blocked_by"):
                            dep_count += len(graph_data["blocked_by"])
                            blocked_count += 1
                
                count_relationships(graph)
                
                # Get status counts
                status_counts = defaultdict(int)
                for tid in all_related:
                    t, _ = find_ticket(tid, gira_root, include_archived=True)
                    if t:
                        status_counts[t.status] += 1
                
                console.print()
                stats_panel = GraphVisuals.create_stats_panel(
                    total_tickets=len(all_related),
                    total_dependencies=dep_count,
                    max_depth=max_depth_found,
                    blocked_count=blocked_count,
                    ticket_counts_by_status=dict(status_counts)
                )
                console.print(stats_panel)
        
        # Compact mode
        elif compact:
            # Show compact representation
            console.print(f"\n{GraphVisuals.create_compact_ticket_line(ticket)}")
            
            if graph["blocked_by"]:
                console.print("  [red]Blocked by:[/red]")
                for blocker in graph["blocked_by"]:
                    console.print(f"    {GraphVisuals.create_compact_ticket_line(blocker)}")
            
            if graph["blocks"]:
                console.print("  [yellow]Blocks:[/yellow]")
                for blocked in graph["blocks"]:
                    console.print(f"    {GraphVisuals.create_compact_ticket_line(blocked)}")
            
            if graph["parent"]:
                console.print(f"  [green]Parent:[/green] {GraphVisuals.create_compact_ticket_line(graph['parent'])}")
            
            if graph["children"]:
                console.print("  [cyan]Children:[/cyan]")
                for child in graph["children"]:
                    console.print(f"    {GraphVisuals.create_compact_ticket_line(child)}")
            
            if show_legend:
                console.print(f"\nLegend: {' '.join([f'{icon} {status[:4]}' for status, icon in GraphVisuals.STATUS_ICONS.items()])}")
        
        # Default tree visualization with enhanced nodes
        else:
            tree = Tree(create_tree_node(ticket, status_color=True, use_icons=True))
            
            visited = {ticket_id}
            add_relationships_to_tree(
                tree, graph, visited, gira_root, depth,
                show_blockers, show_blocks, show_parent, show_children, show_epic_rel
            )
            
            console.print(tree)
            
            # Show stats panel if requested
            if show_stats:
                # Simple stats for tree view
                total_shown = len(visited)
                blocked_count = 1 if graph["blocked_by"] else 0
                
                console.print()
                console.print(f"[dim]Displayed {total_shown} tickets with depth {depth}[/dim]")
                if blocked_count:
                    console.print(f"[red]⚠️  This ticket is blocked[/red]")


def build_epic_graph(
    epic: Epic,
    gira_root,
    all_tickets: Optional[List[Ticket]] = None,
    all_epics: Optional[List[Epic]] = None
) -> Dict:
    """Build a complete graph for an epic including all its tickets and relationships."""
    if all_tickets is None:
        all_tickets = load_all_tickets(gira_root, include_archived=True)
    
    if all_epics is None:
        all_epics = load_all_epics(gira_root)
    
    # Create ticket lookup for performance
    ticket_map = {t.id: t for t in all_tickets}
    
    # Get all tickets in this epic
    epic_tickets = [ticket_map[tid] for tid in epic.tickets if tid in ticket_map]
    
    # Calculate progress
    status_counts = defaultdict(int)
    for ticket in epic_tickets:
        status_counts[ticket.status] += 1
    
    done_count = status_counts.get("done", 0) + status_counts.get("closed", 0)
    total_count = len(epic_tickets)
    progress_pct = (done_count / total_count * 100) if total_count > 0 else 0
    
    # Find inter-epic dependencies
    blocked_epics = set()
    blocking_epics = set()
    
    for ticket in epic_tickets:
        if ticket.blocks:
            for blocked_id in ticket.blocks:
                if blocked_id in ticket_map:
                    blocked_ticket = ticket_map[blocked_id]
                    if blocked_ticket.epic_id and blocked_ticket.epic_id != epic.id:
                        blocked_epics.add(blocked_ticket.epic_id)
        
        if ticket.blocked_by:
            for blocker_id in ticket.blocked_by:
                if blocker_id in ticket_map:
                    blocker_ticket = ticket_map[blocker_id]
                    if blocker_ticket.epic_id and blocker_ticket.epic_id != epic.id:
                        blocking_epics.add(blocker_ticket.epic_id)
    
    return {
        "epic": epic,
        "tickets": epic_tickets,
        "status_counts": dict(status_counts),
        "progress": {
            "done": done_count,
            "total": total_count,
            "percentage": progress_pct
        },
        "blocks": list(blocked_epics),
        "blocked_by": list(blocking_epics)
    }


def visualize_epic_overview(gira_root, show_progress: bool = True, min_progress: Optional[int] = None,
                           status_filter: Optional[str] = None, owner_filter: Optional[str] = None) -> None:
    """Show overview of all epics with their relationships and progress."""
    epics = load_all_epics(gira_root)
    all_tickets = load_all_tickets(gira_root, include_archived=True)
    
    # Apply filters
    filtered_epics = []
    for epic in epics:
        if status_filter and epic.status != status_filter:
            continue
        if owner_filter and epic.owner != owner_filter:
            continue
        
        graph = build_epic_graph(epic, gira_root, all_tickets, epics)
        
        if min_progress is not None and graph["progress"]["percentage"] < min_progress:
            continue
            
        filtered_epics.append((epic, graph))
    
    if not filtered_epics:
        console.print("[yellow]No epics found matching criteria[/yellow]")
        return
    
    # Display epics
    for epic, graph in filtered_epics:
        # Create header with enhanced progress bar
        progress = graph["progress"]
        progress_bar = ""
        if show_progress and progress["total"] > 0:
            progress_bar = " " + GraphVisuals.create_epic_progress_bar(
                progress["percentage"],
                width=20,
                show_percentage=True
            )
        
        console.print(f"\n[bold cyan]{epic.id}[/bold cyan] [bold]{epic.title}[/bold]{progress_bar}")
        
        # Show tickets by status
        for status, count in sorted(graph["status_counts"].items()):
            status_icon = GraphVisuals.STATUS_ICONS.get(status, "•")
            
            # Show sample tickets for each status
            status_tickets = [t for t in graph["tickets"] if t.status == status][:3]
            console.print(f"├── {status_icon} {status}: {count} tickets")
            for ticket in status_tickets:
                title = ticket.title[:40] + "..." if len(ticket.title) > 40 else ticket.title
                console.print(f"│   ├── {ticket.id}: {title}")
            if count > 3:
                console.print(f"│   └── ... and {count - 3} more")
        
        # Show dependencies if any
        if graph["blocks"]:
            console.print(f"├── [yellow]Blocks:[/yellow] {', '.join(graph['blocks'])}")
        if graph["blocked_by"]:
            console.print(f"└── [red]Blocked by:[/red] {', '.join(graph['blocked_by'])}")


def visualize_single_epic(epic_id: str, gira_root, show_all_tickets: bool = False) -> None:
    """Show detailed view of a single epic with all its tickets."""
    # Load the epic
    epic_file = gira_root / ".gira" / "epics" / f"{epic_id}.json"
    if not epic_file.exists():
        console.print(f"[red]Error:[/red] Epic {epic_id} not found")
        raise typer.Exit(1)
    
    epic = Epic.from_json_file(str(epic_file))
    all_tickets = load_all_tickets(gira_root, include_archived=True)
    graph = build_epic_graph(epic, gira_root, all_tickets)
    
    # Create panel header
    progress = graph["progress"]
    header = Panel(
        f"[bold]{epic.title}[/bold]\n"
        f"Status: {epic.status.title()} | "
        f"Progress: {progress['done']}/{progress['total']} tickets ({progress['percentage']:.0f}%)\n"
        f"Owner: {epic.owner}",
        title=f"[cyan]{epic.id}[/cyan]",
        border_style="cyan"
    )
    console.print(header)
    
    # Show description if available
    if epic.description:
        console.print(f"\n[dim]{epic.description}[/dim]\n")
    
    # Create status breakdown tree
    tree = Tree("[bold]Tickets by Status[/bold]")
    
    status_order = ["done", "in_progress", "review", "todo", "backlog"]
    for status in status_order:
        if status not in graph["status_counts"]:
            continue
            
        count = graph["status_counts"][status]
        icon = GraphVisuals.STATUS_ICONS.get(status, "•")
        status_name = status.replace("_", " ").title()
        status_icon = f"{icon} {status_name}"
        
        status_node = tree.add(f"{status_icon} ({count})")
        
        # Add tickets under each status
        status_tickets = [t for t in graph["tickets"] if t.status == status]
        
        # Show all or limited tickets
        tickets_to_show = status_tickets if show_all_tickets else status_tickets[:5]
        
        for ticket in tickets_to_show:
            ticket_text = f"[cyan]{ticket.id}[/cyan]: {ticket.title}"
            
            # Add dependency indicators
            deps = []
            if ticket.blocks:
                deps.append(f"blocks: {', '.join(ticket.blocks)}")
            if ticket.blocked_by:
                deps.append(f"[red]blocked by: {', '.join(ticket.blocked_by)}[/red]")
            
            if deps:
                ticket_text += f" ({', '.join(deps)})"
                
            status_node.add(ticket_text)
        
        if not show_all_tickets and len(status_tickets) > 5:
            status_node.add(f"[dim]... and {len(status_tickets) - 5} more[/dim]")
    
    console.print(tree)
    
    # Show inter-epic dependencies
    if graph["blocks"] or graph["blocked_by"]:
        console.print("\n[bold]Epic Dependencies[/bold]")
        if graph["blocks"]:
            console.print(f"  [yellow]Blocks:[/yellow] {', '.join(graph['blocks'])}")
        if graph["blocked_by"]:
            console.print(f"  [red]Blocked by:[/red] {', '.join(graph['blocked_by'])}")


def visualize_epic_dependencies(gira_root) -> None:
    """Show dependencies between epics."""
    epics = load_all_epics(gira_root)
    all_tickets = load_all_tickets(gira_root, include_archived=True)
    
    # Build dependency map
    epic_graphs = {}
    for epic in epics:
        epic_graphs[epic.id] = build_epic_graph(epic, gira_root, all_tickets, epics)
    
    # Find all epic relationships
    relationships = []
    for epic_id, graph in epic_graphs.items():
        for blocked_epic in graph["blocks"]:
            if blocked_epic in epic_graphs:
                relationships.append((epic_id, blocked_epic, "blocks"))
    
    if not relationships:
        console.print("[yellow]No inter-epic dependencies found[/yellow]")
        return
    
    # Create visual representation
    console.print("[bold]Epic Dependencies[/bold]\n")
    
    # Group by source epic
    deps_by_epic = defaultdict(list)
    for src, dst, rel in relationships:
        deps_by_epic[src].append((dst, rel))
    
    for epic_id in sorted(deps_by_epic.keys()):
        epic = epic_graphs[epic_id]["epic"]
        console.print(f"[cyan]{epic_id}[/cyan] [{epic.title}]")
        
        for dst, rel in deps_by_epic[epic_id]:
            dst_epic = epic_graphs[dst]["epic"]
            arrow = "──blocks──>" if rel == "blocks" else "──>"
            console.print(f"  └{arrow} [cyan]{dst}[/cyan] [{dst_epic.title}]")
        console.print()


def visualize_mixed_view(gira_root, max_depth: int = 2) -> None:
    """Show mixed view of epics with their tickets and cross-epic dependencies."""
    epics = load_all_epics(gira_root)
    all_tickets = load_all_tickets(gira_root, include_archived=True)
    
    # Create panels for each epic
    panels = []
    
    for epic in epics[:6]:  # Limit to 6 epics for display
        graph = build_epic_graph(epic, gira_root, all_tickets, epics)
        
        # Build content for panel
        lines = []
        
        # Show some tickets
        for ticket in graph["tickets"][:5]:
            status_icon = {
                "done": "✓",
                "in_progress": "⚡",
                "review": "⏸",
                "todo": "○"
            }.get(ticket.status, "•")
            
            line = f"{ticket.id} {status_icon}"
            
            # Add cross-epic dependencies
            if ticket.blocks:
                for blocked_id in ticket.blocks:
                    blocked_ticket = next((t for t in all_tickets if t.id == blocked_id), None)
                    if blocked_ticket and blocked_ticket.epic_id and blocked_ticket.epic_id != epic.id:
                        line += f" ──blocks──> {blocked_id}"
                        break
            
            lines.append(line)
        
        if len(graph["tickets"]) > 5:
            lines.append(f"[dim]... {len(graph['tickets']) - 5} more tickets[/dim]")
        
        # Create panel
        panel = Panel(
            "\n".join(lines),
            title=f"[cyan]{epic.id}[/cyan]: {epic.title}",
            border_style="cyan" if epic.status == "active" else "dim"
        )
        panels.append(panel)
    
    # Display in columns
    if panels:
        console.print(Columns(panels[:3]))
        if len(panels) > 3:
            console.print()
            console.print(Columns(panels[3:6]))
    
    if len(epics) > 6:
        console.print(f"\n[dim]... and {len(epics) - 6} more epics[/dim]")