# 🚀 Slack Integration Testing Guide

**Complete guide to test the `/run-release` command and modal functionality**

This guide walks you through setting up and testing the Slack bot integration for the RC Release Automation system.

---

## 📋 Prerequisites

- ✅ Slack workspace admin access (to create apps)
- ✅ Python 3.10+ with all project dependencies installed
- ✅ RC Release Automation project set up locally

---

## 🛠️ Step 1: Slack App Setup

### 1.1 Create Slack App

1. **Go to Slack API:** https://api.slack.com/apps
2. **Create New App:** Click "Create New App" → "From scratch"
3. **App Details:**
   - Name: `RC Release Automation`
   - Workspace: Select your workspace
4. **Click "Create App"**

### 1.2 Configure Bot Permissions

1. **Go to "OAuth & Permissions"** in the left sidebar
2. **Add Bot Token Scopes:**
   ```
   chat:write          # Send messages
   commands            # Use slash commands  
   users:read          # Read user information
   reactions:write     # Add reactions to messages
   ```

### 1.3 Add Slash Command

1. **Go to "Slash Commands"** in the left sidebar
2. **Click "Create New Command"**
3. **Configure command:**
   ```
   Command: /run-release
   Request URL: https://your-bot-url.com/slack/events (or use ngrok for testing)
   Short Description: Start RC release process
   Usage Hint: [no parameters needed]
   ```

### 1.4 Enable Socket Mode (for Development)

1. **Go to "Socket Mode"** in the left sidebar
2. **Enable Socket Mode:** Toggle "Enable Socket Mode"
3. **Generate App-Level Token:**
   - Token Name: `rc-release-bot`
   - Add Scope: `connections:write`
   - Click "Generate"
   - **Save the token** (starts with `xapp-`)

### 1.5 Install App to Workspace

1. **Go to "Install App"** in the left sidebar
2. **Click "Install to Workspace"**
3. **Review permissions** and click "Allow"
4. **Copy tokens:**
   - **Bot User OAuth Token** (starts with `xoxb-`)
   - **Signing Secret** (from "Basic Information")
   - **App-Level Token** (from Socket Mode)

---

## 🔑 Step 2: Environment Configuration

### 2.1 Set Environment Variables

Create a `.env` file in your project root or set these environment variables:

```bash
export SLACK_BOT_TOKEN='xoxb-your-bot-token-here'
export SLACK_SIGNING_SECRET='your-signing-secret-here'
export SLACK_APP_TOKEN='xapp-your-app-level-token-here'
```

### 2.2 Verify Environment

```bash
# Check environment variables are set
echo $SLACK_BOT_TOKEN
echo $SLACK_SIGNING_SECRET  
echo $SLACK_APP_TOKEN
```

---

## 🧪 Step 3: Test Without Real Slack

Before connecting to Slack, test the modal structure and logic:

### 3.1 Test Modal Structure

```bash
python test_slack_modal.py --test-modal
```

**Expected Output:**
```
✅ Modal structure validation:
   - Title: 🚀 Start Release
   - Callback ID: release_modal
   - Input blocks: 6
   - Field 1: Service Name (ID: service_name)
   - Field 2: Production Version (ID: prod_version)
   - Field 3: New Version (ID: new_version)
   - Field 4: Day 1 Date (ID: day1_date)
   - Field 5: Day 2 Date (ID: day2_date)
   - Field 6: Release Manager (ID: rc_manager)
✅ Modal structure is valid
```

### 3.2 Test Workflow Logic

```bash
python test_slack_modal.py --test-workflow
```

**Expected Output:**
```
✅ Modal submission data extraction successful:
   - service_name: test-service
   - prod_version: v1.0.0
   - new_version: v1.1.0
   - day1_date: 2024-01-15
   - day2_date: 2024-01-16
   - rc_manager: U1234567890
   - channel_id: C1234567890
   - trigger_user: U1234567890
✅ All required fields present
✅ Version formats are valid
✅ Date formats are valid
✅ Complete modal workflow test passed
```

---

## 🔗 Step 4: Test Slack Authentication

### 4.1 Test Bot Authentication

```bash
python test_slack_modal.py --test-auth
```

**Expected Output (Success):**
```
✅ All 3 environment variables configured correctly
✅ Bot authenticated successfully:
   - Bot User: rc-release-bot
   - Bot ID: B1234567890
   - Team: Your Team Name
   - URL: https://yourteam.slack.com/
```

**Common Issues:**

❌ **Invalid token format:**
```
❌ SLACK_BOT_TOKEN must start with 'xoxb-'
```
**Solution:** Check your Bot User OAuth Token

❌ **Authentication failed:**
```
❌ Slack API error: invalid_auth
```
**Solution:** Verify your tokens are copied correctly

