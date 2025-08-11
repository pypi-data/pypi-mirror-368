#!/bin/bash
# setup-vscode-extension.sh - Quick setup for NovaLang VS Code Extension

echo "🚀 Setting up NovaLang VS Code Extension..."

# Navigate to extension directory
cd "$(dirname "$0")/extensions/vscode"

# Check if VS Code Extension Manager (vsce) is installed
if ! command -v vsce &> /dev/null; then
    echo "📦 Installing VS Code Extension Manager (vsce)..."
    npm install -g vsce
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Create TypeScript config if not exists
if [ ! -f "tsconfig.json" ]; then
    echo "📝 Creating TypeScript configuration..."
    cat > tsconfig.json << 'EOF'
{
    "compilerOptions": {
        "module": "commonjs",
        "target": "es6",
        "outDir": "out",
        "lib": [
            "es6"
        ],
        "sourceMap": true,
        "rootDir": "src",
        "strict": true
    },
    "exclude": [
        "node_modules",
        ".vscode-test"
    ]
}
EOF
fi

# Create basic extension TypeScript file
if [ ! -d "src" ]; then
    mkdir -p src
    echo "📝 Creating extension source..."
    cat > src/extension.ts << 'EOF'
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log('NovaLang extension is now active!');

    // Register commands
    let runFile = vscode.commands.registerCommand('novalang.runFile', () => {
        const activeEditor = vscode.window.activeTextEditor;
        if (activeEditor && activeEditor.document.fileName.endsWith('.nova')) {
            const terminal = vscode.window.createTerminal('NovaLang');
            terminal.sendText(`python main.py "${activeEditor.document.fileName}"`);
            terminal.show();
        } else {
            vscode.window.showErrorMessage('Please open a .nova file to run');
        }
    });

    let createProject = vscode.commands.registerCommand('novalang.createProject', async () => {
        const folderUri = await vscode.window.showOpenDialog({
            canSelectFolders: true,
            canSelectFiles: false,
            canSelectMany: false,
            openLabel: 'Select Project Folder'
        });

        if (folderUri && folderUri[0]) {
            // Create basic NovaLang project structure
            const fs = require('fs');
            const path = require('path');
            
            const projectPath = folderUri[0].fsPath;
            
            // Create directories
            fs.mkdirSync(path.join(projectPath, 'src', 'main', 'novalang'), { recursive: true });
            fs.mkdirSync(path.join(projectPath, 'src', 'main', 'novalang', 'entity'), { recursive: true });
            fs.mkdirSync(path.join(projectPath, 'src', 'main', 'novalang', 'repository'), { recursive: true });
            fs.mkdirSync(path.join(projectPath, 'src', 'main', 'novalang', 'service'), { recursive: true });
            fs.mkdirSync(path.join(projectPath, 'src', 'main', 'novalang', 'controller'), { recursive: true });
            
            // Create Application.nova
            const appContent = `@Application
class NovaLangApp {
    function main() {
        print "🚀 Starting NovaLang Application..."
        print "✅ Application started successfully!"
    }
}

// Start the application
let app = new NovaLangApp()
app.main()`;
            
            fs.writeFileSync(path.join(projectPath, 'src', 'main', 'novalang', 'Application.nova'), appContent);
            
            vscode.window.showInformationMessage('NovaLang project created successfully!');
        }
    });

    context.subscriptions.push(runFile, createProject);
}

export function deactivate() {}
EOF
fi

# Compile TypeScript
echo "🔨 Compiling TypeScript..."
npx tsc -p ./

# Package the extension
echo "📦 Packaging extension..."
vsce package

# Get the latest .vsix file
VSIX_FILE=$(ls -t *.vsix | head -n1)

if [ -f "$VSIX_FILE" ]; then
    echo "✅ Extension packaged successfully: $VSIX_FILE"
    echo ""
    echo "📋 To install the extension:"
    echo "   1. Open VS Code"
    echo "   2. Press Ctrl+Shift+P (Cmd+Shift+P on Mac)"
    echo "   3. Type 'Extensions: Install from VSIX'"
    echo "   4. Select the file: $(pwd)/$VSIX_FILE"
    echo ""
    echo "🚀 Or run: code --install-extension $(pwd)/$VSIX_FILE"
    
    # Optionally auto-install
    read -p "🤔 Install the extension now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        code --install-extension "$VSIX_FILE"
        echo "✅ Extension installed! Restart VS Code to activate."
    fi
else
    echo "❌ Failed to package extension"
    exit 1
fi

echo ""
echo "🎉 NovaLang VS Code Extension setup complete!"
echo "📚 Open a .nova file in VS Code to test syntax highlighting"
echo "⌨️  Press F5 in a .nova file to run it"
echo "🔧 Use Ctrl+Alt+C to create new components"
