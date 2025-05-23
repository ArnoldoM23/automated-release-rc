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

### **📋 Instant Demo**

```bash
# 1. Clone and install
git clone https://github.com/ArnoldoM23/automated-release-rc.git
cd automated-release-rc
pip install -r requirements.txt

# 2. See it in action - generates 4 professional documents in 30 seconds
python main.py --test-mode --service-name demo --prod-version v1.0.0 --new-version v1.1.0

# 3. Check your generated enterprise documentation
ls -la output/  # See release_notes.txt, crq_day1.txt, crq_day2.txt, release_notes.md
```

### **🚀 Complete Slack Workflow Setup**

**📖 [Follow our 5-Minute Setup Guide →](docs/quickstart.md)**

Get your **complete `/run-release` command** working in Slack:
- ✅ `/run-release` command in Slack (30-second form)
- ✅ Automatic GitHub Actions execution  
- ✅ Professional documentation generation
- ✅ Enterprise CRQ documents with AI insights
- ✅ Copy-paste ready Confluence markup

**⏱️ Setup:** 5 minutes • **Daily use:** 30 seconds • **Output:** 4 enterprise documents

### **🎯 What You'll Generate**

| File | Purpose | Size |
|------|---------|------|
| `release_notes.txt` | **Confluence-ready** wiki markup | 6,000+ bytes |
| `crq_day1.txt` | Day 1 preparation CRQ | 4,500+ bytes |
| `crq_day2.txt` | Day 2 deployment CRQ | 4,600+ bytes |
| `release_notes.md` | GitHub markdown | 2,500+ bytes |

---

## 🏢 **Core Features**

### **📋 Custom CRQ Templates**

The system supports **external CRQ templates** from multiple sources:
- **Microsoft Word** (.docx) - Corporate templates from SharePoint
- **Text files** (.txt) - Simple text-based templates  
- **Markdown** (.md) - GitHub-friendly templates

**✅ Template Features:**
- **Variable substitution** - Automatic placeholder replacement
- **Enterprise integration** - SharePoint, Confluence, file servers
- **Professional formatting** - Maintains corporate branding
- **Copy-paste ready** - No additional formatting needed

**📖 [Template Setup Guide →](docs/quickstart.md#custom-templates)**

### **🤖 Slack Bot Integration**

Transform your release process with intelligent Slack automation:

**Option 1: Slack Workflow Builder** ⭐ *Recommended*
- ✅ **5-minute setup** - No approvals needed
- ✅ **Zero infrastructure** - Uses GitHub Actions  
- ✅ **30-second releases** - Fill form, get documents

**Option 2: Advanced Slack Bot**
- ✅ **Interactive approvals** - Real-time collaboration
- ✅ **Enterprise features** - Advanced workflows
- ✅ **Custom integrations** - API access

**📖 [Slack Setup Guide →](docs/quickstart.md)**

### **📊 Professional Output**

Every release generates enterprise-ready documentation:

**🔗 Wiki Markup Release Notes**
- **Confluence-ready** formatting with professional markup
- **Copy-paste directly** into your organization's wiki
- **15+ sections** including impact analysis and rollback procedures
- **AI-enhanced content** with intelligent risk assessment

**📋 CRQ Documents**
- **Day 1 & Day 2** change request documents
- **AI-powered insights** and risk analysis
- **Complete implementation plans** with validation steps
- **Professional formatting** matching enterprise standards

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

#### **🔗 Wiki Markup Release Notes**

Our **Confluence-ready release notes** (`release_notes.txt`) are generated with professional wiki markup that you can **copy and paste directly** into your organization's wiki or documentation platform:

✅ **Ready-to-use formatting:**
- Structured headings with proper wiki syntax
- Bulleted PR lists with GitHub links  
- Categorized changes (Features, Bug Fixes, Schema Changes)
- Professional styling with emphasis and tables
- Sign-off sections for release approvals

✅ **Copy-paste workflow:**
```bash
# Generate release notes
python main.py --service-name your-service --prod-version v1.0.0 --new-version v1.1.0

# Copy the generated content
cat output/release_notes.txt | pbcopy  # macOS
cat output/release_notes.txt | xclip   # Linux

# Paste directly into Confluence, Notion, or your wiki platform
```

✅ **Enterprise-grade content:**
- **15+ sections** including summary, impact analysis, rollback procedures
- **AI-enhanced descriptions** with intelligent risk assessment
- **Professional formatting** matching corporate documentation standards
- **Complete traceability** with PR links and contributor attribution

---

## 🔧 **Local Development Setup**

For developers who want to run the tool locally or integrate it into CI/CD pipelines:

### **🔑 Quick Local Setup**

```bash
# 1. Clone and configure
git clone https://github.com/ArnoldoM23/automated-release-rc.git
cd automated-release-rc
cp config/settings.example.yaml config/settings.yaml

# 2. Set environment variables
export GITHUB_TOKEN="ghp_your-token-here"
export OPENAI_API_KEY="sk_your-key-here"  # Optional

# 3. Generate release documentation
python main.py --service-name your-service --prod-version v1.0.0 --new-version v1.1.0
```

### **📖 Detailed Setup Documentation**

| Guide | Purpose |
|-------|---------|
| **[📖 Complete Setup Guide](docs/quickstart.md)** | Full Slack workflow + local setup |
| **[🔧 Configuration Guide](#configuration-setup)** | YAML configuration details |
| **[🐙 GitHub Integration](#github-authentication-setup)** | Token setup and repository access |
| **[📋 Custom Templates](#creating-custom-crq-templates)** | Organization-specific templates |

### **🎯 Version Reference Support**

Works with both **Git tags** and **commit SHAs**:
- **Git Tags:** `v1.2.3`, `1.0.0` (standard releases)
- **Commit SHAs:** `abc123f`, `9f8e7d6c` (hotfixes, precise control)
- **Mixed usage:** `v1.0.0` → `def456a` (flexible workflows)