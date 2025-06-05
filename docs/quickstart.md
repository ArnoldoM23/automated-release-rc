# 🚀 Complete Quickstart Guide

**Get your RC Release Automation Agent running in under 10 minutes**

---

## 🎯 **What You'll Achieve**

By the end of this guide, you'll have:
- ✅ Local CLI command `python -m src.cli.run_release_agent` working
- ✅ Automatic GitHub Actions execution (optional)
- ✅ Enterprise-ready release documentation generation
- ✅ Complete CRQ document creation
- ✅ Professional Confluence-ready output

**⏱️ Total Time: 8-10 minutes**

---

## 🚀 **Step 1: Fork & Clone (1 minute)**

### **1.1 Fork the Repository**
1. Go to: https://github.com/ArnoldoM23/automated-release-rc
2. Click **"Fork"** button (top right)
3. Select your GitHub account/organization

### **1.2 Clone Your Fork**
```bash
# Replace YOUR_USERNAME with your GitHub username
git clone https://github.com/YOUR_USERNAME/automated-release-rc.git
cd automated-release-rc

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m src.cli.run_release_agent --help
```

---

## 🔑 **Step 2: GitHub Setup (2 minutes)**

### **2.1 Create GitHub Personal Access Token (Classic)**

**Why Classic Tokens?** The RC Agent requires a classic Personal Access Token (PAT) for reliable repository access across different GitHub configurations.

**📋 Step-by-Step Instructions:**

1. **Navigate to Token Settings:**
   - **Direct Link:** https://github.com/settings/tokens
   - **Or Navigate:** GitHub → Profile Photo → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token:**
   - Click **"Generate new token (classic)"**
   - **Note/Description:** `RC Release Automation Agent`
   - **Expiration:** Select `90 days` (recommended) or your organization's policy
   
3. **⚠️ Critical: Select Required Scopes**
   
   **Required Scopes (check these boxes):**
   - ✅ **`repo`** - Full control of private repositories
     - ✅ `repo:status` (automatically included)
     - ✅ `repo_deployment` (automatically included) 
     - ✅ `public_repo` (automatically included)
     - ✅ `repo:invite` (automatically included)
     - ✅ `security_events` (automatically included)
   
   **Optional Scopes:**
   - ✅ **`workflow`** - Update GitHub Action workflows (only if you plan to use GitHub Actions automation)
   
   **❌ Do NOT Select:**
   - ❌ `admin:*` scopes (unnecessary and security risk)
   - ❌ `delete_repo` (security risk)
   - ❌ Fine-grained permissions (not supported)

4. **Generate and Secure Token:**
   - Click **"Generate token"**
   - **🚨 IMMEDIATELY COPY** the token that appears
   - Token format: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **⚠️ You will NOT see this token again!**
   - Store it securely (password manager recommended)

**🔍 Token Validation (Optional but Recommended):**
```bash
# Test your token immediately after creation
curl -H "Authorization: token ghp_your_token_here" \
     https://api.github.com/user

# Expected response: Your GitHub user info (200 OK)
# Error response: {"message": "Bad credentials"} (401)
```

### **2.2 Update Configuration File**

Edit `src/config/settings.yaml` and replace the placeholder values:

```yaml
# GitHub Configuration  
github:
  token: "ghp_your_actual_token_here"  # Paste your copied token here
  repo: "YOUR_USERNAME/automated-release-rc"  # Update to your forked repository
  api_url: "https://api.github.com"
```

**📝 Configuration Examples:**

**For Personal Fork:**
```yaml
github:
  token: "ghp_1234567890abcdefghijklmnopqrstuvwxyz123"
  repo: "john-doe/automated-release-rc"  
  api_url: "https://api.github.com"
```

**For Organization Repository:**
```yaml
github:
  token: "ghp_1234567890abcdefghijklmnopqrstuvwxyz123"
  repo: "my-company/automated-release-rc"
  api_url: "https://api.github.com"
```

**For GitHub Enterprise Server:**
```yaml
github:
  token: "ghp_enterprise_token_here"
  repo: "my-org/automated-release-rc"
  api_url: "https://github.company.com/api/v3"  # Note the /api/v3 suffix
```

### **2.3 Verify Token Setup**

Test your configuration before proceeding:

```bash
# Test configuration loading
python -c "
import sys
sys.path.insert(0, 'src')
from config.config import load_config
config = load_config()
print(f'✅ Config loaded: {config.github.repo}')
print(f'🔑 Token format: {config.github.token[:8]}...')
"

# Test GitHub API access
python -c "
import sys
sys.path.insert(0, 'src')
from github.fetch_prs import test_github_connection
test_github_connection()
"
```

**Expected Output:**
```
✅ Config loaded: your-username/automated-release-rc
🔑 Token format: ghp_1234...
✅ GitHub API connection successful
✅ Repository access confirmed
```

**🚨 Common Issues & Solutions:**

