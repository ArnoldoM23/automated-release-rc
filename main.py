#!/usr/bin/env python3
"""
Automated RC Release Workflow - CLI Orchestrator

This is the main entry point for the GitHub Actions workflow.
Takes command line arguments and orchestrates the entire release process.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.logging import get_logger
from config.config import load_config
from github_integration.fetch_prs import fetch_prs
from notes.release_notes import render_release_notes  
from crq.generate_crqs import generate_crqs
from utils.ai_client import AIClient


def parse_args():
    """Parse command line arguments from GitHub Actions workflow."""
    parser = argparse.ArgumentParser(
        description="RC Release Automation - Generate release docs and manage sign-offs"
    )
    
    # Required release parameters
    parser.add_argument("--prod-version", required=True,
                       help="Current production version (e.g., v1.2.3)")
    parser.add_argument("--new-version", required=True,
                       help="New release version (e.g., v1.3.0)")
    parser.add_argument("--service-name", required=True,
                       help="Service being released (e.g., cer-cart)")
    parser.add_argument("--release-type", required=True,
                       choices=["standard", "hotfix", "ebf"],
                       help="Type of release")
    parser.add_argument("--rc-name", required=True,
                       help="Release coordinator name")
    parser.add_argument("--rc-manager", required=True,
                       help="Release manager/escalation contact")
    parser.add_argument("--day1-date", required=True,
                       help="Day 1 deployment date (YYYY-MM-DD)")
    parser.add_argument("--day2-date", required=True,
                       help="Day 2 deployment date (YYYY-MM-DD)")
    
    # Optional parameters
    parser.add_argument("--channel", default="#release-rc",
                       help="Slack channel for notifications")
    parser.add_argument("--output-dir", default="outputs",
                       help="Directory for generated files")
    parser.add_argument("--config-path", default="config/settings.yaml",
                       help="Path to configuration file")
    
    return parser.parse_args()


def validate_args(args) -> Dict[str, Any]:
    """Validate and normalize command line arguments."""
    logger = get_logger(__name__)
    
    # Convert args to dict for easier handling
    params = {
        "prod_version": args.prod_version.strip(),
        "new_version": args.new_version.strip(),
        "service_name": args.service_name.strip(),
        "release_type": args.release_type,
        "rc_name": args.rc_name.strip(),
        "rc_manager": args.rc_manager.strip(),
        "day1_date": args.day1_date,
        "day2_date": args.day2_date,
        "channel": args.channel,
        "output_dir": args.output_dir,
        "config_path": args.config_path
    }
    
    # Basic validation
    if not params["prod_version"] or not params["new_version"]:
        raise ValueError("Production and new versions are required")
        
    if not params["service_name"]:
        raise ValueError("Service name is required")
        
    if not params["rc_name"] or not params["rc_manager"]:
        raise ValueError("RC name and manager are required")
    
    # Validate date format (basic check)
    import re
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(date_pattern, params["day1_date"]):
        raise ValueError(f"Day 1 date must be in YYYY-MM-DD format: {params['day1_date']}")
    if not re.match(date_pattern, params["day2_date"]):
        raise ValueError(f"Day 2 date must be in YYYY-MM-DD format: {params['day2_date']}")
    
    logger.info(f"Validated parameters for {params['service_name']} {params['new_version']}")
    return params


def setup_output_directory(output_dir: str) -> Path:
    """Create and verify output directory."""
    logger = get_logger(__name__)
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Output directory: {output_path.absolute()}")
    return output_path


def generate_pr_summary(prs: list, params: Dict[str, Any], output_dir: Path):
    """Generate PR summary JSON for sign-off bot integration."""
    logger = get_logger(__name__)
    
    # Create PR summary for sign-off bot
    pr_summary = []
    for pr in prs:
        pr_data = {
            "number": pr.number,
            "title": pr.title,
            "author": pr.user.login,
            "author_id": pr.user.login,  # Will be mapped to Slack user ID by bot
            "labels": [label.name for label in pr.labels],
            "url": pr.html_url
        }
        pr_summary.append(pr_data)
    
    # Save PR summary
    summary_file = output_dir / "pr_summary.json"
    with open(summary_file, "w") as f:
        json.dump({
            "service_name": params["service_name"],
            "new_version": params["new_version"],
            "prs": pr_summary,
            "total_prs": len(pr_summary)
        }, f, indent=2)
    
    logger.info(f"Generated PR summary: {len(pr_summary)} PRs")
    
    # Output for GitHub Actions to capture
    print(f"::set-output name=prs::{json.dumps(pr_summary)}")
    
    return pr_summary


def main():
    """Main orchestrator function."""
    logger = get_logger(__name__)
    
    try:
        # Parse and validate arguments
        logger.info("Starting RC Release Automation...")
        args = parse_args()
        params = validate_args(args)
        
        # Setup environment
        output_dir = setup_output_directory(params["output_dir"])
        
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config(config_path=params.get("config_path"))
        
        # Validate required environment variables
        required_env_vars = ["GITHUB_TOKEN"]
        missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            sys.exit(1)
        
        # Step 1: Fetch PRs between versions
        logger.info(f"Fetching PRs between {params['prod_version']} and {params['new_version']}")
        prs = fetch_prs(params["prod_version"], params["new_version"])
        logger.info(f"Found {len(prs)} PRs to include in release")
        
        if not prs:
            logger.warning("No PRs found between versions - generating empty release")
        
        # Step 2: Generate release notes
        logger.info("Generating release notes...")
        release_notes_file = render_release_notes(prs, params, output_dir)
        logger.info(f"Release notes generated: {release_notes_file}")
        
        # Step 3: Generate CRQ documents
        logger.info("Generating CRQ documents...")
        crq_files = generate_crqs(prs, params, output_dir)
        logger.info(f"CRQ documents generated: {crq_files}")
        
        # Step 4: Generate PR summary for sign-off bot
        logger.info("Generating PR summary for sign-off tracking...")
        pr_summary = generate_pr_summary(prs, params, output_dir)
        
        # Final summary
        logger.info("🎉 Release automation completed successfully!")
        logger.info(f"📝 Files generated:")
        for file_path in output_dir.glob("*.txt"):
            logger.info(f"  - {file_path.name}")
        for file_path in output_dir.glob("*.json"):
            logger.info(f"  - {file_path.name}")
        
        logger.info(f"📊 Ready for sign-off tracking: {len(pr_summary)} PRs")
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Release automation failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main() 