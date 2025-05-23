# ⚡ Quick Start Guide - 5 Minutes to Live Workflow

**Get your RC Release Automation Agent running in Slack in under 5 minutes**

---

## 🎯 **What You'll Achieve**

By the end of this guide, you'll have:
- ✅ `/run-release` command working in Slack
- ✅ Automatic GitHub Actions execution
- ✅ Enterprise-ready release documentation generation
- ✅ Complete CRQ document creation
- ✅ Professional Confluence-ready output

**⏱️ Total Time: 4-5 minutes**

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

# Install dependencies locally (optional - for testing)
pip install -r requirements.txt
```

---

## 🔑 **Step 2: GitHub Setup (1.5 minutes)**

### **2.1 Create GitHub Personal Access Token**
1. Go to: **GitHub** → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **"Generate new token (classic)"**
3. **Note:** `RC Release Automation`
4. **Expiration:** 90 days (or your preference)
5. **Scopes:** Select these checkboxes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
6. Click **"Generate token"**
7. **Copy the token immediately** (you won't see it again)

### **2.2 Add Repository Secrets**
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

---

## 📱 **Step 3: Slack Workflow Setup (2 minutes)**

### **3.1 Open Slack Workflow Builder**
1. In Slack, click your **workspace name** (top left)
2. Go to **"Tools"** → **"Workflow Builder"**
3. Click **"Create"** → **"From scratch"**

### **3.2 Configure Workflow Trigger**
1. **Name:** `RC Release Automation`
2. **Description:** `Generate release documentation automatically`
3. **Trigger:** Select **"Shortcut"**
4. **Shortcut name:** `run-release`
5. **Short description:** `Generate release docs`
6. Click **"Next"**

### **3.3 Add Release Form**
1. Click **"Add Step"** → **"Send a form"**
2. **Form title:** `🚀 RC Release Information`
3. **Send to:** `Person who starts this workflow`
4. Add these **8 fields** (copy exactly):

```
Field 1: Production Version
- Type: Short text
- Variable: prod_version
- Placeholder: v1.2.3 or abc123f
- Help text: Git tag (v1.2.3) or commit SHA (abc123f)
- Required: Yes

Field 2: New Release Version  
- Type: Short text
- Variable: new_version
- Placeholder: v1.3.0 or def456a
- Help text: Git tag (v1.3.0) or commit SHA (def456a)
- Required: Yes

Field 3: Service Name
- Type: Short text
- Variable: service_name
- Placeholder: cer-cart
- Required: Yes

Field 4: Release Type
- Type: Select from a list
- Variable: release_type
- Options: standard, hotfix, ebf
- Required: Yes

Field 5: Release Coordinator (RC)
- Type: Short text
- Variable: rc_name
- Placeholder: John Doe
- Required: Yes

Field 6: Release Manager
- Type: Short text
- Variable: rc_manager
- Placeholder: Jane Smith
- Required: Yes

Field 7: CRQ Day 1 Date (Preparation)
- Type: Date
- Variable: day1_date
- Required: Yes

Field 8: CRQ Day 2 Date (Deployment)
- Type: Date
- Variable: day2_date
- Required: Yes
```

**📋 Version Reference Support:**

Our system now supports **both Git tags and commit SHAs**:
- **Git Tags:** `v1.2.3`, `1.0.0`, `release-2024-01` (standard releases)
- **Commit SHAs:** `abc123f`, `9f8e7d6c5b4a` (hotfixes, no-tag workflows)
- **Mixed usage:** You can use a tag for production and SHA for new version (or vice versa)

**✅ Benefits:**
- **No tags required** - works with any repository
- **Precise control** - target exact commits for hotfixes
- **Flexible workflows** - supports non-standard release processes  
- **Backward compatible** - existing tag-based workflows still work

5. Click **"Save"** and **"Next"**

### **3.4 Add GitHub Integration**
1. Click **"Add Step"** → **"Send a web request"**
2. **Request name:** `Trigger Release Agent`

**URL:** (Replace YOUR_USERNAME)
```
https://api.github.com/repos/YOUR_USERNAME/automated-release-rc/dispatches
```

**Method:** `POST`

**Headers:** (Replace YOUR_GITHUB_TOKEN)
```
Authorization: Bearer YOUR_GITHUB_TOKEN
Content-Type: application/json
Accept: application/vnd.github.v3+json
```

**Request Body:** (Copy exactly)
```json
{
  "event_type": "run-release",
  "client_payload": {
    "prod_version": "{{prod_version}}",
    "new_version": "{{new_version}}",
    "service_name": "{{service_name}}",
    "release_type": "{{release_type}}",
    "rc_name": "{{rc_name}}",
    "rc_manager": "{{rc_manager}}",
    "day1_date": "{{day1_date}}",
    "day2_date": "{{day2_date}}",
    "slack_channel": "#release-rc",
    "slack_user": "{{workflow_user}}"
  }
}
```

3. Click **"Save"** and **"Next"**

### **3.5 Add Confirmation Message**
1. Click **"Add Step"** → **"Send a message"**
2. **Send to:** `Person who started this workflow`

**Message:** (Replace YOUR_USERNAME)
```
🚀 **Release automation started!**

