# RC Release Agent - Automated Release Workflow

**🎯 Interactive CLI → Document Generation → Professional Release Documentation**

Transform release coordination from manual 30-minute processes to automated 5-minute workflows with intelligent PR analysis and enterprise-ready documentation.

## 🚀 Quick Start

### 1. Clone and Install
```bash
git clone https://github.com/ArnoldoM23/automated-release-rc.git
cd automated-release-rc

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. 🔧 RC Agent Setup (v4.0)

**🎯 v4.0 Configuration Hygiene: Secrets in Environment, System Config in YAML**

#### **Step 1: Create Environment Configuration**

Create your environment file in your home directory (secure location):

```bash
# Copy the template to your home directory
cp .rc_env_checkout.sh ~/.rc_env_checkout.sh

# Edit with your actual values
nano ~/.rc_env_checkout.sh  # or vim/code
```

Edit `~/.rc_env_checkout.sh` with your actual values:

```bash
#!/bin/bash
# =============================================================================
# RC Agent v4.0 - Your Environment Configuration
# =============================================================================
# ⚠️  IMPORTANT: Keep this file in your HOME directory only!
# ⚠️  Never commit this file to git - contains sensitive credentials

# GitHub Authentication (Required)
export GITHUB_TOKEN="ghp_your_actual_token_here"
export GITHUB_REPO="YourOrg/YourRepo"

# Service Configuration (Auto-detected if not specified)
export SERVICE_NAME="your-service-name"        # Optional: auto-extracted from repo
export SERVICE_NAMESPACE="your-namespace"
export SERVICE_REGIONS="us-east-1,us-west-2"
export PLATFORM="kubernetes"

# LLM Configuration (Optional - for AI features)
export LLM_PROVIDER="openai"                   # openai, walmart_sandbox
export OPENAI_API_KEY="sk-your-openai-key"     # OpenAI API key
export WMT_LLM_API_KEY="your-wmt-key"          # Walmart LLM key (optional)
export WMT_LLM_API_URL="http://llm-internal.walmart.com:8000"  # Walmart LLM URL

# Slack Configuration (Optional - for notifications)
export SLACK_BOT_TOKEN="xoxb-your-token"
export SLACK_SIGNING_SECRET="your-secret"
export SLACK_CHANNEL="#releases"
```

#### **Step 2: Get Your GitHub Token**

1. **Navigate to GitHub Token Settings:**
   - Go to https://github.com/settings/tokens
   - Or: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token:**
   - Click **"Generate new token (classic)"**
   - **Note/Description:** `RC Release Automation Agent v4.0`
   - **Expiration:** 90 days (recommended) or your preferred duration

3. **Select Required Scopes:**
   - ✅ **`repo`** - Full control of private repositories
   - ✅ **`workflow`** - Update GitHub Action workflows (if using GitHub Actions)

4. **Generate and Copy Token:**
   - Click **"Generate token"**
   - **IMMEDIATELY COPY** the token (format: `ghp_xxxxxxxxxxxx`)
   - Update your `.rc_env_checkout.sh.local` file with the token

#### **Step 3: Load Environment and Run**

**Option A: Manual Method**
```bash
# Load your environment configuration
source ~/.rc_env_checkout.sh

# Run the RC Agent
python -m src.cli.run_release_agent
```

**Option B: Automated Wrapper (Recommended)**
```bash
# Make the wrapper executable
chmod +x run_rc_agent.sh

# Run with automatic environment loading
./run_rc_agent.sh
```

**Option C: Custom Environment File**
```bash
# Use a custom-named environment file
RC_ENV_FILE=~/.my-secrets.sh ./run_rc_agent.sh
```

#### **🎯 v4.0 Benefits:**

- ✅ **Enhanced Security** - No secrets in configuration files, all in environment variables
- ✅ **Multiple Version Formats** - Support for v1.2.3, 1.2.3-abcdef, abc123 (SHA-only)
- ✅ **Enhanced CLI Guidance** - Release type prompts with helpful tips and validation
- ✅ **Automatic Service Detection** - Smart service name extraction from GitHub repo
- ✅ **LLM Performance Improvements** - 10-second timeout prevents hanging (was 75+ seconds)
- ✅ **Professional Configuration** - Clean separation of system config and secrets
- ✅ **Flexible Environment Setup** - Support for custom environment file names and locations

## 🎯 Usage

### Interactive CLI (Primary Workflow)
```bash
# Main CLI command
python -m src.cli.run_release_agent
```

**Example Session (v4.0 Enhanced):**
```
👋 Welcome to the RC Release Agent!
🛠  Let's gather details for this release.

