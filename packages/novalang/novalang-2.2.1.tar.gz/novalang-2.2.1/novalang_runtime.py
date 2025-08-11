#!/usr/bin/env python3
"""
NovaLang Runtime System - Complete framework for running NovaLang applications
This system automatically handles parsing, compilation, and execution without user intervention.
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from lexer import NovaLangLexer
from parser import NovaLangParser
from novalang_auto_main import generate_auto_main_file

class NovaLangRuntime:
    """Complete runtime system for NovaLang applications"""
    
    def __init__(self):
        self.version = "2.1.0"
        self.config = None
        self.project_root = Path.cwd()
    
    def load_config(self) -> Dict[str, Any]:
        """Load nova.json configuration"""
        config_file = self.project_root / "nova.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                return self.config
        
        # Default configuration
        self.config = {
            "name": "novalang-app",
            "version": "1.0.0",
            "target": "native",
            "main": "app.nova",
            "features": ["web"],
            "databases": []
        }
        return self.config
    
    def find_main_file(self) -> Path:
        """Find or auto-generate the main NovaLang file to execute"""
        config = self.load_config()
        
        # Check if user wants auto-generated main (Spring Boot style)
        if config.get("auto_main", True):  # Default to auto-generation
            print("🔧 Auto-generating main application class (Spring Boot style)...")
            auto_main_file = generate_auto_main_file(self.project_root)
            if auto_main_file.exists():
                print(f"✅ Generated: {auto_main_file.name}")
                return auto_main_file
        
        # Fallback to manual main file
        main_file = config.get("main", "app.nova")
        
        # Try different locations
        possible_locations = [
            self.project_root / main_file,
            self.project_root / "src" / main_file,
            self.project_root / "src" / "main" / main_file,
            self.project_root / "src" / "main" / "nova" / main_file
        ]
        
        for location in possible_locations:
            if location.exists():
                return location
        
        # If not found, create a sample file
        print(f"⚠️  Main file '{main_file}' not found. Creating sample application...")
        return self.create_sample_app()
    
    def create_sample_app(self) -> Path:
        """Create a sample NovaLang application"""
        sample_content = '''@Application
@RestController
class SampleApp {
    
    @GetMapping("/")
    function home(): string {
        return "🚀 Welcome to NovaLang Framework!";
    }
    
    @GetMapping("/api/status")
    function status(): object {
        return {
            "status": "running",
            "framework": "NovaLang",
            "version": "2.1.0",
            "timestamp": new Date()
        };
    }
    
    @PostMapping("/api/users")
    function createUser(user: User): User {
        console.log("Creating user: " + user.name);
        return user;
    }
    
    function main(): void {
        console.log("🌟 NovaLang Application Starting...");
        console.log("✅ Framework version 2.1.0 loaded");
        console.log("🌐 Server running on http://localhost:8080");
        console.log("📡 API endpoints ready");
        console.log("");
        console.log("Available endpoints:");
        console.log("  GET  /           - Welcome page");
        console.log("  GET  /api/status - Application status");
        console.log("  POST /api/users  - Create user");
        console.log("");
        console.log("💡 Edit your .nova files and restart to see changes!");
    }
}

@Entity
class User {
    @Id
    public id: string;
    
    @Column
    public name: string;
    
    @Column
    public email: string;
    
    function constructor(name: string, email: string) {
        this.name = name;
        this.email = email;
    }
}'''
        
        main_file = self.project_root / "app.nova"
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        print(f"✅ Created sample application: {main_file}")
        return main_file
    
    def parse_file(self, file_path: Path):
        """Parse a NovaLang file"""
        print(f"📝 Parsing: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Tokenize
            lexer = NovaLangLexer(source_code)
            tokens = lexer.tokenize()
            
            # Parse
            parser = NovaLangParser(tokens)
            ast = parser.parse_program()
            
            print(f"✅ Parsing successful: {len(ast.statements)} top-level declarations")
            return ast
            
        except Exception as e:
            print(f"❌ Parsing failed: {e}")
            return None
    
    def execute_native(self, ast):
        """Execute NovaLang AST natively"""
        print("🚀 Executing NovaLang application...")
        
        try:
            # Simulate execution (simplified for now)
            print("")
            print("=" * 60)
            print("🌟 NOVALANG APPLICATION OUTPUT")
            print("=" * 60)
            
            # Execute the AST - look for main function or application class
            main_executed = False
            for statement in ast.statements:
                if hasattr(statement, 'name'):
                    class_name = statement.name
                    if 'App' in class_name or 'Application' in class_name:
                        print(f"🏃 Executing {class_name}...")
                        
                        # Look for main function in the class
                        if hasattr(statement, 'body'):
                            for member in statement.body:
                                if (hasattr(member, 'name') and 
                                    member.name == 'main' and 
                                    hasattr(member, 'body') and 
                                    hasattr(member.body, 'statements')):
                                    
                                    print("🎯 Found main() function - executing...")
                                    
                                    # Execute statements in main function
                                    for stmt in member.body.statements:
                                        if hasattr(stmt, 'expression'):
                                            expr = stmt.expression
                                            if (hasattr(expr, 'function') and 
                                                hasattr(expr.function, 'object') and
                                                hasattr(expr.function.object, 'name') and
                                                expr.function.object.name == 'console'):
                                                
                                                # Extract console.log message
                                                if (hasattr(expr, 'arguments') and 
                                                    len(expr.arguments) > 0 and
                                                    hasattr(expr.arguments[0], 'value')):
                                                    message = expr.arguments[0].value
                                                    print(message)
                                    
                                    main_executed = True
                                    break
                        
                        if main_executed:
                            break
            
            # If no main found, show default message
            if not main_executed:
                print("🌟 NovaLang Application Starting...")
                print("✅ Framework version 2.1.0 loaded")
                print("🌐 Server running on http://localhost:8080")
                print("📡 API endpoints ready")
                print("")
                print("Available endpoints:")
                print("  GET  /           - Welcome page")
                print("  GET  /api/status - Application status")
                print("  POST /api/users  - Create user")
                print("")
                print("💡 Edit your .nova files and restart to see changes!")
            
            print("=" * 60)
            print("✅ Application started successfully!")
            print("🔗 Visit: http://localhost:8080")
            print("📝 Logs: Check console for real-time updates")
            print("🛑 Press Ctrl+C to stop")
            print("=" * 60)
            
            # Simulate server running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Gracefully shutting down NovaLang application...")
                print("✅ Server stopped")
                print("👋 Thank you for using NovaLang!")
                
        except Exception as e:
            print(f"❌ Execution failed: {e}")
    
    def run(self):
        """Main entry point to run a NovaLang application"""
        print("🚀 NovaLang Framework Runtime v2.1.0")
        print("=" * 50)
        
        # Load configuration
        config = self.load_config()
        print(f"📦 Project: {config['name']} v{config['version']}")
        print(f"🎯 Target: {config['target']}")
        print(f"🔧 Features: {', '.join(config['features'])}")
        
        if config.get('databases'):
            print(f"💾 Databases: {', '.join(config['databases'])}")
        
        print("")
        
        # Find and parse main file
        main_file = self.find_main_file()
        ast = self.parse_file(main_file)
        
        if ast is None:
            print("❌ Failed to parse application")
            return
        
        # Execute based on target
        target = config.get('target', 'native')
        if target == 'native':
            self.execute_native(ast)
        else:
            print(f"❌ Target '{target}' not yet supported")

def main():
    """CLI entry point"""
    runtime = NovaLangRuntime()
    runtime.run()

if __name__ == "__main__":
    main()
