#!/usr/bin/env python3
"""
RC Release Automation Agent - Main CLI

Enterprise-grade release documentation and CRQ generation from GitHub PRs.
Reduces release captain workload by 90%+ with AI-powered automation.

Usage:
    python main.py --prod-version v1.2.3 --new-version v1.3.0 --service-name cer-cart
    python main.py --help
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
from notes.release_notes import render_release_notes, render_release_notes_markdown
from crq.generate_crqs import generate_crqs


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="RC Release Automation Agent - Generate enterprise-ready release documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python main.py --prod-version v1.2.3 --new-version v1.3.0 --service-name cer-cart

  # Full configuration
  python main.py \\
    --prod-version v2.4.3 \\
    --new-version v2.5.0 \\
    --service-name payment-gateway \\
    --release-type standard \\
    --rc-name "John Doe" \\
    --rc-manager "Jane Smith" \\
    --day1-date 2024-01-15 \\
    --day2-date 2024-01-16 \\
    --output-dir ./release_docs

  # Test with comprehensive mock data
  python main.py --test-mode --service-name test-service

For more information: https://github.com/ArnoldoM23/automated-release-rc
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--prod-version",
        required=True,
        help="Current production version (e.g., v1.2.3)"
    )
    parser.add_argument(
        "--new-version", 
        required=True,
        help="New release version (e.g., v1.3.0)"
    )
    parser.add_argument(
        "--service-name",
        required=True,
        help="Service name (e.g., cer-cart, payment-gateway)"
    )
    
    # Optional release information
    parser.add_argument(
        "--release-type",
        choices=["standard", "hotfix", "ebf"],
        default="standard",
        help="Type of release (default: standard)"
    )
    parser.add_argument(
        "--rc-name",
        default="Release Coordinator",
        help="Release coordinator name (default: Release Coordinator)"
    )
    parser.add_argument(
        "--rc-manager", 
        default="Release Manager",
        help="Release manager name (default: Release Manager)"
    )
    parser.add_argument(
        "--day1-date",
        default="2024-01-15",
        help="Day 1 CRQ date in YYYY-MM-DD format (default: 2024-01-15)"
    )
    parser.add_argument(
        "--day2-date",
        default="2024-01-16", 
        help="Day 2 CRQ date in YYYY-MM-DD format (default: 2024-01-16)"
    )
    
    # Output configuration
    parser.add_argument(
        "--output-dir",
        default="./output",
        help="Output directory for generated files (default: ./output)"
    )
    parser.add_argument(
        "--config-path",
        default="config/settings.yaml",
        help="Path to configuration file (default: config/settings.yaml)"
    )
    
    # Operation modes
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Use mock data for testing (doesn't require real GitHub PRs)"
    )
    parser.add_argument(
        "--skip-ai",
        action="store_true",
        help="Skip AI-powered content generation (use fallback content)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output summary as JSON for automation"
    )
    
    return parser.parse_args()


def create_mock_prs():
    """Create realistic mock PR data for testing."""
    from types import SimpleNamespace
    
    mock_prs = []
    
    # Schema PRs
    schema_prs_data = [
        {"number": 101, "title": "Add userProfile field to User type", "author": "alice", "labels": ["schema", "breaking"]},
        {"number": 102, "title": "Deprecate legacy payment fields", "author": "bob", "labels": ["schema", "deprecation"]},
        {"number": 103, "title": "Update GraphQL mutation signatures", "author": "carol", "labels": ["schema", "api"]},
    ]
    
    # Feature PRs
    feature_prs_data = [
        {"number": 201, "title": "Add express checkout flow", "author": "dave", "labels": ["feature", "checkout"]},
        {"number": 202, "title": "Implement search autocomplete", "author": "eve", "labels": ["feature", "search"]},
        {"number": 203, "title": "Add user dashboard analytics", "author": "frank", "labels": ["feature", "analytics"]},
    ]
    
    # Bugfix PRs
    bugfix_prs_data = [
        {"number": 301, "title": "Fix cart total calculation edge case", "author": "grace", "labels": ["bug", "cart"]},
        {"number": 302, "title": "Resolve memory leak in webhook processing", "author": "henry", "labels": ["bug", "performance"]},
        {"number": 303, "title": "Fix timezone handling in reports", "author": "iris", "labels": ["bug", "timezone"]},
    ]
    
    # International PRs
    international_prs_data = [
        {"number": 401, "title": "Add Spanish (Mexico) locale support", "author": "juan", "labels": ["i18n", "locale"]},
        {"number": 402, "title": "Update currency formatting for EUR", "author": "marie", "labels": ["i18n", "currency"]},
    ]
    
    all_pr_data = schema_prs_data + feature_prs_data + bugfix_prs_data + international_prs_data
    
    for pr_data in all_pr_data:
        pr = SimpleNamespace()
        pr.number = pr_data["number"]
        pr.title = pr_data["title"]
        pr.user = SimpleNamespace()
        pr.user.login = pr_data["author"]
        pr.html_url = f"https://github.com/test/repo/pull/{pr_data['number']}"
        pr.labels = []
        for label_name in pr_data["labels"]:
            label = SimpleNamespace()
            label.name = label_name
            pr.labels.append(label)
        pr.body = f"Mock PR for testing: {pr_data['title']}"
        mock_prs.append(pr)
    
    # Separate international PRs for special handling
    international_prs = [pr for pr in mock_prs if any(label.name in ["i18n", "locale", "currency"] for label in pr.labels)]
    
    return mock_prs, international_prs


def create_params_dict(args) -> Dict[str, Any]:
    """Create parameters dictionary from command line arguments."""
    return {
        "prod_version": args.prod_version,
        "new_version": args.new_version,
        "service_name": args.service_name,
        "release_type": args.release_type,
        "rc_name": args.rc_name,
        "rc_manager": args.rc_manager,
        "day1_date": args.day1_date,
        "day2_date": args.day2_date,
        "channel": "#release-rc",
        "output_dir": args.output_dir,
        "config_path": args.config_path,
        "test_mode": args.test_mode,
        "skip_ai": args.skip_ai,
        "verbose": args.verbose
    }


def main():
    """Main entry point for the RC Release Automation Agent."""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Setup logging
        logger = get_logger(__name__)
        if args.verbose:
            logger.info("Verbose logging enabled")
        
        # Create parameters dictionary
        params = create_params_dict(args)
        
        # Show startup information
        logger.info("🚀 RC Release Automation Agent Starting")
        logger.info("=" * 60)
        logger.info(f"Service: {params['service_name']} {params['prod_version']} → {params['new_version']}")
        logger.info(f"Type: {params['release_type']}")
        logger.info(f"RC: {params['rc_name']} | Manager: {params['rc_manager']}")
        logger.info(f"Schedule: {params['day1_date']} (Day 1) → {params['day2_date']} (Day 2)")
        logger.info(f"Output: {params['output_dir']}")
        logger.info(f"Test Mode: {params['test_mode']}")
        logger.info("=" * 60)
        
        # Create output directory
        output_dir = Path(params["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Output directory: {output_dir.absolute()}")
        
        # Load configuration
        logger.info("🔧 Loading configuration...")
        config = load_config(params["config_path"])
        logger.info(f"✅ Configuration loaded from {params['config_path']}")
        
        # Fetch or create PR data
        if params["test_mode"]:
            logger.info("🧪 Using mock PR data for testing")
            prs, international_prs = create_mock_prs()
            params["international_prs"] = international_prs
        else:
            logger.info("🐙 Fetching PRs from GitHub...")
            prs = fetch_prs(params["prod_version"], params["new_version"], config.github)
            params["international_prs"] = []  # Would be extracted from real PRs
        
        logger.info(f"📋 Found {len(prs)} PRs for processing")
        
        # Generate release documentation
        logger.info("📝 Generating release documentation...")
        confluence_file = render_release_notes(prs, params, output_dir)
        logger.info(f"✅ Confluence release notes: {confluence_file}")
        
        # Generate markdown version
        markdown_file = render_release_notes_markdown(prs, params, output_dir)
        logger.info(f"✅ Markdown release notes: {markdown_file}")
        
        # Generate CRQ documents
        logger.info("📋 Generating CRQ documents...")
        crq_files = generate_crqs(prs, params, output_dir)
        logger.info(f"✅ CRQ documents generated: {len(crq_files)} files")
        
        # Validate generated files
        generated_files = []
        total_size = 0
        
        for file_path in [confluence_file, markdown_file] + crq_files:
            if file_path.exists():
                size = file_path.stat().st_size
                total_size += size
                generated_files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": size
                })
                logger.info(f"  📄 {file_path.name}: {size:,} bytes")
            else:
                logger.error(f"❌ Missing file: {file_path}")
        
        # Create summary
        summary = {
            "status": "success",
            "service_name": params["service_name"],
            "version_change": f"{params['prod_version']} → {params['new_version']}",
            "release_type": params["release_type"],
            "rc_name": params["rc_name"],
            "rc_manager": params["rc_manager"],
            "schedule": {
                "day1": params["day1_date"],
                "day2": params["day2_date"]
            },
            "generated_files": generated_files,
            "total_size": total_size,
            "pr_count": len(prs),
            "output_directory": str(output_dir.absolute())
        }
        
        # Save summary
        summary_file = output_dir / "automation_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        logger.info(f"📊 Summary saved: {summary_file}")
        
        # Output results
        logger.info("\n🎉 RC Release Automation Completed Successfully!")
        logger.info(f"📊 Generated {len(generated_files)} files ({total_size:,} total bytes)")
        logger.info(f"📁 All files saved to: {output_dir.absolute()}")
        
        if args.json_output:
            print(json.dumps(summary, indent=2))
        else:
            logger.info("\n📋 Generated Files:")
            for file_info in generated_files:
                logger.info(f"  📄 {file_info['name']} ({file_info['size']:,} bytes)")
            
            logger.info(f"\n🔗 Next Steps:")
            logger.info(f"  1. Copy release_notes.txt content into Confluence")
            logger.info(f"  2. Use CRQ files for change management process")
            logger.info(f"  3. Share with stakeholders and begin release process")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n⏹️ Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"\n❌ Release automation failed: {e}")
        if args.verbose:
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    exit(main()) 