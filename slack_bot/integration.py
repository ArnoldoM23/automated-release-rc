#!/usr/bin/env python3
"""
Slack Bot Integration Module

Handles integration between GitHub Actions and the Release RC Slack bot.
Provides API endpoints and utilities for triggering sign-off workflows.
"""

import json
import os
import requests
import logging
from typing import Dict, List, Any, Optional
from dataclasses import asdict

logger = logging.getLogger(__name__)

class SlackBotIntegration:
    """Integration layer for triggering Slack bot workflows from GitHub Actions."""
    
    def __init__(self, bot_url: Optional[str] = None):
        """
        Initialize the integration.
        
        Args:
            bot_url: URL where the Slack bot is deployed (e.g., Heroku, Railway)
        """
        self.bot_url = bot_url or os.environ.get("SLACK_BOT_URL")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ.get('SLACK_BOT_API_KEY', '')}"
        }
    
    def trigger_release_workflow(self, pr_data: List[Dict], release_metadata: Dict) -> Dict:
        """
        Trigger a release sign-off workflow via the deployed Slack bot.
        
        Args:
            pr_data: List of PR objects from GitHub API
            release_metadata: Release information from GitHub Actions
            
        Returns:
            Dict with workflow trigger results
        """
        try:
            if not self.bot_url:
                return self._mock_bot_response(pr_data, release_metadata)
            
            payload = {
                "action": "start_release_session",
                "prs": pr_data,
                "release_metadata": release_metadata
            }
            
            response = requests.post(
                f"{self.bot_url}/api/release",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Successfully triggered Slack workflow: {result}")
                return result
            else:
                logger.error(f"Failed to trigger Slack workflow: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error triggering Slack workflow: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _mock_bot_response(self, pr_data: List[Dict], release_metadata: Dict) -> Dict:
        """
        Mock bot response for testing without deployed bot.
        
        This allows the GitHub Actions workflow to complete successfully
        even if the Slack bot isn't deployed yet.
        """
        logger.info("Using mock Slack bot response (bot not deployed)")
        
        # Determine channel for mock response
        channel_id = release_metadata.get("channel_id", "#release-rc")
        
        # Simulate successful bot response
        return {
            "success": True,
            "channel_id": channel_id,
            "thread_ts": "1234567890.123456",
            "message": "Mock: Release sign-off session would be started",
            "mock": True,
            "pr_count": len(pr_data),
            "service": release_metadata.get("service", "unknown"),
            "version": release_metadata.get("version", "unknown"),
            "note": f"Would post to channel: {channel_id}"
        }

def format_prs_for_slack(github_prs: List[Dict]) -> List[Dict]:
    """
    Format GitHub PR data for Slack bot consumption.
    
    Args:
        github_prs: Raw PR data from GitHub API
        
    Returns:
        Formatted PR data for Slack bot
    """
    formatted_prs = []
    
    for pr in github_prs:
        formatted_pr = {
            "number": pr["number"],
            "html_url": pr["html_url"],
            "title": pr.get("title", ""),
            "user": {
                "login": pr["user"]["login"]
            },
            "labels": pr.get("labels", [])
        }
        formatted_prs.append(formatted_pr)
    
    return formatted_prs

def prepare_release_metadata(github_actions_inputs: Dict, channel_override: Optional[str] = None) -> Dict:
    """
    Prepare release metadata from GitHub Actions inputs.
    
    Args:
        github_actions_inputs: Input parameters from GitHub Actions
        channel_override: Optional channel to override default detection
        
    Returns:
        Formatted release metadata for Slack bot
    """
    # Extract common parameters
    service = github_actions_inputs.get("service_name", "unknown-service")
    version = github_actions_inputs.get("new_version", "unknown-version")
    
    # Format dates
    day1_date = github_actions_inputs.get("day1_date", "TBD")
    day2_date = github_actions_inputs.get("day2_date", "TBD")
    
    # Set cutoff time (default to noon next day)
    cutoff_time = github_actions_inputs.get("signoff_cutoff_time", "12:00 PM tomorrow")
    
    # Get RC handle - handle both @ prefixed and non-prefixed
    rc_handle = github_actions_inputs.get("rc_manager", "unknown")
    if rc_handle and not rc_handle.startswith("<@") and not rc_handle.startswith("@"):
        # If it's just a username, format as Slack mention
        rc_handle = f"<@{rc_handle}>"
    elif rc_handle and rc_handle.startswith("@") and not rc_handle.startswith("<@"):
        # Convert @username to <@username>
        rc_handle = f"<{rc_handle}>"
    
    # Determine channel - priority: override > slack_channel input > workflow_builder channel > default
    channel_id = (
        channel_override or 
        github_actions_inputs.get("slack_channel") or 
        github_actions_inputs.get("channel_id") or 
        "#release-rc"
    )
    
    # Get trigger user if available
    trigger_user = github_actions_inputs.get("trigger_user", github_actions_inputs.get("slack_user", ""))
    
    return {
        "service": service,
        "version": version,
        "day1_date": day1_date,
        "day2_date": day2_date,
        "signoff_cutoff_time": cutoff_time,
        "rc_slack_handle": rc_handle,
        "channel_id": channel_id,
        "trigger_user": trigger_user
    }

def trigger_github_workflow(repository: str, workflow_inputs: Dict, github_token: str) -> Dict:
    """
    Trigger GitHub Actions workflow via repository_dispatch.
    
    Args:
        repository: GitHub repository (org/repo)
        workflow_inputs: Inputs for the workflow
        github_token: GitHub API token
        
    Returns:
        Result of the workflow trigger
    """
    try:
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        payload = {
            "event_type": "run-release",
            "client_payload": workflow_inputs
        }
        
        url = f"https://api.github.com/repos/{repository}/dispatches"
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 204:
            logger.info(f"Successfully triggered GitHub workflow for {repository}")
            return {
                "success": True,
                "message": "GitHub workflow triggered successfully",
                "repository": repository
            }
        else:
            logger.error(f"Failed to trigger GitHub workflow: {response.status_code} - {response.text}")
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
            
    except Exception as e:
        logger.error(f"Error triggering GitHub workflow: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def create_workflow_inputs_from_slack(slack_payload: Dict) -> Dict:
    """
    Create GitHub workflow inputs from Slack payload.
    
    This function handles the conversion from Slack Workflow Builder
    or slash command inputs to GitHub Actions workflow inputs.
    
    Args:
        slack_payload: Payload from Slack (Workflow Builder or slash command)
        
    Returns:
        Dict formatted for GitHub Actions workflow
    """
    # Handle different Slack payload formats
    if "client_payload" in slack_payload:
        # Repository dispatch format
        inputs = slack_payload["client_payload"]
    elif "view" in slack_payload:
        # Modal submission format
        values = slack_payload["view"]["state"]["values"]
        inputs = {}
        for block_id, block_values in values.items():
            for action_id, action_value in block_values.items():
                field_name = block_id
                if "value" in action_value:
                    inputs[field_name] = action_value["value"]
                elif "selected_date" in action_value:
                    inputs[field_name] = action_value["selected_date"]
                elif "selected_user" in action_value:
                    inputs[field_name] = action_value["selected_user"]
                elif "selected_option" in action_value:
                    inputs[field_name] = action_value["selected_option"]["value"]
    else:
        # Direct input format
        inputs = slack_payload
    
    # Extract channel information
    channel_id = (
        slack_payload.get("channel", {}).get("id") or
        slack_payload.get("channel_id") or
        inputs.get("channel_id")
    )
    
    # Extract user information
    user_id = (
        slack_payload.get("user", {}).get("id") or
        slack_payload.get("user_id") or
        inputs.get("user_id")
    )
    
    # Format for GitHub Actions
    workflow_inputs = {
        "prod_version": inputs.get("prod_version", ""),
        "new_version": inputs.get("new_version", ""),
        "service_name": inputs.get("service_name", ""),
        "release_type": inputs.get("release_type", "standard"),
        "rc_name": inputs.get("rc_name", ""),
        "rc_manager": inputs.get("rc_manager", ""),
        "day1_date": inputs.get("day1_date", ""),
        "day2_date": inputs.get("day2_date", ""),
        "slack_channel": channel_id,
        "slack_user": user_id
    }
    
    return workflow_inputs

def main():
    """
    Main entry point for integration testing.
    
    This can be called from GitHub Actions to trigger the Slack workflow.
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python integration.py <pr_data_file> [release_metadata_file] [channel_override]")
        sys.exit(1)
    
    # Load PR data from file
    pr_data_file = sys.argv[1]
    with open(pr_data_file, 'r') as f:
        pr_data = json.load(f)
    
    # Load release metadata (or use defaults)
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'r') as f:
            release_metadata = json.load(f)
    else:
        # Use default metadata for testing
        release_metadata = {
            "service": "test-service",
            "version": "v1.0.0",
            "day1_date": "2024-01-15",
            "day2_date": "2024-01-16",
            "signoff_cutoff_time": "12:00 PM tomorrow",
            "rc_manager": "test-user",
            "channel_id": "#release-rc"
        }
    
    # Optional channel override
    channel_override = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Initialize integration
    integration = SlackBotIntegration()
    
    # Format data
    formatted_prs = format_prs_for_slack(pr_data)
    
    # Prepare metadata with channel override
    if channel_override:
        release_metadata["channel_id"] = channel_override
    
    # Trigger workflow
    result = integration.trigger_release_workflow(formatted_prs, release_metadata)
    
    # Output result
    print(json.dumps(result, indent=2))
    
    if result.get("success"):
        print(f"✅ Slack workflow triggered successfully!")
        if result.get("mock"):
            print(f"📝 Mock mode: Would post to {result.get('channel_id')}")
        else:
            print(f"📝 Posted to channel: {result.get('channel_id')}")
            print(f"🧵 Thread: {result.get('thread_ts')}")
        sys.exit(0)
    else:
        print("❌ Failed to trigger Slack workflow")
        sys.exit(1)

if __name__ == "__main__":
    main() 