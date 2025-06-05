# run_release_agent.py

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from .rc_agent_build_release import get_release_inputs

# Import the main workflow functions
from src.github_integration.fetch_prs import fetch_prs
from src.release_notes.release_notes import render_release_notes, render_release_notes_markdown
from src.crq.generate_crqs import generate_crqs
from src.config.config import load_config, GitHubConfig, Settings, SlackConfig, OrganizationConfig, AIConfig
from src.utils.logging import get_logger

def write_config_file(config_data, output_folder="output/"):
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "rc_config.json")

    with open(output_path, "w") as f:
        json.dump(config_data, f, indent=4)
    print(f"📝 Saved config to: {output_path}")
    return output_path

def generate_pr_authors_json(prs, output_dir):
    """Generate PR authors JSON file for tracking"""
    authors_data = {
        "generation_timestamp": datetime.now().isoformat(),
        "total_prs": len(prs),
        "authors": {}
    }
    
    for pr in prs:
        author = pr.user.login
        if author not in authors_data["authors"]:
            authors_data["authors"][author] = {
                "name": author,
                "prs": [],
                "total_prs": 0
            }
        
        authors_data["authors"][author]["prs"].append({
            "number": pr.number,
            "title": pr.title,
            "url": pr.html_url,
            "merged_at": pr.merged_at.isoformat() if hasattr(pr, 'merged_at') and pr.merged_at else None
        })
        authors_data["authors"][author]["total_prs"] += 1
    
    # Save authors JSON
    authors_file = output_dir / "pr_authors.json"
    with open(authors_file, "w", encoding="utf-8") as f:
        json.dump(authors_data, f, indent=2)
    
    print(f"📋 Generated PR authors: {authors_file}")
    return authors_file

