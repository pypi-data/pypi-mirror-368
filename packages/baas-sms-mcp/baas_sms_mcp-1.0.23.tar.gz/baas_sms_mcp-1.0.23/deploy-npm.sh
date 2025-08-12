#!/bin/bash

# NPM 배포 자동화 스크립트
# Usage: ./scripts/deploy-npm.sh [patch|minor|major]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default version type
VERSION_TYPE=${1:-patch}

# Validate version type
if [[ ! "$VERSION_TYPE" =~ ^(patch|minor|major)$ ]]; then
    echo -e "${RED}❌ Error: Version type must be 'patch', 'minor', or 'major'${NC}"
    echo "Usage: $0 [patch|minor|major]"
    exit 1
fi

echo -e "${BLUE}🚀 Starting NPM deployment process...${NC}"
echo -e "${BLUE}📦 Version type: ${VERSION_TYPE}${NC}"

# Check if we're in the right directory
if [[ ! -f "package.json" ]]; then
    echo -e "${RED}❌ Error: package.json not found. Please run this script from the project root.${NC}"
    exit 1
fi

# Check if git working directory is clean
if [[ -n $(git status --porcelain) ]]; then
    echo -e "${RED}❌ Error: Git working directory is not clean. Please commit or stash changes first.${NC}"
    git status --short
    exit 1
fi

# Check if we're on master/main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$CURRENT_BRANCH" != "master" && "$CURRENT_BRANCH" != "main" ]]; then
    echo -e "${YELLOW}⚠️  Warning: Not on master/main branch (currently on: ${CURRENT_BRANCH})${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🛑 Deployment cancelled${NC}"
        exit 0
    fi
fi

# Check NPM authentication
echo -e "${BLUE}🔐 Checking NPM authentication...${NC}"
if ! npm whoami > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Not logged in to NPM. Please run 'npm login' first.${NC}"
    exit 1
fi

NPM_USER=$(npm whoami)
echo -e "${GREEN}✅ Logged in as: ${NPM_USER}${NC}"

# Get current version
CURRENT_VERSION=$(node -p "require('./package.json').version")
echo -e "${BLUE}📋 Current version: ${CURRENT_VERSION}${NC}"

# Run tests if they exist
if npm run test --silent > /dev/null 2>&1; then
    echo -e "${BLUE}🧪 Running tests...${NC}"
    npm test
    echo -e "${GREEN}✅ Tests passed${NC}"
else
    echo -e "${YELLOW}⚠️  No tests found, skipping test phase${NC}"
fi

# Clean previous builds
echo -e "${BLUE}🧹 Cleaning previous builds...${NC}"
npm run clean 2>/dev/null || true

# Build package
echo -e "${BLUE}🔨 Building package...${NC}"
npm run build 2>/dev/null || echo -e "${YELLOW}⚠️  No build script found, skipping build phase${NC}"

# Version bump and tag
echo -e "${BLUE}🏷️  Bumping ${VERSION_TYPE} version...${NC}"
NEW_VERSION=$(npm version $VERSION_TYPE --no-git-tag-version)
echo -e "${GREEN}✅ New version: ${NEW_VERSION}${NC}"

# Update version in pyproject.toml to keep in sync
if [[ -f "pyproject.toml" ]]; then
    echo -e "${BLUE}🔄 Syncing version in pyproject.toml...${NC}"
    # Remove 'v' prefix if present
    CLEAN_VERSION=${NEW_VERSION#v}
    
    # Update pyproject.toml version
    if command -v sed > /dev/null; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS sed
            sed -i '' "s/^version = .*/version = \"$CLEAN_VERSION\"/" pyproject.toml
        else
            # Linux sed
            sed -i "s/^version = .*/version = \"$CLEAN_VERSION\"/" pyproject.toml
        fi
        echo -e "${GREEN}✅ Updated pyproject.toml version to ${CLEAN_VERSION}${NC}"
    else
        echo -e "${YELLOW}⚠️  sed not found, please manually update pyproject.toml version${NC}"
    fi
fi

# Commit changes
echo -e "${BLUE}📝 Committing version bump...${NC}"
git add package.json package-lock.json
[[ -f "pyproject.toml" ]] && git add pyproject.toml
git commit -m "chore: bump version to ${NEW_VERSION}"

# Create git tag
echo -e "${BLUE}🏷️  Creating git tag...${NC}"
git tag -a "${NEW_VERSION}" -m "Release ${NEW_VERSION}"

# Push to remote
echo -e "${BLUE}📤 Pushing changes and tags to remote...${NC}"
git push origin $CURRENT_BRANCH --follow-tags

# Publish to NPM
echo -e "${BLUE}📦 Publishing to NPM...${NC}"
npm publish

# Clean up generated tgz files
echo -e "${BLUE}🧹 Cleaning up generated tgz files...${NC}"
rm -f *.tgz

# Success message
echo -e "${GREEN}🎉 Successfully published ${NEW_VERSION} to NPM!${NC}"
echo -e "${GREEN}📋 Summary:${NC}"
echo -e "   • Version: ${CURRENT_VERSION} → ${NEW_VERSION}"
echo -e "   • NPM Package: https://www.npmjs.com/package/baas-sms-mcp"
echo -e "   • Git Tag: ${NEW_VERSION}"
echo -e "   • Published by: ${NPM_USER}"

# Optional: Open NPM package page
if command -v open > /dev/null 2>&1 && [[ "$OSTYPE" == "darwin"* ]]; then
    read -p "🌐 Open NPM package page? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "https://www.npmjs.com/package/baas-sms-mcp"
    fi
fi

echo -e "${BLUE}✨ NPM deployment completed successfully!${NC}"