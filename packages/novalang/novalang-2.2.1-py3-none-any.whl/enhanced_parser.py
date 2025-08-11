#!/usr/bin/env python3
"""
NovaLang Simple Parser - Enhanced to Support Spring Boot Style Syntax
Focused on making annotations, type hints, and object-oriented features work
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class TokenType(Enum):
    # Basic tokens
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    
    # Keywords
    CLASS = "class"
    FUNCTION = "function"
    PRIVATE = "private"
    PUBLIC = "public"
    RETURN = "return"
    LET = "let"
    NEW = "new"
    THIS = "this"
    IF = "if"
    ELSE = "else"
    
    # Symbols
    AT = "@"
    DOT = "."
    COMMA = ","
    SEMICOLON = ";"
    COLON = ":"
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    
    # Brackets
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    
    # Special
    STRING_CONTENT = "STRING_CONTENT"
    NEWLINE = "NEWLINE"
    EOF = "EOF"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

class SpringBootParser:
    def __init__(self, source: str):
        self.source = source
        self.tokens = self.tokenize(source)
        self.current = 0
        self.ast = []

    def tokenize(self, source: str) -> List[Token]:
        """Enhanced tokenizer supporting annotations and Spring Boot syntax"""
        tokens = []
        lines = source.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            i = 0
            while i < len(line):
                char = line[i]
                
                # Skip whitespace
                if char.isspace():
                    i += 1
                    continue
                
                # Comments
                if char == '/' and i + 1 < len(line) and line[i + 1] == '/':
                    break  # Skip rest of line
                
                # Annotations
                if char == '@':
                    tokens.append(Token(TokenType.AT, '@', line_num, i))
                    i += 1
                    continue
                
                # String literals
                if char == '"':
                    start = i
                    i += 1
                    string_value = ""
                    while i < len(line) and line[i] != '"':
                        string_value += line[i]
                        i += 1
                    if i < len(line):
                        i += 1  # Skip closing quote
                    tokens.append(Token(TokenType.STRING, string_value, line_num, start))
                    continue
                
                # Numbers
                if char.isdigit():
                    start = i
                    while i < len(line) and (line[i].isdigit() or line[i] == '.'):
                        i += 1
                    tokens.append(Token(TokenType.NUMBER, line[start:i], line_num, start))
                    continue
                
                # Identifiers and keywords
                if char.isalpha() or char == '_':
                    start = i
                    while i < len(line) and (line[i].isalnum() or line[i] == '_'):
                        i += 1
                    word = line[start:i]
                    
                    # Keywords
                    keyword_map = {
                        'class': TokenType.CLASS,
                        'function': TokenType.FUNCTION,
                        'private': TokenType.PRIVATE,
                        'public': TokenType.PUBLIC,
                        'return': TokenType.RETURN,
                        'let': TokenType.LET,
                        'new': TokenType.NEW,
                        'this': TokenType.THIS,
                        'if': TokenType.IF,
                        'else': TokenType.ELSE
                    }
                    
                    token_type = keyword_map.get(word, TokenType.IDENTIFIER)
                    tokens.append(Token(token_type, word, line_num, start))
                    continue
                
                # Single character tokens
                single_char_map = {
                    '.': TokenType.DOT,
                    ',': TokenType.COMMA,
                    ';': TokenType.SEMICOLON,
                    ':': TokenType.COLON,
                    '=': TokenType.ASSIGN,
                    '+': TokenType.PLUS,
                    '-': TokenType.MINUS,
                    '*': TokenType.MULTIPLY,
                    '/': TokenType.DIVIDE,
                    '(': TokenType.LEFT_PAREN,
                    ')': TokenType.RIGHT_PAREN,
                    '{': TokenType.LEFT_BRACE,
                    '}': TokenType.RIGHT_BRACE,
                    '[': TokenType.LEFT_BRACKET,
                    ']': TokenType.RIGHT_BRACKET
                }
                
                if char in single_char_map:
                    tokens.append(Token(single_char_map[char], char, line_num, i))
                    i += 1
                    continue
                
                # Unknown character - skip
                i += 1
        
        tokens.append(Token(TokenType.EOF, '', len(lines), 0))
        return tokens

    def peek(self) -> Token:
        """Look at current token without consuming"""
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return Token(TokenType.EOF, '', 0, 0)

    def advance(self) -> Token:
        """Consume and return current token"""
        token = self.peek()
        if self.current < len(self.tokens) - 1:
            self.current += 1
        return token

    def match(self, *types: TokenType) -> bool:
        """Check if current token matches any of given types"""
        return self.peek().type in types

    def consume(self, token_type: TokenType, message: str = "") -> Token:
        """Consume token of expected type or raise error"""
        if self.match(token_type):
            return self.advance()
        current = self.peek()
        error_msg = f"Expected {token_type}, got {current.type} '{current.value}' at line {current.line}"
        if message:
            error_msg += f": {message}"
        raise SyntaxError(error_msg)

    def parse(self) -> Dict[str, Any]:
        """Parse the source code into a working AST"""
        result = {
            'type': 'Program',
            'classes': [],
            'functions': [],
            'annotations': []
        }

        while not self.match(TokenType.EOF):
            # Parse annotations
            annotations = []
            while self.match(TokenType.AT):
                annotations.append(self.parse_annotation())

            # Parse class or function
            if self.match(TokenType.CLASS):
                class_def = self.parse_class(annotations)
                result['classes'].append(class_def)
            elif self.match(TokenType.FUNCTION):
                func_def = self.parse_function(annotations)
                result['functions'].append(func_def)
            else:
                # Skip unknown tokens
                self.advance()

        return result

    def parse_annotation(self) -> Dict[str, Any]:
        """Parse @Entity, @Service, @RestController, etc."""
        self.consume(TokenType.AT)
        name_token = self.consume(TokenType.IDENTIFIER)
        
        annotation = {
            'type': 'Annotation',
            'name': name_token.value,
            'parameters': {}
        }

        # Parse annotation parameters like @GetMapping("/users")
        if self.match(TokenType.LEFT_PAREN):
            self.advance()  # consume (
            
            while not self.match(TokenType.RIGHT_PAREN) and not self.match(TokenType.EOF):
                if self.match(TokenType.STRING):
                    # Simple string parameter
                    param_token = self.advance()
                    annotation['parameters']['value'] = param_token.value
                else:
                    # Skip other parameter types for now
                    self.advance()
                
                if self.match(TokenType.COMMA):
                    self.advance()
            
            if self.match(TokenType.RIGHT_PAREN):
                self.advance()

        return annotation

    def parse_class(self, annotations: List[Dict]) -> Dict[str, Any]:
        """Parse class definition with Spring Boot style"""
        self.consume(TokenType.CLASS)
        name_token = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.LEFT_BRACE)

        class_def = {
            'type': 'Class',
            'name': name_token.value,
            'annotations': annotations,
            'fields': [],
            'methods': []
        }

        while not self.match(TokenType.RIGHT_BRACE) and not self.match(TokenType.EOF):
            # Parse field annotations
            field_annotations = []
            while self.match(TokenType.AT):
                field_annotations.append(self.parse_annotation())

            # Parse visibility modifier
            visibility = 'public'
            if self.match(TokenType.PRIVATE, TokenType.PUBLIC):
                visibility = self.advance().value

            # Parse function or field
            if self.match(TokenType.FUNCTION):
                method = self.parse_method(field_annotations, visibility)
                class_def['methods'].append(method)
            elif self.match(TokenType.IDENTIFIER):
                field = self.parse_field(field_annotations, visibility)
                class_def['fields'].append(field)
            else:
                # Skip unknown content
                self.advance()

        self.consume(TokenType.RIGHT_BRACE)
        return class_def

    def parse_method(self, annotations: List[Dict], visibility: str) -> Dict[str, Any]:
        """Parse method definition"""
        self.consume(TokenType.FUNCTION)
        name_token = self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.LEFT_PAREN)

        parameters = []
        while not self.match(TokenType.RIGHT_PAREN) and not self.match(TokenType.EOF):
            param_token = self.consume(TokenType.IDENTIFIER)
            param = {'name': param_token.value, 'type': 'any'}
            
            # Parse optional type annotation
            if self.match(TokenType.COLON):
                self.advance()
                if self.match(TokenType.IDENTIFIER):
                    type_token = self.advance()
                    param['type'] = type_token.value
            
            parameters.append(param)
            
            if self.match(TokenType.COMMA):
                self.advance()

        self.consume(TokenType.RIGHT_PAREN)

        # Parse return type
        return_type = 'void'
        if self.match(TokenType.COLON):
            self.advance()
            if self.match(TokenType.IDENTIFIER):
                return_type = self.advance().value

        # Parse method body
        body = []
        if self.match(TokenType.LEFT_BRACE):
            self.advance()
            while not self.match(TokenType.RIGHT_BRACE) and not self.match(TokenType.EOF):
                # Simple statement parsing
                stmt = self.parse_statement()
                if stmt:
                    body.append(stmt)
            self.consume(TokenType.RIGHT_BRACE)

        return {
            'type': 'Method',
            'name': name_token.value,
            'annotations': annotations,
            'visibility': visibility,
            'parameters': parameters,
            'returnType': return_type,
            'body': body
        }

    def parse_field(self, annotations: List[Dict], visibility: str) -> Dict[str, Any]:
        """Parse field definition"""
        name_token = self.advance()  # Already matched IDENTIFIER
        
        field_type = 'any'
        if self.match(TokenType.COLON):
            self.advance()
            if self.match(TokenType.IDENTIFIER):
                field_type = self.advance().value

        # Skip initializer for now
        if self.match(TokenType.ASSIGN):
            self.advance()
            # Skip until semicolon or newline
            while not self.match(TokenType.SEMICOLON, TokenType.EOF):
                self.advance()

        if self.match(TokenType.SEMICOLON):
            self.advance()

        return {
            'type': 'Field',
            'name': name_token.value,
            'annotations': annotations,
            'visibility': visibility,
            'fieldType': field_type
        }

    def parse_statement(self) -> Optional[Dict[str, Any]]:
        """Parse a simple statement"""
        # Console.log/print statements
        if self.match(TokenType.IDENTIFIER):
            current = self.peek()
            if current.value in ['console', 'print']:
                return self.parse_print_statement()
        
        # Return statements
        elif self.match(TokenType.RETURN):
            return self.parse_return_statement()
        
        # Skip unknown statements
        else:
            self.advance()
            return None

    def parse_print_statement(self) -> Dict[str, Any]:
        """Parse console.log() or print statements"""
        func_token = self.advance()  # console or print
        args = []  # Initialize args here
        
        if func_token.value == 'console':
            if self.match(TokenType.DOT):
                self.advance()
                if self.match(TokenType.IDENTIFIER):
                    method = self.advance()  # log
        
        if self.match(TokenType.LEFT_PAREN):
            self.advance()
            
            while not self.match(TokenType.RIGHT_PAREN) and not self.match(TokenType.EOF):
                if self.match(TokenType.STRING):
                    args.append({'type': 'String', 'value': self.advance().value})
                elif self.match(TokenType.IDENTIFIER):
                    args.append({'type': 'Identifier', 'value': self.advance().value})
                elif self.match(TokenType.PLUS):
                    self.advance()  # Skip + for string concatenation
                else:
                    self.advance()
            
            if self.match(TokenType.RIGHT_PAREN):
                self.advance()
        
        if self.match(TokenType.SEMICOLON):
            self.advance()
        
        return {
            'type': 'PrintStatement',
            'arguments': args
        }

    def parse_return_statement(self) -> Dict[str, Any]:
        """Parse return statements"""
        self.consume(TokenType.RETURN)
        
        value = None
        if self.match(TokenType.STRING):
            value = {'type': 'String', 'value': self.advance().value}
        elif self.match(TokenType.IDENTIFIER):
            value = {'type': 'Identifier', 'value': self.advance().value}
        
        if self.match(TokenType.SEMICOLON):
            self.advance()
        
        return {
            'type': 'ReturnStatement',
            'value': value
        }

    def parse_function(self, annotations: List[Dict]) -> Dict[str, Any]:
        """Parse standalone function"""
        return self.parse_method(annotations, 'public')


# Test the enhanced parser
if __name__ == "__main__":
    test_code = '''
@RestController
class UserController {
    @GetMapping("/users")
    function getAllUsers() {
        console.log("Getting all users");
        return "Users retrieved";
    }
    
    @PostMapping("/users")
    function createUser(email, firstName) {
        print "Creating user: " + email;
        return "User created";
    }
}

@Entity
class User {
    @Id
    private id;
    
    @Column
    private email;
    
    function getEmail() {
        return this.email;
    }
}
'''

    try:
        parser = SpringBootParser(test_code)
        ast = parser.parse()
        
        print("🎉 Enhanced Parser Working!")
        print(f"✅ Found {len(ast['classes'])} classes")
        
        for cls in ast['classes']:
            print(f"📦 Class: {cls['name']}")
            print(f"   🏷️ Annotations: {[a['name'] for a in cls['annotations']]}")
            print(f"   🔧 Methods: {len(cls['methods'])}")
            print(f"   📊 Fields: {len(cls['fields'])}")
            
    except Exception as e:
        print(f"❌ Parser error: {e}")