Who is the RC? @ArnoldoM23
Who is the RC Manager? Charlie  
Production version (e.g., v1.2.3, 1.2.3-abcdef, or SHA): v0.4.6
New version (e.g., v1.2.4, 1.2.4-abcdef, or SHA): v0.4.7
💡 Pre-filling service name from GitHub repo: perfcopilot
Service name (e.g. ce-cart): perfcopilot

Select a release type:
  - standard: 🟢 Regular feature or service release (non-urgent)
  - hotfix: 🔴 Urgent bug fix going directly to prod  
  - release: 📦 Formal versioned rollout for larger release cycles
Release type: standard

Day 1 Date (YYYY-MM-DD): 2024-02-23
Day 2 Date (YYYY-MM-DD): 2024-02-24
Slack cutoff time (UTC ISO format): 2024-02-22T23:00:00Z
Output folder: output/

🔍 Analyzing PRs between v0.4.6 → v0.4.7...
✅ Found 21 PRs to process
🤖 Requesting AI summary for 21 PRs... (completed in 5.2s)
📝 Generating release documentation...
✅ Documentation generated in: output/perfcopilot_v0.4.7_20240223_192847/

📁 Generated files (24,884 bytes total):
  - release_notes.txt (6,223 bytes)
  - crq_day1.txt (8,891 bytes) 
  - crq_day2.txt (7,234 bytes)
  - pr_authors.json (1,156 bytes)
  - rc_config.json (1,380 bytes)
```

Follow the prompts to generate professional release documentation!

## 🏗️ How the RC Release Agent Works

```mermaid
graph TB
    %% User Inputs
    subgraph Input["🎯 Input Sources"]
        CLI["👨‍💻 Interactive CLI<br/>rc-release-agent"]
        SLACK["💬 Slack Modal<br/>Future Integration"]
        GITHUB["🐙 GitHub Repository<br/>Tags, Commits, PRs"]
    end

    %% Configuration
    subgraph Config["⚙️ Configuration Layer"]
        SETTINGS["📋 settings.yaml<br/>• GitHub Token<br/>• Repository Info<br/>• LLM Settings<br/>• Templates"]
        ENV["🔐 Environment Variables<br/>GITHUB_TOKEN<br/>WMT_LLM_API_KEY<br/>WMT_LLM_API_URL"]
    end

    %% Core Processing Engine
    subgraph Engine["🧠 Core Processing Engine"]
        FETCH["📥 PR Fetcher<br/>• GitHub API Integration<br/>• Tag/Commit Comparison<br/>• Merge Commit Analysis"]
        ANALYZE["🔍 PR Analyzer<br/>• Label-based Categorization<br/>• Author Extraction<br/>• Change Classification"]
        LLM["🤖 LLM Processor<br/>• Walmart Gateway<br/>• OpenAI Integration<br/>• AI-Enhanced Summaries & CRQs"]
    end

    %% Document Generation
    subgraph Generation["📝 Document Generation"]
        NOTES["📄 Release Notes<br/>• Confluence Format<br/>• Markdown Format<br/>• Section-based Layout"]
        CRQ["📋 CRQ Documents<br/>• Day 1 Setup<br/>• Day 2 Release<br/>• Enterprise Format"]
        SLACK_MSG["💬 Slack Messages<br/>• Block Kit Format<br/>• Progress Tracking<br/>• Team Notifications"]
    end

    %% Output & Integration
    subgraph Output["📤 Output & Integration"]
        FILES["📁 Generated Files<br/>• /output/service_v1.0.0_timestamp/<br/>• release_notes.txt<br/>• release_notes.md<br/>• crq_day1.txt<br/>• crq_day2.txt<br/>• rc_config.json"]
        COPY["📋 Copy-Paste Ready<br/>• Confluence Wiki Markup<br/>• Enterprise CRQ Format<br/>• Professional Language"]
    end

    %% Integrations & APIs
    subgraph APIs["🔗 External Integrations"]
        GH_API["🌐 GitHub API<br/>api.github.com<br/>Enterprise Support"]
        LLM_GW["🚀 LLM Gateway<br/>Walmart Internal<br/>SSL Certificates"]
        SLACK_API["💬 Slack API<br/>Block Kit Messages<br/>Socket Mode"]
    end

    %% Optional CI/CD Trigger
    subgraph CI["🚀 GitHub Workflow Trigger (Optional)"]
        GH_ACTIONS["📦 Dispatch GitHub Action<br/>Trigger CI/CD Pipeline"]
    end

    %% Workflow Connections
    CLI --> SETTINGS
    SETTINGS --> ENV
    SETTINGS --> ANALYZE
    CLI --> FETCH
    CLI --> GH_ACTIONS
    GITHUB --> FETCH
    ENV --> FETCH

    FETCH --> GH_API
    GH_API --> ANALYZE

    ANALYZE --> LLM
    LLM --> LLM_GW
    LLM_GW --> NOTES

    ANALYZE --> NOTES
    ANALYZE --> CRQ
    ANALYZE --> SLACK_MSG
    LLM --> CRQ

    NOTES --> FILES
    CRQ --> FILES
    SLACK_MSG --> SLACK_API

    FILES --> COPY

    SLACK --> SLACK_API
