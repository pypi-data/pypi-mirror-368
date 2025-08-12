"""Recursive descent parser for the Gira Query Language."""

from datetime import datetime
from typing import List, Optional, Set, Union

from gira.query.ast import (
    AndExpression,
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
from gira.query.tokenizer import Token, TokenType, Tokenizer


class QueryParseError(Exception):
    """Query parsing error."""
    
    def __init__(self, message: str, position: int):
        super().__init__(message)
        self.position = position


class QueryParser:
    """Recursive descent parser for query expressions."""
    
    # Valid field names for each entity type
    TICKET_FIELDS = {
        'id', 'uuid', 'title', 'description', 'status', 'type', 'priority',
        'assignee', 'reporter', 'epic_id', 'parent_id', 'sprint_id',
        'blocked_by', 'blocks', 'labels', 'comment_count', 'attachment_count',
        'due_date', 'story_points', 'order', 'created_at', 'updated_at'
    }
    
    EPIC_FIELDS = {
        'id', 'title', 'description', 'status', 'owner', 'target_date',
        'tickets', 'created_at', 'updated_at'
    }
    
    SPRINT_FIELDS = {
        'id', 'name', 'goal', 'start_date', 'end_date', 'status',
        'tickets', 'created_at', 'updated_at'
    }
    
    COMMENT_FIELDS = {
        'id', 'ticket_id', 'author', 'content', 'edited', 'edit_count',
        'is_ai_generated', 'ai_model', 'created_at', 'updated_at'
    }
    
    # All valid fields (union of all entity fields)
    ALL_FIELDS = TICKET_FIELDS | EPIC_FIELDS | SPRINT_FIELDS | COMMENT_FIELDS
    
    # Operators that require values
    VALUE_OPERATORS = {
        TokenType.COLON, TokenType.EQUALS, TokenType.NOT_EQUALS,
        TokenType.FUZZY, TokenType.NOT_FUZZY, TokenType.GREATER,
        TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL,
        TokenType.CONTAINS, TokenType.STARTS_WITH, TokenType.ENDS_WITH,
        TokenType.MATCHES, TokenType.IN, TokenType.NOT_IN
    }
    
    # Operators that don't require values
    NO_VALUE_OPERATORS = {
        TokenType.IS_NULL, TokenType.IS_NOT_NULL,
        TokenType.EMPTY, TokenType.NOT_EMPTY
    }
    
    def __init__(self, query: str, entity_type: str = 'ticket', validate_fields: bool = True):
        self.query = query
        self.entity_type = entity_type
        self.tokens: List[Token] = []
        self.position = 0
        self.validate_fields = validate_fields
        
        # Select valid fields based on entity type
        if entity_type == 'ticket':
            self.valid_fields = self.TICKET_FIELDS
        elif entity_type == 'epic':
            self.valid_fields = self.EPIC_FIELDS
        elif entity_type == 'sprint':
            self.valid_fields = self.SPRINT_FIELDS
        elif entity_type == 'comment':
            self.valid_fields = self.COMMENT_FIELDS
        else:
            self.valid_fields = self.ALL_FIELDS
    
    def parse(self) -> Optional[Expression]:
        """Parse the query string and return the AST."""
        # Tokenize the input
        tokenizer = Tokenizer(self.query)
        self.tokens = tokenizer.tokenize()
        self.position = 0
        
        # Empty query
        if self._current_token().type == TokenType.EOF:
            return None
        
        # Parse the expression
        expr = self._parse_or_expression()
        
        # Ensure we've consumed all tokens
        if self._current_token().type != TokenType.EOF:
            raise QueryParseError(
                f"Unexpected token: {self._current_token().value}",
                self._current_token().position
            )
        
        return expr
    
    def _current_token(self) -> Token:
        """Get the current token."""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return self.tokens[-1]  # EOF
    
    def _peek_token(self, offset: int = 1) -> Token:
        """Peek at a future token."""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # EOF
    
    def _consume_token(self) -> Token:
        """Consume and return the current token."""
        token = self._current_token()
        if token.type != TokenType.EOF:
            self.position += 1
        return token
    
    def _expect_token(self, token_type: TokenType) -> Token:
        """Consume a token of the expected type or raise an error."""
        token = self._current_token()
        if token.type != token_type:
            raise QueryParseError(
                f"Expected {token_type.name}, got {token.type.name}",
                token.position
            )
        return self._consume_token()
    
    def _parse_or_expression(self) -> Expression:
        """Parse OR expression (lowest precedence)."""
        left = self._parse_and_expression()
        
        while self._current_token().type == TokenType.OR:
            self._consume_token()  # OR
            right = self._parse_and_expression()
            left = OrExpression(left, right)
        
        return left
    
    def _parse_and_expression(self) -> Expression:
        """Parse AND expression."""
        left = self._parse_not_expression()
        
        while self._current_token().type == TokenType.AND:
            self._consume_token()  # AND
            right = self._parse_not_expression()
            left = AndExpression(left, right)
        
        return left
    
    def _parse_not_expression(self) -> Expression:
        """Parse NOT expression."""
        if self._current_token().type == TokenType.NOT:
            self._consume_token()  # NOT
            expr = self._parse_primary_expression()
            return NotExpression(expr)
        
        return self._parse_primary_expression()
    
    def _parse_primary_expression(self) -> Expression:
        """Parse primary expression (field, grouped, or text search)."""
        token = self._current_token()
        
        # Grouped expression
        if token.type == TokenType.LPAREN:
            return self._parse_grouped_expression()
        
        # Field expression
        elif token.type == TokenType.FIELD:
            return self._parse_field_expression()
        
        # Bare text search
        elif token.type == TokenType.STRING:
            value = token.value
            self._consume_token()
            return TextSearchExpression(str(value))
        
        else:
            raise QueryParseError(
                f"Unexpected token: {token.value}",
                token.position
            )
    
    def _parse_grouped_expression(self) -> GroupedExpression:
        """Parse grouped expression in parentheses."""
        self._expect_token(TokenType.LPAREN)
        expr = self._parse_or_expression()
        self._expect_token(TokenType.RPAREN)
        return GroupedExpression(expr)
    
    def _parse_field_expression(self) -> FieldExpression:
        """Parse field expression."""
        # Get field name (possibly with dots for nested access)
        field_parts = [self._expect_token(TokenType.FIELD).value]
        
        while self._current_token().type == TokenType.DOT:
            self._consume_token()  # DOT
            field_parts.append(self._expect_token(TokenType.FIELD).value)
        
        field = '.'.join(str(part) for part in field_parts)
        
        # Validate field name
        self._validate_field(field)
        
        # Get operator
        operator_token = self._current_token()
        operator_type = operator_token.type
        
        # Handle special case where operator immediately precedes value
        # (e.g., "description:contains(...)" where "contains" is the operator)
        if operator_type == TokenType.COLON:
            self._consume_token()  # :
            
            # Check if next token is a text operator or no-value operator
            next_token = self._current_token()
            if next_token.type in {TokenType.CONTAINS, TokenType.STARTS_WITH, 
                                   TokenType.ENDS_WITH, TokenType.MATCHES,
                                   TokenType.IN, TokenType.NOT_IN}:
                operator = self._consume_token().value
                value = self._parse_value()
                return FieldExpression(field, str(operator), value)
            elif next_token.type in self.NO_VALUE_OPERATORS:
                operator = self._consume_token().value
                return FieldExpression(field, str(operator), None)
            elif next_token.type in {TokenType.GREATER, TokenType.GREATER_EQUAL,
                                     TokenType.LESS, TokenType.LESS_EQUAL,
                                     TokenType.EQUALS, TokenType.NOT_EQUALS,
                                     TokenType.FUZZY, TokenType.NOT_FUZZY}:
                # Allow comparison operators after colon
                operator = self._consume_token().value
                value = self._parse_value()
                return FieldExpression(field, str(operator), value)
            else:
                # Regular field:value
                value = self._parse_value()
                return FieldExpression(field, ":", value)
        
        elif operator_type in self.VALUE_OPERATORS:
            operator = self._consume_token().value
            value = self._parse_value()
            return FieldExpression(field, str(operator), value)
        
        elif operator_type in self.NO_VALUE_OPERATORS:
            operator = self._consume_token().value
            return FieldExpression(field, str(operator), None)
        
        else:
            raise QueryParseError(
                f"Expected operator after field '{field}'",
                operator_token.position
            )
    
    def _parse_value(self) -> Value:
        """Parse a value."""
        token = self._current_token()
        
        if token.type == TokenType.STRING:
            return self._parse_string_value()
        
        elif token.type == TokenType.NUMBER:
            return self._parse_numeric_or_range_value()
        
        elif token.type == TokenType.BOOLEAN:
            value = token.value
            self._consume_token()
            return BooleanValue(bool(value))
        
        elif token.type == TokenType.NULL:
            self._consume_token()
            return NullValue()
        
        elif token.type == TokenType.FUNCTION:
            return self._parse_function_call()
        
        elif token.type == TokenType.LPAREN:
            return self._parse_list_value()
        
        elif token.type == TokenType.FIELD:
            # Unquoted string value (like status:todo)
            value = str(token.value)
            self._consume_token()
            
            # Check if it's a date
            date_obj = self._try_parse_date(value)
            if date_obj:
                is_relative = value in Tokenizer.RELATIVE_DATES
                return DateValue(date_obj, is_relative, value if is_relative else None)
            
            return StringValue(value)
        
        else:
            raise QueryParseError(
                f"Expected value, got {token.type.name}",
                token.position
            )
    
    def _parse_string_value(self) -> Union[StringValue, DateValue]:
        """Parse string value (might be a date)."""
        token = self._expect_token(TokenType.STRING)
        value = str(token.value)
        
        # Check if it's a date
        date_obj = self._try_parse_date(value)
        if date_obj:
            is_relative = value in Tokenizer.RELATIVE_DATES
            return DateValue(date_obj, is_relative, value if is_relative else None)
        
        return StringValue(value)
    
    def _parse_numeric_or_range_value(self) -> Union[NumericValue, RangeValue]:
        """Parse numeric value or range."""
        start_token = self._expect_token(TokenType.NUMBER)
        start = NumericValue(start_token.value)
        
        # Check for range
        if self._current_token().type == TokenType.DOTDOT:
            self._consume_token()  # ..
            end_token = self._expect_token(TokenType.NUMBER)
            end = NumericValue(end_token.value)
            return RangeValue(start, end)
        
        return start
    
    def _parse_function_call(self) -> FunctionCall:
        """Parse function call."""
        name_token = self._expect_token(TokenType.FUNCTION)
        name = str(name_token.value)
        
        self._expect_token(TokenType.LPAREN)
        
        arguments = []
        while self._current_token().type != TokenType.RPAREN:
            arguments.append(self._parse_value())
            
            if self._current_token().type == TokenType.COMMA:
                self._consume_token()
            elif self._current_token().type != TokenType.RPAREN:
                raise QueryParseError(
                    "Expected ',' or ')' in function arguments",
                    self._current_token().position
                )
        
        self._expect_token(TokenType.RPAREN)
        
        return FunctionCall(name, arguments)
    
    def _parse_list_value(self) -> ListValue:
        """Parse list value."""
        self._expect_token(TokenType.LPAREN)
        
        values = []
        while self._current_token().type != TokenType.RPAREN:
            values.append(self._parse_value())
            
            if self._current_token().type == TokenType.COMMA:
                self._consume_token()
            elif self._current_token().type != TokenType.RPAREN:
                raise QueryParseError(
                    "Expected ',' or ')' in list",
                    self._current_token().position
                )
        
        self._expect_token(TokenType.RPAREN)
        
        if not values:
            raise QueryParseError(
                "Empty list not allowed",
                self._current_token().position
            )
        
        return ListValue(values)
    
    def _validate_field(self, field: str) -> None:
        """Validate field name."""
        if not self.validate_fields:
            return
            
        # Handle nested fields (e.g., comments.author)
        base_field = field.split('.')[0]
        
        if base_field not in self.valid_fields:
            raise QueryParseError(
                f"Invalid field: '{base_field}'. Valid fields are: {', '.join(sorted(self.valid_fields))}",
                self._current_token().position
            )
    
    def _try_parse_date(self, value: str) -> Optional[datetime]:
        """Try to parse a date string."""
        # Relative dates
        if value in Tokenizer.RELATIVE_DATES:
            # Return current datetime as placeholder
            # Actual resolution happens during execution
            return datetime.now()
        
        # ISO date formats
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S%z'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        
        return None