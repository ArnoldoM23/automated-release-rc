#!/usr/bin/env python3
"""
Test Script for Release RC Slack Bot

Comprehensive testing for the Slack bot functionality including:
- Bot initialization
- Mock release session creation
- Integration endpoints
- Command handling simulation
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import threading
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from slack_bot.app import ReleaseRCBot, PRInfo, ReleaseSession
from slack_bot.integration import SlackBotIntegration, format_prs_for_slack, prepare_release_metadata
from slack_bot.config import SlackBotConfig

class TestSlackBot(unittest.TestCase):
    """Test cases for the Release RC Slack bot."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock environment variables
        self.env_vars = {
            "SLACK_BOT_TOKEN": "xoxb-test-token",
            "SLACK_APP_TOKEN": "xapp-test-token",
            "REMINDER_INTERVAL_HOURS": "1",
            "RELEASE_CHANNEL": "#test-release",
            "TIMEZONE": "America/Los_Angeles"
        }
        
        # Patch environment variables
        self.env_patcher = patch.dict(os.environ, self.env_vars)
        self.env_patcher.start()
        
        # Mock Slack components
        self.slack_app_patcher = patch('slack_bot.app.App')
        self.slack_client_patcher = patch('slack_bolt.adapter.socket_mode.SocketModeHandler')
        self.scheduler_patcher = patch('slack_bot.app.BackgroundScheduler')
        
        self.mock_app = self.slack_app_patcher.start()
        self.mock_handler = self.slack_client_patcher.start()
        self.mock_scheduler = self.scheduler_patcher.start()
        
        # Create mock client
        self.mock_client = Mock()
        self.mock_app.return_value.client = self.mock_client
        
        # Create bot instance
        self.bot = ReleaseRCBot()
    
    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
        self.slack_app_patcher.stop()
        self.slack_client_patcher.stop()
        self.scheduler_patcher.stop()
    
    def test_bot_initialization(self):
        """Test bot initialization with configuration."""
        self.assertIsNotNone(self.bot)
        self.assertEqual(self.bot.config["reminder_interval_hours"], 1)
        self.assertEqual(self.bot.config["default_channel"], "#test-release")
        self.assertEqual(len(self.bot.sessions), 0)
    
    def test_pr_info_creation(self):
        """Test PRInfo dataclass creation."""
        pr = PRInfo(
            number=123,
            html_url="https://github.com/org/repo/pull/123",
            author="testuser",
            title="Test PR",
            labels=["feature", "enhancement"]
        )
        
        self.assertEqual(pr.number, 123)
        self.assertEqual(pr.author, "testuser")
        self.assertFalse(pr.signed_off)
    
    def test_release_session_creation(self):
        """Test ReleaseSession dataclass creation."""
        prs = [
            PRInfo(123, "https://github.com/org/repo/pull/123", "user1", "PR 1"),
            PRInfo(124, "https://github.com/org/repo/pull/124", "user2", "PR 2")
        ]
        
        session = ReleaseSession(
            service="test-service",
            version="1.0.0",
            day1_date="2024-01-15",
            day2_date="2024-01-16",
            signoff_cutoff_time="12:00 PM tomorrow",
            rc_slack_handle="<@manager>",
            channel_id="#test-channel",
            thread_ts="1234567890.123456",
            prs=prs,
            trigger_user="U12345"
        )
        
        self.assertEqual(session.service, "test-service")
        self.assertEqual(len(session.prs), 2)
        self.assertEqual(len(session.pending_authors), 2)
        self.assertEqual(len(session.signed_off_authors), 0)
        self.assertEqual(session.trigger_user, "U12345")
    
    def test_start_release_session(self):
        """Test starting a release session."""
        # Mock the client response
        self.mock_client.chat_postMessage.return_value = {"ts": "1234567890.123456"}
        
        # Sample PR data
        pr_data = [
            {
                "number": 123,
                "html_url": "https://github.com/org/repo/pull/123",
                "title": "Test PR",
                "user": {"login": "testuser"},
                "labels": [{"name": "feature"}]
            }
        ]
        
        # Release metadata
        release_metadata = {
            "service": "test-service",
            "version": "1.0.0",
            "day1_date": "2024-01-15",
            "day2_date": "2024-01-16",
            "signoff_cutoff_time": "12:00 PM tomorrow",
            "rc_slack_handle": "<@manager>",
            "channel_id": "#test-channel",
            "trigger_user": "U12345"
        }
        
        # Start session
        result = self.bot.start_release_session(pr_data, release_metadata)
        
        # Verify result
        self.assertTrue(result["success"])
        self.assertEqual(result["channel_id"], "#test-channel")
        self.assertEqual(result["thread_ts"], "1234567890.123456")
        
        # Verify session was created
        self.assertEqual(len(self.bot.sessions), 1)
        
        # Verify client was called
        self.mock_client.chat_postMessage.assert_called_once()
    
    def test_announcement_message_generation(self):
        """Test announcement message generation."""
        prs = [
            PRInfo(123, "https://github.com/org/repo/pull/123", "user1", "Feature A"),
            PRInfo(124, "https://github.com/org/repo/pull/124", "user2", "Bug fix B")
        ]
        
        session = ReleaseSession(
            service="test-service",
            version="1.0.0",
            day1_date="2024-01-15",
            day2_date="2024-01-16",
            signoff_cutoff_time="12:00 PM tomorrow",
            rc_slack_handle="<@manager>",
            channel_id="#test-channel",
            thread_ts="",
            prs=prs,
            trigger_user="U12345"
        )
        
        message = self.bot._generate_announcement_message(session)
        
        # Verify message content
        self.assertIn("test-service v1.0.0", message)
        self.assertIn("2024-01-15", message)
        self.assertIn("2024-01-16", message)
        self.assertIn("<@user1>", message)
        self.assertIn("<@user2>", message)
        self.assertIn("PR #123", message)
        self.assertIn("PR #124", message)
        self.assertIn("<@manager>", message)
        self.assertIn("<@U12345>", message)
    
    def test_status_message_generation(self):
        """Test status message generation."""
        prs = [
            PRInfo(123, "https://github.com/org/repo/pull/123", "user1", "Feature A"),
            PRInfo(124, "https://github.com/org/repo/pull/124", "user2", "Bug fix B", signed_off=True)
        ]
        
        session = ReleaseSession(
            service="test-service",
            version="1.0.0",
            day1_date="2024-01-15",
            day2_date="2024-01-16",
            signoff_cutoff_time="12:00 PM tomorrow",
            rc_slack_handle="<@manager>",
            channel_id="#test-channel",
            thread_ts="",
            prs=prs
        )
        
        message = self.bot._generate_status_message(session)
        
        # Verify message content
        self.assertIn("Sign-off Status", message)
        self.assertIn("Completed:", message)
        self.assertIn("Pending:", message)
        self.assertIn("✅", message)
        self.assertIn("❌", message)
        self.assertIn("user2", message)  # Signed off user
        self.assertIn("user1", message)  # Pending user
    
    def test_user_signoff(self):
        """Test marking a user as signed off."""
        prs = [
            PRInfo(123, "https://github.com/org/repo/pull/123", "user1", "Feature A"),
            PRInfo(124, "https://github.com/org/repo/pull/124", "user1", "Bug fix B")
        ]
        
        session = ReleaseSession(
            service="test-service",
            version="1.0.0",
            day1_date="2024-01-15",
            day2_date="2024-01-16",
            signoff_cutoff_time="12:00 PM tomorrow",
            rc_slack_handle="<@manager>",
            channel_id="#test-channel",
            thread_ts="",
            prs=prs
        )
        
        # Initially, user should have pending PRs
        self.assertIn("user1", session.pending_authors)
        self.assertNotIn("user1", session.signed_off_authors)
        
        # Mark user as signed off
        result = self.bot._mark_user_signed_off(session, "user1")
        
        # Verify sign-off
        self.assertTrue(result)
        self.assertNotIn("user1", session.pending_authors)
        self.assertIn("user1", session.signed_off_authors)
        
        # All PRs should be signed off
        for pr in session.prs:
            if pr.author == "user1":
                self.assertTrue(pr.signed_off)

