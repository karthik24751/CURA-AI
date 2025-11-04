#!/bin/bash

# CuraLink Automatic Deployment Script
# This script will automatically deploy to Koyeb and Netlify

set -e  # Exit on error

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  CuraLink Automatic Deployment Script${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Step 1: Initialize Git if needed
echo -e "${YELLOW}Step 1: Initializing Git repository...${NC}"
if [ ! -d ".git" ]; then
    git init
    echo -e "${GREEN}✓ Git initialized${NC}"
else
    echo -e "${GREEN}✓ Git already initialized${NC}"
fi

# Step 2: Add and commit changes
echo ""
echo -e "${YELLOW}Step 2: Committing changes...${NC}"
git add .
if git diff --cached --quiet; then
    echo -e "${GREEN}✓ No changes to commit${NC}"
else
    git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')" || echo -e "${YELLOW}⚠ Nothing to commit${NC}"
    echo -e "${GREEN}✓ Changes committed${NC}"
fi

# Step 3: Check for remote
echo ""
echo -e "${YELLOW}Step 3: Checking GitHub remote...${NC}"
if ! git remote | grep -q "origin"; then
    echo -e "${RED}❌ No GitHub remote configured!${NC}"
    echo ""
    echo "Please configure GitHub remote first:"
    echo "1. Create a repository at https://github.com/new"
    echo "2. Run: git remote add origin YOUR_REPO_URL"
    echo "3. Run: git push -u origin main"
    echo "4. Then run this script again"
    echo ""
    exit 1
else
    echo -e "${GREEN}✓ Remote configured${NC}"
fi

# Step 4: Push to GitHub
echo ""
echo -e "${YELLOW}Step 4: Pushing to GitHub...${NC}"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push origin $CURRENT_BRANCH 2>&1 || {
    echo -e "${YELLOW}⚠ Push failed. Trying to set upstream...${NC}"
    git push -u origin $CURRENT_BRANCH 2>&1 || {
        echo -e "${RED}❌ Push failed. Please check your credentials.${NC}"
        exit 1
    }
}
echo -e "${GREEN}✓ Code pushed to GitHub${NC}"

# Step 5: Instructions for platform deployment
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Git deployment complete!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Your code is now on GitHub and ready for cloud deployment!"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo "1. DEPLOY BACKEND (Koyeb):"
echo "   → Go to: https://app.koyeb.com"
echo "   → Click 'Create App'"
echo "   → Select your GitHub repository"
echo "   → Root directory: curalink-backend"
echo "   → Add environment variables from .env.production"
echo "   → Deploy!"
echo ""
echo "2. DEPLOY FRONTEND (Netlify):"
echo "   → Go to: https://app.netlify.com"
echo "   → Click 'Add new site'"
echo "   → Select your GitHub repository"
echo "   → Base directory: curalink-frontend"
echo "   → Build command: npm run build"
echo "   → Publish directory: .next"
echo "   → Add environment variables from .env.production"
echo "   → Deploy!"
echo ""
echo -e "${GREEN}Both platforms will auto-deploy on future git pushes!${NC}"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
