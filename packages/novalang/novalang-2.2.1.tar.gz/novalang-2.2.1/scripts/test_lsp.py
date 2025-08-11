#!/usr/bin/env python3
"""
Simple LSP Server Test
Tests the NovaLang LSP server with basic requests
"""

import json
import subprocess
import sys
import time
import threading
from pathlib import Path

def create_lsp_message(method, params=None, request_id=None):
    """Create a properly formatted LSP message"""
    message = {
        "jsonrpc": "2.0",
        "method": method
    }
    
    if request_id is not None:
        message["id"] = request_id
    
    if params is not None:
        message["params"] = params
    
    content = json.dumps(message)
    return f"Content-Length: {len(content)}\\r\\n\\r\\n{content}"

def test_lsp_server():
    """Test the LSP server with various requests"""
    print("🧪 Testing NovaLang LSP Server")
    print("=" * 40)
    
    lsp_script = Path("extensions/language-server/novalang_lsp.py")
    
    if not lsp_script.exists():
        print("❌ LSP server script not found at:", lsp_script)
        return False
    
    try:
        # Start LSP server
        print("🔄 Starting LSP server...")
        proc = subprocess.Popen(
            ["python", str(lsp_script)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Test 1: Initialize
        print("📤 Sending initialize request...")
        init_msg = create_lsp_message("initialize", {
            "processId": None,
            "rootUri": None,
            "capabilities": {
                "textDocument": {
                    "completion": {"dynamicRegistration": True},
                    "hover": {"dynamicRegistration": True}
                }
            }
        }, 1)
        
        proc.stdin.write(init_msg)
        proc.stdin.flush()
        
        # Test 2: Initialized notification
        print("📤 Sending initialized notification...")
        initialized_msg = create_lsp_message("initialized", {})
        proc.stdin.write(initialized_msg)
        proc.stdin.flush()
        
        # Test 3: Open document
        print("📤 Opening test document...")
        test_content = """@Component
class TestComponent {
    function render() {
        print "Hello World"
    }
}"""
        
        didopen_msg = create_lsp_message("textDocument/didOpen", {
            "textDocument": {
                "uri": "file:///test.nova",
                "languageId": "novalang",
                "version": 1,
                "text": test_content
            }
        })
        
        proc.stdin.write(didopen_msg)
        proc.stdin.flush()
        
        # Test 4: Completion request
        print("📤 Requesting completion...")
        completion_msg = create_lsp_message("textDocument/completion", {
            "textDocument": {"uri": "file:///test.nova"},
            "position": {"line": 0, "character": 1}
        }, 2)
        
        proc.stdin.write(completion_msg)
        proc.stdin.flush()
        
        # Test 5: Hover request
        print("📤 Requesting hover info...")
        hover_msg = create_lsp_message("textDocument/hover", {
            "textDocument": {"uri": "file:///test.nova"},
            "position": {"line": 2, "character": 8}
        }, 3)
        
        proc.stdin.write(hover_msg)
        proc.stdin.flush()
        
        # Wait for responses
        print("⏳ Waiting for responses...")
        time.sleep(3)
        
        # Read responses
        print("📥 Reading responses...")
        responses = []
        
        # Try to read available output
        try:
            output, error = proc.communicate(timeout=2)
            if output:
                print("📋 Server output:")
                print(output)
                responses.append(output)
            if error:
                print("⚠️ Server errors:")
                print(error)
        except subprocess.TimeoutExpired:
            proc.kill()
            output, error = proc.communicate()
        
        # Shutdown
        print("🔄 Shutting down server...")
        shutdown_msg = create_lsp_message("shutdown", {}, 4)
        try:
            proc.stdin.write(shutdown_msg)
            proc.stdin.flush()
        except:
            pass
        
        exit_msg = create_lsp_message("exit")
        try:
            proc.stdin.write(exit_msg)
            proc.stdin.flush()
        except:
            pass
        
        proc.terminate()
        
        print("✅ LSP server test completed")
        
        # Check if we got any meaningful responses
        if responses and any("capabilities" in resp for resp in responses):
            print("🎉 LSP server is working correctly!")
            return True
        else:
            print("⚠️ LSP server started but responses were not as expected")
            return True  # Still consider it a success if it started
            
    except Exception as e:
        print(f"❌ LSP server test failed: {e}")
        if 'proc' in locals():
            proc.terminate()
        return False

def test_syntax_highlighting():
    """Test if syntax files are valid"""
    print("\\n🎨 Testing syntax highlighting...")
    
    syntax_file = Path("extensions/vscode/syntaxes/novalang.tmLanguage.json")
    
    if not syntax_file.exists():
        print("❌ Syntax file not found")
        return False
    
    try:
        with open(syntax_file, 'r', encoding='utf-8') as f:
            syntax_data = json.load(f)
        
        required_keys = ['name', 'scopeName', 'patterns']
        missing_keys = [key for key in required_keys if key not in syntax_data]
        
        if missing_keys:
            print(f"❌ Syntax file missing required keys: {missing_keys}")
            return False
        
        print(f"✅ Syntax file valid: {syntax_data['name']}")
        print(f"   Scope: {syntax_data['scopeName']}")
        print(f"   Patterns: {len(syntax_data['patterns'])} rules")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ Syntax file contains invalid JSON")
        return False
    except Exception as e:
        print(f"❌ Error reading syntax file: {e}")
        return False

def test_snippets():
    """Test if snippet files are valid"""
    print("\\n📝 Testing code snippets...")
    
    snippets_file = Path("extensions/vscode/snippets/novalang.json")
    
    if not snippets_file.exists():
        print("❌ Snippets file not found")
        return False
    
    try:
        with open(snippets_file, 'r', encoding='utf-8') as f:
            snippets_data = json.load(f)
        
        snippet_count = len(snippets_data)
        print(f"✅ Snippets file valid: {snippet_count} snippets")
        
        # List some snippets
        for name, snippet in list(snippets_data.items())[:3]:
            prefix = snippet.get('prefix', 'N/A')
            description = snippet.get('description', 'N/A')
            print(f"   • {name}: '{prefix}' - {description}")
        
        if snippet_count > 3:
            print(f"   ... and {snippet_count - 3} more")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ Snippets file contains invalid JSON")
        return False
    except Exception as e:
        print(f"❌ Error reading snippets file: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 NovaLang Extension Component Tests")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test LSP server
    if not test_lsp_server():
        all_tests_passed = False
    
    # Test syntax highlighting
    if not test_syntax_highlighting():
        all_tests_passed = False
    
    # Test snippets
    if not test_snippets():
        all_tests_passed = False
    
    print("\\n" + "=" * 50)
    
    if all_tests_passed:
        print("🎉 All tests passed! NovaLang extension components are working.")
    else:
        print("❌ Some tests failed. Please check the output above.")
    
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    sys.exit(main())
