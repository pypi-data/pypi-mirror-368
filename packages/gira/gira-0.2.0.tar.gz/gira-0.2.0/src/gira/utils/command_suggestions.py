"""Command suggestion utilities for better error messages."""

import difflib
from typing import List, Optional, Tuple, Dict, Any
import click
import typer
from click.core import Context, Command
from typer.core import TyperGroup


def get_available_commands(ctx: Context) -> Dict[str, str]:
    """Get available commands and their help text from the current context.
    
    Args:
        ctx: Click context object
        
    Returns:
        Dictionary mapping command names to their help text
    """
    commands = {}
    
    if ctx.parent and hasattr(ctx.parent, 'command'):
        # We're in a subcommand group
        group = ctx.parent.command
        if isinstance(group, (click.Group, TyperGroup)):
            for name, cmd in group.commands.items():
                if not name.startswith('_'):
                    help_text = cmd.get_short_help_str(limit=80) if hasattr(cmd, 'get_short_help_str') else cmd.help or ""
                    commands[name] = help_text
    elif hasattr(ctx, 'command') and isinstance(ctx.command, (click.Group, TyperGroup)):
        # We're at the main command level
        for name, cmd in ctx.command.commands.items():
            if not name.startswith('_'):
                help_text = cmd.get_short_help_str(limit=50) if hasattr(cmd, 'get_short_help_str') else cmd.help or ""
                commands[name] = help_text
                
    return commands


def find_similar_commands(
    attempted_cmd: str,
    available_commands: List[str],
    max_suggestions: int = 3,
    cutoff: float = 0.6
) -> List[str]:
    """Find commands similar to the attempted command.
    
    Args:
        attempted_cmd: The command the user tried to run
        available_commands: List of available command names
        max_suggestions: Maximum number of suggestions to return
        cutoff: Minimum similarity score (0.0 to 1.0)
        
    Returns:
        List of similar command names, ordered by similarity
    """
    # Use difflib to find close matches
    matches = difflib.get_close_matches(
        attempted_cmd,
        available_commands,
        n=max_suggestions,
        cutoff=cutoff
    )
    
    # If no matches with default cutoff, try a lower threshold
    if not matches and cutoff > 0.4:
        matches = difflib.get_close_matches(
            attempted_cmd,
            available_commands,
            n=max_suggestions,
            cutoff=0.4
        )
    
    return matches


def format_suggestions(suggestions: List[Tuple[str, str]]) -> str:
    """Format command suggestions for display.
    
    Args:
        suggestions: List of (command_name, help_text) tuples
        
    Returns:
        Formatted string with suggestions
    """
    if not suggestions:
        return ""
    
    lines = ["\n[yellow]Did you mean one of these?[/yellow]"]
    for cmd, help_text in suggestions:
        if help_text:
            lines.append(f"  [cyan]→[/cyan] [bold]{cmd}[/bold] - {help_text}")
        else:
            lines.append(f"  [cyan]→[/cyan] [bold]{cmd}[/bold]")
    
    return "\n".join(lines)


def suggest_commands(ctx: Context, attempted_cmd: str) -> Optional[str]:
    """Generate command suggestions for a failed command attempt.
    
    Args:
        ctx: Click context
        attempted_cmd: The command that was attempted
        
    Returns:
        Formatted suggestion string, or None if no suggestions
    """
    available = get_available_commands(ctx)
    if not available:
        return None
    
    similar = find_similar_commands(attempted_cmd, list(available.keys()))
    if not similar:
        return None
    
    suggestions = [(cmd, available[cmd]) for cmd in similar]
    return format_suggestions(suggestions)


def handle_command_error(error: click.ClickException, ctx: Context) -> None:
    """Enhanced error handler that adds command suggestions.
    
    Args:
        error: The Click exception that was raised
        ctx: Click context
    """
    from gira.utils.console import console
    
    # Check if this is a "no such command" error
    error_msg = str(error)
    if "No such command" in error_msg:
        # Extract the attempted command name
        import re
        match = re.search(r"No such command ['\"](\w+)['\"]", error_msg)
        if match:
            attempted_cmd = match.group(1)
            suggestions = suggest_commands(ctx, attempted_cmd)
            
            # Print the original error
            console.print(f"[red]Error:[/red] {error_msg}")
            
            # Print suggestions if available
            if suggestions:
                console.print(suggestions)
            
            # Exit with error code
            raise typer.Exit(2)
    
    # For other errors, just re-raise
    raise error


class SuggestiveGroup(TyperGroup):
    """Typer Group that provides command suggestions for typos."""
    
    def resolve_command(self, ctx: Context, args: List[str]) -> Tuple[Optional[str], Optional[Command], List[str]]:
        """Override to provide suggestions when command resolution fails."""
        try:
            return super().resolve_command(ctx, args)
        except click.exceptions.UsageError as e:
            # Check if this is a "no such command" error
            error_msg = str(e)
            if "No such command" in error_msg and args:
                attempted_cmd = args[0]
                
                # Get available commands
                available = {}
                for name, cmd in self.commands.items():
                    if not name.startswith('_'):
                        help_text = cmd.get_short_help_str(limit=80) if hasattr(cmd, 'get_short_help_str') else ""
                        available[name] = help_text
                
                # Find similar commands
                similar = find_similar_commands(attempted_cmd, list(available.keys()))
                
                if similar:
                    from gira.utils.console import console
                    
                    # Show error with suggestions
                    console.print(f"\n[red]Error:[/red] No such command '{attempted_cmd}'")
                    
                    suggestions = [(cmd, available[cmd]) for cmd in similar]
                    console.print(format_suggestions(suggestions))
                    
                    raise typer.Exit(2)
            
            # Re-raise the original error if no suggestions
            raise


def create_typer_with_suggestions(
    name: Optional[str] = None,
    help: Optional[str] = None,
    **kwargs
) -> typer.Typer:
    """Create a Typer app with command suggestions enabled.
    
    Args:
        name: App name
        help: App help text
        **kwargs: Other arguments to pass to Typer()
        
    Returns:
        Typer app with suggestion support
    """
    # Create the app with our custom group class
    app = typer.Typer(
        name=name,
        help=help,
        cls=SuggestiveGroup,
        **kwargs
    )
    return app