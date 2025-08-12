"""Main CLI interface for Gira."""

from typing import Optional
import typer
from gira.utils.console import console
from gira import __version__
from gira.cli.commands.board import board as board_command_function
from gira.cli.commands.backlog import backlog as backlog_command_function
from gira.cli.commands import config as config_commands
from gira.cli.commands.init import init as init_command_function
from gira.cli.commands.archive import (
    archive_done,
    archive_old,
    archive_ticket,
    list_archived,
    restore,
    suggest,
)
from gira.cli.commands.backup import backup, restore as restore_backup
from gira.cli.commands.cache import clear as cache_clear, status as cache_status
from gira.cli.commands.comment import (
    add as comment_add,
    list_comments as comment_list,
    attach as comment_attach,
    detach as comment_detach,
    download as comment_download
)
# Import delete function explicitly to avoid module name conflicts
from gira.cli.commands.comment.delete_inline import delete as comment_delete
from gira.cli.commands.completion import install_completion, show_completion
from gira.cli.commands.docs import generate as docs_generate
from gira.cli.commands.epic import create as epic_create
from gira.cli.commands.export import app as export_app
from gira.cli.commands.epic import delete as epic_delete
from gira.cli.commands.epic import list as epic_list
from gira.cli.commands.epic import show as epic_show
from gira.cli.commands.epic import update as epic_update
from gira.cli.commands.query import query_app
from gira.cli.commands.query_save import query_save
from gira.cli.commands.query_list import query_list
from gira.cli.commands.query_run import query_run
from gira.cli.commands.sprint import close as sprint_close
from gira.cli.commands.sprint import complete as sprint_complete
from gira.cli.commands.sprint import create as sprint_create
from gira.cli.commands.sprint import delete as sprint_delete
from gira.cli.commands.sprint import list_sprints as sprint_list
from gira.cli.commands.sprint import show as sprint_show
from gira.cli.commands.sprint import start as sprint_start
from gira.cli.commands.sprint import update as sprint_update
from gira.cli.commands.sprint import assign_by_dates, assign_by_epic, assign_wizard, assign, unassign, generate_historical
from gira.cli.commands.sync import sync
from gira.cli.commands.team import team_app
from gira.cli.commands.storage import configure as storage_configure
from gira.cli.commands.storage import status as storage_status
from gira.cli.commands.storage import validate as storage_validate
from gira.cli.commands.attachment import add as attachment_add
from gira.cli.commands.attachment import cat_attachment as attachment_cat_attachment
from gira.cli.commands.metrics import velocity as metrics_velocity, trends as metrics_trends, duration as metrics_duration, overview as metrics_overview
from gira.cli.commands.attachment import download_attachment as attachment_download_attachment
from gira.cli.commands.attachment import list_attachments as attachment_list_attachments
from gira.cli.commands.attachment import open_attachment as attachment_open_attachment
from gira.cli.commands.attachment import remove_attachment as attachment_remove_attachment
from gira.cli.commands.ticket import (
    add_dep,
    blame,
    bulk_update,
    commits,
    create,
    delete,
    deps,
    move,
    order,
    remove_dep,
    show,
    tree,
    update,
)
from gira.cli.commands.ticket.bulk_add_deps import bulk_add_deps
from gira.cli.commands.ticket.bulk_remove_deps import bulk_remove_deps
from gira.cli.commands.ticket.clear_deps import clear_deps
from gira.cli.commands.ticket.list import list_tickets
from gira.cli.commands.ticket import edit, ls, mv, rm
from gira.cli.commands.ticket.estimate import estimate_app
from gira.cli.commands.context import context, context_app
from gira.cli.commands.workflow import workflow, workflow_app
from gira.cli.commands.graph import graph_command
from gira.cli.commands.migrate.hybrid import hybrid as migrate_hybrid
from gira.cli.commands.describe import create_describe_command
from gira.cli.commands.hooks import install as hooks_install
from gira.cli.commands.hooks import uninstall as hooks_uninstall
from gira.cli.commands.hooks import status as hooks_status
from gira.cli.commands.extensibility_hooks import app as extensibility_hooks_app
from gira.cli.commands.webhook import app as webhook_app
from gira.cli.commands.operation import app as operation_app
from gira.cli.commands.ai import ai_app
from gira.utils.error_codes import enable_json_errors
from gira.utils.output import OutputFormat, add_format_option

# Initialize Typer app with command suggestions
from gira.utils.command_suggestions import create_typer_with_suggestions

