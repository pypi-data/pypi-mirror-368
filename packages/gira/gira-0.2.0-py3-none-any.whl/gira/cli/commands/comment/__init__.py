"""Comment commands."""

from gira.cli.commands.comment.add import add
from gira.cli.commands.comment.list import list_comments
from gira.cli.commands.comment.attach import attach
from gira.cli.commands.comment.detach import detach
from gira.cli.commands.comment.download import download

# Import the inline delete function and explicitly assign it to 'delete'
# This ensures that 'delete' in this namespace refers to the function,
# not the standalone delete.py module that might be loaded elsewhere
from gira.cli.commands.comment.delete_inline import delete as _delete_func
delete = _delete_func

__all__ = ["add", "list_comments", "delete", "attach", "detach", "download"]
