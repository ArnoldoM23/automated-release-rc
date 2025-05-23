# 🤖 Release RC Slack Bot

**Enterprise Slack Bot for PR Sign-off Tracking and Release Coordination**

The Release RC bot manages PR sign-off workflows, sends periodic reminders, tracks developer approvals, and handles cut-off logic for release coordination.

---

## 🚀 **Quick Start**

### **1. Local Development**

```bash
# Clone the repository
git clone https://github.com/your-org/automated-release-rc.git
cd automated-release-rc

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_APP_TOKEN="xapp-your-app-token"

# Run the bot
python -m slack_bot.app
```

### **2. Docker Deployment**

```bash
# Create .env file with your Slack credentials
echo "SLACK_BOT_TOKEN=xoxb-your-token" > .env
echo "SLACK_APP_TOKEN=xapp-your-token" >> .env

# Run with Docker Compose
docker-compose up -d

# Check health
curl http://localhost:5000/health
```

---

## 🔧 **Slack App Setup**

### **Step 1: Create Slack App**

1. Go to [Slack API](https://api.slack.com/apps)
2. Click **"Create New App"** → **"From scratch"**
3. Name: `Release RC Bot`
4. Select your workspace

### **Step 2: Configure Bot Permissions**

In **OAuth & Permissions**, add these **Bot Token Scopes**:
- `app_mentions:read` - Listen for mentions
- `channels:history` - Read channel messages
- `channels:read` - View channel info
- `chat:write` - Send messages
- `reactions:write` - Add reactions
- `users:read` - Read user info
- `im:history` - Read DM history
- `mpim:history` - Read group DM history

### **Step 3: Enable Socket Mode**

1. Go to **Socket Mode** in your app settings
2. **Enable Socket Mode**
3. Create an **App-Level Token** with `connections:write` scope
4. Copy the token (starts with `xapp-`)

### **Step 4: Subscribe to Events**

In **Event Subscriptions**:
1. **Enable Events**
2. Subscribe to **Bot Events**:
   - `message.channels`
   - `message.groups`
   - `message.im`
   - `message.mpim`
   - `app_mention`

### **Step 5: Install App**

1. Go to **Install App**
2. Click **"Install to Workspace"**
3. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

---

## ⚙️ **Configuration**

### **Environment Variables**

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SLACK_BOT_TOKEN` | ✅ | Bot User OAuth Token | `xoxb-123-456-abc` |
| `SLACK_APP_TOKEN` | ✅ | App-Level Token | `xapp-1-A123-456-def` |
| `SLACK_SIGNING_SECRET` | ❌ | For webhook verification | `abc123def456` |
| `REMINDER_INTERVAL_HOURS` | ❌ | Reminder frequency | `2` (default) |
| `RELEASE_CHANNEL` | ❌ | Default channel | `#release-rc` |
| `TIMEZONE` | ❌ | Bot timezone | `America/Los_Angeles` |
| `HOST` | ❌ | Server host | `0.0.0.0` |
| `PORT` | ❌ | Server port | `5000` |

### **Example .env File**

```bash
# Required Slack credentials
SLACK_BOT_TOKEN=xoxb-1234567890-1234567890123-abcdefghijklmnopqrstuvwx
SLACK_APP_TOKEN=xapp-1-A1234567890-1234567890123-abcdefghijklmnopqrstuvwxyz123456

# Optional configuration
REMINDER_INTERVAL_HOURS=2
RELEASE_CHANNEL=#release-rc
TIMEZONE=America/Los_Angeles
DEBUG=false
```

---

## 🎯 **Bot Commands**

### **Release Sign-off Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `@release_rc signed off` | Mark your PRs as signed off | `@release_rc signed off` |
| `@release_rc signoff` | Alternative sign-off command | `@release_rc signoff` |
| `@release_rc status` | Show current sign-off status | `@release_rc status` |
| `@release_rc abort` | Abort the release workflow | `@release_rc abort` |

### **Bot Responses**

**Sign-off Success:**
```
✅ @username signed off! Thank you.
```

**Status Update:**
```
📊 Sign-off Status for service-name v1.2.0

Completed:
• ✅ @alice — PR #123
• ✅ @bob — PR #124

Pending:
• ❌ @charlie — PR #125

⏰ Cutoff: 12:00 PM tomorrow
```

**All Signed Off:**
```
🎉 All PRs signed off early!

All developers have signed off on their PRs for service-name v1.2.0.

@release-manager the release is ready to proceed ahead of schedule!
```

---

## 📋 **Workflow Example**

### **1. Release Triggered (from GitHub Actions)**

**Initial Announcement:**
```
Hi team! 🚀

Release *cer-cart v2.5.0* is scheduled for:
• Day 1 (prep): 2024-01-15
• Day 2 (deploy): 2024-01-16

Please sign off on your PRs by *12:00 PM tomorrow*:

• ❌ @alice — PR #123: Add payment validation
• ❌ @bob — PR #124: Fix cart calculation bug
• ❌ @charlie — PR #125: Update GraphQL schema

To sign off, reply in this thread: `@release_rc signed off`
For status: `@release_rc status`
To abort: `@release_rc abort`

Release Coordinator: @release-manager
```

### **2. Developer Signs Off**

```
alice: @release_rc signed off
```

**Bot Response:**
```
✅ @alice signed off! Thank you.
```

### **3. Periodic Reminders (every 2 hours)**

```
📢 Friendly reminder to sign off by *12:00 PM tomorrow*:

• @bob
• @charlie

Reply: `@release_rc signed off`
```

### **4. Cut-off Time Reached**

**If all signed off:**
```
🎉 All PRs signed off! Ready for CRQ review.

Release *cer-cart v2.5.0* is ready to proceed.

@release-manager please proceed with the release process.
```

**If some pending:**
```
⚠️ Sign-off incomplete

The following developers have not signed off by the cutoff time:
• @charlie

Their changes will be removed from the release branch.

@release-manager please review and proceed accordingly.
```

---

## 🚀 **Deployment Options**

### **Option 1: Heroku**

```bash
# Create Heroku app
heroku create release-rc-bot

# Set environment variables
heroku config:set SLACK_BOT_TOKEN=xoxb-your-token
heroku config:set SLACK_APP_TOKEN=xapp-your-token

# Deploy
git push heroku main

# Check logs
heroku logs --tail
```

### **Option 2: Railway**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway add
railway up

# Set environment variables in Railway dashboard
```

### **Option 3: Docker on VPS**

```bash
# Pull and run
docker pull your-org/release-rc-bot:latest

docker run -d \
  --name release-rc-bot \
  -p 5000:5000 \
  -e SLACK_BOT_TOKEN=xoxb-your-token \
  -e SLACK_APP_TOKEN=xapp-your-token \
  your-org/release-rc-bot:latest
```

### **Option 4: Kubernetes**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: release-rc-bot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: release-rc-bot
  template:
    metadata:
      labels:
        app: release-rc-bot
    spec:
      containers:
      - name: bot
        image: your-org/release-rc-bot:latest
        ports:
        - containerPort: 5000
        env:
        - name: SLACK_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: slack-secrets
              key: bot-token
        - name: SLACK_APP_TOKEN
          valueFrom:
            secretKeyRef:
              name: slack-secrets
              key: app-token
```

---

## 🔗 **GitHub Actions Integration**

The bot integrates with your existing GitHub Actions workflow:

### **Updated GitHub Workflow**

```yaml
# .github/workflows/run_release.yml
- name: Trigger Slack Sign-off
  if: env.SLACK_BOT_URL != ''
  run: |
    python -m slack_bot.integration pr_data.json release_metadata.json
  env:
    SLACK_BOT_URL: ${{ secrets.SLACK_BOT_URL }}
    SLACK_BOT_API_KEY: ${{ secrets.SLACK_BOT_API_KEY }}
```

### **Required GitHub Secrets**

Add these to your repository secrets:

- `SLACK_BOT_URL` - URL where your bot is deployed (e.g., `https://your-bot.herokuapp.com`)
- `SLACK_BOT_API_KEY` - API key for securing bot endpoints

---

## 🧪 **Testing**

### **Local Testing**

```bash
# Test bot functionality
python -m pytest slack_bot/tests/

# Test integration
python slack_bot/integration.py test_data/prs.json test_data/release.json

# Test server endpoints
curl http://localhost:5000/health
curl -X POST http://localhost:5000/api/release -d '{"action":"start_release_session",...}'
```

### **Mock Data Testing**

```bash
# Create test PR data
echo '[
  {
    "number": 123,
    "html_url": "https://github.com/org/repo/pull/123",
    "title": "Test PR",
    "user": {"login": "testuser"},
    "labels": []
  }
]' > test_prs.json

# Test integration
python slack_bot/integration.py test_prs.json
```

---

## 📊 **Monitoring & Health Checks**

### **Health Endpoint**

```bash
curl http://localhost:5000/health

# Response:
{
  "status": "healthy",
  "bot": "release_rc",
  "version": "1.0.0"
}
```

### **Active Sessions**

```bash
curl http://localhost:5000/api/sessions

# Response:
{
  "success": true,
  "sessions": [
    {
      "thread_ts": "1234567890.123456",
      "service": "cer-cart",
      "version": "v2.5.0",
      "pending_count": 2,
      "total_prs": 5,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

## 🔒 **Security**

### **API Security**

- All endpoints require valid API key in `Authorization` header
- Slack signature verification for webhook security
- No sensitive data logged
- Environment variables for all credentials

### **Best Practices**

1. **Use HTTPS** for all deployments
2. **Rotate tokens** regularly
3. **Monitor bot activity** in Slack audit logs
4. **Set up alerts** for bot failures
5. **Use secrets management** for credentials

---

## 🛠️ **Troubleshooting**

### **Common Issues**

**Bot not responding:**
- Check `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN`
- Verify bot is installed in workspace
- Check bot permissions and scopes

**Commands not working:**
- Ensure bot is mentioned with `@release_rc`
- Commands must be in release thread
- Check bot has necessary permissions

**Reminders not sent:**
- Verify APScheduler is running
- Check timezone configuration
- Look for errors in bot logs

**GitHub integration failed:**
- Check `SLACK_BOT_URL` is accessible
- Verify `SLACK_BOT_API_KEY` matches
- Test API endpoint manually

### **Debug Mode**

```bash
# Run with debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG
python -m slack_bot.server
```

### **Logs**

```bash
# Docker logs
docker logs release-rc-bot

# Heroku logs
heroku logs --tail --app release-rc-bot

# Check specific errors
grep ERROR /var/log/release-rc-bot.log
```

---

## 🤝 **Contributing**

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/bot-enhancement`
3. **Make changes** and add tests
4. **Run tests**: `pytest slack_bot/tests/`
5. **Submit pull request**

### **Development Setup**

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests with coverage
pytest --cov=slack_bot

# Format code
black slack_bot/
flake8 slack_bot/
```

---

## 📄 **License**

MIT License - Free for commercial and personal use.

**Built with ❤️ for Release Engineering teams** 