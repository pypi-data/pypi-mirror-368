"""Hook management commands for Gira."""

import os
import shutil
from typing import Optional

import typer
from rich.syntax import Syntax
from rich.table import Table

from gira.utils.console import console
from gira.utils.hooks import get_hook_executor
from gira.utils.project import ensure_gira_project

app = typer.Typer(help="Manage Gira hooks for extensibility")


@app.command("list")
def list_hooks(
        verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information about each hook")
) -> None:
    """List all available hooks and their status."""
    root = ensure_gira_project()
    hooks_dir = root / ".gira" / "hooks"

    if not hooks_dir.exists():
        console.print("[yellow]No hooks directory found. Use 'gira hooks init' to create it.[/yellow]")
        return

    # Get all hook files
    hook_files = []
    for ext in ['.sh', '.py', '.js', '.rb']:
        hook_files.extend(hooks_dir.glob(f"*{ext}"))

    # Also check for extension-less executable files
    for file in hooks_dir.iterdir():
        if file.is_file() and not file.suffix and os.access(file, os.X_OK):
            hook_files.append(file)

    if not hook_files:
        console.print("[yellow]No hooks found in .gira/hooks/[/yellow]")
        console.print("Use 'gira hooks install <hook-name>' to install hook templates")
        return

    # Get hook executor to check if hooks are enabled
    try:
        executor = get_hook_executor()
        hooks_enabled = executor.is_enabled()
        timeout = executor.get_timeout()
    except Exception:
        hooks_enabled = True
        timeout = 30

    console.print(f"\n[bold]Hook System Status:[/bold] {'🟢 Enabled' if hooks_enabled else '🔴 Disabled'}")
    if hooks_enabled:
        console.print(f"[bold]Timeout:[/bold] {timeout} seconds")
    console.print()

    # Create table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Hook", style="cyan")
    table.add_column("Type", width=8)
    table.add_column("Executable", width=10)
    table.add_column("Size", width=8)

    if verbose:
        table.add_column("Modified", width=16)
        table.add_column("Path", style="dim")

    for hook_file in sorted(hook_files):
        hook_name = hook_file.name
        hook_type = hook_file.suffix[1:] if hook_file.suffix else "script"
        is_executable = os.access(hook_file, os.X_OK)
        file_size = f"{hook_file.stat().st_size}B" if hook_file.stat().st_size < 1024 else f"{hook_file.stat().st_size // 1024}KB"

        executable_status = "✅ Yes" if is_executable else "❌ No"

        row = [hook_name, hook_type, executable_status, file_size]

        if verbose:
            from datetime import datetime
            mtime = datetime.fromtimestamp(hook_file.stat().st_mtime)
            row.extend([mtime.strftime("%Y-%m-%d %H:%M"), str(hook_file)])

        table.add_row(*row)

    console.print(table)

    if not hooks_enabled:
        console.print("\n[yellow]💡 Hooks are disabled. Enable them with:[/yellow]")
        console.print("   gira config set hooks.enabled true")

    # Check for non-executable hooks
    non_executable = [f for f in hook_files if not os.access(f, os.X_OK)]
    if non_executable:
        console.print(
            f"\n[yellow]⚠️  {len(non_executable)} hook(s) are not executable. Make them executable with:[/yellow]")
        for hook in non_executable[:3]:  # Show first 3
            console.print(f"   chmod +x {hook}")
        if len(non_executable) > 3:
            console.print(f"   ... and {len(non_executable) - 3} more")


