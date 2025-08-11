#!/usr/bin/env python3
"""
NovaLang IDE Setup Script
Automatically configures your preferred IDE for NovaLang development
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def detect_ides():
    """Detect installed IDEs on the system"""
    ides = {}
    
    # VS Code
    if subprocess.run(['code', '--version'], capture_output=True).returncode == 0:
        ides['vscode'] = 'Visual Studio Code'
    
    # Sublime Text
    if subprocess.run(['subl', '--version'], capture_output=True).returncode == 0:
        ides['sublime'] = 'Sublime Text'
    
    # Vim
    if subprocess.run(['vim', '--version'], capture_output=True).returncode == 0:
        ides['vim'] = 'Vim'
    
    # Emacs
    if subprocess.run(['emacs', '--version'], capture_output=True).returncode == 0:
        ides['emacs'] = 'Emacs'
    
    return ides

def setup_vscode():
    """Setup VS Code for NovaLang"""
    print("🔧 Setting up Visual Studio Code...")
    
    # Install NovaLang extension
    result = subprocess.run(['code', '--install-extension', 'novalang-1.0.3.vsix'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ NovaLang VS Code extension installed!")
    else:
        print("⚠️ Extension installation failed. Install manually from marketplace.")
    
    # Create VS Code settings for NovaLang
    vscode_dir = Path.home() / '.vscode'
    vscode_dir.mkdir(exist_ok=True)
    
    settings = {
        "files.associations": {
            "*.nova": "novalang"
        },
        "terminal.integrated.shell.windows": "powershell.exe",
        "novalang.enableIntelliSense": True,
        "novalang.autoIndent": True
    }
    
    settings_file = vscode_dir / 'settings.json'
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)
    
    print("✅ VS Code settings configured for NovaLang!")

def setup_sublime():
    """Setup Sublime Text for NovaLang"""
    print("🔧 Setting up Sublime Text...")
    
    # Sublime Text packages directory
    if sys.platform == 'win32':
        sublime_dir = Path.home() / 'AppData/Roaming/Sublime Text 3/Packages/User'
    elif sys.platform == 'darwin':
        sublime_dir = Path.home() / 'Library/Application Support/Sublime Text 3/Packages/User'
    else:
        sublime_dir = Path.home() / '.config/sublime-text-3/Packages/User'
    
    sublime_dir.mkdir(parents=True, exist_ok=True)
    
    # Create syntax file
    syntax_content = '''%YAML 1.2
---
name: NovaLang
file_extensions: [nova]
scope: source.novalang

contexts:
  main:
    - match: '\\b(function|let|if|else|while|for|return|print)\\b'
      scope: keyword.control.novalang
    - match: '"'
      scope: punctuation.definition.string.begin.novalang
      push: double_quoted_string
    - match: '\\b\\d+(\\.\\d+)?\\b'
      scope: constant.numeric.novalang
    - match: '//.*$'
      scope: comment.line.double-slash.novalang

  double_quoted_string:
    - meta_scope: string.quoted.double.novalang
    - match: '\\\\"'
      scope: constant.character.escape.novalang
    - match: '"'
      scope: punctuation.definition.string.end.novalang
      pop: true'''
    
    syntax_file = sublime_dir / 'NovaLang.sublime-syntax'
    with open(syntax_file, 'w') as f:
        f.write(syntax_content)
    
    # Create build system
    build_content = '''{
    "shell_cmd": "nova run $file",
    "file_regex": "^Error in ([^:]*):.*line ([0-9]+)",
    "selector": "source.novalang",
    "variants": [
        {
            "name": "Build Web",
            "shell_cmd": "nova build --web"
        },
        {
            "name": "Build Mobile", 
            "shell_cmd": "nova build --mobile"
        },
        {
            "name": "Build All",
            "shell_cmd": "nova build --all"
        },
        {
            "name": "Dev Server",
            "shell_cmd": "nova dev"
        }
    ]
}'''
    
    build_file = sublime_dir / 'NovaLang.sublime-build'
    with open(build_file, 'w') as f:
        f.write(build_content)
    
    print("✅ Sublime Text configured for NovaLang!")

def setup_vim():
    """Setup Vim for NovaLang"""
    print("🔧 Setting up Vim...")
    
    vim_dir = Path.home() / '.vim'
    syntax_dir = vim_dir / 'syntax'
    ftdetect_dir = vim_dir / 'ftdetect'
    ftplugin_dir = vim_dir / 'ftplugin'
    
    syntax_dir.mkdir(parents=True, exist_ok=True)
    ftdetect_dir.mkdir(parents=True, exist_ok=True)
    ftplugin_dir.mkdir(parents=True, exist_ok=True)
    
    # Syntax file
    syntax_content = '''if exists("b:current_syntax")
  finish
endif

syn keyword novalangKeyword function let if else while for return print
syn keyword novalangBoolean true false
syn keyword novalangNull null

syn region novalangString start='"' end='"' contains=novalangEscape
syn match novalangEscape contained '\\\\\\\\'
syn match novalangNumber '\\d\\+\\(\\.\\d\\+\\)\\?'
syn match novalangComment '//.*$'

hi def link novalangKeyword Keyword
hi def link novalangBoolean Boolean  
hi def link novalangNull Constant
hi def link novalangString String
hi def link novalangNumber Number
hi def link novalangComment Comment

let b:current_syntax = "novalang"'''
    
    with open(syntax_dir / 'novalang.vim', 'w') as f:
        f.write(syntax_content)
    
    # File detection
    with open(ftdetect_dir / 'novalang.vim', 'w') as f:
        f.write('au BufRead,BufNewFile *.nova setfiletype novalang\\n')
    
    # Plugin file
    plugin_content = '''command! NovaRun !nova run %
command! NovaBuildWeb !nova build --web
command! NovaBuildMobile !nova build --mobile  
command! NovaBuildAll !nova build --all
command! NovaDevServer !nova dev

nnoremap <buffer> <F5> :NovaRun<CR>
nnoremap <buffer> <F6> :NovaDevServer<CR>
nnoremap <buffer> <F7> :NovaBuildAll<CR>'''
    
    with open(ftplugin_dir / 'novalang.vim', 'w') as f:
        f.write(plugin_content)
    
    print("✅ Vim configured for NovaLang!")

def main():
    print("🚀 NovaLang IDE Setup Script")
    print("============================")
    
    # Check if NovaLang is installed
    try:
        result = subprocess.run(['nova', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ NovaLang not found. Install with: pip install novalang")
            return
        print(f"✅ NovaLang found: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ NovaLang not found. Install with: pip install novalang")
        return
    
    # Detect IDEs
    ides = detect_ides()
    
    if not ides:
        print("❌ No supported IDEs found.")
        print("Supported: VS Code, Sublime Text, Vim, Emacs")
        return
    
    print("\\n🔍 Detected IDEs:")
    for key, name in ides.items():
        print(f"   • {name}")
    
    print("\\n🛠️ Choose IDE to configure:")
    for i, (key, name) in enumerate(ides.items(), 1):
        print(f"   {i}. {name}")
    print("   0. All detected IDEs")
    
    try:
        choice = input("\\nEnter choice (0-{}): ".format(len(ides)))
        choice = int(choice)
        
        if choice == 0:
            # Setup all
            for key in ides.keys():
                globals()[f'setup_{key}']()
        elif 1 <= choice <= len(ides):
            key = list(ides.keys())[choice - 1]
            globals()[f'setup_{key}']()
        else:
            print("❌ Invalid choice")
            return
            
    except (ValueError, KeyboardInterrupt):
        print("\\n❌ Setup cancelled")
        return
    
    print("\\n🎉 Setup complete!")
    print("\\n📝 Next steps:")
    print("   1. Create a new project: nova create my-app")
    print("   2. Open in your IDE: cd my-app && code .")
    print("   3. Start development: nova dev")
    
    print("\\n🔧 Available commands in IDE:")
    print("   • nova run filename.nova  - Run NovaLang file")
    print("   • nova dev                - Start development server")
    print("   • nova build --web        - Build web app")
    print("   • nova build --mobile     - Build mobile apps")
    print("   • nova build --all        - Build all platforms")

if __name__ == '__main__':
    main()