---

## 🤖 Step 5: Test Bot Integration

### 5.1 Test Complete Integration

```bash
python test_slack_modal.py --test-all
```

**Expected Output:**
```
🧪 Running comprehensive Slack modal tests...
✅ Environment Check: PASSED
✅ Authentication: PASSED  
✅ Modal Structure: PASSED
✅ Modal Workflow: PASSED
✅ Bot Integration: PASSED

📊 Test Results: 5/5 tests passed
🎉 All tests passed! Your Slack integration is ready.
```

---

## 🚀 Step 6: Start the Bot

### 6.1 Start Bot in Development Mode

```bash
cd slack_bot
python app.py
```

**Expected Output:**
```
[INFO] Starting RC Release Slack Bot...
[INFO] Socket Mode connection established
[INFO] Bot is running and listening for events
⚡️ Bolt app is running!
```

### 6.2 Test in Slack

1. **Go to your Slack workspace**
2. **In any channel, type:** `/run-release`
3. **The modal should appear with these fields:**
   - 📝 Service Name (text input)
   - 📝 Production Version (text input)  
   - 📝 New Version (text input)
   - 📅 Day 1 Date (date picker)
   - 📅 Day 2 Date (date picker)
   - 👤 Release Manager (user selector)

### 6.3 Test Modal Submission

1. **Fill out the modal:**
   ```
   Service Name: test-service
   Production Version: v1.0.0
   New Version: v1.1.0
   Day 1 Date: Tomorrow
   Day 2 Date: Day after tomorrow
   Release Manager: @yourself
   ```

2. **Click "Start Release"**

3. **Expected response:**
   ```
   🚀 Starting release process for *test-service v1.1.0*...
   
   Fetching PRs and generating documentation. This may take a moment.
   ```

---

## 📋 Step 7: Complete Workflow Test

### 7.1 Integration with Main System

The bot should trigger the main release automation system. Test this by:

1. **Setting up GitHub token:** `export GITHUB_TOKEN=your-token`
2. **Running the bot with real integration**
3. **Using `/run-release` in Slack**
4. **Verifying the bot calls the main automation system**

### 7.2 Expected Complete Flow

```
User types: /run-release
    ↓
Modal appears with release form
    ↓
User fills form and submits
    ↓
Bot posts confirmation message
    ↓
Bot triggers GitHub Actions or main.py
    ↓
Documentation gets generated
    ↓
Bot posts results back to Slack
```

---

## 🐛 Troubleshooting

### Common Issues

**❌ Modal doesn't appear:**
- Check `/run-release` command is properly configured in Slack app
- Verify Request URL is correct (use ngrok for local testing)
- Check bot has `commands` scope

**❌ "App not responding" error:**
- Bot server is not running or not reachable
- Check Socket Mode is enabled for development
- Verify App-Level Token has `connections:write` scope

**❌ Modal appears but submission fails:**
- Check bot has `chat:write` scope  
- Verify modal callback_id matches in code (`release_modal`)
- Check bot is handling `view` submissions

**❌ User selector doesn't work:**
- Bot needs `users:read` scope
- User must be in the same workspace as the bot

### Debug Mode

Run with debug logging:

```bash
export LOG_LEVEL=DEBUG
cd slack_bot
python app.py
```

### Test Individual Components

```bash
# Test just authentication
python test_slack_modal.py --test-auth

# Test just modal structure  
python test_slack_modal.py --test-modal

# Test just workflow logic
python test_slack_modal.py --test-workflow
```

---

## 🏢 Production Deployment

### For Production Use:

1. **Replace Socket Mode** with HTTP endpoints
2. **Use proper server** (not development server)
3. **Set up HTTPS** for Slack webhooks
4. **Configure proper logging**
5. **Add error handling and retries**
6. **Set up monitoring**

### Production Checklist:

- [ ] Bot tokens secured as environment variables
- [ ] HTTPS endpoint configured
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Rate limiting considered
- [ ] Monitoring set up
- [ ] Backup bot tokens available

---

## 📚 Additional Resources

- **Slack API Documentation:** https://api.slack.com/
- **Slack Bolt Framework:** https://slack.dev/bolt-python/
- **Socket Mode Guide:** https://api.slack.com/apis/connections/socket
- **Slack Modals Guide:** https://api.slack.com/surfaces/modals

---

## ✅ Success Criteria

Your Slack integration is working correctly when:

1. ✅ All tests pass (`python test_slack_modal.py --test-all`)
2. ✅ `/run-release` command shows the modal in Slack
3. ✅ Modal submits successfully and shows confirmation message
4. ✅ Bot integrates with the main release automation system
5. ✅ Generated documentation is accessible to users

**🎉 Once all criteria are met, your Slack bot is ready for production use!** 