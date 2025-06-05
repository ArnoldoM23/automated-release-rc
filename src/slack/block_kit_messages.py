from typing import List, Dict, Any

def create_initial_signoff_message(
    service_name: str,
    version: str,
    day1_date: str,
    day2_date: str,
    cutoff_time: str,
    authors: List[str],
    rc_name: str,
    rc_manager: str
) -> Dict[str, Any]:
    """Create initial sign-off notification with Block Kit formatting."""
    author_mentions = ", ".join([f"<@{author}>" for author in authors])
    
    return {
        "channel": "#release-rc",
        "text": "RC release sign-off notification",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🚀 Release Sign-Off Notification"}
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Hi team,*\nThe release version for *{service_name} {version}* has been locked.\n\n• *Day 1:* {day1_date}\n• *Day 2:* {day2_date}\n• *Cutoff:* {cutoff_time}\n\nPlease react with ✅ to this message to confirm your sign-off.\n\n*PR Authors:* {author_mentions}\n\n*Cc:* <@{rc_manager}>"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"RC: <@{rc_name}> | Changes without sign-off will be removed from the release branch."
                    }
                ]
            }
        ]
    }


def create_reminder_message(cutoff_time: str) -> Dict[str, Any]:
    """Create reminder message before cutoff."""
    return {
        "channel": "#release-rc",
        "text": "Reminder to sign off on RC release",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "⏰ Sign-Off Reminder"}
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hi team,\n\nThis is a gentle reminder to *sign off on your PRs* by the cutoff time (*{cutoff_time}*).\nReact with ✅ to the original release message to confirm.\n\n*Changes without sign-off will be removed from the release branch.*\n\nThank you!"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "⚠️ This is an automated reminder. Please ensure all your changes are signed off."
                    }
                ]
            }
        ]
    }


def create_all_signed_off_message(rc_name: str, total_prs: int, total_authors: int) -> Dict[str, Any]:
    """Create success message when all PRs are signed off."""
    return {
        "channel": "#release-rc",
        "text": "All PRs signed off",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "✅ All PRs Signed Off"}
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"All developers have signed off on their changes.\n\n*RC <@{rc_name}>* – please proceed to finalize and submit the CRQs for approval.\n\nGreat job, everyone!"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Total PRs:*\n{total_prs}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Authors:*\n{total_authors}"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🎉 Release sign-off complete! Ready for CRQ submission."
                    }
                ]
            }
        ]
    }


def create_pending_signoffs_message(
    rc_name: str,
    rc_manager: str,
    pending_authors: List[str],
    cutoff_time: str
) -> Dict[str, Any]:
    """Create warning message for pending sign-offs."""
    pending_mentions = "\n".join([f"- <@{author}>" for author in pending_authors])
    
    return {
        "channel": "#release-rc",
        "text": "Pending sign-offs before CRQ submission",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "⚠️ Pending Sign-Offs"}
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*RC <@{rc_name}>, <@{rc_manager}>* – we are still missing sign-offs from the following developers:\n\n{pending_mentions}\n\nThis may delay CRQ review and approval.\n\n*Reminder:* Changes without sign-off will be removed from the release branch. Please confirm ASAP."
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Cutoff Time:*\n{cutoff_time}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Pending Count:*\n{len(pending_authors)}"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🚨 Urgent action required. RC Manager has been notified."
                    }
                ]
            }
        ]
    }


def create_progress_update_message(
    signed_count: int,
    total_count: int,
    time_remaining: str
) -> Dict[str, Any]:
    """Create progress update message showing current sign-off status."""
    progress_percentage = int((signed_count / total_count) * 100) if total_count > 0 else 0
    progress_bar = "█" * (progress_percentage // 10) + "░" * (10 - (progress_percentage // 10))
    
    return {
        "channel": "#release-rc",
        "text": "Sign-off progress update",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "📊 Sign-Off Progress"}
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Current Progress:* {signed_count}/{total_count} signed off ({progress_percentage}%)\n\n`{progress_bar}`\n\n*Time Remaining:* {time_remaining}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "📈 Keep up the great work! Remember to react with ✅ to sign off your changes."
                    }
                ]
            }
        ]
    } 