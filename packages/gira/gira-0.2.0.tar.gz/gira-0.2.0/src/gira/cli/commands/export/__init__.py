"""Export command group for Gira data export functionality."""

import typer

from gira.cli.commands.export.csv import csv_export
from gira.cli.commands.export.json import json_export
from gira.cli.commands.export.markdown import markdown_export

app = typer.Typer(
    name="export",
    help="Export Gira data to various formats",
    no_args_is_help=True,
)

# Register subcommands
app.command(name="json", help="Export tickets to JSON format")(json_export)
app.command(name="csv", help="Export tickets to CSV format")(csv_export)
app.command(name="md", help="Export tickets to Markdown format")(markdown_export)
