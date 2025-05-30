#!/usr/bin/env python3
# tests/test_refactored_structure.py - Test suite for refactored src/ structure

"""
Comprehensive test suite for the refactored RC Release Agent.
Tests the new src/ structure following Python best practices.
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

def test_package_structure():
    """Test that the src/ package structure is correct."""
    print("📁 Testing Src Package Structure")
    print("=" * 40)
    
    required_files = [
        'src/__init__.py',
        'src/cli/__init__.py',
        'src/cli/run_release_agent.py',
        'src/cli/rc_agent_build_release.py',
        'src/github/__init__.py',
        'src/slack/__init__.py',
        'src/slack/release_signoff_notifier.py',
        'src/crq/__init__.py',
        'src/utils/__init__.py',
        'src/config/__init__.py',
        'src/templates/',
        'main.py',
        'pyproject.toml',
        'README.md'
    ]
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}: Found")
        else:
            print(f"❌ {file_path}: Missing")
            return False
    
    return True

def test_src_imports():
    """Test that all src modules can be imported correctly."""
    print("\n🧪 Testing Src Module Imports")
    print("=" * 40)
    
    tests = [
        ("CLI Main", "src.cli.run_release_agent", "main"),
        ("CLI Prompts", "src.cli.rc_agent_build_release", "get_release_inputs"),
        ("Slack Bot", "src.slack.release_signoff_notifier", "main"),
    ]
    
    for name, module, function in tests:
        try:
            mod = __import__(module, fromlist=[function])
            getattr(mod, function)
            print(f"✅ {name}: Import successful")
        except Exception as e:
            print(f"❌ {name}: Import failed - {e}")
            return False
    
    return True

def test_main_entry_point():
    """Test the main entry point."""
    print("\n🎯 Testing Main Entry Point")
    print("=" * 40)
    
    try:
        main_py = project_root / 'main.py'
        with open(main_py, 'r') as f:
            content = f.read()
        
        # Check that the script has the required structure
        required_elements = [
            'import sys',
            'import os',
            'sys.path.insert',
            'from src.cli.run_release_agent import main as cli_main',
            'if __name__ == "__main__":'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if not missing_elements:
            print("✅ Main Entry Point: Structure valid")
            return True
        else:
            print(f"❌ Main Entry Point: Missing elements - {missing_elements}")
            return False
            
    except Exception as e:
        print(f"❌ Main Entry Point: Test failed - {e}")
        return False

def test_python_module_execution():
    """Test Python module execution standards."""
    print("\n🐍 Testing Python Module Execution")
    print("=" * 40)
    
    try:
        # Test that we can run with python -m syntax
        test_code = f"""
import sys
sys.path.insert(0, '{project_root / "src"}')
try:
    from src.cli import run_release_agent
    print('MODULE_IMPORT_SUCCESS')
except Exception as e:
    print(f'MODULE_IMPORT_ERROR: {{e}}')
"""
        
        result = subprocess.run([
            sys.executable, '-c', test_code
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0 and 'MODULE_IMPORT_SUCCESS' in result.stdout:
            print("✅ Python Module Execution: Import successful")
            return True
        else:
            print(f"❌ Python Module Execution: Failed - {result.stderr or result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ Python Module Execution: Test failed - {e}")
        return False

def test_github_integration():
    """Test GitHub integration if token is available."""
    print("\n🐙 Testing GitHub Integration")
    print("=" * 40)
    
    if not os.getenv('GITHUB_TOKEN'):
        print("⚠️  GITHUB_TOKEN not set - skipping GitHub tests")
        return True
    
    try:
        script_path = project_root / 'scripts' / 'test_github_trigger.py'
        result = subprocess.run([
            sys.executable, str(script_path)
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ GitHub integration test PASSED")
            return True
        else:
            print(f"❌ GitHub integration test FAILED: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ GitHub test execution failed: {e}")
        return False

def test_pyproject_toml():
    """Test that pyproject.toml is properly configured."""
    print("\n📦 Testing PyProject.toml")
    print("=" * 40)
    
    try:
        pyproject_path = project_root / 'pyproject.toml'
        with open(pyproject_path, 'r') as f:
            content = f.read()
        
        required_sections = [
            '[build-system]',
            '[project]',
            '[project.scripts]',
            '[tool.setuptools.packages.find]',
            'name = "rc-release-agent"',
            'where = ["src"]'
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if not missing_sections:
            print("✅ PyProject.toml: Configuration valid")
            return True
        else:
            print(f"❌ PyProject.toml: Missing sections - {missing_sections}")
            return False
            
    except Exception as e:
        print(f"❌ PyProject.toml: Test failed - {e}")
        return False

def main():
    """Run all tests and report results."""
    print("🚀 RC Release Agent - Refactored Structure Test Suite")
    print("=" * 55)
    print("Testing proper Python src/ structure and standards\n")
    
    tests = [
        ("Package Structure", test_package_structure),
        ("Src Module Imports", test_src_imports),
        ("Main Entry Point", test_main_entry_point),
        ("Python Module Execution", test_python_module_execution),
        ("PyProject.toml", test_pyproject_toml),
        ("GitHub Integration", test_github_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: Unexpected error - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 55)
    print("🎯 TEST SUMMARY")
    print("=" * 55)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Refactored structure is ready!")
        print("\n🚀 Usage:")
        print("  python main.py                    # Main CLI entry point")
        print("  python -m src.cli.run_release_agent  # Module execution")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 