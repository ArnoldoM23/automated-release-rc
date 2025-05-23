# 🚀 Serverless Release RC Workflow - Slack Workflow Builder Only

**Complete setup for serverless PR sign-off tracking using only Slack Workflow Builder + GitHub Actions**

**🎯 Zero Infrastructure Required - Leadership Approved!**

---

## 📋 **Architecture: Pure Serverless**

```
👤 User Types           📱 Slack Workflow          🔄 GitHub Actions
   /run-release     ──►    Builder Form       ──►   Repository Dispatch
       │                        │                        │
       │                   ✅ Modal Form              📋 Generate Docs
       │                   📝 8 Fields                🤖 AI Processing  
       │                   🚀 Submit                  📊 PR Analysis
       │                        │                        │
       │                        │                   📤 Post Results
       └─────────────────── 📨 Slack Message ◄──── 📁 Artifacts Ready
                           📊 Release Thread
                           👥 Sign-off Tracking
```

**✅ Benefits:**
- **No servers to maintain** - Pure Slack + GitHub
- **No deployment costs** - Uses existing infrastructure  
- **Leadership approved** - Zero new infrastructure
- **Still fully automated** - Complete workflow automation

---

## 🔧 **Setup Part 1: Slack Workflow Builder**

### **Step 1: Create New Workflow**

1. **Open Slack → Tools → Workflow Builder**
2. **Click "Create Workflow"**
3. **Name:** `Release RC Automation`
4. **Choose trigger:** `Slash Command`

### **Step 2: Configure Slash Command**

1. **Command:** `/run-release`
2. **Description:** `Start automated release workflow`
3. **Usage hint:** `[service] [version]`
4. **Where to use:** `Channels and DMs`

### **Step 3: Add Form Step**

**Click "Add Step" → "Send a form"**

**Form Title:** `🚀 Start Release Process`

**Add these form fields:**

| Field Name | Type | Required | Placeholder |
|------------|------|----------|-------------|
| `prod_version` | Short text | ✅ | e.g., v2.4.3 |
| `new_version` | Short text | ✅ | e.g., v2.5.0 |
| `service_name` | Short text | ✅ | e.g., cer-cart |
| `release_type` | Single select | ✅ | standard, hotfix, ebf |
| `rc_name` | Short text | ✅ | Release Coordinator |
| `rc_manager` | Person | ✅ | Select user |
| `day1_date` | Date | ✅ | Day 1 prep date |
| `day2_date` | Date | ✅ | Day 2 deploy date |

### **Step 4: Add Webhook Step**

**Click "Add Step" → "Send a webhook"**

**Webhook URL:** `https://api.github.com/repos/YOUR-ORG/YOUR-REPO/dispatches`

**Method:** `POST`

**Headers:**
```
Authorization: token YOUR_GITHUB_TOKEN
Accept: application/vnd.github.v3+json
Content-Type: application/json
```

**Body (JSON):**
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
    "slack_channel": "{{workflow_channel_id}}",
    "slack_user": "{{workflow_user_id}}",
    "slack_ts": "{{workflow_message_ts}}"
  }
}
```

### **Step 5: Add Confirmation Message**

**Click "Add Step" → "Send a message"**

**Send to:** `Channel where workflow started`

**Message:**
```
🚀 **Release process starting for {{service_name}} {{new_version}}**

📋 **Details:**
• Production version: {{prod_version}}
• New version: {{new_version}}
• Service: {{service_name}}
• Type: {{release_type}}
• RC: {{rc_name}}
• Manager: {{rc_manager}}
• Day 1: {{day1_date}}
• Day 2: {{day2_date}}

⏳ Fetching PRs and generating documentation...
🤖 GitHub Actions workflow triggered!

You'll receive an update here when the release documentation is ready.
```

### **Step 6: Publish Workflow**

1. **Click "Publish"**
2. **Test with:** `/run-release`

---

## 🔄 **Setup Part 2: GitHub Actions (Serverless)**

Replace the Slack bot integration step in `.github/workflows/run_release.yml` with this serverless version:

```yaml
    - name: 📤 Post Results to Slack (Serverless)
      env:
        SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
      run: |
        echo "📤 Posting results to Slack..."
        
        # Get file sizes for summary
        RELEASE_NOTES_SIZE=$(stat -c%s "release_output/release_notes.txt" 2>/dev/null || echo "0")
        CRQ_DAY1_SIZE=$(stat -c%s "release_output/crq_day1.txt" 2>/dev/null || echo "0")
        CRQ_DAY2_SIZE=$(stat -c%s "release_output/crq_day2.txt" 2>/dev/null || echo "0")
        
        # Create sign-off tracking message
        cat > slack_message.json << 'EOF'
        {
          "channel": "${{ steps.params.outputs.slack_channel }}",
          "text": "🎉 Release documentation ready for ${{ steps.params.outputs.service_name }} ${{ steps.params.outputs.new_version }}!",
          "blocks": [
            {
              "type": "header",
              "text": {
                "type": "plain_text",
                "text": "🎉 Release ${{ steps.params.outputs.service_name }} ${{ steps.params.outputs.new_version }} Ready!"
              }
            },
            {
              "type": "section",
              "text": {
                "type": "mrkdwn",
                "text": "*📋 Generated Documentation:*\n• Release Notes: $RELEASE_NOTES_SIZE bytes\n• Day 1 CRQ: $CRQ_DAY1_SIZE bytes\n• Day 2 CRQ: $CRQ_DAY2_SIZE bytes\n\n*📁 Download:* <${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Artifacts>"
              }
            },
            {
              "type": "section",
              "text": {
                "type": "mrkdwn",
                "text": "*🗓️ Schedule:*\n• Day 1 (prep): ${{ steps.params.outputs.day1_date }}\n• Day 2 (deploy): ${{ steps.params.outputs.day2_date }}\n• RC Manager: <@${{ steps.params.outputs.rc_manager }}>"
              }
            },
            {
              "type": "divider"
            },
            {
              "type": "section",
              "text": {
                "type": "mrkdwn",
                "text": "🔄 *PR Sign-off Tracking*\nDevelopers with PRs in this release, please confirm sign-off by reacting with ✅ to this message.\n\n*Cut-off: 12:00 PM tomorrow*"
              }
            },
            {
              "type": "section",
              "text": {
                "type": "mrkdwn",
                "text": "*🚀 Next Steps:*\n1. Download release artifacts above\n2. Review generated documentation\n3. Confirm PR sign-offs with ✅ reactions\n4. Proceed with deployment on scheduled dates"
              }
            }
          ]
        }
        EOF
        
        # Post to Slack using webhook
        if [ -n "$SLACK_BOT_TOKEN" ]; then
          curl -X POST -H 'Authorization: Bearer ${{ secrets.SLACK_BOT_TOKEN }}' \
               -H 'Content-type: application/json' \
               --data @slack_message.json \
               https://slack.com/api/chat.postMessage
          echo "✅ Posted to Slack channel: ${{ steps.params.outputs.slack_channel }}"
        else
          echo "⚠️ SLACK_BOT_TOKEN not configured - skipping Slack notification"
        fi
