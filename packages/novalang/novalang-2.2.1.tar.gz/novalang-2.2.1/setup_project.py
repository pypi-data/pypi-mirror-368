#!/usr/bin/env python3
"""
NovaLang Project Setup Script
Automates the setup of a complete NovaLang development environment
"""

import os
import subprocess
import sys
import json

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def create_project_structure():
    """Create the complete project directory structure"""
    directories = [
        "novalang-ecosystem",
        "novalang-ecosystem/src/core",
        "novalang-ecosystem/extensions/vscode",
        "novalang-ecosystem/extensions/language-server", 
        "novalang-ecosystem/docs",
        "novalang-ecosystem/examples",
        "novalang-ecosystem/tests",
        "novalang-ecosystem/scripts",
        "novalang-ecosystem/dist"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created directory: {directory}")

def create_package_json():
    """Create VS Code extension package.json"""
    package_json = {
        "name": "novalang",
        "displayName": "NovaLang",
        "description": "Language support for NovaLang - The Full-Stack Programming Language",
        "version": "1.0.0",
        "publisher": "martinmaboya",
        "engines": {"vscode": "^1.74.0"},
        "categories": ["Programming Languages", "Snippets", "Formatters"],
        "keywords": ["novalang", "nova", "full-stack", "enterprise"],
        "main": "./out/extension.js",
        "contributes": {
            "languages": [{
                "id": "novalang",
                "aliases": ["NovaLang", "nova"],
                "extensions": [".nova"],
                "configuration": "./language-configuration.json"
            }]
        },
        "scripts": {
            "compile": "tsc -p ./",
            "watch": "tsc -watch -p ./"
        },
        "devDependencies": {
            "@types/vscode": "^1.74.0",
            "typescript": "^4.9.4"
        }
    }
    
    with open("novalang-ecosystem/extensions/vscode/package.json", "w") as f:
        json.dump(package_json, f, indent=2)
    print("📦 Created package.json for VS Code extension")

def create_setup_py():
    """Create setup.py for PyPI distribution"""
    setup_content = '''from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="novalang",
    version="1.0.0",
    author="Martin Maboya",
    author_email="martinmaboya@gmail.com",
    description="NovaLang - The Full-Stack Programming Language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/martinmaboya/novalang",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "novalang=src.main:main",
            "nova=src.main:main",
            "novalang-lsp=extensions.language-server.novalang_lsp:main"
        ],
    },
)'''
    
    with open("novalang-ecosystem/setup.py", "w") as f:
        f.write(setup_content)
    print("🐍 Created setup.py for PyPI distribution")

def create_example_files():
    """Create example NovaLang files"""
    
    # Hello World example
    hello_content = '''// Hello World in NovaLang
print "Hello, NovaLang! 🚀"
print "Welcome to the future of full-stack development!"

// Simple function
function greet(name) {
    return "Hello, " + name + "!"
}

print greet("Developer")
'''
    
    with open("novalang-ecosystem/examples/hello.nova", "w") as f:
        f.write(hello_content)
    
    # Enterprise example
    enterprise_content = '''// NovaLang Enterprise Application Example

@Entity
class User {
    id: number
    name: string
    email: string
    
    function User(data) {
        this.id = data.id
        this.name = data.name
        this.email = data.email
    }
}

@Service
class UserService {
    function getUsers() {
        return [
            new User({id: 1, name: "John", email: "john@example.com"}),
            new User({id: 2, name: "Jane", email: "jane@example.com"})
        ]
    }
}

@Controller("/api/users")
class UserController {
    function GET index() {
        const users = UserService.getUsers()
        return {status: 200, data: users}
    }
}

@Component
class UserList {
    function render() {
        return `<div>User Management System</div>`
    }
}

@Application
class App {
    function start() {
        print "🚀 NovaLang Enterprise App started!"
    }
}

const app = new App()
app.start()
'''
    
    with open("novalang-ecosystem/examples/enterprise.nova", "w") as f:
        f.write(enterprise_content)
    
    print("📝 Created example NovaLang files")

def main():
    """Main setup function"""
    print("🚀 NovaLang Project Setup")
    print("=" * 50)
    
    # Create project structure
    create_project_structure()
    
    # Create configuration files
    create_package_json()
    create_setup_py()
    create_example_files()
    
    # Initialize git repository
    os.chdir("novalang-ecosystem")
    run_command("git init", "Initialize Git repository")
    
    # Create .gitignore
    gitignore_content = '''# Dependencies
node_modules/
__pycache__/
*.pyc

# Build outputs
dist/
build/
out/
*.vsix

# IDE files
.vscode/settings.json
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*

# Environment
.env
.env.local
'''
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    
    print("\n✅ NovaLang project setup completed!")
    print("\n📁 Project structure created in: novalang-ecosystem/")
    print("\n🚀 Next steps:")
    print("   1. cd novalang-ecosystem")
    print("   2. Copy your NovaLang source files")
    print("   3. Set up your VS Code extension")
    print("   4. Configure your Language Server")
    print("   5. Publish to PyPI and VS Code Marketplace")
    print("\n🎯 Happy coding with NovaLang!")

if __name__ == "__main__":
    main()