**Service:** {{service_name}} {{prod_version}} → {{new_version}}
**RC:** {{rc_name}}
**Manager:** {{rc_manager}}
**Type:** {{release_type}}
**Schedule:** {{day1_date}} (Day 1) → {{day2_date}} (Day 2)

⏳ Generating release documentation...
📋 GitHub Actions will post results when complete
🔗 Check progress: https://github.com/YOUR_USERNAME/automated-release-rc/actions

*Estimated completion: 30-60 seconds*
```

3. Click **"Save"** and **"Next"**

### **3.6 Publish Workflow**
1. Review settings and add collaborators if needed
2. Click **"Publish"**
3. Confirm publishing

---

## 🧪 **Step 4: Test Complete Workflow (30 seconds)**

### **4.1 Run Test Release**
1. In any Slack channel, type: `/run-release`
2. Fill out the form with test data:

**Option A: Using Git Tags (Standard Release)**
   - **Production Version:** `v1.0.0`
   - **New Version:** `v1.1.0`
   - **Service Name:** `test-service`
   - **Release Type:** `standard`
   - **RC Name:** `Your Name`
   - **Release Manager:** `Your Manager`
   - **Day 1 Date:** Tomorrow's date
   - **Day 2 Date:** Day after tomorrow

**Option B: Using Commit SHAs (Hotfix/No-Tag Workflow)**
   - **Production Version:** `abc123f`
   - **New Version:** `def456a`
   - **Service Name:** `test-service`
   - **Release Type:** `hotfix`
   - **RC Name:** `Your Name`
   - **Release Manager:** `Your Manager`
   - **Day 1 Date:** Tomorrow's date
   - **Day 2 Date:** Day after tomorrow

**Option C: Mixed Usage (Tag to Commit)**
   - **Production Version:** `v1.4.2`
   - **New Version:** `9f8e7d6c`
   - **Service Name:** `test-service`
   - **Release Type:** `standard`
   - **RC Name:** `Your Name`
   - **Release Manager:** `Your Manager`
   - **Day 1 Date:** Tomorrow's date
   - **Day 2 Date:** Day after tomorrow

3. Click **"Submit"**

### **4.2 Verify Results**
1. ✅ You should see the confirmation message in Slack
2. ✅ Go to GitHub → Your repo → Actions tab
3. ✅ You should see "🚀 RC Release Automation" workflow running
4. ✅ Wait 30-60 seconds for completion
5. ✅ Download artifacts when workflow completes

### **4.3 Check Generated Files**
When the workflow completes, download artifacts to find:
- **`release_notes.txt`** - Enterprise Confluence content (6,000+ bytes)
- **`crq_day1.txt`** - Day 1 preparation CRQ  
- **`crq_day2.txt`** - Day 2 deployment CRQ
- **`release_notes.md`** - GitHub markdown version
- **`RELEASE_SUMMARY.md`** - Complete summary

---

## 🎉 **Success! You're Live**

**✅ Your RC Release Automation Agent is now fully operational!**

### **What You Now Have:**
- 🚀 **Slack Command:** `/run-release` generates professional docs in 30 seconds
- 📋 **Enterprise Documentation:** Copy-paste ready Confluence release notes with wiki markup
- 📝 **CRQ Documents:** Day 1 & Day 2 change requests with AI insights
- 🔧 **GitHub Actions:** Serverless, zero-cost execution  
- 📊 **Professional Output:** 6,000+ bytes of enterprise-ready content
- 🎯 **Flexible Version Support:** Works with Git tags AND commit SHAs
- ⚡ **Multi-Workflow Support:** Standard releases, hotfixes, and custom builds
- 🔗 **Copy-Paste Ready:** Confluence markup that works immediately

### **🆕 Latest Capabilities:**
- ✅ **Commit SHA Support:** Use `abc123f` instead of tags for precise version control
- ✅ **Mixed References:** Combine tags and commit SHAs (e.g., `v1.0.0` → `def456a`)
- ✅ **No-Tag Workflows:** Perfect for repositories without consistent tagging
- ✅ **Hotfix Releases:** Target exact commits for emergency deployments
- ✅ **Enterprise Validation:** Built-in testing and reference validation
- ✅ **Wiki Markup:** Professional Confluence formatting ready for copy-paste

### **Next Steps:**
1. **Share with your team** - Add collaborators to the Slack workflow
2. **Customize templates** - Edit `templates/release_notes.j2` for your organization
3. **Configure settings** - Update `config/settings.yaml` with your details
4. **Scale across services** - Use with any microservice or application

---

## 🆘 **Troubleshooting**

### **"Could not reach URL" Error**
- Verify GitHub token has `repo` and `workflow` permissions
- Check repository name in URL is correct (YOUR_USERNAME/automated-release-rc)
- Ensure repository is public or token has private repo access

### **"Workflow not triggering" Error**
- Go to repo Settings → Actions → General → ensure "Allow all actions" is selected
- Verify repository secrets are named exactly: `GITHUB_TOKEN`
- Check GitHub token hasn't expired

### **"Form variables not passing" Error**  
- Double-check variable names match exactly (`prod_version`, not `production_version`)
- Ensure all fields are marked as required
- Verify JSON syntax in request body is valid

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

### **Testing Version References**
If you want to test your version references before running the full workflow:

```bash
# Clone your repository locally
git clone https://github.com/YOUR_USERNAME/automated-release-rc.git
cd automated-release-rc

