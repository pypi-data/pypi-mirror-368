#!/usr/bin/env python3
"""
NovaLang Setup for IntelliJ IDEA and NetBeans
Generates configuration files and instructions for JetBrains and Apache IDEs
"""

import os
import json
from pathlib import Path

def create_intellij_config():
    """Create IntelliJ IDEA configuration"""
    
    # Get absolute path to LSP server
    lsp_path = Path(__file__).parent.parent / "extensions" / "language-server" / "novalang_lsp.py"
    
    config = {
        "intellij_lsp_settings": {
            "servers": [
                {
                    "name": "NovaLang Language Server",
                    "extension": "nova",
                    "command": "python",
                    "args": [str(lsp_path.absolute())],
                    "scope": "project"
                }
            ]
        },
        
        "file_type_mapping": {
            "nova": {
                "description": "NovaLang Source Files",
                "extensions": ["nova"],
                "syntax_highlighter": "JavaScript",  # Fallback until custom highlighter
                "icon": "FileTypes.JavaScript"
            }
        },
        
        "live_templates": {
            "NovaLang": {
                "comp": {
                    "template": "@Component\nclass $CLASS_NAME$ {\n    state = {\n        $STATE$\n    }\n    \n    function render($PROPS$) {\n        return `$TEMPLATE$`\n    }\n}",
                    "description": "NovaLang Component",
                    "variables": {
                        "CLASS_NAME": "componentName()",
                        "STATE": "\"// component state\"",
                        "PROPS": "\"props\"",
                        "TEMPLATE": "\"<div>Component content</div>\""
                    }
                },
                "svc": {
                    "template": "@Service\nclass $SERVICE_NAME$ {\n    \n    function $METHOD_NAME$($PARAMS$) {\n        print \"⚙️ $SERVICE_NAME$.$METHOD_NAME$()\"\n        $BODY$\n    }\n}",
                    "description": "NovaLang Service",
                    "variables": {
                        "SERVICE_NAME": "className()",
                        "METHOD_NAME": "\"processData\"",
                        "PARAMS": "\"data\"",
                        "BODY": "\"// business logic\""
                    }
                }
            }
        }
    }
    
    return config

def create_netbeans_config():
    """Create NetBeans configuration"""
    
    lsp_path = Path(__file__).parent.parent / "extensions" / "language-server" / "novalang_lsp.py"
    
    config = {
        "language_servers": {
            "novalang": {
                "command": ["python", str(lsp_path.absolute())],
                "extensions": ["nova"],
                "mimeType": "text/x-novalang",
                "displayName": "NovaLang"
            }
        },
        
        "mime_type_registration": {
            "mimeType": "text/x-novalang",
            "extension": "nova",
            "displayName": "NovaLang Source",
            "iconBase": "org/netbeans/modules/languages/javascript/javascript.png"
        },
        
        "syntax_highlighting": {
            "lexer": "JavaScript",  # Fallback
            "colorings": {
                "keyword": {"color": "#CC7832"},
                "string": {"color": "#6A8759"},
                "comment": {"color": "#808080"},
                "decorator": {"color": "#FFC66D"}
            }
        },
        
        "code_templates": {
            "comp": "@Component\nclass ${cursor} {\n    state = {}\n    \n    function render(props) {\n        return `<div></div>`\n    }\n}",
            "svc": "@Service\nclass ${cursor} {\n    \n    function processData(data) {\n        // business logic\n    }\n}"
        }
    }
    
    return config

