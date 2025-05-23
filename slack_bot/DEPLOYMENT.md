# 🚀 Release RC Slack Bot - Deployment Guide

**Complete guide for deploying the Release RC Slack bot for enterprise PR sign-off workflows**

---

## 📋 **Overview**

The Release RC Slack bot provides:
- **`/run-release` slash command** - Start releases directly from Slack
- **Interactive sign-off tracking** - Developers sign off with `@release_rc signed off`
- **Periodic reminders** - Automatic reminders every 2 hours
- **Cut-off handling** - Escalation when deadlines are missed
- **GitHub Actions integration** - Seamless workflow triggers

---

## 🎯 **Quick Deployment Options**

### **Option 1: Heroku (Fastest)**
```bash
# 1. Deploy to Heroku
git clone https://github.com/your-org/automated-release-rc.git
cd automated-release-rc
heroku create your-release-bot

# 2. Set environment variables
heroku config:set SLACK_BOT_TOKEN=xoxb-your-token
heroku config:set SLACK_APP_TOKEN=xapp-your-token

# 3. Deploy
git push heroku main

# 4. Get bot URL
heroku info | grep "Web URL"
```

### **Option 2: Railway**
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Deploy
railway login
railway init
railway add --service slack-bot
railway up

# 3. Set environment variables in Railway dashboard
```

### **Option 3: Docker**
```bash
# 1. Build and run
cd slack_bot
docker build -t release-rc-bot .
docker run -d -p 5000:5000 \
  -e SLACK_BOT_TOKEN=xoxb-your-token \
  -e SLACK_APP_TOKEN=xapp-your-token \
  release-rc-bot
```

---

## 🔧 **Detailed Setup Guide**

### **Step 1: Create Slack App**

1. **Go to [Slack API](https://api.slack.com/apps)**
2. **Click "Create New App" → "From scratch"**
3. **Name:** `Release RC Bot`
4. **Select your workspace**

### **Step 2: Configure Bot Permissions**

In **OAuth & Permissions**, add these **Bot Token Scopes**:

| Scope | Purpose |
|-------|---------|
| `app_mentions:read` | Listen for @release_rc mentions |
| `channels:history` | Read channel messages |
| `channels:read` | View channel information |
| `chat:write` | Send messages and replies |
| `commands` | Handle slash commands |
| `reactions:write` | Add checkmark reactions |
| `users:read` | Get user information |

### **Step 3: Create Slash Command**

1. **Go to "Slash Commands"**
2. **Click "Create New Command"**
3. **Command:** `/run-release`
4. **Request URL:** `https://your-bot.herokuapp.com/slack/events`
5. **Short Description:** `Start a release workflow`
6. **Usage Hint:** `[service] [version]`

### **Step 4: Enable Socket Mode**

1. **Go to "Socket Mode"**
2. **Enable Socket Mode**
3. **Create App-Level Token:**
   - Name: `Release RC Socket Token`
   - Scopes: `connections:write`
   - Copy token (starts with `xapp-`)

### **Step 5: Subscribe to Events**

In **Event Subscriptions**:
1. **Enable Events**
2. **Subscribe to Bot Events:**
   - `message.channels`
   - `message.groups`
   - `message.im`
   - `message.mpim`
   - `app_mention`

### **Step 6: Install App**

1. **Go to "Install App"**
2. **Click "Install to Workspace"**
3. **Copy Bot User OAuth Token** (starts with `xoxb-`)

---

## ⚙️ **Environment Configuration**

### **Required Variables**

```bash
# Slack credentials
SLACK_BOT_TOKEN=xoxb-1234567890-1234567890123-abcdefghijklmnopqrstuvwx
SLACK_APP_TOKEN=xapp-1-A1234567890-1234567890123-abcdefghijklmnopqrstuvwxyz123456

# Bot configuration
REMINDER_INTERVAL_HOURS=2
RELEASE_CHANNEL=#release-rc
TIMEZONE=America/Los_Angeles

# Server settings
HOST=0.0.0.0
PORT=5000
DEBUG=false

# External integrations (optional)
GITHUB_TOKEN=ghp_your_github_token
SLACK_BOT_URL=https://your-bot.herokuapp.com
SLACK_BOT_API_KEY=your_api_key

# Deployment
DEPLOYMENT_MODE=production
LOG_LEVEL=INFO
```

