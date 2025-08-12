"""Tokenizer for the Gira Query Language."""

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Union


class TokenType(Enum):
    """Token types for the query language."""
    
    # Literals
    STRING = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    NULL = auto()
    
    # Identifiers
    FIELD = auto()
    FUNCTION = auto()
    
    # Operators
    COLON = auto()          # :
    EQUALS = auto()         # =
    NOT_EQUALS = auto()     # != or !:
    FUZZY = auto()          # ~
    NOT_FUZZY = auto()      # !~
    GREATER = auto()        # >
    GREATER_EQUAL = auto()  # >=
    LESS = auto()           # <
    LESS_EQUAL = auto()     # <=
    
    # Text operators
    CONTAINS = auto()
    STARTS_WITH = auto()
    ENDS_WITH = auto()
    MATCHES = auto()
    
    # List operators
    IN = auto()
    NOT_IN = auto()
    
    # Null operators
    IS_NULL = auto()
    IS_NOT_NULL = auto()
    EMPTY = auto()
    NOT_EMPTY = auto()
    
    # Boolean operators
    AND = auto()
    OR = auto()
    NOT = auto()
    
    # Delimiters
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    COMMA = auto()          # ,
    DOT = auto()            # .
    DOTDOT = auto()         # ..
    
    # Special
    EOF = auto()


@dataclass
class Token:
    """Represents a token in the query language."""
    type: TokenType
    value: Union[str, int, float, bool, None]
    position: int
    length: int
    
    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, {self.position}:{self.position + self.length})"


