#!/usr/bin/env python3
"""
Show Different Auto-Generated Main File Examples
"""

from novalang_auto_main import NovaLangAutoMain

def show_minimal_config():
    """Show minimal configuration main file"""
    print("📋 1. MINIMAL CONFIGURATION (like Spring Boot starter)")
    print("=" * 60)
    
    config = {
        "name": "simple-api",
        "features": ["web"]
    }
    
    print("nova.json:")
    print('{\n  "name": "simple-api",\n  "auto_main": true,\n  "features": ["web"]\n}')
    print("\nAuto-generated main file:")
    print("-" * 40)
    
    generator = NovaLangAutoMain(config)
    print(generator.generate_auto_main())

def show_database_config():
    """Show database-enabled configuration"""
    print("\n\n📋 2. DATABASE-ENABLED CONFIGURATION")
    print("=" * 60)
    
    config = {
        "name": "user-service",
        "features": ["web", "jpa"],
        "databases": ["mysql"]
    }
    
    print("nova.json:")
    print('{\n  "name": "user-service",\n  "auto_main": true,\n  "features": ["web", "jpa"],\n  "databases": ["mysql"]\n}')
    print("\nAuto-generated main file:")
    print("-" * 40)
    
    generator = NovaLangAutoMain(config)
    print(generator.generate_auto_main())

def show_secure_config():
    """Show security-enabled configuration"""
    print("\n\n📋 3. SECURITY-ENABLED CONFIGURATION")
    print("=" * 60)
    
    config = {
        "name": "secure-banking-api",
        "features": ["web", "security", "jpa"],
        "databases": ["postgresql"]
    }
    
    print("nova.json:")
    print('{\n  "name": "secure-banking-api",\n  "auto_main": true,\n  "features": ["web", "security", "jpa"],\n  "databases": ["postgresql"]\n}')
    print("\nAuto-generated main file:")
    print("-" * 40)
    
    generator = NovaLangAutoMain(config)
    print(generator.generate_auto_main())

if __name__ == "__main__":
    print("🚀 NovaLang Auto-Generated Main File Examples")
    print("Shows how different configurations create different main files")
    print("Just like Spring Boot's auto-configuration!\n")
    
    show_minimal_config()
    show_database_config() 
    show_secure_config()
    
    print("\n\n🎉 KEY BENEFITS:")
    print("✅ Zero boilerplate code")
    print("✅ Convention over configuration") 
    print("✅ Spring Boot-like experience")
    print("✅ Production-ready endpoints")
    print("✅ Automatic feature detection")
    print("\n💡 Developers just create nova.json and run 'nova run'!")
