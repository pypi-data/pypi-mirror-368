#!/usr/bin/env python3
"""
NovaLang Extension Setup and Testing Script
Installs VS Code extension and tests LSP server functionality
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=shell, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    success, stdout, stderr = run_command("python --version")
    if success:
        print(f"✅ Python: {stdout.strip()}")
    else:
        print("❌ Python not found. Please install Python 3.7+")
        return False
    
    # Check Node.js
    success, stdout, stderr = run_command("node --version")
    if success:
        print(f"✅ Node.js: {stdout.strip()}")
    else:
        print("❌ Node.js not found. Please install Node.js 16+")
        return False
    
    # Check npm
    success, stdout, stderr = run_command("npm --version")
    if success:
        print(f"✅ npm: {stdout.strip()}")
    else:
        print("❌ npm not found. Please install npm")
        return False
    
    # Check VS Code
    success, stdout, stderr = run_command("code --version")
    if success:
        print(f"✅ VS Code: {stdout.strip().split()[0]}")
    else:
        print("❌ VS Code not found. Please install VS Code and add to PATH")
        return False
    
    return True

def setup_vscode_extension():
    """Set up the VS Code extension"""
    print("\n🔧 Setting up VS Code extension...")
    
    vscode_dir = Path("extensions/vscode")
    
    if not vscode_dir.exists():
        print("❌ VS Code extension directory not found")
        return False
    
    # Install dependencies
    print("📦 Installing npm dependencies...")
    success, stdout, stderr = run_command("npm install", cwd=vscode_dir)
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    
    # Install vsce if not available
    print("📦 Installing vsce (VS Code Extension Manager)...")
    success, stdout, stderr = run_command("npm install -g vsce")
    if not success:
        print("⚠️ Could not install vsce globally, trying local install...")
        success, stdout, stderr = run_command("npm install vsce", cwd=vscode_dir)
    
    # Compile TypeScript
    print("🔨 Compiling TypeScript...")
    success, stdout, stderr = run_command("npm run compile", cwd=vscode_dir)
    if not success:
        print(f"❌ Failed to compile TypeScript: {stderr}")
        return False
    
    print("✅ VS Code extension setup complete")
    return True

def test_lsp_server():
    """Test the LSP server directly"""
    print("\n🧪 Testing LSP server...")
    
    lsp_script = Path("extensions/language-server/novalang_lsp.py")
    
    if not lsp_script.exists():
        print("❌ LSP server script not found")
        return False
    
    # Test LSP server initialization
    print("🔄 Testing LSP server startup...")
    
    # Create a simple test
    test_message = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "processId": None,
            "rootUri": None,
            "capabilities": {}
        }
    }
    
    content = json.dumps(test_message)
    message = f"Content-Length: {len(content)}\\r\\n\\r\\n{content}"
    
    # Test if the LSP server can start
    try:
        import subprocess
        import signal
        
        # Start LSP server process
        proc = subprocess.Popen(
            ["python", str(lsp_script)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send initialize message
        proc.stdin.write(message)
        proc.stdin.flush()
        
        # Wait a bit for response
        time.sleep(2)
        
        # Terminate the process
        proc.terminate()
        
        print("✅ LSP server started and responded successfully")
        return True
        
    except Exception as e:
        print(f"❌ LSP server test failed: {e}")
        return False

def package_extension():
    """Package the VS Code extension"""
    print("\n📦 Packaging VS Code extension...")
    
    vscode_dir = Path("extensions/vscode")
    
    # Package extension
    success, stdout, stderr = run_command("npx vsce package", cwd=vscode_dir)
    if not success:
        print(f"❌ Failed to package extension: {stderr}")
        return False
    
    # Find the generated .vsix file
    vsix_files = list(vscode_dir.glob("*.vsix"))
    if vsix_files:
        vsix_file = vsix_files[0]
        print(f"✅ Extension packaged: {vsix_file}")
        return str(vsix_file)
    else:
        print("❌ No .vsix file found after packaging")
        return None

def install_extension(vsix_path):
    """Install the extension in VS Code"""
    print(f"\n📥 Installing extension from {vsix_path}...")
    
    success, stdout, stderr = run_command(f"code --install-extension {vsix_path}")
    if success:
        print("✅ Extension installed successfully")
        return True
    else:
        print(f"❌ Failed to install extension: {stderr}")
        return False

def open_test_file():
    """Open the test NovaLang file in VS Code"""
    print("\n🚀 Opening test file in VS Code...")
    
    test_file = Path("test_lsp.nova")
    if test_file.exists():
        success, stdout, stderr = run_command(f"code {test_file}")
        if success:
            print("✅ Test file opened in VS Code")
            print("\n🎯 You should now see:")
            print("   • Syntax highlighting for NovaLang")
            print("   • Code completion when typing '@' or keywords")
            print("   • Hover documentation on keywords")
            print("   • Error diagnostics in the Problems panel")
            print("   • Right-click context menu with NovaLang commands")
            return True
        else:
            print(f"❌ Failed to open test file: {stderr}")
            return False
    else:
        print("❌ Test file not found")
        return False

def main():
    """Main setup function"""
    print("🚀 NovaLang Extension Setup and Testing")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\\n❌ Prerequisites check failed. Please install missing requirements.")
        return 1
    
    # Setup VS Code extension
    if not setup_vscode_extension():
        print("\\n❌ VS Code extension setup failed.")
        return 1
    
    # Test LSP server
    if not test_lsp_server():
        print("\\n❌ LSP server test failed.")
        return 1
    
    # Package extension
    vsix_path = package_extension()
    if not vsix_path:
        print("\\n❌ Extension packaging failed.")
        return 1
    
    # Install extension
    if not install_extension(vsix_path):
        print("\\n❌ Extension installation failed.")
        return 1
    
    # Open test file
    if not open_test_file():
        print("\\n❌ Failed to open test file.")
        return 1
    
    print("\\n" + "=" * 50)
    print("🎉 Setup complete! Your NovaLang extension is ready to use.")
    print("\\n📋 Next steps:")
    print("   1. Check the test file for syntax highlighting")
    print("   2. Try typing '@' to see decorator completions")
    print("   3. Hover over keywords for documentation")
    print("   4. Right-click in explorer to create new NovaLang files")
    print("   5. Press F5 to run NovaLang files")
    print("\\n🌟 Happy coding with NovaLang! 🚀")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