```

### 🔄 Detailed Workflow Steps

**1. 🎯 User Initiation**
```
User runs: python -m src.cli.run_release_agent
↓
Interactive prompts collect:
• RC Name & Manager
• Version range (v1.0.0 → v1.1.0)  
• Service name
• Release dates
• Output preferences
```

**2. 🔍 GitHub Analysis**
```
GitHub API Integration:
• Authenticate with personal access token
• Compare version tags/commits
• Fetch all merged PRs in range
• Extract PR metadata (titles, labels, authors)
• Categorize by type (feature/bug/schema/international)
```

**3. 🤖 AI Enhancement (Version 3.0)**
```
LLM Processing:
• Send PR summaries to Walmart Gateway
• Generate executive-friendly summaries
• Enhance technical descriptions
• Create professional language
• Fallback to template-based if AI unavailable
```

**4. 📝 Document Generation**
```
Multi-Format Output:
• Confluence release notes (wiki markup)
• Markdown release notes (GitHub ready)
• CRQ Day 1 document (setup instructions)
• CRQ Day 2 document (release execution)
• Configuration backup (JSON)
```

**5. 📤 Professional Output**
```
Enterprise-Ready Results:
• Copy-paste ready for Confluence
• Professional formatting and language
• Complete audit trail
• Timestamp-based organization
• Zero manual formatting required
```

### ⚡ Key Advantages

- **🚀 Speed**: 3-hour manual process → 5-minute automation
- **📊 Accuracy**: Automated PR analysis eliminates human error  
- **🎯 Consistency**: Template-based formatting ensures standards
- **🔗 Integration**: Direct GitHub API connection for real-time data
- **🤖 AI-Powered**: Smart categorization and executive summaries
- **📋 Enterprise**: Professional CRQ and release documentation
- **🔄 Flexible**: Works with tags, commits, branches, and date ranges

## 📁 Project Structure

```
automated-release-rc/
├── 🎛️ src/                        # Main source package
│   ├── cli/                       # Interactive CLI components
│   │   ├── run_release_agent.py   # Main CLI orchestrator
│   │   └── rc_agent_build_release.py
│   ├── config/                    # Configuration management
│   │   ├── config.py              # Settings and validation
│   │   ├── settings.yaml          # Main configuration (v4.0: no secrets)
│   │   └── settings.example.yaml  # Example configuration
│   ├── crq/                       # CRQ document generation
│   │   └── generate_crqs.py       # CRQ creation logic
│   ├── github_integration/        # GitHub API integration
│   │   └── fetch_prs.py           # PR fetching and analysis
│   ├── llm/                       # LLM integration (v4.0: enhanced)
│   │   ├── llm_client.py          # LLM orchestration
│   │   └── wmt_gateway_adapter.py # Walmart LLM gateway (v4.0: timeout)
│   ├── release_notes/             # Release notes generation
│   │   └── release_notes.py       # Notes creation logic
│   ├── slack/                     # Slack integration (optional)
│   │   └── release_signoff_notifier.py
│   ├── templates/                 # Jinja2 templates
│   │   ├── crq_template.j2        # CRQ document template
│   │   └── release_notes.j2       # Release notes template
│   └── utils/                     # Utilities and helpers
│       ├── ai_client.py           # AI integration
│       └── logging.py             # Logging configuration
│
├── 📚 docs/                       # Documentation
│   ├── quickstart.md              # Complete setup guide
│   ├── CLI_AGENT_README.md        # Comprehensive user guide
│   ├── configuration.md           # Configuration documentation
│   ├── IMPLEMENTATION_SUMMARY.md  # Technical implementation
│   ├── TEST_SUMMARY.md            # Testing documentation
│   └── plan.md                    # Project plan and status
│
├── 🧪 tests/                      # Test suite (v4.0: 36 tests)
│   ├── test_v4_features.py        # v4.0 feature tests (NEW)
│   ├── test_pr_counts.py          # Critical PR counting tests
│   ├── test_cli.py                # CLI integration tests
│   ├── test_github/               # GitHub integration tests
│   ├── test_slack/                # Slack integration tests
│   └── test_refactored_structure.py # Structure validation
│
├── 📋 scripts/                    # Helper scripts
│   └── run_tests.py               # Test runner utility
│
├── 🚀 run_rc_agent.sh            # v4.0: Automated wrapper script (NEW)
├── 🔐 .rc_env_checkout.sh        # v4.0: Environment template (do not commit)
├── 📁 output/                     # Generated files directory
├── 📁 cache/                      # Template cache directory
├── 📋 requirements.txt            # Python dependencies
└── 📋 pyproject.toml              # Python package metadata
```

### Testing & Validation
```bash
# Run all tests (v4.0: 36 tests total)
python -m pytest tests/ -v

