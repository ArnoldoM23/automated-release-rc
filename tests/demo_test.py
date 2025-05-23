#!/usr/bin/env python3
"""
Demo Test Script - Generates sample outputs to show test capabilities
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import os
from types import SimpleNamespace
from datetime import datetime

def create_mock_prs():
    """Create sample PR data for testing."""
    prs = []
    
    # Schema PRs
    for i, title in enumerate([
        "Add userProfile field to GraphQL schema",
        "Deprecate legacy payment fields",
        "Update mutation signatures for cart operations"
    ], 101):
        pr = SimpleNamespace()
        pr.number = i
        pr.title = title
        pr.user = SimpleNamespace()
        pr.user.login = f"dev{i-100}"
        pr.html_url = f"https://github.com/example/repo/pull/{i}"
        pr.labels = []
        # Add schema label
        label = SimpleNamespace()
        label.name = "schema"
        pr.labels.append(label)
        pr.body = f"Schema update: {title}"
        prs.append(pr)
    
    # Feature PRs
    for i, title in enumerate([
        "Add express checkout flow",
        "Implement search autocomplete",
        "Add user dashboard analytics",
        "Add bulk operations API"
    ], 201):
        pr = SimpleNamespace()
        pr.number = i
        pr.title = title
        pr.user = SimpleNamespace()
        pr.user.login = f"dev{i-200}"
        pr.html_url = f"https://github.com/example/repo/pull/{i}"
        pr.labels = []
        # Add feature label
        label = SimpleNamespace()
        label.name = "feature"
        pr.labels.append(label)
        pr.body = f"New feature: {title}"
        prs.append(pr)
    
    # Bug fix PRs
    for i, title in enumerate([
        "Fix cart total calculation",
        "Resolve memory leak in webhooks",
        "Fix timezone handling in reports"
    ], 301):
        pr = SimpleNamespace()
        pr.number = i
        pr.title = title
        pr.user = SimpleNamespace()
        pr.user.login = f"dev{i-300}"
        pr.html_url = f"https://github.com/example/repo/pull/{i}"
        pr.labels = []
        # Add bug label
        label = SimpleNamespace()
        label.name = "bug"
        pr.labels.append(label)
        pr.body = f"Bug fix: {title}"
        prs.append(pr)
    
    return prs

def generate_demo_release_notes(prs, output_dir):
    """Generate demo release notes."""
    content = f"""# Release Notes - example-service v1.3.0

**Release Date:** 2024-01-16
**Release Coordinator:** Release Coordinator  
**Release Manager:** Release Manager  
**Release Type:** Standard

---

## 📋 Summary

This release includes {len(prs)} pull request(s) with the following changes:

* ✨ **4 New Features**
* 🐛 **3 Bug Fixes** 
* 🔗 **3 Schema Changes**

---

## 🔗 Schema Changes

"""
    
    schema_prs = [pr for pr in prs if any(label.name == "schema" for label in pr.labels)]
    for pr in schema_prs:
        content += f"* **PR #{pr.number}:** {pr.title}\n"
        content += f"  * Author: @{pr.user.login}\n"
        content += f"  * [View PR]({pr.html_url})\n\n"
    
    content += "## ✨ New Features\n\n"
    feature_prs = [pr for pr in prs if any(label.name == "feature" for label in pr.labels)]
    for pr in feature_prs:
        content += f"* **PR #{pr.number}:** {pr.title}\n"
        content += f"  * Author: @{pr.user.login}\n"
        content += f"  * [View PR]({pr.html_url})\n\n"
    
    content += "## 🐛 Bug Fixes\n\n"
    bug_prs = [pr for pr in prs if any(label.name == "bug" for label in pr.labels)]
    for pr in bug_prs:
        content += f"* **PR #{pr.number}:** {pr.title}\n"
        content += f"  * Author: @{pr.user.login}\n"
        content += f"  * [View PR]({pr.html_url})\n\n"
    
    content += f"""---

## 🚀 Deployment Information

**Deployment Schedule:**
* **Day 1 (2024-01-15):** Pre-deployment setup and validation
* **Day 2 (2024-01-16):** Production deployment

**Rollback Plan:** 
If issues are encountered, we can rollback to v1.2.3 using our standard rollback procedures.