@app.command("init")
def init_hooks(
        force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing hooks directory")
) -> None:
    """Initialize the hooks directory with example templates."""
    root = ensure_gira_project()
    hooks_dir = root / ".gira" / "hooks"

    if hooks_dir.exists() and not force:
        console.print(f"[yellow]Hooks directory already exists at {hooks_dir}[/yellow]")
        console.print("Use --force to overwrite existing directory")
        return

    # Create hooks directory
    hooks_dir.mkdir(parents=True, exist_ok=True)

    # Copy templates from the templates directory
    templates_dir = root / ".gira" / "templates" / "hooks"

    if not templates_dir.exists():
        console.print("[yellow]No hook templates found. Creating basic directory structure.[/yellow]")

        # Create a simple example hook
        example_hook = hooks_dir / "ticket-created.sh"
        example_hook.write_text('''#!/bin/bash
# Example hook: ticket-created
# This hook runs when a new ticket is created

echo "New ticket created: $GIRA_TICKET_ID - $GIRA_TICKET_TITLE"

# Add your custom logic here
# Examples:
# - Send notifications
# - Update external systems  
# - Auto-assign tickets
# - Log events
''')
        example_hook.chmod(0o755)  # Make executable

        console.print(f"[green]✓[/green] Created example hook: {example_hook}")
    else:
        # Copy templates
        copied_count = 0
        for template in templates_dir.glob("*"):
            if template.is_file():
                dest = hooks_dir / template.name
                shutil.copy2(template, dest)
                dest.chmod(0o755)  # Make executable
                copied_count += 1
                console.print(f"[green]✓[/green] Installed hook template: {template.name}")

        console.print(f"\n[green]Installed {copied_count} hook templates[/green]")

    console.print(f"\n[bold]Hooks directory initialized at:[/bold] {hooks_dir}")
    console.print("\n[yellow]Next steps:[/yellow]")
    console.print("1. Review and customize the hook templates")
    console.print("2. Make sure hooks are executable: chmod +x .gira/hooks/*")
    console.print("3. Test your hooks: gira hooks test <hook-name>")
    console.print("4. Enable hooks if needed: gira config set hooks.enabled true")


@app.command("install")
def install_hook(
        hook_name: str = typer.Argument(..., help="Name of the hook template to install"),
        force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing hook")
) -> None:
    """Install a specific hook template."""
    root = ensure_gira_project()
    hooks_dir = root / ".gira" / "hooks"
    templates_dir = root / ".gira" / "templates" / "hooks"

    # Ensure hooks directory exists
    hooks_dir.mkdir(parents=True, exist_ok=True)

    # Find template file (try different extensions)
    template_file = None
    for ext in ['', '.sh', '.py', '.js', '.rb']:
        potential_template = templates_dir / f"{hook_name}{ext}"
        if potential_template.exists():
            template_file = potential_template
            break

    if not template_file:
        console.print(f"[red]Hook template '{hook_name}' not found[/red]")
        console.print(f"Available templates in {templates_dir}:")
        if templates_dir.exists():
            for template in templates_dir.glob("*"):
                if template.is_file():
                    console.print(f"  - {template.stem}")
        else:
            console.print("  (No templates directory found)")
        return

    # Copy template
    dest_file = hooks_dir / template_file.name

    if dest_file.exists() and not force:
        console.print(f"[yellow]Hook '{dest_file.name}' already exists[/yellow]")
        console.print("Use --force to overwrite")
        return

    shutil.copy2(template_file, dest_file)
    dest_file.chmod(0o755)  # Make executable

    console.print(f"[green]✓[/green] Installed hook: {dest_file.name}")
    console.print(f"[dim]Location: {dest_file}[/dim]")
    console.print("\n[yellow]Don't forget to customize the hook for your needs![/yellow]")


