#!/usr/bin/env python3
"""
Fix NovaLang Language Detection in VS Code
Ensures .nova files are recognized as NovaLang, not JavaScript/TypeScript
"""

import json
import os
from pathlib import Path

def create_vscode_settings():
    """Create VS Code workspace settings to force NovaLang recognition"""
    
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    settings = {
        "files.associations": {
            "*.nova": "novalang"
        },
        "editor.detectIndentation": False,
        "editor.tabSize": 4,
        "editor.insertSpaces": True,
        "editor.defaultFormatter": "martinmaboya.novalang",
        "novalang.enableDiagnostics": True,
        "novalang.enableAutoFormat": True,
        "[novalang]": {
            "editor.defaultFormatter": "martinmaboya.novalang",
            "editor.formatOnSave": True,
            "editor.semanticHighlighting.enabled": True
        },
        "typescript.validate.enable": False,
        "javascript.validate.enable": False,
        "extensions.ignoreRecommendations": False
    }
    
    settings_file = vscode_dir / "settings.json"
    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)
    
    print(f"✅ Created VS Code settings: {settings_file}")
    return settings_file

def check_extension_status():
    """Check NovaLang extension status"""
    
    import subprocess
    
    try:
        result = subprocess.run(
            ["code", "--list-extensions"], 
            capture_output=True, 
            text=True
        )
        
        extensions = result.stdout.split('\\n')
        novalang_extensions = [ext for ext in extensions if 'novalang' in ext.lower()]
        
        print("🔍 NovaLang Extensions Found:")
        for ext in novalang_extensions:
            if ext.strip():
                print(f"   ✅ {ext}")
        
        if not novalang_extensions:
            print("❌ No NovaLang extensions found!")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking extensions: {e}")
        return False

def fix_language_detection():
    """Fix language detection issues"""
    
    print("🔧 Fixing NovaLang Language Detection...")
    
    # Step 1: Create workspace settings
    settings_file = create_vscode_settings()
    
    # Step 2: Check extension status
    extension_ok = check_extension_status()
    
    if not extension_ok:
        print("❌ Extension not found. Please reinstall:")
        print("   cd extensions/vscode")
        print("   code --install-extension novalang-1.0.0.vsix")
        return False
    
    # Step 3: Instructions for user
    print("\\n🎯 Next Steps:")
    print("1. ✅ VS Code settings created")
    print("2. 🔄 Reload VS Code window (Ctrl+Shift+P -> 'Reload Window')")
    print("3. 📝 Open your .nova file")
    print("4. 👀 Check bottom-right corner - should show 'NovaLang'")
    print("5. 🎨 If still JavaScript, click and select 'NovaLang' manually")
    
    print("\\n💡 Manual Override:")
    print("   - Click language indicator (bottom-right)")
    print("   - Type 'NovaLang' or 'Configure File Association'")
    print("   - Select 'NovaLang' from the list")
    
    return True

def create_test_commands():
    """Create VS Code tasks for testing"""
    
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    tasks = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Test NovaLang Extension",
                "type": "shell",
                "command": "python",
                "args": ["scripts/test_lsp.py"],
                "group": "test",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "new"
                },
                "problemMatcher": []
            },
            {
                "label": "Start NovaLang LSP Server",
                "type": "shell",
                "command": "python",
                "args": ["extensions/language-server/novalang_lsp.py"],
                "group": "build",
                "isBackground": True,
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "new"
                },
                "problemMatcher": []
            },
            {
                "label": "Run NovaLang File",
                "type": "shell",
                "command": "python",
                "args": ["main.py", "${file}"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "new"
                }
            }
        ]
    }
    
    tasks_file = vscode_dir / "tasks.json"
    with open(tasks_file, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=4)
    
    print(f"✅ Created VS Code tasks: {tasks_file}")

def main():
    """Main function"""
    
    print("🚀 NovaLang Language Detection Fix")
    print("=" * 50)
    
    # Change to project root
    os.chdir(Path(__file__).parent.parent)
    
    # Fix language detection
    if fix_language_detection():
        # Create additional VS Code configuration
        create_test_commands()
        
        print("\\n" + "=" * 50)
        print("🎉 Fix Applied Successfully!")
        print("\\n📋 Summary:")
        print("   ✅ VS Code workspace settings created")
        print("   ✅ File associations configured")
        print("   ✅ NovaLang extension verified")
        print("   ✅ Test tasks created")
        print("\\n🔄 Now reload VS Code and test your .nova files!")
    else:
        print("\\n❌ Fix failed. Please check the extension installation.")

if __name__ == "__main__":
    main()
