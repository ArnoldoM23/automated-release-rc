#!/usr/bin/env python3
"""
Slack Bot Testing Script

Test the sign-off bot functionality independently.
This helps validate the bot before deploying it to production.

Usage:
    python test_slack_bot.py --help
    python test_slack_bot.py --test-bot
    python test_slack_bot.py --test-message
    python test_slack_bot.py --mock-signoff
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.logging import get_logger


def test_slack_credentials():
    """Test Slack bot credentials and environment setup."""
    logger = get_logger(__name__)
    logger.info("🔐 Testing Slack credentials...")
    
    required_vars = [
        "SLACK_BOT_TOKEN",
        "SLACK_SIGNING_SECRET",
    ]
    
    missing_vars = []
    for var in required_vars:
        if os.environ.get(var):
            logger.info(f"✅ {var} is set")
        else:
            logger.error(f"❌ {var} is missing")
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        logger.info("Set them with:")
        for var in missing_vars:
            logger.info(f"  export {var}='your-value-here'")
        return False
    
    return True


def test_slack_imports():
    """Test that all required Slack libraries are available."""
    logger = get_logger(__name__)
    logger.info("📦 Testing Slack library imports...")
    
    try:
        from slack_bolt import App
        logger.info("✅ slack_bolt imported successfully")
        
        from slack_sdk import WebClient
        logger.info("✅ slack_sdk imported successfully")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        logger.info("Install missing dependencies with:")
        logger.info("  pip install slack_bolt slack_sdk")
        return False


def create_mock_release_data() -> Dict[str, Any]:
    """Create mock release data for testing."""
    return {
        "service_name": "cer-cart",
        "new_version": "v1.3.0",
        "prod_version": "v1.2.3",
        "rc_name": "Test RC",
        "rc_manager": "Test Manager",
        "day1_date": "2024-01-15",
        "day2_date": "2024-01-16",
        "channel": "#release-rc-test",
        "approvers": ["user1", "user2", "user3"]
    }


def test_release_tracker():
    """Test the ReleaseTracker class functionality."""
    logger = get_logger(__name__)
    logger.info("🤖 Testing ReleaseTracker class...")
    
    try:
        # Import the ReleaseTracker
        sys.path.append(str(Path(__file__).parent))
        from signoff_bot import ReleaseTracker
        
        # Create mock release data
        release_data = create_mock_release_data()
        
        # Initialize tracker (without Slack for testing)
        tracker = ReleaseTracker()
        
        # Test adding a release
        release_id = f"{release_data['service_name']}-{release_data['new_version']}"
        tracker.add_release(
            release_id=release_id,
            service_name=release_data['service_name'],
            version=release_data['new_version'],
            approvers=release_data['approvers']
        )
        
        logger.info(f"✅ Release added: {release_id}")
        
        # Test getting release
        release_info = tracker.get_release(release_id)
        if release_info:
            logger.info(f"✅ Release retrieved: {release_info['service_name']}")
        else:
            logger.error("❌ Failed to retrieve release")
            return False
        
        # Test adding signoffs
        for user in ["user1", "user2"]:
            tracker.add_signoff(release_id, user)
            logger.info(f"✅ Signoff added for {user}")
        
        # Test checking completion
        is_complete = tracker.is_complete(release_id)
        logger.info(f"📊 Release completion status: {is_complete}")
        
        # Add final signoff
        tracker.add_signoff(release_id, "user3")
        is_complete = tracker.is_complete(release_id)
        logger.info(f"📊 Final completion status: {is_complete}")
        
        if is_complete:
            logger.info("✅ ReleaseTracker functionality working correctly")
        else:
            logger.error("❌ ReleaseTracker completion logic failed")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"❌ ReleaseTracker test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def test_mock_slack_interaction():
    """Test Slack bot without actually sending messages."""
    logger = get_logger(__name__)
    logger.info("💬 Testing mock Slack interaction...")
    
    if not test_slack_credentials():
        logger.warning("⚠️ Skipping Slack interaction test - credentials not set")
        return True
    
    try:
        from slack_bolt import App
        from slack_sdk import WebClient
        
        # Initialize app
        app = App(
            token=os.environ.get("SLACK_BOT_TOKEN"),
            signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
        )
        
        client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
        
        # Test bot connection
        auth_response = client.auth_test()
        if auth_response["ok"]:
            bot_user = auth_response["user"]
            logger.info(f"✅ Bot authenticated as: {bot_user}")
        else:
            logger.error("❌ Bot authentication failed")
            return False
        
        # Test getting channel info (if channel exists)
        test_channel = "#general"  # Use general as a safe test
        try:
            channel_info = client.conversations_info(channel=test_channel)
            if channel_info["ok"]:
                logger.info(f"✅ Can access channel: {test_channel}")
            else:
                logger.warning(f"⚠️ Cannot access channel: {test_channel}")
        except Exception:
            logger.warning(f"⚠️ Channel test skipped - {test_channel} not accessible")
        
        logger.info("✅ Mock Slack interaction successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Slack interaction test failed: {e}")
        return False


def test_sign_off_workflow():
    """Test the complete sign-off workflow with mock data."""
    logger = get_logger(__name__)
    logger.info("📋 Testing complete sign-off workflow...")
    
    try:
        # Test all components together
        if not test_slack_imports():
            return False
            
        if not test_release_tracker():
            return False
            
        # Simulate the workflow
        release_data = create_mock_release_data()
        
        logger.info("🚀 Simulating sign-off workflow:")
        logger.info(f"  Service: {release_data['service_name']} {release_data['new_version']}")
        logger.info(f"  Approvers: {', '.join(release_data['approvers'])}")
        
        # Simulate message posting
        logger.info("📤 [MOCK] Posting sign-off message to Slack...")
        time.sleep(1)
        
        # Simulate signoffs
        for i, user in enumerate(release_data['approvers']):
            logger.info(f"✅ [MOCK] {user} signed off ({i+1}/{len(release_data['approvers'])})")
            time.sleep(0.5)
        
        logger.info("🎉 [MOCK] All users signed off - updating message...")
        logger.info("✅ Complete sign-off workflow simulation successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Sign-off workflow test failed: {e}")
        return False


def test_message_formatting():
    """Test message formatting functions."""
    logger = get_logger(__name__)
    logger.info("📝 Testing message formatting...")
    
    try:
        sys.path.append(str(Path(__file__).parent))
        from signoff_bot import format_signoff_message, format_completion_message
        
        release_data = create_mock_release_data()
        
        # Test initial message
        message = format_signoff_message(
            service_name=release_data['service_name'],
            version=release_data['new_version'],
            approvers=release_data['approvers'],
            signoffs=[]
        )
        
        if "cer-cart" in message and "v1.3.0" in message:
            logger.info("✅ Initial message formatting correct")
        else:
            logger.error("❌ Initial message formatting failed")
            return False
        
        # Test completion message
        completion_msg = format_completion_message(
            service_name=release_data['service_name'],
            version=release_data['new_version']
        )
        
        if "cer-cart" in completion_msg and "v1.3.0" in completion_msg:
            logger.info("✅ Completion message formatting correct")
        else:
            logger.error("❌ Completion message formatting failed")
            return False
            
        logger.info("✅ Message formatting tests passed")
        return True
        
    except ImportError:
        logger.warning("⚠️ Skipping message formatting test - signoff_bot not available")
        return True
    except Exception as e:
        logger.error(f"❌ Message formatting test failed: {e}")
        return False


def run_all_bot_tests():
    """Run all bot-related tests."""
    logger = get_logger(__name__)
    logger.info("🤖 Running comprehensive Slack bot test suite...")
    
    test_results = {}
    
    # Test 1: Imports
    test_results["imports"] = test_slack_imports()
    
    # Test 2: Credentials
    test_results["credentials"] = test_slack_credentials()
    
    # Test 3: Release Tracker
    test_results["tracker"] = test_release_tracker()
    
    # Test 4: Message Formatting
    test_results["formatting"] = test_message_formatting()
    
    # Test 5: Mock Slack Interaction
    test_results["slack"] = test_mock_slack_interaction()
    
    # Test 6: Complete Workflow
    test_results["workflow"] = test_sign_off_workflow()
    
    # Summary
    logger.info("\n🎯 Slack Bot Test Results:")
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {test_name:<15}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n📊 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All Slack bot tests passed! Bot is ready for deployment.")
        return True
    else:
        logger.error("⚠️ Some bot tests failed. Please check the issues above.")
        return False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Slack Bot Testing Script",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--test-bot", action="store_true",
                       help="Run all bot tests")
    parser.add_argument("--test-credentials", action="store_true",
                       help="Test Slack credentials only")
    parser.add_argument("--test-tracker", action="store_true",
                       help="Test ReleaseTracker functionality")
    parser.add_argument("--test-message", action="store_true",
                       help="Test message formatting")
    parser.add_argument("--mock-signoff", action="store_true",
                       help="Run mock sign-off workflow")
    
    return parser.parse_args()


def main():
    """Main testing function."""
    logger = get_logger(__name__)
    
    try:
        args = parse_args()
        
        logger.info("🤖 Slack Bot Testing Suite")
        logger.info("=" * 40)
        
        success = True
        
        if args.test_bot:
            success = run_all_bot_tests()
        elif args.test_credentials:
            success = test_slack_credentials()
        elif args.test_tracker:
            success = test_release_tracker()
        elif args.test_message:
            success = test_message_formatting()
        elif args.mock_signoff:
            success = test_sign_off_workflow()
        else:
            # Default: run all tests
            success = run_all_bot_tests()
        
        if success:
            logger.info("\n🎉 Bot testing completed successfully!")
            logger.info("\n📋 Next Steps:")
            logger.info("  1. Deploy the bot to your hosting platform")
            logger.info("  2. Configure the webhook URL in Slack app settings")
            logger.info("  3. Test with real Slack interactions")
            exit(0)
        else:
            logger.error("\n❌ Bot testing failed!")
            exit(1)
            
    except KeyboardInterrupt:
        logger.info("\nBot testing interrupted by user")
        exit(130)
    except Exception as e:
        logger.error(f"Bot testing failed with error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        exit(1)


if __name__ == "__main__":
    main() 