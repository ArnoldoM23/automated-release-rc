# check_github_permissions.py

import os
import requests

def check_github_token_permissions():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN not found")
        return
    
    print("🔍 Checking GitHub Token Permissions")
    print("====================================\n")
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    # Check user info and token scopes
    print("1. Testing basic API access...")
    response = requests.get("https://api.github.com/user", headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Token works! User: {user_data.get('login', 'Unknown')}")
        
        # Check token scopes
        scopes = response.headers.get('X-OAuth-Scopes', '')
        print(f"📋 Current token scopes: {scopes}")
        
    else:
        print(f"❌ Basic API test failed: {response.status_code}")
        print(response.text)
        return
    
    # Test repository access
    repo = "ArnoldoM23/automated-release-rc"
    print(f"\n2. Testing repository access ({repo})...")
    
    repo_url = f"https://api.github.com/repos/{repo}"
    response = requests.get(repo_url, headers=headers)
    
    if response.status_code == 200:
        repo_data = response.json()
        print(f"✅ Repository accessible: {repo_data.get('full_name')}")
        print(f"📊 Repository permissions: {repo_data.get('permissions', {})}")
    else:
        print(f"❌ Repository access failed: {response.status_code}")
        print(response.text)
        return
    
    # Test dispatch endpoint (the failing one)
    print(f"\n3. Testing repository dispatch endpoint...")
    dispatch_url = f"https://api.github.com/repos/{repo}/dispatches"
    
    # Try a minimal test payload
    test_payload = {
        "event_type": "test-permissions",
        "client_payload": {"test": "true"}
    }
    
    response = requests.post(dispatch_url, headers=headers, json=test_payload)
    
    if response.status_code == 204:
        print("✅ Repository dispatch works!")
    else:
        print(f"❌ Repository dispatch failed: {response.status_code}")
        print(response.text)
        
        print(f"\n🔧 SOLUTION NEEDED:")
        print(f"Your GitHub token needs additional permissions:")
        print(f"1. Go to: https://github.com/settings/tokens")
        print(f"2. Find your token or create a new one")
        print(f"3. Make sure these scopes are checked:")
        print(f"   ✅ repo (Full control of private repositories)")
        print(f"   ✅ workflow (Update GitHub Action workflows)")
        print(f"   ✅ write:repo_hook (Write repository hooks)")
        print(f"\n📋 Current scopes: {scopes}")
        print(f"📋 Required scopes: repo, workflow")

if __name__ == "__main__":
    check_github_token_permissions() 