class Tokenizer:
    """Tokenizes query strings into tokens."""
    
    # Reserved keywords (case-insensitive)
    KEYWORDS = {
        # Boolean operators
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
        
        # Boolean values
        'true': TokenType.BOOLEAN,
        'false': TokenType.BOOLEAN,
        'yes': TokenType.BOOLEAN,
        'no': TokenType.BOOLEAN,
        
        # Null values
        'null': TokenType.NULL,
        'empty': TokenType.EMPTY,
        
        # Operators
        'contains': TokenType.CONTAINS,
        'starts_with': TokenType.STARTS_WITH,
        'ends_with': TokenType.ENDS_WITH,
        'matches': TokenType.MATCHES,
        'in': TokenType.IN,
        'not_in': TokenType.NOT_IN,
        'is_null': TokenType.IS_NULL,
        'is_not_null': TokenType.IS_NOT_NULL,
        'not_empty': TokenType.NOT_EMPTY,
    }
    
    # Relative date keywords
    RELATIVE_DATES = {
        'today', 'yesterday', 'tomorrow',
        'this_week', 'last_week', 'next_week',
        'this_month', 'last_month', 'next_month',
        'this_year', 'last_year', 'next_year'
    }
    
    def __init__(self, query: str):
        self.query = query
        self.position = 0
        self.tokens: List[Token] = []
        
    def tokenize(self) -> List[Token]:
        """Tokenize the query string."""
        while self.position < len(self.query):
            self._skip_whitespace()
            
            if self.position >= len(self.query):
                break
                
            # Try to match each token type
            if self._match_string():
                continue
            elif self._match_date():
                continue
            elif self._match_number():
                continue
            elif self._match_identifier_or_keyword():
                continue
            elif self._match_operator():
                continue
            elif self._match_delimiter():
                continue
            else:
                # Unknown character
                raise ValueError(f"Unexpected character '{self.query[self.position]}' at position {self.position}")
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.position, 0))
        return self.tokens
    
    def _skip_whitespace(self) -> None:
        """Skip whitespace characters."""
        while self.position < len(self.query) and self.query[self.position].isspace():
            self.position += 1
    
    def _peek(self, offset: int = 0) -> Optional[str]:
        """Peek at a character without consuming it."""
        pos = self.position + offset
        if pos < len(self.query):
            return self.query[pos]
        return None
    
    def _consume(self) -> str:
        """Consume and return the current character."""
        if self.position < len(self.query):
            char = self.query[self.position]
            self.position += 1
            return char
        raise ValueError("Unexpected end of input")
    
    def _match_date(self) -> bool:
        """Match ISO date format (YYYY-MM-DD)."""
        if not (self._peek() and self._peek().isdigit()):
            return False
            
        start = self.position
        
        # Try to match YYYY-MM-DD pattern
        if (self.position + 10 <= len(self.query) and
            self.query[self.position:self.position+4].isdigit() and
            self.query[self.position+4] == '-' and
            self.query[self.position+5:self.position+7].isdigit() and
            self.query[self.position+7] == '-' and
            self.query[self.position+8:self.position+10].isdigit()):
            
            # Consume the date
            for _ in range(10):
                self._consume()
            
            # Check for optional time part
            if self._peek() == 'T':
                # Try to match time part
                saved_pos = self.position
                self._consume()  # T
                
                # HH:MM:SS
                if (self.position + 8 <= len(self.query) and
                    self.query[self.position:self.position+2].isdigit() and
                    self.query[self.position+2] == ':' and
                    self.query[self.position+3:self.position+5].isdigit() and
                    self.query[self.position+5] == ':' and
                    self.query[self.position+6:self.position+8].isdigit()):
                    
                    for _ in range(8):
                        self._consume()
                    
                    # Optional Z or timezone
                    if self._peek() == 'Z':
                        self._consume()
                    elif self._peek() in '+-':
                        # Timezone offset
                        self._consume()  # + or -
                        if (self.position + 5 <= len(self.query) and
                            self.query[self.position:self.position+2].isdigit() and
                            self.query[self.position+2] == ':' and
                            self.query[self.position+3:self.position+5].isdigit()):
                            for _ in range(5):
                                self._consume()
                else:
                    # Invalid time part, reset
                    self.position = saved_pos
            
            value = self.query[start:self.position]
            self.tokens.append(Token(TokenType.STRING, value, start, self.position - start))
            return True
        
        return False
    
    def _match_string(self) -> bool:
        """Match a quoted string."""
        if self._peek() != '"':
            return False
            
        start = self.position
        self._consume()  # Opening quote
        
        value = []
        while self.position < len(self.query):
            char = self._peek()
            if char == '"':
                self._consume()  # Closing quote
                self.tokens.append(Token(
                    TokenType.STRING,
                    ''.join(value),
                    start,
                    self.position - start
                ))
                return True
            elif char == '\\' and self._peek(1) == '"':
                # Escaped quote
                self._consume()  # Backslash
                self._consume()  # Quote
                value.append('"')
            elif char == '\\' and self._peek(1) == '\\':
                # Escaped backslash
                self._consume()  # Backslash
                self._consume()  # Backslash
                value.append('\\')
            else:
                value.append(self._consume())
        
        raise ValueError(f"Unterminated string starting at position {start}")
    
    def _match_number(self) -> bool:
        """Match a numeric value."""
        if not (self._peek() and (self._peek().isdigit() or self._peek() == '-')):
            return False
            
        start = self.position
        
        # Optional negative sign
        if self._peek() == '-':
            self._consume()
        
        # Require at least one digit
        if not (self._peek() and self._peek().isdigit()):
            self.position = start  # Reset
            return False
        
        # Consume digits
        while self._peek() and self._peek().isdigit():
            self._consume()
        
        # Check for decimal point
        is_float = False
        if self._peek() == '.' and self._peek(1) and self._peek(1).isdigit():
            is_float = True
            self._consume()  # Decimal point
            while self._peek() and self._peek().isdigit():
                self._consume()
        
        value_str = self.query[start:self.position]
        value = float(value_str) if is_float else int(value_str)
        
        self.tokens.append(Token(
            TokenType.NUMBER,
            value,
            start,
            self.position - start
        ))
        return True
    
    def _match_identifier_or_keyword(self) -> bool:
        """Match an identifier or keyword."""
        if not (self._peek() and (self._peek().isalpha() or self._peek() == '_')):
            return False
            
        start = self.position
        
        # First character must be letter or underscore
        self._consume()
        
        # Subsequent characters can be letters, digits, underscores, @ or . (for email)
        # Special handling for hyphens - only include if part of an ID pattern
        while self._peek():
            char = self._peek()
            if char.isalnum() or char in '_@.':
                self._consume()
            elif char == '-' and self._peek(1) and self._peek(1).isalnum():
                # Allow hyphen if followed by alphanumeric (for IDs like GIRA-123)
                self._consume()
            else:
                break
        
        value = self.query[start:self.position]
        value_lower = value.lower()
        
        # Check if it's a keyword
        if value_lower in self.KEYWORDS:
            token_type = self.KEYWORDS[value_lower]
            
            # Handle boolean values
            if token_type == TokenType.BOOLEAN:
                bool_value = value_lower in ('true', 'yes', '1')
                self.tokens.append(Token(
                    TokenType.BOOLEAN,
                    bool_value,
                    start,
                    self.position - start
                ))
            else:
                self.tokens.append(Token(
                    token_type,
                    value_lower,
                    start,
                    self.position - start
                ))
        elif value_lower in self.RELATIVE_DATES:
            # Relative date keywords are treated as strings
            self.tokens.append(Token(
                TokenType.STRING,
                value_lower,
                start,
                self.position - start
            ))
        else:
            # Check if followed by '(' to determine if it's a function
            self._skip_whitespace()
            if self._peek() == '(':
                self.tokens.append(Token(
                    TokenType.FUNCTION,
                    value,
                    start,
                    self.position - start
                ))
            else:
                self.tokens.append(Token(
                    TokenType.FIELD,
                    value,
                    start,
                    self.position - start
                ))
        
        return True
    
    def _match_operator(self) -> bool:
        """Match an operator."""
        start = self.position
        
        # Two-character operators
        if self._peek() and self._peek(1):
            two_char = self._peek() + self._peek(1)
            token_type = None
            
            if two_char == '!=':
                token_type = TokenType.NOT_EQUALS
            elif two_char == '!:':
                token_type = TokenType.NOT_EQUALS
            elif two_char == '!~':
                token_type = TokenType.NOT_FUZZY
            elif two_char == '>=':
                token_type = TokenType.GREATER_EQUAL
            elif two_char == '<=':
                token_type = TokenType.LESS_EQUAL
            elif two_char == '..':
                token_type = TokenType.DOTDOT
            
            if token_type:
                self._consume()
                self._consume()
                self.tokens.append(Token(
                    token_type,
                    two_char,
                    start,
                    2
                ))
                return True
        
        # Single-character operators
        if self._peek():
            char = self._peek()
            token_type = None
            
            if char == ':':
                token_type = TokenType.COLON
            elif char == '=':
                token_type = TokenType.EQUALS
            elif char == '~':
                token_type = TokenType.FUZZY
            elif char == '>':
                token_type = TokenType.GREATER
            elif char == '<':
                token_type = TokenType.LESS
            
            if token_type:
                self._consume()
                self.tokens.append(Token(
                    token_type,
                    char,
                    start,
                    1
                ))
                return True
        
        return False
    
    def _match_delimiter(self) -> bool:
        """Match a delimiter."""
        if not self._peek():
            return False
            
        start = self.position
        char = self._peek()
        token_type = None
        
        if char == '(':
            token_type = TokenType.LPAREN
        elif char == ')':
            token_type = TokenType.RPAREN
        elif char == ',':
            token_type = TokenType.COMMA
        elif char == '.':
            token_type = TokenType.DOT
        
        if token_type:
            self._consume()
            self.tokens.append(Token(
                token_type,
                char,
                start,
                1
            ))
            return True
        
        return False