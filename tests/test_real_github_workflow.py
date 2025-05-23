#!/usr/bin/env python3
"""
Real GitHub Workflow Integration Test

This test fetches real pull requests from GitHub and generates complete release documentation
including release notes and CRQ documents for Day 1 and Day 2.

Usage:
    python test_real_github_workflow.py --help
    python test_real_github_workflow.py --repo ArnoldoM23/PerfCopilot --old-tag v0.0.1 --new-tag v0.4.7
    python test_real_github_workflow.py --test-all  # Uses default test repository
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from utils.logging import get_logger
from github_integration.fetch_prs import fetch_prs
from notes.release_notes import render_release_notes, render_release_notes_markdown
from crq.generate_crqs import generate_crqs
from config.config import load_config, GitHubConfig


class RealGitHubWorkflowTester:
    """Test the complete workflow using real GitHub data."""
    
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.logger = get_logger(__name__)
        
        # Set environment variable for GitHub integration
        os.environ['GITHUB_TOKEN'] = github_token
        
    def test_complete_workflow(
        self,
        repo: str,
        old_tag: str,
        new_tag: str,
        service_name: Optional[str] = None,
        rc_name: str = "Test RC",
        rc_manager: str = "Test Manager"
    ) -> Dict[str, Any]:
        """Test the complete workflow from PR fetching to document generation."""
        
        self.logger.info("🚀 Starting Real GitHub Workflow Integration Test")
        self.logger.info("=" * 70)
        self.logger.info(f"Repository: {repo}")
        self.logger.info(f"Version Range: {old_tag} → {new_tag}")
        self.logger.info(f"Service: {service_name or repo.split('/')[-1]}")
        self.logger.info("=" * 70)
        
        results = {
            "success": False,
            "repo": repo,
            "old_tag": old_tag,
            "new_tag": new_tag,
            "prs_fetched": 0,
            "files_generated": [],
            "errors": [],
            "output_directory": None
        }
        
        try:
            # Step 1: Fetch PRs from GitHub
            self.logger.info("📥 Step 1: Fetching pull requests from GitHub...")
            prs = self._fetch_prs(repo, old_tag, new_tag)
            results["prs_fetched"] = len(prs)
            
            if not prs:
                error_msg = f"No pull requests found between {old_tag} and {new_tag}"
                self.logger.error(f"❌ {error_msg}")
                results["errors"].append(error_msg)
                return results
                
            self.logger.info(f"✅ Fetched {len(prs)} pull requests")
            
            # Step 2: Prepare parameters
            self.logger.info("⚙️ Step 2: Preparing release parameters...")
            params = self._prepare_params(repo, old_tag, new_tag, service_name, rc_name, rc_manager)
            self.logger.info(f"✅ Parameters prepared for {params['service_name']}")
            
            # Step 3: Create output directory
            output_dir = self._create_output_directory(repo, new_tag)
            results["output_directory"] = str(output_dir)
            self.logger.info(f"✅ Output directory: {output_dir}")
            
            # Step 4: Load configuration
            self.logger.info("🔧 Step 3: Loading configuration...")
            config = load_config("config/settings.test.yaml")
            self.logger.info("✅ Configuration loaded")
            
            # Step 5: Generate release notes
            self.logger.info("📝 Step 4: Generating release notes...")
            release_files = self._generate_release_notes(prs, params, output_dir, config)
            results["files_generated"].extend(release_files)
            self.logger.info(f"✅ Generated {len(release_files)} release note files")
            
            # Step 6: Generate CRQ documents
            self.logger.info("📋 Step 5: Generating CRQ documents...")
            crq_files = self._generate_crq_documents(prs, params, output_dir, config)
            results["files_generated"].extend(crq_files)
            self.logger.info(f"✅ Generated {len(crq_files)} CRQ files")
            
            # Step 7: Validate outputs
            self.logger.info("✅ Step 6: Validating generated files...")
            validation_results = self._validate_outputs(results["files_generated"])
            
            if validation_results["all_valid"]:
                results["success"] = True
                self.logger.info("✅ All files validated successfully")
            else:
                results["errors"].extend(validation_results["errors"])
                self.logger.error("❌ Some files failed validation")
            
            # Step 8: Generate summary
            self._generate_summary(results, prs, params)
            
        except Exception as e:
            error_msg = f"Workflow test failed: {e}"
            self.logger.error(f"❌ {error_msg}")
            results["errors"].append(error_msg)
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            
        return results
    
    def _fetch_prs(self, repo: str, old_ref: str, new_ref: str) -> List:
        """Fetch PRs between Git references (tags or commit SHAs) using the existing GitHub integration."""
        try:
            # Create a proper GitHubConfig object for the fetch function
            github_config = GitHubConfig(
                token=self.github_token,
                repo=repo,
                api_url="https://api.github.com"
            )
            
            prs = fetch_prs(old_ref, new_ref, github_config)
            self.logger.info(f"Successfully fetched {len(prs)} PRs from {repo}")
            
            # Log PR summary
            for i, pr in enumerate(prs[:5], 1):  # Show first 5 PRs
                labels = [label.name for label in pr.labels] if pr.labels else []
                self.logger.info(f"  {i}. PR #{pr.number}: {pr.title} (Labels: {labels})")
            
            if len(prs) > 5:
                self.logger.info(f"  ... and {len(prs) - 5} more PRs")
                
            return prs
            
        except Exception as e:
            self.logger.error(f"Failed to fetch PRs: {e}")
            raise
    
    def _prepare_params(
        self, 
        repo: str, 
        old_tag: str, 
        new_tag: str, 
        service_name: Optional[str],
        rc_name: str,
        rc_manager: str
    ) -> Dict[str, Any]:
        """Prepare parameters for document generation."""
        
        # Use repo name as service name if not provided
        if not service_name:
            service_name = repo.split('/')[-1].lower().replace('-', '_')
        
        # Calculate dates (Day 1 tomorrow, Day 2 day after)
        tomorrow = datetime.now() + timedelta(days=1)
        day_after = datetime.now() + timedelta(days=2)
        
        return {
            "service_name": service_name,
            "prod_version": old_tag,
            "new_version": new_tag,
            "release_type": "standard",
            "rc_name": rc_name,
            "rc_manager": rc_manager,
            "day1_date": tomorrow.strftime("%Y-%m-%d"),
            "day2_date": day_after.strftime("%Y-%m-%d"),
            "config_path": "config/settings.test.yaml",
            "github_repo": repo,
            "output_dir": f"test_outputs/{service_name}_{new_tag}"
        }
    
    def _create_output_directory(self, repo: str, version: str) -> Path:
        """Create output directory for generated files."""
        service_name = repo.split('/')[-1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"test_outputs/{service_name}_{version}_{timestamp}")
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def _generate_release_notes(self, prs: List, params: Dict[str, Any], output_dir: Path, config) -> List[str]:
        """Generate release notes in multiple formats."""
        generated_files = []
        
        try:
            # Generate Confluence format
            confluence_file = render_release_notes(prs, params, output_dir, config)
            if confluence_file and confluence_file.exists():
                generated_files.append(str(confluence_file))
                self.logger.info(f"✅ Confluence release notes: {confluence_file.name}")
            
            # Generate Markdown format
            markdown_file = render_release_notes_markdown(prs, params, output_dir, config)
            if markdown_file and markdown_file.exists():
                generated_files.append(str(markdown_file))
                self.logger.info(f"✅ Markdown release notes: {markdown_file.name}")
                
        except Exception as e:
            self.logger.error(f"Failed to generate release notes: {e}")
            raise
            
        return generated_files
    
    def _generate_crq_documents(self, prs: List, params: Dict[str, Any], output_dir: Path, config) -> List[str]:
        """Generate CRQ documents for Day 1 and Day 2."""
        generated_files = []
        
        try:
            crq_files = generate_crqs(prs, params, output_dir, config)
            
            for crq_file in crq_files:
                if crq_file.exists():
                    generated_files.append(str(crq_file))
                    self.logger.info(f"✅ CRQ document: {crq_file.name}")
                    
        except Exception as e:
            self.logger.error(f"Failed to generate CRQ documents: {e}")
            raise
            
        return generated_files
    
    def _validate_outputs(self, file_paths: List[str]) -> Dict[str, Any]:
        """Validate that all generated files exist and have content."""
        validation_results = {
            "all_valid": True,
            "valid_files": [],
            "invalid_files": [],
            "errors": []
        }
        
        for file_path in file_paths:
            file_obj = Path(file_path)
            
            if not file_obj.exists():
                validation_results["all_valid"] = False
                validation_results["invalid_files"].append(file_path)
                validation_results["errors"].append(f"File does not exist: {file_path}")
                continue
                
            if file_obj.stat().st_size == 0:
                validation_results["all_valid"] = False
                validation_results["invalid_files"].append(file_path)
                validation_results["errors"].append(f"File is empty: {file_path}")
                continue
                
            # Check for minimum expected content
            try:
                content = file_obj.read_text()
                
                # Basic content validation
                if len(content) < 100:  # Very basic check
                    validation_results["all_valid"] = False
                    validation_results["invalid_files"].append(file_path)
                    validation_results["errors"].append(f"File content too short: {file_path}")
                    continue
                    
                validation_results["valid_files"].append(file_path)
                self.logger.info(f"✅ Valid: {file_obj.name} ({file_obj.stat().st_size:,} bytes)")
                
            except Exception as e:
                validation_results["all_valid"] = False
                validation_results["invalid_files"].append(file_path)
                validation_results["errors"].append(f"Error reading file {file_path}: {e}")
                
        return validation_results
    
    def _generate_summary(self, results: Dict[str, Any], prs: List, params: Dict[str, Any]):
        """Generate and display test summary."""
        self.logger.info("\n" + "=" * 70)
        self.logger.info("📊 INTEGRATION TEST SUMMARY")
        self.logger.info("=" * 70)
        
        # Test Results
        status = "✅ PASSED" if results["success"] else "❌ FAILED"
        self.logger.info(f"Status: {status}")
        self.logger.info(f"Repository: {results['repo']}")
        self.logger.info(f"Version Range: {results['old_tag']} → {results['new_tag']}")
        self.logger.info(f"PRs Processed: {results['prs_fetched']}")
        self.logger.info(f"Files Generated: {len(results['files_generated'])}")
        
        # PR Categorization
        if prs:
            categories = self._categorize_prs(prs)
            self.logger.info(f"\n📋 PR Breakdown:")
            for category, count in categories.items():
                self.logger.info(f"  - {category}: {count}")
        
        # Generated Files
        if results["files_generated"]:
            self.logger.info(f"\n📁 Generated Files:")
            total_size = 0
            for file_path in results["files_generated"]:
                file_obj = Path(file_path)
                if file_obj.exists():
                    size = file_obj.stat().st_size
                    total_size += size
                    self.logger.info(f"  📄 {file_obj.name}: {size:,} bytes")
            
            self.logger.info(f"\n💾 Total Output: {total_size:,} bytes")
            self.logger.info(f"📂 Location: {results['output_directory']}")
        
        # Errors
        if results["errors"]:
            self.logger.info(f"\n❌ Errors ({len(results['errors'])}):")
            for error in results["errors"]:
                self.logger.info(f"  - {error}")
        
        # Release Information
        self.logger.info(f"\n🚀 Release Information:")
        self.logger.info(f"  Service: {params['service_name']}")
        self.logger.info(f"  Day 1 Date: {params['day1_date']}")
        self.logger.info(f"  Day 2 Date: {params['day2_date']}")
        self.logger.info(f"  RC Name: {params['rc_name']}")
        self.logger.info(f"  RC Manager: {params['rc_manager']}")
        
        self.logger.info("=" * 70)
    
    def _categorize_prs(self, prs: List) -> Dict[str, int]:
        """Categorize PRs by labels."""
        categories = {
            "Features": 0,
            "Bug Fixes": 0,
            "Schema Changes": 0,
            "Infrastructure": 0,
            "Documentation": 0,
            "Other": 0
        }
        
        for pr in prs:
            labels = [label.name.lower() for label in pr.labels] if pr.labels else []
            
            categorized = False
            
            # Check for feature labels
            if any(label in labels for label in ['feature', 'enhancement', 'new']):
                categories["Features"] += 1
                categorized = True
            
            # Check for bug labels
            elif any(label in labels for label in ['bug', 'fix', 'bugfix', 'hotfix']):
                categories["Bug Fixes"] += 1
                categorized = True
            
            # Check for schema labels
            elif any(label in labels for label in ['schema', 'database', 'migration']):
                categories["Schema Changes"] += 1
                categorized = True
            
            # Check for infrastructure labels
            elif any(label in labels for label in ['infrastructure', 'devops', 'ci', 'deployment']):
                categories["Infrastructure"] += 1
                categorized = True
            
            # Check for documentation labels
            elif any(label in labels for label in ['documentation', 'docs']):
                categories["Documentation"] += 1
                categorized = True
            
            # If not categorized, put in "Other"
            if not categorized:
                categories["Other"] += 1
        
        return categories


def main():
    """Main entry point for the integration test."""
    parser = argparse.ArgumentParser(
        description="Real GitHub Workflow Integration Test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Test with specific repository and tags
    python test_real_github_workflow.py --repo ArnoldoM23/PerfCopilot --old-tag v0.0.1 --new-tag v0.4.7
    
    # Test with custom service name and release team
    python test_real_github_workflow.py --repo owner/repo --old-tag v1.0.0 --new-tag v1.1.0 \\
        --service-name my-service --rc-name "John Doe" --rc-manager "Jane Smith"
    
    # Run with default test setup
    python test_real_github_workflow.py --test-all
        """
    )
    
    parser.add_argument("--repo", default="ArnoldoM23/PerfCopilot", 
                       help="GitHub repository (owner/repo)")
    parser.add_argument("--old-tag", default="v0.0.1", 
                       help="Starting tag/version")
    parser.add_argument("--new-tag", default="v0.4.7", 
                       help="Ending tag/version")
    parser.add_argument("--service-name", 
                       help="Service name (defaults to repo name)")
    parser.add_argument("--rc-name", default="Integration Test RC", 
                       help="Release Coordinator name")
    parser.add_argument("--rc-manager", default="Integration Test Manager", 
                       help="Release Manager name")
    parser.add_argument("--test-all", action="store_true", 
                       help="Run with default test parameters")
    parser.add_argument("--github-token", 
                       help="GitHub token (can also use GITHUB_TOKEN env var)")
    
    args = parser.parse_args()
    
    # Get GitHub token
    github_token = (
        args.github_token or 
        os.environ.get("GITHUB_TOKEN")
    )
    
    if not github_token:
        print("❌ Error: GitHub token is required")
        print("Set GITHUB_TOKEN environment variable or use --github-token")
        return 1
    
    # Create tester
    tester = RealGitHubWorkflowTester(github_token)
    
    # Run test
    try:
        results = tester.test_complete_workflow(
            repo=args.repo,
            old_tag=args.old_tag,
            new_tag=args.new_tag,
            service_name=args.service_name,
            rc_name=args.rc_name,
            rc_manager=args.rc_manager
        )
        
        # Exit with appropriate code
        return 0 if results["success"] else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 