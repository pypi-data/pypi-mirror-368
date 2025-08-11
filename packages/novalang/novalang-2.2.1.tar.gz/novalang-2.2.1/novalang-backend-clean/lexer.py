"""
NovaLang Lexer
Tokenizes NovaLang source code into tokens for parsing.
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Iterator


class TokenType(Enum):
    TEST = auto()
    IMPORT = auto()
    UI = auto()
    TRY = auto()
    CATCH = auto()
    API = auto()
    AI = auto()
    PLUGIN = auto()
    EXPORT = auto()
    COMPONENT = auto()
    GET = auto()
    POST = auto()
    PUT = auto()
    DELETE = auto()
    # Literals
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    
    # Identifiers
    IDENTIFIER = auto()
    
    # Keywords
    LET = auto()
    CONST = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    FUNCTION = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    PRINT = auto()
    ASK = auto()
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    ASSIGN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    
    # Delimiters
    SEMICOLON = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()
    
    # Brackets
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    
    # Special
    NEWLINE = auto()
    EOF = auto()
    

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
        # Keywords mapping
        self.keywords = {
            'let': TokenType.LET,
            'const': TokenType.CONST,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'function': TokenType.FUNCTION,
            'return': TokenType.RETURN,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
            'null': TokenType.NULL,
            'print': TokenType.PRINT,
            'ask': TokenType.ASK,
            'api': TokenType.API,
            'GET': TokenType.GET,
            'POST': TokenType.POST,
            'PUT': TokenType.PUT,
            'DELETE': TokenType.DELETE,
            'try': TokenType.TRY,
            'catch': TokenType.CATCH,
            'ui': TokenType.UI,
            'import': TokenType.IMPORT,
            'export': TokenType.EXPORT,
            'test': TokenType.TEST,
            'component': TokenType.COMPONENT,
        }
        
        # Two-character operators
        self.two_char_ops = {
            '==': TokenType.EQUAL,
            '!=': TokenType.NOT_EQUAL,
            '<=': TokenType.LESS_EQUAL,
            '>=': TokenType.GREATER_EQUAL,
            '&&': TokenType.AND,
            '||': TokenType.OR,
        }
        
        # Single-character operators and delimiters
        self.single_char_tokens = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '%': TokenType.MODULO,
            '=': TokenType.ASSIGN,
            '<': TokenType.LESS,
            '>': TokenType.GREATER,
            '!': TokenType.NOT,
            ';': TokenType.SEMICOLON,
            ',': TokenType.COMMA,
            '.': TokenType.DOT,
            ':': TokenType.COLON,
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            '{': TokenType.LEFT_BRACE,
            '}': TokenType.RIGHT_BRACE,
            '[': TokenType.LEFT_BRACKET,
            ']': TokenType.RIGHT_BRACKET,
        }
    
    def current_char(self) -> Optional[str]:
        """Get the current character."""
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Peek at the character at current position + offset."""
        pos = self.position + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self) -> Optional[str]:
        """Advance to the next character and return the current one."""
        if self.position >= len(self.source):
            return None
        
        char = self.source[self.position]
        self.position += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def skip_whitespace(self):
        """Skip whitespace characters except newlines."""
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        """Skip single-line comments."""
        if self.current_char() == '/' and self.peek_char() == '/':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_number(self) -> str:
        """Read a number literal."""
        number = ''
        has_dot = False
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if has_dot:
                    break  # Second dot, stop reading
                has_dot = True
            number += self.advance()
        
        return number
    
    def read_string(self) -> str:
        """Read a string literal."""
        quote_char = self.current_char()
        self.advance()  # Skip opening quote
        
        string_value = ''
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()  # Skip backslash
                escaped_char = self.current_char()
                if escaped_char in '"\'\\nrt':
                    escape_map = {'n': '\n', 'r': '\r', 't': '\t'}
                    string_value += escape_map.get(escaped_char, escaped_char)
                    self.advance()
                else:
                    string_value += '\\'
            else:
                string_value += self.advance()
        
        if self.current_char() == quote_char:
            self.advance()  # Skip closing quote
        
        return string_value
    
    def read_identifier(self) -> str:
        """Read an identifier or keyword."""
        identifier = ''
        while (self.current_char() and 
               (self.current_char().isalnum() or self.current_char() == '_')):
            identifier += self.advance()
        return identifier
    
    def add_token(self, token_type: TokenType, value: str = ''):
        """Add a token to the tokens list."""
        token = Token(token_type, value, self.line, self.column - len(value))
        # print(f"[LEXER DEBUG] Token: {token_type.name}, value: '{value}', line: {token.line}, column: {token.column}")
        self.tokens.append(token)
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code."""
        while self.position < len(self.source):
            self.skip_whitespace()
            char = self.current_char()
            if not char:
                break
            # Handle Windows (\r\n) and Unix (\n) newlines
            if char == '\r' and self.peek_char() == '\n':
                self.add_token(TokenType.NEWLINE, '\r\n')
                self.advance()  # skip '\r'
                self.advance()  # skip '\n'
                continue
            if char == '\n':
                self.add_token(TokenType.NEWLINE, char)
                self.advance()
                continue
            
            # Handle comments
            if char == '/' and self.peek_char() == '/':
                self.skip_comment()
                continue
            
            # Handle numbers
            if char.isdigit():
                number = self.read_number()
                self.add_token(TokenType.NUMBER, number)
                continue
            
            # Handle strings
            if char in '"\'':
                string_value = self.read_string()
                self.add_token(TokenType.STRING, string_value)
                continue
            
            # Handle identifiers and keywords
            if char.isalpha() or char == '_':
                identifier = self.read_identifier()
                token_type = self.keywords.get(identifier, TokenType.IDENTIFIER)
                self.add_token(token_type, identifier)
                continue
            
            # Handle two-character operators
            two_char = char + (self.peek_char() or '')
            if two_char in self.two_char_ops:
                self.add_token(self.two_char_ops[two_char], two_char)
                self.advance()
                self.advance()
                continue
            
            # Handle single-character tokens
            if char in self.single_char_tokens:
                self.add_token(self.single_char_tokens[char], char)
                self.advance()
                continue
            
            # Unknown character
            raise SyntaxError(f"Unexpected character '{char}' at line {self.line}, column {self.column}")
        
        # Add EOF token
        self.add_token(TokenType.EOF)
        return self.tokens


if __name__ == "__main__":
    # Test the lexer
    with open("test_framework.nova", "r", encoding="utf-8") as f:
        source = f.read()
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    for token in tokens:
        print(f"{token.type.name}: '{token.value}' at {token.line}:{token.column}")
