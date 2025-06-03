# rc_agent_build_release.py

import os
import re
from datetime import datetime
import questionary
from pathlib import Path

from src.config.config import load_config, extract_service_name_from_repo
from src.github.fetch_prs import GitHubClient

def is_valid_version(version):
    """Validate version string format (semantic versioning)"""
    pattern = r'^v?\d+\.\d+\.\d+$'
    return bool(re.match(pattern, version))

def validate_date(date_str):
    """Validate date string in YYYY-MM-DD format"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return "Date must be in YYYY-MM-DD format"

def validate_iso_utc(time_str):
    """Validate ISO UTC time string"""
    try:
        datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        return True
    except ValueError:
        return "Time must be in ISO UTC format (e.g., 2025-05-29T23:00:00Z)"

def get_release_inputs():
    """Collect release configuration via interactive prompts"""
    print("\n👋 Welcome to the RC Release Agent!")
    print("🛠  Let's gather details for this release.\n")

    # Load config to get GitHub details and defaults
    try:
        config = load_config()
        github_client = GitHubClient(config.github) if config.github.token != "xoxb-000000000000-000000000000-placeholder-for-testing" else None
    except Exception as e:
        print(f"⚠️ Warning: Could not load GitHub config: {e}")
        github_client = None
        config = None

    # Get current user info for RC field
    current_user = os.getenv("USER", "")
    rc_display_name = current_user
    
    if github_client and current_user:
        try:
            # Try to get enhanced display name from GitHub
            enhanced_name = github_client.get_user_display_name(current_user)
            rc_display_name = enhanced_name
        except Exception as e:
            print(f"⚠️ Could not fetch GitHub user details: {e}")

    # Basic release info
    rc = questionary.text(
        "Who is the RC?",
        default=rc_display_name
    ).ask()
    
    rc_manager = questionary.text(
        "Who is the RC Manager?",
        default="Charlie"
    ).ask()

    # Version validation
    production_version = questionary.text(
        "Production version (e.g. v2.3.1)",
        validate=lambda text: is_valid_version(text) or "Invalid semantic version format"
    ).ask()

    new_version = questionary.text(
        "New version (e.g. v2.4.0)",
        validate=lambda text: is_valid_version(text) or "Invalid semantic version format"
    ).ask()

    # Service details - pre-fill from GitHub repo if available
    default_service = "ce-cart"
    if config and hasattr(config, 'github') and config.github.repo:
        try:
            extracted_service = extract_service_name_from_repo(config.github.repo)
            if extracted_service != "unknown-service":
                default_service = extracted_service
                print(f"💡 Pre-filling service name from GitHub repo: {default_service}")
        except Exception:
            pass

    service_name = questionary.text(
        "Service name (e.g. ce-cart)",
        default=default_service
    ).ask()

    release_type = questionary.select(
        "Release type",
        choices=["standard", "hotfix", "release"]
    ).ask()

    # Release dates
    day1_date = questionary.text(
        "Day 1 Date (YYYY-MM-DD)",
        validate=validate_date
    ).ask()
    
    day2_date = questionary.text(
        "Day 2 Date (YYYY-MM-DD)",
        validate=validate_date
    ).ask()

    # Slack configuration
    cutoff_time = questionary.text(
        "Slack cutoff time (UTC ISO format, e.g. 2025-05-29T23:00:00Z)",
        validate=validate_iso_utc
    ).ask()

    # Output configuration
    output_folder = questionary.text(
        "Output folder",
        default="output/"
    ).ask()

    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    return {
        "rc": rc,
        "rc_manager": rc_manager,
        "production_version": production_version,
        "new_version": new_version,
        "service_name": service_name,
        "release_type": release_type,
        "day1_date": day1_date,
        "day2_date": day2_date,
        "cutoff_time": cutoff_time,
        "output_folder": output_folder
    }

if __name__ == "__main__":
    # Test the input collection
    config = get_release_inputs()
    print("\n🎯 Collected configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}") 