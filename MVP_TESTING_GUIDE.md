# MVP Testing Guide

This guide helps you test the RC Release Automation MVP before deploying to production.

## 🎯 Overview

We've created two separate testing scripts to validate functionality:

1. **`test_cli.py`** - Tests core document generation functionality
2. **`test_slack_bot.py`** - Tests Slack bot sign-off functionality

## 📋 Prerequisites

### Environment Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**
   ```bash
   # Copy example config
   cp config/settings.example.yaml config/settings.yaml
   
   # Edit with your settings
   nano config/settings.yaml
   ```

3. **Environment Variables**
   ```bash
   # Required for GitHub integration
   export GITHUB_TOKEN="your-github-token"
   
   # Required for AI features
   export OPENAI_API_KEY="your-openai-api-key"
   
   # Required for Slack bot testing
   export SLACK_BOT_TOKEN="xoxb-your-slack-bot-token"
   export SLACK_SIGNING_SECRET="your-slack-signing-secret"
   ```

## 🧪 Core Functionality Testing

### Test All Components

```bash
# Run comprehensive test suite
python test_cli.py --test-all

# Test with custom parameters
python test_cli.py --test-all \
  --service-name "cer-cart" \
  --prod-version "v1.2.3" \
  --new-version "v1.3.0" \
  --rc-name "John Doe" \
  --rc-manager "Jane Smith"
```

### Individual Component Tests

```bash
# Test configuration loading
python test_cli.py --test-config

# Test GitHub PR fetching
python test_cli.py --test-prs --prod-version v1.2.3 --new-version v1.3.0

# Test document generation (uses mock data if no GitHub token)
python test_cli.py --test-docs

# Test AI integration
python test_cli.py --test-ai
```

### Expected Output

When running `--test-all`, you should see:

```
🧪 RC Release Automation - MVP Testing
==================================================
Service: cer-cart v1.2.3 → v1.3.0
RC: Test RC | Manager: Test Manager
Dates: 2024-01-15 (Day 1) | 2024-01-16 (Day 2)
==================================================

🔧 Testing configuration loading...
✅ Configuration loaded successfully
✅ github section present
✅ ai section present
✅ organization section present

🤖 Testing AI integration...
✅ AI integration successful (response: 156 chars)

🐙 Testing GitHub integration...
✅ GitHub integration successful: 5 PRs fetched

📝 Testing release notes generation...
✅ Confluence release notes: test_outputs/release_notes.txt
✅ Markdown release notes: test_outputs/release_notes.md

📋 Testing CRQ generation...
✅ CRQ generation successful: 2 files
✅ crq_day1.txt generated successfully (8234 bytes)
✅ crq_day2.txt generated successfully (9156 bytes)

🎯 Test Results Summary:
  config         : ✅ PASS
  ai             : ✅ PASS
  github         : ✅ PASS
  release_notes  : ✅ PASS
  crq            : ✅ PASS

📊 Overall: 5/5 tests passed
🎉 All tests passed! MVP is ready for deployment.
```

### Generated Files

After testing, check the `test_outputs/` directory:

```bash
ls -la test_outputs/
# Should contain:
# - release_notes.txt (Confluence format)
# - release_notes.md (Markdown format)
# - crq_day1.txt (Day 1 CRQ document)
# - crq_day2.txt (Day 2 CRQ document)
```

## 🤖 Slack Bot Testing

### Test All Bot Functions

```bash
# Run comprehensive bot test suite
python test_slack_bot.py --test-bot
```

### Individual Bot Tests

```bash
# Test Slack credentials
python test_slack_bot.py --test-credentials

# Test release tracking logic
python test_slack_bot.py --test-tracker

# Test message formatting
python test_slack_bot.py --test-message

# Run mock sign-off workflow
python test_slack_bot.py --mock-signoff
```

### Expected Bot Test Output

```
🤖 Slack Bot Testing Suite
========================================

📦 Testing Slack library imports...
✅ slack_bolt imported successfully
✅ slack_sdk imported successfully

🔐 Testing Slack credentials...
✅ SLACK_BOT_TOKEN is set
✅ SLACK_SIGNING_SECRET is set

🤖 Testing ReleaseTracker class...
✅ Release added: cer-cart-v1.3.0
✅ Release retrieved: cer-cart
✅ Signoff added for user1
✅ Signoff added for user2
✅ Signoff added for user3
✅ ReleaseTracker functionality working correctly

🎯 Slack Bot Test Results:
  imports        : ✅ PASS
  credentials    : ✅ PASS
  tracker        : ✅ PASS
  formatting     : ✅ PASS
  slack          : ✅ PASS
  workflow       : ✅ PASS

📊 Overall: 6/6 tests passed
🎉 All Slack bot tests passed! Bot is ready for deployment.
```

## 🔧 Troubleshooting

### Common Issues

**1. Configuration Errors**
```bash
# Error: Configuration file not found
cp config/settings.example.yaml config/settings.yaml

# Error: Invalid YAML syntax
yamllint config/settings.yaml
```

**2. GitHub Token Issues**
```bash
# Check token permissions
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Token needs 'repo' scope for private repos
```

**3. AI Integration Problems**
```bash
# Test OpenAI connection
python -c "import openai; print('OpenAI available')"

# Check API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

**4. Slack Bot Issues**
```bash
# Check Slack app permissions in Slack admin
# Bot needs: app_mentions:read, chat:write, users:read

# Test bot connection
python -c "from slack_sdk import WebClient; client = WebClient(token='$SLACK_BOT_TOKEN'); print(client.auth_test())"
```

### Mock Data Testing

If you don't have tokens set up, the scripts will use mock data:

```bash
# Test without GitHub token (uses mock PRs)
unset GITHUB_TOKEN
python test_cli.py --test-all

# Test without AI (uses fallback content)
unset OPENAI_API_KEY
python test_cli.py --test-docs
```

## 📊 Validation Checklist

### ✅ Core MVP Functionality

- [ ] Configuration loads successfully
- [ ] GitHub PR fetching works (or mock data loads)
- [ ] AI integration works (or fallback content used)
- [ ] Release notes generate in both formats
- [ ] CRQ documents generate for Day 1 and Day 2
- [ ] All generated files have reasonable content and size

### ✅ Slack Bot Functionality

- [ ] Slack libraries import successfully
- [ ] Bot credentials are valid
- [ ] ReleaseTracker class works correctly
- [ ] Message formatting functions work
- [ ] Mock sign-off workflow completes

### ✅ Generated Content Quality

**Release Notes:**
- [ ] Contains service name and version
- [ ] Lists PRs with authors and links
- [ ] Categorizes changes appropriately
- [ ] Includes deployment information

**CRQ Documents:**
- [ ] Follows organization's CRQ format
- [ ] Contains all 7 required questions
- [ ] Includes AI-generated risk assessment
- [ ] Has proper Day 1/Day 2 separation
- [ ] Lists all included PRs

## 🚀 Ready for Production?

If all tests pass and generated content looks good:

1. **Deploy the Slack bot** using the deployment guide
2. **Set up GitHub Actions** workflow
3. **Configure Slack Workflow Builder** 
4. **Test end-to-end** with a small test release

## 📞 Support

If you encounter issues:

1. Check the generated log files in `test_outputs/`
2. Run individual tests to isolate problems
3. Verify environment variables and configuration
4. Check the troubleshooting section above

The testing scripts provide detailed error messages and suggestions for common issues. 