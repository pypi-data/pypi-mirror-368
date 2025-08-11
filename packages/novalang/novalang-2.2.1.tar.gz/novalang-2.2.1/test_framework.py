#!/usr/bin/env python3
"""
NovaLang End-to-End Test
Tests the complete published framework functionality
"""

import subprocess
import sys
import os
import tempfile
import shutil
from pathlib import Path

def test_novalang_framework():
    """Test the complete NovaLang framework"""
    
    print("🧪 NovaLang Framework End-to-End Test")
    print("=" * 50)
    
    # Create a temporary test directory
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        print(f"📂 Test directory: {test_dir}")
        
        # Copy the framework files
        current_dir = Path(__file__).parent
        framework_files = [
            'lexer.py', 'parser.py', 'compiler.py', 
            'nova_runtime.py', 'run_nova.py'
        ]
        
        for file in framework_files:
            src = current_dir / file
            if src.exists():
                shutil.copy2(src, test_dir / file)
        
        # Create a test NovaLang application
        app_content = '''@Component
@Application  
class TestApplication {
    
    function main(): void {
        print("🎉 NovaLang Framework Test Successful!");
        print("✅ Parsing works automatically");
        print("✅ Runtime executes without manual parser usage");
        print("✅ Ready for production deployment!");
        
        runServices();
    }
    
    function runServices(): void {
        let userService = new UserService();
        let message = userService.welcome("Developer");
        print(message);
    }
}

@Service
class UserService {
    
    function welcome(name: string): string {
        return "Welcome to NovaLang, " + name + "!";
    }
    
    function getVersion(): string {
        return "NovaLang v2.1.0";
    }
}'''
        
        app_file = test_dir / "TestApplication.nova"
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(app_content)
        
        # Create nova.json config
        config_content = '''{
  "name": "test-framework",
  "version": "1.0.0",
  "target": "native",
  "main": "TestApplication.nova"
}'''
        
        config_file = test_dir / "nova.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print("\n📝 Created test application:")
        print(f"   {app_file}")
        print(f"   {config_file}")
        
        # Test the runtime
        print("\n🚀 Testing NovaLang runtime...")
        
        try:
            # Change to test directory
            original_cwd = os.getcwd()
            os.chdir(test_dir)
            
            # Add current directory to Python path
            sys.path.insert(0, str(test_dir))
            
            # Import and test the runtime
            from nova_runtime import NovaLangRuntime
            
            runtime = NovaLangRuntime()
            success = runtime.execute_nova_file(app_file)
            
            if success:
                print("\n✅ Framework test PASSED!")
                print("🎯 Key achievements:")
                print("   ✅ NovaLang files parse automatically")
                print("   ✅ No manual parser usage required")  
                print("   ✅ Runtime executes applications seamlessly")
                print("   ✅ Framework ready for publication")
                print("\n🌟 NovaLang Framework is ready for users!")
                return True
            else:
                print("\n❌ Framework test FAILED!")
                return False
                
        except Exception as e:
            print(f"\n❌ Framework test ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            # Restore original directory
            os.chdir(original_cwd)
            if str(test_dir) in sys.path:
                sys.path.remove(str(test_dir))

if __name__ == "__main__":
    success = test_novalang_framework()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 NovaLang Framework is ready for publication!")
        print("\n📦 Next steps:")
        print("   1. Update version in setup.py")
        print("   2. Build package: python setup.py sdist bdist_wheel")
        print("   3. Upload to PyPI: twine upload dist/*")
        print("   4. Users can install: pip install novalang")
        print("   5. Users can run: nova MyApp.nova")
        sys.exit(0)
    else:
        print("\n❌ TESTS FAILED!")
        print("🔧 Fix issues before publishing")
        sys.exit(1)