### **GitHub Secrets for Integration**

Add these to your GitHub repository secrets:

| Secret | Value | Purpose |
|--------|-------|---------|
| `SLACK_BOT_URL` | `https://your-bot.herokuapp.com` | Bot endpoint URL |
| `SLACK_BOT_API_KEY` | Random secure string | API authentication |

---

## 🚀 **Platform-Specific Deployment**

### **Heroku Deployment**

```bash
# 1. Create Heroku app
heroku create your-release-bot

# 2. Add buildpack
heroku buildpacks:set heroku/python

# 3. Set environment variables
heroku config:set SLACK_BOT_TOKEN=xoxb-your-token
heroku config:set SLACK_APP_TOKEN=xapp-your-token
heroku config:set REMINDER_INTERVAL_HOURS=2
heroku config:set RELEASE_CHANNEL=#release-rc
heroku config:set DEPLOYMENT_MODE=production

# 4. Deploy
git add .
git commit -m "Deploy Release RC bot"
git push heroku main

# 5. Verify deployment
heroku logs --tail
curl https://your-release-bot.herokuapp.com/health
```

### **Railway Deployment**

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login and initialize
railway login
railway init

# 3. Create service
railway add --service slack-bot

# 4. Deploy
railway up

# 5. Set environment variables
# Go to Railway dashboard and add all required variables

# 6. Get deployment URL
railway status
```

### **Docker Deployment**

#### **Build & Run Locally**
```bash
cd slack_bot
docker build -t release-rc-bot .

docker run -d --name release-rc-bot \
  -p 5000:5000 \
  -e SLACK_BOT_TOKEN=xoxb-your-token \
  -e SLACK_APP_TOKEN=xapp-your-token \
  -e REMINDER_INTERVAL_HOURS=2 \
  -e RELEASE_CHANNEL=#release-rc \
  release-rc-bot
```

#### **Docker Compose**
```yaml
# slack_bot/docker-compose.yml
version: '3.8'
services:
  release-rc-bot:
    build: .
    ports:
      - "5000:5000"
    environment:
      - SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
      - SLACK_APP_TOKEN=${SLACK_APP_TOKEN}
      - REMINDER_INTERVAL_HOURS=2
      - RELEASE_CHANNEL=#release-rc
      - DEPLOYMENT_MODE=production
    restart: unless-stopped
```

#### **Production with Redis**
```bash
# Run with Redis for persistence
docker-compose --profile with-redis up -d
```

### **AWS/GCP/Azure Deployment**

#### **AWS Lambda**
```bash
# Install serverless framework
npm install -g serverless

# Deploy to Lambda
serverless create --template aws-python3 --path release-rc-lambda
cd release-rc-lambda
# Configure serverless.yml and deploy
serverless deploy
```

#### **Google Cloud Run**
```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/PROJECT-ID/release-rc-bot
gcloud run deploy --image gcr.io/PROJECT-ID/release-rc-bot --platform managed
```

#### **Azure Container Instances**
```bash
# Deploy to Azure
az container create \
  --resource-group myResourceGroup \
  --name release-rc-bot \
  --image your-registry/release-rc-bot \
  --dns-name-label release-rc-bot \
  --ports 5000
```

---

## 🔗 **GitHub Actions Integration**

### **Update Workflow**

Add to your `.github/workflows/run_release.yml`:

```yaml
- name: 🤖 Trigger Slack Sign-off Workflow
  if: env.SLACK_BOT_URL != ''
  env:
    SLACK_BOT_URL: ${{ secrets.SLACK_BOT_URL }}
    SLACK_BOT_API_KEY: ${{ secrets.SLACK_BOT_API_KEY }}
  run: |
    python -m slack_bot.integration pr_data.json release_metadata.json
```

### **Repository Secrets**

Add these secrets to your GitHub repository:

1. **Go to GitHub repository → Settings → Secrets → Actions**
2. **Add new repository secrets:**
   - `SLACK_BOT_URL`: Your deployed bot URL
   - `SLACK_BOT_API_KEY`: Secure API key for authentication

---

## 🧪 **Testing & Validation**

### **Local Testing**

```bash
# 1. Test bot components
python slack_bot/test_bot.py

# 2. Test integration
python -m slack_bot.integration test_data/sample_prs.json test_data/sample_metadata.json

