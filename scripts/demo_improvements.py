#!/usr/bin/env python3
"""
Demo script showing the new improvements to RC Release Agent:

1. RC Name Enhancement: "Arnoldo Munoz (a0m02bh)" instead of just "a0m02bh"
2. Service Name Pre-filling: Extract "PerfCopilot" from "ArnoldoM23/PerfCopilot"
3. PR Author Name Enhancement: "Arnoldo Munoz @ArnoldoM23" instead of just "@githubusername"
4. International/Tenant Labels: Configurable labels for section 9 filtering
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config.config import load_config, extract_service_name_from_repo
from src.github_integration.fetch_prs import GitHubClient
from src.release_notes.release_notes import filter_international_prs


def demo_improvement_1():
    """Demo 1: RC Name Enhancement"""
    print("=" * 60)
    print("🚀 IMPROVEMENT 1: RC Name Enhancement")
    print("=" * 60)
    print("BEFORE: RC field shows just 'a0m02bh'")
    print("AFTER:  RC field shows 'Arnoldo Munoz (a0m02bh)'")
    print()
    
    try:
        config = load_config()
        if config.github.token and not config.github.token.startswith("xoxb-000000000000"):
            github_client = GitHubClient(config.github)
            
            # Simulate getting user display name
            current_user = os.getenv("USER", "testuser")
            print(f"Current USER env: {current_user}")
            
            try:
                enhanced_name = github_client.get_user_display_name(current_user)
                print(f"✅ Enhanced RC name: {enhanced_name}")
            except Exception as e:
                print(f"⚠️ Could not fetch from GitHub: {e}")
                print(f"📋 Fallback: @{current_user}")
        else:
            print("⚠️ GitHub token not configured - using fallback")
            current_user = os.getenv("USER", "testuser")
            print(f"📋 Would show: @{current_user}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_improvement_2():
    """Demo 2: Service Name Pre-filling"""
    print("\n" + "=" * 60)
    print("🎯 IMPROVEMENT 2: Service Name Pre-filling")
    print("=" * 60)
    print("BEFORE: User always types service name manually")
    print("AFTER:  Auto-extracts 'PerfCopilot' from 'ArnoldoM23/PerfCopilot'")
    print()
    
    try:
        config = load_config()
        repo_url = config.github.repo
        print(f"GitHub repo: {repo_url}")
        
        extracted_service = extract_service_name_from_repo(repo_url)
        print(f"✅ Extracted service name: {extracted_service}")
        
        # Test with other examples
        test_repos = [
            "company/service-cart",
            "org/api-payments",
            "user/microservice-auth",
            "team/MyAwesomeApp"
        ]
        
        print("\n📋 Other examples:")
        for repo in test_repos:
            service = extract_service_name_from_repo(repo)
            print(f"  {repo} → {service}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_improvement_3():
    """Demo 3: PR Author Name Enhancement"""
    print("\n" + "=" * 60)
    print("👥 IMPROVEMENT 3: PR Author Name Enhancement")
    print("=" * 60)
    print("BEFORE: Release notes show '@githubusername'")
    print("AFTER:  Release notes show 'Arnoldo Munoz @ArnoldoM23'")
    print()
    
    print("Example output in release notes:")
    print("OLD: | ❌ | [#22|...] | @ArnoldoM23 | fix stable version... |")
    print("NEW: | ❌ | [#22|...] | Arnoldo Munoz @ArnoldoM23 | fix stable version... |")
    print()
    
    try:
        config = load_config()
        if config.github.token and not config.github.token.startswith("xoxb-000000000000"):
            github_client = GitHubClient(config.github)
            
            # Test with some usernames
            test_users = ["ArnoldoM23", os.getenv("USER", "testuser")]
            
            for username in test_users:
                try:
                    display_name = github_client.get_user_display_name(username)
                    print(f"✅ {username} → {display_name}")
                except Exception as e:
                    print(f"⚠️ {username} → @{username} (fallback: {e})")
        else:
            print("⚠️ GitHub token not configured - showing format only")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_improvement_4():
    """Demo 4: International/Tenant Labels Configuration"""
    print("\n" + "=" * 60)
    print("🌍 IMPROVEMENT 4: International/Tenant Labels")
    print("=" * 60)
    print("BEFORE: Section 9 always shows 'No internationalization changes'")
    print("AFTER:  Section 9 shows PRs with configurable labels")
    print()
    
    try:
        config = load_config()
        
        # Show configured labels
        if hasattr(config.organization, 'international_labels'):
            labels = config.organization.international_labels
            print(f"📋 Configured international labels: {labels}")
        else:
            print("📋 Using default international labels")
            
        print("\nExample: PR with label 'i18n' will now appear in Section 9")
        print("Example: PR with 'tenant' in title will appear in Section 9")
        print("Example: PR with 'localization' label will appear in Section 9")
        
        # Simulate filtering (with mock data since we might not have real PRs)
        print("\n🧪 Testing filter function:")
        
        # Create mock PR objects
        class MockPR:
            def __init__(self, number, title, labels, body=""):
                self.number = number
                self.title = title
                self.labels = [MockLabel(label) for label in labels]
                self.body = body
                
        class MockLabel:
            def __init__(self, name):
                self.name = name
        
        mock_prs = [
            MockPR(101, "Add localization support for French", ["i18n", "feature"]),
            MockPR(102, "Fix bug in payment flow", ["bug"]),
            MockPR(103, "Update tenant configuration system", ["tenant", "config"]),
            MockPR(104, "Improve international date formatting", []),
        ]
        
        international_prs = filter_international_prs(mock_prs, config)
        
        print(f"✅ Found {len(international_prs)} international PRs:")
        for pr in international_prs:
            label_names = [label.name for label in pr.labels]
            print(f"  - PR #{pr.number}: {pr.title} (labels: {label_names})")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all improvement demos"""
    print("🎉 RC RELEASE AGENT - NEW IMPROVEMENTS DEMO")
    print("Based on feedback from leadership demo")
    
    demo_improvement_1()
    demo_improvement_2() 
    demo_improvement_3()
    demo_improvement_4()
    
    print("\n" + "=" * 60)
    print("✅ ALL IMPROVEMENTS IMPLEMENTED!")
    print("=" * 60)
    print("🚀 Version 2.0 Demo Complete!")
    print("\n📋 Next Steps:")
    print("1. Set up your GitHub token: export GITHUB_TOKEN='ghp_...'")
    print("2. Run: rc-release-agent")
    print("3. Test the improvements with real data")
    print("4. Deploy to production!")


if __name__ == "__main__":
    main() 