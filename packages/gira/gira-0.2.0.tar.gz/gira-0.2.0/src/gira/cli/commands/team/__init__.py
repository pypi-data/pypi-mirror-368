"""Team management commands for Gira."""

import typer
from gira.utils.console import console
from gira.cli.commands.team.add import add_member
from gira.cli.commands.team.discover import discover_members
from gira.cli.commands.team.list import list_members
from gira.cli.commands.team.remove import remove_member

# Create the team subcommand group
team_app = typer.Typer(
    name="team",
    help="Team management commands",
    no_args_is_help=True
)

# Register subcommands
team_app.command("list")(list_members)
team_app.command("add")(add_member)
team_app.command("remove")(remove_member)
team_app.command("discover")(discover_members)

__all__ = ["team_app"]
