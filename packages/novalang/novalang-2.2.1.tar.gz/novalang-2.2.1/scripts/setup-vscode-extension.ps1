# 🚀 NovaLang VS Code Extension Setup (Windows)

Write-Host "🚀 Setting up NovaLang VS Code Extension..." -ForegroundColor Green

# Navigate to extension directory
Set-Location "$PSScriptRoot\..\extensions\vscode"

# Check if VS Code Extension Manager (vsce) is installed
try {
    vsce --version | Out-Null
    Write-Host "✅ VS Code Extension Manager (vsce) is installed" -ForegroundColor Green
} catch {
    Write-Host "📦 Installing VS Code Extension Manager (vsce)..." -ForegroundColor Yellow
    npm install -g vsce
}

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
npm install

# Create TypeScript config if not exists
if (-not (Test-Path "tsconfig.json")) {
    Write-Host "📝 Creating TypeScript configuration..." -ForegroundColor Yellow
    @"
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
"@ | Out-File -FilePath "tsconfig.json" -Encoding UTF8
}

# Create basic extension TypeScript file
if (-not (Test-Path "src")) {
    New-Item -ItemType Directory -Path "src" -Force | Out-Null
    Write-Host "📝 Creating extension source..." -ForegroundColor Yellow
    
    @"
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log('NovaLang extension is now active!');

    // Register commands
    let runFile = vscode.commands.registerCommand('novalang.runFile', () => {
        const activeEditor = vscode.window.activeTextEditor;
        if (activeEditor && activeEditor.document.fileName.endsWith('.nova')) {
            const terminal = vscode.window.createTerminal('NovaLang');
            terminal.sendText(`python main.py "`${activeEditor.document.fileName}`"`);
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
"@ | Out-File -FilePath "src\extension.ts" -Encoding UTF8
}

# Compile TypeScript
Write-Host "🔨 Compiling TypeScript..." -ForegroundColor Yellow
npx tsc -p .\

# Package the extension
Write-Host "📦 Packaging extension..." -ForegroundColor Yellow
vsce package

# Get the latest .vsix file
$vsixFile = Get-ChildItem -Filter "*.vsix" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($vsixFile) {
    Write-Host "✅ Extension packaged successfully: $($vsixFile.Name)" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 To install the extension:" -ForegroundColor Cyan
    Write-Host "   1. Open VS Code" -ForegroundColor White
    Write-Host "   2. Press Ctrl+Shift+P" -ForegroundColor White
    Write-Host "   3. Type 'Extensions: Install from VSIX'" -ForegroundColor White
    Write-Host "   4. Select the file: $(Get-Location)\$($vsixFile.Name)" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 Or run: code --install-extension `"$(Get-Location)\$($vsixFile.Name)`"" -ForegroundColor Yellow
    
    # Optionally auto-install
    $install = Read-Host "🤔 Install the extension now? (y/n)"
    if ($install -eq "y" -or $install -eq "Y") {
        & code --install-extension "$($vsixFile.FullName)"
        Write-Host "✅ Extension installed! Restart VS Code to activate." -ForegroundColor Green
    }
} else {
    Write-Host "❌ Failed to package extension" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 NovaLang VS Code Extension setup complete!" -ForegroundColor Green
Write-Host "📚 Open a .nova file in VS Code to test syntax highlighting" -ForegroundColor Cyan
Write-Host "⌨️  Press F5 in a .nova file to run it" -ForegroundColor Cyan
Write-Host "🔧 Use Ctrl+Alt+C to create new components" -ForegroundColor Cyan
