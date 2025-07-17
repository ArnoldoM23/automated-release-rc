# rc_agent_build_release.py

import os
import re
from datetime import datetime
import questionary
from pathlib import Path

from src.config.config import load_config, extract_service_name_from_repo
from src.github_integration.fetch_prs import GitHubClient

# v4.0 Enhancement: Release Types with Tips
RELEASE_TYPES = {
    "standard": "🟢 Regular feature or service release (non-urgent)",
    "hotfix": "🔴 Urgent bug fix going directly to prod",
    "release": "📦 Formal versioned rollout for larger release cycles"
}

def normalize_version(version: str) -> str:
    """Normalize version string by removing v/V prefix"""
    return version.lstrip("vV")

def is_valid_version(version: str) -> bool:
    """Validate version string format - supports multiple formats for v4.0"""
    version = normalize_version(version)
    
    # v4.0 Enhancement: Support multiple version formats
    patterns = [
        r'^\d+\.\d+\.\d+$',                         # SemVer: 1.2.3
        r'^\d+\.\d+\.\d+-[a-fA-F0-9]{6,40}$',       # SemVer + SHA: 1.2.3-abcdef (6+ chars, case insensitive)
        r'^[a-fA-F0-9]{6,40}$',                     # SHA-only: abcdef123 (6-40 chars, case insensitive)
    ]
    
    return any(re.match(pattern, version) for pattern in patterns)

def get_version_format_examples() -> str:
    """Return formatted examples for version input"""
    return """Invalid version format. Examples:
  - v1.2.3 or 1.2.3 (SemVer)
  - 1.2.3-abcdef (SemVer + SHA, 6+ chars)
  - abcdef123 (SHA only, 6-40 chars)"""

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

    # Get current user info for RC field (not repo owner)
    rc_display_name = os.getenv("USER", "")  # Fallback to OS user
    
    # Extract username from repo owner for RC field
    if github_client and config:
        try:
            if hasattr(config, 'github') and config.github.repo:
                repo_parts = config.github.repo.split('/')
                if len(repo_parts) == 2:
                    github_username = repo_parts[0]
                    enhanced_name = github_client.get_user_display_name(github_username)
                    rc_display_name = enhanced_name
        except Exception:
            rc_display_name = f"@{os.getenv('USER', 'unknown')}"

    # Basic release info
    rc = questionary.text(
        "Who is the RC?",
        default=rc_display_name
    ).ask()
    
    rc_manager = questionary.text(
        "Who is the RC Manager?",
        default="Charlie"
    ).ask()

    # v4.0 Enhancement: Enhanced version validation with multiple formats
    def version_validator(text):
        if not text.strip():
            return "Version cannot be empty"
        if not is_valid_version(text):
            return get_version_format_examples()
        return True

    production_version = questionary.text(
        "Production version (e.g., v1.2.3, 1.2.3-abcdef, or SHA)",
        validate=version_validator
    ).ask()

    new_version = questionary.text(
        "New version (e.g., v1.2.4, 1.2.4-abcdef, or SHA)",
        validate=version_validator
    ).ask()

    # Normalize versions for storage
    production_version = normalize_version(production_version)
    new_version = normalize_version(new_version)

    # Service details - pre-fill from GitHub repo if available
    default_service = "ce-cart"
    
    # v4.0 Enhancement: Try config first, then fallback to environment variables
    if config and hasattr(config, 'github') and config.github.repo:
        try:
            extracted_service = extract_service_name_from_repo(config.github.repo)
            if extracted_service != "unknown-service":
                default_service = extracted_service
                print(f"💡 Pre-filling service name from GitHub repo: {default_service}")
        except Exception:
            pass
    else:
        # Fallback: Extract from environment variables when config fails
        github_repo = os.getenv("GITHUB_REPO")
        if github_repo:
            try:
                extracted_service = extract_service_name_from_repo(github_repo)
                if extracted_service != "unknown-service":
                    default_service = extracted_service
                    print(f"💡 Pre-filling service name from environment GITHUB_REPO: {default_service}")
            except Exception:
                pass

    service_name = questionary.text(
        "Service name (e.g. ce-cart)",
        default=default_service
    ).ask()

    # v4.0 Enhancement: Release type selection with tips
    print("\nSelect a release type:")
    for rtype, tip in RELEASE_TYPES.items():
        print(f"  - {rtype}: {tip}")
    
    release_type = questionary.select(
        "Release type",
        choices=list(RELEASE_TYPES.keys())
    ).ask()

    # Validate release type (extra safety)
    if release_type not in RELEASE_TYPES:
        print(f"❌ Invalid release type. Choose one of: {list(RELEASE_TYPES.keys())}")
        return None

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
    if config:
        print("\n🎯 Collected configuration:")
        for key, value in config.items():
            print(f"  {key}: {value}")
    else:
        print("❌ Failed to collect configuration") 