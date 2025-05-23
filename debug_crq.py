#!/usr/bin/env python3
"""Debug script to test CRQ generation exactly like the main code."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from types import SimpleNamespace
from crq.generate_crqs import generate_crqs
from config.config import load_config

def test_crq_generation():
    print("Testing CRQ generation with exact same logic as main code...")
    
    # Create mock PR
    mock_pr = SimpleNamespace()
    mock_pr.number = 123
    mock_pr.title = "Test PR"
    mock_pr.user = SimpleNamespace()
    mock_pr.user.login = "test-user"
    mock_pr.html_url = "https://github.com/test/repo/pull/123"
    mock_pr.labels = []
    mock_pr.body = "Test PR body"
    
    prs = [mock_pr]
    
    # Create test parameters
    params = {
        "prod_version": "v1.2.3",
        "new_version": "v1.3.0", 
        "service_name": "test-service",
        "release_type": "standard",
        "rc_name": "Test User",
        "rc_manager": "Test Manager",
        "day1_date": "2024-01-15",
        "day2_date": "2024-01-16",
        "config_path": "config/settings.test.yaml"
    }
    
    # Create output directory
    output_dir = Path("debug_outputs")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Load config
        config = load_config(params["config_path"])
        
        # Generate CRQs
        crq_files = generate_crqs(prs, params, output_dir, config=config)
        
        print(f"Generated {len(crq_files)} CRQ files:")
        for file_path in crq_files:
            print(f"  - {file_path} ({file_path.stat().st_size} bytes)")
            
            # Check content
            content = file_path.read_text()
            
            print(f"\n=== CONTENT ANALYSIS FOR {file_path.name} ===")
            if "===== Pull Requests Included =====" in content:
                print("❌ PROBLEM: PR list section found!")
            else:
                print("✅ No PR list section")
                
            if "Generated:" in content and "Total PRs:" in content:
                print("❌ PROBLEM: Automation footer found!")
            else:
                print("✅ No automation footer")
                
            if "Day 1 Validation:" in content:
                print("❌ PROBLEM: Built-in template style found!")
            else:
                print("✅ No built-in template style")
                
            print(f"First 200 chars: {content[:200]}")
            print(f"Last 200 chars: {content[-200:]}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_crq_generation() 