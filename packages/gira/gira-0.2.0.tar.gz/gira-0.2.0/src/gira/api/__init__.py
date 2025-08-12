"""Gira API foundation for web and TUI interfaces."""

from gira.api.bulk.manager import BulkOperationManager
from gira.api.bulk.tracker import OperationTracker
from gira.api.bulk.validation import ValidationEngine
from gira.api.bulk.response import ResponseFormatter
from gira.api.bulk.errors import ErrorHandler, APIError

__all__ = [
    "BulkOperationManager",
    "OperationTracker", 
    "ValidationEngine",
    "ResponseFormatter",
    "ErrorHandler",
    "APIError",
]