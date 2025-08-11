#!/usr/bin/env python3
"""
NovaLang Simple Parser - Fixed for Basic Syntax
Handles the working syntax pattern: class { function() { print ""; } }
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from lexer import Token, TokenType, NovaLangLexer

@dataclass
class SimpleFunction:
    name: str
    parameters: List[str]
    body: List[str]

@dataclass
class SimpleClass:
    name: str
    functions: List[SimpleFunction]

class SimpleNovaParser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def current_token(self) -> Optional[Token]:
        if self.current >= len(self.tokens):
            return None
        return self.tokens[self.current]
    
    def advance(self):
        if self.current < len(self.tokens):
            self.current += 1
    
    def match(self, *token_types: TokenType) -> bool:
        token = self.current_token()
        return token is not None and token.type in token_types
    
    def consume(self, token_type: TokenType) -> Token:
        token = self.current_token()
        if not token or token.type != token_type:
            raise Exception(f"Expected {token_type}, got {token.type if token else 'EOF'}")
        self.advance()
        return token
    
    def parse_class(self) -> SimpleClass:
        # Consume 'class'
        self.consume(TokenType.CLASS)
        
        # Get class name
        name_token = self.consume(TokenType.IDENTIFIER)
        class_name = name_token.value
        
        # Consume '{'
        self.consume(TokenType.LEFT_BRACE)
        
        functions = []
        
        # Parse functions until '}'
        while not self.match(TokenType.RIGHT_BRACE) and self.current_token():
            # Skip newlines
            if self.match(TokenType.NEWLINE):
                self.advance()
                continue
                
            if self.match(TokenType.FUNCTION):
                function = self.parse_function()
                functions.append(function)
            else:
                # Skip unknown tokens
                self.advance()
        
        # Consume '}'
        self.consume(TokenType.RIGHT_BRACE)
        
        return SimpleClass(class_name, functions)
    
    def parse_function(self) -> SimpleFunction:
        # Consume 'function'
        self.consume(TokenType.FUNCTION)
        
        # Get function name
        name_token = self.consume(TokenType.IDENTIFIER)
        function_name = name_token.value
        
        # Consume '('
        self.consume(TokenType.LEFT_PAREN)
        
        # Parse parameters (simplified)
        parameters = []
        while not self.match(TokenType.RIGHT_PAREN) and self.current_token():
            if self.match(TokenType.IDENTIFIER):
                param_token = self.consume(TokenType.IDENTIFIER)
                parameters.append(param_token.value)
                
                # Skip comma if present
                if self.match(TokenType.COMMA):
                    self.advance()
            else:
                self.advance()
        
        # Consume ')'
        self.consume(TokenType.RIGHT_PAREN)
        
        # Consume '{'
        self.consume(TokenType.LEFT_BRACE)
        
        # Parse function body (simplified - just collect tokens)
        body = []
        brace_count = 1  # We already consumed one {
        
        while brace_count > 0 and self.current_token():
            token = self.current_token()
            
            if token.type == TokenType.LEFT_BRACE:
                brace_count += 1
            elif token.type == TokenType.RIGHT_BRACE:
                brace_count -= 1
                
            if brace_count > 0:  # Don't include the final }
                if token.type == TokenType.STRING:
                    body.append(f'print {token.value}')
                elif token.type == TokenType.IDENTIFIER and token.value == 'print':
                    body.append('print statement')
                elif token.type == TokenType.RETURN:
                    body.append('return statement')
            
            self.advance()
        
        return SimpleFunction(function_name, parameters, body)
    
    def parse(self) -> Optional[SimpleClass]:
        """Parse a simple NovaLang class"""
        # Skip any leading newlines
        while self.match(TokenType.NEWLINE):
            self.advance()
            
        if self.match(TokenType.CLASS):
            return self.parse_class()
        return None

def parse_nova_file(content: str) -> Optional[SimpleClass]:
    """Parse NovaLang content and return a SimpleClass if found"""
    try:
        print(f"📝 Parsing content: {content[:50]}...")
        lexer = NovaLangLexer(content)
        tokens = lexer.tokenize()
        print(f"🔤 Generated {len(tokens)} tokens")
        
        for i, token in enumerate(tokens[:10]):  # Show first 10 tokens
            print(f"  {i}: {token.type} = '{token.value}'")
        
        parser = SimpleNovaParser(tokens)
        result = parser.parse()
        print(f"✅ Parse result: {result}")
        return result
    except Exception as e:
        print(f"❌ Parse error: {e}")
        import traceback
        traceback.print_exc()
        return None

# Test the parser
if __name__ == "__main__":
    test_code = '''
class UserController {
    function getAllUsers() {
        print "🌐 GET /api/users";
        print "✅ Returning all users";
        return "Users list retrieved";
    }
    
    function createUser(email, firstName, lastName) {
        print "🌐 POST /api/users";
        return "User created";
    }
}
'''
    
    result = parse_nova_file(test_code)
    if result:
        print(f"✅ Parsed class: {result.name}")
        for func in result.functions:
            print(f"  📝 Function: {func.name}({', '.join(func.parameters)})")
            for line in func.body:
                print(f"    {line}")
    else:
        print("❌ Parse failed")
