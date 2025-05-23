#!/usr/bin/env python3
"""
Release RC Slack Bot

Enterprise Slack bot for managing PR sign-off workflows and release coordination.
Handles announcement messages, periodic reminders, developer sign-offs, and cut-off logic.
"""

import json
import os
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Set, Optional
from dataclasses import dataclass, field
from threading import Lock

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PRInfo:
    """PR information for sign-off tracking."""
    number: int
    html_url: str
    author: str  # Slack handle
    title: str
    labels: List[str] = field(default_factory=list)
    signed_off: bool = False

@dataclass 
class ReleaseSession:
    """Active release sign-off session."""
    service: str
    version: str
    day1_date: str
    day2_date: str
    signoff_cutoff_time: str
    rc_slack_handle: str
    channel_id: str
    thread_ts: str
    prs: List[PRInfo]
    created_at: datetime = field(default_factory=datetime.now)
    reminder_job_id: str = None
    cutoff_job_id: str = None
    trigger_user: str = ""  # User who triggered the release
    
    @property
    def pending_authors(self) -> Set[str]:
        """Get set of authors who haven't signed off."""
        return {pr.author for pr in self.prs if not pr.signed_off}
    
    @property
    def signed_off_authors(self) -> Set[str]:
        """Get set of authors who have signed off."""
        return {pr.author for pr in self.prs if pr.signed_off}

