# 🚀 Complete Setup Guide

**Get your RC Release Automation running in production**

This guide walks you through every step from initial setup to production deployment, with real examples and troubleshooting tips.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Python 3.8+** installed (`python --version`)
- [ ] **Git** configured with your GitHub account
- [ ] **GitHub repository** with Actions enabled
- [ ] **GitHub Personal Access Token** ready
- [ ] **Slack workspace** access (optional for integration)

---

## ⚡ Step-by-Step Setup

### **Step 1: Clone and Install (3 minutes)**

```bash
# Clone the repository
git clone https://github.com/ArnoldoM23/automated-release-rc.git
cd automated-release-rc

# Install the package and all dependencies in one step
pip install -e .

# Verify installation
python --version  # Should be 3.8+
rc-release-agent --help  # Should show CLI help
```

**✅ What this does:**
- Installs all Python dependencies automatically
- Sets up the `rc-release-agent` command
- Sets up the `rc-slack-bot` command  
- Makes the package available for development

### **Step 2: Environment Configuration (5 minutes)**

Create your environment file with secrets:

```bash
# Create environment file for secrets
touch .env
```

**Add your tokens to `.env`:**

```bash
# .env file (keep this private and never commit!)
GITHUB_TOKEN=ghp_your_github_personal_access_token
OPENAI_API_KEY=sk-your_openai_api_key_optional
SLACK_BOT_TOKEN=xoxb-your_slack_bot_token_optional
```

**⚠️ Important:** Add `.env` to your `.gitignore` to keep secrets safe!

### **Step 3: GitHub Token Setup (5 minutes)**

1. **Generate GitHub Token:**
   - Visit: https://github.com/settings/tokens
   - Click **"Generate new token (classic)"**
   - **Name:** `RC Release Automation`
   - **Scopes:** Select these checkboxes:
     - ✅ `repo` (Full repository access)
     - ✅ `workflow` (GitHub Actions access)
   - Click **"Generate token"**
   - **Copy the token immediately** (starts with `ghp_`)

2. **Add token to your environment:**
   ```bash
   export GITHUB_TOKEN="ghp_your_token_here"
   
   # Or add it to your .env file:
   echo "GITHUB_TOKEN=ghp_your_token_here" >> .env
   ```

3. **Test GitHub access:**
   ```bash
   python -c "
   import os
   from github import Github
   g = Github(os.getenv('GITHUB_TOKEN'))
   user = g.get_user()
   print(f'✅ GitHub access OK: {user.login}')
   print(f'Rate limit: {g.get_rate_limit().core.remaining}/5000')
   "
   ```

### **Step 4: Basic Verification (2 minutes)**

Test that everything is working:

```bash
# Test with demo data (no tokens required)
python demo_cli_workflow.py

# Test the CLI entry point
rc-release-agent --help

# Verify output directory is created
ls -la output/
# Should see: crq_day1.txt, crq_day2.txt, release_notes.txt
```

### **Step 5: Real Integration Test (5 minutes)**

Test with your actual repository:

```bash
# Set your GitHub token
export GITHUB_TOKEN="ghp_your_token"

# Run the CLI interactively
rc-release-agent

# Follow the prompts:
# - Service name: test-service
# - Production version: v1.0.0  
# - New version: v1.1.0
# - RC name: Your Name
# - RC Manager: Manager Name
# - Dates: Use tomorrow and day after

# Check generated files
echo "📄 Generated files:"
ls -la output/
echo "📋 CRQ Day 1 preview:"
head -20 output/crq_day1.txt
```

---

## 🔧 Advanced Configuration

### **AI Provider Setup (Optional but Recommended)**

#### **OpenAI Setup:**
```yaml
ai:
  provider: "openai"
  openai:
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4-1106-preview"  # or "gpt-3.5-turbo" for cost savings
    max_tokens: 1000
```

#### **Azure OpenAI Setup:**
```yaml
ai:
  provider: "azure"
  azure:
    endpoint: "${AZURE_OPENAI_ENDPOINT}"
    api_key: "${AZURE_OPENAI_API_KEY}"
    api_version: "2023-12-01-preview"
    deployment: "your-gpt4-deployment"
```