app = create_typer_with_suggestions(
    name="gira",
    help="Git-based project management for developers and AI agents",
    add_completion=True,
    rich_markup_mode="markdown",
    pretty_exceptions_show_locals=False,
    no_args_is_help=True, # This ensures help is shown if no command is given
)

# Initialize Rich console
def _version_callback(value: bool) -> None:
    if value:
        console.print(f"gira version {__version__}")
        raise typer.Exit()


# Sub-command groups with command suggestions
ticket_app = create_typer_with_suggestions(help="Manage tickets")
epic_app = create_typer_with_suggestions(help="Manage epics")
sprint_app = create_typer_with_suggestions(help="Manage sprints")
comment_app = create_typer_with_suggestions(help="Manage comments")
config_app = create_typer_with_suggestions(help="Configuration management")
metrics_app = create_typer_with_suggestions(help="Project metrics and analytics")
completion_app = create_typer_with_suggestions(help="Shell completion management")
archive_app = create_typer_with_suggestions(help="Archive management")
migrate_app = create_typer_with_suggestions(help="Migrate project structure")
docs_app = create_typer_with_suggestions(help="Documentation generation")
hooks_app = create_typer_with_suggestions(help="Git hooks management")
extensibility_app = create_typer_with_suggestions(help="Extensibility hooks management")
webhook_app_cli = create_typer_with_suggestions(help="HTTP webhook management")
cache_app = create_typer_with_suggestions(help="Cache management")
storage_app = create_typer_with_suggestions(help="Storage backend management")
attachment_app = create_typer_with_suggestions(help="Attachment management")

# Add sub-commands to main app
app.add_typer(ticket_app, name="ticket")
app.add_typer(epic_app, name="epic")
app.add_typer(sprint_app, name="sprint")
app.add_typer(comment_app, name="comment")
app.add_typer(config_app, name="config")
app.add_typer(metrics_app, name="metrics")
app.add_typer(completion_app, name="completion")
app.add_typer(archive_app, name="archive")
app.add_typer(migrate_app, name="migrate")
app.add_typer(team_app, name="team")
app.add_typer(docs_app, name="docs")
app.add_typer(export_app, name="export")
app.add_typer(hooks_app, name="hooks")
app.add_typer(extensibility_hooks_app, name="ext")
app.add_typer(webhook_app, name="webhook")
app.add_typer(cache_app, name="cache")
app.add_typer(storage_app, name="storage")
app.add_typer(attachment_app, name="attachment")
app.add_typer(operation_app, name="operation")
app.add_typer(ai_app, name="ai")