**❌ "Bad credentials" (401 Error):**
- Check token was copied correctly (no extra spaces)
- Verify token hasn't expired
- Ensure you're using a classic token (`ghp_` prefix)

**❌ "Not Found" (404 Error):**
- Check repository name format: `owner/repo-name`
- Verify repository exists and is accessible
- Ensure token has `repo` scope selected

**❌ "API rate limit exceeded":**
- Wait 60 minutes for rate limit reset
- Or use a different GitHub account temporarily

---

## ✅ **Step 3: Test Your Setup (2 minutes)**

### **3.1 Test Configuration**
```bash
# Test configuration loading
python -c "from src.config.config import load_config; config = load_config(); print('✅ Config loads successfully')"

# Test critical PR counting functionality (very important)
python tests/test_pr_counts.py

# Test CLI help
python -m src.cli.run_release_agent --help
```

### **3.2 Quick Test Run**
```bash
# Run the CLI interactively
python -m src.cli.run_release_agent

# Follow the prompts with test data:
# - RC name: Your Name
# - RC Manager: Manager Name  
# - Production version: v1.0.0 (or any existing tag/commit)
# - New version: v1.1.0 (or any target tag/commit)
# - Service name: test-service
# - Release type: standard
# - Day 1 Date: 2024-02-23
# - Day 2 Date: 2024-02-24
# - Output folder: test-output/

# Check generated files
echo "📄 Generated files:"
ls -la test-output/*/
```

**Expected output structure:**
```
test-output/
└── test-service_v1.1.0_20240223_[timestamp]/
    ├── rc_config.json
    ├── crq_day1.txt
    ├── crq_day2.txt
    ├── release_notes.txt
    └── release_notes.md
```

---

## 🤖 **Step 4: GitHub Actions Setup (Optional, 3 minutes)**

For remote execution via GitHub Actions, add repository secrets:

### **4.1 Add Repository Secrets**
1. Go to your forked repository on GitHub
2. Click **"Settings"** → **"Secrets and variables"** → **"Actions"**
3. Click **"New repository secret"** and add:

**Required:**
```
Name: GITHUB_TOKEN
Value: ghp_your_personal_access_token_here
```

**Optional (for AI features):**
```
Name: OPENAI_API_KEY
Value: sk-your_openai_key_here

Name: ANTHROPIC_API_KEY  
Value: your_anthropic_key_here
```

### **4.2 Test GitHub Actions**
You can trigger the workflow manually or via API:

```bash
# Trigger via GitHub CLI (if you have gh installed)
gh workflow run "RC Release Automation" \
  --repo YOUR_USERNAME/automated-release-rc \
  -f prod_version="v1.0.0" \
  -f new_version="v1.1.0" \
  -f service_name="test-service" \
  -f release_type="standard" \
  -f rc_name="Your Name" \
  -f rc_manager="Manager Name" \
  -f day1_date="2024-02-23" \
  -f day2_date="2024-02-24"

# Or trigger via API
curl -X POST \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/YOUR_USERNAME/automated-release-rc/actions/workflows/rc-release-automation.yml/dispatches \
  -d '{"ref":"main","inputs":{"prod_version":"v1.0.0","new_version":"v1.1.0","service_name":"test-service","release_type":"standard","rc_name":"Your Name","rc_manager":"Manager Name","day1_date":"2024-02-23","day2_date":"2024-02-24"}}'
```

---

## 🧪 **Step 5: Test Complete Workflow (30 seconds)**

### **5.1 Run a Real Test**
```bash
# Run with actual repository data
python -m src.cli.run_release_agent
```

Fill out with realistic test data:

**Example Test Data:**
- **RC name:** `Your Name`
- **RC Manager:** `Your Manager`
- **Production version:** `v0.4.6` (or any existing tag/commit)
- **New version:** `v0.4.7` (or target tag/commit)
- **Service name:** `ce-cartxo`
- **Release type:** `standard`
- **Day 1 Date:** Tomorrow's date
- **Day 2 Date:** Day after tomorrow
- **Output folder:** `output/`

### **5.2 Verify Results**
Check the generated output directory:

```bash
# List generated files
ls -la output/*/

# Preview CRQ content
head -50 output/*/crq_day1.txt

# Check release notes
head -50 output/*/release_notes.txt

# Verify PR counts
grep -E "(feature|schema|international)" output/*/release_notes.txt
```

### **5.3 Validate PR Detection**
The most critical functionality is PR counting. Verify it works:

```bash
# Run the critical test
python tests/test_pr_counts.py

# Should show something like:
# ✅ Found 10 total PRs
# ✅ 3 schema PRs  
# ✅ 4 feature PRs
# ✅ 0 international PRs
```

---

## 🎉 **Success! You're Live**

**✅ Your RC Release Automation Agent is now fully operational!**

