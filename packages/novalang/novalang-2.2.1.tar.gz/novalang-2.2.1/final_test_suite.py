#!/usr/bin/env python3
"""
Final Pre-Publishing Test Suite
Comprehensive test to ensure everything works before publishing
"""

import os
import json
import tempfile
import shutil
import subprocess
from pathlib import Path

def test_auto_main_generation():
    """Test auto-main generation works correctly"""
    print("🔧 Testing Auto-Main Generation...")
    
    try:
        from novalang_auto_main import generate_auto_main_file, NovaLangAutoMain
        
        # Test with current project
        config = {
            "name": "test-app",
            "auto_main": True,
            "features": ["web", "jpa", "security"],
            "databases": ["mysql"]
        }
        
        generator = NovaLangAutoMain(config)
        main_content = generator.generate_auto_main()
        
        # Verify content is generated
        assert "@Application" in main_content
        assert "class testappApplication" in main_content
        assert "function main()" in main_content
        assert "@GetMapping" in main_content
        
        print("✅ Auto-main generation: WORKING")
        return True
        
    except Exception as e:
        print(f"❌ Auto-main generation: FAILED - {e}")
        return False

def test_runtime_system():
    """Test the runtime system"""
    print("🚀 Testing Runtime System...")
    
    try:
        from novalang_runtime import NovaLangRuntime
        
        # Create test project
        test_dir = Path("test_runtime")
        test_dir.mkdir(exist_ok=True)
        
        # Create nova.json
        config = {
            "name": "runtime-test",
            "auto_main": True,
            "features": ["web"]
        }
        
        with open(test_dir / "nova.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        # Test runtime loading
        original_cwd = os.getcwd()
        os.chdir(test_dir)
        
        try:
            runtime = NovaLangRuntime()
            loaded_config = runtime.load_config()
            
            assert loaded_config["name"] == "runtime-test"
            assert loaded_config["auto_main"] == True
            
            print("✅ Runtime system: WORKING")
            return True
            
        finally:
            os.chdir(original_cwd)
            shutil.rmtree(test_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"❌ Runtime system: FAILED - {e}")
        return False

def test_parser_integration():
    """Test parser integration"""
    print("📝 Testing Parser Integration...")
    
    try:
        from lexer import NovaLangLexer
        from parser import NovaLangParser
        
        # Test simple NovaLang code
        code = '''@Application
class TestApp {
    function main(): void {
        console.log("App started");
    }
}'''
        
        lexer = NovaLangLexer(code)
        tokens = lexer.tokenize()
        
        parser = NovaLangParser(tokens)
        ast = parser.parse_program()
        
        assert ast is not None
        # Check that we have parsed statements
        assert hasattr(ast, 'statements') or hasattr(ast, 'declarations')
        
        print("✅ Parser integration: WORKING")
        return True
        
    except Exception as e:
        print(f"❌ Parser integration: FAILED - {e}")
        return False

def test_complete_workflow():
    """Test the complete end-to-end workflow"""
    print("🔄 Testing Complete Workflow...")
    
    try:
        # Create temporary project
        test_dir = Path("test_complete_workflow")
        test_dir.mkdir(exist_ok=True)
        
        # Create nova.json
        config = {
            "name": "workflow-test",
            "version": "1.0.0",
            "auto_main": True,
            "features": ["web", "jpa"],
            "databases": ["mysql"]
        }
        
        with open(test_dir / "nova.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        # Test auto-main generation
        original_cwd = os.getcwd()
        os.chdir(test_dir)
        
        try:
            from novalang_auto_main import generate_auto_main_file
            auto_main_file = generate_auto_main_file(Path('.'))
            
            assert auto_main_file.exists()
            
            # Read and verify content
            with open(auto_main_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            assert "@Application" in content
            assert "workflowtestApplication" in content
            assert "function main()" in content
            
            print("✅ Complete workflow: WORKING")
            return True
            
        finally:
            os.chdir(original_cwd)
            shutil.rmtree(test_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"❌ Complete workflow: FAILED - {e}")
        return False

def test_setup_py():
    """Test setup.py configuration"""
    print("📦 Testing Setup.py Configuration...")
    
    try:
        # Check if setup.py exists and has correct modules
        setup_file = Path("setup.py")
        assert setup_file.exists()
        
        with open(setup_file, 'r') as f:
            content = f.read()
            
        # Check for required modules
        required_modules = [
            'novalang_runtime',
            'novalang_auto_main',
            'lexer',
            'parser'
        ]
        
        for module in required_modules:
            assert module in content, f"Missing module: {module}"
        
        # Check for entry points
        assert 'console_scripts' in content
        assert 'nova' in content
        
        print("✅ Setup.py configuration: WORKING")
        return True
        
    except Exception as e:
        print(f"❌ Setup.py configuration: FAILED - {e}")
        return False

def run_full_test_suite():
    """Run the complete test suite"""
    print("🧪 NovaLang Framework - Pre-Publishing Test Suite")
    print("=" * 60)
    
    tests = [
        test_auto_main_generation,
        test_runtime_system, 
        test_parser_integration,
        test_complete_workflow,
        test_setup_py
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED - READY FOR PUBLISHING!")
        print("\n🚀 Publishing Checklist:")
        print("✅ Auto-main generation working")
        print("✅ Runtime system stable")
        print("✅ Parser integration complete")
        print("✅ End-to-end workflow tested")
        print("✅ Package configuration verified")
        print("\n💡 Framework is production-ready!")
        return True
    else:
        print("❌ SOME TESTS FAILED - FIX BEFORE PUBLISHING")
        return False

if __name__ == "__main__":
    success = run_full_test_suite()
    
    if success:
        print("\n🎯 Ready to publish with:")
        print("   pip install build")
        print("   python -m build")
        print("   pip install twine")
        print("   twine upload dist/*")
    else:
        print("\n⚠️  Fix failing tests before publishing")
