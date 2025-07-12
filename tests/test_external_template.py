#!/usr/bin/env python3
"""
Test script for external template and dashboard configuration features.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
import tempfile
from typing import Dict, Any

from src.config.config import load_config
from src.crq.external_template import ExternalTemplateManager

def test_dashboard_configuration():
    """Test dashboard URL configuration."""
    print("🔗 Testing Dashboard Configuration...")
    
    try:
        # Load test configuration
        config = load_config("src/config/settings.test.yaml")
        
        # Test dashboard URL access
        dashboard_urls = config.dashboard.get_dashboard_urls()
        
        print(f"✅ Dashboard URLs configured:")
        for key, url in dashboard_urls.items():
            print(f"  - {key}: {url}")
        
        # Verify all required URLs are present
        required_urls = [
            'confluence_dashboard_url', 'p0_dashboard_url', 'l1_dashboard_url',
            'services_dashboard_url', 'wcnp_dashboard_url', 'istio_dashboard_url'
        ]
        
        missing_urls = []
        for url_key in required_urls:
            if url_key not in dashboard_urls:
                print(f"❌ Missing required dashboard URL: {url_key}")
                missing_urls.append(url_key)
        
        assert not missing_urls, f"Missing required dashboard URLs: {missing_urls}"
        print(f"✅ All {len(required_urls)} dashboard URLs configured correctly")
        
    except Exception as e:
        print(f"❌ Dashboard configuration test failed: {e}")
        assert False, f"Dashboard configuration test failed: {e}"

def test_external_template_manager():
    """Test external template manager functionality."""
    print("\n📄 Testing External Template Manager...")
    
    try:
        # Load test configuration  
        config = load_config("src/config/settings.test.yaml")
        
        # Create external template manager
        manager = ExternalTemplateManager(config)
        
        # Test template conversion
        sample_template = """
        Summary: {service_name} Application Code deployment for {platform} ({regions}) - Day {day_number}
        
        Description Section:
        Application Name: {service_name}
        Namespace: {namespace}
        
        Day 1 activities:
        - Prepare deployment
        - Validate environment
        
        Day 2 activities:
        - Execute deployment
        - Monitor results
        """
        
        converted = manager.convert_to_jinja_template(sample_template)
        print("✅ Template conversion successful")
        print("📝 Converted template preview:")
        print(converted[:200] + "..." if len(converted) > 200 else converted)
        
        # Test cache directory creation
        print(f"📁 Cache directory: {manager.cache_dir}")
        print(f"✅ Cache directory exists: {manager.cache_dir.exists()}")
        
        assert converted is not None, "Template conversion should not return None"
        
    except Exception as e:
        print(f"❌ External template manager test failed: {e}")
        assert False, f"External template manager test failed: {e}"

def test_configuration_loading():
    """Test loading configuration with new sections."""
    print("\n⚙️ Testing Configuration Loading...")
    
    try:
        # Load test configuration
        config = load_config("src/config/settings.test.yaml")
        
        # Check dashboard config
        print(f"✅ Dashboard URLs configured:")
        dashboard_urls = config.dashboard.get_dashboard_urls()
        for key, url in dashboard_urls.items():
            print(f"  - {key}: {url}")
        
        # Check external template config
        print(f"✅ External template config:")
        print(f"  - Enabled: {config.external_template.enabled}")
        print(f"  - Fallback: {config.external_template.fallback_to_builtin}")
        print(f"  - Cache duration: {config.external_template.cache_duration}s")
        
        assert config is not None, "Configuration should not be None"
        assert hasattr(config, 'dashboard'), "Configuration should have dashboard section"
        assert hasattr(config, 'external_template'), "Configuration should have external_template section"
        
    except Exception as e:
        print(f"❌ Configuration loading test failed: {e}")
        assert False, f"Configuration loading test failed: {e}"

def main():
    """Run all tests."""
    print("🧪 Testing New Dashboard and External Template Features")
    print("=" * 60)
    
    tests = [
        test_configuration_loading,
        test_dashboard_configuration, 
        test_external_template_manager
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        print("\n💡 How to use these features:")
        print("1. 📝 Configure dashboard URLs in your settings.yaml:")
        print("   dashboard:")
        print("     confluence_dashboard_url: 'https://confluence.yourcompany.com/display/SERVICE/Dashboards'")
        print("     p0_dashboard_url: 'https://grafana.yourcompany.com/d/service-p0'")
        print("     l1_dashboard_url: 'https://grafana.yourcompany.com/d/service-l1'")
        print()
        print("2. 🌐 Enable external template downloading:")
        print("   external_template:")
        print("     enabled: true")
        print("     template_url: 'https://your-sharepoint.com/CRQ_Template.docx'")
        print("     fallback_to_builtin: true")
    else:
        print("❌ Some tests failed. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 