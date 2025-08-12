"""Attachment management commands for Gira."""

from gira.cli.commands.attachment.add import add
from gira.cli.commands.attachment.cat import cat_attachment
from gira.cli.commands.attachment.download import download_attachment
from gira.cli.commands.attachment.list import list_attachments
from gira.cli.commands.attachment.open import open_attachment
from gira.cli.commands.attachment.remove import remove_attachment

__all__ = ["add", "cat_attachment", "download_attachment", "list_attachments", "open_attachment", "remove_attachment"]