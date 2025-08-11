#!/usr/bin/env python3
"""
Simple NovaLang Runner
Usage: python run_nova.py <file.nova>
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from nova_runtime import NovaLangRuntime

def main():
    """Simple runner for NovaLang files"""
    if len(sys.argv) < 2:
        print("Usage: python run_nova.py <file.nova>")
        print("   or: python run_nova.py (auto-discover)")
        return 1
    
    runtime = NovaLangRuntime()
    
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
        success = runtime.execute_nova_file(file_path)
    else:
        success = runtime.run()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
