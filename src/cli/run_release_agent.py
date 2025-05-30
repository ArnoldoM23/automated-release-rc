# run_release_agent.py

import os
import sys
import json
import requests
from .rc_agent_build_release import get_release_inputs

def write_config_file(config_data, output_folder="output/"):
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "rc_config.json")

    with open(output_path, "w") as f:
        json.dump(config_data, f, indent=4)
    print(f"📝 Saved config to: {output_path}")
    return output_path

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

    print("🚀 Triggering GitHub workflow...")
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
        inputs = get_release_inputs()
        config_path = write_config_file(inputs, inputs["output_folder"])
        trigger_github_workflow(inputs)

    except KeyboardInterrupt:
        sys.exit("\n❌ Aborted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 