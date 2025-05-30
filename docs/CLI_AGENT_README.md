# RC Release Agent CLI - Complete Automation Workflow

**Interactive CLI → Document Generation → Automated Slack Sign-off Collection**

This system transforms release coordination from manual document creation and sign-off tracking into a fully automated workflow that runs from a single interactive command.

## 🎯 Overview

The RC Release Agent CLI provides:

1. **Interactive Configuration Collection** - User-friendly prompts for all release details
2. **Automated Document Generation** - CRQ and Confluence documents via GitHub Actions
3. **Intelligent Slack Automation** - Scheduled reminders and escalation management
4. **Zero-Modal Enterprise Compliance** - Works within Walmart's UI restrictions

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GITHUB_TOKEN="ghp_your_token_here"
export SLACK_BOT_TOKEN="xoxb-your-slack-token"
```

### Basic Usage

```bash
# Option 1: Install package and use entry point (recommended)
pip install -e .
rc-release-agent

# Option 2: Direct module execution
python -m src.cli.run_release_agent

# Demo workflow with example data
python demo_cli_workflow.py
```

The CLI will:
1. ✅ Collect all release information via interactive prompts
2. ✅ Save configuration to `output/rc_config.json`
3. ✅ Trigger GitHub Actions workflow for document generation
4. ✅ Create Slack configuration for automated sign-off collection

## 📋 Complete Workflow

### Step 1: Interactive Configuration

```bash
# Recommended: Use entry point after installing
pip install -e .
rc-release-agent

# Alternative: Direct module execution
python -m src.cli.run_release_agent
```

**Example Interaction:**
```
👋 Welcome to the RC Release Agent!
🛠  Let's gather details for this release.

Who is the RC? munoz
Who is the RC Manager? Charlie
Production version (e.g. v2.3.1): v2.3.1
New version (e.g. v2.4.0): v2.4.0
Service name (e.g. cer-cart): cer-cart
Release type: standard
Day 1 Date (YYYY-MM-DD): 2025-05-29
Day 2 Date (YYYY-MM-DD): 2025-05-30
Slack cutoff time (UTC ISO format): 2025-05-29T23:00:00Z
Output folder: output/
```

### Step 2: GitHub Actions Integration

The CLI triggers a GitHub repository dispatch event that:

- Fetches PR metadata between versions
- Generates enterprise Confluence release notes
- Creates CRQ documents (Day 1 & Day 2)
- Extracts PR author list for Slack notifications

**GitHub Workflow Payload:**
```json
{
  "event_type": "run-release",
  "client_payload": {
    "prod_version": "v2.3.1",
    "new_version": "v2.4.0",
    "service_name": "cer-cart",
    "release_type": "standard",
    "rc_name": "munoz",
    "rc_manager": "Charlie",
    "day1_date": "2025-05-29",
    "day2_date": "2025-05-30",
    "slack_channel": "#engineering-release",
    "slack_user": "Charlie"
  }
}
```

### Step 3: Automated Slack Sign-off Collection

Once documents are generated, start the automated Slack workflow:

```bash
# The GitHub Action will create a slack_config.json file
python signoff_bot.py --config output/slack_config.json
```

**Automated Message Schedule:**
1. **Initial Message** - Sent immediately with sign-off request
2. **Reminder 1** - 4 hours before cutoff
3. **Final Reminder** - 1 hour before cutoff  
4. **Escalation** - At cutoff time (success or escalation)

## 📁 File Structure

```
output/
├── rc_config.json              # CLI configuration
├── slack_config.json           # Slack automation config
├── authors.json                # PR authors list
├── release_notes.txt           # Confluence format
├── crq_day1.txt               # Day 1 CRQ document
└── crq_day2.txt               # Day 2 CRQ document
```

## 🔧 Configuration Files

### RC Configuration (`rc_config.json`)
```json
{
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
  "timestamp": "2025-05-28T111102Z"
}
```

### Slack Configuration (`slack_config.json`)
```json
{
  "channel": "#releases",
  "rc": "@munoz",
  "rc_manager": "@Charlie",
  "cutoff_time_utc": "2025-05-29T23:00:00Z",
  "reminder_intervals": [4, 1],
  "authors": ["@alice", "@bob", "@carol"],
  "day1_date": "2025-05-29",
  "day2_date": "2025-05-30",
  "service_name": "cer-cart",
  "production_version": "v2.3.1",
  "new_version": "v2.4.0"
}
```

## 💬 Slack Message Examples

### Initial Sign-off Request
```
🚀 **Release Sign-off Required**

Hi team! We've locked the release for:
• **Day 1**: 2025-05-29
• **Day 2**: 2025-05-30

