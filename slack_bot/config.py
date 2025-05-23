#!/usr/bin/env python3
"""
Slack Bot Configuration

Configuration management for the Release RC Slack bot with environment
variables, defaults, and validation.
"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class SlackBotConfig:
    """Configuration for the Release RC Slack bot."""
    
    # Slack app credentials
    slack_bot_token: str = ""
    slack_app_token: str = ""  # For Socket Mode
    slack_signing_secret: str = ""
    
    # Bot behavior settings
    reminder_interval_hours: int = 2
    default_channel: str = "#release-rc"
    timezone: str = "America/Los_Angeles"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    
    # External integrations
    github_token: Optional[str] = None
    slack_bot_url: Optional[str] = None
    slack_bot_api_key: Optional[str] = None
    
    # Deployment settings
    deployment_mode: str = "development"  # development, production
    log_level: str = "INFO"
    
    @classmethod
    def from_environment(cls) -> "SlackBotConfig":
        """Create configuration from environment variables."""
        return cls(
            # Required Slack credentials
            slack_bot_token=os.environ.get("SLACK_BOT_TOKEN", ""),
            slack_app_token=os.environ.get("SLACK_APP_TOKEN", ""),
            slack_signing_secret=os.environ.get("SLACK_SIGNING_SECRET", ""),
            
            # Bot behavior
            reminder_interval_hours=int(os.environ.get("REMINDER_INTERVAL_HOURS", "2")),
            default_channel=os.environ.get("RELEASE_CHANNEL", "#release-rc"),
            timezone=os.environ.get("TIMEZONE", "America/Los_Angeles"),
            
            # Server
            host=os.environ.get("HOST", "0.0.0.0"),
            port=int(os.environ.get("PORT", "5000")),
            debug=os.environ.get("DEBUG", "false").lower() == "true",
            
            # External
            github_token=os.environ.get("GITHUB_TOKEN"),
            slack_bot_url=os.environ.get("SLACK_BOT_URL"),
            slack_bot_api_key=os.environ.get("SLACK_BOT_API_KEY"),
            
            # Deployment
            deployment_mode=os.environ.get("DEPLOYMENT_MODE", "development"),
            log_level=os.environ.get("LOG_LEVEL", "INFO")
        )
    
    def validate(self) -> bool:
        """Validate required configuration."""
        if not self.slack_bot_token:
            raise ValueError("SLACK_BOT_TOKEN is required")
        
        if not self.slack_app_token:
            raise ValueError("SLACK_APP_TOKEN is required for Socket Mode")
        
        if self.reminder_interval_hours < 1:
            raise ValueError("REMINDER_INTERVAL_HOURS must be at least 1")
        
        if self.port < 1 or self.port > 65535:
            raise ValueError("PORT must be between 1 and 65535")
        
        return True
    
    def to_dict(self) -> dict:
        """Convert config to dictionary for logging (excluding secrets)."""
        return {
            "reminder_interval_hours": self.reminder_interval_hours,
            "default_channel": self.default_channel,
            "timezone": self.timezone,
            "host": self.host,
            "port": self.port,
            "debug": self.debug,
            "deployment_mode": self.deployment_mode,
            "log_level": self.log_level,
            "has_slack_bot_token": bool(self.slack_bot_token),
            "has_slack_app_token": bool(self.slack_app_token),
            "has_github_token": bool(self.github_token),
            "has_slack_bot_url": bool(self.slack_bot_url)
        } 