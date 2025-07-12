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
        'src/github_integration/__init__.py',
        'src/slack/__init__.py',
        'src/slack/release_signoff_notifier.py',
        'src/crq/__init__.py',
        'src/utils/__init__.py',
        'src/config/__init__.py',
        'src/templates/',
        'pyproject.toml',
        'README.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}: Found")
        else:
            print(f"❌ {file_path}: Missing")
            missing_files.append(file_path)
    
    assert not missing_files, f"Missing required files: {missing_files}"

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
            assert False, f"Import failed for {name}: {e}"

def test_main_entry_point():
    """Test the package entry points."""
    print("\n🎯 Testing Package Entry Points")
    print("=" * 40)
    
    try:
        pyproject_path = project_root / 'pyproject.toml'
        with open(pyproject_path, 'r') as f:
            content = f.read()
        
        # Check that the script has the required entry points
        required_elements = [
            '[project.scripts]',
            'rc-release-agent = "src.cli.run_release_agent:main"',
            'rc-slack-bot = "src.slack.release_signoff_notifier:main"'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if not missing_elements:
            print("✅ Package Entry Points: Configuration valid")
        else:
            print(f"❌ Package Entry Points: Missing elements - {missing_elements}")
            assert False, f"Missing required elements in pyproject.toml: {missing_elements}"
            
    except Exception as e:
        print(f"❌ Package Entry Points: Test failed - {e}")
        assert False, f"Package entry point test failed: {e}"

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
        else:
            print(f"❌ Python Module Execution: Failed - {result.stderr or result.stdout}")
            assert False, f"Python module execution failed: {result.stderr or result.stdout}"
            
    except Exception as e:
        print(f"❌ Python Module Execution: Test failed - {e}")
        assert False, f"Python module execution test failed: {e}"

def test_github_integration():
    """Test GitHub integration if token is available."""
    print("\n🐙 Testing GitHub Integration")
    print("=" * 40)
    
    if not os.getenv('GITHUB_TOKEN'):
        print("⚠️  GITHUB_TOKEN not set - skipping GitHub tests")
        return  # Skip test if no token
    
    try:
        script_path = project_root / 'scripts' / 'test_github_trigger.py'
        result = subprocess.run([
            sys.executable, str(script_path)
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            print("✅ GitHub integration test PASSED")
        else:
            print(f"❌ GitHub integration test FAILED: {result.stderr}")
            assert False, f"GitHub integration test failed: {result.stderr}"
    except Exception as e:
        print(f"❌ GitHub test execution failed: {e}")
        assert False, f"GitHub test execution failed: {e}"

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
        else:
            print(f"❌ PyProject.toml: Missing sections - {missing_sections}")
            assert False, f"Missing required sections in pyproject.toml: {missing_sections}"
            
    except Exception as e:
        print(f"❌ PyProject.toml: Test failed - {e}")
        assert False, f"PyProject.toml test failed: {e}"

def main():
    """Run all tests and report results."""
    print("🚀 RC Release Agent - Refactored Structure Test Suite")
    print("=" * 55)
    print("Testing proper Python src/ structure and standards\n")
    
    tests = [
        ("Package Structure", test_package_structure),
        ("Src Module Imports", test_src_imports),
        ("Package Entry Points", test_main_entry_point),
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
        print("  pip install -e . && rc-release-agent    # Package entry point (recommended)")
        print("  python -m src.cli.run_release_agent     # Module execution")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 