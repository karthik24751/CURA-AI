#!/bin/bash

echo "════════════════════════════════════════════════════════════"
echo "  CuraLink Deployment Setup Script"
echo "  This script will prepare your project for deployment"
echo "════════════════════════════════════════════════════════════"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed. Please install Git first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Git is installed${NC}"

# Check if we're in the right directory
if [ ! -d "curalink-backend" ] || [ ! -d "curalink-frontend" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Project directories found${NC}"

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    echo ""
    echo -e "${YELLOW}Initializing Git repository...${NC}"
    git init
    echo -e "${GREEN}✓ Git repository initialized${NC}"
else
    echo -e "${GREEN}✓ Git repository already initialized${NC}"
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo ""
    echo -e "${YELLOW}Adding files to Git...${NC}"
    git add .
    
    echo ""
    echo -e "${YELLOW}Committing changes...${NC}"
    git commit -m "Prepare for deployment - Configuration files added"
    echo -e "${GREEN}✓ Changes committed${NC}"
else
    echo -e "${GREEN}✓ No uncommitted changes${NC}"
fi

# Check if remote origin is set
if ! git remote | grep -q "origin"; then
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}GitHub Setup Required${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════${NC}"
    echo ""
    echo "1. Go to: https://github.com/new"
    echo "2. Create a new repository named: curalink"
    echo "3. Do NOT initialize with README"
    echo ""
    read -p "Enter your GitHub repository URL (e.g., https://github.com/username/curalink.git): " repo_url
    
    if [ -n "$repo_url" ]; then
        git remote add origin "$repo_url"
        git branch -M main
        echo ""
        echo -e "${GREEN}✓ Remote origin added${NC}"
        
        echo ""
        echo -e "${YELLOW}Pushing to GitHub...${NC}"
        git push -u origin main
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Code pushed to GitHub successfully!${NC}"
        else
            echo -e "${RED}❌ Failed to push to GitHub. Please check your credentials.${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ No repository URL provided${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Git remote origin already configured${NC}"
    
    echo ""
    echo -e "${YELLOW}Pushing latest changes to GitHub...${NC}"
    git push origin main
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Code pushed to GitHub successfully!${NC}"
    else
        echo -e "${YELLOW}⚠ Push failed. You may need to pull first or check credentials.${NC}"
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Your project is now ready for deployment!"
echo ""
echo "Next Steps:"
echo "1. Follow the instructions in DEPLOYMENT_INSTRUCTIONS.txt"
echo "2. Set up your free database (Aiven MySQL recommended)"
echo "3. Deploy backend to Koyeb"
echo "4. Deploy frontend to Netlify"
echo "5. Use DEPLOYMENT_CHECKLIST.txt to verify everything works"
echo ""
echo "Files created for deployment:"
echo "  - curalink-backend/Procfile"
echo "  - curalink-backend/runtime.txt"
echo "  - curalink-backend/koyeb.yaml"
echo "  - curalink-backend/.env.production"
echo "  - curalink-backend/.gitignore"
echo "  - curalink-frontend/netlify.toml"
echo "  - curalink-frontend/.env.production"
echo "  - curalink-frontend/.gitignore"
echo ""
echo "Documentation:"
echo "  - DEPLOYMENT_INSTRUCTIONS.txt (Complete step-by-step guide)"
echo "  - DEPLOYMENT_CHECKLIST.txt (Verification checklist)"
echo ""
echo "════════════════════════════════════════════════════════════"