# Test v4.0 specific features
python tests/test_v4_features.py

# Test critical PR counting functionality (very important)
python tests/test_pr_counts.py

# Test configuration loading (v4.0: environment-based)
python -c "from src.config.config import load_config; config = load_config(); print('✅ Config loads successfully')"

# Quick environment validation
source ~/.rc_env_checkout.sh && echo "✅ Environment loaded successfully"
```

**🎯 v4.0 Test Coverage:**
- ✅ **36 tests total** (100% passing)
- ✅ **6 new v4.0 feature tests** - Version validation, environment config, LLM timeout
- ✅ **30 existing tests** - All legacy functionality verified

### GitHub Actions (Optional)
You can also trigger via GitHub Actions by setting up repository secrets and using the workflow manually or via API.

## 🔧 Configuration Setup

### GitHub Token (Required)

**Step-by-Step Token Creation:**

1. **Go to GitHub Token Settings:**
   - Direct link: https://github.com/settings/tokens
   - Or navigate: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Create New Token:**
   - Click **"Generate new token (classic)"**
   - **Note:** `RC Release Automation Agent`
   - **Expiration:** 90 days (recommended)

3. **Required Scopes:**
   - ✅ **`repo`** - Full control of private repositories
     - This includes: repo:status, repo_deployment, public_repo, repo:invite, security_events
   - ✅ **`workflow`** - Update GitHub Action workflows (optional, only if using GitHub Actions)

4. **Token Format:**
   - Classic tokens start with `ghp_` (e.g., `ghp_1234567890abcdef...`)
   - Fine-grained tokens start with `github_pat_` (not recommended for this tool)

5. **Add to Environment File:**
   ```bash
   # Add to ~/.rc_env_checkout.sh
   export GITHUB_TOKEN="ghp_your_token_here"
   export GITHUB_REPO="your-org/your-repo"
   ```
   
   **🔒 v4.0 Security Note:** Tokens are NEVER stored in configuration files - only in environment variables!

**🔍 Troubleshooting Common Issues:**

**401 Unauthorized:**
- ❌ Token expired or invalid
- ❌ Missing `repo` scope
- ❌ Using fine-grained token instead of classic
- ❌ Wrong API URL for enterprise GitHub

**403 Forbidden:**
- ❌ Repository doesn't exist or no access
- ❌ Token lacks required permissions
- ❌ Rate limiting (wait a few minutes)

**Token Validation Test:**
```bash
# Test your token and repository access
curl -H "Authorization: token YOUR_TOKEN" \
     https://api.github.com/repos/YOUR_ORG/YOUR_REPO
