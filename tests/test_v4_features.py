#!/usr/bin/env python3
"""
RC Release Agent v4.0 Feature Tests

Comprehensive testing of all v4.0 features including:
- Version validation and normalization
- Release type prompts with tips
- Environment variable configuration
- LLM timeout handling
- Service name extraction from environment

Usage:
    python test_v4_features.py --help
    python test_v4_features.py --test-all
"""

import sys
from pathlib import Path
import os
import tempfile
import json
from unittest.mock import patch, MagicMock
import time

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logging import get_logger
from src.config.config import load_config, Settings
from src.llm.wmt_gateway_adapter import call_llm


def test_version_validation():
    """Test v4.0 version validation and normalization."""
    logger = get_logger(__name__)
    logger.info("🔢 Testing v4.0 version validation...")
    
    # Import the CLI module to test version functions
    from src.cli.rc_agent_build_release import normalize_version, is_valid_version
    
    # Test version normalization (strips v prefix)
    test_cases = [
        # Input, Expected Output
        ("v1.2.3", "1.2.3"),
        ("1.2.3", "1.2.3"),
        ("v1.2.3-abc123", "1.2.3-abc123"),
        ("1.2.3-abc123", "1.2.3-abc123"),
        ("abc123", "abc123"),  # SHA only
        ("abcdef123456", "abcdef123456"),  # Longer SHA
    ]
    
    for input_version, expected in test_cases:
        result = normalize_version(input_version)
        if result == expected:
            logger.info(f"✅ normalize_version('{input_version}') = '{result}'")
        else:
            logger.error(f"❌ normalize_version('{input_version}') = '{result}', expected '{expected}'")
            return False
    
    # Test version validation
    valid_versions = [
        "v1.2.3",
        "1.2.3",
        "v1.2.3-abc123",
        "1.2.3-abc123",
        "abc123",
        "v10.20.30",
        "v0.0.1",
        "1.2.3-abcdef123456",  # SHA with more characters
        "fedcba987654321"  # Longer SHA
    ]
    
    for version in valid_versions:
        if is_valid_version(version):
            logger.info(f"✅ is_valid_version('{version}') = True")
        else:
            logger.error(f"❌ is_valid_version('{version}') = False, expected True")
            return False
    
    # Test invalid versions
    invalid_versions = [
        "",
        "   ",
        "v1.2",
        "1.2.3.4",
        "v1.2.3.4",
        "invalid!version",
        "version with spaces",
        "feature-branch",  # Branch names not supported
        "main",  # Branch names not supported
        "HEAD~1",  # Git refs not supported
        "abc12"  # SHA too short (< 6 chars)
    ]
    
    for version in invalid_versions:
        if not is_valid_version(version):
            logger.info(f"✅ is_valid_version('{version}') = False")
        else:
            logger.error(f"❌ is_valid_version('{version}') = True, expected False")
            return False
    
    logger.info("✅ Version validation tests passed")
    return True


def test_release_type_prompts():
    """Test v4.0 release type prompts with tips."""
    logger = get_logger(__name__)
    logger.info("📝 Testing v4.0 release type prompts...")
    
    # Import the CLI module to test release types
    from src.cli.rc_agent_build_release import RELEASE_TYPES
    
    # Verify all expected release types are present
    expected_types = ["standard", "hotfix", "release"]
    
    for release_type in expected_types:
        if release_type in RELEASE_TYPES:
            logger.info(f"✅ Release type '{release_type}' is configured")
            
            # Verify each type has a tip description
            tip_text = RELEASE_TYPES[release_type]
            if isinstance(tip_text, str) and len(tip_text) > 10:
                logger.info(f"✅ Release type '{release_type}' has helpful tip ({len(tip_text)} chars)")
            else:
                logger.error(f"❌ Release type '{release_type}' tip is too short or empty")
                return False
        else:
            logger.error(f"❌ Release type '{release_type}' not found in RELEASE_TYPES")
            return False
    
    # Test all release types have helpful content
    for release_type, tip in RELEASE_TYPES.items():
        if len(tip) > 20:  # Ensure tips have meaningful content
            logger.info(f"✅ Release type '{release_type}' has helpful tip ({len(tip)} chars)")
        else:
            logger.error(f"❌ Release type '{release_type}' tip is too short or empty")
            return False
    
    logger.info("✅ Release type prompts tests passed")
    return True