@app.command("test")
def test_hook(
        hook_name: str = typer.Argument(..., help="Name of the hook to test"),
        event_data: Optional[str] = typer.Option(None, "--data", help="JSON string with test event data")
) -> None:
    """Test a hook with sample data."""
    root = ensure_gira_project()

    try:
        executor = get_hook_executor()
    except Exception as e:
        console.print(f"[red]Error initializing hook executor: {e}[/red]")
        return

    # Prepare test data
    if event_data:
        import json
        try:
            test_data = json.loads(event_data)
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON in --data parameter[/red]")
            return
    else:
        # Use sample data based on hook name
        if "ticket" in hook_name:
            test_data = {
                "ticket_id": "TEST-123",
                "ticket_title": "Test Ticket for Hook Testing",
                "ticket_description": "This is a test ticket used for hook testing",
                "ticket_status": "todo",
                "ticket_type": "task",
                "ticket_priority": "medium",
                "ticket_assignee": "test@example.com",
                "ticket_reporter": "test@example.com",
                "ticket_labels": "test,hook",
                "ticket_created_at": "2023-01-01T12:00:00Z"
            }

            if "moved" in hook_name:
                test_data.update({
                    "old_status": "todo",
                    "new_status": "in_progress"
                })
        elif "sprint" in hook_name:
            test_data = {
                "sprint_id": "SPRINT-TEST-01",
                "sprint_name": "Test Sprint",
                "sprint_status": "completed",
                "sprint_start_date": "2023-01-01T00:00:00Z",
                "sprint_end_date": "2023-01-14T23:59:59Z",
                "sprint_tickets": "TEST-123,TEST-124,TEST-125"
            }
        else:
            test_data = {"test": "true", "hook_name": hook_name}

    console.print(f"[bold]Testing hook:[/bold] {hook_name}")
    console.print(f"[bold]Test data:[/bold]")

    # Show test data in a nice format
    for key, value in test_data.items():
        console.print(f"  [cyan]{key.upper()}[/cyan] = {value}")

    console.print(f"\n[yellow]Executing hook...[/yellow]")

    # Execute the hook
    success = executor.execute_hook(hook_name, test_data, silent=False)

    if success:
        console.print(f"\n[green]✅ Hook '{hook_name}' executed successfully[/green]")
    else:
        console.print(f"\n[red]❌ Hook '{hook_name}' failed or timed out[/red]")


@app.command("enable")
def enable_hooks() -> None:
    """Enable hook execution."""
    from gira.utils.config import load_config, save_config

    ensure_gira_project()
    config = load_config()

    if "hooks" not in config:
        config["hooks"] = {}

    config["hooks"]["enabled"] = True
    save_config(config)

    console.print("[green]✅ Hooks enabled[/green]")


@app.command("disable")
def disable_hooks() -> None:
    """Disable hook execution."""
    from gira.utils.config import load_config, save_config

    ensure_gira_project()
    config = load_config()

    if "hooks" not in config:
        config["hooks"] = {}

    config["hooks"]["enabled"] = False
    save_config(config)

    console.print("[yellow]🔴 Hooks disabled[/yellow]")


@app.command("show")
def show_hook(
        hook_name: str = typer.Argument(..., help="Name of the hook to display")
) -> None:
    """Display the contents of a hook file."""
    root = ensure_gira_project()
    hooks_dir = root / ".gira" / "hooks"

    # Find hook file (try different extensions)
    hook_file = None
    for ext in ['', '.sh', '.py', '.js', '.rb']:
        potential_file = hooks_dir / f"{hook_name}{ext}"
        if potential_file.exists():
            hook_file = potential_file
            break

    if not hook_file:
        console.print(f"[red]Hook '{hook_name}' not found[/red]")
        return

    try:
        content = hook_file.read_text()

        # Determine syntax highlighting based on file extension
        if hook_file.suffix == '.py':
            lexer = "python"
        elif hook_file.suffix == '.js':
            lexer = "javascript"
        elif hook_file.suffix == '.rb':
            lexer = "ruby"
        else:
            lexer = "bash"

        syntax = Syntax(content, lexer, theme="monokai", line_numbers=True)

        console.print(f"\n[bold]Hook: {hook_file.name}[/bold]")
        console.print(f"[dim]Path: {hook_file}[/dim]")
        console.print(f"[dim]Executable: {'Yes' if os.access(hook_file, os.X_OK) else 'No'}[/dim]\n")

        console.print(syntax)

    except Exception as e:
        console.print(f"[red]Error reading hook file: {e}[/red]")


if __name__ == "__main__":
    app()