```

### GitHub Enterprise Server (Corporate Users)
If you're using **GitHub Enterprise Server** (common in corporate environments), you need to update the API URL:

**Identify Your Setup:**
- **Public GitHub**: URLs like `https://github.com/your-org/repo`
- **Enterprise GitHub**: URLs like `https://github.company.com/your-org/repo`

**Configuration for Enterprise:**
```bash
# Add to ~/.rc_env_checkout.sh
export GITHUB_TOKEN="your_enterprise_token"
export GITHUB_REPO="your-org/your-repo"
export GITHUB_API_URL="https://github.company.com/api/v3"  # Note the /api/v3 suffix
```

**Examples:**
- Microsoft: `"https://github.microsoft.com/api/v3"`
- General pattern: `"https://[your-github-domain]/api/v3"`

**⚠️ Common Error:** Using `"https://api.github.com"` with enterprise tokens causes **401 Unauthorized** errors.

### AI Provider (Optional)
Add to your environment file `~/.rc_env_checkout.sh`:
```bash
# LLM Configuration (Optional - for AI features)
export LLM_PROVIDER="openai"                   # openai, walmart_sandbox
export OPENAI_API_KEY="sk-your-openai-key"     # OpenAI API key
export WMT_LLM_API_KEY="your-wmt-key"          # Walmart LLM key (optional)
export WMT_LLM_API_URL="http://llm-internal.walmart.com:8000"  # Walmart LLM URL
```

**🔒 v4.0 Security:** All API keys are environment variables only - never in configuration files!

## 🧠 Version 3.0 - LLM Integration Features

**Enhanced AI-Powered Release Automation**

Version 3.0 introduces advanced LLM integration for intelligent release documentation:

### **🎯 Multi-Provider LLM Support**
- **Walmart Enterprise Gateway** - Internal LLM access with SSL certificates
- **OpenAI** - GPT-4o-mini and other OpenAI models  
- **Anthropic** - Claude models for enterprise use
- **Automatic Fallback** - Graceful degradation when LLM unavailable

### **📊 AI-Generated Release Summaries**
- **Section 8 Enhancement** - AI-powered release summaries for leadership
- **International PR Filtering** - Smart detection of tenant/localization changes
- **Executive-Friendly Language** - Optimized for non-technical stakeholders

### **🔧 LLM Configuration**
Environment variables (in `~/.rc_env_checkout.sh`):
```bash
# LLM Provider Selection
export LLM_PROVIDER="openai"                   # openai, walmart_sandbox
export OPENAI_API_KEY="sk-your-openai-key"
export WMT_LLM_API_KEY="your-wmt-key"          # Optional: Walmart internal
export WMT_LLM_API_URL="http://llm-internal.walmart.com:8000"
```

System configuration (in `src/config/settings.yaml` - no secrets):
```yaml
llm:
  provider: "openai"                  # Default provider
  model: "gpt-4o-mini"
  enabled: false                      # v4.0: Disabled by default for performance
  fallback_enabled: true              # Use existing logic if LLM fails  
  timeout: 10                         # v4.0: 10-second timeout prevents hanging
  temperature: 0.1                    # Lower temperature for consistent output
```