### **What You Now Have:**
- 🚀 **CLI Command:** `python -m src.cli.run_release_agent` generates professional docs in 30 seconds
- 📋 **Enterprise Documentation:** Copy-paste ready Confluence release notes with wiki markup
- 📝 **CRQ Documents:** Day 1 & Day 2 change requests with AI insights
- 🔧 **GitHub Actions:** Optional serverless execution  
- 📊 **Professional Output:** 6,000+ bytes of enterprise-ready content
- 🎯 **Flexible Version Support:** Works with Git tags AND commit SHAs
- ⚡ **Multi-Workflow Support:** Standard releases, hotfixes, and custom builds
- 🔗 **Copy-Paste Ready:** Confluence markup that works immediately

### **🆕 Key Features:**
- ✅ **Commit SHA Support:** Use `abc123f` instead of tags for precise version control
- ✅ **Mixed References:** Combine tags and commit SHAs (e.g., `v1.0.0` → `def456a`)
- ✅ **No-Tag Workflows:** Perfect for repositories without consistent tagging
- ✅ **Hotfix Releases:** Target exact commits for emergency deployments
- ✅ **Enterprise Validation:** Built-in testing and reference validation
- ✅ **Release Date Naming:** Output directories use your release dates, not current time

### **Daily Usage:**
```bash
# Standard workflow
cd /path/to/automated-release-rc
source .venv/bin/activate
python -m src.cli.run_release_agent

# Quick test
python tests/test_pr_counts.py

# Check latest output
ls -la output/*/
```

---

## 🆘 **Troubleshooting**

### **"ModuleNotFoundError" or Import Errors**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Test imports
python -c "from src.config.config import load_config; print('✅ Imports work')"
```

### **"Configuration validation error"**
```bash
# Check your settings file
cat src/config/settings.yaml

# Verify GitHub token is set
python -c "
from src.config.config import load_config
config = load_config()
print(f'GitHub token configured: {bool(config.github.token and len(config.github.token) > 10)}')
print(f'Repository: {config.github.repo}')
"
```

### **"No PRs found between versions" Error**
- **For Git tags:** Ensure tags exist in repository: `git tag -l`
- **For commit SHAs:** Verify commits exist and are valid (7-40 hex characters)
- Check commit messages contain PR references (`#123`, `PR #123`, `Merge pull request #123`)
- Ensure PRs were actually merged (not just closed)
- Verify you have access to the repository

### **"Invalid version reference" Error**
- **Git tags:** Use format `v1.2.3` or `1.2.3` (with or without 'v' prefix)
- **Commit SHAs:** Use 7-40 character hex strings (e.g., `abc123f`, `9f8e7d6c5b4a`)
- **Mixed usage:** You can combine tags and commit SHAs (e.g., `v1.0.0` → `def456a`)
- Verify references exist in the target repository

### **GitHub Actions failing**
- Check Actions tab for detailed error messages
- Verify all repository secrets are set correctly
- Look for Python errors in workflow logs
- Ensure workflow file exists: `.github/workflows/rc-release-automation.yml`

### **Testing Your Setup**
If you want to validate everything works:

```bash
# Test configuration
python -c "from src.config.config import load_config; load_config(); print('✅ Config OK')"

# Test GitHub access  
python -c "
from src.github.fetch_prs import GitHubPRFetcher
from src.config.config import load_config
config = load_config()
fetcher = GitHubPRFetcher(config.github.token, config.github.repo)
print('✅ GitHub access OK')
"

# Test critical functionality
python tests/test_pr_counts.py

# Run with demo data
python -m src.cli.run_release_agent
```

---

## 🔧 **Advanced Configuration**

### **AI Provider Setup (Optional)**

Edit `src/config/settings.yaml` to enable AI features:

```yaml
ai:
  provider: "openai"  # or "anthropic"
  openai:
    api_key: "sk-your_openai_api_key_here"
    model: "gpt-4-1106-preview"
    max_tokens: 1000
```

### **Organization Customization**

```yaml
organization:
  name: "Your Company"
  default_service: "your-service"
  timezone: "UTC"
  regions:
    - "EUS"
    - "SCUS"
    - "WUS"
  platform: "Glass"  # or "Store"
```

### **Dashboard URLs**

```yaml
dashboard:
  confluence_dashboard_url: "https://confluence.yourcompany.com/display/SERVICE/Dashboards"
  p0_dashboard_url: "https://grafana.yourcompany.com/d/service-p0"
  l1_dashboard_url: "https://grafana.yourcompany.com/d/service-l1"
  services_dashboard_url: "https://grafana.yourcompany.com/d/service-overview"
```

---

## 📞 **Need Help?**

- 🐛 **Issues:** [GitHub Issues](https://github.com/ArnoldoM23/automated-release-rc/issues)
- 💬 **Questions:** [GitHub Discussions](https://github.com/ArnoldoM23/automated-release-rc/discussions)
- 📧 **Enterprise Support:** Contact for professional services

**🎯 You now have a professional release automation agent that reduces RC workload by 90%!** 