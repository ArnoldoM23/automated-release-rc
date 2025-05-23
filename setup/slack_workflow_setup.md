# 🔧 Complete Slack Workflow Builder Setup

**Create the `/run-release` command that triggers your Release Automation Agent**

---

## 📋 **Overview**

This guide walks you through creating a Slack Workflow Builder workflow that:
1. Triggers with `/run-release` slash command
2. Collects release information via a form
3. Sends data to GitHub Actions via `repository_dispatch`
4. Generates release documentation automatically

**⏱️ Setup Time:** 3-5 minutes

---

## 🚀 **Step 1: Create New Workflow**

### **1.1 Open Workflow Builder**
1. In Slack, click on your workspace name (top left)
2. Go to **Tools** → **Workflow Builder**
3. Click **Create** → **From scratch**

### **1.2 Set Workflow Trigger**
1. **Name your workflow:** `RC Release Automation`
2. **Description:** `Automated release documentation generation for RC deployments`
3. **Choose trigger:** Select **Shortcut**
4. **Shortcut name:** `run-release`
5. **Short description:** `Generate release documentation`
6. Click **Next**

---

## 📝 **Step 2: Create Release Information Form**

### **2.1 Add Form Step**
1. Click **Add Step** → **Send a form**
2. **Form title:** `🚀 RC Release Information`
3. **Send form to:** `Person who starts this workflow`

### **2.2 Configure Form Fields**

**Copy and paste these exact field configurations:**

#### **Field 1: Production Version**
- **Field type:** Short text
- **Question:** Production Version
- **Variable name:** `prod_version`
- **Placeholder:** `v2.4.3`
- **Required:** ✅ Yes

#### **Field 2: New Version**
- **Field type:** Short text  
- **Question:** New Release Version
- **Variable name:** `new_version`
- **Placeholder:** `v2.5.0`
- **Required:** ✅ Yes

#### **Field 3: Service Name**
- **Field type:** Short text
- **Question:** Service Name
- **Variable name:** `service_name`
- **Placeholder:** `cer-cart`
- **Required:** ✅ Yes

#### **Field 4: Release Type**
- **Field type:** Select from a list
- **Question:** Release Type
- **Variable name:** `release_type`
- **Options:** 
  - `standard`
  - `hotfix` 
  - `ebf`
- **Required:** ✅ Yes

#### **Field 5: Release Coordinator**
- **Field type:** Short text
- **Question:** Release Coordinator (RC)
- **Variable name:** `rc_name`
- **Placeholder:** `John Doe`
- **Required:** ✅ Yes

#### **Field 6: Release Manager**
- **Field type:** Short text
- **Question:** Release Manager
- **Variable name:** `rc_manager`
- **Placeholder:** `Jane Smith`
- **Required:** ✅ Yes

#### **Field 7: Day 1 Date**
- **Field type:** Date
- **Question:** CRQ Day 1 Date (Preparation)
- **Variable name:** `day1_date`
- **Required:** ✅ Yes

#### **Field 8: Day 2 Date**
- **Field type:** Date
- **Question:** CRQ Day 2 Date (Deployment)
- **Variable name:** `day2_date`
- **Required:** ✅ Yes

### **2.3 Complete Form Setup**
1. Click **Save** on the form step
2. Click **Next** to proceed

---

## 🔗 **Step 3: Configure GitHub Actions Integration**

### **3.1 Add HTTP Request Step**
1. Click **Add Step** → **Send a web request**
2. **Request name:** `Trigger Release Agent`

### **3.2 HTTP Request Configuration**

**Copy these exact settings:**

#### **Request Details:**
- **URL:** `https://api.github.com/repos/YOUR_GITHUB_USERNAME/automated-release-rc/dispatches`
  
  ⚠️ **Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username**

- **Method:** `POST`

#### **Headers:**
```
Authorization: Bearer YOUR_GITHUB_TOKEN
Content-Type: application/json
Accept: application/vnd.github.v3+json
```

⚠️ **Replace `YOUR_GITHUB_TOKEN` with your personal access token**

#### **Request Body (JSON):**
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

### **3.3 Complete HTTP Step**
1. Click **Save** on the web request step
2. Click **Next**

---

## 💬 **Step 4: Add Confirmation Message**

### **4.1 Add Message Step**
1. Click **Add Step** → **Send a message**
2. **Send message to:** `Person who started this workflow`

### **4.2 Confirmation Message**
```
🚀 **Release automation started!**

**Service:** {{service_name}} {{prod_version}} → {{new_version}}
**RC:** {{rc_name}}
**Manager:** {{rc_manager}}
**Type:** {{release_type}}
**Schedule:** {{day1_date}} (Day 1) → {{day2_date}} (Day 2)

⏳ Generating release documentation...
📋 GitHub Actions will post results when complete
🔗 Check progress: https://github.com/YOUR_GITHUB_USERNAME/automated-release-rc/actions

*Estimated completion: 30-60 seconds*
```

