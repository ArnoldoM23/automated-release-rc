#!/bin/bash
# RC Agent v4.0 - Auto-loading Environment Wrapper
# This script automatically loads your environment and runs the RC Agent

echo "🔧 RC Agent v4.0 - Loading Environment..."

# Default environment file location (home directory only for security)
ENV_FILE=${RC_ENV_FILE:-~/.rc_env_checkout.sh}

# Check if environment file exists (only in home directory)
if [ -f "$ENV_FILE" ]; then
    echo "✅ Loading environment from $ENV_FILE"
    source "$ENV_FILE"
    echo "🔐 GitHub Token: ${GITHUB_TOKEN:0:8}..."
    echo "📋 GitHub Repo: $GITHUB_REPO"
    echo ""
else
    echo "❌ Environment file not found: $ENV_FILE"
    echo "📝 Please create your environment file:"
    echo "   cp .rc_env_checkout.sh ~/.rc_env_checkout.sh"
    echo "   # Edit with your actual secrets"
    echo ""
    echo "💡 Or specify custom location:"
    echo "   RC_ENV_FILE=~/.my-secrets.sh $0"
    exit 1
fi

# Run the RC Agent
echo "🚀 Starting RC Agent v4.0..."
python -m src.cli.run_release_agent 