"""Enhanced visual elements for graph command."""

from typing import Dict, List, Optional

from rich import box
from rich.panel import Panel
from rich.table import Table

from gira.models import Ticket


class GraphVisuals:
    """Enhanced visual elements for graph display."""

    # Status icons
    STATUS_ICONS = {
        "todo": "📋",
        "in_progress": "🔄",
        "review": "⏸️",
        "done": "✅",
        "backlog": "📋",
        "closed": "✅"
    }

    # Priority icons
    PRIORITY_ICONS = {
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢"
    }

    # Relationship arrows
    RELATIONSHIP_ARROWS = {
        "blocks": "→blocks→",
        "blocked_by": "←blocked by←",
        "related": "↔related↔",
        "parent": "↑parent↑",
        "child": "↓child↓"
    }

    # Status colors for Rich
    STATUS_COLORS = {
        "todo": "yellow",
        "in_progress": "cyan",
        "review": "magenta",
        "done": "green",
        "backlog": "dim",
        "closed": "green"
    }

    # Priority colors
    PRIORITY_COLORS = {
        "high": "red",
        "medium": "yellow",
        "low": "green"
    }

    @classmethod
    def format_ticket_node(
        cls,
        ticket: Ticket,
        relationship: str = "",
        show_icons: bool = True,
        show_priority: bool = True,
        truncate_title: int = 50
    ) -> str:
        """Create a beautifully formatted ticket node."""
        parts = []

        # Add relationship if present
        if relationship:
            parts.append(f"[dim]{relationship}[/dim]")

        # Ticket ID with color
        parts.append(f"[cyan]{ticket.id}[/cyan]")

        # Status icon
        if show_icons:
            icon = cls.STATUS_ICONS.get(ticket.status.lower(), "•")
            parts.append(icon)

        # Title (truncated if needed)
        title = ticket.title
        if truncate_title and len(title) > truncate_title:
            title = title[:truncate_title] + "..."
        parts.append(title)

        # Status with color
        status_color = cls.STATUS_COLORS.get(ticket.status.lower(), "white")
        parts.append(f"[{status_color}]{ticket.status}[/{status_color}]")

        # Priority icon
        if show_priority and ticket.priority:
            priority_icon = cls.PRIORITY_ICONS.get(ticket.priority.lower(), "")
            if priority_icon:
                parts.append(priority_icon)

        return " ".join(parts)

    @classmethod
    def create_ticket_panel(
        cls,
        ticket: Ticket,
        show_description: bool = True,
        show_metadata: bool = True,
        show_relationships: bool = True,
        blocks: Optional[List[str]] = None,
        blocked_by: Optional[List[str]] = None
    ) -> Panel:
        """Create a rich panel for detailed ticket display."""
        # Header with status and priority
        status_icon = cls.STATUS_ICONS.get(ticket.status.lower(), "•")
        priority_icon = cls.PRIORITY_ICONS.get(ticket.priority.lower(), "") if ticket.priority else ""

        header_parts = [
            f"Status: {status_icon} {ticket.status.title()}",
            f"Priority: {priority_icon} {ticket.priority.title() if ticket.priority else 'None'}"
        ]

        if ticket.type:
            header_parts.append(f"Type: {ticket.type.title()}")

        content_lines = [" | ".join(header_parts)]

        # Assignee
        if show_metadata and ticket.assignee:
            content_lines.append(f"Assignee: {ticket.assignee}")

        # Description
        if show_description and ticket.description:
            content_lines.append("")
            # Wrap long descriptions
            desc_lines = ticket.description.split('\n')
            for line in desc_lines[:5]:  # Show first 5 lines
                if len(line) > 80:
                    line = line[:77] + "..."
                content_lines.append(line)
            if len(desc_lines) > 5:
                content_lines.append("...")

        # Relationships
        if show_relationships:
            if blocks or blocked_by:
                content_lines.append("")

            if blocked_by:
                content_lines.append(f"⚠️  Blocked by: {', '.join(blocked_by)}")

            if blocks:
                content_lines.append(f"🚫 Blocks: {', '.join(blocks)}")

        # Create panel
        panel_content = "\n".join(content_lines)
        title = f"[bold cyan]{ticket.id}[/bold cyan]: [bold]{ticket.title}[/bold]"

        status_color = cls.STATUS_COLORS.get(ticket.status.lower(), "white")

        return Panel(
            panel_content,
            title=title,
            border_style=status_color,
            box=box.ROUNDED
        )

    @classmethod
    def create_stats_panel(
        cls,
        total_tickets: int,
        total_dependencies: int,
        max_depth: int,
        blocked_count: int,
        critical_path_days: Optional[int] = None,
        ticket_counts_by_status: Optional[Dict[str, int]] = None
    ) -> Panel:
        """Create a statistics panel for graph display."""
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right")

        table.add_row("Total Tickets", str(total_tickets))
        table.add_row("Dependencies", str(total_dependencies))
        table.add_row("Max Depth", str(max_depth))

        if blocked_count > 0:
            table.add_row("Blocked", f"[red]{blocked_count}[/red]")
        else:
            table.add_row("Blocked", "0")

        if critical_path_days:
            table.add_row("Critical Path", f"{critical_path_days}d")

        # Add status breakdown if provided
        if ticket_counts_by_status:
            table.add_row("", "")  # Empty row for spacing
            for status, count in sorted(ticket_counts_by_status.items()):
                icon = cls.STATUS_ICONS.get(status.lower(), "•")
                color = cls.STATUS_COLORS.get(status.lower(), "white")
                table.add_row(f"{icon} {status.title()}", f"[{color}]{count}[/{color}]")

        return Panel(
            table,
            title="[bold]Statistics[/bold]",
            border_style="blue",
            box=box.ROUNDED
        )

    @classmethod
    def create_epic_progress_bar(
        cls,
        progress_percentage: float,
        width: int = 20,
        show_percentage: bool = True
    ) -> str:
        """Create a visual progress bar for epics."""
        filled = int(progress_percentage / 100 * width)
        empty = width - filled

        bar = f"[green]{'█' * filled}[/green][dim]{'░' * empty}[/dim]"

        if show_percentage:
            bar += f" {progress_percentage:.0f}%"

        return bar

    @classmethod
    def format_relationship_arrow(
        cls,
        relationship_type: str,
        with_color: bool = True
    ) -> str:
        """Format relationship arrows with optional color."""
        arrow = cls.RELATIONSHIP_ARROWS.get(relationship_type, "→")

        if with_color:
            color_map = {
                "blocks": "yellow",
                "blocked_by": "red",
                "related": "blue",
                "parent": "green",
                "child": "cyan"
            }
            color = color_map.get(relationship_type, "white")
            arrow = f"[{color}]{arrow}[/{color}]"

        return arrow

    @classmethod
    def create_compact_ticket_line(
        cls,
        ticket: Ticket,
        indent: int = 0,
        show_status: bool = True
    ) -> str:
        """Create a compact single-line ticket representation."""
        indent_str = "  " * indent

        # Status icon or abbreviated status
        if show_status:
            icon = cls.STATUS_ICONS.get(ticket.status.lower(), "")
            status_str = f" {icon}" if icon else f" [{ticket.status[:4]}]"
        else:
            status_str = ""

        # Priority indicator
        priority_str = ""
        if ticket.priority and ticket.priority.lower() == "high":
            priority_str = " " + cls.PRIORITY_ICONS["high"]

        # Compact title
        title = ticket.title[:40] + "..." if len(ticket.title) > 40 else ticket.title

        return f"{indent_str}{ticket.id}{status_str} {title}{priority_str}"

    @classmethod
    def create_legend_panel(cls) -> Panel:
        """Create a legend panel explaining icons and colors."""
        content_lines = []

        # Status legend
        content_lines.append("[bold]Status Icons:[/bold]")
        for status, icon in cls.STATUS_ICONS.items():
            color = cls.STATUS_COLORS.get(status, "white")
            content_lines.append(f"  {icon} [{color}]{status.replace('_', ' ').title()}[/{color}]")

        content_lines.append("")

        # Priority legend
        content_lines.append("[bold]Priority Levels:[/bold]")
        for priority, icon in cls.PRIORITY_ICONS.items():
            color = cls.PRIORITY_COLORS.get(priority, "white")
            content_lines.append(f"  {icon} [{color}]{priority.title()}[/{color}]")

        content_lines.append("")

        # Relationship arrows
        content_lines.append("[bold]Relationships:[/bold]")
        content_lines.append("  → Blocks another ticket")
        content_lines.append("  ← Blocked by another ticket")
        content_lines.append("  ⚠️  Currently blocked")

        return Panel(
            "\n".join(content_lines),
            title="[bold]Legend[/bold]",
            border_style="dim",
            box=box.ROUNDED
        )
