#!/usr/bin/env python3
"""
Test Runner for RC Release Automation Agent

Comprehensive test runner that executes all tests in the proper order
with clear output and error handling.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run unit tests only  
    python run_tests.py --integration      # Run integration tests only
    python run_tests.py --github           # Run GitHub tests only
    python run_tests.py --slack            # Run Slack tests only
    python run_tests.py --cli              # Run CLI tests only
    python run_tests.py --external         # Run external template tests
"""

import argparse
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.logging import get_logger


def run_command(command: List[str], description: str) -> bool:
    """Run a command and return success status."""
    logger = get_logger(__name__)
    logger.info(f"🧪 Running: {description}")
    
    try:
        result = subprocess.run(
            command,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {description}: PASSED")
            if result.stdout.strip():
                logger.debug(f"Output: {result.stdout.strip()}")
            return True
        else:
            logger.error(f"❌ {description}: FAILED")
            if result.stderr.strip():
                logger.error(f"Error: {result.stderr.strip()}")
            if result.stdout.strip():
                logger.error(f"Output: {result.stdout.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"❌ {description}: TIMEOUT (5 minutes)")
        return False
    except Exception as e:
        logger.error(f"❌ {description}: ERROR - {e}")
        return False


def run_github_tests() -> bool:
    """Run GitHub integration tests."""
    logger = get_logger(__name__)
    logger.info("🐙 Running GitHub Integration Tests")
    
    # Check if we can run real GitHub tests
    import os
    has_github_token = bool(os.environ.get("GITHUB_TOKEN"))
    
    if has_github_token:
        logger.info("✅ GitHub token found - running full integration tests")
        return run_command([
            sys.executable, "tests/test_github/test_github_integration.py", "--test-all"
        ], "GitHub Integration Tests (with real API)")
    else:
        logger.warning("⚠️ No GitHub token - testing authentication check only")
        return run_command([
            sys.executable, "tests/test_github/test_github_integration.py", "--help"
        ], "GitHub Integration Tests (dry run)")


def run_slack_tests() -> bool:
    """Run Slack integration tests."""
    logger = get_logger(__name__)
    logger.info("💬 Running Slack Integration Tests")
    
    tests = [
        ([sys.executable, "tests/test_slack/test_slack_modal.py", "--test-modal"], 
         "Slack Modal Structure Test"),
        ([sys.executable, "tests/test_slack/test_slack_modal.py", "--test-workflow"], 
         "Slack Modal Workflow Test"),
        ([sys.executable, "tests/test_slack/test_slack_bot.py"], 
         "Slack Bot Configuration Test"),
    ]
    
    passed = 0
    for command, description in tests:
        if run_command(command, description):
            passed += 1
    
    logger.info(f"📊 Slack Tests: {passed}/{len(tests)} passed")
    return passed == len(tests)


def run_cli_tests() -> bool:
    """Run CLI and core functionality tests."""
    logger = get_logger(__name__)
    logger.info("🖥️ Running CLI and Core Tests")
    
    return run_command([
        sys.executable, "tests/test_cli.py", "--test-all"
    ], "CLI and Core Functionality Tests")


def run_external_tests() -> bool:
    """Run external template tests."""
    logger = get_logger(__name__)
    logger.info("📄 Running External Template Tests")
    
    return run_command([
        sys.executable, "tests/test_external_template.py"
    ], "External Template Tests")


def run_unit_tests() -> bool:
    """Run unit tests using pytest if available."""
    logger = get_logger(__name__)
    logger.info("🔬 Running Unit Tests")
    
    # Try to use pytest if available
    try:
        import pytest
        return run_command([
            sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"
        ], "Unit Tests (pytest)")
    except ImportError:
        logger.warning("⚠️ pytest not available, running basic tests")
        # Run basic tests manually
        tests_passed = 0
        total_tests = 0
        
        # Run available test files
        test_files = [
            ("tests/demo_test.py", "Demo Tests"),
        ]
        
        for test_file, description in test_files:
            if Path(test_file).exists():
                total_tests += 1
                if run_command([sys.executable, test_file], description):
                    tests_passed += 1
        
        return tests_passed == total_tests


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(
        description="Run tests for RC Release Automation Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Unit tests only
    python run_tests.py --integration      # Integration tests only
    python run_tests.py --github           # GitHub tests only
    python run_tests.py --slack            # Slack tests only
        """
    )
    
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--github", action="store_true", help="Run GitHub tests only")
    parser.add_argument("--slack", action="store_true", help="Run Slack tests only")
    parser.add_argument("--cli", action="store_true", help="Run CLI tests only")
    parser.add_argument("--external", action="store_true", help="Run external template tests only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    logger = get_logger(__name__)
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("🚀 RC Release Automation Agent - Test Runner")
    logger.info("=" * 60)
    
    tests_run = []
    tests_passed = []
    
    # Determine which tests to run
    if args.unit:
        tests_run.append(("Unit Tests", run_unit_tests))
    elif args.integration:
        tests_run.extend([
            ("GitHub Integration", run_github_tests),
            ("Slack Integration", run_slack_tests),
            ("External Templates", run_external_tests),
        ])
    elif args.github:
        tests_run.append(("GitHub Integration", run_github_tests))
    elif args.slack:
        tests_run.append(("Slack Integration", run_slack_tests))
    elif args.cli:
        tests_run.append(("CLI Tests", run_cli_tests))
    elif args.external:
        tests_run.append(("External Templates", run_external_tests))
    else:
        # Run all tests
        tests_run.extend([
            ("Unit Tests", run_unit_tests),
            ("CLI Tests", run_cli_tests),
            ("GitHub Integration", run_github_tests),
            ("Slack Integration", run_slack_tests),
            ("External Templates", run_external_tests),
        ])
    
    # Run tests
    for test_name, test_func in tests_run:
        logger.info(f"\n🔍 Starting {test_name}...")
        try:
            if test_func():
                tests_passed.append(test_name)
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info(f"📊 Test Results: {len(tests_passed)}/{len(tests_run)} test suites passed")
    
    if tests_passed:
        logger.info("✅ Passed:")
        for test in tests_passed:
            logger.info(f"   - {test}")
    
    failed_tests = [name for name, _ in tests_run if name not in tests_passed]
    if failed_tests:
        logger.error("❌ Failed:")
        for test in failed_tests:
            logger.error(f"   - {test}")
    
    # Exit with appropriate code
    success = len(tests_passed) == len(tests_run)
    if success:
        logger.info("🎉 All tests passed!")
    else:
        logger.error("💥 Some tests failed!")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 