class ReleaseRCBot:
    """Release RC Slack bot for managing PR sign-off workflows."""
    
    def __init__(self):
        # Initialize Slack app
        self.app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
        self.client = self.app.client
        
        # Active release sessions (in production, use Redis)
        self.sessions: Dict[str, ReleaseSession] = {}
        self.sessions_lock = Lock()
        
        # Configuration
        self.config = {
            "reminder_interval_hours": int(os.environ.get("REMINDER_INTERVAL_HOURS", "2")),
            "default_channel": os.environ.get("RELEASE_CHANNEL", "#release-rc"),
            "timezone": os.environ.get("TIMEZONE", "America/Los_Angeles")
        }
        
        # Setup scheduler for reminders and cutoffs
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        
        # Register event handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register Slack event handlers."""
        
        @self.app.command("/run-release")
        def handle_run_release_command(ack, body, client, say):
            """Handle /run-release slash command."""
            ack()
            
            try:
                user_id = body["user_id"]
                channel_id = body["channel_id"]
                trigger_id = body["trigger_id"]
                
                # Open modal for release parameters
                modal_view = {
                    "type": "modal",
                    "callback_id": "release_modal",
                    "title": {"type": "plain_text", "text": "🚀 Start Release"},
                    "submit": {"type": "plain_text", "text": "Start Release"},
                    "close": {"type": "plain_text", "text": "Cancel"},
                    "private_metadata": json.dumps({
                        "channel_id": channel_id,
                        "user_id": user_id
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
                
                client.views_open(trigger_id=trigger_id, view=modal_view)
                
            except Exception as e:
                logger.error(f"Error handling /run-release command: {e}")
                say(f"❌ Error: {str(e)}")
        
        @self.app.view("release_modal")
        def handle_release_modal_submission(ack, body, client, view):
            """Handle release modal submission."""
            ack()
            
            try:
                # Extract metadata
                metadata = json.loads(view["private_metadata"])
                channel_id = metadata["channel_id"]
                user_id = metadata["user_id"]
                
                # Extract form values
                values = view["state"]["values"]
                
                release_params = {
                    "service_name": values["service_name"]["service_name_input"]["value"],
                    "prod_version": values["prod_version"]["prod_version_input"]["value"],
                    "new_version": values["new_version"]["new_version_input"]["value"],
                    "day1_date": values["day1_date"]["day1_date_input"]["selected_date"],
                    "day2_date": values["day2_date"]["day2_date_input"]["selected_date"],
                    "rc_manager": values["rc_manager"]["rc_manager_input"]["selected_user"],
                    "channel_id": channel_id,
                    "trigger_user": user_id
                }
                
                # Post confirmation message
                client.chat_postMessage(
                    channel=channel_id,
                    text=f"🚀 Starting release process for *{release_params['service_name']} {release_params['new_version']}*...\n\nFetching PRs and generating documentation. This may take a moment."
                )
                
                # Here you would trigger the GitHub Actions workflow
                # For now, we'll simulate with a mock response
                self._simulate_github_actions_trigger(release_params, client)
                
            except Exception as e:
                logger.error(f"Error handling modal submission: {e}")
                client.chat_postMessage(
                    channel=channel_id,
                    text=f"❌ Error processing release request: {str(e)}"
                )
        
        @self.app.message(re.compile(r"@release_rc\s+(signed off|signoff)", re.IGNORECASE))
        def handle_signoff(message, say, client):
            """Handle developer sign-off messages."""
            try:
                user_id = message["user"]
                channel_id = message["channel"]
                thread_ts = message.get("thread_ts")
                
                if not thread_ts:
                    say("❌ Sign-off commands must be used in the release thread.", thread_ts=message["ts"])
                    return
                
                session = self._get_session_by_thread(thread_ts)
                if not session:
                    say("❌ No active release session found for this thread.", thread_ts=thread_ts)
                    return
                
                # Get user info to find Slack handle
                user_info = client.users_info(user=user_id)
                username = user_info["user"]["name"]
                
                # Mark user as signed off
                signed_off = self._mark_user_signed_off(session, username)
                
                if signed_off:
                    # React with checkmark
                    client.reactions_add(
                        channel=channel_id,
                        timestamp=message["ts"],
                        name="white_check_mark"
                    )
                    
                    say(f"✅ <@{user_id}> signed off! Thank you.", thread_ts=thread_ts)
                    
                    # Check if all users have signed off
                    if not session.pending_authors:
                        self._handle_all_signed_off(session)
                else:
                    say(f"❌ <@{user_id}> - No pending PRs found for your account.", thread_ts=thread_ts)
                
            except Exception as e:
                logger.error(f"Error handling sign-off: {e}")
                say("❌ Error processing sign-off. Please try again.", thread_ts=message.get("thread_ts"))
        
        @self.app.message(re.compile(r"@release_rc\s+abort", re.IGNORECASE))
        def handle_abort(message, say):
            """Handle abort command."""
            try:
                thread_ts = message.get("thread_ts")
                
                if not thread_ts:
                    say("❌ Abort command must be used in the release thread.", thread_ts=message["ts"])
                    return
                
                session = self._get_session_by_thread(thread_ts)
                if not session:
                    say("❌ No active release session found for this thread.", thread_ts=thread_ts)
                    return
                
                # Cancel scheduled jobs
                self._cancel_session_jobs(session)
                
                # Remove session
                with self.sessions_lock:
                    if session.thread_ts in self.sessions:
                        del self.sessions[session.thread_ts]
                
                say("🛑 Release workflow aborted. All reminders cancelled. You can trigger a new workflow anytime.", 
                    thread_ts=thread_ts)
                
                logger.info(f"Release session aborted for {session.service} v{session.version}")
                
            except Exception as e:
                logger.error(f"Error handling abort: {e}")
                say("❌ Error processing abort command.", thread_ts=message.get("thread_ts"))
        
        @self.app.message(re.compile(r"@release_rc\s+status", re.IGNORECASE))
        def handle_status(message, say):
            """Handle status command."""
            try:
                thread_ts = message.get("thread_ts")
                
                if not thread_ts:
                    say("❌ Status command must be used in the release thread.", thread_ts=message["ts"])
                    return
                
                session = self._get_session_by_thread(thread_ts)
                if not session:
                    say("❌ No active release session found for this thread.", thread_ts=thread_ts)
                    return
                
                # Generate status message
                status_msg = self._generate_status_message(session)
                say(status_msg, thread_ts=thread_ts)
                
            except Exception as e:
                logger.error(f"Error handling status: {e}")
                say("❌ Error getting status.", thread_ts=message.get("thread_ts"))
    
    def _simulate_github_actions_trigger(self, release_params: Dict, client):
        """Simulate triggering GitHub Actions workflow (for demo purposes)."""
        try:
            # In a real implementation, this would trigger the GitHub Actions workflow
            # For now, simulate with mock PR data
            mock_prs = [
                {
                    "number": 123,
                    "html_url": "https://github.com/org/repo/pull/123",
                    "title": "Add new payment validation",
                    "user": {"login": "alice"},
                    "labels": [{"name": "feature"}]
                },
                {
                    "number": 124,
                    "html_url": "https://github.com/org/repo/pull/124",
                    "title": "Fix cart calculation bug",
                    "user": {"login": "bob"},
                    "labels": [{"name": "bugfix"}]
                }
            ]
            
            # Prepare release metadata
            release_metadata = {
                "service": release_params["service_name"],
                "version": release_params["new_version"],
                "day1_date": release_params["day1_date"],
                "day2_date": release_params["day2_date"],
                "signoff_cutoff_time": "12:00 PM tomorrow",
                "rc_slack_handle": f"<@{release_params['rc_manager']}>",
                "channel_id": release_params["channel_id"],
                "trigger_user": release_params["trigger_user"]
            }
            
            # Start the release session
            result = self.start_release_session(mock_prs, release_metadata)
            
            if not result.get("success"):
                client.chat_postMessage(
                    channel=release_params["channel_id"],
                    text=f"❌ Failed to start release session: {result.get('error', 'Unknown error')}"
                )
            
        except Exception as e:
            logger.error(f"Error simulating GitHub Actions trigger: {e}")
            client.chat_postMessage(
                channel=release_params["channel_id"],
                text=f"❌ Error starting release process: {str(e)}"
            )
    
    def start_release_session(self, prs_data: List[Dict], release_metadata: Dict) -> Dict:
        """
        Start a new release sign-off session.
        
        Args:
            prs_data: List of PR objects with number, html_url, user.login, etc.
            release_metadata: Dict with service, version, dates, rc_handle, etc.
        
        Returns:
            Dict with session info and thread details
        """
        try:
            # Parse PR data
            prs = []
            for pr_data in prs_data:
                pr = PRInfo(
                    number=pr_data["number"],
                    html_url=pr_data["html_url"],
                    author=pr_data["user"]["login"],
                    title=pr_data.get("title", ""),
                    labels=[label.get("name", "") for label in pr_data.get("labels", [])]
                )
                prs.append(pr)
            
            # Use the channel from metadata (where command was triggered)
            channel_id = release_metadata.get("channel_id", self.config["default_channel"])
            
            # Create session
            session = ReleaseSession(
                service=release_metadata["service"],
                version=release_metadata["version"],
                day1_date=release_metadata["day1_date"],
                day2_date=release_metadata["day2_date"],
                signoff_cutoff_time=release_metadata["signoff_cutoff_time"],
                rc_slack_handle=release_metadata["rc_slack_handle"],
                channel_id=channel_id,
                thread_ts="",  # Will be set after posting
                prs=prs,
                trigger_user=release_metadata.get("trigger_user", "")
            )
            
            # Post announcement message
            announcement = self._generate_announcement_message(session)
            result = self.client.chat_postMessage(
                channel=channel_id,
                text=announcement,
                mrkdwn=True
            )
            
            # Update session with thread timestamp
            session.thread_ts = result["ts"]
            
            # Store session
            with self.sessions_lock:
                self.sessions[session.thread_ts] = session
            
            # Schedule periodic reminders
            self._schedule_reminders(session)
            
            # Schedule cutoff handling
            self._schedule_cutoff(session)
            
            logger.info(f"Started release session for {session.service} v{session.version} in channel {channel_id}")
            
            return {
                "success": True,
                "channel_id": channel_id,
                "thread_ts": session.thread_ts,
                "message": "Release sign-off session started successfully"
            }
            
        except Exception as e:
            logger.error(f"Error starting release session: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_announcement_message(self, session: ReleaseSession) -> str:
        """Generate the initial announcement message."""
        pr_list = []
        for pr in session.prs:
            pr_list.append(f"• ❌ <@{pr.author}> — <{pr.html_url}|PR #{pr.number}>: {pr.title}")
        
        trigger_mention = f"\n\nTriggered by: <@{session.trigger_user}>" if session.trigger_user else ""
        
        return f"""Hi team! 🚀

Release *{session.service} v{session.version}* is scheduled for:
• Day 1 (prep): {session.day1_date}
• Day 2 (deploy): {session.day2_date}

Please sign off on your PRs by *{session.signoff_cutoff_time}*:

{chr(10).join(pr_list)}

To sign off, reply in this thread: `@release_rc signed off`
For status: `@release_rc status`
To abort: `@release_rc abort`

Release Coordinator: {session.rc_slack_handle}{trigger_mention}"""
    
    def _generate_status_message(self, session: ReleaseSession) -> str:
        """Generate status message showing current sign-off state."""
        signed_off = []
        pending = []
        
        for pr in session.prs:
            if pr.signed_off:
                signed_off.append(f"• ✅ <@{pr.author}> — PR #{pr.number}")
            else:
                pending.append(f"• ❌ <@{pr.author}> — PR #{pr.number}")
        
        msg = f"📊 *Sign-off Status for {session.service} v{session.version}*\n\n"
        
        if signed_off:
            msg += "*Completed:*\n" + "\n".join(signed_off) + "\n\n"
        
        if pending:
            msg += "*Pending:*\n" + "\n".join(pending) + "\n\n"
            msg += f"⏰ Cutoff: {session.signoff_cutoff_time}"
        else:
            msg += "🎉 All PRs signed off!"
        
        return msg
    
    def _mark_user_signed_off(self, session: ReleaseSession, username: str) -> bool:
        """Mark a user as signed off. Returns True if user had pending PRs."""
        signed_off_any = False
        for pr in session.prs:
            if pr.author == username and not pr.signed_off:
                pr.signed_off = True
                signed_off_any = True
        return signed_off_any
    
    def _get_session_by_thread(self, thread_ts: str) -> Optional[ReleaseSession]:
        """Get session by thread timestamp."""
        with self.sessions_lock:
            return self.sessions.get(thread_ts)
    
    def _schedule_reminders(self, session: ReleaseSession):
        """Schedule periodic reminder messages."""
        try:
            job_id = f"reminder_{session.thread_ts}"
            
            self.scheduler.add_job(
                func=self._send_reminder,
                trigger=IntervalTrigger(hours=self.config["reminder_interval_hours"]),
                args=[session.thread_ts],
                id=job_id,
                max_instances=1
            )
            
            session.reminder_job_id = job_id
            logger.info(f"Scheduled reminders every {self.config['reminder_interval_hours']} hours for {session.service}")
            
        except Exception as e:
            logger.error(f"Error scheduling reminders: {e}")
    
    def _schedule_cutoff(self, session: ReleaseSession):
        """Schedule cutoff handling."""
        try:
            # Parse cutoff time (simplified - in production, use proper datetime parsing)
            # For now, assume cutoff is tomorrow at specified time
            cutoff_time = datetime.now() + timedelta(days=1)  # Simplified
            
            job_id = f"cutoff_{session.thread_ts}"
            
            self.scheduler.add_job(
                func=self._handle_cutoff,
                trigger=DateTrigger(run_date=cutoff_time),
                args=[session.thread_ts],
                id=job_id,
                max_instances=1
            )
            
            session.cutoff_job_id = job_id
            logger.info(f"Scheduled cutoff for {session.service} at {cutoff_time}")
            
        except Exception as e:
            logger.error(f"Error scheduling cutoff: {e}")
    
    def _send_reminder(self, thread_ts: str):
        """Send periodic reminder message."""
        try:
            session = self._get_session_by_thread(thread_ts)
            if not session:
                return
            
            pending = session.pending_authors
            if not pending:
                # All signed off, cancel reminders
                if session.reminder_job_id:
                    self.scheduler.remove_job(session.reminder_job_id)
                return
            
            reminder_msg = f"""📢 Friendly reminder to sign off by *{session.signoff_cutoff_time}*:

{chr(10).join([f'• <@{user}>' for user in pending])}

Reply: `@release_rc signed off`"""
            
            self.client.chat_postMessage(
                channel=session.channel_id,
                thread_ts=thread_ts,
                text=reminder_msg,
                mrkdwn=True
            )
            
            logger.info(f"Sent reminder for {session.service} to {len(pending)} users")
            
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
    
    def _handle_cutoff(self, thread_ts: str):
        """Handle sign-off cutoff time."""
        try:
            session = self._get_session_by_thread(thread_ts)
            if not session:
                return
            
            pending = session.pending_authors
            
            if not pending:
                # All signed off
                cutoff_msg = f"""🎉 *All PRs signed off!* Ready for CRQ review.

Release *{session.service} v{session.version}* is ready to proceed.

{session.rc_slack_handle} please proceed with the release process."""
            else:
                # Some pending
                pending_list = "\n".join([f"• <@{user}>" for user in pending])
                cutoff_msg = f"""⚠️ *Sign-off incomplete*

The following developers have not signed off by the cutoff time:
{pending_list}

Their changes will be removed from the release branch.

{session.rc_slack_handle} please review and proceed accordingly."""
            
            self.client.chat_postMessage(
                channel=session.channel_id,
                thread_ts=thread_ts,
                text=cutoff_msg,
                mrkdwn=True
            )
            
            # Cancel reminder job
            self._cancel_session_jobs(session)
            
            logger.info(f"Handled cutoff for {session.service}, {len(pending)} users pending")
            
        except Exception as e:
            logger.error(f"Error handling cutoff: {e}")
    
    def _handle_all_signed_off(self, session: ReleaseSession):
        """Handle when all users have signed off."""
        try:
            success_msg = f"""🎉 *All PRs signed off early!*

All developers have signed off on their PRs for *{session.service} v{session.version}*.

{session.rc_slack_handle} the release is ready to proceed ahead of schedule!"""
            
            self.client.chat_postMessage(
                channel=session.channel_id,
                thread_ts=session.thread_ts,
                text=success_msg,
                mrkdwn=True
            )
            
            # Cancel scheduled jobs since we're done early
            self._cancel_session_jobs(session)
            
            logger.info(f"All users signed off early for {session.service} v{session.version}")
            
        except Exception as e:
            logger.error(f"Error handling all signed off: {e}")
    
    def _cancel_session_jobs(self, session: ReleaseSession):
        """Cancel all scheduled jobs for a session."""
        try:
            if session.reminder_job_id:
                self.scheduler.remove_job(session.reminder_job_id)
            if session.cutoff_job_id:
                self.scheduler.remove_job(session.cutoff_job_id)
        except Exception as e:
            logger.error(f"Error cancelling jobs: {e}")
    
    def run(self):
        """Run the Slack bot."""
        handler = SocketModeHandler(self.app, os.environ["SLACK_APP_TOKEN"])
        handler.start()

def main():
    """Main entry point for the bot."""
    bot = ReleaseRCBot()
    logger.info("🤖 Release RC bot starting...")
    bot.run()

if __name__ == "__main__":
    main() 