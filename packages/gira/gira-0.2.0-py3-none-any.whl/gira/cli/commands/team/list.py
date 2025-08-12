"""List team members command."""

from typing import Optional

import typer
from gira.utils.console import console
from rich.table import Table

from gira.utils.output import OutputFormat, print_output, add_format_option, add_color_option, add_no_color_option, get_color_kwargs
from gira.utils.team_utils import load_team

def show_team_table(members, team):
    """Display team members in a table format."""
    table = Table(title=f"Team Members ({len(members)} total)")
    table.add_column("Email", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Username", style="yellow")
    table.add_column("Aliases", style="dim")
    table.add_column("Role", style="green")
    table.add_column("Status", style="blue")
    table.add_column("Joined", style="dim")

    for member in members:
        # Find aliases for this member
        aliases = [f"@{alias}" for alias, email in team.aliases.items() if email == member.email]
        aliases_str = ", ".join(aliases) if aliases else ""

        username_str = f"@{member.username}" if member.username else ""
        status_str = "[green]Active[/green]" if member.active else "[red]Inactive[/red]"
        joined_str = member.joined_at.strftime("%Y-%m-%d")

        table.add_row(
            member.email,
            member.name,
            username_str,
            aliases_str,
            member.role.capitalize(),
            status_str,
            joined_str
        )

    console.print(table)

    # Show summary
    console.print()
    active_count = len([m for m in members if m.active])
    console.print(f"[dim]Active members: {active_count}/{len(members)}[/dim]")

    # Show available roles
    if team.roles:
        console.print(f"[dim]Available roles: {', '.join(team.roles)}[/dim]")


def list_members(
    role: Optional[str] = typer.Option(None, "-r", "--role", help="Filter by role"),
    active_only: bool = typer.Option(False, "--active-only", help="Show only active members"),
    output_format: OutputFormat = add_format_option(),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON (shorthand for --format json)"),
    filter_json: Optional[str] = typer.Option(None, "--filter-json", help="JSONPath expression to filter JSON output (e.g., '$[?(@.active==true)].email')"),
    color: bool = add_color_option(),
    no_color: bool = add_no_color_option(),
) -> None:
    """List all team members.
    
    Examples:
        # List all team members
        gira team list
        
        # List only active members
        gira team list --active-only
        
        # Filter by role
        gira team list --role developer
        
        # Export as JSON
        gira team list --format json
        gira team list --json
        
        # Export as JSON with JSONPath filtering
        gira team list --json --filter-json '$[?(@.active==true)].email'
        gira team list --format json --filter-json '$[*].{email: email, role: role}'
    """
    try:
        team = load_team()
        
        # Handle --json flag as shorthand for --format json
        if json_output:
            output_format = OutputFormat.JSON

        if not team or not team.members:
            console.print("[yellow]No team members found.[/yellow]")
            console.print("Run [cyan]gira team add[/cyan] to add team members.")
            return

        # Filter members
        members = team.members
        if active_only:
            members = [m for m in members if m.active]
        if role:
            members = [m for m in members if m.role.lower() == role.lower()]

        if not members:
            console.print(f"[yellow]No members found with role '{role}'[/yellow]")
            return
        
        # Validate filter_json is only used with JSON format
        if filter_json and output_format != OutputFormat.JSON:
            console.print("[red]Error:[/red] --filter-json can only be used with --format json or --json")
            raise typer.Exit(1)

        if output_format == OutputFormat.TABLE:
            # Use the existing table display
            show_team_table(members, team)
        else:
            # Prepare data for other formats
            output = []
            for member in members:
                member_dict = {
                    "email": member.email,
                    "name": member.name,
                    "role": member.role,
                    "active": member.active,
                    "joined_at": member.joined_at.isoformat()
                }
                if member.username:
                    member_dict["username"] = member.username

                # Find aliases
                aliases = [alias for alias, email in team.aliases.items() if email == member.email]
                if aliases:
                    member_dict["aliases"] = ", ".join(aliases)

                output.append(member_dict)

            # Use the new output system for other formats
            color_kwargs = get_color_kwargs(color, no_color)
            print_output(output, output_format, jsonpath_filter=filter_json, **color_kwargs)

    except Exception as e:
        console.print(f"[red]Error listing team members: {e}[/red]")
        raise typer.Exit(1)
