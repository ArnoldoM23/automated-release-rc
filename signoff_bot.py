#!/usr/bin/env python3
"""
Persistent Slack Bot for Release Sign-Off Tracking

This bot listens for mentions and updates sign-off messages in real-time.
Designed to work alongside the GitHub Actions workflow for document generation.
"""

import os
import re
import json
import logging
from typing import Dict, Set, List, Tuple
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Slack app
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)
client: WebClient = app.client

# In-memory state for sign-offs (use Redis for production persistence)
active_releases: Dict[str, Dict] = {}

class ReleaseTracker:
    """Manages sign-off state for active releases"""
    
    def __init__(self, release_id: str, channel: str, message_ts: str, prs: List[Dict]):
        self.release_id = release_id
        self.channel = channel
        self.message_ts = message_ts
        self.prs = prs
        self.signoffs: Set[str] = set()
        
    def add_signoff(self, user_id: str) -> bool:
        """Add user sign-off and return True if all complete"""
        self.signoffs.add(user_id)
        return self.is_complete()
    
    def is_complete(self) -> bool:
        """Check if all PR authors have signed off"""
        required_users = {pr['author_id'] for pr in self.prs}
        return required_users.issubset(self.signoffs)
    
    def generate_message(self, service_name: str, version: str) -> str:
        """Generate the sign-off message with current status"""
        lines = [
            f"🚀 *Release for {service_name} {version}*",
            'Please sign off on your PRs by replying here with "done."',
            ""
        ]
        
        for pr in self.prs:
            status = "✅" if pr['author_id'] in self.signoffs else "❌"
            lines.append(f"• {status} <@{pr['author_id']}> — PR #{pr['number']}: {pr['title']}")
        
        return "\n".join(lines)

@app.event("app_mention")
def handle_signoff_mention(event, say, logger):
    """Handle mentions for sign-off tracking"""
    try:
        text = event["text"].lower()
        user_id = event["user"]
        channel = event["channel"]
        
        # Check if this is a "done" mention
        if "done" not in text:
            return
            
        # Find active release in this channel
        release_tracker = None
        for tracker in active_releases.values():
            if tracker.channel == channel:
                release_tracker = tracker
                break
                
        if not release_tracker:
            logger.info(f"No active release found in channel {channel}")
            return
            
        # Add sign-off
        was_complete = release_tracker.is_complete()
        release_tracker.add_signoff(user_id)
        
        # Update the message
        updated_message = release_tracker.generate_message(
            service_name=release_tracker.prs[0].get('service_name', 'Unknown'),
            version=release_tracker.prs[0].get('version', 'Unknown')
        )
        
        # Edit the original message
        client.chat_update(
            channel=channel,
            ts=release_tracker.message_ts,
            text=updated_message
        )
        
        # Check if all complete
        if not was_complete and release_tracker.is_complete():
            # Post completion message
            completion_message = (
                "✅ *All PRs signed off—RC ready to deploy!*\n"
                f"📊 Release artifacts: "
                f"[Download CRQ](https://github.com/{os.environ.get('GITHUB_REPOSITORY', '')}/actions) "
                f"[Download Release Notes](https://github.com/{os.environ.get('GITHUB_REPOSITORY', '')}/actions)"
            )
            
            say(completion_message)
            
            # Clean up completed release
            del active_releases[release_tracker.release_id]
            
        logger.info(f"Sign-off recorded for user {user_id} in release {release_tracker.release_id}")
        
    except SlackApiError as e:
        logger.error(f"Slack API error: {e.response['error']}")
    except Exception as e:
        logger.error(f"Error handling sign-off: {str(e)}")

@app.message("create-signoff")
def handle_create_signoff(message, say, logger):
    """Handle creation of new sign-off message (called by GitHub Actions)"""
    try:
        # Parse the message for release data
        # Expected format: "create-signoff {json_data}"
        text = message["text"]
        if not text.startswith("create-signoff "):
            return
            
        json_data = text.replace("create-signoff ", "")
        release_data = json.loads(json_data)
        
        # Extract release information
        service_name = release_data["service_name"]
        version = release_data["new_version"]
        prs = release_data["prs"]
        channel = message["channel"]
        
        # Create release tracker
        release_id = f"{service_name}-{version}"
        
        # Generate initial message
        tracker = ReleaseTracker(
            release_id=release_id,
            channel=channel,
            message_ts="",  # Will be set after posting
            prs=prs
        )
        
        initial_message = tracker.generate_message(service_name, version)
        
        # Post initial sign-off message
        response = say(initial_message)
        
        # Store message timestamp
        tracker.message_ts = response["ts"]
        active_releases[release_id] = tracker
        
        logger.info(f"Created sign-off tracking for release {release_id}")
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in create-signoff message: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating sign-off message: {str(e)}")

@app.command("/release-status")
def handle_release_status(ack, respond, command, logger):
    """Slash command to check active release status"""
    ack()
    
    try:
        if not active_releases:
            respond("No active releases currently being tracked.")
            return
            
        status_lines = ["📊 *Active Releases:*\n"]
        for release_id, tracker in active_releases.items():
            total_prs = len(tracker.prs)
            signed_off = len(tracker.signoffs)
            status_lines.append(f"• {release_id}: {signed_off}/{total_prs} signed off")
            
        respond("\n".join(status_lines))
        
    except Exception as e:
        logger.error(f"Error getting release status: {str(e)}")
        respond("Error retrieving release status.")

@app.error
def error_handler(error, body, logger):
    """Global error handler"""
    logger.error(f"Error: {error}")
    logger.error(f"Request body: {body}")

# Health check endpoint for deployment platforms
@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "active_releases": len(active_releases)}

def main():
    """Main entry point"""
    logger.info("Starting Release Sign-Off Bot...")
    
    # Validate environment variables
    required_env_vars = ["SLACK_BOT_TOKEN", "SLACK_SIGNING_SECRET"]
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        exit(1)
        
    # Start the app
    port = int(os.environ.get("PORT", 3000))
    app.start(port=port)

if __name__ == "__main__":
    main() 