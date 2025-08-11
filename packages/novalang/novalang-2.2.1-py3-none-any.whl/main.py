#!/usr/bin/env python3
"""
NovaLang E-commerce Backend - Main Entry Point

This is the main Python file that bootstraps the NovaLang application.
It handles compilation, execution, and runtime management of .nova files.
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from typing import Optional, List

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import NovaLang components
try:
    from lexer import NovaLangLexer as NovaLexer
    from parser import NovaLangParser as NovaParser  
    from src.core.interpreter import Interpreter as NovaInterpreter
except ImportError:
    # Fallback to core modules
    try:
        from src.core.lexer import Lexer as NovaLexer
        from src.core.parser import Parser as NovaParser
        from src.core.interpreter import Interpreter as NovaInterpreter
    except ImportError:
        # Final fallback - create mock classes for demonstration
        print("Warning: Using mock classes for demonstration")
        
        class NovaLexer:
            def tokenize(self, code): return []
            
        class NovaParser:
            def parse(self, tokens): return type('AST', (), {'statements': []})()
            
        class NovaInterpreter:
            def execute_main(self, module): return True
            def execute_tests(self, module): return True
            def evaluate(self, statement): return None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NovaLangApplication:
    """Main application class for NovaLang backend"""
    
    def __init__(self):
        self.lexer = NovaLexer()
        self.parser = NovaParser()
        self.interpreter = NovaInterpreter()
        self.project_root = project_root
        
    def run_application(self, entry_point: Optional[str] = None) -> int:
        """
        Run the NovaLang application
        
        Args:
            entry_point: Path to the main .nova file (defaults to Application.nova)
            
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        try:
            # Determine entry point
            if entry_point is None:
                entry_point = self.project_root / "src" / "main" / "nova" / "Application.nova"
            else:
                entry_point = Path(entry_point)
            
            if not entry_point.exists():
                logger.error(f"Entry point not found: {entry_point}")
                # Fallback to REPL mode
                logger.info("Falling back to REPL mode...")
                return self.run_repl()
            
            logger.info("🚀 Starting NovaLang E-commerce Backend...")
            logger.info(f"📂 Project root: {self.project_root}")
            logger.info(f"🎯 Entry point: {entry_point}")
            
            # Compile and run the application
            return self._compile_and_run(entry_point)
            
        except Exception as e:
            logger.error(f"❌ Application failed to start: {e}")
            return 1
    
    def _compile_and_run(self, entry_point: Path) -> int:
        """Compile and execute the NovaLang application"""
        
        # Step 1: Discover all .nova source files
        source_files = self._discover_source_files()
        logger.info(f"📁 Found {len(source_files)} .nova source files")
        
        # Step 2: Compile all source files
        compiled_modules = {}
        for source_file in source_files:
            try:
                module = self._compile_file(source_file)
                compiled_modules[source_file] = module
                logger.debug(f"✅ Compiled: {source_file}")
            except Exception as e:
                logger.error(f"❌ Failed to compile {source_file}: {e}")
                return 1
        
        # Step 3: Execute the main application
        try:
            main_module = compiled_modules[entry_point]
            logger.info("🎬 Executing main application...")
            
            # Execute the main class
            result = self.interpreter.execute_main(main_module)
            
            if result:
                logger.info("✅ Application executed successfully")
                return 0
            else:
                logger.error("❌ Application execution failed")
                return 1
                
        except Exception as e:
            logger.error(f"❌ Runtime error: {e}")
            return 1
    
    def _discover_source_files(self) -> List[Path]:
        """Discover all .nova source files in the project"""
        source_files = []
        
        # Search in src/main/nova directory
        src_dir = self.project_root / "src" / "main" / "nova"
        if src_dir.exists():
            source_files.extend(src_dir.rglob("*.nova"))
        
        # Sort files to ensure deterministic compilation order
        source_files.sort()
        
        return source_files
    
    def _compile_file(self, file_path: Path) -> dict:
        """Compile a single .nova file"""
        
        # Read source code
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Lexical analysis
        if hasattr(self.lexer, 'tokenize'):
            tokens = self.lexer.tokenize(source_code)
        else:
            # Fallback for original lexer
            lexer = NovaLexer(source_code)
            tokens = lexer.tokenize()
        
        # Syntactic analysis  
        if hasattr(self.parser, 'parse'):
            ast = self.parser.parse(tokens)
        else:
            # Fallback for original parser
            parser = NovaParser(tokens)
            ast = parser.parse()
        
        # Return compiled module
        return {
            'file_path': file_path,
            'source_code': source_code,
            'tokens': tokens,
            'ast': ast,
            'metadata': {
                'compiled_at': __import__('datetime').datetime.now(),
                'file_size': len(source_code),
                'token_count': len(tokens) if hasattr(tokens, '__len__') else 0
            }
        }
    
    def build_project(self) -> int:
        """Build the project (compile all .nova files)"""
        try:
            logger.info("🔨 Building NovaLang project...")
            
            source_files = self._discover_source_files()
            
            for source_file in source_files:
                self._compile_file(source_file)
                logger.info(f"✅ Built: {source_file.relative_to(self.project_root)}")
            
            logger.info(f"✅ Build completed successfully! ({len(source_files)} files)")
            return 0
            
        except Exception as e:
            logger.error(f"❌ Build failed: {e}")
            return 1
    
    def run_tests(self) -> int:
        """Run project tests"""
        try:
            logger.info("🧪 Running tests...")
            
            # Discover test files
            test_dir = self.project_root / "src" / "test" / "nova"
            if not test_dir.exists():
                logger.warning("No test directory found")
                return 0
            
            test_files = list(test_dir.rglob("*Test.nova"))
            
            if not test_files:
                logger.warning("No test files found")
                return 0
            
            # Run each test file
            failed_tests = 0
            for test_file in test_files:
                try:
                    module = self._compile_file(test_file)
                    result = self.interpreter.execute_tests(module)
                    
                    if result:
                        logger.info(f"✅ {test_file.name}")
                    else:
                        logger.error(f"❌ {test_file.name}")
                        failed_tests += 1
                        
                except Exception as e:
                    logger.error(f"❌ {test_file.name}: {e}")
                    failed_tests += 1
            
            total_tests = len(test_files)
            passed_tests = total_tests - failed_tests
            
            logger.info(f"🧪 Test Results: {passed_tests}/{total_tests} passed")
            
            return 0 if failed_tests == 0 else 1
            
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            return 1
    
    def clean_project(self) -> int:
        """Clean build artifacts"""
        try:
            logger.info("🧹 Cleaning project...")
            
            # Clean build directories
            build_dirs = [
                self.project_root / "build",
                self.project_root / "target",
                self.project_root / "dist",
                self.project_root / "__pycache__"
            ]
            
            cleaned_count = 0
            for build_dir in build_dirs:
                if build_dir.exists():
                    import shutil
                    shutil.rmtree(build_dir)
                    cleaned_count += 1
                    logger.info(f"🗑️  Removed: {build_dir}")
            
            logger.info(f"✅ Clean completed! ({cleaned_count} directories removed)")
            return 0
            
        except Exception as e:
            logger.error(f"❌ Clean failed: {e}")
            return 1
    
    def run_repl(self) -> int:
        """Run the NovaLang REPL (Read-Eval-Print Loop)."""
        print("NovaLang v2.0.0 - E-commerce Backend")
        print("Type 'exit' to quit, 'help' for help")
        print()

        while True:
            try:
                # Multi-line input support
                lines = []
                prompt = "nova> "
                while True:
                    line = input(prompt)
                    if not lines and line.strip() == '':
                        continue
                    if line.strip() in ('exit', 'quit'):
                        return 0
                    if line.strip() == 'help':
                        self.print_help()
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
                    if hasattr(self.lexer, 'tokenize'):
                        tokens = self.lexer.tokenize(code_block)
                    else:
                        lexer = NovaLexer(code_block)
                        tokens = lexer.tokenize()
                        
                    if hasattr(self.parser, 'parse'):
                        ast = self.parser.parse(tokens)
                    else:
                        parser = NovaParser(tokens)
                        ast = parser.parse()
                        
                    for statement in ast.statements:
                        result = self.interpreter.evaluate(statement)
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

    def print_help(self):
        """Print help information."""
        help_text = """
NovaLang E-commerce Backend Help

USAGE:
    python main.py [options]         Run with options
    python main.py [file]           Run a specific .nova file
    python main.py                  Start application or REPL

COMMANDS:
    --build                         Build the project
    --test                          Run tests
    --clean                         Clean build artifacts
    --file FILE                     Run specific file
    --port PORT                     Set server port (default: 8080)

BACKEND FEATURES:
    Multi-database support          MySQL, MongoDB, Redis
    RESTful APIs                    Full CRUD operations
    Security                        JWT authentication
    Caching                         Redis-based caching
    Testing                         Unit and integration tests

EXAMPLES:
    python main.py --build          # Build project
    python main.py --test           # Run tests
    python main.py --file app.nova  # Run specific file
"""
        print(help_text)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="NovaLang E-commerce Backend Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Run the application
  python main.py --build                           # Build the project
  python main.py --test                            # Run tests
  python main.py --clean                           # Clean build artifacts
  python main.py --file src/main/nova/Custom.nova  # Run specific file
        """
    )
    
    parser.add_argument(
        '--build',
        action='store_true',
        help='Build the project (compile all .nova files)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run project tests'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean build artifacts'
    )
    
    parser.add_argument(
        '--file',
        type=str,
        help='Specific .nova file to run (defaults to Application.nova)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Server port (default: 8080)'
    )
    
    # Handle legacy arguments (single file without --file flag)
    args, unknown = parser.parse_known_args()
    
    if unknown and len(unknown) == 1 and not unknown[0].startswith('-'):
        args.file = unknown[0]
    elif unknown:
        parser.error(f"Unknown arguments: {unknown}")
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Set environment variables
    os.environ['SERVER_PORT'] = str(args.port)
    
    # Create application instance
    app = NovaLangApplication()
    
    # Execute requested action
    try:
        if args.build:
            return app.build_project()
        elif args.test:
            return app.run_tests()
        elif args.clean:
            return app.clean_project()
        else:
            return app.run_application(args.file)
            
    except KeyboardInterrupt:
        logger.info("🛑 Application interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
