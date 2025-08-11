#!/usr/bin/env python3
"""
NovaLang Language Server Protocol (LSP) Implementation
Provides language features for any LSP-compatible editor

Usage: python novalang_lsp.py
"""

import json
import sys
import re
from typing import List, Dict, Any, Optional
import logging

# Set up logging
logging.basicConfig(filename='novalang_lsp.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class NovaLangLSP:
    def __init__(self):
        self.documents = {}
        self.capabilities = {
            "textDocumentSync": 1,  # Full sync
            "completionProvider": {
                "triggerCharacters": [".", "@", " ", "("]
            },
            "hoverProvider": True,
            "definitionProvider": True,
            "diagnosticsProvider": True,
            "documentFormattingProvider": True,
            "documentSymbolProvider": True,
            "signatureHelpProvider": {
                "triggerCharacters": ["(", ","]
            }
        }
        
        # NovaLang keywords and built-ins
        self.keywords = [
            "if", "else", "while", "for", "return", "break", "continue",
            "function", "class", "let", "const", "new", "this", "null", 
            "true", "false", "print", "len", "str", "num"
        ]
        
        self.decorators = [
            "@Component", "@Entity", "@Service", "@Repository", 
            "@Controller", "@Application", "@Configuration"
        ]
        
        self.snippets = {
            "@Component": {
                "label": "@Component",
                "kind": 14,  # Snippet
                "insertText": "@Component\nclass ${1:ComponentName} {\n    state = {\n        ${2:// component state}\n    }\n    \n    function render(${3:props}) {\n        return `\n            ${4:// JSX-like template}\n        `\n    }\n    \n    function ${5:onMount}() {\n        ${6:// lifecycle method}\n    }\n}",
                "insertTextFormat": 2,
                "documentation": "Create a NovaLang Frontend Component"
            },
            "@Entity": {
                "label": "@Entity",
                "kind": 14,
                "insertText": "@Entity\nclass ${1:EntityName} {\n    ${2:id}: number\n    ${3:name}: string\n    \n    function ${1:EntityName}(${4:params}) {\n        ${5:// constructor}\n    }\n    \n    function validate() {\n        ${6:// validation logic}\n        return null\n    }\n}",
                "insertTextFormat": 2,
                "documentation": "Create a NovaLang Entity (shared between frontend and backend)"
            },
            "@Service": {
                "label": "@Service", 
                "kind": 14,
                "insertText": "@Service\nclass ${1:ServiceName} {\n    \n    function ${2:methodName}(${3:params}) {\n        ${4:// business logic}\n    }\n}",
                "insertTextFormat": 2,
                "documentation": "Create a NovaLang Service (business logic layer)"
            },
            "@Repository": {
                "label": "@Repository",
                "kind": 14,
                "insertText": "@Repository\nclass ${1:EntityName}Repository {\n    \n    function findAll() {\n        print \"📋 ${1:EntityName}Repository.findAll()\"\n        ${2:// database query logic}\n    }\n    \n    function save(${3:entity}) {\n        print \"💾 ${1:EntityName}Repository.save()\"\n        ${4:// save logic}\n    }\n}",
                "insertTextFormat": 2,
                "documentation": "Create a NovaLang Repository (data access layer)"
            },
            "@Controller": {
                "label": "@Controller",
                "kind": 14,
                "insertText": "@Controller(\"${1:/api/endpoint}\")\nclass ${2:ControllerName} {\n    \n    function GET ${3:index}() {\n        print \"🌐 GET ${1:/api/endpoint}\"\n        return {\n            status: 200,\n            data: ${4:data}\n        }\n    }\n    \n    function POST ${5:create}(request) {\n        print \"🌐 POST ${1:/api/endpoint}\"\n        return {\n            status: 201,\n            data: ${6:result}\n        }\n    }\n}",
                "insertTextFormat": 2,
                "documentation": "Create a NovaLang REST Controller (API endpoints)"
            }
        }
    
    def handle_initialize(self, params):
        """Handle LSP initialize request"""
        logger.info("LSP Initialize request received")
        return {
            "capabilities": self.capabilities,
            "serverInfo": {
                "name": "NovaLang LSP",
                "version": "1.0.0"
            }
        }
    
    def handle_completion(self, params):
        """Provide code completion suggestions"""
        try:
            uri = params["textDocument"]["uri"]
            position = params["position"]
            
            logger.info(f"Completion request for {uri} at {position}")
            
            # Get document content
            content = self.documents.get(uri, "")
            lines = content.split('\n')
            
            if position["line"] < len(lines):
                current_line = lines[position["line"]]
                char_pos = position["character"]
                
                # Get text before cursor
                text_before = current_line[:char_pos]
                
                completions = []
                
                # Decorator completions
                if text_before.endswith('@') or '@' in text_before.split()[-1] if text_before.split() else False:
                    for decorator in self.decorators:
                        if decorator in self.snippets:
                            completions.append(self.snippets[decorator])
                
                # Keyword completions
                else:
                    # Add keywords
                    for keyword in self.keywords:
                        completions.append({
                            "label": keyword,
                            "kind": 14,  # Keyword
                            "insertText": keyword,
                            "documentation": f"NovaLang keyword: {keyword}"
                        })
                    
                    # Add function snippets
                    completions.extend([
                        {
                            "label": "function",
                            "kind": 3,  # Function
                            "insertText": "function ${1:name}(${2:params}) {\n    ${3:// body}\n}",
                            "insertTextFormat": 2,
                            "documentation": "Create a function"
                        },
                        {
                            "label": "print",
                            "kind": 3,
                            "insertText": "print ${1:message}",
                            "insertTextFormat": 2,
                            "documentation": "Print statement"
                        },
                        {
                            "label": "if",
                            "kind": 14,
                            "insertText": "if (${1:condition}) {\n    ${2:// code}\n}",
                            "insertTextFormat": 2,
                            "documentation": "If statement"
                        },
                        {
                            "label": "while",
                            "kind": 14,
                            "insertText": "while (${1:condition}) {\n    ${2:// loop body}\n}",
                            "insertTextFormat": 2,
                            "documentation": "While loop"
                        }
                    ])
                
                return {
                    "isIncomplete": False,
                    "items": completions
                }
                
        except Exception as e:
            logger.error(f"Completion error: {e}")
            return {"isIncomplete": False, "items": []}
    
    def handle_hover(self, params):
        """Provide hover information"""
        try:
            uri = params["textDocument"]["uri"]
            position = params["position"]
            
            # Get word at position
            content = self.documents.get(uri, "")
            lines = content.split('\n')
            
            if position["line"] < len(lines):
                line = lines[position["line"]]
                char_pos = position["character"]
                
                # Extract word at cursor
                word_match = re.search(r'\b\w+\b', line[max(0, char_pos-20):char_pos+20])
                if word_match:
                    word = word_match.group()
                    
                    # Provide documentation for keywords
                    docs = {
                        "print": "**print** - Output values to console\n\nUsage: `print \"message\"`",
                        "function": "**function** - Define a reusable block of code\n\nUsage: `function name(params) { ... }`",
                        "class": "**class** - Define a class (can be Component, Entity, Service, etc.)\n\nUsage: `class Name { ... }`",
                        "@Component": "**@Component** - Frontend component decorator\n\nCreates React-style components with state management",
                        "@Entity": "**@Entity** - Entity decorator\n\nDefines data models that work in both frontend and backend",
                        "@Service": "**@Service** - Service decorator\n\nDefines business logic layer components",
                        "@Repository": "**@Repository** - Repository decorator\n\nDefines data access layer components",
                        "@Controller": "**@Controller** - Controller decorator\n\nDefines REST API endpoint handlers"
                    }
                    
                    if word in docs:
                        return {
                            "contents": {
                                "kind": "markdown",
                                "value": docs[word]
                            }
                        }
            
            # Default hover
            return {
                "contents": {
                    "kind": "markdown",
                    "value": "**NovaLang** - The Full-Stack Programming Language"
                }
            }
            
        except Exception as e:
            logger.error(f"Hover error: {e}")
            return None
    
    def handle_diagnostics(self, uri, text):
        """Check for syntax errors and issues"""
        diagnostics = []
        
        try:
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                # Check for common syntax issues
                
                # Missing semicolons (optional but recommended)
                if line.strip() and not line.strip().endswith((';', '{', '}', ')', ',')):
                    if any(keyword in line for keyword in ['print', 'let', 'const', 'return']):
                        diagnostics.append({
                            "range": {
                                "start": {"line": i, "character": len(line) - 1},
                                "end": {"line": i, "character": len(line)}
                            },
                            "severity": 3,  # Information
                            "message": "Consider adding semicolon for clarity",
                            "source": "novalang"
                        })
                
                # Undefined variables (basic check)
                if 'undefined' in line.lower():
                    diagnostics.append({
                        "range": {
                            "start": {"line": i, "character": 0},
                            "end": {"line": i, "character": len(line)}
                        },
                        "severity": 1,  # Error
                        "message": "Potential undefined reference",
                        "source": "novalang"
                    })
                
                # Missing decorators for classes that look like they need them
                if line.strip().startswith('class ') and i > 0:
                    prev_line = lines[i-1].strip()
                    if not prev_line.startswith('@'):
                        class_name = line.split()[1]
                        if any(suffix in class_name for suffix in ['Service', 'Repository', 'Controller', 'Component']):
                            diagnostics.append({
                                "range": {
                                    "start": {"line": i, "character": 0},
                                    "end": {"line": i, "character": len(line)}
                                },
                                "severity": 2,  # Warning
                                "message": f"Consider adding appropriate decorator for {class_name}",
                                "source": "novalang"
                            })
        
        except Exception as e:
            logger.error(f"Diagnostics error: {e}")
        
        return diagnostics
    
    def handle_did_open(self, params):
        """Handle document open"""
        uri = params["textDocument"]["uri"]
        text = params["textDocument"]["text"]
        self.documents[uri] = text
        
        # Send diagnostics
        diagnostics = self.handle_diagnostics(uri, text)
        self.send_notification("textDocument/publishDiagnostics", {
            "uri": uri,
            "diagnostics": diagnostics
        })
    
    def handle_did_change(self, params):
        """Handle document changes"""
        uri = params["textDocument"]["uri"]
        changes = params["contentChanges"]
        
        # For full sync, take the last change
        if changes:
            self.documents[uri] = changes[-1]["text"]
            
            # Send updated diagnostics
            diagnostics = self.handle_diagnostics(uri, changes[-1]["text"])
            self.send_notification("textDocument/publishDiagnostics", {
                "uri": uri,
                "diagnostics": diagnostics
            })
    
    def send_response(self, request_id, result):
        """Send LSP response"""
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        self.send_message(response)
    
    def send_notification(self, method, params):
        """Send LSP notification"""
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        self.send_message(notification)
    
    def send_message(self, message):
        """Send message to client"""
        content = json.dumps(message)
        response = f"Content-Length: {len(content)}\r\n\r\n{content}"
        sys.stdout.write(response)
        sys.stdout.flush()
    
    def read_message(self):
        """Read LSP message from stdin"""
        # Read headers
        headers = {}
        while True:
            line = sys.stdin.readline()
            if line == '\r\n' or line == '\n':
                break
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
        
        # Read content
        content_length = int(headers.get('Content-Length', 0))
        content = sys.stdin.read(content_length)
        
        return json.loads(content)
    
    def run(self):
        """Main LSP server loop"""
        logger.info("NovaLang LSP Server starting...")
        
        while True:
            try:
                message = self.read_message()
                method = message.get("method")
                params = message.get("params", {})
                request_id = message.get("id")
                
                logger.info(f"Received message: {method}")
                
                # Handle requests
                if method == "initialize":
                    result = self.handle_initialize(params)
                    self.send_response(request_id, result)
                
                elif method == "textDocument/completion":
                    result = self.handle_completion(params)
                    self.send_response(request_id, result)
                
                elif method == "textDocument/hover":
                    result = self.handle_hover(params)
                    self.send_response(request_id, result)
                
                # Handle notifications
                elif method == "textDocument/didOpen":
                    self.handle_did_open(params)
                
                elif method == "textDocument/didChange":
                    self.handle_did_change(params)
                
                elif method == "initialized":
                    logger.info("LSP initialized successfully")
                
                elif method == "shutdown":
                    self.send_response(request_id, None)
                    break
                
                elif method == "exit":
                    break
                    
            except EOFError:
                break
            except Exception as e:
                logger.error(f"LSP Server error: {e}")
                break
        
        logger.info("NovaLang LSP Server shutting down...")

def main():
    """Main entry point for the novalang-lsp command"""
    server = NovaLangLSP()
    server.run()

if __name__ == "__main__":
    main()