### **Dashboard URL Configuration**

Configure your monitoring system URLs directly:

```yaml
dashboard:
  # Direct URLs - specify exactly what you want
  confluence_dashboard_url: "https://confluence.yourcompany.com/display/YOUR_SERVICE/Dashboards"
  p0_dashboard_url: "https://grafana.yourcompany.com/d/your-service-p0"
  l1_dashboard_url: "https://grafana.yourcompany.com/d/your-service-l1"
  services_dashboard_url: "https://grafana.yourcompany.com/d/your-service-overview"
  wcnp_dashboard_url: "https://grafana.yourcompany.com/d/your-service-wcnp"
  istio_dashboard_url: "https://grafana.yourcompany.com/d/your-service-istio"
```

**Test dashboard URL configuration:**
```bash
python test_external_template.py
# Should show your configured URLs
```

### **External CRQ Template Setup**

For organizations with existing CRQ templates:

```yaml
external_template:
  enabled: true
  template_url: "https://sharepoint.company.com/sites/IT/CRQ_Template.docx"
  template_type: "auto"  # auto-detects format
  cache_duration: 3600  # 1 hour cache
  fallback_to_builtin: true  # Use built-in if download fails
```

**Supported template sources:**
- Microsoft Word documents (.docx)
- Text files (.txt)
- Markdown files (.md)
- SharePoint documents
- GitHub raw files

---

## 📋 Creating Your CRQ Template

### **Template Structure Guidelines**

Your CRQ template should use these placeholders:

```text
**CHANGE REQUEST - DAY {day_number}**

**Summary:** {service_name} Application Code deployment for {platform} ({regions}) - Day {day_number}

**Service Information:**
- Application Name: {service_name}
- Namespace: {namespace}
- Assembly: {service_name}-assembly
- Platform: {platform}
- Regions: {regions}

**Version Information:**
- Current Version: {prod_version}
- New Version: {new_version}
- Rollback Version: {prod_version}

**Release Team:**
- Release Coordinator: {rc_name}
- Release Manager: {rc_manager}
- Day 1 Date: {day1_date}
- Day 2 Date: {day2_date}

**Description Section:**
1. What is the business reason for this change?
   Standard release containing bug fixes, feature enhancements, and system improvements.

2. What is the technical summary of this change?
   Deployment of {service_name} version {new_version} containing multiple code changes.

3. What testing has been performed?
   All automated test suites passing, integration tests completed, performance validation done.

4. What is the risk assessment for this change?
   Medium risk - Standard deployment with established rollback procedures.

**Implementation Plan:**
Day {day_number} specific activities will be executed according to standard procedures.

**Validation Plan:**
- P0 Dashboard: {p0_dashboard_url}
- L1 Dashboard: {l1_dashboard_url}
- Services Dashboard: {services_dashboard_url}
- WCNP Dashboard: {wcnp_dashboard_url}
- Istio Dashboard: {istio_dashboard_url}

**Backout Plan:**
Rollback to version {prod_version} if issues are detected.

**Changes Included:**
{changes_summary}
```

### **Advanced Template Features**

#### **Day-Specific Content:**
```text
{% if day_number == "1" %}
**DAY 1 PREPARATION ACTIVITIES:**
- Environment validation
- Artifact preparation
- Team coordination
{% else %}
**DAY 2 DEPLOYMENT ACTIVITIES:**
- Production deployment
- Monitoring and validation
{% endif %}
```

#### **AI-Enhanced Content:**
```text
**Risk Assessment:**
{{ ai_analysis.get('RISK_ASSESSMENT', 'Standard deployment with established procedures') }}

**Technical Summary:**
{{ ai_analysis.get('TECHNICAL_SUMMARY', 'Code deployment containing ' + total_prs|string + ' changes') }}
```

#### **PR Integration:**
```text
**Pull Requests Included:**
{% for pr in prs %}
- PR #{{ pr.number }}: {{ pr.title }} (@{{ pr.user.login }})
  Type: {{ pr.labels | map(attribute='name') | join(', ') }}
{% endfor %}

Total Changes: {{ total_prs }} pull requests
```

