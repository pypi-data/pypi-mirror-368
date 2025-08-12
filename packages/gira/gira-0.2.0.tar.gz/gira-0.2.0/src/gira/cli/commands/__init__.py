"""Command modules for Gira."""

from gira.cli.commands.archive import (
    archive_done,
    archive_old,
    archive_ticket,
    list_archived,
    restore,
    suggest,
)
from gira.cli.commands.board import board
from gira.cli.commands.comment import add, delete, list_comments
from gira.cli.commands.completion import install_completion, show_completion
from gira.cli.commands.config import config_get, config_set, config_reset
from gira.cli.commands.context import context
from gira.cli.commands.describe import create_describe_command
from gira.cli.commands.epic import create, delete, list_epics, show, update
from gira.cli.commands.graph import graph_command
from gira.cli.commands.init import init
from gira.cli.commands.query import execute_query_command as query
from gira.cli.commands.sprint import close, create, delete, list_sprints, show, start, update
from gira.cli.commands.sync import sync
from gira.cli.commands.team import team_app
from gira.cli.commands.ticket import (
    add_dep,
    delete,
    deps,
    move,
    order,
    remove_dep,
    show,
    tree,
    update,
)
from gira.cli.commands.ticket.list import list_tickets

__all__ = [
    "archive_done",
    "archive_old",
    "archive_ticket",
    "list_archived",
    "restore",
    "suggest",
    "add",
    "delete",
    "list_epics",
    "install_completion",
    "show_completion",
    "config_get",
    "config_set",
    "config_reset",
    "context",
    "create",
    "delete",
    "list_epics",
    "show",
    "update",
    "graph_command",
    "init",
    "query",
    "close",
    "create",
    "delete",
    "list_sprints",
    "show",
    "start",
    "update",
    "sync",
    "team_app",
    "add_dep",
    "delete",
    "deps",
    "list_tickets",
    "move",
    "order",
    "remove_dep",
    "show",
    "tree",
    "update",
    "board",
    "create_describe_command",
]
