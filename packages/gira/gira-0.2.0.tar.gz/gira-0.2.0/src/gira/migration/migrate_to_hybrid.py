#!/usr/bin/env python3
"""Migration script to convert flat backlog structure to hybrid hashed structure.

This script migrates existing Gira projects from the flat directory structure
to the new hybrid structure where backlog tickets use hashed directories.
"""

import argparse
import json
from pathlib import Path
from typing import Tuple

from gira.utils.console import console
from rich.progress import Progress, SpinnerColumn, TextColumn

from gira.models import Ticket
from gira.utils.hybrid_storage import get_backlog_ticket_count, get_hash_path
from gira.utils.project import get_gira_root

def migrate_backlog_to_hybrid(root: Path, dry_run: bool = False) -> Tuple[int, int]:
    """
    Migrate backlog tickets from flat to hashed structure.

    Args:
        root: The project root path
        dry_run: If True, only simulate the migration without making changes

    Returns:
        Tuple of (migrated_count, failed_count)
    """
    backlog_dir = root / ".gira" / "backlog"
    if not backlog_dir.exists():
        return 0, 0

    # Find all flat structure tickets (JSON files directly in backlog)
    flat_tickets = list(backlog_dir.glob("*.json"))

    if not flat_tickets:
        console.print("[green]No flat backlog tickets to migrate[/green]")
        return 0, 0

    migrated = 0
    failed = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(
            f"Migrating {len(flat_tickets)} backlog tickets...", total=len(flat_tickets)
        )

        for ticket_file in flat_tickets:
            try:
                # Load ticket
                ticket = Ticket.from_json_file(str(ticket_file))

                # Get hashed path
                hash_path = get_hash_path(ticket.id)
                new_dir = backlog_dir / hash_path
                new_path = new_dir / ticket_file.name

                if dry_run:
                    console.print(
                        f"[dim]Would move:[/dim] {ticket_file.name} → {hash_path}/{ticket_file.name}"
                    )
                else:
                    # Create hashed directory structure
                    new_dir.mkdir(parents=True, exist_ok=True)

                    # Move the file
                    ticket_file.rename(new_path)
                    console.print(
                        f"[green]✓[/green] Migrated {ticket.id} → {hash_path}/{ticket_file.name}"
                    )

                migrated += 1

            except Exception as e:
                console.print(f"[red]✗[/red] Failed to migrate {ticket_file.name}: {e}")
                failed += 1

            progress.update(task, advance=1)

    return migrated, failed


def verify_migration(root: Path) -> bool:
    """
    Verify that the migration was successful.

    Args:
        root: The project root path

    Returns:
        True if migration appears successful, False otherwise
    """
    flat_count, hashed_count = get_backlog_ticket_count(root)

    console.print("\n[bold]Migration Verification:[/bold]")
    console.print(f"  Flat structure tickets: {flat_count}")
    console.print(f"  Hashed structure tickets: {hashed_count}")

    if flat_count == 0 and hashed_count > 0:
        console.print("[green]✓ Migration verified successfully[/green]")
        return True
    elif flat_count > 0:
        console.print(
            f"[yellow]⚠ {flat_count} tickets still in flat structure[/yellow]"
        )
        return False
    else:
        console.print("[dim]No backlog tickets found[/dim]")
        return True


def update_config_for_hybrid(root: Path, dry_run: bool = False) -> None:
    """
    Update project config to indicate hybrid structure is enabled.

    Args:
        root: The project root path
        dry_run: If True, only simulate the update
    """
    config_path = root / ".gira" / "config.json"

    if not config_path.exists():
        console.print("[yellow]Warning:[/yellow] No config.json found")
        return

    with open(config_path) as f:
        config = json.load(f)

    # Add hybrid structure flag
    if "features" not in config:
        config["features"] = {}

    if not config["features"].get("hybrid_backlog", False):
        config["features"]["hybrid_backlog"] = True

        if dry_run:
            console.print(
                "[dim]Would update config.json to enable hybrid_backlog feature[/dim]"
            )
        else:
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            console.print(
                "[green]✓[/green] Updated config.json to enable hybrid_backlog feature"
            )


def main():
    """Main entry point for migration script."""
    parser = argparse.ArgumentParser(
        description="Migrate Gira project to hybrid directory structure"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate migration without making changes",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify migration status without making changes",
    )

    args = parser.parse_args()

    # Get project root
    root = get_gira_root()
    if not root:
        console.print("[red]Error:[/red] Not in a Gira project")
        return 1

    console.print("[bold]Gira Hybrid Structure Migration[/bold]")
    console.print(f"Project: {root.name}\n")

    if args.verify_only:
        # Just verify current state
        verify_migration(root)
        return 0

    # Check current state
    flat_count, hashed_count = get_backlog_ticket_count(root)

    if flat_count == 0 and hashed_count > 0:
        console.print("[green]✓[/green] Project already using hybrid structure")
        verify_migration(root)
        return 0
    elif flat_count == 0:
        console.print("[dim]No backlog tickets to migrate[/dim]")
        update_config_for_hybrid(root, args.dry_run)
        return 0

    console.print(f"Found [yellow]{flat_count}[/yellow] tickets to migrate\n")

    if args.dry_run:
        console.print("[yellow]DRY RUN MODE[/yellow] - No changes will be made\n")

    # Perform migration
    migrated, failed = migrate_backlog_to_hybrid(root, args.dry_run)

    console.print("\n[bold]Migration Summary:[/bold]")
    console.print(f"  Successfully migrated: [green]{migrated}[/green]")
    if failed > 0:
        console.print(f"  Failed: [red]{failed}[/red]")

    if not args.dry_run and failed == 0:
        # Update config
        update_config_for_hybrid(root)

        # Verify migration
        verify_migration(root)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
