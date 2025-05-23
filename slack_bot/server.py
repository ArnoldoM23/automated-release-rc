#!/usr/bin/env python3
"""
Release RC Slack Bot Web Server

Flask web server that wraps the Slack bot and provides API endpoints
for integration with GitHub Actions and other external services.
"""

import json
import logging
import threading
from typing import Dict, Any

from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest

from .app import ReleaseRCBot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotServer:
    """Web server wrapper for the Release RC Slack bot."""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.bot = ReleaseRCBot()
        self._setup_routes()
        
        # Start bot in background thread
        self.bot_thread = threading.Thread(target=self.bot.run, daemon=True)
        self.bot_thread.start()
    
    def _setup_routes(self):
        """Setup Flask routes for the API."""
        
        @self.app.route("/health", methods=["GET"])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "bot": "release_rc",
                "version": "1.0.0"
            })
        
        @self.app.route("/api/release", methods=["POST"])
        def trigger_release():
            """
            Trigger a new release sign-off session.
            
            Expected payload:
            {
                "action": "start_release_session",
                "prs": [...],
                "release_metadata": {...}
            }
            """
            try:
                data = request.get_json()
                
                if not data:
                    raise BadRequest("No JSON payload provided")
                
                action = data.get("action")
                if action != "start_release_session":
                    raise BadRequest(f"Unknown action: {action}")
                
                prs = data.get("prs", [])
                release_metadata = data.get("release_metadata", {})
                
                if not prs:
                    raise BadRequest("No PRs provided")
                
                if not release_metadata:
                    raise BadRequest("No release metadata provided")
                
                # Trigger the release session
                result = self.bot.start_release_session(prs, release_metadata)
                
                return jsonify(result)
                
            except BadRequest as e:
                logger.error(f"Bad request: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 400
            
            except Exception as e:
                logger.error(f"Error triggering release: {e}")
                return jsonify({
                    "success": False,
                    "error": "Internal server error"
                }), 500
        
        @self.app.route("/api/sessions", methods=["GET"])
        def list_sessions():
            """List active release sessions."""
            try:
                sessions = []
                with self.bot.sessions_lock:
                    for thread_ts, session in self.bot.sessions.items():
                        sessions.append({
                            "thread_ts": thread_ts,
                            "service": session.service,
                            "version": session.version,
                            "pending_count": len(session.pending_authors),
                            "total_prs": len(session.prs),
                            "created_at": session.created_at.isoformat()
                        })
                
                return jsonify({
                    "success": True,
                    "sessions": sessions,
                    "total": len(sessions)
                })
                
            except Exception as e:
                logger.error(f"Error listing sessions: {e}")
                return jsonify({
                    "success": False,
                    "error": "Internal server error"
                }), 500
        
        @self.app.route("/api/sessions/<thread_ts>", methods=["GET"])
        def get_session(thread_ts: str):
            """Get details of a specific session."""
            try:
                session = self.bot._get_session_by_thread(thread_ts)
                
                if not session:
                    return jsonify({
                        "success": False,
                        "error": "Session not found"
                    }), 404
                
                # Build detailed session info
                prs_info = []
                for pr in session.prs:
                    prs_info.append({
                        "number": pr.number,
                        "author": pr.author,
                        "title": pr.title,
                        "signed_off": pr.signed_off,
                        "html_url": pr.html_url
                    })
                
                session_info = {
                    "service": session.service,
                    "version": session.version,
                    "day1_date": session.day1_date,
                    "day2_date": session.day2_date,
                    "signoff_cutoff_time": session.signoff_cutoff_time,
                    "rc_slack_handle": session.rc_slack_handle,
                    "channel_id": session.channel_id,
                    "thread_ts": session.thread_ts,
                    "created_at": session.created_at.isoformat(),
                    "prs": prs_info,
                    "pending_authors": list(session.pending_authors),
                    "signed_off_authors": list(session.signed_off_authors)
                }
                
                return jsonify({
                    "success": True,
                    "session": session_info
                })
                
            except Exception as e:
                logger.error(f"Error getting session: {e}")
                return jsonify({
                    "success": False,
                    "error": "Internal server error"
                }), 500
        
        @self.app.route("/api/sessions/<thread_ts>", methods=["DELETE"])
        def abort_session(thread_ts: str):
            """Abort a specific session."""
            try:
                session = self.bot._get_session_by_thread(thread_ts)
                
                if not session:
                    return jsonify({
                        "success": False,
                        "error": "Session not found"
                    }), 404
                
                # Cancel jobs and remove session
                self.bot._cancel_session_jobs(session)
                
                with self.bot.sessions_lock:
                    if thread_ts in self.bot.sessions:
                        del self.bot.sessions[thread_ts]
                
                logger.info(f"Aborted session for {session.service} v{session.version}")
                
                return jsonify({
                    "success": True,
                    "message": "Session aborted successfully"
                })
                
            except Exception as e:
                logger.error(f"Error aborting session: {e}")
                return jsonify({
                    "success": False,
                    "error": "Internal server error"
                }), 500
    
    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
        """Run the Flask server."""
        logger.info(f"🚀 Starting Release RC bot server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

def main():
    """Main entry point for the server."""
    import os
    
    # Configuration from environment
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    
    # Create and run server
    server = BotServer()
    server.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    main() 