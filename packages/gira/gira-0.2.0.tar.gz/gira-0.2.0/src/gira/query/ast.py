"""Abstract Syntax Tree (AST) nodes for the Gira Query Language."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, List, Optional, Union


class ASTNode(ABC):
    """Base class for all AST nodes."""
    
    @abstractmethod
    def accept(self, visitor: 'ASTVisitor') -> Any:
        """Accept a visitor for the visitor pattern."""
        pass


class Expression(ASTNode):
    """Base class for all expressions."""
    pass


class Value(ASTNode):
    """Base class for all values."""
    pass


@dataclass
class StringValue(Value):
    """String value node."""
    value: str
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_string_value(self)


@dataclass
class NumericValue(Value):
    """Numeric value node (int or float)."""
    value: Union[int, float]
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_numeric_value(self)


@dataclass
class BooleanValue(Value):
    """Boolean value node."""
    value: bool
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_boolean_value(self)


@dataclass
class DateValue(Value):
    """Date/datetime value node."""
    value: Union[date, datetime]
    is_relative: bool = False
    relative_keyword: Optional[str] = None
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_date_value(self)


@dataclass
class ListValue(Value):
    """List value node."""
    values: List[Value]
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_list_value(self)


@dataclass
class RangeValue(Value):
    """Range value node (e.g., 1..10)."""
    start: NumericValue
    end: NumericValue
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_range_value(self)


@dataclass
class NullValue(Value):
    """Null value node."""
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_null_value(self)


@dataclass
class FunctionCall(Value):
    """Function call node."""
    name: str
    arguments: List[Value]
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_function_call(self)


@dataclass
class FieldExpression(Expression):
    """Field expression node (e.g., status:todo)."""
    field: str
    operator: str
    value: Optional[Value] = None
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_field_expression(self)


@dataclass
class TextSearchExpression(Expression):
    """Bare text search expression."""
    text: str
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_text_search_expression(self)


@dataclass
class AndExpression(Expression):
    """AND expression node."""
    left: Expression
    right: Expression
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_and_expression(self)


@dataclass
class OrExpression(Expression):
    """OR expression node."""
    left: Expression
    right: Expression
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_or_expression(self)


@dataclass
class NotExpression(Expression):
    """NOT expression node."""
    expression: Expression
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_not_expression(self)


@dataclass
class GroupedExpression(Expression):
    """Grouped expression node (parentheses)."""
    expression: Expression
    
    def accept(self, visitor: 'ASTVisitor') -> Any:
        return visitor.visit_grouped_expression(self)


class ASTVisitor(ABC):
    """Abstract visitor for AST nodes."""
    
    @abstractmethod
    def visit_string_value(self, node: StringValue) -> Any:
        pass
    
    @abstractmethod
    def visit_numeric_value(self, node: NumericValue) -> Any:
        pass
    
    @abstractmethod
    def visit_boolean_value(self, node: BooleanValue) -> Any:
        pass
    
    @abstractmethod
    def visit_date_value(self, node: DateValue) -> Any:
        pass
    
    @abstractmethod
    def visit_list_value(self, node: ListValue) -> Any:
        pass
    
    @abstractmethod
    def visit_range_value(self, node: RangeValue) -> Any:
        pass
    
    @abstractmethod
    def visit_null_value(self, node: NullValue) -> Any:
        pass
    
    @abstractmethod
    def visit_function_call(self, node: FunctionCall) -> Any:
        pass
    
    @abstractmethod
    def visit_field_expression(self, node: FieldExpression) -> Any:
        pass
    
    @abstractmethod
    def visit_text_search_expression(self, node: TextSearchExpression) -> Any:
        pass
    
    @abstractmethod
    def visit_and_expression(self, node: AndExpression) -> Any:
        pass
    
    @abstractmethod
    def visit_or_expression(self, node: OrExpression) -> Any:
        pass
    
    @abstractmethod
    def visit_not_expression(self, node: NotExpression) -> Any:
        pass
    
    @abstractmethod
    def visit_grouped_expression(self, node: GroupedExpression) -> Any:
        pass