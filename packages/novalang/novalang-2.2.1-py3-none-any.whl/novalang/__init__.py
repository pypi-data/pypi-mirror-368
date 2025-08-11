"""
NovaLang - The Full-Stack Programming Language

A modern, enterprise-ready programming language that bridges frontend and backend development
with universal IDE support through Language Server Protocol.

Features:
- Full-stack development capabilities
- Universal IDE support (VS Code, IntelliJ, NetBeans, Eclipse, Vim, Emacs)
- Enterprise-grade annotations (@Component, @Service, @Repository, @Controller)
- Built-in web framework and database integration
- Language Server Protocol for intelligent code completion
- Cross-platform compatibility

Usage:
    # Run a NovaLang file
    from novalang import interpreter
    interpreter.run_file("myapp.nova")
    
    # Start Language Server
    from novalang.lsp_server import main as lsp_main
    lsp_main()

Author: Martin Maboya
Email: martinmaboya@gmail.com
GitHub: https://github.com/martinmaboya/novalang
"""

__version__ = "1.1.0"
__author__ = "Martin Maboya"
__email__ = "martinmaboya@gmail.com"
__description__ = "NovaLang - The Full-Stack Programming Language with Universal IDE Support"

# Core modules
from . import lexer
from . import parser
from . import interpreter

# Main entry points
try:
    from .main import main
except ImportError:
    main = None

try:
    from .nova import main as nova_main
except ImportError:
    nova_main = None

# Export main functions for easy access
__all__ = [
    "lexer",
    "parser", 
    "interpreter",
    "main",
    "nova_main",
    "__version__",
    "__author__",
    "__email__",
    "__description__"
]

def get_version():
    """Return the current version of NovaLang."""
    return __version__

def get_info():
    """Return information about NovaLang."""
    return {
        "name": "NovaLang",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": __description__,
        "homepage": "https://github.com/martinmaboya/novalang",
        "documentation": "https://martinmaboya.github.io/novalang"
    }