class TestSlackBotIntegration(unittest.TestCase):
    """Test cases for Slack bot integration."""
    
    def test_format_prs_for_slack(self):
        """Test formatting GitHub PR data for Slack."""
        github_prs = [
            {
                "number": 123,
                "html_url": "https://github.com/org/repo/pull/123",
                "title": "Feature update",
                "user": {"login": "developer1"},
                "labels": [{"name": "feature"}, {"name": "enhancement"}]
            },
            {
                "number": 124,
                "html_url": "https://github.com/org/repo/pull/124",
                "title": "Bug fix",
                "user": {"login": "developer2"},
                "labels": [{"name": "bugfix"}]
            }
        ]
        
        formatted = format_prs_for_slack(github_prs)
        
        self.assertEqual(len(formatted), 2)
        self.assertEqual(formatted[0]["number"], 123)
        self.assertEqual(formatted[0]["user"]["login"], "developer1")
        self.assertEqual(formatted[1]["title"], "Bug fix")
    
    def test_prepare_release_metadata(self):
        """Test preparing release metadata from GitHub Actions inputs."""
        github_inputs = {
            "service_name": "test-service",
            "new_version": "1.0.0",
            "day1_date": "2024-01-15",
            "day2_date": "2024-01-16",
            "rc_manager": "manager_user",
            "slack_channel": "#releases",
            "slack_user": "U12345"
        }
        
        metadata = prepare_release_metadata(github_inputs)
        
        self.assertEqual(metadata["service"], "test-service")
        self.assertEqual(metadata["version"], "1.0.0")
        self.assertEqual(metadata["channel_id"], "#releases")
        self.assertEqual(metadata["trigger_user"], "U12345")
        self.assertIn("<@manager_user>", metadata["rc_slack_handle"])
    
    def test_prepare_release_metadata_with_override(self):
        """Test preparing release metadata with channel override."""
        github_inputs = {
            "service_name": "test-service",
            "new_version": "1.0.0",
            "slack_channel": "#releases"
        }
        
        metadata = prepare_release_metadata(github_inputs, channel_override="#override-channel")
        
        self.assertEqual(metadata["channel_id"], "#override-channel")
    
    def test_mock_bot_response(self):
        """Test mock bot response when no bot URL is configured."""
        integration = SlackBotIntegration()  # No bot_url
        
        pr_data = [{"number": 123, "user": {"login": "test"}}]
        release_metadata = {
            "service": "test-service",
            "version": "1.0.0",
            "channel_id": "#test-channel"
        }
        
        result = integration.trigger_release_workflow(pr_data, release_metadata)
        
        self.assertTrue(result["success"])
        self.assertTrue(result["mock"])
        self.assertEqual(result["channel_id"], "#test-channel")
        self.assertEqual(result["pr_count"], 1)

