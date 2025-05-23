# 🚀 RC Release Automation Agent

**Enterprise-Grade Release Documentation & CRQ Generation**  
*Reduce Release Captain workload by 90% with AI-powered automation*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Enterprise Ready](https://img.shields.io/badge/enterprise-ready-success.svg)](#core-features)
[![Slack Integration](https://img.shields.io/badge/slack-workflow%20ready-purple.svg)](#slack-bot-integration)

---

## 🎯 **Transform Your Release Process in < 30 Seconds**

Stop spending **hours** manually creating release documentation. Our **Release Automation Agent** generates enterprise-ready Confluence pages and CRQ documents automatically from your GitHub PRs.

**Before:** 2-4 hours of manual documentation per release  
**After:** 30-second Slack command → Complete professional documentation ✨

### **🚀 Live Demo: `/run-release` Command**

```
1. Type: /run-release in Slack
2. Fill 8-field form (30 seconds)
3. Get enterprise documentation automatically
```

**Generated Output:**
- 📄 **6,000+ byte** Confluence-ready release notes
- 📋 **Day 1 & Day 2** CRQ documents with AI insights
- 📊 **Professional formatting** with sign-off tracking
- 🔗 **Copy-paste ready** for immediate use

---

## ⚡ **Quick Start - Get Running in 10 Minutes**

### **🎯 Prerequisites**
- Python 3.10+ installed
- GitHub account with repository access
- Slack workspace (for integration)
- Optional: OpenAI API key for enhanced AI features

### **📋 Instant Setup**

```bash
# 1. Clone and install
git clone https://github.com/ArnoldoM23/automated-release-rc.git
cd automated-release-rc
pip install -r requirements.txt

# 2. Test without any tokens (uses mock data)
python main.py --test-mode --service-name demo --prod-version v1.0.0 --new-version v1.1.0

# 3. Setup your configuration (see detailed setup below)
cp config/settings.example.yaml config/settings.yaml
# Edit config/settings.yaml with your details
```

### **🔗 Detailed Setup Guides**

| Setup Guide | Time | Purpose |
|-------------|------|---------|
| [**GitHub Authentication**](#github-authentication-setup) | 3 min | Connect to your repositories |
| [**Configuration Setup**](#configuration-setup) | 5 min | Basic YAML configuration |
| [**Slack Bot Integration**](#slack-bot-integration) | 10 min | Full workflow automation |
| [**Custom CRQ Templates**](#creating-custom-crq-templates) | 5 min | Use your organization's templates |

**🚀 Ready to run?** Jump to [Local Development Setup](#local-development-setup) for detailed instructions.

---

## 🏢 **Core Features**

### **📋 Creating Custom CRQ Templates**

The system supports **external CRQ templates** from various sources. Here's how to create templates that work seamlessly with our tool:

#### **🎯 Template Structure**

Your CRQ template should follow this structure for best results:

```text
**CHANGE REQUEST - DAY {day_number}**

**Summary:** {service_name} Application Code deployment for {platform} ({regions}) - Day {day_number}

**Service Information:**
- Application Name: {service_name}
- Namespace: {namespace}
- Platform: {platform}
- Regions: {regions}

**Version Information:**
- Current Version: {prod_version}
- New Version: {new_version}
- Rollback Version: {prod_version}

**Release Details:**
- Release Type: {release_type}
- Release Coordinator: {rc_name}
- Release Manager: {rc_manager}
- Day 1 Date: {day1_date}
- Day 2 Date: {day2_date}

**Description Section:**
1. What is the business reason for this change?
2. What is the technical summary?
3. What testing has been performed?
4. What is the risk assessment?

**Implementation Plan:**
{implementation_plan}

**Validation Plan:**
- P0 Dashboard: {p0_dashboard_url}
- L1 Dashboard: {l1_dashboard_url}
- Services Dashboard: {services_dashboard_url}

**Backout Plan:**
{backout_plan}
```

#### **📝 Supported Template Formats**

| Format | Configuration | Use Case |
|--------|---------------|----------|
| **Word (.docx)** | `template_type: "word"` | Corporate templates |
| **Text (.txt)** | `template_type: "text"` | Simple text templates |
| **Markdown (.md)** | `template_type: "markdown"` | GitHub-friendly templates |

```yaml
# config/settings.yaml
external_template:
  enabled: true
  template_url: "https://sharepoint.company.com/sites/IT/CRQ_Template.docx"
  template_type: "word"
```

#### **🔧 Variable Placeholders**

The tool automatically converts these placeholders:

| Placeholder | Converts To | Description |
|-------------|-------------|-------------|
| `{service_name}` | `{{ service_name }}` | Service being deployed |
| `{new_version}` | `{{ new_version }}` | Target version |
| `{prod_version}` | `{{ prod_version }}` | Current production version |
| `{platform}` | `{{ platform }}` | Deployment platform |
| `{regions}` | `{{ regions \| join(", ") }}` | Deployment regions |
| `{day_number}` | `{{ day_number }}` | Day 1 or Day 2 |
| `{rc_name}` | `{{ rc_name }}` | Release coordinator name |

### **🤖 Slack Bot Integration**

Transform your release process with intelligent Slack automation.

#### **Option 1: Slack Workflow Builder (Recommended)**

**✅ Pros:** No approvals needed, 5-minute setup, zero infrastructure  
**❌ Cons:** Limited to basic notifications

1. **Setup Slack Workflow:**
   - Open Slack → Tools → Workflow Builder
   - Create new workflow → "Shortcut" trigger
   - Add webhook step pointing to your GitHub Actions

2. **Configure GitHub Actions:**
   ```yaml
   # .github/workflows/run_release.yml
   name: Release Automation
   on:
     repository_dispatch:
       types: [slack_release_request]
   ```

#### **Option 2: Full Slack Bot Integration**

**✅ Pros:** Interactive approvals, real-time updates, enterprise features  
**❌ Cons:** Requires app approval, hosting needed

1. **Deploy Bot:**
   ```bash
   # Deploy to Railway/Heroku
   cd slack_bot
   railway up  # or git push heroku main
   ```

2. **Create Slack App:**
   - Visit api.slack.com/apps
   - Create new app → Enable Socket Mode
   - Add bot scopes: chat:write, commands

### **📊 Dashboard URL Configuration**

Configure your monitoring dashboard URLs directly:

```yaml
# config/settings.yaml
dashboard:
  confluence_dashboard_url: "https://confluence.yourcompany.com/display/YOUR_SERVICE/Dashboards"
  p0_dashboard_url: "https://grafana.yourcompany.com/d/your-service-p0-dashboard"
  l1_dashboard_url: "https://grafana.yourcompany.com/d/your-service-l1-dashboard"
  services_dashboard_url: "https://grafana.yourcompany.com/d/your-service-overview"
```

### **📁 Generated Output Files**

When you run the automation, you get these professional documents:

| File | Size | Purpose | Format |
|------|------|---------|---------|
| `release_notes.txt` | 6,000+ bytes | **Confluence-ready** release notes with 15 sections | Confluence markup |
| `crq_day1.txt` | 4,500+ bytes | **Day 1 preparation** CRQ with detailed steps | Plain text |
| `crq_day2.txt` | 4,600+ bytes | **Day 2 deployment** CRQ with rollback plans | Plain text |
| `release_notes.md` | 2,500+ bytes | **GitHub markdown** version for repositories | Markdown |

---

## 🔧 **Local Development Setup**

### **🔑 Configuration Setup**

```bash
# Copy example configuration
cp config/settings.example.yaml config/settings.yaml

# Edit with your details
nano config/settings.yaml  # or your preferred editor
```

**Essential configuration (minimum required):**

```yaml
# config/settings.yaml
github:
  token: "${GITHUB_TOKEN}"  # Set via environment variable
  repo: "your-org/your-repo"

ai:
  provider: "openai"  # or "azure" or "anthropic"
  openai:
    api_key: "${OPENAI_API_KEY}"  # Optional but recommended

organization:
  name: "Your Company"
  default_service: "your-service"
  regions: ["EUS", "SCUS", "WUS"]  # Your deployment regions

slack:
  bot_token: "${SLACK_BOT_TOKEN}"  # Only if using Slack integration
  signing_secret: "${SLACK_SIGNING_SECRET}"
```

### **🔑 Environment Variables**

Create a `.env` file or set environment variables:

```bash
# .env file (create in project root)
GITHUB_TOKEN=ghp_your_github_token_here
OPENAI_API_KEY=sk-your_openai_key_here
SLACK_BOT_TOKEN=xoxb-your_slack_token_here
SLACK_SIGNING_SECRET=your_slack_signing_secret
```

### **🐙 GitHub Authentication Setup**

The system requires a GitHub Personal Access Token to fetch PR data between releases.

#### **Creating a GitHub Token:**

1. **Go to GitHub Settings:**
   - Visit https://github.com/settings/tokens
   - Click "Generate new token (classic)"

2. **Configure Token:**
   - **Note:** `RC Release Automation` (or similar)
   - **Expiration:** Set based on your security policy
   - **Scopes:** Select appropriate permissions:
     - For **public repositories:** `public_repo`
     - For **private repositories:** `repo` (full repo access)

3. **Copy and Store Token:**
   ```bash
   # Set as environment variable
   export GITHUB_TOKEN="ghp_your-actual-token-here"
   
   # Or add to .env file
   echo "GITHUB_TOKEN=ghp_your-actual-token-here" >> .env
   ```

#### **📋 Supported Version References:**

The system supports both **Git tags** and **commit SHAs** as version references:

| Reference Type | Format | Examples | Use Case |
|----------------|--------|----------|----------|
| **Git Tags** | `v1.2.3` or `1.2.3` | `v2.4.0`, `1.0.0`, `release-2024-01` | Standard releases with semantic versioning |
| **Commit SHAs** | 7-40 hex characters | `abc123f`, `9f8e7d6c5b4a`, `f45b2a1fc2bcf208` | Hot fixes, custom builds, no-tag workflows |

**Examples:**

```bash
# Using Git tags (recommended for releases)
python main.py --prod-version v1.4.2 --new-version v1.5.0

# Using commit SHAs (useful for hotfixes or pre-release testing)  
python main.py --prod-version abc123f --new-version def456a

# Mixed approach (tag to commit)
python main.py --prod-version v1.4.2 --new-version 9f8e7d6c
```

**✅ Advantages of Commit SHA Support:**
- **No tags required** - works with any repository
- **Precise control** - target exact commits for hotfixes  
- **Flexible workflows** - supports non-standard release processes
- **Backward compatible** - existing tag-based workflows still work

#### **GitHub Enterprise Support:**

If using GitHub Enterprise, update your configuration:

```yaml
# config/settings.yaml
github:
  token: "${GITHUB_TOKEN}"
  repo: "your-org/your-repo"
  api_url: "https://your-enterprise.github.com/api/v3"  # Enterprise API URL
```

### **🚀 Running Locally**

#### **Option 1: CLI-Only Usage**

Perfect for CI/CD integration or manual releases:

```bash
# Manual release generation
python main.py \
  --service-name cer-cart \
  --prod-version v2.4.3 \
  --new-version v2.5.0 \
  --rc-name "Alice Johnson" \
  --rc-manager "Bob Smith" \
  --day1-date "2024-01-15" \
  --day2-date "2024-01-16"

# Test with real GitHub data
export GITHUB_TOKEN="your_token"
python main.py --service-name your-service --prod-version v1.0.0 --new-version v1.1.0

# Integrate into CI/CD
./scripts/generate_release_docs.sh $SERVICE_NAME $NEW_VERSION
```

#### **Option 2: With Mock Data**

```bash
# Test with 25 mock PRs (5 schema + 10 features + 5 bugfixes + 5 i18n)
python main.py --test-mode \
  --service-name test-service \
  --prod-version v1.0.0 \
  --new-version v1.1.0 \
  --rc-name "Test User" \
  --rc-manager "Test Manager"
```

---

## 🧪 **Testing & Validation**

### **🔍 Test Your Configuration**

```bash
# Run all tests with the new test runner
python run_tests.py

# Test specific components
python run_tests.py --github          # GitHub integration tests
python run_tests.py --slack           # Slack integration tests  
python run_tests.py --cli             # CLI and core functionality
python run_tests.py --unit            # Unit tests only
python run_tests.py --integration     # Integration tests only
python run_tests.py --external        # External template tests
```

### **📊 GitHub Integration Testing**

```bash
# Test GitHub authentication and PR fetching  
python run_tests.py --github

# Test with your repository (interactive)
python tests/test_github/test_github_integration.py --test-all

# Test with specific repository and tags
python tests/test_github/test_github_integration.py \
  --repo your-org/your-repo \
  --old-tag v1.0.0 \
  --new-tag v1.1.0

# Test with commit SHAs (when tags aren't available)
python tests/test_github/test_github_integration.py \
  --repo your-org/your-repo \
  --old-tag abc123f \
  --new-tag def456a

# Mix tags and commit SHAs
python tests/test_github/test_github_integration.py \
  --repo your-org/your-repo \
  --old-tag v1.0.0 \
  --new-tag 9f8e7d6c

# List available tags in your repository
python tests/test_github/test_github_integration.py \
  --list-tags \
  --repo your-org/your-repo
```

### **🎯 Real Workflow Testing**

```bash
# Test the complete workflow with commit SHAs
python tests/test_real_github_workflow.py \
  --repo ArnoldoM23/PerfCopilot \
  --old-tag abc123f \
  --new-tag def456a

# Test with your repository and custom parameters
python tests/test_real_github_workflow.py \
  --repo owner/repo \
  --old-tag v1.0.0 \
  --new-tag v1.1.0 \
  --service-name my-service \
  --rc-name "John Doe" \
  --rc-manager "Jane Smith"

# Run with default test setup
python tests/test_real_github_workflow.py --test-all
```

### **📊 Mock Data Testing**

The system includes comprehensive mock data for testing:

**Mock PRs include:**
- Schema changes (database migrations)
- Feature additions (new functionality)  
- Bug fixes (critical and non-critical)
- International/localization updates
- Various label combinations for testing categorization

### **🔧 Individual Test Files**

For advanced testing:

```bash
python tests/test_cli.py --test-config      # Configuration validation
python tests/test_cli.py --test-ai          # AI provider connectivity  
python tests/test_cli.py --test-github      # GitHub API integration
python tests/test_cli.py --test-templates   # Template processing

# Test configuration loading
python -c "from config.config import load_config; print('✅ Config loaded successfully')"

# Test external template validation
python tests/test_external_template.py
```

### **❓ Troubleshooting**

#### **GitHub Issues:**

**❌ Authentication failed:**
- Verify token format starts with `ghp_` or `github_pat_`
- Check token hasn't expired
- Ensure token has correct repository permissions

**❌ Repository access denied:**
- Verify repository name format: `owner/repo`
- Check if repository is private and token has `repo` scope
- Confirm you have access to the repository

**❌ No PRs found:**
- Ensure tags exist: `git tag -l`
- Check commit messages contain PR references (`#123`, `PR #123`)
- Verify PRs were actually merged (not just closed)

#### **Template Validation:**

```bash
# Test external template download
python tests/test_external_template.py

# Validate template conversion
python -c "
from crq.external_template import ExternalTemplateManager
from config.config import load_config
manager = ExternalTemplateManager(load_config())
result = manager.get_external_template()
print('✅ Template loaded successfully' if result else '❌ Template failed')
"
```