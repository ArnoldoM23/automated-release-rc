"""
Test suite for LLM Section 8 bug fix.

This test file validates the fix for the issue where Section 8 of release notes
was always showing fallback summary instead of LLM-generated descriptions.

Tests cover:
- LLM-enabled Section 8 generation
- Fallback Section 8 generation when LLM disabled
- OpenAI API integration
- Multi-provider API key configuration
- Error handling and graceful degradation

Bug fix implemented in PR: [Section 8 LLM Description Bug Fix]
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Test imports
from src.config.config import load_config
from src.release_notes.release_notes import generate_ai_release_summary, generate_fallback_summary
from src.llm.llm_client import LLMClient


class MockPR:
    """Mock PR object for testing."""
    def __init__(self, number, title, user_login="test-user", labels=None):
        self.number = number
        self.title = title
        self.user = type('User', (), {
            'login': user_login,
            'display_name': f"{user_login.title()} (@{user_login})"
        })()
        self.labels = labels or []
        self.html_url = f"https://github.com/test/repo/pull/{number}"


@pytest.fixture
def mock_prs():
    """Create mock PR data for testing."""
    return [
        MockPR(1, "Add new checkout feature", "alice"),
        MockPR(2, "Fix cart calculation bug", "bob"),
        MockPR(3, "Update GraphQL schema", "charlie"),
        MockPR(4, "Add internationalization support", "david"),
        MockPR(5, "Improve payment validation", "eve")
    ]


@pytest.fixture
def test_config():
    """Create test configuration."""
    config = load_config(allow_missing_token=True)
    return config


class TestLLMSection8BugFix:
    """Test suite for LLM Section 8 bug fix."""
    
    def test_llm_enabled_generates_ai_summary(self, mock_prs, test_config):
        """Test that LLM-enabled config generates AI-powered summaries."""
        print("🧪 Testing LLM-enabled Section 8 generation...")
        
        # Configure for LLM
        test_config.llm.enabled = True
        test_config.llm.provider = "openai"
        test_config.llm.openai_api_key = "test-key"
        
        # Mock the LLM client to return AI-generated content
        with patch('src.llm.llm_client.LLMClient') as mock_llm_class:
            mock_llm_instance = MagicMock()
            mock_llm_instance.generate_release_summary.return_value = (
                "This release introduces significant checkout improvements, "
                "resolves critical cart calculation issues, and enhances GraphQL schema "
                "to support better user experience and business growth."
            )
            mock_llm_class.return_value = mock_llm_instance
            
            # Test AI summary generation
            summary = generate_ai_release_summary(mock_prs, test_config)
            
            # Verify it's AI-generated (not fallback)
            assert "This release introduces significant checkout improvements" in summary
            assert "to support better user experience and business growth" in summary
            assert len(summary) > 150  # AI summaries are typically longer than fallback
            
            # Verify LLM client was called
            mock_llm_class.assert_called_once()
            mock_llm_instance.generate_release_summary.assert_called_once()
        
        print("✅ LLM-enabled Section 8 generates AI summaries correctly")
        return True
    
    def test_llm_disabled_uses_fallback_summary(self, mock_prs, test_config):
        """Test that LLM-disabled config uses fallback summaries."""
        print("🧪 Testing LLM-disabled Section 8 fallback...")
        
        # Configure for fallback
        test_config.llm.enabled = False
        
        # Test fallback summary generation
        summary = generate_ai_release_summary(mock_prs, test_config)
        
        # Verify it's fallback content
        assert "This release includes" in summary
        assert "to improve system functionality" in summary
        assert len(summary) < 150  # Fallback summaries are shorter
        
        print("✅ LLM-disabled Section 8 uses fallback summaries correctly")
        return True
    
    def test_fallback_summary_content_quality(self, mock_prs):
        """Test that fallback summaries contain meaningful content."""
        print("🧪 Testing fallback summary quality...")
        
        # Generate fallback summary
        summary = generate_fallback_summary(mock_prs)
        
        # Verify meaningful content
        assert isinstance(summary, str)
        assert len(summary) > 20
        assert "release" in summary.lower()
        assert "change" in summary.lower()
        
        print("✅ Fallback summaries contain meaningful content")
        return True
    
    def test_openai_api_key_configuration(self, test_config):
        """Test that OpenAI API key is properly configured."""
        print("🧪 Testing OpenAI API key configuration...")
        
        # Test multi-provider API key support
        test_config.llm.provider = "openai"
        test_config.llm.openai_api_key = "sk-test-key-123"
        
        # Create LLM client
        llm_client = LLMClient(test_config.llm.__dict__)
        
        # Verify configuration
        assert llm_client.provider.value == "openai"
        assert hasattr(test_config.llm, 'openai_api_key')
        assert test_config.llm.openai_api_key == "sk-test-key-123"
        
        print("✅ OpenAI API key configuration works correctly")
        return True
    
    def test_multi_provider_api_key_support(self, test_config):
        """Test that multi-provider API keys are supported."""
        print("🧪 Testing multi-provider API key support...")
        
        # Test that all provider-specific keys are available
        assert hasattr(test_config.llm, 'openai_api_key')
        assert hasattr(test_config.llm, 'anthropic_api_key')
        assert hasattr(test_config.llm, 'walmart_api_key')
        
        # Test provider switching
        providers = ["openai", "anthropic", "walmart_sandbox"]
        for provider in providers:
            test_config.llm.provider = provider
            # Should not raise exception
            llm_client = LLMClient(test_config.llm.__dict__)
            assert llm_client.provider.value == provider
        
        print("✅ Multi-provider API key support works correctly")
        return True
    
    def test_llm_error_handling_graceful_fallback(self, mock_prs, test_config):
        """Test that LLM errors gracefully fall back to default summary."""
        print("🧪 Testing LLM error handling and graceful fallback...")
        
        # Configure for LLM but mock failure
        test_config.llm.enabled = True
        test_config.llm.provider = "openai"
        test_config.llm.fallback_enabled = True
        
        # Mock LLM client to raise exception
        with patch('src.llm.llm_client.LLMClient') as mock_llm_class:
            mock_llm_instance = MagicMock()
            mock_llm_instance.generate_release_summary.side_effect = Exception("API Error")
            mock_llm_class.return_value = mock_llm_instance
            
            # Test error handling
            summary = generate_ai_release_summary(mock_prs, test_config)
            
            # Should fall back to default summary
            assert "This release includes" in summary
            assert "to improve system functionality" in summary
            
            # Verify LLM was attempted
            mock_llm_class.assert_called_once()
            mock_llm_instance.generate_release_summary.assert_called_once()
        
        print("✅ LLM error handling provides graceful fallback")
        return True
    
    def test_section8_content_in_release_notes(self, mock_prs, test_config):
        """Test that Section 8 content appears correctly in release notes."""
        print("🧪 Testing Section 8 content in full release notes...")
        
        # Import release notes generation
        from src.release_notes.release_notes import render_release_notes
        
        # Create test parameters
        params = {
            'rc_name': 'Test User',
            'rc_manager': 'Test Manager',
            'service_name': 'test-service',
            'new_version': 'v1.0.1',
            'prod_version': 'v1.0.0',
            'day1_date': '2025-01-15',
            'day2_date': '2025-01-16',
            'release_type': 'standard',
            'github_repo': 'test/repo'
        }
        
        # Test with LLM enabled
        test_config.llm.enabled = True
        test_config.llm.provider = "openai"
        
        # Mock LLM to return specific content
        with patch('src.llm.llm_client.LLMClient') as mock_llm_class:
            mock_llm_instance = MagicMock()
            mock_llm_instance.generate_release_summary.return_value = (
                "AI-generated test summary for Section 8 validation"
            )
            mock_llm_class.return_value = mock_llm_instance
            
            # Create output directory
            output_dir = Path("test_outputs")
            output_dir.mkdir(exist_ok=True)
            
            # Generate release notes
            release_notes_file = render_release_notes(mock_prs, params, output_dir, test_config)
            
            # Verify file was created
            assert release_notes_file.exists()
            
            # Check Section 8 content
            with open(release_notes_file, 'r') as f:
                content = f.read()
            
            # Verify AI content appears in Section 8
            assert "AI-generated test summary for Section 8 validation" in content
            assert "|| 8 || Release Summary ||" in content
            
            # Clean up
            if release_notes_file.exists():
                release_notes_file.unlink()
        
        print("✅ Section 8 content appears correctly in release notes")
        return True
    
    def test_openai_api_compatibility(self):
        """Test OpenAI API compatibility with modern versions."""
        print("🧪 Testing OpenAI API compatibility...")
        
        # Test that we can import and use modern OpenAI API
        try:
            import openai
            
            # Test modern API structure
            assert hasattr(openai, 'OpenAI')
            client = openai.OpenAI(api_key="test-key")
            assert hasattr(client, 'chat')
            assert hasattr(client.chat, 'completions')
            
            print("✅ OpenAI API compatibility verified")
            return True
            
        except Exception as e:
            print(f"❌ OpenAI API compatibility issue: {e}")
            return False


def test_llm_section8_bugfix_integration():
    """Integration test for the complete LLM Section 8 bug fix."""
    print("🧪 Running LLM Section 8 bug fix integration test...")
    
    # Create test instance
    test_instance = TestLLMSection8BugFix()
    
    # Run all tests
    results = []
    
    # Test with fixtures
    mock_prs = [
        MockPR(1, "Add feature", "alice"),
        MockPR(2, "Fix bug", "bob"),
        MockPR(3, "Update schema", "charlie")
    ]
    
    test_config = load_config(allow_missing_token=True)
    
    # Run individual tests
    results.append(test_instance.test_llm_enabled_generates_ai_summary(mock_prs, test_config))
    results.append(test_instance.test_llm_disabled_uses_fallback_summary(mock_prs, test_config))
    results.append(test_instance.test_fallback_summary_content_quality(mock_prs))
    results.append(test_instance.test_openai_api_key_configuration(test_config))
    results.append(test_instance.test_multi_provider_api_key_support(test_config))
    results.append(test_instance.test_llm_error_handling_graceful_fallback(mock_prs, test_config))
    results.append(test_instance.test_section8_content_in_release_notes(mock_prs, test_config))
    results.append(test_instance.test_openai_api_compatibility())
    
    # Verify all tests passed
    passed_tests = sum(results)
    total_tests = len(results)
    
    print(f"\n🎉 LLM Section 8 Bug Fix Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ All LLM Section 8 bug fix tests passed!")
        return True
    else:
        print("❌ Some LLM Section 8 bug fix tests failed")
        return False


if __name__ == "__main__":
    test_llm_section8_bugfix_integration() 