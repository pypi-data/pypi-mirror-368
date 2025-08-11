@echo off
echo 🚀 NovaLang Extension Setup for Windows
echo =====================================

REM Check if we're in the right directory
if not exist "extensions\vscode\package.json" (
    echo ❌ Error: Please run this script from the NovaLang root directory
    echo    Make sure you can see extensions\vscode\package.json
    pause
    exit /b 1
)

echo 🔍 Running NovaLang extension setup...
python scripts\setup_extension.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Setup completed successfully!
    echo.
    echo 📋 Quick Start Guide:
    echo    • VS Code should now have NovaLang support
    echo    • Open test_lsp.nova to see syntax highlighting
    echo    • Type '@' to see decorator completions
    echo    • Press F5 to run NovaLang files
    echo    • Right-click in explorer for NovaLang commands
    echo.
) else (
    echo.
    echo ❌ Setup failed. Please check the error messages above.
    echo.
)

echo Press any key to exit...
pause >nul
