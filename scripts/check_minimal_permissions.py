# check_minimal_permissions.py

import os
import requests

def test_minimal_scopes():
    """
    Test what minimal GitHub token scopes work for repository dispatch
    """
    print("🔍 Testing Minimal GitHub Token Scopes")
    print("======================================\n")
    
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN not found")
        return
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    # Get current scopes
    response = requests.get("https://api.github.com/user", headers=headers)
    if response.status_code == 200:
        scopes = response.headers.get('X-OAuth-Scopes', '')
        print(f"📋 Current token scopes: '{scopes}'")
    
    print("\n🎯 What GitHub Documentation Says:")
    print("Repository dispatch requires one of:")
    print("• 'repo' scope (for any repository)")
    print("• 'public_repo' scope (for public repositories only)")
    print("• 'workflow' scope (for GitHub Actions)")
    
    print("\n💡 For your PUBLIC repository, you should only need:")
    print("• 'public_repo' scope (write access to public repos)")
    print("• 'workflow' scope (trigger Actions)")
    
    print(f"\n🔧 Recommended Token Scopes:")
    print(f"Instead of 'repo' (all repositories), try:")
    print(f"✅ public_repo - Public repository access")
    print(f"✅ workflow - GitHub Actions workflows")
    
    # Test what we actually have access to
    repo = "ArnoldoM23/automated-release-rc"
    print(f"\n🧪 Testing repository dispatch with current token...")
    
    dispatch_url = f"https://api.github.com/repos/{repo}/dispatches"
    test_payload = {
        "event_type": "test-minimal-permissions", 
        "client_payload": {"test": "minimal scopes"}
    }
    
    response = requests.post(dispatch_url, headers=headers, json=test_payload)
    
    if response.status_code == 204:
        print("✅ Repository dispatch works with current scopes!")
        print(f"Your current scopes ('{scopes}') are sufficient")
    else:
        print(f"❌ Repository dispatch failed: {response.status_code}")
        print(f"Response: {response.text}")
        
        print(f"\n🛠️ Token Update Options:")
        print(f"Option 1 (Minimal): public_repo + workflow")
        print(f"Option 2 (Standard): repo (what GitHub recommends)")
        print(f"Option 3 (Alternative): Try 'workflow' scope only")

if __name__ == "__main__":
    test_minimal_scopes() 