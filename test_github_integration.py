#!/usr/bin/env python3
"""
GitHub Integration Testing Script

Test the GitHub PR fetching functionality with a real repository.
This validates that the GitHub logic works correctly for fetching PRs between tags.

Usage:
    export GITHUB_TOKEN="ghp_your-token"
    python test_github_integration.py --repo owner/repo --old-tag v1.0.0 --new-tag v1.1.0
    python test_github_integration.py --test-all  # Interactive setup
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.logging import get_logger
from config.config import GitHubConfig
from github_integration.fetch_prs import GitHubClient, fetch_prs


def check_github_environment():
    """Check if GitHub environment is properly configured."""
    logger = get_logger(__name__)
    logger.info("🔐 Checking GitHub environment setup...")
    
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        logger.error("❌ GITHUB_TOKEN environment variable not set")
        logger.info("📋 How to set up GitHub token:")
        logger.info("1. Go to https://github.com/settings/tokens")
        logger.info("2. Click 'Generate new token (classic)'")
        logger.info("3. Select scopes: 'repo' (or 'public_repo' for public repos only)")
        logger.info("4. Copy token and set: export GITHUB_TOKEN='ghp_your-token-here'")
        return False
    
    if not token.startswith("ghp_") and not token.startswith("github_pat_"):
        logger.warning(f"⚠️ Token format seems unusual. Expected 'ghp_' or 'github_pat_' prefix")
    
    if len(token) < 20:
        logger.error(f"❌ Token seems too short: {len(token)} characters")
        return False
    
    logger.info(f"✅ GitHub token configured (length: {len(token)})")
    return True


def test_repository_access(repo_name: str):
    """Test basic repository access."""
    logger = get_logger(__name__)
    logger.info(f"🏢 Testing repository access: {repo_name}")
    
    try:
        config = GitHubConfig(
            token=os.environ.get("GITHUB_TOKEN"),
            repo=repo_name,
            api_url="https://api.github.com"
        )
        
        client = GitHubClient(config)
        repo_info = client.get_repository_info()
        
        if repo_info:
            logger.info("✅ Repository access successful:")
            logger.info(f"   - Name: {repo_info.get('name', 'N/A')}")
            logger.info(f"   - Full Name: {repo_info.get('full_name', 'N/A')}")
            logger.info(f"   - Description: {repo_info.get('description', 'No description')}")
            logger.info(f"   - Default Branch: {repo_info.get('default_branch', 'N/A')}")
            logger.info(f"   - Private: {repo_info.get('private', 'N/A')}")
            logger.info(f"   - URL: {repo_info.get('url', 'N/A')}")
            return True
        else:
            logger.error("❌ Could not fetch repository information")
            return False
            
    except Exception as e:
        logger.error(f"❌ Repository access failed: {e}")
        logger.info("💡 Possible issues:")
        logger.info("- Repository name format should be 'owner/repo'")
        logger.info("- Token might not have access to this repository")
        logger.info("- Repository might not exist or be private")
        return False


def test_tag_validation(repo_name: str, old_tag: str, new_tag: str):
    """Test that both tags exist in the repository."""
    logger = get_logger(__name__)
    logger.info(f"🏷️ Validating tags: {old_tag} → {new_tag}")
    
    try:
        config = GitHubConfig(
            token=os.environ.get("GITHUB_TOKEN"),
            repo=repo_name,
            api_url="https://api.github.com"
        )
        
        client = GitHubClient(config)
        
        # Check old tag
        if client.validate_tag(old_tag):
            logger.info(f"✅ Old tag '{old_tag}' exists")
        else:
            logger.error(f"❌ Old tag '{old_tag}' not found")
            return False
        
        # Check new tag
        if client.validate_tag(new_tag):
            logger.info(f"✅ New tag '{new_tag}' exists")
        else:
            logger.error(f"❌ New tag '{new_tag}' not found")
            return False
        
        logger.info("✅ Both tags validated successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Tag validation failed: {e}")
        return False


def test_pr_fetching(repo_name: str, old_tag: str, new_tag: str):
    """Test fetching PRs between two tags."""
    logger = get_logger(__name__)
    logger.info(f"📥 Testing PR fetching between {old_tag} and {new_tag}")
    
    try:
        config = GitHubConfig(
            token=os.environ.get("GITHUB_TOKEN"),
            repo=repo_name,
            api_url="https://api.github.com"
        )
        
        # Fetch PRs using the main function
        prs = fetch_prs(old_tag, new_tag, config)
        
        logger.info(f"✅ Successfully fetched {len(prs)} PRs")
        
        if prs:
            logger.info("📋 PR Summary:")
            for i, pr in enumerate(prs[:10], 1):  # Show first 10 PRs
                labels = [label.name for label in pr.labels] if pr.labels else []
                logger.info(f"   {i}. #{pr.number}: {pr.title}")
                logger.info(f"      Author: {pr.user.login}")
                logger.info(f"      Labels: {labels}")
                logger.info(f"      URL: {pr.html_url}")
                
            if len(prs) > 10:
                logger.info(f"   ... and {len(prs) - 10} more PRs")
        else:
            logger.info("📋 No PRs found between these tags")
            logger.info("💡 This could mean:")
            logger.info("- No PRs were merged between these tags")
            logger.info("- PRs don't have merge commit messages with PR numbers")
            logger.info("- Tags are very close together")
        
        return prs
        
    except Exception as e:
        logger.error(f"❌ PR fetching failed: {e}")
        logger.info("💡 Possible issues:")
        logger.info("- Network connectivity problems")
        logger.info("- GitHub API rate limiting")
        logger.info("- Repository access permissions")
        return None


def test_pr_categorization(prs: List):
    """Test PR categorization logic."""
    logger = get_logger(__name__)
    logger.info("🏷️ Testing PR categorization...")
    
    try:
        from notes.release_notes import categorize_prs
        
        categories = categorize_prs(prs)
        
        logger.info("✅ PR categorization results:")
        total_categorized = 0
        for category, prs_in_category in categories.items():
            if prs_in_category:
                total_categorized += len(prs_in_category)
                logger.info(f"   - {category}: {len(prs_in_category)} PRs")
                
                # Show first few PRs in each category
                for pr in prs_in_category[:3]:
                    logger.info(f"     • #{pr.number}: {pr.title}")
                if len(prs_in_category) > 3:
                    logger.info(f"     ... and {len(prs_in_category) - 3} more")
        
        logger.info(f"✅ Total categorized: {total_categorized}/{len(prs)} PRs")
        return categories
        
    except Exception as e:
        logger.error(f"❌ PR categorization failed: {e}")
        return None


def get_repository_tags(repo_name: str, limit: int = 20):
    """Get latest tags from repository for user reference."""
    logger = get_logger(__name__)
    logger.info(f"🏷️ Fetching latest tags from {repo_name}...")
    
    try:
        config = GitHubConfig(
            token=os.environ.get("GITHUB_TOKEN"),
            repo=repo_name,
            api_url="https://api.github.com"
        )
        
        client = GitHubClient(config)
        tags = client.get_latest_tags(limit)
        
        if tags:
            logger.info(f"📋 Latest {len(tags)} tags:")
            for i, tag in enumerate(tags, 1):
                logger.info(f"   {i}. {tag}")
        else:
            logger.warning("⚠️ No tags found in repository")
            
        return tags
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch tags: {e}")
        return []


def interactive_setup():
    """Interactive setup to get repository and tag information."""
    logger = get_logger(__name__)
    logger.info("🚀 Interactive GitHub Integration Setup")
    
    # Check environment first
    if not check_github_environment():
        return None
    
    print("\n" + "="*60)
    print("📋 Repository Information")
    print("="*60)
    
    # Get repository name
    repo_name = input("Enter repository (owner/repo format): ").strip()
    if not repo_name or "/" not in repo_name:
        logger.error("❌ Invalid repository format. Use 'owner/repo'")
        return None
    
    # Test repository access
    if not test_repository_access(repo_name):
        return None
    
    # Get available tags
    tags = get_repository_tags(repo_name)
    
    if not tags:
        logger.error("❌ No tags found. Repository needs tags to test PR fetching.")
        return None
    
    print(f"\n📋 Available tags (showing latest {len(tags)}):")
    for i, tag in enumerate(tags, 1):
        print(f"   {i}. {tag}")
    
    # Get tag selection
    print("\n" + "="*60)
    print("🏷️ Tag Selection")
    print("="*60)
    
    old_tag = input("Enter old tag (e.g., v1.0.0): ").strip()
    new_tag = input("Enter new tag (e.g., v1.1.0): ").strip()
    
    if not old_tag or not new_tag:
        logger.error("❌ Both tags are required")
        return None
    
    return {
        "repo_name": repo_name,
        "old_tag": old_tag,
        "new_tag": new_tag
    }


def run_comprehensive_test(repo_name: str, old_tag: str, new_tag: str):
    """Run comprehensive GitHub integration test."""
    logger = get_logger(__name__)
    logger.info("🧪 Running comprehensive GitHub integration test")
    logger.info("="*60)
    
    tests = [
        ("Environment Check", lambda: check_github_environment()),
        ("Repository Access", lambda: test_repository_access(repo_name)),
        ("Tag Validation", lambda: test_tag_validation(repo_name, old_tag, new_tag)),
    ]
    
    passed = 0
    total = len(tests)
    
    # Run basic tests first
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Running {test_name}...")
        try:
            if test_func():
                logger.info(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name}: FAILED")
                logger.info("🛑 Stopping tests due to failure")
                break
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            break
    
    # If basic tests pass, run PR fetching
    if passed == total:
        logger.info(f"\n🔍 Running PR Fetching Test...")
        try:
            prs = test_pr_fetching(repo_name, old_tag, new_tag)
            if prs is not None:
                logger.info("✅ PR Fetching: PASSED")
                passed += 1
                
                # Test categorization if we have PRs
                if prs:
                    logger.info(f"\n🔍 Running PR Categorization Test...")
                    categories = test_pr_categorization(prs)
                    if categories is not None:
                        logger.info("✅ PR Categorization: PASSED")
                        passed += 1
                    else:
                        logger.error("❌ PR Categorization: FAILED")
                else:
                    logger.info("⚠️ Skipping categorization test (no PRs found)")
                    passed += 1  # Count as pass since fetching worked
                
            else:
                logger.error("❌ PR Fetching: FAILED")
        except Exception as e:
            logger.error(f"❌ PR Fetching: ERROR - {e}")
    
    total_tests = passed + (2 if passed == total else 0)  # Add PR tests if basic tests passed
    
    logger.info(f"\n📊 Test Results: {passed}/{total_tests} tests passed")
    
    if passed == total_tests:
        logger.info("🎉 All GitHub integration tests passed!")
        logger.info("✅ Your GitHub logic is working correctly")
    else:
        logger.error("❌ Some tests failed. Check the issues above.")
    
    return passed == total_tests


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test GitHub integration functionality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python test_github_integration.py --test-all
    python test_github_integration.py --repo ArnoldoM23/my-project --old-tag v1.0.0 --new-tag v1.1.0
    python test_github_integration.py --list-tags --repo ArnoldoM23/my-project
        """
    )
    
    parser.add_argument("--repo", help="Repository in owner/repo format")
    parser.add_argument("--old-tag", help="Older tag for PR fetching")
    parser.add_argument("--new-tag", help="Newer tag for PR fetching")
    parser.add_argument("--list-tags", action="store_true", help="List available tags")
    parser.add_argument("--test-all", action="store_true", help="Interactive test setup")
    
    args = parser.parse_args()
    
    if args.test_all:
        setup = interactive_setup()
        if setup:
            success = run_comprehensive_test(
                setup["repo_name"], 
                setup["old_tag"], 
                setup["new_tag"]
            )
            sys.exit(0 if success else 1)
        else:
            sys.exit(1)
    
    elif args.list_tags:
        if not args.repo:
            logger.error("❌ --repo is required when using --list-tags")
            sys.exit(1)
        
        if check_github_environment():
            get_repository_tags(args.repo)
        sys.exit(0)
    
    elif args.repo and args.old_tag and args.new_tag:
        success = run_comprehensive_test(args.repo, args.old_tag, args.new_tag)
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 