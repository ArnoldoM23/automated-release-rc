# release_signoff_notifier.py

import json
import os
import time
import argparse
import threading
from datetime import datetime, timedelta
from pathlib import Path
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dataclasses import dataclass
from typing import List, Optional
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class SlackConfig:
    """Configuration for Slack notifications"""
    channel: str
    rc: str
    rc_manager: str
    cutoff_time_utc: str
    reminder_intervals: List[int]  # hours before cutoff
    authors: List[str]
    day1_date: str
    day2_date: str
    service_name: str = ""
    production_version: str = ""
    new_version: str = ""

class ReleaseSignoffNotifier:
    """Automated Slack sign-off collection and reminder system"""
    
    def __init__(self, config: SlackConfig, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.client = None
        self.scheduler = None
        
        if not dry_run:
            slack_token = os.getenv("SLACK_BOT_TOKEN")
            if not slack_token:
                raise EnvironmentError("SLACK_BOT_TOKEN environment variable not set")
            self.client = WebClient(token=slack_token)
        
        # Parse cutoff time
        self.cutoff_datetime = datetime.fromisoformat(config.cutoff_time_utc.replace('Z', '+00:00'))
        
        # Calculate reminder times
        self.reminder_times = []
        for hours_before in config.reminder_intervals:
            reminder_time = self.cutoff_datetime - timedelta(hours=hours_before)
            self.reminder_times.append(reminder_time)
        
        logger.info(f"Cutoff time: {self.cutoff_datetime}")
        logger.info(f"Reminder times: {self.reminder_times}")

    def post_message(self, text: str, blocks: Optional[List] = None) -> bool:
        """Post message to Slack channel with error handling"""
        if self.dry_run:
            print(f"\n🧪 DRY RUN - Would post to {self.config.channel}:")
            print("-" * 50)
            print(text)
            print("-" * 50)
            return True
        
        try:
            response = self.client.chat_postMessage(
                channel=self.config.channel,
                text=text,
                blocks=blocks
            )
            logger.info(f"✅ Message sent to {self.config.channel}")
            return True
        except SlackApiError as e:
            logger.error(f"❌ Slack API error: {e.response['error']}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False

    def create_initial_message(self) -> str:
        """Create the initial sign-off request message"""
        authors_list = "\n".join([f"• {author}" for author in self.config.authors])
        
        message = f"""🚀 **Release Sign-off Required**

Hi team! We've locked the release for:
• **Day 1**: {self.config.day1_date}
• **Day 2**: {self.config.day2_date}

**Service**: {self.config.service_name} ({self.config.production_version} → {self.config.new_version})

📋 **Please sign off on your PRs by**: `{self.config.cutoff_time_utc}`

**PR Authors requiring sign-off**:
{authors_list}

Thank you for your prompt response!
**RC**: {self.config.rc}"""
        
        return message

    def create_reminder_message(self, hours_remaining: int) -> str:
        """Create reminder message"""
        authors_list = "\n".join([f"• {author}" for author in self.config.authors])
        
        if hours_remaining <= 1:
            urgency = "🚨 **FINAL REMINDER**"
            time_desc = "less than 1 hour"
        elif hours_remaining <= 4:
            urgency = "⏰ **Reminder**"
            time_desc = f"{hours_remaining} hours"
        else:
            urgency = "🔔 **Gentle Reminder**"
            time_desc = f"{hours_remaining} hours"
        
        message = f"""{urgency}

Release sign-off deadline in **{time_desc}**: `{self.config.cutoff_time_utc}`

If you don't sign off by the deadline, your changes may need to be removed from this release.

**Pending sign-offs**:
{authors_list}

**RC**: {self.config.rc}"""
        
        return message

    def create_final_message(self, all_signed_off: bool = False) -> str:
        """Create final escalation or success message"""
        if all_signed_off:
            message = f"""✅ **All Sign-offs Complete!**

Great job team! All PR authors have signed off on their changes.

{self.config.rc}, you may proceed with the CRQ review and release process.

**Release Schedule**:
• **Day 1**: {self.config.day1_date}
• **Day 2**: {self.config.day2_date}"""
        else:
            authors_list = "\n".join([f"• {author}" for author in self.config.authors])
            
            message = f"""⚠️ **Sign-off Deadline Reached - Escalation Required**

The following PR authors have NOT signed off by the deadline `{self.config.cutoff_time_utc}`:

{authors_list}

{self.config.rc} {self.config.rc_manager}, please follow up immediately or consider removing these changes before CRQ submission.

**Next Steps**:
1. Contact authors directly for immediate sign-off
2. OR remove unsigned changes from release
3. Proceed with CRQ once resolved"""
        
        return message

    def send_initial_message(self):
        """Send the initial sign-off request"""
        logger.info("📤 Sending initial sign-off request...")
        message = self.create_initial_message()
        success = self.post_message(message)
        
        if success:
            logger.info("✅ Initial message sent successfully")
        else:
            logger.error("❌ Failed to send initial message")
        
        return success

    def send_reminder(self, hours_remaining: int):
        """Send reminder message"""
        logger.info(f"📤 Sending reminder ({hours_remaining}h remaining)...")
        message = self.create_reminder_message(hours_remaining)
        success = self.post_message(message)
        
        if success:
            logger.info(f"✅ Reminder sent ({hours_remaining}h remaining)")
        else:
            logger.error(f"❌ Failed to send reminder ({hours_remaining}h remaining)")
            # Retry once after 30 seconds
            time.sleep(30)
            logger.info("🔄 Retrying reminder...")
            self.post_message(message)
        
        return success

    def send_final_message(self, all_signed_off: bool = False):
        """Send final message (escalation or success)"""
        logger.info("📤 Sending final message...")
        message = self.create_final_message(all_signed_off)
        
        # Critical message - retry up to 3 times
        for attempt in range(3):
            success = self.post_message(message)
            if success:
                logger.info("✅ Final message sent successfully")
                return True
            else:
                logger.warning(f"⚠️ Final message failed (attempt {attempt + 1}/3)")
                if attempt < 2:
                    time.sleep(30)
        
        logger.error("❌ Failed to send final message after 3 attempts")
        return False

    def check_sign_off_status(self) -> bool:
        """Check if all authors have signed off (placeholder implementation)"""
        # This is a placeholder - in a real implementation, you might:
        # 1. Check reactions on the original message
        # 2. Look for sign-off messages in the channel
        # 3. Check a database or file for sign-off status
        # 4. Use GitHub PR approval status
        
        # For now, we'll simulate based on time (closer to deadline = less likely to be signed off)
        now = datetime.now(self.cutoff_datetime.tzinfo)
        time_remaining = (self.cutoff_datetime - now).total_seconds()
        
        # Simulate: if less than 30 minutes remaining, assume some people haven't signed off
        if time_remaining < 1800:  # 30 minutes
            return False
        else:
            return True  # Optimistic assumption for demo

    def run_simple_workflow(self):
        """Run a simple workflow without scheduling (for testing/demo)"""
        logger.info("🚀 Starting simple release sign-off workflow...")
        
        # Send initial message
        self.send_initial_message()
        
        # Get current time as timezone-aware
        now = datetime.now(self.cutoff_datetime.tzinfo)
        
        # Wait and send reminders
        for i, reminder_time in enumerate(self.reminder_times):
            time_to_wait = (reminder_time - now).total_seconds()
            
            if time_to_wait > 0:
                logger.info(f"⏳ Waiting {time_to_wait:.0f} seconds until reminder {i+1}...")
                if self.dry_run:
                    # In dry run, just wait a few seconds for demo
                    time.sleep(min(10, time_to_wait))
                else:
                    time.sleep(time_to_wait)
            
            # Update now time for next calculation
            now = datetime.now(self.cutoff_datetime.tzinfo)
            hours_remaining = (self.cutoff_datetime - now).total_seconds() / 3600
            self.send_reminder(int(max(0, hours_remaining)))
        
        # Wait until cutoff time
        now = datetime.now(self.cutoff_datetime.tzinfo)
        time_to_cutoff = (self.cutoff_datetime - now).total_seconds()
        if time_to_cutoff > 0:
            logger.info(f"⏳ Waiting {time_to_cutoff:.0f} seconds until cutoff...")
            if self.dry_run:
                time.sleep(5)  # Short wait for demo
            else:
                time.sleep(time_to_cutoff)
        
        # Check final status and send final message
        all_signed_off = self.check_sign_off_status()
        self.send_final_message(all_signed_off)
        
        logger.info("🎉 Release sign-off workflow completed!")

    def run_scheduled_workflow(self):
        """Run workflow with proper scheduling (for production)"""
        logger.info("🚀 Starting scheduled release sign-off workflow...")
        
        # Create scheduler
        self.scheduler = BlockingScheduler()
        
        # Send initial message immediately
        self.send_initial_message()
        
        # Schedule reminders
        for i, reminder_time in enumerate(self.reminder_times):
            hours_remaining = self.config.reminder_intervals[i]
            self.scheduler.add_job(
                func=self.send_reminder,
                trigger="date",
                run_date=reminder_time,
                args=[hours_remaining],
                id=f"reminder_{i+1}"
            )
            logger.info(f"📅 Scheduled reminder {i+1} for {reminder_time}")
        
        # Schedule final message
        self.scheduler.add_job(
            func=lambda: self.send_final_message(self.check_sign_off_status()),
            trigger="date",
            run_date=self.cutoff_datetime,
            id="final_message"
        )
        logger.info(f"📅 Scheduled final message for {self.cutoff_datetime}")
        
        # Start scheduler
        try:
            logger.info("⏰ Scheduler started - waiting for scheduled events...")
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("⏹️ Scheduler stopped")

def load_slack_config(config_path: str) -> SlackConfig:
    """Load Slack configuration from JSON file"""
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    return SlackConfig(
        channel=config_data["channel"],
        rc=config_data["rc"],
        rc_manager=config_data["rc_manager"],
        cutoff_time_utc=config_data["cutoff_time_utc"],
        reminder_intervals=config_data["reminder_intervals"],
        authors=config_data["authors"],
        day1_date=config_data["day1_date"],
        day2_date=config_data["day2_date"],
        service_name=config_data.get("service_name", ""),
        production_version=config_data.get("production_version", ""),
        new_version=config_data.get("new_version", "")
    )

def send_release_signoff_notifications(config_dict: dict):
    """Legacy function to maintain compatibility with original code"""
    # Convert dict to SlackConfig
    slack_config = SlackConfig(
        channel="#releases",
        rc=f"@{config_dict['rc']}",
        rc_manager=f"@{config_dict['rc_manager']}",
        cutoff_time_utc=config_dict["cutoff_time"],
        reminder_intervals=[4, 1],  # Default intervals
        authors=[],  # Would need to be populated from PR data
        day1_date=config_dict["day1_date"],
        day2_date=config_dict["day2_date"],
        service_name=config_dict.get("service_name", ""),
        production_version=config_dict.get("production_version", ""),
        new_version=config_dict.get("new_version", "")
    )
    
    notifier = ReleaseSignoffNotifier(slack_config)
    notifier.run_simple_workflow()

def main():
    """Main entry point for the release sign-off notifier"""
    parser = argparse.ArgumentParser(description="Release Sign-off Notifier")
    parser.add_argument("--config", required=True, help="Path to Slack configuration JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode - print messages instead of sending")
    parser.add_argument("--simple", action="store_true", help="Use simple workflow (for testing)")
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_slack_config(args.config)
        logger.info(f"📄 Loaded config from {args.config}")
        logger.info(f"📱 Channel: {config.channel}")
        logger.info(f"👥 Authors: {len(config.authors)} people")
        logger.info(f"⏰ Cutoff: {config.cutoff_time_utc}")
        
        # Create and run notifier
        notifier = ReleaseSignoffNotifier(config, dry_run=args.dry_run)
        
        if args.simple or args.dry_run:
            notifier.run_simple_workflow()
        else:
            notifier.run_scheduled_workflow()
        
    except FileNotFoundError:
        logger.error(f"❌ Configuration file not found: {args.config}")
        return 1
    except KeyError as e:
        logger.error(f"❌ Missing required configuration key: {e}")
        return 1
    except Exception as e:
        logger.error(f"❌ Notifier failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    exit(main()) 