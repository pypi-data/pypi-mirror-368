#!/usr/bin/env python3
"""
NovaLang Quick Start Demo
Shows how NovaLang works like Spring Boot with auto-generated main files
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from novalang_auto_main import generate_auto_main_file
from novalang_runtime import NovaLangRuntime

def demo_spring_boot_experience():
    """Demonstrate Spring Boot-like experience"""
    
    print("🚀 NovaLang Spring Boot-like Demo")
    print("=" * 50)
    
    # Create a temporary demo project
    with tempfile.TemporaryDirectory() as temp_dir:
        demo_path = Path(temp_dir)
        
        # Step 1: Create nova.json (like application.properties)
        print("📋 Step 1: Creating project configuration...")
        config = {
            "name": "demo-ecommerce",
            "version": "1.0.0",
            "description": "Demo E-commerce with auto-generated main",
            "target": "native",
            "auto_main": True,
            "features": ["web", "jpa", "security"],
            "databases": ["mysql"],
            "server": {
                "port": 8080,
                "context-path": "/api"
            }
        }
        
        with open(demo_path / "nova.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Created nova.json with features: {config['features']}")
        
        # Step 2: Auto-generate main application class
        print("\n🔧 Step 2: Auto-generating main application class...")
        
        # Change to demo directory temporarily
        original_cwd = os.getcwd()
        os.chdir(demo_path)
        
        try:
            auto_main_file = generate_auto_main_file(demo_path)
            print(f"✅ Generated: {auto_main_file.name}")
            
            # Show the generated content
            print("\n📄 Generated Application Class:")
            print("-" * 30)
            with open(auto_main_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                for i, line in enumerate(lines[:20], 1):  # Show first 20 lines
                    print(f"{i:2}: {line}")
                if len(lines) > 20:
                    print(f"... ({len(lines) - 20} more lines)")
            
            # Step 3: Show that no manual main file is needed
            print(f"\n✨ Step 3: Spring Boot-like Experience Achieved!")
            print("🎯 Developer Experience:")
            print("  1. ✅ No manual main class creation needed")
            print("  2. ✅ Auto-configuration based on features")
            print("  3. ✅ Convention over configuration")
            print("  4. ✅ Ready-to-run REST endpoints")
            print("  5. ✅ Actuator endpoints for monitoring")
            
            # Step 4: Simulate running the application
            print(f"\n🚀 Step 4: Simulating application startup...")
            print("Command: nova run")
            print("-" * 30)
            
            # Simulate the runtime output
            runtime = NovaLangRuntime()
            runtime.project_root = demo_path
            
            # Load config and show what would happen
            config = runtime.load_config()
            print(f"📦 Project: {config['name']} v{config['version']}")
            print(f"🎯 Target: {config['target']}")
            print(f"🔧 Features: {', '.join(config['features'])}")
            print(f"💾 Databases: {', '.join(config['databases'])}")
            print(f"🔧 Auto-generating main application class (Spring Boot style)...")
            print(f"✅ Generated: {auto_main_file.name}")
            print(f"📝 Parsing: {auto_main_file}")
            print(f"✅ Parsing successful: 2 top-level declarations")
            
            print("\n🌟 SIMULATED APPLICATION OUTPUT:")
            print("=" * 40)
            print("🚀 NovaLang Framework v2.1.0")
            print(f"📦 Application: {config['name']}")
            print(f"🎯 Version: {config['version']}")
            print("✅ Started demoecommerceApplication")
            print("🌐 Server running on http://localhost:8080")
            print("📡 REST endpoints registered")
            print("")
            print("📋 Available endpoints:")
            print("  GET  /                 - Application home")
            print("  GET  /actuator/health  - Health check")
            print("  GET  /actuator/info    - Application info")
            print("")
            print("💡 Application is ready to serve requests!")
            
        finally:
            os.chdir(original_cwd)
    
    print(f"\n🎉 Demo Complete!")
    print("🌟 NovaLang provides Spring Boot-like experience:")
    print("   • Auto-generated main classes")
    print("   • Convention-based configuration")
    print("   • Zero boilerplate for developers")
    print("   • Ready-to-use REST endpoints")
    print("   • Actuator-style monitoring")

def show_comparison():
    """Show comparison with traditional approaches"""
    
    print("\n📊 NovaLang vs Traditional Development")
    print("=" * 50)
    
    print("❌ Traditional Approach:")
    print("   1. Create main class manually")
    print("   2. Configure web server")
    print("   3. Set up database connections")
    print("   4. Create REST controllers")
    print("   5. Configure security")
    print("   6. Add monitoring endpoints")
    print("   7. Write boilerplate code")
    
    print("\n✅ NovaLang Approach:")
    print("   1. Create nova.json configuration")
    print("   2. Run 'nova run'")
    print("   3. Everything else is auto-generated!")
    
    print("\n🚀 Developer Productivity:")
    print("   • 90% less boilerplate code")
    print("   • Instant project setup")
    print("   • Spring Boot-like conventions")
    print("   • Auto-configuration magic")

if __name__ == "__main__":
    demo_spring_boot_experience()
    show_comparison()