# 3. Test server endpoints
curl http://localhost:5000/health
curl -X POST http://localhost:5000/api/release \
  -H "Content-Type: application/json" \
  -d '{"action":"start_release_session","prs":[],"release_metadata":{}}'
```

### **Production Testing**

```bash
# 1. Health check
curl https://your-bot.herokuapp.com/health

# 2. Test slash command
# In Slack: /run-release

# 3. Test integration
# Trigger a GitHub Actions workflow

# 4. Monitor logs
heroku logs --tail --app your-release-bot
```

---

## 📊 **Monitoring & Maintenance**

### **Health Monitoring**

Set up monitoring for:
- **Health endpoint:** `GET /health`
- **Active sessions:** `GET /api/sessions`
- **Bot response time**
- **Error rates**

### **Log Analysis**

```bash
# Heroku logs
heroku logs --tail --app your-bot

# Docker logs
docker logs release-rc-bot

# Railway logs
railway logs
```

### **Performance Optimization**

1. **Scale workers** for high-traffic workspaces
2. **Add Redis** for session persistence
3. **Configure CDN** for static assets
4. **Set up auto-scaling** based on usage

---

## 🔒 **Security Best Practices**

### **Token Security**
- ✅ Store tokens in environment variables
- ✅ Use secrets management (Heroku Config, Railway Variables)
- ✅ Rotate tokens regularly
- ✅ Monitor token usage in Slack audit logs

### **API Security**
- ✅ Use HTTPS for all endpoints
- ✅ Validate API key for webhook endpoints
- ✅ Rate limit API calls
- ✅ Log security events

### **Network Security**
- ✅ Restrict inbound traffic to necessary ports
- ✅ Use firewall rules for production deployments
- ✅ Enable CORS protection
- ✅ Monitor for suspicious activity

---

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **Bot Not Responding**
```bash
# Check bot token
curl -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  https://slack.com/api/auth.test

# Verify bot permissions
# Check OAuth & Permissions in Slack app settings

# Test Socket Mode connection
# Verify SLACK_APP_TOKEN is correct
```

#### **Slash Command Not Working**
```bash
# Verify command registration
# Check Slash Commands in Slack app settings

# Test request URL
curl -X POST https://your-bot.herokuapp.com/slack/events \
  -H "Content-Type: application/json" \
  -d '{"type":"url_verification","challenge":"test"}'
```

#### **Integration Failures**
```bash
# Test GitHub Actions integration
python -m slack_bot.integration test_data/sample_prs.json

# Check GitHub secrets
# Verify SLACK_BOT_URL and SLACK_BOT_API_KEY

# Monitor workflow logs
# Check GitHub Actions workflow run logs
```

### **Debug Mode**

```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run with debug output
python -m slack_bot.server
```

---

## 📈 **Scaling for Enterprise**

### **Multi-Workspace Support**

```python
# Configure multiple workspace tokens
SLACK_BOT_TOKENS = {
    "workspace1": "xoxb-token1",
    "workspace2": "xoxb-token2"
}
```

### **Database Integration**

```python
# Add PostgreSQL for session persistence
DATABASE_URL = "postgresql://user:pass@host:port/db"
```

### **Load Balancing**

```yaml
# kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: release-rc-bot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: release-rc-bot
```

---

## 🎉 **Success Metrics**

Track these metrics for success:

| Metric | Target | Tool |
|--------|--------|------|
| **Bot Uptime** | 99.9% | Health checks |
| **Response Time** | < 2s | Application monitoring |
| **Sign-off Rate** | > 90% | Bot analytics |
| **User Adoption** | Team-wide | Slack analytics |
| **Release Cycle Time** | Reduced by 50% | Process metrics |

---

## 🆘 **Support & Help**

### **Documentation**
- 📖 [Bot README](README.md) - Complete user guide
- 🔧 [Configuration Guide](../docs/configuration.md) - Detailed configuration
- 🐛 [GitHub Issues](https://github.com/your-org/automated-release-rc/issues) - Bug reports

### **Community**
- 💬 [GitHub Discussions](https://github.com/your-org/automated-release-rc/discussions) - Community help
- 📺 [Demo Videos](https://your-org.github.io/demos) - Video tutorials
- 📧 [Support Email](mailto:support@your-org.com) - Direct support

---

**🎯 Ready to deploy? Choose your platform and follow the guide above!**

**Built with ❤️ for Release Engineering teams everywhere** 