# Test with your repository
python tests/test_github/test_github_integration.py \
  --repo your-org/your-repo \
  --old-tag v1.0.0 \
  --new-tag v1.1.0

# Test with commit SHAs
python tests/test_github/test_github_integration.py \
  --repo your-org/your-repo \
  --old-tag abc123f \
  --new-tag def456a

# List available tags in your repository
python tests/test_github/test_github_integration.py \
  --list-tags \
  --repo your-org/your-repo
```

---

## 🔗 **What's Next?**

- **[Configuration Guide](configuration.md)** - Customize for your organization
- **[Template Customization](templates.md)** - Brand the output for your company
- **[Enterprise Deployment](enterprise.md)** - Scale across multiple teams
- **[API Reference](api.md)** - Integrate programmatically

---

## 📞 **Need Help?**

- 🐛 **Issues:** [GitHub Issues](https://github.com/ArnoldoM23/automated-release-rc/issues)
- 💬 **Questions:** [GitHub Discussions](https://github.com/ArnoldoM23/automated-release-rc/discussions)
- 📧 **Enterprise Support:** Contact for professional services

**🎯 You now have a professional release automation agent that reduces RC workload by 90%!**

---

## 📋 **Custom Templates Setup**

### **🎯 Template Structure**

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

### **📝 Supported Template Formats**

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

### **🔧 Variable Placeholders**

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
| `{rc_manager}` | `{{ rc_manager }}` | Release manager name |
| `{confluence_link}` | `{{ confluence_link }}` | Generated Confluence URL |
| `{p0_dashboard_url}` | `{{ p0_dashboard_url }}` | P0 dashboard URL |
| `{l1_dashboard_url}` | `{{ l1_dashboard_url }}` | L1 dashboard URL |
| `{services_dashboard_url}` | `{{ services_dashboard_url }}` | Services dashboard URL |

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

### **✅ Template Testing**

Test your custom template:

```bash
# Test external template download
python tests/test_external_template.py

# Test with your template
python main.py --test-mode --config-path config/settings.yaml

# Validate template conversion
python -c "
from crq.external_template import ExternalTemplateManager
from config.config import load_config
manager = ExternalTemplateManager(load_config())
result = manager.get_external_template()
print('✅ Template loaded successfully' if result else '❌ Template failed')
"
```

--- 