# Register commands
app.command()(init_command_function)
app.command()(board_command_function)
app.command()(backlog_command_function)
# Custom query command handler that supports both direct queries and subcommands
@app.command("query", context_settings={"allow_extra_args": True, "allow_interspersed_args": True})
def query_command(
    ctx: typer.Context,
    entity: str = typer.Option("ticket", "--entity", "-e", help="Type of entity to search"),
    output_format: str = typer.Option("table", "--format", "-f", help="Output format"),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Maximum number of results to return"),
    offset: int = typer.Option(0, "--offset", "-o", help="Number of results to skip"),
    sort: Optional[str] = typer.Option(None, "--sort", "-s", help="Sort results by field"),
    filter_json: Optional[str] = typer.Option(None, "--filter-json", help="JSONPath expression to filter JSON output"),
    no_header: bool = typer.Option(False, "--no-header", help="Don't show table header"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed error messages"),
    save: Optional[str] = typer.Option(None, "--save", help="Save query with given name"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Description for saved query"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing saved query"),
    color: bool = typer.Option(True, "--color/--no-color", help="Enable/disable colored output"),
):
    """Execute queries and manage saved queries."""
    from gira.cli.commands.query import execute_query_command, list_saved_queries, show_saved_query, delete_saved_query, edit_saved_query
    from gira.utils.output import OutputFormat
    
    # Get the first argument as potential query string or subcommand
    if not ctx.args:
        # No arguments, show help
        console.print(ctx.get_help())
        raise typer.Exit()
    
    first_arg = ctx.args[0]
    
    # Check if it's a known subcommand
    if first_arg == "list":
        # Handle list subcommand
        entity_filter = ctx.args[1] if len(ctx.args) > 1 and ctx.args[1] in ["ticket", "epic", "sprint", "comment"] else None
        list_saved_queries(entity=entity_filter, verbose=verbose, output_format=OutputFormat(output_format.lower()), color=color, no_color=not color)
    elif first_arg == "show":
        if len(ctx.args) < 2:
            console.print("[red]Error:[/red] 'show' requires a query name")
            raise typer.Exit(1)
        show_saved_query(name=ctx.args[1], output_format=OutputFormat(output_format.lower()), color=color, no_color=not color)
    elif first_arg == "delete":
        if len(ctx.args) < 2:
            console.print("[red]Error:[/red] 'delete' requires a query name")
            raise typer.Exit(1)
        delete_saved_query(name=ctx.args[1], force=force)
    elif first_arg == "edit": 
        if len(ctx.args) < 2:
            console.print("[red]Error:[/red] 'edit' requires a query name")
            raise typer.Exit(1)
        edit_saved_query(name=ctx.args[1])
    else:
        # Treat it as a query string
        execute_query_command(
            query_string=first_arg,
            entity=entity,
            output_format=OutputFormat(output_format.lower()),
            limit=limit,
            offset=offset,
            sort=sort,
            filter_json=filter_json,
            no_header=no_header,
            verbose=verbose,
            save=save,
            description=description,
            force=force,
            color=color,
            no_color=not color,
        )

# Legacy commands with deprecation warnings
@app.command("query-save", deprecated=True)
def deprecated_query_save(
    name: str = typer.Argument(..., help="Name for the saved query"),
    query_string: str = typer.Argument(..., help="Query expression to save"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Description of what the query returns"),
    entity_type: str = typer.Option("ticket", "--entity", "-e", help="Entity type the query targets"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing query with the same name"),
) -> None:
    """Save a query expression for later reuse (DEPRECATED)."""
    console.print("[yellow]Warning:[/yellow] 'gira query-save' is deprecated. Use 'gira query exec \"<expression>\" --save <name>' instead.")
    return query_save(name, query_string, description, entity_type, force)

@app.command("query-list", deprecated=True) 
def deprecated_query_list(
    entity: Optional[str] = typer.Option(None, "--entity", "-e", help="Filter by entity type"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
    output_format: OutputFormat = add_format_option()
) -> None:
    """List all saved queries (DEPRECATED)."""
    console.print("[yellow]Warning:[/yellow] 'gira query-list' is deprecated. Use 'gira query list' instead.")
    return query_list(entity, verbose, output_format)

@app.command("query-run", deprecated=True)
def deprecated_query_run(
    name: str = typer.Argument(..., help="Name of the saved query to run"),
    output_format: OutputFormat = add_format_option(),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Maximum number of results"),
    offset: int = typer.Option(0, "--offset", "-o", help="Number of results to skip"),
    sort: Optional[str] = typer.Option(None, "--sort", "-s", help="Sort results by field"),
    filter_json: Optional[str] = typer.Option(None, "--filter-json", help="JSONPath expression"),
    no_header: bool = typer.Option(False, "--no-header", help="Don't show table header"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed error messages"),
) -> None:
    """Run a saved query by name (DEPRECATED)."""
    console.print("[yellow]Warning:[/yellow] 'gira query-run' is deprecated. Use 'gira query exec @<name>' instead.")
    return query_run(name, output_format, limit, offset, sort, filter_json, no_header, verbose)

# Add context as a Typer app for subcommands
app.add_typer(context_app, name="context")
# Add workflow as a Typer app for subcommands
app.add_typer(workflow_app, name="workflow")
app.command("graph")(graph_command)
app.command("describe")(create_describe_command(app))
app.command()(backup)
app.command("restore")(restore_backup)
app.command()(sync)

# Add convenient ai-help alias at top level
@app.command("ai-help")
def ai_help_alias(
    agent: Optional[str] = typer.Argument(None, help="Specific AI agent (claude, gemini, etc.)")
) -> None:
    """Show AI-optimized command examples and patterns."""
    from gira.cli.commands.ai import ai_help
    ai_help(agent)


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
        expose_value=False,
    ),
    json_errors: bool = typer.Option(
        False,
        "--json-errors",
        help="Output errors in JSON format to stderr",
        envvar="GIRA_JSON_ERRORS",
    )
):
    """
    Gira - Git-based project management for developers and AI agents.
    
    Use --json-errors to get machine-readable error output.
    """
    if json_errors:
        enable_json_errors()


# Sync command
app.command("sync")(sync)


# Ticket subcommands
ticket_app.command("create")(create.create)
ticket_app.command("list")(list_tickets)
ticket_app.command("show")(show.show)
ticket_app.command("update")(update.update)
ticket_app.command("move")(move.move)
ticket_app.command("tree")(tree.tree)
ticket_app.command("add-dep")(add_dep.add_dep)
ticket_app.command("remove-dep")(remove_dep.remove_dep)
ticket_app.command("deps")(deps.deps)
ticket_app.command("order")(order.order)
ticket_app.command("delete")(delete.delete)
ticket_app.command("bulk-update")(bulk_update.bulk_update)
ticket_app.command("bulk-add-deps")(bulk_add_deps)
ticket_app.command("bulk-remove-deps")(bulk_remove_deps)
ticket_app.command("clear-deps")(clear_deps)
ticket_app.command("commits")(commits.commits)
ticket_app.command("blame")(blame.blame)

# Add estimate sub-app for story point estimation
ticket_app.add_typer(estimate_app, name="estimate")

# Add aliases for better usability
ticket_app.command("edit")(edit.edit)  # Alias for update
ticket_app.command("mv")(mv.mv)        # Alias for move
ticket_app.command("ls")(ls.ls)        # Alias for list
ticket_app.command("rm")(rm.rm)        # Alias for delete


# Epic subcommands
epic_app.command("create")(epic_create.create)
epic_app.command("list")(epic_list.list_epics)
epic_app.command("show")(epic_show.show)
epic_app.command("update")(epic_update.update)
epic_app.command("delete")(epic_delete.delete)


# Sprint subcommands
sprint_app.command("create")(sprint_create)
sprint_app.command("list")(sprint_list)
sprint_app.command("show")(sprint_show.show)
sprint_app.command("update")(sprint_update.update)
sprint_app.command("start")(sprint_start)
sprint_app.command("close")(sprint_close)
sprint_app.command("complete")(sprint_complete)
sprint_app.command("delete")(sprint_delete.delete)
sprint_app.command("assign")(assign)
sprint_app.command("unassign")(unassign)
sprint_app.command("assign-by-dates")(assign_by_dates)
sprint_app.command("assign-by-epic")(assign_by_epic)
sprint_app.command("assign-wizard")(assign_wizard)
sprint_app.command("generate-historical")(generate_historical)


# Metrics subcommands
@metrics_app.callback(invoke_without_command=True)
def metrics_callback(
    ctx: typer.Context,
    format: str = typer.Option("human", "--format", "-f", help="Output format: human, json"),
    days: int = typer.Option(30, "--days", "-d", help="Number of days to analyze for trends")
):
    """Display comprehensive metrics overview for the project."""
    if ctx.invoked_subcommand is None:
        # No subcommand was invoked, run overview
        metrics_overview(format=format, days=days)

metrics_app.command("overview")(metrics_overview)
metrics_app.command("velocity")(metrics_velocity)
metrics_app.command("trends")(metrics_trends)
metrics_app.command("duration")(metrics_duration)


# Comment subcommands
comment_app.command("add")(comment_add)
comment_app.command("list")(comment_list)
comment_app.command("delete")(comment_delete)
comment_app.command("attach")(comment_attach)
comment_app.command("detach")(comment_detach)
comment_app.command("download")(comment_download)


# Completion subcommands
completion_app.command("install")(install_completion)
completion_app.command("show")(show_completion)


# Config subcommands
config_app.command("set")(config_commands.config_set)
config_app.command("get")(config_commands.config_get)
config_app.command("reset")(config_commands.config_reset)
config_app.command("rename-prefix")(config_commands.config_rename_prefix)


# Archive subcommands
archive_app.command("ticket")(archive_ticket)
archive_app.command("done")(archive_done)
archive_app.command("old")(archive_old)
archive_app.command("list")(list_archived)
archive_app.command("restore")(restore)
archive_app.command("suggest")(suggest)


# Migrate subcommands
migrate_app.command("hybrid")(migrate_hybrid)


# Docs subcommands
docs_app.command("generate")(docs_generate.generate)


# Hooks subcommands
hooks_app.command("install")(hooks_install.install)
hooks_app.command("uninstall")(hooks_uninstall.uninstall)
hooks_app.command("status")(hooks_status.status)


# Cache subcommands
cache_app.command("clear")(cache_clear)
cache_app.command("status")(cache_status)


# Storage subcommands  
storage_app.command("configure")(storage_configure)
storage_app.command("status")(storage_status)
storage_app.command("validate")(storage_validate)


# Attachment subcommands
attachment_app.command("add")(attachment_add)
attachment_app.command("cat")(attachment_cat_attachment)
attachment_app.command("download")(attachment_download_attachment)
attachment_app.command("list")(attachment_list_attachments)
attachment_app.command("open")(attachment_open_attachment)
attachment_app.command("remove")(attachment_remove_attachment)


# Main entry point
if __name__ == "__main__":
    app()
