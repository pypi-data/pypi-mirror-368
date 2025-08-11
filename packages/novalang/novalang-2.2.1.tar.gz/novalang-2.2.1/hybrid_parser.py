#!/usr/bin/env python3
"""
NovaLang Hybrid Parser - Supports both basic and advanced syntax
"""

from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
import traceback
from lexer import Token, TokenType, NovaLangLexer
from simple_parser import SimpleNovaParser, SimpleClass, SimpleFunction

# Try to import the advanced parser, fall back if not available
try:
    from parser import NovaLangParser
    ADVANCED_PARSER_AVAILABLE = True
except ImportError:
    ADVANCED_PARSER_AVAILABLE = False

class HybridNovaParser:
    def __init__(self, content: str):
        self.content = content
        self.lexer = NovaLangLexer(content)
        self.tokens = self.lexer.tokenize()
    
    def parse(self):
        """Try advanced parser first, fall back to simple parser"""
        
        # First, try the simple parser (for basic syntax)
        try:
            simple_parser = SimpleNovaParser(self.tokens)
            result = simple_parser.parse()
            if result:
                print(f"✅ Simple parser succeeded: {result.name}")
                return self.convert_simple_to_executable(result)
        except Exception as e:
            print(f"Simple parser failed: {e}")
        
        # If simple parser fails and advanced parser is available, try it
        if ADVANCED_PARSER_AVAILABLE:
            try:
                advanced_parser = NovaLangParser(self.tokens)
                result = advanced_parser.parse()
                print(f"✅ Advanced parser succeeded")
                return result
            except Exception as e:
                print(f"Advanced parser failed: {e}")
        
        raise Exception("Both simple and advanced parsers failed")
    
    def convert_simple_to_executable(self, simple_class: SimpleClass):
        """Convert SimpleClass to executable format"""
        return {
            'type': 'class',
            'name': simple_class.name,
            'functions': [
                {
                    'name': func.name,
                    'parameters': func.parameters,
                    'body': func.body
                }
                for func in simple_class.functions
            ]
        }

def parse_file(file_path: str):
    """Parse a NovaLang file using hybrid approach"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parser = HybridNovaParser(content)
        return parser.parse()
    except Exception as e:
        print(f"❌ Failed to parse {file_path}: {e}")
        return None

# Test the hybrid parser
if __name__ == "__main__":
    # Test with our working UserController
    test_file = r"c:\Users\nm\Documents\novalang\ecommerce-auto-mysql\src\controllers\UserController.nova"
    
    result = parse_file(test_file)
    if result:
        print(f"🎉 Successfully parsed: {result}")
    else:
        print("❌ Parse failed")