### **Template Validation**

Test your template before using in production:

```bash
# Test external template download
python test_external_template.py

# Test template with mock data
rc-release-agent --test-mode --config-path config/settings.yaml

# Validate specific template features
python -c "
from crq.external_template import ExternalTemplateManager
from config.config import load_config
manager = ExternalTemplateManager(load_config())
print('✅ Template system working' if manager else '❌ Template failed')
"
```

---

## 💬 Slack Integration Setup

### **Option 1: Slack Workflow Builder (Recommended)**

**Pros:** No app approval, 5-minute setup, zero hosting  
**Cons:** Basic notifications only

1. **Create Webhook Workflow:**
   - Open Slack → Tools → Workflow Builder
   - Create new workflow → "Shortcut" trigger
   - Add steps:
     - Form with fields: service_name, prod_version, new_version, etc.
     - Send a web request to your GitHub Actions webhook

2. **GitHub Actions Integration:**
   Create `.github/workflows/release_automation.yml`:
   ```yaml
   name: Release Automation
   on:
     repository_dispatch:
       types: [slack_release_request]
   
   jobs:
     generate_release_docs:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - uses: actions/setup-python@v4
           with:
             python-version: '3.10'
         - run: pip install -r requirements.txt
         - run: |
             rc-release-agent \
               --service-name "${{ github.event.client_payload.service_name }}" \
               --prod-version "${{ github.event.client_payload.prod_version }}" \
               --new-version "${{ github.event.client_payload.new_version }}" \
               --rc-name "${{ github.event.client_payload.rc_name }}" \
               --rc-manager "${{ github.event.client_payload.rc_manager }}"
           env:
             GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
             OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
         - uses: actions/upload-artifact@v3
           with:
             name: release-documents
             path: output/
   ```

### **Option 2: Full Slack Bot (Advanced)**

For interactive features, deploy the included Slack bot:

```bash
cd slack_bot
# Follow instructions in slack_bot/README.md
```

---

## 🧪 Testing & Validation

### **Comprehensive Test Suite**

```bash
# Run all tests
python test_cli.py --test-all

# Individual test components
python test_cli.py --test-config      # Configuration
python test_cli.py --test-github      # GitHub API
python test_cli.py --test-ai          # AI providers
python test_cli.py --test-templates   # Template processing

# External features
python test_external_template.py      # Dashboard URLs + external templates
```

### **Mock Data Testing**

The system includes 15 mock PRs for comprehensive testing:

```bash
rc-release-agent --test-mode \
  --service-name test-service \
  --prod-version v1.0.0 \
  --new-version v1.1.0
```

**Mock data includes:**
- 5 schema PRs (database changes)
- 4 feature PRs (new functionality)
- 5 bugfix PRs (critical and non-critical)
- 1 international PR (i18n updates)

### **Production Readiness Checklist**

- [ ] Configuration loads without errors
- [ ] GitHub API connection works
- [ ] AI provider responds (optional)
- [ ] Templates generate successfully
- [ ] Dashboard URLs format correctly
- [ ] External template downloads (if enabled)
- [ ] Output files are well-formatted
- [ ] All tests pass

---

## 🚨 Troubleshooting

### **Common Issues**

#### **"Configuration validation failed"**
```bash
# Check your YAML syntax
python -c "import yaml; yaml.safe_load(open('config/settings.yaml'))"

# Validate configuration
python -c "from config.config import load_config; load_config()"
```

#### **"GitHub API rate limit exceeded"**
```bash
# Check your rate limit
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit

# Use authenticated requests (should give 5000/hour instead of 60/hour)
```

#### **"No PRs found"**
```bash
# Check if your repository has recent PRs
python -c "
from github import Github
import os
g = Github(os.getenv('GITHUB_TOKEN'))
repo = g.get_repo('your-org/your-repo')
prs = list(repo.get_pulls(state='closed', sort='updated', direction='desc'))[:5]
print(f'Recent PRs: {len(prs)}')
for pr in prs:
    print(f'  #{pr.number}: {pr.title}')
"
```