def generate_setup_instructions():
    """Generate setup instructions for both IDEs"""
    
    instructions = {
        "intellij": [
            "1. Install LSP Support Plugin:",
            "   - File -> Settings -> Plugins",
            "   - Search for 'LSP Support' by gtache",
            "   - Install and restart IntelliJ",
            "",
            "2. Configure NovaLang LSP:",
            "   - File -> Settings -> Languages & Frameworks -> Language Server Protocol",
            "   - Click '+' to add new server",
            "   - Extension: nova",
            f"   - Path: python",
            f"   - Args: {Path(__file__).parent.parent / 'extensions' / 'language-server' / 'novalang_lsp.py'}",
            "",
            "3. Configure File Types:",
            "   - File -> Settings -> Editor -> File Types",
            "   - Add '*.nova' pattern to JavaScript or create new type",
            "",
            "4. Test:",
            "   - Open a .nova file",
            "   - Type '@' to see completions",
            "   - Hover over keywords for documentation"
        ],
        
        "netbeans": [
            "1. Ensure NetBeans 12+ (has built-in LSP support):",
            "   - Download from https://netbeans.apache.org/",
            "",
            "2. Configure Language Server:",
            "   - Tools -> Options -> Editor -> Language Servers",
            "   - Click 'Add'",
            "   - Language Server: Custom",
            "   - File Extensions: nova",
            "   - Command: python",
            f"   - Arguments: {Path(__file__).parent.parent / 'extensions' / 'language-server' / 'novalang_lsp.py'}",
            "",
            "3. Configure File Association:",
            "   - Tools -> Options -> Advanced Options -> System -> Object Types",
            "   - Add nova extension mapping",
            "",
            "4. Test:",
            "   - Open a .nova file",
            "   - Check for syntax highlighting and completions"
        ]
    }
    
    return instructions

def create_test_files():
    """Create test files for IDE validation"""
    
    test_files = {
        "simple_test.nova": '''// Simple NovaLang Test for IDE
@Component
class HelloWorld {
    state = { message: "Hello from IntelliJ/NetBeans!" }
    
    function render(props) {
        return `<h1>${this.state.message}</h1>`
    }
}

@Service  
class TestService {
    function greet(name) {
        print "👋 Hello", name
        return "Greeting sent!"
    }
}

// Test the setup
const component = new HelloWorld()
const service = new TestService()
service.greet("Developer")''',

        "completion_test.nova": '''// Test Code Completion
// Type '@' below to test decorator completion:


// Type 'comp' below and press Tab for component snippet:


// Type 'svc' below and press Tab for service snippet:


// Hover over 'print' to test hover documentation:
print "Testing hover docs"

// This should show error diagnostics:
class ServiceWithoutDecorator {
    function doSomething() {
        return "missing @Service decorator"
    }
}'''
    }
    
    return test_files

def main():
    """Generate all configuration files and instructions"""
    
    print("🚀 Generating NovaLang Configuration for IntelliJ IDEA and NetBeans...")
    
    # Create configurations
    intellij_config = create_intellij_config()
    netbeans_config = create_netbeans_config()
    instructions = generate_setup_instructions()
    test_files = create_test_files()
    
    # Output directory
    output_dir = Path("ide_configs")
    output_dir.mkdir(exist_ok=True)
    
    # Save IntelliJ config
    with open(output_dir / "intellij_config.json", "w") as f:
        json.dump(intellij_config, f, indent=2)
    
    # Save NetBeans config  
    with open(output_dir / "netbeans_config.json", "w") as f:
        json.dump(netbeans_config, f, indent=2)
    
    # Save setup instructions
    with open(output_dir / "INTELLIJ_SETUP.md", "w", encoding='utf-8') as f:
        f.write("# IntelliJ IDEA Setup for NovaLang\n\n")
        f.write("\n".join(instructions["intellij"]))
    
    with open(output_dir / "NETBEANS_SETUP.md", "w", encoding='utf-8') as f:
        f.write("# NetBeans Setup for NovaLang\n\n")
        f.write("\n".join(instructions["netbeans"]))
    
    # Save test files
    for filename, content in test_files.items():
        with open(output_dir / filename, "w", encoding='utf-8') as f:
            f.write(content)
    
    print("✅ Configuration files generated in 'ide_configs/' directory:")
    print("   📁 intellij_config.json - IntelliJ IDEA configuration")
    print("   📁 netbeans_config.json - NetBeans configuration") 
    print("   📁 INTELLIJ_SETUP.md - Step-by-step IntelliJ setup")
    print("   📁 NETBEANS_SETUP.md - Step-by-step NetBeans setup")
    print("   📁 simple_test.nova - Basic test file")
    print("   📁 completion_test.nova - Code completion test file")
    print("")
    print("🎯 Next Steps:")
    print("   1. Follow the setup instructions for your IDE")
    print("   2. Test with the provided .nova files")
    print("   3. Enjoy NovaLang development in IntelliJ/NetBeans!")
    print("")
    print("💡 Pro Tip: Our LSP server works with ANY LSP-compatible IDE!")

if __name__ == "__main__":
    main()
