# Sign-Off Bot Deployment Guide

This guide covers deploying the persistent Slack bot for real-time sign-off tracking. The bot works alongside the GitHub Actions workflow for complete release automation.

## 🎯 Overview

The sign-off bot provides:
- **Real-time message updates** when developers sign off
- **Live status tracking** with ✅/❌ indicators  
- **Completion notifications** when all PRs are signed off
- **Status commands** to check active releases

## 🚀 Deployment Options

### Option A: Railway (Recommended)

Railway offers the easiest deployment with automatic SSL and custom domains.

```bash
# 1. Go to railway.app and connect your GitHub repo
# 2. Create new project from your forked repo
# 3. Select "Deploy from GitHub repo"
# 4. Railway will auto-detect Python and use signoff_bot.py

# 5. Set environment variables in Railway dashboard:
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
PORT=3000

# 6. Deploy and copy the generated URL (e.g., your-bot.railway.app)
```

**Benefits:**
- ✅ Free tier available
- ✅ Automatic HTTPS
- ✅ Easy GitHub integration
- ✅ Environment variable management

### Option B: Heroku

Heroku provides reliable hosting with good documentation.

```bash
# 1. Install Heroku CLI
# 2. Create new Heroku app
heroku create your-signoff-bot

# 3. Set environment variables
heroku config:set SLACK_BOT_TOKEN=xoxb-your-bot-token
heroku config:set SLACK_SIGNING_SECRET=your-signing-secret

# 4. Create Procfile
echo "web: python signoff_bot.py" > Procfile

# 5. Deploy
git add .
git commit -m "Deploy sign-off bot"
git push heroku main

# 6. Copy app URL (e.g., your-signoff-bot.herokuapp.com)
```

### Option C: Local Development

For testing and development purposes.

```bash
# 1. Clone repository and install dependencies
git clone your-forked-repo
cd automated-release-rc
pip install -r requirements.txt

# 2. Set environment variables
export SLACK_BOT_TOKEN=xoxb-your-bot-token
export SLACK_SIGNING_SECRET=your-signing-secret
export PORT=3000

# 3. Run bot locally
python signoff_bot.py

# 4. Use ngrok for webhook URL (development only)
ngrok http 3000
# Copy the HTTPS URL for Slack app configuration
```

## 🔧 Slack App Configuration

### 1. Create Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name: "Release Sign-Off Bot"
4. Select your workspace

### 2. Configure Bot Permissions

Add these OAuth scopes in **OAuth & Permissions**:

```
chat:write        # Post messages
chat:write.public # Post in public channels
app_mentions:read # Listen for mentions
commands          # Slash commands
```

### 3. Enable Events

In **Event Subscriptions**:
1. Turn on "Enable Events"
2. Set Request URL: `https://your-deployed-bot.com/slack/events`
3. Subscribe to these bot events:
   - `app_mention`
   - `message.channels` (if needed)

### 4. Add Slash Commands

In **Slash Commands**, add:
- Command: `/release-status`
- Request URL: `https://your-deployed-bot.com/slack/commands`
- Description: "Check active release sign-off status"

### 5. Install App

1. Go to **Install App** section
2. Click "Install to Workspace"
3. Copy the **Bot User OAuth Token** (starts with `xoxb-`)
4. Copy the **Signing Secret** from **Basic Information**

## 🔗 Integration with GitHub Actions

The GitHub Actions workflow automatically triggers the sign-off bot:

```yaml
# In .github/workflows/run_release.yml
- name: Post Sign-Off Message
  run: |
    curl -X POST "${{ secrets.SIGNOFF_BOT_URL }}/slack/messages" \
      -H "Content-Type: application/json" \
      -d '{
        "channel": "${{ github.event.client_payload.channel }}",
        "text": "create-signoff {\"service_name\":\"${{ github.event.client_payload.service_name }}\",\"new_version\":\"${{ github.event.client_payload.new_version }}\",\"prs\":${{ toJSON(steps.fetch-prs.outputs.prs) }}}"
      }'
```

## 🧪 Testing Your Deployment

### 1. Health Check

```bash
curl https://your-deployed-bot.com/health
# Should return: {"status": "healthy", "active_releases": 0}
```

### 2. Slack Integration Test

1. Invite the bot to a test channel: `/invite @Release Sign-Off Bot`
2. Manually create a test sign-off message
3. Mention the bot with "done" to test real-time updates
4. Run `/release-status` to check the slash command

### 3. End-to-End Test

1. Run `/run-release` in Slack (triggers GitHub Actions)
2. Verify sign-off message appears
3. Reply with "done" to test sign-off tracking
4. Confirm message updates in real-time

## 🔒 Security Considerations

### Environment Variables
- Store all secrets in your deployment platform's environment variables
- Never commit tokens to version control
- Use different tokens for development and production

### Network Security
- Bot endpoint should use HTTPS (automatic with Railway/Heroku)
- Slack signing secret validates requests are from Slack
- Consider IP allowlisting if your platform supports it

### Access Control
- Bot only responds to mentions in channels where it's invited
- Only tracks releases initiated through proper workflow
- Automatic cleanup of completed releases

## 📊 Monitoring & Troubleshooting

### Logs
```bash
# Railway: View in dashboard
# Heroku: 
heroku logs --tail --app your-signoff-bot

# Local:
python signoff_bot.py  # Logs to console
```

### Common Issues

**Bot not responding to mentions:**
- Check bot is invited to the channel
- Verify SLACK_BOT_TOKEN is correct
- Check Event Subscriptions URL is set

**Sign-off message not updating:**
- Verify app has `chat:write` permissions
- Check bot user ID matches the mention format
- Review logs for API errors

**Slash command not working:**
- Confirm `/release-status` is configured in Slack app
- Verify Request URL points to your bot
- Check command response in logs

## 🚀 Production Deployment

### Scaling Considerations
- Single instance handles typical team usage (< 100 users)
- For large organizations, consider Redis for state persistence
- Monitor memory usage for long-running releases

### Backup & Recovery
- State is in-memory by default (releases clean up automatically)
- For persistence, add Redis and modify `active_releases` storage
- Bot restarts cleanly without data loss for short outages

### Monitoring
- Use deployment platform monitoring (Railway/Heroku dashboards)
- Set up alerts for bot downtime
- Monitor Slack API rate limits (rare with typical usage)

---

**🎯 Goal: Lightweight, reliable sign-off tracking that enhances the GitHub Actions workflow without adding complexity.** 