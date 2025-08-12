"""Webhook management commands for Gira."""

import typer
from gira.cli.commands.webhook.add import add
from gira.cli.commands.webhook.remove import remove
from gira.cli.commands.webhook.list import list_webhooks
from gira.cli.commands.webhook.test import test
from gira.cli.commands.webhook.enable import enable, disable
from gira.cli.commands.webhook.filter import filter_help, validate
from gira.cli.commands.webhook.health import health, stats

app = typer.Typer(
    name="webhook",
    help="Manage HTTP webhooks for external integrations",
    rich_markup_mode="rich"
)

# Create filter subcommand group
filter_app = typer.Typer(help="Webhook filter management")
filter_app.command("help")(filter_help)
filter_app.command("validate")(validate)

# Register commands
app.command("add")(add)
app.command("remove")(remove)
app.command("list")(list_webhooks)
app.command("test")(test)
app.command("enable")(enable)
app.command("disable")(disable)
app.command("health")(health)
app.command("stats")(stats)
app.add_typer(filter_app, name="filter")