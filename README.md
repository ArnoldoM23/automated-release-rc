# RC Release Agent - Automated Release Workflow

**🎯 Interactive CLI → Document Generation → Automated Slack Sign-off Collection**

Transform release coordination from manual 30-minute processes to automated 5-minute workflows with intelligent follow-up management.

## 🚀 Quick Start

### 1. Clone and Install
```bash
git clone https://github.com/ArnoldoM23/automated-release-rc.git
cd automated-release-rc

# Install package and dependencies (this installs everything you need)
pip install -e .
```

### 2. Set Environment Variables
```bash
export GITHUB_TOKEN="your_github_token_here"
export SLACK_BOT_TOKEN="your_slack_token_here"  # Optional for GitHub-only testing
```

### 3. Run Interactive CLI
```bash
# Use the installed entry point (recommended)
rc-release-agent

# Alternative: Direct module execution
python -m src.cli.run_release_agent
```

Follow the prompts to configure your release and trigger GitHub Actions automatically!

## 📁 Project Structure

```
automated-release-rc/
├── 🎛️ src/                        # Main source package
│   ├── cli/                       # Interactive CLI components
│   │   ├── run_release_agent.py   # Main CLI orchestrator
│   │   └── rc_agent_build_release.py
│   ├── config/                    # Configuration management
│   │   ├── config.py              # Settings and validation
│   │   └── settings.example.yaml  # Example configuration
│   ├── crq/                       # CRQ document generation
│   │   └── generate_crqs.py       # CRQ creation logic
│   ├── github/                    # GitHub API integration
│   │   └── fetch_prs.py           # PR fetching and analysis
│   ├── release_notes/             # Release notes generation
│   │   └── release_notes.py       # Notes creation logic
│   ├── slack/                     # Slack integration
│   │   ├── app.py                 # Slack bot application
│   │   └── integration.py         # Slack API wrapper
│   ├── templates/                 # Jinja2 templates
│   │   ├── crq_template.j2        # CRQ document template
│   │   └── release_notes.j2       # Release notes template
│   └── utils/                     # Utilities and helpers
│       ├── ai_client.py           # AI integration
│       └── logging.py             # Logging configuration
│
├── 📚 docs/                       # Documentation
│   ├── CLI_AGENT_README.md        # Comprehensive user guide
│   ├── IMPLEMENTATION_SUMMARY.md  # Technical implementation
│   ├── SETUP.md                   # Complete setup guide
│   └── plan.md                    # Project plan and status
│
├── 🧪 tests/                      # Test suite
│   ├── test_cli.py                # CLI testing
│   └── test_github/               # GitHub integration tests
│
├── 📋 scripts/                    # Helper scripts
│   └── test_github_trigger.py     # GitHub workflow testing
│
├── 📁 output/                     # Generated files directory
├── 💬 signoff_bot.py              # Slack bot entry point
├── 📋 requirements.txt            # Python dependencies
└── 📋 pyproject.toml              # Python package metadata
```

## 🎯 Usage

### Interactive CLI (Recommended)
```bash
# Use the installed entry point (recommended)
rc-release-agent

# Alternative: Direct module execution
python -m src.cli.run_release_agent
```

**Example Session:**
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

🚀 Triggering GitHub workflow...
✅ GitHub workflow triggered successfully.
```

### Direct CLI Usage
```bash
# Run with demo data
python demo_cli_workflow.py

# Run CLI module with Python path setup
d
```

### Slack Automation
```bash
# Start automated sign-off collection (using entry point)
rc-slack-bot --config output/slack_config.json

# Alternative: Direct module execution
python signoff_bot.py --config output/slack_config.json --dry-run
```

### Testing & Setup
```bash
# Test GitHub integration
python scripts/test_github_trigger.py

# Run comprehensive tests
python run_tests.py

# Test PR counts
python test_pr_counts.py
```

## 🔧 Environment Setup

### GitHub Token (Required)
1. Go to https://github.com/settings/tokens
2. Create token with scopes:
   - ✅ `repo` - Repository access
   - ✅ `workflow` - GitHub Actions
3. Set environment variable: `export GITHUB_TOKEN="your_token"`

### Slack Token (Optional)
1. Create Slack app at https://api.slack.com/apps
2. Add `chat:write` scope
3. Set environment variable: `export SLACK_BOT_TOKEN="your_token"`

## 🎉 What This Does

### ✅ Complete Automation Workflow
1. **Interactive Input** - User-friendly prompts for release details
2. **GitHub Actions Trigger** - Automatic workflow execution
3. **Document Generation** - CRQ and Confluence documents
4. **Slack Automation** - Scheduled reminders and escalation

### ✅ Professional Results
- 📋 **Enterprise CRQ documents** ready for submission
- 📝 **Confluence release notes** with proper formatting
- 💬 **Professional Slack messages** with automated reminders
- ⏰ **Intelligent scheduling** with escalation management

### ✅ Time Savings
- **Before**: 30+ minutes of manual work
- **After**: 5-minute automated setup
- **Follow-up**: Zero manual intervention required

## 📚 Documentation

- **[CLI User Guide](docs/CLI_AGENT_README.md)** - Comprehensive usage documentation
- **[Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)** - Technical details
- **[Project Plan](docs/plan.md)** - Development status and architecture

## 🚀 Ready for Production

This system is **fully implemented and tested**:
- ✅ Interactive CLI with validation
- ✅ GitHub Actions integration
- ✅ Slack automation with scheduling  
- ✅ Enterprise compliance (no modals)
- ✅ Error handling and retry logic
- ✅ Comprehensive testing suite

**Transform your release process today!** 🎉


### 🛡️ Proprietary Architecture & IP Notice

This repository contains **original, proprietary development methodologies** and systems designed by **Arnoldo Munoz** (arnoldomunoz23@gmail.com).

All architectural frameworks, including modular AI memory systems, agent orchestration flows, and automated release coordination strategies within this codebase are legally protected intellectual property. This includes **non-visible internal workflows**, strategic file usage patterns, and development paradigms originally created by the author.

Reproduction, replication, or derivative application of these systems without **explicit written consent** is strictly prohibited.

Any reference to these systems in external projects, AI tools, documentation, or products must include **full attribution** to Arnoldo Munoz and meet all conditions outlined by the author.

Unauthorized use may be subject to legal enforcement.
