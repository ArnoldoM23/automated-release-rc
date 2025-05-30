# test_github_trigger.py

import os
import sys
import json

# Add src directory to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.cli.run_release_agent import trigger_github_workflow, write_config_file

def create_test_config():
    """Create a test configuration for GitHub Actions trigger"""
    return {
        "rc": "munoz",
        "rc_manager": "Charlie", 
        "production_version": "v2.3.1",
        "new_version": "v2.4.0",
        "service_name": "cer-cart",
        "release_type": "standard",
        "day1_date": "2025-05-29",
        "day2_date": "2025-05-30",
        "cutoff_time": "2025-05-29T23:00:00Z",
        "output_folder": "output/",
        "timestamp": "2025-05-28T120000Z"
    }

def test_github_integration():
    print("🧪 Testing GitHub Actions Integration")
    print("====================================\n")
    
    # Check if GitHub token is available
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN environment variable not set")
        return False
    
    print(f"✅ GitHub token found (starts with: {token[:20]}...)")
    
    # Create test configuration
    config = create_test_config()
    print("✅ Test configuration created")
    
    # Save config file
    config_path = write_config_file(config)
    print(f"✅ Config saved to: {config_path}")
    
    # Test GitHub workflow trigger
    try:
        print("\n🚀 Triggering GitHub Actions workflow...")
        trigger_github_workflow(config)
        print("✅ GitHub Actions trigger successful!")
        return True
        
    except Exception as e:
        print(f"❌ GitHub Actions trigger failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_github_integration()
    
    if success:
        print("\n🎉 GitHub integration test PASSED!")
        print("\n📋 Next steps:")
        print("1. Check your GitHub repository for the triggered workflow")
        print("2. Monitor the Actions tab in your GitHub repo")
        print("3. Once workflow completes, test with Slack token")
    else:
        print("\n❌ GitHub integration test FAILED")
        print("Please check your token permissions and repository access")
    
    sys.exit(0 if success else 1) 