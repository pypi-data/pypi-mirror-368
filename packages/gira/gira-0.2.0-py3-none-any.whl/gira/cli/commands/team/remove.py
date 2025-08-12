"""Remove team member command."""

import typer
from gira.utils.console import console
from rich.prompt import Confirm

from gira.utils.team_utils import load_team, remove_team_member

def remove_member(
    identifier: str = typer.Argument(..., help="Email, username, or alias of the team member to remove"),
    force: bool = typer.Option(False, "-f", "--force", help="Skip confirmation prompt"),
) -> None:
    """Remove a team member."""
    try:
        # Load team to find member
        team = load_team()
        if not team:
            console.print("[yellow]No team configuration found.[/yellow]")
            raise typer.Exit(1)

        # Find the member
        member = team.find_member(identifier)
        if not member:
            console.print(f"[red]Error:[/red] No team member found with identifier: {identifier}")
            raise typer.Exit(1)

        # Show member details
        console.print("[bold]Member to remove:[/bold]")
        console.print(f"  Email: [cyan]{member.email}[/cyan]")
        console.print(f"  Name: {member.name}")
        if member.username:
            console.print(f"  Username: [yellow]@{member.username}[/yellow]")
        console.print(f"  Role: [green]{member.role}[/green]")

        # Find aliases
        aliases = [alias for alias, email in team.aliases.items() if email == member.email]
        if aliases:
            console.print(f"  Aliases: {', '.join([f'[yellow]@{a}[/yellow]' for a in aliases])}")

        # Check for tickets assigned to this member
        # TODO: Implement when ticket search by assignee is available
        # tickets = search_tickets_by_assignee(member.email)
        # if tickets:
        #     console.print(f"\n[yellow]Warning:[/yellow] This member has {len(tickets)} assigned tickets")

        # Confirm removal
        if not force:
            if not Confirm.ask(f"Remove {member.name} from the team?"):
                console.print("[yellow]Cancelled[/yellow]")
                raise typer.Exit(0)

        # Remove the member
        if remove_team_member(identifier):
            console.print(f"[green]✓[/green] Removed team member: {member.name} ({member.email})")

            # Note about aliases
            if aliases:
                console.print(f"[dim]Also removed aliases: {', '.join([f'@{a}' for a in aliases])}[/dim]")

            # Note about reassignment
            console.print()
            console.print("[yellow]Note:[/yellow] Any tickets assigned to this member will remain assigned to their email address.")
            console.print("Consider reassigning their tickets to other team members.")
        else:
            console.print("[red]Error:[/red] Failed to remove team member")
            raise typer.Exit(1)

    except typer.Exit:
        # Re-raise Exit exceptions to preserve exit code
        raise
    except Exception as e:
        if "No team member found" not in str(e):
            console.print(f"[red]Error removing team member: {e}[/red]")
        raise typer.Exit(1)
