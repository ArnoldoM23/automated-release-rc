#!/usr/bin/env python3
"""Debug script to test CRQ template loading."""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader

def test_template():
    template_path = Path("templates")
    
    print(f"Template directory: {template_path.absolute()}")
    print(f"Template exists: {(template_path / 'crq_template.j2').exists()}")
    
    if (template_path / "crq_template.j2").exists():
        print("Loading enterprise template...")
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("crq_template.j2")
        
        # Test with minimal vars
        test_vars = {
            "service_name": "test-service",
            "platform": "Glass",
            "regions": ["EUS", "SCUS"],
            "day_number": "1",
            "namespace": "test-service",
            "assembly": "test-assembly",
            "prod_version": "v1.0.0",
            "new_version": "v1.1.0",
            "confluence_link": "https://test.com",
            "total_prs": 5,
            "ai_analysis": {
                "BUSINESS_IMPACT": "Test impact",
                "VALIDATION_STEPS": "Test validation",
                "RISK_ASSESSMENT": "Test risk",
                "ROLLBACK_SCENARIOS": "Test rollback"
            },
            "dashboard_url": "https://test.com",
            "grafana_url": "https://test.com",
            "l1_dashboard_url": "https://test.com",
            "services_dashboard_url": "https://test.com",
            "wcnp_dashboard_url": "https://test.com",
            "istio_dashboard_url": "https://test.com"
        }
        
        content = template.render(**test_vars)
        print(f"Generated content length: {len(content)}")
        print("First 500 chars:")
        print(content[:500])
        print("Last 500 chars:")
        print(content[-500:])
        
        # Check for problematic sections
        if "===== Pull Requests Included =====" in content:
            print("❌ PROBLEM: PR list section found in template!")
        else:
            print("✅ No PR list section found")
            
        if "Generated:" in content:
            print("❌ PROBLEM: Automation footer found in template!")
        else:
            print("✅ No automation footer found")
            
        if "Day 1 Validation:" in content:
            print("❌ PROBLEM: Built-in template style found!")
        else:
            print("✅ No built-in template style found")
    else:
        print("Template not found!")

if __name__ == "__main__":
    test_template() 