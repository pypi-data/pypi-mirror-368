#!/usr/bin/env python3
"""
Test specific NovaLang constructs that are failing
"""

from lexer import NovaLangLexer
from parser import NovaLangParser
import traceback

def test_constructs():
    """Test various NovaLang constructs"""
    
    tests = [
        # Test 1: Simple class with method
        ("Simple class", '''
@Component
class SimpleService {
    
    function hello(): void {
        console.log("Hello World");
    }
}'''),
        
        # Test 2: Method with parameters  
        ("Method with params", '''
@Service
class UserService {
    
    function getUser(id: string): User {
        return new User(id);
    }
}'''),
        
        # Test 3: Array syntax
        ("Array syntax", '''
@Component
class DataService {
    
    function getUsers(): User[] {
        return [new User("1"), new User("2")];
    }
}'''),
        
        # Test 4: Generic types
        ("Generic types", '''
@Service
class Repository<T> {
    
    function findAll(): T[] {
        return [];
    }
}'''),
    ]
    
    for test_name, code in tests:
        print(f"\n🔍 Testing: {test_name}")
        print("=" * 50)
        
        try:
            lexer = NovaLangLexer(code)
            tokens = lexer.tokenize()
            
            parser = NovaLangParser(tokens)
            ast = parser.parse_program()
            
            print(f"✅ {test_name} - SUCCESS")
            
        except Exception as e:
            print(f"❌ {test_name} - FAILED: {e}")
            # Print some context
            if hasattr(e, '__traceback__'):
                traceback.print_exc()

if __name__ == "__main__":
    test_constructs()