```

---

## 🔧 **Setup Part 3: Slack App (Minimal)**

We still need a minimal Slack app for posting messages, but **no server deployment**:

### **Step 1: Create Slack App**

1. **Go to [Slack API](https://api.slack.com/apps)**
2. **Click "Create New App" → "From scratch"**
3. **Name:** `Release RC Notifications`
4. **Select your workspace**

### **Step 2: Add Bot Permissions**

In **OAuth & Permissions**, add only:
- `chat:write` - Post messages
- `channels:read` - Read channel info

### **Step 3: Install App**

1. **Install to workspace**
2. **Copy Bot User OAuth Token** (starts with `xoxb-`)
3. **Add to GitHub Secrets as `SLACK_BOT_TOKEN`**

**That's it! No server deployment needed.**

---

## 📋 **How It Works (Serverless)**

### **Workflow Flow:**
1. **User:** `/run-release` in any Slack channel
2. **Slack Workflow Builder:** Shows form, collects data
3. **Webhook:** Triggers GitHub Actions via repository_dispatch
4. **GitHub Actions:** 
   - Fetches PRs between versions
   - Generates AI-powered documentation
   - Creates release artifacts
   - Posts results back to Slack
5. **Slack:** Shows completion message with sign-off tracking

### **Sign-off Tracking (Simplified):**
- **PR authors react with ✅** to the completion message
- **Release manager monitors reactions** 
- **Simple visual tracking** - no complex state management
- **Cut-off enforcement** - manual review by RC manager

---

## 🎯 **Benefits of Serverless Approach**

### **✅ Leadership Approved**
- **Zero server infrastructure** - Uses existing Slack + GitHub
- **No ongoing costs** - No hosting fees or maintenance
- **Security compliant** - No external servers to secure
- **Audit friendly** - All actions logged in GitHub Actions

### **✅ Still Fully Automated**
- **30-second release kick-off** - From `/run-release` to documentation
- **AI-powered content** - Professional release notes and CRQs
- **Artifact management** - All documents downloadable from GitHub
- **Slack integration** - Results posted back to team

### **✅ Scalable & Reliable**
- **GitHub Actions limits** - Generous free tier
- **Slack Workflow Builder** - Enterprise-grade reliability
- **No single points of failure** - Distributed architecture
- **Easy to modify** - No server code to maintain

---

## 🔧 **Required GitHub Secrets**

Add these to your repository settings:

| Secret | Value | Purpose |
|--------|-------|---------|
| `SLACK_BOT_TOKEN` | `xoxb-your-token` | Post completion messages |
| `OPENAI_API_KEY` | Your OpenAI key | AI documentation generation |
| `GITHUB_TOKEN` | Auto-provided | PR fetching and artifact upload |

---

## 📊 **Testing Your Serverless Setup**

### **Step 1: Test Slack Workflow**
```
1. Type: /run-release
2. Fill out the form
3. Submit
4. Verify GitHub Actions triggered
```

### **Step 2: Test GitHub Actions**
```
1. Check workflow run in Actions tab
2. Verify all steps complete successfully
3. Download artifacts to test content
4. Check Slack for completion message
```

### **Step 3: Test Sign-off Flow**
```
1. Have team members react with ✅
2. RC manager monitors reactions
3. Proceed with release when ready
```

---

## 🎉 **Result: Enterprise Release Automation Without Servers**

You now have:

- **✅ `/run-release` command** - Works in any channel
- **✅ Interactive form** - Professional data collection
- **✅ Automated documentation** - AI-generated release notes and CRQs
- **✅ Slack notifications** - Results posted back to team
- **✅ Sign-off tracking** - Visual reaction-based workflow
- **✅ Zero infrastructure** - No servers to deploy or maintain
- **✅ Leadership approved** - Uses only existing tools

**🚀 Ready to transform your release process with zero infrastructure!**

---

*Perfect for organizations with strict infrastructure policies* 🏢