**Validation:**
* All automated tests passing
* Manual QA validation completed
* Performance benchmarks verified
* Security scans completed

---

## 📞 Contact Information

**Release Coordinator:** Release Coordinator  
**Release Manager:** Release Manager  
**For issues or questions:** Contact the release team in #release-rc

---

*Generated automatically by RC Release Automation on {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}*
"""
    
    # Save to file
    release_file = output_dir / "release_notes.txt"
    with open(release_file, "w") as f:
        f.write(content)
    
    return release_file

def generate_demo_crq(output_dir):
    """Generate demo CRQ documents."""
    crq_content = f"""# Change Request (CRQ) - Day 1
# Service: example-service v1.3.0
# Date: 2024-01-15

## Executive Summary
This CRQ covers the pre-deployment activities for example-service v1.3.0, including 10 pull requests with new features, bug fixes, and schema changes.

## Change Description
**What is being changed:**
- Deployment of example-service v1.3.0
- 4 new features including express checkout and search improvements
- 3 critical bug fixes for cart calculations and memory leaks
- 3 schema updates with backward compatibility

**Business Impact:**
- Enhanced user experience with express checkout
- Improved system reliability with memory leak fixes
- Better search performance for customers

## Risk Assessment
**Risk Level:** MEDIUM

**Primary Risks:**
1. Schema changes may affect downstream services
2. New features require thorough testing
3. Memory leak fixes need validation

**Mitigation:**
- All changes tested in staging environment
- Rollback plan available to v1.2.3
- Monitoring alerts configured

## Implementation Plan
**Pre-deployment (Day 1):**
1. Deploy to staging environment
2. Run full test suite
3. Validate schema compatibility
4. Performance benchmark testing
5. Security vulnerability scan

**Production deployment scheduled for Day 2**

## Rollback Procedure
If issues occur:
1. Stop deployment immediately
2. Revert to v1.2.3 using automated rollback
3. Investigate and document issues
4. Plan remediation for next release

---
Generated by RC Release Automation on {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
"""
    
    crq_file = output_dir / "crq_day1.txt"
    with open(crq_file, "w") as f:
        f.write(crq_content)
    
    return crq_file

def generate_demo_summary(output_dir, files):
    """Generate test summary JSON."""
    summary = {
        "status": "success",
        "test_mode": True,
        "service_name": "example-service",
        "version_change": "v1.2.3 → v1.3.0",
        "release_type": "standard",
        "generated_files": [],
        "pr_count": 10,
        "timestamp": datetime.now().isoformat(),
        "output_directory": str(output_dir.absolute())
    }
    
    for file_path in files:
        if file_path.exists():
            summary["generated_files"].append({
                "name": file_path.name,
                "path": str(file_path),
                "size": file_path.stat().st_size
            })
    
    summary_file = output_dir / "test_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    return summary_file

def main():
    """Run demo test to generate sample outputs."""
    print("🚀 Running Demo Test - Generating Sample Outputs")
    print("=" * 60)
    
    # Create output directory
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Generate mock data
    print("📋 Creating mock PR data...")
    prs = create_mock_prs()
    print(f"✅ Created {len(prs)} PRs")
    
    # Generate outputs
    print("📝 Generating release notes...")
    release_file = generate_demo_release_notes(prs, output_dir)
    print(f"✅ Release notes: {release_file}")
    
    print("📋 Generating CRQ document...")
    crq_file = generate_demo_crq(output_dir)
    print(f"✅ CRQ document: {crq_file}")
    
    print("📊 Generating test summary...")
    summary_file = generate_demo_summary(output_dir, [release_file, crq_file])
    print(f"✅ Test summary: {summary_file}")
    
    # Show results
    print("\n📁 Generated Test Outputs:")
    total_size = 0
    for file_path in sorted(output_dir.glob("*")):
        size = file_path.stat().st_size
        total_size += size
        print(f"  📄 {file_path.name} ({size:,} bytes)")
    
    print(f"\n🎉 Demo completed successfully!")
    print(f"📊 Total output: {total_size:,} bytes")
    print(f"📁 Location: {output_dir.absolute()}")
    
    return True

if __name__ == "__main__":
    main() 