#### **"AI provider failed"**
```bash
# Test AI connectivity
python -c "
from utils.ai_client import AIClient
from config.config import load_config
client = AIClient(load_config().ai)
print('✅ AI working' if client else '❌ AI failed')
"

# The system works without AI - it uses fallback content
```

#### **"External template download failed"**
```bash
# Test external template access
python -c "
import requests
url = 'your_template_url'
resp = requests.get(url)
print(f'Status: {resp.status_code}, Content-Type: {resp.headers.get('content-type')}')
"

# Check if fallback is enabled
grep "fallback_to_builtin" config/settings.yaml
```

### **Debug Mode**

Enable verbose logging for troubleshooting:

```bash
# Set debug logging
export LOG_LEVEL=DEBUG

# Or in config/settings.yaml
app:
  log_level: "DEBUG"

# Run with debug output
rc-release-agent --test-mode --service-name debug-test
```

### **Performance Optimization**

For faster execution:

```bash
# Cache AI responses locally (for development)
export OPENAI_API_KEY=""  # Disable AI for faster testing

# Use smaller PR sets for testing
rc-release-agent --max-prs 5 --service-name test

# Disable external template downloads during development
# Set external_template.enabled: false in config
```

---

## 🔒 Security Best Practices

### **Token Management**

```bash
# Never commit tokens to git
echo ".env" >> .gitignore
echo "config/settings.local.yaml" >> .gitignore

# Use GitHub secrets for CI/CD
gh secret set GITHUB_TOKEN --body "ghp_your_token"
gh secret set OPENAI_API_KEY --body "sk_your_key"

# Rotate tokens regularly
# Check token permissions periodically
```

### **Environment Separation**

```bash
# Different configs for different environments
config/settings.yaml          # Production
config/settings.staging.yaml  # Staging
config/settings.local.yaml    # Local development

# Load specific config
rc-release-agent --config-path config/settings.staging.yaml
```

---

## 🚀 Production Deployment

### **GitHub Actions Deployment**

1. **Set up repository secrets:**
   ```bash
   gh secret set GITHUB_TOKEN --body "ghp_your_production_token"
   gh secret set OPENAI_API_KEY --body "sk_your_openai_key"
   gh secret set SLACK_WEBHOOK_URL --body "https://hooks.slack.com/..."
   ```

2. **Enable Actions in your repository:**
   - Go to Settings → Actions → General
   - Allow actions and reusable workflows

3. **Test the workflow:**
   ```bash
   # Trigger manually
   gh workflow run release_automation.yml
   
   # Check status
   gh run list --workflow=release_automation.yml
   ```

### **Local Production Setup**

For running locally in production:

```bash
# Production environment setup
cp config/settings.example.yaml config/settings.prod.yaml
# Edit with production values

# Production run
rc-release-agent \
  --config-path config/settings.prod.yaml \
  --service-name your-service \
  --prod-version v2.1.0 \
  --new-version v2.2.0

# Set up cron job for scheduled releases
crontab -e
# Add: 0 9 * * 1 cd /path/to/project && rc-release-agent --scheduled-release
```

---

## 📈 Next Steps

Once you have the basic system running:

1. **📋 Customize your CRQ template** for your organization's format
2. **🔧 Configure dashboard URLs** for your monitoring systems
3. **🤖 Set up AI providers** for enhanced content generation
4. **💬 Deploy Slack integration** for team workflow
5. **📊 Add monitoring** for the automation system itself
6. **🔄 Integrate with CI/CD** for automated releases
7. **👥 Train your team** on the new workflow

---

## 💡 Pro Tips

- **Start simple:** Use test mode and mock data first
- **Gradual rollout:** Begin with one service, expand to others
- **Monitor usage:** Track time savings and quality improvements
- **Gather feedback:** Get input from Release Captains and stakeholders
- **Iterate quickly:** The system is designed for easy customization

---

**Need help?** Open an issue on GitHub or check our troubleshooting guide! 