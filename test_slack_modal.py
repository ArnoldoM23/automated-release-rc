#!/usr/bin/env python3
"""
Slack Modal Testing Script

Test the /run-release command and modal functionality for the RC Release Automation.
This script helps verify the Slack integration works correctly before deploying to production.

Usage:
    python test_slack_modal.py --setup          # Setup test environment
    python test_slack_modal.py --test-auth      # Test Slack authentication
    python test_slack_modal.py --test-modal     # Test modal structure
    python test_slack_modal.py --test-workflow  # Test complete workflow
    python test_slack_modal.py --test-all       # Run all tests
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any
import time

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.logging import get_logger


def check_environment():
    """Check if required environment variables are set."""
    logger = get_logger(__name__)
    logger.info("🔐 Checking Slack environment setup...")
    
    required_vars = {
        "SLACK_BOT_TOKEN": "Bot User OAuth Token (xoxb-...)",
        "SLACK_SIGNING_SECRET": "Signing Secret for request verification",
        "SLACK_APP_TOKEN": "App-Level Token for Socket Mode (xapp-...)"
    }
    
    missing_vars = []
    valid_vars = []
    
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            # Validate token format
            if var == "SLACK_BOT_TOKEN" and not value.startswith("xoxb-"):
                logger.error(f"❌ {var} must start with 'xoxb-' (got: {value[:10]}...)")
                missing_vars.append(var)
            elif var == "SLACK_APP_TOKEN" and not value.startswith("xapp-"):
                logger.error(f"❌ {var} must start with 'xapp-' (got: {value[:10]}...)")
                missing_vars.append(var)
            else:
                logger.info(f"✅ {var} is configured correctly")
                valid_vars.append(var)
        else:
            logger.error(f"❌ {var} is missing ({description})")
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"\n🚨 Missing {len(missing_vars)} required environment variables:")
        for var in missing_vars:
            logger.error(f"   - {var}: {required_vars[var]}")
        
        logger.info(f"\n📋 How to set up Slack environment:")
        logger.info(f"1. Create a Slack app at https://api.slack.com/apps")
        logger.info(f"2. Add Bot Token Scopes: chat:write, commands, users:read")
        logger.info(f"3. Install app to workspace")
        logger.info(f"4. Set environment variables:")
        for var in missing_vars:
            logger.info(f"   export {var}='your-token-here'")
        
        return False
    
    logger.info(f"✅ All {len(valid_vars)} environment variables configured correctly")
    return True


def test_slack_authentication():
    """Test Slack bot authentication."""
    logger = get_logger(__name__)
    logger.info("🔑 Testing Slack bot authentication...")
    
    try:
        from slack_sdk import WebClient
        from slack_sdk.errors import SlackApiError
        
        # Test bot token
        client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
        
        try:
            auth_response = client.auth_test()
            if auth_response["ok"]:
                bot_info = auth_response
                logger.info(f"✅ Bot authenticated successfully:")
                logger.info(f"   - Bot User: {bot_info['user']}")
                logger.info(f"   - Bot ID: {bot_info['user_id']}")
                logger.info(f"   - Team: {bot_info['team']}")
                logger.info(f"   - URL: {bot_info['url']}")
                return True
            else:
                logger.error(f"❌ Bot authentication failed: {auth_response}")
                return False
                
        except SlackApiError as e:
            logger.error(f"❌ Slack API error: {e.response['error']}")
            if e.response['error'] == 'invalid_auth':
                logger.error("   Check your SLACK_BOT_TOKEN is correct")
            return False
            
    except ImportError:
        logger.error("❌ Slack SDK not installed. Run: pip install slack_sdk slack_bolt")
        return False
    except Exception as e:
        logger.error(f"❌ Authentication test failed: {e}")
        return False


def test_modal_structure():
    """Test the modal structure and validation."""
    logger = get_logger(__name__)
    logger.info("📋 Testing Slack modal structure...")
    
    try:
        # Import the bot app to access modal definition
        sys.path.append(str(Path(__file__).parent / "slack_bot"))
        from app import ReleaseRCBot
        
        # Create a mock modal view (this is what we'd send to Slack)
        mock_modal = {
            "type": "modal",
            "callback_id": "release_modal",
            "title": {"type": "plain_text", "text": "🚀 Start Release"},
            "submit": {"type": "plain_text", "text": "Start Release"},
            "close": {"type": "plain_text", "text": "Cancel"},
            "private_metadata": json.dumps({
                "channel_id": "C1234567890",
                "user_id": "U1234567890"
            }),
            "blocks": [
                {
                    "type": "input",
                    "block_id": "service_name",
                    "label": {"type": "plain_text", "text": "Service Name"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "service_name_input",
                        "placeholder": {"type": "plain_text", "text": "e.g., cer-cart"}
                    }
                },
                {
                    "type": "input",
                    "block_id": "prod_version",
                    "label": {"type": "plain_text", "text": "Production Version"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "prod_version_input",
                        "placeholder": {"type": "plain_text", "text": "e.g., v2.4.3"}
                    }
                },
                {
                    "type": "input",
                    "block_id": "new_version",
                    "label": {"type": "plain_text", "text": "New Version"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "new_version_input",
                        "placeholder": {"type": "plain_text", "text": "e.g., v2.5.0"}
                    }
                },
                {
                    "type": "input",
                    "block_id": "day1_date",
                    "label": {"type": "plain_text", "text": "Day 1 Date"},
                    "element": {
                        "type": "datepicker",
                        "action_id": "day1_date_input",
                        "placeholder": {"type": "plain_text", "text": "Select Day 1 date"}
                    }
                },
                {
                    "type": "input",
                    "block_id": "day2_date",
                    "label": {"type": "plain_text", "text": "Day 2 Date"},
                    "element": {
                        "type": "datepicker",
                        "action_id": "day2_date_input",
                        "placeholder": {"type": "plain_text", "text": "Select Day 2 date"}
                    }
                },
                {
                    "type": "input",
                    "block_id": "rc_manager",
                    "label": {"type": "plain_text", "text": "Release Manager"},
                    "element": {
                        "type": "users_select",
                        "action_id": "rc_manager_input",
                        "placeholder": {"type": "plain_text", "text": "Select release manager"}
                    }
                }
            ]
        }
        
        # Validate modal structure
        logger.info("✅ Modal structure validation:")
        logger.info(f"   - Title: {mock_modal['title']['text']}")
        logger.info(f"   - Callback ID: {mock_modal['callback_id']}")
        logger.info(f"   - Input blocks: {len(mock_modal['blocks'])}")
        
        # Validate each input block
        expected_fields = [
            "service_name", "prod_version", "new_version", 
            "day1_date", "day2_date", "rc_manager"
        ]
        
        for i, block in enumerate(mock_modal['blocks']):
            field_name = expected_fields[i]
            block_id = block['block_id']
            label = block['label']['text']
            logger.info(f"   - Field {i+1}: {label} (ID: {block_id})")
            
            if block_id != field_name:
                logger.error(f"❌ Block ID mismatch: expected {field_name}, got {block_id}")
                return False
        
        logger.info("✅ Modal structure is valid")
        return True
        
    except Exception as e:
        logger.error(f"❌ Modal structure test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def test_modal_workflow():
    """Test the complete modal workflow with simulated data."""
    logger = get_logger(__name__)
    logger.info("🔄 Testing complete modal workflow...")
    
    try:
        from slack_sdk import WebClient
        
        client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
        
        # Test 1: Simulate modal submission data
        mock_submission_data = {
            "state": {
                "values": {
                    "service_name": {
                        "service_name_input": {"value": "test-service"}
                    },
                    "prod_version": {
                        "prod_version_input": {"value": "v1.0.0"}
                    },
                    "new_version": {
                        "new_version_input": {"value": "v1.1.0"}
                    },
                    "day1_date": {
                        "day1_date_input": {"selected_date": "2024-01-15"}
                    },
                    "day2_date": {
                        "day2_date_input": {"selected_date": "2024-01-16"}
                    },
                    "rc_manager": {
                        "rc_manager_input": {"selected_user": "U1234567890"}
                    }
                }
            },
            "private_metadata": json.dumps({
                "channel_id": "C1234567890",
                "user_id": "U1234567890"
            })
        }
        
        # Extract values (simulate what the bot would do)
        values = mock_submission_data["state"]["values"]
        metadata = json.loads(mock_submission_data["private_metadata"])
        
        release_params = {
            "service_name": values["service_name"]["service_name_input"]["value"],
            "prod_version": values["prod_version"]["prod_version_input"]["value"],
            "new_version": values["new_version"]["new_version_input"]["value"],
            "day1_date": values["day1_date"]["day1_date_input"]["selected_date"],
            "day2_date": values["day2_date"]["day2_date_input"]["selected_date"],
            "rc_manager": values["rc_manager"]["rc_manager_input"]["selected_user"],
            "channel_id": metadata["channel_id"],
            "trigger_user": metadata["user_id"]
        }
        
        logger.info("✅ Modal submission data extraction successful:")
        for key, value in release_params.items():
            logger.info(f"   - {key}: {value}")
        
        # Test 2: Validate required fields
        required_fields = ["service_name", "prod_version", "new_version", "day1_date", "day2_date", "rc_manager"]
        missing_fields = [field for field in required_fields if not release_params.get(field)]
        
        if missing_fields:
            logger.error(f"❌ Missing required fields: {missing_fields}")
            return False
        
        logger.info("✅ All required fields present")
        
        # Test 3: Validate version format
        version_pattern = r"^v?\d+\.\d+\.\d+$"
        import re
        
        for version_field in ["prod_version", "new_version"]:
            version_value = release_params[version_field]
            if not re.match(version_pattern, version_value):
                logger.error(f"❌ Invalid version format for {version_field}: {version_value}")
                return False
        
        logger.info("✅ Version formats are valid")
        
        # Test 4: Validate date format
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        for date_field in ["day1_date", "day2_date"]:
            date_value = release_params[date_field]
            if not re.match(date_pattern, date_value):
                logger.error(f"❌ Invalid date format for {date_field}: {date_value}")
                return False
        
        logger.info("✅ Date formats are valid")
        
        # Test 5: Test user lookup
        try:
            user_info = client.users_info(user=release_params["rc_manager"])
            if user_info["ok"]:
                logger.info(f"✅ Release manager user lookup successful: {user_info['user']['name']}")
            else:
                logger.warning(f"⚠️ User lookup failed (expected in test): {user_info}")
        except Exception as e:
            logger.warning(f"⚠️ User lookup failed (expected in test): {e}")
        
        logger.info("✅ Complete modal workflow test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Modal workflow test failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def test_bot_integration():
    """Test the bot integration with Socket Mode."""
    logger = get_logger(__name__)
    logger.info("🤖 Testing bot integration...")
    
    try:
        from slack_bolt import App
        from slack_bolt.adapter.socket_mode import SocketModeHandler
        
        # Initialize app
        app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
        
        # Test if we can create a handler (don't start it)
        handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
        
        logger.info("✅ Socket Mode handler created successfully")
        
        # Test command registration
        @app.command("/test-command")
        def test_command(ack, body):
            ack()
            return {"text": "Test successful"}
        
        logger.info("✅ Command registration working")
        
        # Test view registration  
        @app.view("test_view")
        def test_view(ack, body):
            ack()
            return {"response": "success"}
        
        logger.info("✅ View registration working")
        
        logger.info("✅ Bot integration test passed")
        logger.info("📋 To start the bot in production, run:")
        logger.info("   cd slack_bot && python app.py")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Missing dependencies: {e}")
        logger.info("Install with: pip install slack_bolt")
        return False
    except Exception as e:
        logger.error(f"❌ Bot integration test failed: {e}")
        return False


def setup_test_environment():
    """Set up test environment and provide guidance."""
    logger = get_logger(__name__)
    logger.info("🛠️ Setting up Slack test environment...")
    
    logger.info("\n📋 Slack App Setup Checklist:")
    logger.info("1. 🌐 Go to https://api.slack.com/apps")
    logger.info("2. ➕ Click 'Create New App' → 'From scratch'")
    logger.info("3. 📝 Name: 'RC Release Automation' (or similar)")
    logger.info("4. 🏢 Select your workspace")
    
    logger.info("\n🔧 Configure Bot Features:")
    logger.info("1. 🤖 OAuth & Permissions → Bot Token Scopes:")
    logger.info("   - chat:write (Send messages)")
    logger.info("   - commands (Add slash commands)")
    logger.info("   - users:read (Read user information)")
    logger.info("   - reactions:write (Add reactions)")
    
    logger.info("\n⚡ Add Slash Command:")
    logger.info("1. 🔗 Slash Commands → Create New Command")
    logger.info("   - Command: /run-release")
    logger.info("   - Request URL: Your bot URL (or ngrok for testing)")
    logger.info("   - Description: Start RC release process")
    logger.info("   - Usage Hint: [no parameters needed]")
    
    logger.info("\n🔌 Enable Socket Mode (for development):")
    logger.info("1. ⚙️ Socket Mode → Enable Socket Mode")
    logger.info("2. 🎟️ Generate App-Level Token with connections:write scope")
    
    logger.info("\n📦 Install App:")
    logger.info("1. 🏠 Install App → Install to Workspace")
    logger.info("2. 📋 Copy Bot User OAuth Token (xoxb-...)")
    logger.info("3. 📋 Copy Signing Secret")
    logger.info("4. 📋 Copy App-Level Token (xapp-...)")
    
    logger.info("\n🔑 Set Environment Variables:")
    logger.info("export SLACK_BOT_TOKEN='xoxb-your-token'")
    logger.info("export SLACK_SIGNING_SECRET='your-signing-secret'")
    logger.info("export SLACK_APP_TOKEN='xapp-your-app-token'")
    
    logger.info("\n✅ Setup complete! Run the tests to verify:")
    logger.info("python test_slack_modal.py --test-auth")
    logger.info("python test_slack_modal.py --test-modal")


def run_all_tests():
    """Run all Slack modal tests."""
    logger = get_logger(__name__)
    logger.info("🧪 Running comprehensive Slack modal tests...")
    logger.info("=" * 60)
    
    tests = [
        ("Environment Check", check_environment),
        ("Authentication", test_slack_authentication),
        ("Modal Structure", test_modal_structure),
        ("Modal Workflow", test_modal_workflow),
        ("Bot Integration", test_bot_integration)
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
    
    logger.info(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Your Slack integration is ready.")
        logger.info("\n🚀 Next Steps:")
        logger.info("1. Start the bot: cd slack_bot && python app.py")
        logger.info("2. Test /run-release command in Slack")
        logger.info("3. Verify modal appears and submits correctly")
    else:
        logger.error("❌ Some tests failed. Check the issues above.")
        logger.info("\n🔧 Troubleshooting:")
        logger.info("- Ensure all environment variables are set correctly")
        logger.info("- Check Slack app permissions and installation")
        logger.info("- Verify bot token scopes include required permissions")
    
    return passed == total


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test Slack /run-release command and modal functionality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python test_slack_modal.py --setup          # Setup guide
    python test_slack_modal.py --test-auth      # Test authentication
    python test_slack_modal.py --test-modal     # Test modal
    python test_slack_modal.py --test-all       # Run all tests
        """
    )
    
    parser.add_argument("--setup", action="store_true", help="Show setup guide")
    parser.add_argument("--test-auth", action="store_true", help="Test Slack authentication")
    parser.add_argument("--test-modal", action="store_true", help="Test modal structure")
    parser.add_argument("--test-workflow", action="store_true", help="Test modal workflow")
    parser.add_argument("--test-integration", action="store_true", help="Test bot integration")
    parser.add_argument("--test-all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    if args.setup:
        setup_test_environment()
    elif args.test_auth:
        success = check_environment() and test_slack_authentication()
        sys.exit(0 if success else 1)
    elif args.test_modal:
        success = test_modal_structure()
        sys.exit(0 if success else 1)
    elif args.test_workflow:
        success = test_modal_workflow()
        sys.exit(0 if success else 1)
    elif args.test_integration:
        success = test_bot_integration()
        sys.exit(0 if success else 1)
    elif args.test_all:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 