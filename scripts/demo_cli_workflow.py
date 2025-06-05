#!/usr/bin/env python3
"""
Demo: RC Release Agent CLI Workflow

This demonstrates the complete interactive CLI workflow:
1. Interactive prompts collect release information  
2. Documents generated (CRQ + Confluence)
3. Slack configuration created for automated reminders
4. Shows how to run the Slack workflow

Usage:
    python demo_cli_workflow.py
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

def create_demo_config():
    """Create a demo configuration to show the structure"""
    
    # Calculate demo dates (tomorrow and day after)
    day1 = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    day2 = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    cutoff = (datetime.now() + timedelta(hours=8)).strftime("%Y-%m-%dT%H:00:00Z")
    
    demo_config = {
        "rc": "munoz",
        "rc_manager": "Charlie",
        "production_version": "v2.3.1",
        "new_version": "v2.4.0",
        "service_name": "cer-cart",
        "release_type": "standard",
        "day1_date": day1,
        "day2_date": day2,
        "cutoff_time": cutoff,
        "output_folder": "output/",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H%M%SZ")
    }
    
    return demo_config

def create_demo_slack_config(config, authors):
    """Create demo Slack configuration"""
    slack_config = {
        "channel": "#releases",
        "rc": f"@{config['rc']}",
        "rc_manager": f"@{config['rc_manager']}",
        "cutoff_time_utc": config["cutoff_time"],
        "reminder_intervals": [4, 1],  # 4 hours before, 1 hour before
        "authors": [f"@{author}" for author in authors],
        "day1_date": config["day1_date"],
        "day2_date": config["day2_date"],
        "service_name": config["service_name"],
        "production_version": config["production_version"],
        "new_version": config["new_version"]
    }
    
    return slack_config

def create_demo_authors():
    """Create demo PR authors list"""
    return ["alice", "bob", "carol", "david", "eve"]

def demonstrate_workflow():
    """Demonstrate the complete CLI workflow"""
    
    print("🎯 RC Release Agent CLI Workflow Demo")
    print("=" * 50)
    
    # Step 1: Show what interactive CLI would collect
    print("\n📝 Step 1: Interactive CLI Input Collection")
    print("   (In real usage: python run_release_agent.py rc_agent_build_release)")
    
    config = create_demo_config()
    print("   Collected configuration:")
    for key, value in config.items():
        print(f"     {key}: {value}")
    
    # Step 2: Document generation
    print(f"\n📋 Step 2: Document Generation")
    print("   - Fetches PRs from GitHub")
    print("   - Generates Confluence release notes")
    print("   - Creates CRQ documents")
    print("   - Extracts PR authors")
    
    authors = create_demo_authors()
    print(f"   Found {len(authors)} PR authors: {', '.join(authors)}")
    
    # Step 3: Slack configuration
    print(f"\n💬 Step 3: Slack Configuration Creation")
    slack_config = create_demo_slack_config(config, authors)
    
    # Save demo files
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Save RC config
    rc_config_path = output_dir / f"demo_rc_config_{config['timestamp']}.json"
    with open(rc_config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"   ✅ Created: {rc_config_path}")
    
    # Save Slack config
    slack_config_path = output_dir / f"demo_slack_config_{config['timestamp']}.json"
    with open(slack_config_path, "w") as f:
        json.dump(slack_config, f, indent=2)
    print(f"   ✅ Created: {slack_config_path}")
    
    # Save authors list
    authors_data = {
        "pr_authors": authors,
        "count": len(authors),
        "extracted_at": datetime.utcnow().isoformat() + "Z"
    }
    authors_path = output_dir / "demo_authors.json"
    with open(authors_path, "w") as f:
        json.dump(authors_data, f, indent=2)
    print(f"   ✅ Created: {authors_path}")
    
    # Step 4: Show Slack workflow commands
    print(f"\n🚀 Step 4: Slack Workflow Execution")
    print("   To start automated sign-off collection:")
    print(f"     python release_signoff_notifier.py --config {slack_config_path}")
    print("\n   For dry run testing:")
    print(f"     python release_signoff_notifier.py --config {slack_config_path} --dry-run")
    
    # Step 5: Show the generated Slack config content
    print(f"\n📄 Generated Slack Configuration:")
    print("   " + "-" * 40)
    print(json.dumps(slack_config, indent=2))
    print("   " + "-" * 40)
    
    # Step 6: Explain the automated workflow
    print(f"\n⏰ Automated Slack Workflow:")
    print("   1. 📤 Initial message sent immediately")
    print("   2. 🔔 Reminder sent 4 hours before cutoff")
    print("   3. 🚨 Final reminder sent 1 hour before cutoff")
    print("   4. ⚠️ Escalation message sent at cutoff time")
    
    print(f"\n✅ Demo complete! Check the files in output/ directory")
    
    return rc_config_path, slack_config_path

def demonstrate_slack_dry_run(slack_config_path):
    """Demonstrate what the Slack workflow would do"""
    print(f"\n🧪 Demonstrating Slack Workflow (Dry Run)")
    print("=" * 50)
    
    try:
        from release_signoff_notifier import load_slack_config, ReleaseSignoffNotifier
        
        # Load config and create notifier in dry run mode
        config = load_slack_config(slack_config_path)
        notifier = ReleaseSignoffNotifier(config, dry_run=True)
        
        print("📤 Initial Message Preview:")
        message = notifier.create_initial_message()
        print("   " + "-" * 40)
        print(message)
        print("   " + "-" * 40)
        
        print("\n📤 Reminder Message Preview:")
        reminder = notifier.create_reminder_message(4)
        print("   " + "-" * 40)
        print(reminder)
        print("   " + "-" * 40)
        
        print("\n📤 Final Escalation Message Preview:")
        final = notifier.create_final_message(all_signed_off=False)
        print("   " + "-" * 40)
        print(final)
        print("   " + "-" * 40)
        
    except ImportError as e:
        print(f"⚠️ Could not import Slack notifier: {e}")
        print("   This is expected if dependencies aren't fully installed")

if __name__ == "__main__":
    try:
        # Run the main demonstration
        rc_config_path, slack_config_path = demonstrate_workflow()
        
        # Show Slack message previews
        demonstrate_slack_dry_run(slack_config_path)
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Install dependencies: pip install -r requirements.txt")
        print(f"   2. Set environment variables (SLACK_BOT_TOKEN, GITHUB_TOKEN)")
        print(f"   3. Run: python run_release_agent.py rc_agent_build_release")
        print(f"   4. Test Slack workflow: python release_signoff_notifier.py --config {slack_config_path} --dry-run")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc() 