"""Complete sprint command - alias for close."""

from typing import Optional
import typer

from gira.cli.commands.sprint.close import close as close_sprint


def complete(
    sprint_id: str = typer.Argument(
        ...,
        help="Sprint ID to complete"
    ),
    retrospective: bool = typer.Option(
        True,
        "--retrospective/--no-retrospective",
        help="Include retrospective"
    ),
    git: Optional[bool] = typer.Option(
        None,
        "--git/--no-git",
        help="Stage the sprint move using 'git mv'"
    ),
) -> None:
    """Complete a sprint (alias for close).
    
    This is a more intuitive alias for the 'close' command. It changes the
    sprint status to completed and optionally collects retrospective feedback.
    
    Git Integration:
        By default, sprint moves are automatically staged with 'git mv' if .gira is tracked.
        Control this behavior with:
        - --git / --no-git flags
        - GIRA_AUTO_GIT_MV environment variable
        - git.auto_stage_moves in config.json
    """
    # Simply call the close function with the same parameters
    close_sprint(sprint_id=sprint_id, retrospective=retrospective, git=git)