⚠️ **Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username**

### **4.3 Complete Message Step**
1. Click **Save** on the message step
2. Click **Next**

---

## ✅ **Step 5: Publish Workflow**

### **5.1 Review Settings**
1. **Workflow name:** `RC Release Automation`
2. **Collaborators:** Add your team members who can use this workflow
3. **Workflow visibility:** Choose appropriate visibility for your organization

### **5.2 Publish**
1. Click **Publish**
2. Confirm publishing

### **5.3 Test Workflow**
1. In any Slack channel, type: `/run-release`
2. The form should appear
3. Fill out test data and submit
4. You should see the confirmation message

---

## 🔑 **Step 6: GitHub Token Setup**

### **6.1 Create GitHub Personal Access Token**
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click **Generate new token (classic)**
3. **Note:** `RC Release Automation`
4. **Expiration:** Choose appropriate timeframe
5. **Scopes:** Select:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
6. Click **Generate token**
7. **Copy the token immediately** (you won't see it again)

### **6.2 Configure GitHub Repository Secrets**
1. Go to your repository: `https://github.com/YOUR_USERNAME/automated-release-rc`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each:

#### **Required Secrets:**
```bash
# Required for workflow
GITHUB_TOKEN = "ghp_your_personal_access_token_here"

# Optional for AI features
OPENAI_API_KEY = "sk-your_openai_key_here"
ANTHROPIC_API_KEY = "your_anthropic_key_here"
AZURE_OPENAI_API_KEY = "your_azure_openai_key_here"
AZURE_OPENAI_ENDPOINT = "https://your-resource.openai.azure.com/"
```

---

## 🧪 **Step 7: End-to-End Testing**

### **7.1 Test the Complete Workflow**
1. In Slack, run: `/run-release`
2. Fill out the form with test data:
   - **Production Version:** `v1.0.0`
   - **New Version:** `v1.1.0`
   - **Service Name:** `test-service`
   - **Release Type:** `standard`
   - **RC Name:** `Your Name`
   - **Release Manager:** `Your Manager`
   - **Day 1 Date:** Tomorrow
   - **Day 2 Date:** Day after tomorrow

### **7.2 Verify Results**
1. ✅ Confirmation message appears in Slack
2. ✅ GitHub Actions workflow starts running
3. ✅ Workflow completes successfully (30-60 seconds)
4. ✅ Release documentation files are generated

### **7.3 Check Generated Output**
Navigate to your GitHub Actions run and download the artifacts:
- `release_notes.txt` - Confluence-ready release notes
- `crq_day1.txt` - Day 1 preparation CRQ
- `crq_day2.txt` - Day 2 deployment CRQ
- `release_notes.md` - Markdown version

---

## ⚡ **Quick Copy-Paste Summary**

### **Slack Workflow Fields:**
```
1. prod_version (Short text) - "v2.4.3"
2. new_version (Short text) - "v2.5.0"  
3. service_name (Short text) - "cer-cart"
4. release_type (Select) - standard/hotfix/ebf
5. rc_name (Short text) - "John Doe"
6. rc_manager (Short text) - "Jane Smith"
7. day1_date (Date) - Preparation date
8. day2_date (Date) - Deployment date
```

### **GitHub API Endpoint:**
```
POST https://api.github.com/repos/YOUR_USERNAME/automated-release-rc/dispatches
```

### **Headers:**
```
Authorization: Bearer YOUR_GITHUB_TOKEN
Content-Type: application/json
Accept: application/vnd.github.v3+json
```

### **Test Command:**
```
/run-release
```

---

## 🆘 **Troubleshooting**

### **Common Issues:**

**❌ "Could not reach URL"**
- Check GitHub token has correct permissions
- Verify repository name in URL is correct
- Ensure repository is public or token has private repo access

**❌ "Workflow not triggering"**
- Verify GitHub Actions are enabled in repository settings
- Check repository secrets are set correctly
- Confirm webhook payload format matches expected structure

**❌ "Form variables not passing"**
- Double-check variable names match exactly (`prod_version`, not `production_version`)
- Ensure all required fields are marked as required
- Verify JSON syntax in request body

### **Debug Steps:**
1. Check GitHub Actions tab for error messages
2. Verify repository secrets are set
3. Test GitHub token permissions manually
4. Review Slack workflow builder logs

---

## 🎯 **Success Criteria**

**✅ Your workflow is working when:**
- `/run-release` command triggers the form
- Form submission shows confirmation message
- GitHub Actions workflow executes successfully
- Release documentation files are generated
- Total execution time < 60 seconds

**🎉 Congratulations! Your RC Release Automation Agent is now fully operational.** 