class TestSlackBotConfig(unittest.TestCase):
    """Test cases for Slack bot configuration."""
    
    def test_config_from_environment(self):
        """Test configuration creation from environment variables."""
        env_vars = {
            "SLACK_BOT_TOKEN": "xoxb-test",
            "SLACK_APP_TOKEN": "xapp-test",
            "REMINDER_INTERVAL_HOURS": "3",
            "RELEASE_CHANNEL": "#test-releases",
            "HOST": "localhost",
            "PORT": "3000"
        }
        
        with patch.dict(os.environ, env_vars):
            config = SlackBotConfig.from_environment()
        
        self.assertEqual(config.slack_bot_token, "xoxb-test")
        self.assertEqual(config.slack_app_token, "xapp-test")
        self.assertEqual(config.reminder_interval_hours, 3)
        self.assertEqual(config.default_channel, "#test-releases")
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 3000)
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Valid config
        config = SlackBotConfig(
            slack_bot_token="xoxb-test",
            slack_app_token="xapp-test",
            reminder_interval_hours=2,
            port=5000
        )
        self.assertTrue(config.validate())
        
        # Invalid config - missing tokens
        config_invalid = SlackBotConfig()
        with self.assertRaises(ValueError):
            config_invalid.validate()
    
    def test_config_to_dict(self):
        """Test configuration dictionary conversion."""
        config = SlackBotConfig(
            slack_bot_token="xoxb-test",
            slack_app_token="xapp-test",
            reminder_interval_hours=2
        )
        
        config_dict = config.to_dict()
        
        self.assertIn("reminder_interval_hours", config_dict)
        self.assertIn("has_slack_bot_token", config_dict)
        self.assertTrue(config_dict["has_slack_bot_token"])
        self.assertNotIn("slack_bot_token", config_dict)  # Should not expose actual token

def run_integration_test():
    """Run a comprehensive integration test."""
    print("🧪 Running Slack Bot Integration Test...")
    
    # Create temporary files for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        pr_file = os.path.join(temp_dir, "test_prs.json")
        metadata_file = os.path.join(temp_dir, "test_metadata.json")
        
        # Create test data
        pr_data = [
            {
                "number": 123,
                "html_url": "https://github.com/test/repo/pull/123",
                "title": "Test feature",
                "user": {"login": "testuser1"},
                "labels": [{"name": "feature"}]
            },
            {
                "number": 124,
                "html_url": "https://github.com/test/repo/pull/124",
                "title": "Test bugfix",
                "user": {"login": "testuser2"},
                "labels": [{"name": "bugfix"}]
            }
        ]
        
        metadata = {
            "service": "test-service",
            "version": "1.0.0",
            "day1_date": "2024-01-15",
            "day2_date": "2024-01-16",
            "signoff_cutoff_time": "12:00 PM tomorrow",
            "rc_manager": "test-manager",
            "channel_id": "#test-releases"
        }
        
        # Write test files
        with open(pr_file, 'w') as f:
            json.dump(pr_data, f)
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)
        
        # Test integration
        from slack_bot.integration import main as integration_main
        
        # Mock sys.argv for the test
        original_argv = sys.argv
        try:
            sys.argv = ["integration.py", pr_file, metadata_file, "#override-channel"]
            
            # Capture the integration test (it will use mock mode)
            try:
                integration_main()
                print("✅ Integration test completed successfully")
                return True
            except SystemExit as e:
                if e.code == 0:
                    print("✅ Integration test completed successfully")
                    return True
                else:
                    print(f"❌ Integration test failed with exit code {e.code}")
                    return False
        finally:
            sys.argv = original_argv

def main():
    """Main test runner."""
    print("🚀 Starting Release RC Slack Bot Tests")
    print("=" * 50)
    
    # Run unit tests
    print("\n📋 Running Unit Tests...")
    unittest.main(
        module=__name__,
        argv=[''],
        exit=False,
        verbosity=2
    )
    
    print("\n🔗 Running Integration Test...")
    integration_success = run_integration_test()
    
    print("\n" + "=" * 50)
    if integration_success:
        print("🎉 All tests completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Deploy the bot to your preferred platform")
        print("2. Configure Slack app with proper tokens")
        print("3. Test with a real release workflow")
    else:
        print("❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 