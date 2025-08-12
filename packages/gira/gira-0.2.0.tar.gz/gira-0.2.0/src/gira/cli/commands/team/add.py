"""Add team member command."""

from typing import List, Optional

import typer
from gira.utils.console import console
from rich.prompt import Prompt

from gira.utils.team_utils import add_team_member, load_team

def add_member(
    email: str = typer.Argument(..., help="Email address of the team member"),
    name: Optional[str] = typer.Option(None, "-n", "--name", help="Display name"),
    username: Optional[str] = typer.Option(None, "-u", "--username", help="Username for @mentions"),
    role: str = typer.Option("developer", "-r", "--role", help="Role in the project"),
    aliases: Optional[List[str]] = typer.Option(None, "-a", "--alias", help="Alias for quick assignment (can be used multiple times)"),
    interactive: bool = typer.Option(False, "-i", "--interactive", help="Interactive mode"),
) -> None:
    """Add a new team member."""
    try:
        # Load existing team to validate
        team = load_team()

        # Interactive mode
        if interactive:
            email = Prompt.ask("Email address", default=email if email != "..." else "")
            name = Prompt.ask("Display name", default=name or email.split("@")[0])
            username = Prompt.ask("Username (for @mentions)", default=username or "")

            # Show available roles
            available_roles = team.roles if team else ["lead", "developer", "reviewer", "observer"]
            console.print(f"[dim]Available roles: {', '.join(available_roles)}[/dim]")
            role = Prompt.ask("Role", default=role, choices=available_roles)

            # Aliases
            alias_list = []
            while True:
                alias = Prompt.ask("Add alias (or press Enter to skip)", default="")
                if not alias:
                    break
                alias_list.append(alias)
            if alias_list:
                aliases = alias_list

        # Use email username as name if not provided
        if not name:
            name = email.split("@")[0]

        # Validate email format
        if "@" not in email:
            console.print("[red]Error:[/red] Invalid email format")
            raise typer.Exit(1)

        # Check if member already exists
        if team and team.find_member(email):
            console.print(f"[red]Error:[/red] Member with email {email} already exists")
            raise typer.Exit(1)

        # Add the member
        member = add_team_member(
            email=email,
            name=name,
            username=username,
            role=role
        )

        # Add aliases if provided
        if aliases and team:
            team = load_team()  # Reload after adding member
            for alias in aliases:
                try:
                    team.add_alias(alias, email)
                except ValueError as e:
                    console.print(f"[yellow]Warning:[/yellow] {e}")

            # Save team with aliases
            from gira.utils.team_utils import save_team
            save_team(team)

        # Success message
        console.print(f"[green]✓[/green] Added team member: {member.name} ({member.email})")

        # Show member details
        console.print()
        console.print("[bold]Member Details:[/bold]")
        console.print(f"  Email: [cyan]{member.email}[/cyan]")
        console.print(f"  Name: {member.name}")
        if member.username:
            console.print(f"  Username: [yellow]@{member.username}[/yellow]")
        console.print(f"  Role: [green]{member.role}[/green]")
        if aliases:
            console.print(f"  Aliases: {', '.join([f'[yellow]@{a}[/yellow]' for a in aliases])}")
        console.print("  Status: [green]Active[/green]")

        # Show usage examples
        console.print()
        console.print("[dim]Usage examples:[/dim]")
        console.print(f"  gira ticket create \"New task\" -a {email}")
        if member.username:
            console.print(f"  gira ticket create \"New task\" -a @{member.username}")
        if aliases:
            console.print(f"  gira ticket create \"New task\" -a @{aliases[0]}")

    except Exception as e:
        if "already exists" not in str(e):
            console.print(f"[red]Error adding team member: {e}[/red]")
        raise typer.Exit(1)
