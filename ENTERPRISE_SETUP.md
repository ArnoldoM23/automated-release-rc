# Enterprise GitHub Setup Guide

## Quick Setup for Enterprise GitHub

If you're using an enterprise GitHub instance (not public GitHub), follow these steps:

### 1. Identify Your Enterprise GitHub URL

Your enterprise GitHub URL typically looks like:
- `https://github.company.com` 
- `https://gecgithub01.walmart.com`
- `https://github.microsoft.com`
- `https://ghe.company.com`

### 2. Set Environment Variables

Create or update your `~/.rc_env_checkout.sh` file:

```bash
#!/bin/bash
# Enterprise GitHub Configuration

# Your enterprise GitHub token
export GITHUB_TOKEN="ghp_your_enterprise_token_here"

# Your repository in owner/repo format
export GITHUB_REPO="ce-orchestration/ce-cartxo"

# Your enterprise API URL (add /api/v3 to your GitHub domain)
export GITHUB_API_URL="https://gecgithub01.walmart.com/api/v3"

# Optional: Other configurations
export SERVICE_NAME="ce-cartxo"
export SERVICE_NAMESPACE="ce-orchestration"
```

### 3. Generate Enterprise GitHub Token

1. Go to your enterprise GitHub instance: `https://your-github-domain.com`
2. Navigate to: Settings → Developer settings → Personal access tokens → Tokens (classic)
3. Click "Generate new token (classic)"
4. Set **Note**: `RC Release Automation Agent`
5. Select **Scopes**:
   - ✅ `repo` - Full control of private repositories
   - ✅ `workflow` - Update GitHub Action workflows (if needed)
6. Click "Generate token"
7. Copy the token (starts with `ghp_`) and add it to your environment file

### 4. Test Your Setup

```bash
# Load your environment
source ~/.rc_env_checkout.sh

# Test GitHub API access
curl -H "Authorization: token $GITHUB_TOKEN" \
     "$GITHUB_API_URL/user"

# Should return your user info (not an error)
```

### 5. Run the RC Agent

```bash
# Load environment and run
source ~/.rc_env_checkout.sh
python -m src.cli.run_release_agent
```

## Common Issues & Solutions

### Issue: Timeouts or Slow Performance
**Solution**: The system automatically uses longer timeouts for enterprise instances (5 minutes vs 1 minute for public GitHub).

### Issue: "Invalid credentials" or 401 errors
**Solution**: 
- Check your `GITHUB_TOKEN` is valid
- Verify your `GITHUB_API_URL` includes `/api/v3`
- Ensure your token has `repo` scope

### Issue: "Repository not found"
**Solution**:
- Verify `GITHUB_REPO` is in `owner/repo` format
- Check you have access to the repository
- Confirm the repository name is correct

### Issue: RC name shows organization instead of your name
**Solution**: The system now fetches your actual user profile (not the repo owner). This should be fixed automatically.

## Example: Walmart Enterprise

```bash
# For Walmart users
export GITHUB_TOKEN="ghp_your_walmart_token"
export GITHUB_REPO="ce-orchestration/ce-cartxo"
export GITHUB_API_URL="https://gecgithub01.walmart.com/api/v3"
```

## Example: Microsoft Enterprise

```bash
# For Microsoft users
export GITHUB_TOKEN="ghp_your_microsoft_token"
export GITHUB_REPO="microsoft/your-repo"
export GITHUB_API_URL="https://github.microsoft.com/api/v3"
```

## Need Help?

If you're still having issues:
1. Check the logs for specific error messages
2. Verify your network can reach your enterprise GitHub instance
3. Test your token and API URL with `curl` first
4. Create an issue with your specific error message (remove sensitive info) 