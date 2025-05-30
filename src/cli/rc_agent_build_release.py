# rc_agent_build_release.py

import questionary
import datetime
import re
import os

def is_valid_version(version):
    """Validate semantic version format (v1.2.3 or 1.2.3)"""
    return re.match(r"^v?\d+\.\d+\.\d+$", version) is not None

def validate_date(text):
    """Validate date format YYYY-MM-DD"""
    try:
        datetime.datetime.strptime(text, "%Y-%m-%d")
        return True
    except ValueError:
        return "Date must be in YYYY-MM-DD format"

def validate_iso_utc(text):
    """Validate ISO UTC timestamp format"""
    try:
        # Basic validation for ISO format with Z
        if "T" not in text or "Z" not in text:
            return "Must be ISO UTC format (e.g., 2025-05-29T23:00:00Z)"
        
        # Try to parse the datetime
        datetime.datetime.fromisoformat(text.replace('Z', '+00:00'))
        return True
    except ValueError:
        return "Invalid ISO UTC format. Use: YYYY-MM-DDTHH:MM:SSZ"

def get_release_inputs():
    """Collect release configuration via interactive prompts"""
    print("\n👋 Welcome to the RC Release Agent!")
    print("🛠  Let's gather details for this release.\n")

    # Basic release info
    rc = questionary.text(
        "Who is the RC?",
        default=os.getenv("USER", "")
    ).ask()
    
    rc_manager = questionary.text(
        "Who is the RC Manager?",
        default="anil"
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

    # Service details
    service_name = questionary.text(
        "Service name (e.g. cer-cart)",
        default="cer-cart"
    ).ask()

    release_type = questionary.select(
        "Release type",
        choices=["standard", "hotfix", "ebf"]
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
        "output_folder": output_folder,
        "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%SZ")
    }

if __name__ == "__main__":
    # Test the input collection
    config = get_release_inputs()
    print("\n🎯 Collected configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}") 