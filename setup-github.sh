#!/bin/bash

# Quick GitHub Setup Script

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  GitHub Repository Setup Helper"
echo "════════════════════════════════════════════════════════════"
echo ""

# Check if remote already exists
if git remote | grep -q "origin"; then
    echo "✅ GitHub remote already configured!"
    git remote -v
    echo ""
    echo "To push changes:"
    echo "  git push origin main"
    exit 0
fi

echo "No GitHub remote found. Let's set it up!"
echo ""
echo "First, create a repository on GitHub:"
echo "  1. Go to: https://github.com/new"
echo "  2. Repository name: curalink"
echo "  3. Keep it Public"
echo "  4. Do NOT check 'Add README'"
echo "  5. Click 'Create repository'"
echo ""
read -p "Have you created the repository? (y/n): " created

if [ "$created" != "y" ]; then
    echo "Please create the repository first, then run this script again."
    exit 0
fi

echo ""
read -p "Enter your GitHub repository URL (e.g., https://github.com/username/curalink.git): " repo_url

if [ -z "$repo_url" ]; then
    echo "❌ No URL provided. Exiting."
    exit 1
fi

echo ""
echo "Setting up remote..."
git remote add origin "$repo_url"
git branch -M main

echo ""
echo "Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Success! Code pushed to GitHub!"
    echo ""
    echo "Next steps:"
    echo "  1. Deploy backend to Koyeb: https://app.koyeb.com"
    echo "  2. Deploy frontend to Netlify: https://app.netlify.com"
    echo ""
    echo "Or run: ./auto-deploy.sh"
else
    echo ""
    echo "❌ Push failed. Please check your credentials and try again."
    echo ""
    echo "Manual commands:"
    echo "  git push -u origin main"
fi
