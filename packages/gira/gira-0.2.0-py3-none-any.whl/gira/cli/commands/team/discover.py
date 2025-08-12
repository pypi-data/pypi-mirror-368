"""Discover team members from Git history."""

import subprocess
from typing import Dict

import typer
from gira.utils.console import console
from rich.prompt import Confirm
from rich.table import Table

from gira.models.team import TeamMember
from gira.utils.team_utils import create_default_team, load_team, save_team

def discover_members(
    limit: int = typer.Option(50, "-l", "--limit", help="Maximum number of commits to analyze"),
    add_all: bool = typer.Option(False, "--add-all", help="Add all discovered members without prompting"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be added without making changes"),
) -> None:
    """Discover team members from Git commit history."""
    try:
        # Load existing team
        team = load_team() or create_default_team()
        existing_emails = {m.email.lower() for m in team.members}

        # Get unique authors from git log
        console.print(f"[dim]Analyzing last {limit} commits...[/dim]")

        result = subprocess.run(
            ["git", "log", f"-{limit}", "--pretty=format:%an|%ae"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            console.print("[red]Error:[/red] Failed to read Git history. Make sure you're in a Git repository.")
            raise typer.Exit(1)

        # Parse unique authors
        discovered: Dict[str, Dict[str, any]] = {}
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                name, email = line.split("|", 1)
                email = email.strip().lower()
                name = name.strip()

                if email and email not in existing_emails:
                    if email not in discovered:
                        discovered[email] = {
                            "name": name,
                            "names": {name},
                            "count": 0
                        }
                    else:
                        discovered[email]["names"].add(name)
                    discovered[email]["count"] += 1

        if not discovered:
            console.print("[yellow]No new team members found in Git history.[/yellow]")
            console.print(f"[dim]Current team has {len(team.members)} members.[/dim]")
            return

        # Sort by commit count
        sorted_discovered = sorted(
            discovered.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )

        # Show discovered members
        console.print(f"\n[bold]Discovered {len(discovered)} potential team members:[/bold]")

        table = Table()
        table.add_column("Email", style="cyan")
        table.add_column("Name(s)", style="white")
        table.add_column("Commits", style="yellow")
        table.add_column("Status", style="dim")

        for email, info in sorted_discovered:
            names = ", ".join(sorted(info["names"]))
            table.add_row(
                email,
                names,
                str(info["count"]),
                "[green]New[/green]"
            )

        console.print(table)

        if dry_run:
            console.print("\n[yellow]Dry run mode - no changes made.[/yellow]")
            return

        # Process additions
        added_count = 0

        if add_all:
            # Add all discovered members
            for email, info in sorted_discovered:
                try:
                    # Use the most common name (first in sorted set)
                    name = sorted(info["names"])[0]
                    member = TeamMember(
                        email=email,
                        name=name,
                        role="developer"
                    )
                    team.add_member(member)
                    added_count += 1
                except Exception as e:
                    console.print(f"[yellow]Warning:[/yellow] Could not add {email}: {e}")
        else:
            # Interactive mode
            console.print("\n[dim]Review each member (y/n/q to quit):[/dim]")

            for email, info in sorted_discovered:
                names = sorted(info["names"])
                name = names[0]

                # Show member details
                console.print(f"\nEmail: [cyan]{email}[/cyan]")
                console.print(f"Name: {name}")
                if len(names) > 1:
                    console.print(f"[dim]Also seen as: {', '.join(names[1:])}[/dim]")
                console.print(f"Commits: [yellow]{info['count']}[/yellow]")

                # Ask for confirmation
                response = Confirm.ask("Add this member?", default=True)
                if response is None:  # User pressed 'q' to quit
                    break
                elif response:
                    try:
                        member = TeamMember(
                            email=email,
                            name=name,
                            role="developer"
                        )
                        team.add_member(member)
                        added_count += 1
                        console.print("[green]✓[/green] Added")
                    except Exception as e:
                        console.print(f"[red]Error:[/red] {e}")
                else:
                    console.print("[dim]Skipped[/dim]")

        # Save if any members were added
        if added_count > 0:
            save_team(team)
            console.print(f"\n[green]✓[/green] Added {added_count} new team member(s)")
            console.print(f"[dim]Total team size: {len(team.members)} members[/dim]")
        else:
            console.print("\n[yellow]No team members were added.[/yellow]")

    except Exception as e:
        console.print(f"[red]Error discovering team members: {e}[/red]")
        raise typer.Exit(1)
