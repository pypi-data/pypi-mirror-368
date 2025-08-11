"""
NovaLang Main Entry Point
Command-line interface for the NovaLang programming language.
"""

import sys
import os
from pathlib import Path

# Add src/core to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'core'))

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter


def read_file(filepath: str) -> str:
    """Read source code from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{filepath}': {e}")
        sys.exit(1)


def run_code(source: str, filename: str = "<stdin>"):
    """Run NovaLang source code."""
    try:
        # Tokenize
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Interpret
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
    except SyntaxError as e:
        print(f"Syntax Error in {filename}: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Runtime Error in {filename}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error in {filename}: {e}")
        sys.exit(1)


def run_file(filepath: str):
    """Run a NovaLang file."""
    source = read_file(filepath)
    run_code(source, filepath)


def run_repl():
    """Run the NovaLang REPL (Read-Eval-Print Loop)."""
    print("NovaLang v1.0.0 - Interactive REPL")
    print("Type 'exit' to quit, 'help' for help")
    print()
    
    interpreter = Interpreter()

    while True:
        try:
            # Multi-line input support
            lines = []
            prompt = "nova> "
            while True:
                line = input(prompt)
                if not lines and line.strip() == '':
                    continue
                if not lines and line.strip().startswith('.inject '):
                    # Runtime code injection: execute Python code in interpreter context
                    code = line.strip()[len('.inject '):]
                    try:
                        exec(code, globals(), {'interpreter': interpreter})
                        print("[Injected]")
                    except Exception as e:
                        print(f"[Injection Error] {e}")
                    break
                if line.strip() in ('exit', 'quit'):
                    return
                if line.strip() == 'help':
                    print_help()
                    break
                if line.strip() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    break
                lines.append(line)
                # End multi-line input on empty line
                if line.strip() == '':
                    break
                prompt = "...> "

            # Skip if only empty input
            if not lines or all(l.strip() == '' for l in lines):
                continue

            # Join lines and execute
            code_block = '\n'.join(lines).strip()
            if not code_block:
                continue
            try:
                lexer = Lexer(code_block)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
                for statement in ast.statements:
                    result = interpreter.evaluate(statement)
                    if (result is not None and 
                        hasattr(statement, 'expression') and 
                        not code_block.strip().endswith(';')):
                        print(f"=> {result}")
            except (SyntaxError, RuntimeError) as e:
                print(f"Error: {e}")
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Unexpected error: {e}")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


def print_help():
    """Print help information."""
    help_text = """
NovaLang Programming Language Help

USAGE:
    python main.py [file]           Run a NovaLang file
    python main.py                  Start interactive REPL

REPL COMMANDS:
    exit, quit                      Exit the REPL
    help                           Show this help
    clear                          Clear the screen

LANGUAGE FEATURES:
    Variables:     let x = 10; const y = 20;
    Functions:     function add(a, b) { return a + b; }
    Conditionals:  if (x > 5) { ... } else { ... }
    Loops:         while (condition) { ... }
    
    Data Types:    numbers, strings, booleans, null
    Operators:     +, -, *, /, %, ==, !=, <, <=, >, >=, &&, ||, !
    
BUILT-IN FUNCTIONS:
    print(...)                     Print values to console
    len(string/array)              Get length
    str(value)                     Convert to string
    num(value)                     Convert to number

EXAMPLES:
    let name = "World";
    print("Hello,", name);
    
    function factorial(n) {
        if (n <= 1) return 1;
        return n * factorial(n - 1);
    }
    
    print("5! =", factorial(5));
"""
    print(help_text)


def print_usage():
    """Print usage information."""
    print("NovaLang Programming Language")
    print()
    print("Usage:")
    print("  python main.py [file]     Run a NovaLang file")
    print("  python main.py            Start interactive REPL")
    print("  python main.py --help     Show help")
    print()


def main():
    """Main entry point."""
    args = sys.argv[1:]
    
    if len(args) == 0:
        # No arguments - start REPL
        run_repl()
    elif len(args) == 1:
        arg = args[0]
        if arg in ('--help', '-h', 'help'):
            print_usage()
            print_help()
        elif arg in ('--version', '-v', 'version'):
            print("NovaLang v1.0.2")
            print("Premium features available with license")
            print("Get premium: https://premium.novalang.dev")
            print("License management: novalang-license --help")
        elif arg == 'serve':
            # Serve API endpoints from main.nova
            filename = 'main.nova'
            if not os.path.exists(filename):
                print(f"Error: File '{filename}' not found")
                sys.exit(1)
            source = read_file(filename)
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            interpreter = Interpreter()
            interpreter.run_api_server(ast)
        elif arg == 'deploy':
            print("[nova deploy] Deployment tool coming soon! This will let you deploy NovaLang apps to the cloud.")
            sys.exit(0)
        elif arg == 'install':
            print("[nova install] Package manager coming soon! This will let you install NovaLang packages from the ecosystem.")
            sys.exit(0)
        elif arg.startswith('-'):
            print(f"Unknown option: {arg}")
            print_usage()
            sys.exit(1)
        else:
            # Run file
            if not os.path.exists(arg):
                print(f"Error: File '{arg}' not found")
                sys.exit(1)
            run_file(arg)
    else:
        print("Error: Too many arguments")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
