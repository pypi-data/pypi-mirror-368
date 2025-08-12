"""Show commits associated with a ticket."""

from typing import Optional

import typer
from gira.utils.console import console
from rich.table import Table

from gira.models.config import ProjectConfig
from gira.utils.git_utils import get_commits_for_ticket, is_git_repository
from gira.utils.output import OutputFormat, print_output, add_color_option, add_no_color_option, get_color_kwargs
from gira.utils.project import ensure_gira_project
from gira.utils.ticket_utils import find_ticket

def commits(
    ticket_id: str = typer.Argument(..., help="Ticket ID to show commits for"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Maximum number of commits to show"),
    output_format: str = typer.Option("text", "--format", "-f", help="Output format: text, json"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON (shorthand for --format json)"),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
) -> None:
    """List all commits associated with a ticket.
    
    This command searches through the git history to find all commits that
    reference the specified ticket ID in their commit messages.
    
    Examples:
        # Show all commits for a ticket
        gira ticket commits GCM-123
        
        # Limit to last 10 commits
        gira ticket commits GCM-123 --limit 10
        
        # Export as JSON
        gira ticket commits GCM-123 --json
    """
    root = ensure_gira_project()
    
    # Handle --json flag as shorthand for --format json
    if json_output:
        output_format = "json"
    
    # Validate output format
    output_format = output_format.lower()
    if output_format not in ["text", "json"]:
        console.print(f"[red]Error:[/red] Unsupported output format '{output_format}'. Supported formats: text, json")
        raise typer.Exit(1)
    
    # Verify ticket exists
    ticket, _ = find_ticket(ticket_id, root, include_archived=True)
    if not ticket:
        console.print(f"[red]Error:[/red] Ticket {ticket_id.upper()} not found")
        raise typer.Exit(1)
    
    # Check if we're in a git repository
    if not is_git_repository():
        console.print("[yellow]Warning:[/yellow] Not in a git repository. No commits to show.")
        raise typer.Exit(0)
    
    # Get configuration for commit patterns
    config_path = root / ".gira" / "config.json"
    patterns = None
    if config_path.exists():
        config = ProjectConfig.from_json_file(str(config_path))
        patterns = config.commit_id_patterns
    
    # Get commits for the ticket - search using both current and historical IDs
    from gira.utils.prefix_history import PrefixHistory
    commits = []
    
    # Get all historical IDs for this ticket
    history = PrefixHistory(root)
    all_prefixes = history.get_all_prefixes()
    
    # Extract the ticket number
    ticket_number = ticket.id.split('-')[1]
    
    # Search with all possible historical IDs
    searched_ids = set()
    for prefix in all_prefixes:
        historical_id = f"{prefix}-{ticket_number}"
        if historical_id not in searched_ids:
            searched_ids.add(historical_id)
            historical_commits = get_commits_for_ticket(historical_id, limit=limit, patterns=patterns)
            # Add commits that aren't already in the list
            existing_shas = {c.sha for c in commits}
            for commit in historical_commits:
                if commit.sha not in existing_shas:
                    commits.append(commit)
    
    # Sort by date (newest first)
    commits.sort(key=lambda c: c.date, reverse=True)
    
    # Apply limit if specified
    if limit and len(commits) > limit:
        commits = commits[:limit]
    
    if not commits:
        console.print(f"[yellow]No commits found for ticket {ticket.id}[/yellow]")
        raise typer.Exit(0)
    
    # Output in requested format
    if output_format == "text":
        # Create a table for text output
        # Show all searched IDs if there are historical ones
        if len(searched_ids) > 1:
            all_ids = sorted(searched_ids)
            title = f"Commits for {ticket.id} (searched all IDs: {', '.join(all_ids)})"
        else:
            title = f"Commits for {ticket.id}"
        
        table = Table(
            title=title,
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("SHA", style="cyan", no_wrap=True)
        table.add_column("Date", style="dim")
        table.add_column("Author", style="green")
        table.add_column("Subject", overflow="fold")
        
        for commit in commits:
            table.add_row(
                commit.short_sha,
                commit.date.strftime("%Y-%m-%d"),
                commit.author[:20] + "..." if len(commit.author) > 20 else commit.author,
                commit.subject
            )
        
        console.print(table)
        
        # Show count with all searched IDs
        if len(searched_ids) > 1:
            console.print(f"\n[dim]Found {len(commits)} commit{'s' if len(commits) != 1 else ''} across all historical IDs[/dim]")
        else:
            console.print(f"\n[dim]Found {len(commits)} commit{'s' if len(commits) != 1 else ''} for {ticket.id}[/dim]")
    
    elif output_format == "json":
        # Convert commits to dictionaries for JSON output
        commit_data = []
        for commit in commits:
            commit_dict = {
                "sha": commit.sha,
                "short_sha": commit.short_sha,
                "author": commit.author,
                "date": commit.date.isoformat(),
                "subject": commit.subject,
                "ticket_ids": commit.ticket_ids
            }
            if commit.body:
                commit_dict["body"] = commit.body
            commit_data.append(commit_dict)
        
        color_kwargs = get_color_kwargs(color, no_color)
        print_output({"ticket_id": ticket.id, "commits": commit_data}, OutputFormat.JSON, **color_kwargs)