### **🛡️ Enterprise Security Features**
- **Environment Variable Integration** - Secure API key management
- **SSL Certificate Support** - Walmart enterprise certificate handling
- **Graceful Fallback** - Continues working when LLM unavailable
- **Rate Limiting Protection** - Built-in request throttling

### **📈 Enhanced Output Quality**
- **Intelligent PR Categorization** - AI-assisted feature/bug/schema detection
- **Rich Slack Block Kit Messages** - Modern Slack formatting with progress bars
- **CRQ Generation** - AI-powered change request documentation
- **Professional Language** - Enterprise-appropriate tone and terminology

**🚀 Version 3.0 brings enterprise-grade AI to release automation while maintaining backward compatibility!**

## 🎉 What This Generates

### ✅ Professional Release Documentation
1. **Enterprise CRQ Documents** - Day 1 & Day 2 change requests
2. **Confluence Release Notes** - Copy-paste ready with wiki markup
3. **GitHub Release Notes** - Markdown formatted
4. **Release Configuration** - Complete setup details

### ✅ Output Structure
```
output/
└── service_v1.1.0_20240223_[timestamp]/
    ├── rc_config.json          # Complete release configuration
    ├── pr_authors.json         # PR authors list for Slack bot
    ├── crq_day1.txt           # Day 1 CRQ document
    ├── crq_day2.txt           # Day 2 CRQ document
    ├── release_notes.txt      # Confluence-ready release notes
    └── release_notes.md       # GitHub markdown version
```

### ✅ Key Features
- 🎯 **Flexible Version Support** - Works with Git tags AND commit SHAs
- 📊 **Intelligent PR Analysis** - Categorizes PRs by type (feature, schema, international)
- 📋 **Enterprise Compliance** - Professional formatting for corporate environments
- 🔗 **Copy-Paste Ready** - Confluence markup that works immediately
- ⏰ **Release Date Naming** - Output directories use your release dates
- 🚀 **30-Second Generation** - Complete documentation in under a minute

### ✅ Time Savings
- **Before**: 30+ minutes of manual documentation work
- **After**: 5-minute setup + 30-second generation
- **Quality**: Enterprise-ready, professional formatting

## 📚 Documentation

- **[Complete Quickstart Guide](docs/quickstart.md)** - Setup and usage (10 minutes)
- **[CLI User Guide](docs/CLI_AGENT_README.md)** - Comprehensive usage documentation
- **[Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)** - Technical details
- **[Test Summary](docs/TEST_SUMMARY.md)** - Testing documentation

## 🚀 Ready for Production (v4.0)

This system is **fully implemented and tested** with v4.0 enhancements:
- ✅ **v4.0 Enhanced Security** - Environment-only secrets, no config file exposure
- ✅ **v4.0 Multiple Version Formats** - Support for v1.2.3, 1.2.3-sha, SHA-only
- ✅ **v4.0 Enhanced CLI** - Release type prompts with helpful tips and validation
- ✅ **v4.0 Performance Optimizations** - LLM timeout (10s) prevents hanging
- ✅ **v4.0 Smart Service Detection** - Auto-extraction from GitHub repo names
- ✅ **Interactive CLI with validation** - Professional user experience
- ✅ **Enterprise-ready documentation** - Confluence + CRQ generation
- ✅ **Comprehensive testing suite** - 36/36 tests passing (100% success rate)
- ✅ **Flexible wrapper script** - Automated environment loading option

**Transform your release process with v4.0 today!** 🎉

---

### 🛡️ Proprietary Architecture & IP Notice

This repository contains **original, proprietary development methodologies** and systems designed by **Arnoldo Munoz** (arnoldomunoz23@gmail.com).

All architectural frameworks, including modular AI memory systems, agent orchestration flows, and automated release coordination strategies within this codebase are legally protected intellectual property. This includes **non-visible internal workflows**, strategic file usage patterns, and development paradigms originally created by the author.

Reproduction, replication, or derivative application of these systems without **explicit written consent** is strictly prohibited.

Any reference to these systems in external projects, AI tools, documentation, or products must include **full attribution** to Arnoldo Munoz and meet all conditions outlined by the author.

Unauthorized use may be subject to legal enforcement.