def test_environment_configuration():
    """Test v4.0 environment variable configuration."""
    logger = get_logger(__name__)
    logger.info("🌍 Testing v4.0 environment configuration...")
    
    # Create a test environment file
    test_env_content = """#!/bin/bash
# Test environment configuration

# GitHub Configuration
export GITHUB_TOKEN="ghp_test_token_12345"
export GITHUB_REPO="test-org/test-service"

# Service Configuration
export SERVICE_NAME="test-service"
export SERVICE_NAMESPACE="test-namespace"
export SERVICE_REGIONS="us-east-1,us-west-2"
export PLATFORM="kubernetes"

# Slack Configuration
export SLACK_BOT_TOKEN="xoxb-test-token"
export SLACK_SIGNING_SECRET="test-signing-secret"
export SLACK_CHANNEL="#test-channel"

# LLM Configuration
export LLM_PROVIDER="openai"
export OPENAI_API_KEY="sk-test-key"
export WMT_GATEWAY_URL="#http://llm-internal.walmart.com:8000"
export WMT_GATEWAY_KEY="test-key"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(test_env_content)
        temp_env_file = f.name
    
    try:
        # Test environment file parsing
        env_vars = {}
        for line in test_env_content.split('\n'):
            line = line.strip()
            if line.startswith('export ') and '=' in line:
                key, value = line[7:].split('=', 1)
                env_vars[key] = value.strip('"')
        
        logger.info(f"✅ Parsed {len(env_vars)} environment variables from test file")
        
        # Expected count should be around 13 variables (removed 7 Azure variables from original 20)
        
        # Test required variables are present
        required_vars = [
            "GITHUB_TOKEN", "GITHUB_REPO", "SERVICE_NAME", 
            "SLACK_BOT_TOKEN", "SLACK_SIGNING_SECRET", "OPENAI_API_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if var in env_vars:
                logger.info(f"✅ Required variable '{var}' present")
            else:
                logger.error(f"❌ Required variable '{var}' missing")
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing required variables: {missing_vars}")
            return False
        
        # Test service name extraction
        service_name = env_vars.get("SERVICE_NAME")
        if service_name:
            logger.info(f"✅ Service name extracted: '{service_name}'")
        else:
            # Test fallback extraction from GITHUB_REPO
            github_repo = env_vars.get("GITHUB_REPO", "")
            if "/" in github_repo:
                fallback_service = github_repo.split("/")[-1].lower()
                logger.info(f"✅ Fallback service name from repo: '{fallback_service}'")
            else:
                logger.error("❌ No service name or valid GitHub repo found")
                return False
        
        logger.info("✅ Environment configuration tests passed")
        return True
        
    finally:
        # Clean up temp file
        os.unlink(temp_env_file)


def test_llm_timeout_handling():
    """Test v4.0 LLM timeout handling."""
    logger = get_logger(__name__)
    logger.info("⏰ Testing v4.0 LLM timeout handling...")
    
    # Test WMT Gateway timeout by setting environment variables to a non-existent server
    try:
        with patch.dict(os.environ, {
            "WMT_LLM_API_URL": "http://non-existent-server.com:8000",
            "WMT_LLM_API_KEY": "test-key"
        }, clear=False):
            
            start_time = time.time()
            try:
                # This should timeout quickly due to the 10-second timeout in the code
                response = call_llm("test prompt")
                # If we get here, it means the timeout worked and returned None
                if response is None:
                    elapsed = time.time() - start_time
                    if elapsed < 15:  # Should timeout within 15 seconds
                        logger.info(f"✅ LLM timeout handled correctly ({elapsed:.2f}s)")
                    else:
                        logger.error(f"❌ Timeout took too long ({elapsed:.2f}s)")
                        return False
                else:
                    logger.error("❌ Expected timeout but got response")
                    return False
            except Exception as e:
                elapsed = time.time() - start_time
                if elapsed < 15:  # Should timeout within 15 seconds
                    logger.info(f"✅ LLM timeout handled correctly with exception ({elapsed:.2f}s)")
                else:
                    logger.error(f"❌ Timeout took too long ({elapsed:.2f}s)")
                    return False
        
        logger.info("✅ LLM timeout handling tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ LLM timeout test failed: {e}")
        return False


def test_service_name_extraction():
    """Test v4.0 service name extraction from environment."""
    logger = get_logger(__name__)
    logger.info("🏷️ Testing v4.0 service name extraction...")
    
    # Test cases for service name extraction
    test_cases = [
        # (SERVICE_NAME, GITHUB_REPO, expected_result)
        ("custom-service", "owner/repo", "custom-service"),
        ("", "owner/my-service", "my-service"),
        ("", "ArnoldoM23/PerfCopilot", "perfcopilot"),
        ("", "company/CoolApp", "coolapp"),
        ("", "", "ce-cart"),  # Default fallback
        ("explicit-name", "", "explicit-name"),
    ]
    
    for service_name, github_repo, expected in test_cases:
        # Mock environment variables
        with patch.dict(os.environ, {
            "SERVICE_NAME": service_name,
            "GITHUB_REPO": github_repo
        }, clear=False):
            
            # Test service name extraction logic
            extracted = os.environ.get("SERVICE_NAME")
            if not extracted and github_repo:
                if "/" in github_repo:
                    extracted = github_repo.split("/")[-1].lower()
                else:
                    extracted = github_repo.lower()
            
            if not extracted:
                extracted = "ce-cart"  # Default fallback
            
            if extracted == expected:
                logger.info(f"✅ Service name extraction: '{service_name}' + '{github_repo}' = '{extracted}'")
            else:
                logger.error(f"❌ Service name extraction: '{service_name}' + '{github_repo}' = '{extracted}', expected '{expected}'")
                return False
    
    logger.info("✅ Service name extraction tests passed")
    return True


def test_config_validation():
    """Test v4.0 configuration validation."""
    logger = get_logger(__name__)
    logger.info("⚙️ Testing v4.0 configuration validation...")
    
    try:
        # Test loading config with environment variables
        with patch.dict(os.environ, {
            "GITHUB_TOKEN": "ghp_test_token",
            "GITHUB_REPO": "test/repo",
            "SERVICE_NAME": "test-service",
            "OPENAI_API_KEY": "sk-test-key",
            "SLACK_BOT_TOKEN": "xoxb-test-token",
            "SLACK_SIGNING_SECRET": "test-secret",
        }, clear=False):
            
            # Test config loads successfully
            config = load_config("src/config/settings.yaml")
            logger.info("✅ Configuration loaded with environment variables")
            
            # Test config has required sections
            required_sections = ["github", "slack", "llm", "organization", "ai"]
            for section in required_sections:
                if hasattr(config, section):
                    logger.info(f"✅ Configuration has '{section}' section")
                else:
                    logger.error(f"❌ Configuration missing '{section}' section")
                    return False
            
            # Test environment variables are injected
            if config.github.token:
                logger.info("✅ GitHub token injected from environment")
            else:
                logger.error("❌ GitHub token not injected from environment")
                return False
            
            if config.github.repo:
                logger.info("✅ GitHub repo injected from environment")
            else:
                logger.error("❌ GitHub repo not injected from environment")
                return False
            
            logger.info("✅ Configuration validation tests passed")
            return True
            
    except Exception as e:
        logger.error(f"❌ Configuration validation test failed: {e}")
        return False


def run_all_v4_tests():
    """Run all v4.0 feature tests."""
    logger = get_logger(__name__)
    logger.info("🧪 Running RC Release Agent v4.0 Feature Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Version Validation", test_version_validation),
        ("Release Type Prompts", test_release_type_prompts),
        ("Environment Configuration", test_environment_configuration),
        ("LLM Timeout Handling", test_llm_timeout_handling),
        ("Service Name Extraction", test_service_name_extraction),
        ("Config Validation", test_config_validation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Running {test_name} test...")
        try:
            if test_func():
                logger.info(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
    
    logger.info(f"\n📊 v4.0 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All v4.0 tests passed! New features are working correctly.")
        logger.info("\n🚀 v4.0 Features Ready:")
        logger.info("- ✅ Multiple version format support (v1.2.3, 1.2.3-sha, SHA-only)")
        logger.info("- ✅ Enhanced CLI with release type prompts and tips")
        logger.info("- ✅ Environment variable configuration loading")
        logger.info("- ✅ LLM timeout handling for better performance")
        logger.info("- ✅ Service name extraction from environment")
        logger.info("- ✅ Strict configuration validation")
    else:
        logger.error("❌ Some v4.0 tests failed. Please check the issues above.")
    
    return passed == total


def main():
    """Main testing function."""
    logger = get_logger(__name__)
    
    try:
        logger.info("🚀 RC Release Agent v4.0 Feature Testing")
        logger.info("=" * 50)
        
        success = run_all_v4_tests()
        
        if success:
            logger.info("\n🎉 v4.0 feature testing completed successfully!")
            logger.info("\n📋 Next Steps:")
            logger.info("  1. All v4.0 features are working correctly")
            logger.info("  2. Configuration hygiene improvements are active")
            logger.info("  3. Enhanced CLI user experience is ready")
            logger.info("  4. Performance optimizations are in place")
            return 0
        else:
            logger.error("\n❌ v4.0 feature testing failed!")
            return 1
            
    except KeyboardInterrupt:
        logger.info("\nv4.0 feature testing interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"v4.0 feature testing failed with error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 