def run_local_document_generation(config_data):
    """Run the complete local document generation workflow"""
    logger = get_logger(__name__)
    
    print("\n🔄 Starting local document generation...")
    
    try:
        # Load configuration with fallback for missing Slack tokens
        try:
            config = load_config()
        except Exception as config_error:
            logger.warning(f"Failed to load full configuration: {config_error}")
            print("⚠️  Warning: Slack configuration not available - proceeding with GitHub-only mode")
            
            # Create minimal fallback config for GitHub operations
            config = Settings(
                github=GitHubConfig(
                    token=os.getenv("GITHUB_TOKEN", ""),
                    repo=os.getenv("GITHUB_REPO", "ArnoldoM23/PerfCopilot"),
                    api_url="https://api.github.com"
                ),
                slack=SlackConfig(
                    bot_token="xoxb-fallback-token",  # Dummy token to satisfy validation
                    signing_secret="fallback-secret",
                    app_token="xapp-fallback-token"
                ),
                organization=OrganizationConfig(
                    name="Default",
                    regions=["EUS", "SCUS", "WUS"]
                ),
                ai=AIConfig(
                    openai={"api_key": "fallback-key"},
                    anthropic={"api_key": "fallback-key"},
                    azure_openai={"api_key": "fallback-key", "endpoint": "https://fallback.openai.azure.com"}
                )
            )
            
        # Create output directory with release date instead of current timestamp
        # Use Day 1 date as the primary reference since that's when prep starts
        from datetime import datetime as dt
        try:
            release_date = dt.strptime(config_data["day1_date"], "%Y-%m-%d")
            date_str = release_date.strftime("%Y%m%d")
        except (ValueError, KeyError):
            # Fallback to current date if parsing fails
            date_str = datetime.now().strftime("%Y%m%d")
        
        # Add current time for uniqueness (in case multiple runs on same day)
        time_str = datetime.now().strftime("%H%M%S")
        
        service_name = config_data["service_name"].replace("-", "_")
        output_dir = Path(config_data["output_folder"]) / f"{service_name}_{config_data['new_version']}_{date_str}_{time_str}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Output directory: {output_dir}")
        
        # Step 1: Fetch PRs from GitHub
        print("📥 Step 1: Fetching PRs from GitHub...")
        
        # Debug: Check GitHub token
        github_token = os.getenv("GITHUB_TOKEN", "")
        print(f"🔍 Debug: GitHub token available: {'Yes' if github_token else 'No'}")
        if github_token:
            print(f"🔍 Debug: Token starts with: {github_token[:10]}...")
        
        # Use the GitHub config from the loaded configuration
        prs = fetch_prs(
            prod_ref=config_data["production_version"],
            new_ref=config_data["new_version"],
            config=config.github
        )
        
        print(f"✅ Fetched {len(prs)} PRs")
        
        # Step 2: Generate PR authors JSON
        print("📋 Step 2: Generating PR authors...")
        generate_pr_authors_json(prs, output_dir)
        
        # Step 3: Prepare release parameters
        print("⚙️ Step 3: Preparing release parameters...")
        release_params = {
            "service_name": config_data["service_name"],
            "new_version": config_data["new_version"],
            "prod_version": config_data["production_version"],
            "release_type": config_data["release_type"],
            "rc_name": config_data["rc"],
            "rc_manager": config_data["rc_manager"],
            "day1_date": config_data["day1_date"],
            "day2_date": config_data["day2_date"]
        }
        
        # Step 4: Generate release notes
        print("📝 Step 4: Generating release notes...")
        release_notes_file = render_release_notes(prs, release_params, output_dir, config)
        release_notes_md_file = render_release_notes_markdown(prs, release_params, output_dir, config)
        print(f"✅ Release notes: {release_notes_file.name}")
        print(f"✅ Release notes (MD): {release_notes_md_file.name}")
        
        # Step 5: Generate CRQ documents
        print("📋 Step 5: Generating CRQ documents...")
        crq_files = generate_crqs(prs, release_params, output_dir, config)
        for crq_file in crq_files:
            print(f"✅ CRQ document: {crq_file.name}")
        
        # Step 6: Validate all files
        print("✅ Step 6: Validating generated files...")
        all_files = [release_notes_file, release_notes_md_file] + crq_files + [output_dir / "pr_authors.json"]
        
        total_size = 0
        for file_path in all_files:
            if file_path.exists():
                file_size = file_path.stat().st_size
                total_size += file_size
                print(f"✅ Valid: {file_path.name} ({file_size:,} bytes)")
            else:
                print(f"❌ Missing: {file_path.name}")
        
        print(f"\n📊 Summary:")
        print(f"   📁 Output directory: {output_dir}")
        print(f"   📄 Files generated: {len(all_files)}")
        print(f"   💾 Total size: {total_size:,} bytes")
        print(f"   🚀 Ready for release: {config_data['service_name']} {config_data['new_version']}")
        
        return output_dir
        
    except Exception as e:
        print(f"❌ Document generation failed: {e}")
        logger.error(f"Local document generation failed: {e}")
        raise

def trigger_github_workflow(config_data):
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN environment variable not set.")
        sys.exit(1)

    repo = "ArnoldoM23/automated-release-rc"
    api_url = f"https://api.github.com/repos/{repo}/dispatches"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    payload = {
        "event_type": "run-release",
        "client_payload": {
            "prod_version": config_data["production_version"],
            "new_version": config_data["new_version"],
            "service_name": config_data["service_name"],
            "release_type": config_data["release_type"],
            "rc_name": config_data["rc"],
            "rc_manager": config_data["rc_manager"],
            "day1_date": config_data["day1_date"],
            "day2_date": config_data["day2_date"],
            "slack_channel": "#engineering-release",  # Optional
            "slack_user": config_data["rc_manager"]
        }
    }

    print("\n🚀 Triggering GitHub workflow...")
    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code == 204:
        print("✅ GitHub workflow triggered successfully.")
    else:
        print(f"❌ Failed to trigger GitHub workflow: {response.status_code}")
        print(response.text)
        sys.exit(1)

def main():
    print("🎛️ RC Release Automation CLI")
    print("=============================\n")

    try:
        # Step 1: Collect inputs
        inputs = get_release_inputs()
        
        # Step 2: Save configuration
        config_path = write_config_file(inputs, inputs["output_folder"])
        
        # Step 3: Run local document generation
        output_dir = run_local_document_generation(inputs)
        
        # Step 4: Trigger GitHub workflow
        trigger_github_workflow(inputs)
        
        print(f"\n🎉 Release automation completed successfully!")
        print(f"📁 Check your documents in: {output_dir}")

    except KeyboardInterrupt:
        sys.exit("\n❌ Aborted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 