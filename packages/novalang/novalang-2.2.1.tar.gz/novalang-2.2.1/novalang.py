#!/usr/bin/env python3
"""
NovaLang - The Full-Stack Programming Language
Main entry point for the NovaLang interpreter
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.interpreter import NovaInterpreter

def main():
    """Main entry point for NovaLang"""
    if len(sys.argv) != 2:
        print("Usage: python novalang.py <file.nova>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    
    interpreter = NovaInterpreter()
    interpreter.run_file(file_path)

if __name__ == "__main__":
    main()
