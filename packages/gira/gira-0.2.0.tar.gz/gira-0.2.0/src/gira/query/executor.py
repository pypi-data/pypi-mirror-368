"""Query executor for evaluating parsed AST against Gira data models."""

import operator
import re
from datetime import datetime, timedelta, timezone
from enum import Enum
from functools import reduce
from typing import Any, Callable, Dict, List, Optional, Set, Union

from gira.models.comment import Comment
from gira.models.epic import Epic
from gira.models.sprint import Sprint
from gira.models.ticket import Ticket
from gira.query.ast import (
    AndExpression,
    ASTVisitor,
    BooleanValue,
    DateValue,
    Expression,
    FieldExpression,
    FunctionCall,
    GroupedExpression,
    ListValue,
    NotExpression,
    NullValue,
    NumericValue,
    OrExpression,
    RangeValue,
    StringValue,
    TextSearchExpression,
    Value,
)


class EntityType(Enum):
    """Entity types that can be queried."""

    TICKET = "ticket"
    EPIC = "epic"
    SPRINT = "sprint"
    COMMENT = "comment"


class QueryExecutor(ASTVisitor):
    """Executes queries by evaluating AST against data models."""

    def __init__(self, entity_type: EntityType):
        """Initialize the query executor.

        Args:
            entity_type: The type of entity to query
        """
        self.entity_type = entity_type
        self._current_entity: Optional[Union[Ticket, Epic, Sprint, Comment]] = None
        self._user_email: Optional[str] = None

    def execute(
        self,
        expression: Expression,
        entities: List[Union[Ticket, Epic, Sprint, Comment]],
        user_email: Optional[str] = None,
    ) -> List[Union[Ticket, Epic, Sprint, Comment]]:
        """Execute a query expression against a list of entities.

        Args:
            expression: The parsed query expression
            entities: List of entities to filter
            user_email: Current user's email for me() function

        Returns:
            List of entities matching the query
        """
        self._user_email = user_email
        results = []

        for entity in entities:
            self._current_entity = entity
            if expression.accept(self):
                results.append(entity)

        return results

    def visit_field_expression(self, expr: FieldExpression) -> bool:
        """Evaluate a field expression."""
        field_value = self._get_field_value(expr.field)
        
        # Special handling for function calls that act as operators
        if isinstance(expr.value, FunctionCall) and expr.value.name == "in_range":
            if len(expr.value.arguments) == 2:
                start = self._evaluate_value(expr.value.arguments[0])
                end = self._evaluate_value(expr.value.arguments[1])
                return self._in_range(field_value, start, end)
        
        expected_value = self._evaluate_value(expr.value)
        return self._compare_values(field_value, expr.operator, expected_value)

    def visit_and_expression(self, expr: AndExpression) -> bool:
        """Evaluate an AND expression."""
        return expr.left.accept(self) and expr.right.accept(self)

    def visit_or_expression(self, expr: OrExpression) -> bool:
        """Evaluate an OR expression."""
        return expr.left.accept(self) or expr.right.accept(self)

    def visit_not_expression(self, expr: NotExpression) -> bool:
        """Evaluate a NOT expression."""
        return not expr.expression.accept(self)

    def visit_grouped_expression(self, expr: GroupedExpression) -> bool:
        """Evaluate a grouped expression."""
        return expr.expression.accept(self)

    def visit_text_search_expression(self, expr: TextSearchExpression) -> bool:
        """Evaluate a text search expression."""
        query = expr.text.lower()
        
        # Get searchable fields based on entity type
        searchable_fields = self._get_searchable_fields()
        
        for field in searchable_fields:
            value = self._get_field_value(field)
            if value is not None:
                if isinstance(value, str) and query in value.lower():
                    return True
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and query in item.lower():
                            return True
        
        return False

    def _get_field_value(self, field: str) -> Any:
        """Get the value of a field from the current entity."""
        if not self._current_entity:
            return None

        # Handle nested fields
        parts = field.split(".")
        value = self._current_entity

        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            elif isinstance(value, dict) and part in value:
                value = value[part]
            elif isinstance(value, list) and parts.index(part) == 0:
                # Handle list fields like comments.author
                if part == "comments" and hasattr(self._current_entity, "comment_ids"):
                    # For tickets/epics with comment references
                    return getattr(self._current_entity, "comment_ids", [])
                return value
            else:
                return None

        return value

    def _evaluate_value(self, value: Value) -> Any:
        """Evaluate a value node to its Python representation."""
        if isinstance(value, StringValue):
            return value.value
        elif isinstance(value, NumericValue):
            return value.value
        elif isinstance(value, BooleanValue):
            return value.value
        elif isinstance(value, DateValue):
            return self.visit_date_value(value)
        elif isinstance(value, ListValue):
            return [self._evaluate_value(v) for v in value.values]
        elif isinstance(value, RangeValue):
            return (self._evaluate_value(value.start), self._evaluate_value(value.end))
        elif isinstance(value, NullValue):
            return None
        elif isinstance(value, FunctionCall):
            return self._evaluate_function(value)
        else:
            return value

    def _resolve_date(self, date_input: Union[str, datetime]) -> datetime:
        """Resolve a date string or datetime to a datetime object.
        
        Args:
            date_input: A datetime object or date string to resolve
            
        Returns:
            Resolved datetime object
            
        Raises:
            ValueError: If the date string cannot be parsed
        """
        if isinstance(date_input, datetime):
            return date_input

        # Handle relative dates
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        relative_dates = {
            "today": today,
            "yesterday": today - timedelta(days=1),
            "tomorrow": today + timedelta(days=1),
            "this_week": today - timedelta(days=today.weekday()),
            "last_week": today - timedelta(days=today.weekday() + 7),
            "next_week": today - timedelta(days=today.weekday() - 7),
            "this_month": today.replace(day=1),
            "last_month": (today.replace(day=1) - timedelta(days=1)).replace(day=1),
            "next_month": (today.replace(day=28) + timedelta(days=4)).replace(day=1),
        }

        if date_input.lower() in relative_dates:
            return relative_dates[date_input.lower()]

        # Try to parse as ISO date
        try:
            return datetime.fromisoformat(date_input.replace("Z", "+00:00"))
        except ValueError as e:
            raise ValueError(f"Unable to parse date string: '{date_input}'") from e

    def _evaluate_function(self, func: FunctionCall) -> Any:
        """Evaluate a function call."""
        if func.name == "me":
            return self._user_email or "unknown@example.com"
        
        elif func.name == "now":
            return datetime.now(timezone.utc)
        
        elif func.name == "today":
            return datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        elif func.name == "days_ago":
            if func.arguments and isinstance(func.arguments[0], NumericValue):
                days = int(func.arguments[0].value)
                return datetime.now(timezone.utc) - timedelta(days=days)
            return datetime.now(timezone.utc)
        
        elif func.name == "hours_ago":
            if func.arguments and isinstance(func.arguments[0], NumericValue):
                hours = int(func.arguments[0].value)
                return datetime.now(timezone.utc) - timedelta(hours=hours)
            return datetime.now(timezone.utc)
        
        elif func.name == "days_from_now":
            if func.arguments and isinstance(func.arguments[0], NumericValue):
                days = int(func.arguments[0].value)
                return datetime.now(timezone.utc) + timedelta(days=days)
            return datetime.now(timezone.utc)
        
        elif func.name in ["count", "len"]:
            if func.arguments and isinstance(func.arguments[0], StringValue):
                field_name = func.arguments[0].value
                field_value = self._get_field_value(field_name)
                if isinstance(field_value, (list, str)):
                    return len(field_value)
                return 0
            return 0
        
        elif func.name in ["upper", "lower"]:
            if func.arguments and isinstance(func.arguments[0], StringValue):
                field_name = func.arguments[0].value
                field_value = self._get_field_value(field_name)
                if isinstance(field_value, str):
                    return getattr(field_value, func.name)()
                return ""
            return ""
        
        # Unknown function - return None
        return None

    def _check_contains(self, field_value: Any, expected_value: Any, negate: bool = False) -> bool:
        """Check if field value contains expected value.
        
        Args:
            field_value: The field value to check
            expected_value: The value to look for
            negate: If True, check for not contains
            
        Returns:
            True if contains check passes (or not contains if negated)
        """
        # If expected_value is a list (from contains(item)), extract the first item
        if isinstance(expected_value, list) and len(expected_value) == 1:
            expected_value = expected_value[0]
        
        if isinstance(field_value, list):
            result = expected_value in field_value
        elif isinstance(field_value, str) and isinstance(expected_value, str):
            result = expected_value.lower() in field_value.lower()
        else:
            result = False
        
        return not result if negate else result

    def _compare_values(self, field_value: Any, op: str, expected_value: Any) -> bool:
        """Compare field value with expected value using the given operator."""
        # Handle null checks
        if op == "is_null":
            return field_value is None
        elif op == "is_not_null":
            return field_value is not None

        # Handle IN operator
        if op == "in":
            if isinstance(expected_value, list):
                return field_value in expected_value
            return False
        elif op == "not_in":
            if isinstance(expected_value, list):
                return field_value not in expected_value
            return True

        # Handle CONTAINS operator
        if op == "contains":
            return self._check_contains(field_value, expected_value, negate=False)
        elif op == "not_contains":
            return self._check_contains(field_value, expected_value, negate=True)

        # Handle fuzzy matching
        if op == "~":
            return self._fuzzy_match(field_value, expected_value)
        elif op == "!~":
            return not self._fuzzy_match(field_value, expected_value)

        # Handle range operator
        if op == "in_range" and isinstance(expected_value, tuple) and len(expected_value) == 2:
            start, end = expected_value
            return self._in_range(field_value, start, end)

        # Handle comparison operators
        comparison_ops = {
            ":": operator.eq,  # Colon is the default equality operator
            "=": operator.eq,
            "==": operator.eq,
            "!=": operator.ne,
            "<": operator.lt,
            "<=": operator.le,
            ">": operator.gt,
            ">=": operator.ge,
        }

        if op in comparison_ops:
            # Convert strings to lowercase for case-insensitive comparison
            if isinstance(field_value, str) and isinstance(expected_value, str):
                field_value = field_value.lower()
                expected_value = expected_value.lower()
            
            # Handle date comparisons
            if isinstance(expected_value, datetime):
                if isinstance(field_value, str):
                    try:
                        field_value = datetime.fromisoformat(field_value.replace("Z", "+00:00"))
                    except ValueError:
                        return False
            
            try:
                return comparison_ops[op](field_value, expected_value)
            except TypeError:
                # Type mismatch - values can't be compared
                return False

        # Unknown operator
        return False

    def _fuzzy_match(self, field_value: Any, pattern: Any) -> bool:
        """Perform fuzzy matching using wildcards.
        
        Args:
            field_value: The field value to match against
            pattern: The pattern with wildcards (* and ?)
            
        Returns:
            True if the field value matches the pattern
        """
        if not isinstance(field_value, str) or not isinstance(pattern, str):
            return False

        # Escape special regex characters except for wildcards
        # Use re.escape but preserve wildcards
        import re as regex_module
        
        # Temporarily replace wildcards with placeholders
        placeholder_star = '\x00STAR\x00'
        placeholder_question = '\x00QUESTION\x00'
        
        escaped_pattern = pattern.replace('*', placeholder_star).replace('?', placeholder_question)
        
        # Escape all special regex characters
        escaped_pattern = regex_module.escape(escaped_pattern)
        
        # Restore wildcards
        escaped_pattern = escaped_pattern.replace(placeholder_star, '*').replace(placeholder_question, '?')
        
        # Convert wildcards to regex after escaping
        regex_pattern = escaped_pattern.replace("*", ".*").replace("?", ".")
        regex_pattern = f"^{regex_pattern}$"

        try:
            return bool(re.match(regex_pattern, field_value, re.IGNORECASE))
        except re.error:
            return False

    def _in_range(self, value: Any, start: Any, end: Any) -> bool:
        """Check if value is in range [start, end]."""
        try:
            return start <= value <= end
        except TypeError:
            return False

    def visit_string_value(self, value: StringValue) -> str:
        """Visit a string value."""
        return value.value

    def visit_numeric_value(self, value: NumericValue) -> Union[int, float]:
        """Visit a numeric value."""
        return value.value

    def visit_boolean_value(self, value: BooleanValue) -> bool:
        """Visit a boolean value."""
        return value.value

    def visit_date_value(self, value: DateValue) -> datetime:
        """Visit a date value."""
        # If it has a relative keyword, resolve that instead of the stored value
        if hasattr(value, 'relative_keyword') and value.relative_keyword:
            return self._resolve_date(value.relative_keyword)
        return self._resolve_date(value.value)

    def visit_list_value(self, value: ListValue) -> List[Any]:
        """Visit a list value."""
        return [self._evaluate_value(v) for v in value.values]

    def visit_range_value(self, value: RangeValue) -> tuple:
        """Visit a range value."""
        return (self._evaluate_value(value.start), self._evaluate_value(value.end))

    def visit_null_value(self, value: NullValue) -> None:
        """Visit a null value."""
        return None

    def visit_function_call(self, value: FunctionCall) -> Any:
        """Visit a function call."""
        return self._evaluate_function(value)

    def _get_searchable_fields(self) -> List[str]:
        """Get list of searchable fields for the current entity type."""
        searchable_by_type = {
            EntityType.TICKET: ["title", "description", "id", "labels", "assignee", "reporter"],
            EntityType.EPIC: ["title", "description", "id", "owner"],
            EntityType.SPRINT: ["name", "goal", "id"],
            EntityType.COMMENT: ["content", "author"],
        }
        
        return searchable_by_type.get(self.entity_type, [])