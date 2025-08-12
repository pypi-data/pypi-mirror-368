"""Show tickets associated with file lines using git blame."""

from pathlib import Path
from typing import List, Optional, Tuple

import typer
from gira.utils.console import console
from rich.table import Table

from gira.models.config import ProjectConfig
from gira.schemas.blame import (
    BlameFileResult,
    BlameLineRange,
    BlameOutput,
    BlameSummary,
    BlameTicketInfo,
)
from gira.utils.blame import get_file_blame, get_line_history, parse_line_range
from gira.utils.output import OutputFormat, print_output, add_color_option, add_no_color_option, get_color_kwargs
from gira.utils.project import ensure_gira_project

def blame(
    files: List[str] = typer.Argument(..., help="File(s) to analyze for ticket references"),
    lines: Optional[str] = typer.Option(None, "--lines", "-L", help="Line range (e.g., '10,20' or '10,+5')"),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format: table, json, simple"),
    ids_only: bool = typer.Option(False, "--ids-only", help="Show only ticket IDs (implies simple format)"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON (shorthand for --format json)"),
    context: Optional[int] = typer.Option(None, "--context", "-C", help="Show N lines of context around blamed lines"),
    history: bool = typer.Option(False, "--history", help="Show full history of tickets that touched specific lines (requires -L)"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Bypass cache and force fresh blame analysis"),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
) -> None:
    """Discover tickets associated with specific file lines.
    
    This command uses git blame to find which commits (and their associated tickets)
    last modified specific lines in files. It's similar to git blame but focuses on
    ticket tracking rather than just commit attribution.
    
    Examples:
        # Find tickets for a specific file
        gira ticket blame src/main.py
        
        # Find tickets for specific lines
        gira ticket blame src/main.py -L 10,20
        
        # Find tickets for multiple files
        gira ticket blame src/*.py
        
        # Show only ticket IDs
        gira ticket blame src/main.py --ids-only
        
        # Export as JSON for tooling
        gira ticket blame src/main.py --json
    
    JSON Output Schema:
        When using --json or --format json, the output follows a structured schema
        designed for reliable parsing by tools and AI agents.
        
        See 'gira ticket blame --help-json' for detailed schema documentation.
    """
    root = ensure_gira_project()
    
    # Handle output format options
    if json_output:
        output_format = "json"
    if ids_only:
        output_format = "simple"
    
    # Validate output format
    output_format = output_format.lower()
    if output_format not in ["table", "json", "simple"]:
        console.print(f"[red]Error:[/red] Invalid output format '{output_format}'. Valid formats: table, json, simple")
        raise typer.Exit(1)
    
    # Parse line range if provided
    line_range = None
    if lines:
        line_range = parse_line_range(lines)
        if not line_range:
            console.print(f"[red]Error:[/red] Invalid line range format '{lines}'. Use formats like '10,20' or '10,+5'")
            raise typer.Exit(1)
    
    # Load configuration for ticket patterns
    config_path = root / ".gira" / "config.json"
    patterns = None
    if config_path.exists():
        try:
            config = ProjectConfig.from_json_file(str(config_path))
            patterns = config.blame_config.ticket_patterns
        except Exception:
            pass
    
    # If history mode is requested, handle it separately
    if history:
        if not lines:
            console.print("[red]Error:[/red] --history requires --lines/-L to specify which lines to analyze")
            raise typer.Exit(1)
        
        if len(files) != 1:
            console.print("[red]Error:[/red] --history can only analyze one file at a time")
            raise typer.Exit(1)
        
        return _handle_history_mode(
            file_path=Path(files[0]),
            line_range=line_range,
            patterns=patterns,
            root=root,
            output_format=output_format,
            no_cache=no_cache,
            color=color,
            no_color=no_color
        )
    
    # Process each file
    all_results = []
    total_tickets = set()
    
    for file_pattern in files:
        file_path = Path(file_pattern)
        
        # Check if file exists
        if not file_path.exists():
            console.print(f"[red]Error:[/red] File not found: {file_pattern}")
            continue
        
        if not file_path.is_file():
            console.print(f"[yellow]Warning:[/yellow] Skipping directory: {file_pattern}")
            continue
        
        # Get blame information
        kwargs = dict(line_range=line_range, patterns=patterns, cwd=root, context=context)
        if no_cache:
            kwargs["no_cache"] = True
        result = get_file_blame(file_path, **kwargs)
        
        if not result:
            console.print(f"[yellow]Warning:[/yellow] Could not get blame information for {file_pattern}")
            continue
        
        all_results.append(result)
        total_tickets.update(result.tickets.keys())
    
    if not all_results:
        console.print("[red]Error:[/red] No files could be analyzed")
        raise typer.Exit(1)
    
    # Output results based on format
    if output_format == "simple":
        # Simple format: just ticket IDs
        for ticket_id in sorted(total_tickets):
            console.print(ticket_id)
    
    elif output_format == "json":
        # JSON format using Pydantic models
        files = []
        
        for result in all_results:
            tickets = {}
            
            for ticket_id, ticket_info in result.tickets.items():
                tickets[ticket_id] = BlameTicketInfo(
                    title=ticket_info.title,
                    status=ticket_info.status,
                    type=ticket_info.type,
                    lines_affected=ticket_info.lines_affected,
                    total_lines=ticket_info.total_lines(),
                    last_modified=ticket_info.last_modified,
                    commits=sorted(list(ticket_info.commits))
                )
            
            file_result = BlameFileResult(
                file=str(result.file_path),
                tickets=tickets,
                range=BlameLineRange(start=line_range[0], end=line_range[1]) if line_range else None
            )
            
            files.append(file_result)
        
        output = BlameOutput(
            files=files,
            summary=BlameSummary(
                total_files=len(all_results),
                unique_tickets=sorted(list(total_tickets)),
                ticket_count=len(total_tickets)
            )
        )
        
        # Use Pydantic's model_dump with mode='json' for proper serialization
        color_kwargs = get_color_kwargs(color, no_color)
        print_output(output.model_dump(mode='json'), OutputFormat.JSON, **color_kwargs)
    
    else:  # table format (default)
        # If context is requested, show detailed line-by-line output
        if context is not None and context > 0:
            for result in all_results:
                if len(all_results) > 1:
                    console.print(f"\n[bold]{result.file_path}[/bold]")
                else:
                    console.print(f"[bold]File: {result.file_path}[/bold]")
                
                if not result.lines:
                    console.print("[dim]No lines to display[/dim]")
                    continue
                
                # Display lines with blame info
                for line in result.lines:
                    if line.is_context:
                        # Context lines are dimmed with consistent formatting
                        console.print(f"[dim]   {line.line_number:5d}         {line.line_content}[/dim]")
                    else:
                        # Blamed lines show ticket info with better formatting
                        if line.ticket_ids:
                            # Truncate long ticket lists for better alignment
                            if len(line.ticket_ids) > 3:
                                ticket_str = f"{', '.join(line.ticket_ids[:3])}, +{len(line.ticket_ids)-3} more"
                            else:
                                ticket_str = ", ".join(line.ticket_ids)
                            # Truncate if still too long
                            if len(ticket_str) > 40:
                                ticket_str = ticket_str[:37] + "..."
                        else:
                            ticket_str = "[dim]no ticket[/dim]"
                        console.print(f"   {line.line_number:5d} {ticket_str} {line.line_content}")
                
                # Show summary
                console.print()
                if result.tickets:
                    console.print(f"[dim]Found {len(result.tickets)} ticket(s) in this file[/dim]")
                    for ticket_id, info in sorted(result.tickets.items()):
                        console.print(f"  [cyan]{ticket_id}[/cyan]: {info.title} ([yellow]{info.status}[/yellow])")
        else:
            # Original table format without context
            for result in all_results:
                if len(all_results) > 1:
                    console.print(f"\n[bold]{result.file_path}[/bold]")
                
                if not result.tickets:
                    console.print("[dim]No tickets found[/dim]")
                    continue
                
                # Create table
                table = Table(
                    title=f"Tickets in {result.file_path.name}" if len(all_results) == 1 else None,
                    show_header=True,
                    header_style="bold cyan"
                )
                
                table.add_column("Ticket", style="cyan", no_wrap=True)
                table.add_column("Status", style="yellow")
                table.add_column("Line Numbers", style="green")
                table.add_column("Title", overflow="fold")
                table.add_column("Last Modified", style="dim")
                
                # Sort tickets by first line affected
                sorted_tickets = sorted(
                    result.tickets.items(),
                    key=lambda x: x[1].lines_affected[0][0] if x[1].lines_affected else 0
                )
                
                for ticket_id, ticket_info in sorted_tickets:
                    # Format line ranges
                    line_ranges = []
                    for start, end in ticket_info.lines_affected:
                        if start == end:
                            line_ranges.append(f"L{start}")
                        else:
                            line_ranges.append(f"L{start}-{end}")
                    lines_str = ", ".join(line_ranges)
                    
                    # Format date
                    date_str = ticket_info.last_modified.strftime("%Y-%m-%d") if ticket_info.last_modified else "-"
                    
                    # Add row
                    table.add_row(
                        ticket_id,
                        ticket_info.status,
                        lines_str,
                        ticket_info.title[:60] + "..." if len(ticket_info.title) > 60 else ticket_info.title,
                        date_str
                    )
                
                console.print(table)
                
                # Summary
                total_lines_with_tickets = sum(info.total_lines() for info in result.tickets.values())
                total_lines = len([line for line in result.lines if not line.is_context])
                coverage = (total_lines_with_tickets / total_lines * 100) if total_lines > 0 else 0
                
                console.print(f"\n[dim]Found {len(result.tickets)} ticket(s) affecting {total_lines_with_tickets} line(s) ({coverage:.1f}% coverage)[/dim]")


def _handle_history_mode(
    file_path: Path,
    line_range: Tuple[int, int],
    patterns: Optional[List[str]],
    root: Path,
    output_format: str,
    no_cache: bool = False,
    color: bool = False,
    no_color: bool = False
) -> None:
    """Handle the --history mode to show historical changes to lines."""
    
    # Get the line history
    # Note: get_line_history doesn't support no_cache parameter
    history = get_line_history(file_path, line_range, patterns=patterns, cwd=root)
    
    if not history:
        console.print(f"[red]Error:[/red] Could not get history for {file_path}")
        raise typer.Exit(1)
    
    if not history.entries:
        console.print(f"[yellow]No history found for lines {line_range[0]}-{line_range[1]} in {file_path}[/yellow]")
        return
    
    # Output based on format
    if output_format == "json":
        # Create JSON output
        output_data = {
            "file": str(file_path),
            "line_range": {"start": line_range[0], "end": line_range[1]},
            "entries": [
                {
                    "commit": entry.commit_sha,
                    "short_sha": entry.short_sha,
                    "author": entry.author,
                    "date": entry.date.isoformat(),
                    "message": entry.message,
                    "tickets": entry.ticket_ids,
                    "diff_preview": entry.diff_preview
                }
                for entry in history.entries
            ],
            "tickets": {
                ticket_id: {
                    "title": info.title,
                    "status": info.status,
                    "type": info.type,
                    "commits": sorted(list(info.commits)),
                    "last_modified": info.last_modified.isoformat() if info.last_modified else None
                }
                for ticket_id, info in history.tickets.items()
            },
            "summary": {
                "total_commits": len(history.entries),
                "unique_tickets": sorted(list(history.tickets.keys())),
                "ticket_count": len(history.tickets)
            }
        }
        color_kwargs = get_color_kwargs(color, no_color)
        print_output(output_data, OutputFormat.JSON, **color_kwargs)
    
    elif output_format == "simple":
        # Simple format: just unique ticket IDs
        for ticket_id in sorted(history.tickets.keys()):
            console.print(ticket_id)
    
    else:  # table format
        # Header
        console.print(f"\n[bold]History for {file_path}:{line_range[0]},{line_range[1]}[/bold]")
        console.print(f"[dim]Showing {len(history.entries)} commits that touched these lines[/dim]\n")
        
        # Create a table for the history
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Commit", style="yellow", no_wrap=True)
        table.add_column("Date", style="dim")
        table.add_column("Author", overflow="fold")
        table.add_column("Tickets", style="cyan")
        table.add_column("Message", overflow="fold")
        
        # Add entries in chronological order (newest first)
        for entry in history.entries:
            tickets_str = ", ".join(entry.ticket_ids) if entry.ticket_ids else "[dim]no ticket[/dim]"
            date_str = entry.date.strftime("%Y-%m-%d %H:%M")
            
            table.add_row(
                entry.short_sha,
                date_str,
                entry.author[:20] + "..." if len(entry.author) > 20 else entry.author,
                tickets_str,
                entry.message[:50] + "..." if len(entry.message) > 50 else entry.message
            )
        
        console.print(table)
        
        # Ticket summary
        if history.tickets:
            console.print(f"\n[bold]Tickets that touched these lines:[/bold]")
            
            ticket_table = Table(show_header=True, header_style="bold cyan")
            ticket_table.add_column("Ticket", style="cyan", no_wrap=True)
            ticket_table.add_column("Status", style="yellow")
            ticket_table.add_column("Type")
            ticket_table.add_column("Commits", style="dim")
            ticket_table.add_column("Title", overflow="fold")
            
            for ticket_id, info in sorted(history.tickets.items()):
                ticket_table.add_row(
                    ticket_id,
                    info.status,
                    info.type,
                    str(len(info.commits)),
                    info.title[:60] + "..." if len(info.title) > 60 else info.title
                )
            
            console.print(ticket_table)
            console.print(f"\n[dim]Total: {len(history.tickets)} unique ticket(s) across {len(history.entries)} commit(s)[/dim]")