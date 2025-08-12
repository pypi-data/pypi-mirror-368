"""CLI command for migrating to hybrid directory structure."""


import typer
from gira.utils.console import console
from gira.migration.migrate_to_hybrid import (
    get_backlog_ticket_count,
    migrate_backlog_to_hybrid,
    update_config_for_hybrid,
    verify_migration,
)
from gira.utils.project import get_gira_root

def hybrid(
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview migration without making changes"
    ),
    verify: bool = typer.Option(
        False,
        "--verify",
        help="Verify current migration status without changes"
    ),
    force: bool = typer.Option(
        False,
        "--force", "-f",
        help="Skip confirmation prompts"
    ),
) -> None:
    """
    Migrate the project to use hybrid directory structure for backlog tickets.

    The hybrid structure uses:
    - Flat directories for active board tickets (human-readable)
    - Hashed directories for backlog tickets (Git performance)

    This improves Git performance for projects with large backlogs (1000+ tickets)
    while maintaining readability for active work.
    """
    # Get project root
    root = get_gira_root()
    if not root:
        console.print("[red]Error:[/red] Not in a Gira project")
        raise typer.Exit(1)

    console.print("[bold]Gira Hybrid Structure Migration[/bold]")
    console.print(f"Project: {root.name}\\n")

    if verify:
        # Just verify current state
        verify_migration(root)
        raise typer.Exit(0)

    # Check current state
    flat_count, hashed_count = get_backlog_ticket_count(root)

    if flat_count == 0 and hashed_count > 0:
        console.print("[green]✓[/green] Project already using hybrid structure")
        verify_migration(root)
        raise typer.Exit(0)
    elif flat_count == 0:
        console.print("[dim]No backlog tickets to migrate[/dim]")
        update_config_for_hybrid(root, dry_run)
        raise typer.Exit(0)

    console.print(f"Found [yellow]{flat_count}[/yellow] tickets to migrate\\n")

    if dry_run:
        console.print("[yellow]DRY RUN MODE[/yellow] - No changes will be made\\n")
    elif not force:
        # Confirm migration
        confirm = typer.confirm(
            f"Migrate {flat_count} backlog tickets to hybrid structure?"
        )
        if not confirm:
            console.print("Migration cancelled")
            raise typer.Exit(0)

    # Perform migration
    migrated, failed = migrate_backlog_to_hybrid(root, dry_run)

    console.print("\\n[bold]Migration Summary:[/bold]")
    console.print(f"  Successfully migrated: [green]{migrated}[/green]")
    if failed > 0:
        console.print(f"  Failed: [red]{failed}[/red]")

    if not dry_run and failed == 0:
        # Update config
        update_config_for_hybrid(root)

        # Verify migration
        console.print()
        verify_migration(root)

        console.print("\\n[green]✓[/green] Migration completed successfully!")
        console.print("\\nBenefits:")
        console.print("  • Faster Git operations for large backlogs")
        console.print("  • Active tickets remain human-readable")
        console.print("  • Automatic routing based on ticket status")

    exit_code = 0 if failed == 0 else 1
    raise typer.Exit(exit_code)
