"""Backup and restore commands for Gira projects."""

import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from gira.utils.console import console
from gira.utils.help_formatter import create_example, format_examples_simple
from rich.prompt import Confirm

from gira.utils.project import ensure_gira_project

def backup(
        output: Optional[Path] = typer.Option(
            None,
            "--output",
            "-o",
            help="Output file path. If not specified, creates backup in current directory",
        ),
        exclude_archived: bool = typer.Option(
            False,
            "--exclude-archived",
            help="Exclude archived tickets from the backup",
        ),
) -> None:
    f"""Create a backup of the entire Gira project.
    
    Creates a compressed tar.gz archive containing all project data from the .gira directory.
    The backup filename includes the project name and timestamp for easy identification.
    {format_examples_simple([
        create_example("Create backup in current directory", "gira backup"),
        create_example("Create backup at specific location", "gira backup --output ~/backups/my-project.tar.gz"),
        create_example("Create backup excluding archived tickets", "gira backup --exclude-archived")
    ])}"""
    root = ensure_gira_project()
    gira_dir = root / ".gira"

    # Load project config to get project name
    config_file = gira_dir / "config.json"
    if config_file.exists():
        import json
        with open(config_file) as f:
            config = json.load(f)
            project_name = config.get("name", "gira-project").lower().replace(" ", "-")
    else:
        project_name = "gira-project"

    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    default_filename = f"{project_name}-backup-{timestamp}.tar.gz"

    # Determine output path
    if output:
        backup_path = output
        # Ensure parent directory exists
        backup_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        backup_path = Path.cwd() / default_filename

    console.print(f"📦 Creating backup of Gira project...", style="bold cyan")

    try:
        # Create temporary directory for filtered backup if needed
        if exclude_archived:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Copy all non-archived content
                import shutil

                # Copy everything except archived directory
                for item in gira_dir.iterdir():
                    if item.name == "archived":
                        continue

                    dest = temp_path / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest)
                    else:
                        shutil.copy2(item, dest)

                # Create tar.gz from temp directory
                with tarfile.open(backup_path, "w:gz") as tar:
                    tar.add(temp_path, arcname=".gira")
        else:
            # Create tar.gz directly from .gira directory
            with tarfile.open(backup_path, "w:gz") as tar:
                tar.add(gira_dir, arcname=".gira")

        # Calculate backup size
        size_mb = backup_path.stat().st_size / (1024 * 1024)

        console.print(f"✅ Backup created successfully!", style="bold green")
        console.print(f"   📄 File: [cyan]{backup_path}[/cyan]")
        console.print(f"   📊 Size: {size_mb:.2f} MB")

    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to create backup: {e}")
        raise typer.Exit(1)


def restore(
        backup_file: Path = typer.Argument(
            ...,
            help="Path to the backup file to restore",
            exists=True,
        ),
        target: Optional[Path] = typer.Option(
            None,
            "--target",
            "-t",
            help="Target directory for restoration. Defaults to current directory",
        ),
        force: bool = typer.Option(
            False,
            "--force",
            "-f",
            help="Skip confirmation prompt",
        ),
) -> None:
    f"""Restore a Gira project from a backup archive.
    
    Extracts a previously created backup archive to restore the .gira directory.
    By default, restores to the current directory, but you can specify a different target.
    {format_examples_simple([
        create_example("Restore backup to current directory", "gira restore my-project-backup-2025-07-14.tar.gz"),
        create_example("Restore to specific directory", "gira restore backup.tar.gz --target ~/projects/restored-project"),
        create_example("Restore without confirmation prompt", "gira restore backup.tar.gz --force")
    ])}"""
    # Determine target directory
    if target:
        target_dir = target
        target_dir.mkdir(parents=True, exist_ok=True)
    else:
        target_dir = Path.cwd()

    gira_target = target_dir / ".gira"

    # Check if .gira already exists
    if gira_target.exists():
        if not force:
            console.print(
                f"⚠️  [yellow]Warning:[/yellow] A .gira directory already exists at [cyan]{target_dir}[/cyan]",
                style="bold",
            )
            console.print("   This operation will overwrite the existing project data.")

            if not Confirm.ask("   Do you want to continue?", default=False):
                console.print("❌ Restore cancelled", style="red")
                raise typer.Exit(0)

    console.print(f"📦 Restoring Gira project from backup...", style="bold cyan")

    try:
        # Verify it's a valid tar.gz file
        if not tarfile.is_tarfile(backup_file):
            raise ValueError("Invalid backup file: not a valid tar archive")

        # Extract the backup
        with tarfile.open(backup_file, "r:gz") as tar:
            # Verify the archive contains .gira directory
            members = tar.getnames()
            if not any(m.startswith(".gira") for m in members):
                raise ValueError("Invalid backup file: no .gira directory found")

            # Remove existing .gira directory if it exists
            if gira_target.exists():
                import shutil
                shutil.rmtree(gira_target)

            # Extract to target directory
            tar.extractall(target_dir)

        # Verify restoration
        if not gira_target.exists():
            raise ValueError("Restoration failed: .gira directory not created")

        # Load and display project info
        config_file = gira_target / "config.json"
        if config_file.exists():
            import json
            with open(config_file) as f:
                config = json.load(f)
                project_name = config.get("name", "Unknown")
                prefix = config.get("ticket_id_prefix", "N/A")
        else:
            project_name = "Unknown"
            prefix = "N/A"

        console.print(f"✅ Project restored successfully!", style="bold green")
        console.print(f"   📁 Location: [cyan]{target_dir}[/cyan]")
        console.print(f"   📋 Project: {project_name}")
        console.print(f"   🏷️  Prefix: {prefix}")

    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to restore backup: {e}")
        raise typer.Exit(1)
