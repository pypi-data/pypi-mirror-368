#!/usr/bin/env python3
"""
Show Auto-Generated Main File Example
"""

from novalang_auto_main import NovaLangAutoMain

# Use the full-stack config from the test
config = {
    "name": "full-stack-ecommerce",
    "version": "2.0.0", 
    "description": "Full-stack e-commerce platform",
    "features": ["web", "jpa", "security", "validation", "cache"],
    "databases": ["mysql", "redis"]
}

print("🚀 Auto-Generated Main File for full-stack-ecommerce")
print("=" * 60)

generator = NovaLangAutoMain(config)
main_content = generator.generate_auto_main()

print(main_content)

print("\n" + "=" * 60)
print("✨ This file is automatically created - no manual coding needed!")