**Service**: cer-cart (v2.3.1 → v2.4.0)

📋 **Please sign off on your PRs by**: `2025-05-29T23:00:00Z`

**PR Authors requiring sign-off**:
• @alice
• @bob
• @carol

Thank you for your prompt response!
**RC**: @munoz
```

### Reminder Message
```
⏰ **Reminder**

Release sign-off deadline in **4 hours**: `2025-05-29T23:00:00Z`

If you don't sign off by the deadline, your changes may need to be removed from this release.

**Pending sign-offs**:
• @alice
• @bob

**RC**: @munoz
```

### Final Escalation
```
⚠️ **Sign-off Deadline Reached - Escalation Required**

The following PR authors have NOT signed off by the deadline `2025-05-29T23:00:00Z`:

• @alice

@munoz @Charlie, please follow up immediately or consider removing these changes before CRQ submission.

**Next Steps**:
1. Contact authors directly for immediate sign-off
2. OR remove unsigned changes from release
3. Proceed with CRQ once resolved
```

## 🧪 Testing & Dry Runs

### Test CLI Input Collection
```bash
python rc_agent_build_release.py
```

### Test Slack Workflow (Dry Run)
```bash
python release_signoff_notifier.py --config output/slack_config.json --dry-run --simple
```

### Demo Complete Workflow
```bash
python demo_cli_workflow.py
```

## 🔐 Security & Environment Setup

### Required Environment Variables
```bash
# GitHub Personal Access Token (repo scope)
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"

# Slack Bot Token (chat:write scope)
export SLACK_BOT_TOKEN="xoxb-xxxxxxxxxxxxxxxxxxxx"

# Optional: Repository override
export GITHUB_REPO="ArnoldoM23/automated-release-rc"
```

### Slack Bot Setup
1. Create Slack app at https://api.slack.com/apps
2. Add `chat:write` OAuth scope
3. Install app to workspace
4. Copy Bot User OAuth Token

### GitHub Token Setup
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate token with `repo` scope
3. Add to environment variables

## 🎛️ Advanced Usage

### Custom Reminder Intervals
Edit `slack_config.json` to customize reminder timing:
```json
{
  "reminder_intervals": [8, 4, 1],  // 8h, 4h, 1h before cutoff
  "cutoff_time_utc": "2025-05-29T23:00:00Z"
}
```

### Multiple Services
Run the CLI multiple times for different services:
```bash
# Service 1
rc-release-agent
# (Configure for cer-cart)

# Service 2  
rc-release-agent
# (Configure for payment-service)
```

### Production Scheduling
For production use, run the Slack notifier as a background service:
```bash
# Start scheduled workflow (runs until cutoff)
nohup python signoff_bot.py --config output/slack_config.json > slack.log 2>&1 &
```

## 🔄 Integration with Existing Systems

### GitHub Actions Workflow
The CLI triggers the `run-release` event. Your `.github/workflows/` should include:

```yaml
name: Release Document Generation
on:
  repository_dispatch:
    types: [run-release]

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate Release Documents
        run: |
          python -m src.cli.run_release_agent \
            --prod-version ${{ github.event.client_payload.prod_version }} \
            --new-version ${{ github.event.client_payload.new_version }} \
            --service-name ${{ github.event.client_payload.service_name }}
```

### Existing Document Generation
The CLI integrates with your existing:
- `src/cli/run_release_agent.py` - Main CLI logic
- `src/templates/` - Jinja2 templates for CRQ and Confluence
- `src/config/settings.yaml` - Application configuration

## 🎯 Benefits

### For Release Coordinators
- **5-minute setup** instead of 30+ minutes of manual work
- **Zero manual follow-up** - automated reminders and escalation
- **Professional messaging** - consistent, enterprise-appropriate communication
- **Audit trail** - all configurations and timings logged

### For Development Teams  
- **Clear expectations** - automated reminders with specific deadlines
- **Reduced interruptions** - no manual RC follow-ups
- **Transparent process** - everyone sees the same timeline

### For Enterprise Compliance
- **No Slack modals** - works within UI restrictions
- **Documented workflow** - all steps logged and traceable
- **Consistent process** - same workflow every release
- **Escalation management** - automatic manager notification

## 🚀 Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Set environment variables** (GitHub and Slack tokens)
3. **Install package**: `pip install -e .`
4. **Run demo**: `python demo_cli_workflow.py`
5. **Test with real data**: `rc-release-agent`
6. **Set up GitHub Actions** workflow for document generation
7. **Configure Slack channels** and permissions

---

**Questions?** Check the demo files in `output/` or run `python demo_cli_workflow.py` for a complete walkthrough. 