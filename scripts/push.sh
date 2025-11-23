#!/bin/bash
set -e

# Change to project directory
cd /root/bizdna-new

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "❌ .env file not found!"
    exit 1
fi

# Check if GITHUB_TOKEN exists
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GITHUB_TOKEN not found in .env!"
    exit 1
fi

# Set repository URL with token
REPO_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_REPO}"

# Check if remote exists, if not - add it
if ! git remote | grep -q origin; then
    git remote add origin $REPO_URL
fi

# Get commit message from argument or use interactive mode
if [ -n "$1" ]; then
    COMMIT_MSG="$1"
else
    # Interactive mode - ask for commit message
    echo "Enter commit message (or press Enter for default):"
    read COMMIT_MSG
    if [ -z "$COMMIT_MSG" ]; then
        COMMIT_MSG="Update: $(date '+%Y-%m-%d %H:%M:%S')"
    fi
fi

# Check if there are changes
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ No changes to commit"
    exit 0
fi

# Git operations
echo "📦 Adding files..."
git add .

echo "💾 Committing with message: '$COMMIT_MSG'"
git commit -m "$COMMIT_MSG"

echo "📤 Pushing to GitHub..."
if git push -u origin main 2>&1; then
    echo "✅ Successfully pushed to GitHub!"
else
    echo "⚠️  Push failed. Trying with token..."
    git remote set-url origin $REPO_URL
    if git push -u origin main 2>&1; then
        echo "✅ Successfully pushed with token!"
    else
        echo "❌ Push failed. Check your token and repository permissions."
        exit 1
    fi
fi
