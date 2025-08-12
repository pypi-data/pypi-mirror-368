#!/bin/bash

# PyPI 배포 자동화 스크립트
# Usage: ./scripts/deploy-pypi.sh [patch|minor|major] [--test]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
VERSION_TYPE=${1:-patch}
USE_TEST_PYPI=false

if [[ "$2" == "--test" ]] || [[ "$1" == "--test" ]]; then
    USE_TEST_PYPI=true
    if [[ "$1" == "--test" ]]; then
        VERSION_TYPE="patch"
    fi
fi

# Validate version type
if [[ ! "$VERSION_TYPE" =~ ^(patch|minor|major)$ ]]; then
    echo -e "${RED}❌ Error: Version type must be 'patch', 'minor', or 'major'${NC}"
    echo "Usage: $0 [patch|minor|major] [--test]"
    exit 1
fi

echo -e "${BLUE}🐍 Starting PyPI deployment process...${NC}"
echo -e "${BLUE}📦 Version type: ${VERSION_TYPE}${NC}"
if [[ "$USE_TEST_PYPI" == true ]]; then
    echo -e "${YELLOW}🧪 Using Test PyPI${NC}"
fi

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    echo -e "${RED}❌ Error: pyproject.toml not found. Please run this script from the project root.${NC}"
    exit 1
fi

# Check Python and pip
echo -e "${BLUE}🐍 Checking Python environment...${NC}"
if ! command -v python3 > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Python 3 not found${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ Found: ${PYTHON_VERSION}${NC}"

# Check for required tools
echo -e "${BLUE}🔧 Checking required tools...${NC}"

# Install/upgrade build tools
echo -e "${BLUE}📦 Installing/upgrading build tools...${NC}"
python3 -m pip install --upgrade pip build twine

# Check if git working directory is clean
if [[ -n $(git status --porcelain) ]]; then
    echo -e "${RED}❌ Error: Git working directory is not clean. Please commit or stash changes first.${NC}"
    git status --short
    exit 1
fi

# Get current version from pyproject.toml
CURRENT_VERSION=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])" 2>/dev/null || \
                 python3 -c "import tomli; print(tomli.load(open('pyproject.toml', 'rb'))['project']['version'])" 2>/dev/null || \
                 grep '^version = ' pyproject.toml | cut -d'"' -f2)

if [[ -z "$CURRENT_VERSION" ]]; then
    echo -e "${RED}❌ Error: Could not read current version from pyproject.toml${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Current version: ${CURRENT_VERSION}${NC}"

# Calculate new version
calculate_new_version() {
    local version=$1
    local type=$2
    
    # Split version into parts
    IFS='.' read -ra VERSION_PARTS <<< "$version"
    local major=${VERSION_PARTS[0]}
    local minor=${VERSION_PARTS[1]}
    local patch=${VERSION_PARTS[2]:-0}
    
    case $type in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
    esac
    
    echo "${major}.${minor}.${patch}"
}

NEW_VERSION=$(calculate_new_version "$CURRENT_VERSION" "$VERSION_TYPE")
echo -e "${BLUE}🔢 New version: ${NEW_VERSION}${NC}"

# Update version in pyproject.toml
echo -e "${BLUE}📝 Updating version in pyproject.toml...${NC}"
if command -v sed > /dev/null; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS sed
        sed -i '' "s/^version = .*/version = \"$NEW_VERSION\"/" pyproject.toml
    else
        # Linux sed
        sed -i "s/^version = .*/version = \"$NEW_VERSION\"/" pyproject.toml
    fi
else
    echo -e "${RED}❌ Error: sed not found${NC}"
    exit 1
fi

# Update version in package.json to keep in sync
if [[ -f "package.json" ]]; then
    echo -e "${BLUE}🔄 Syncing version in package.json...${NC}"
    npm version --no-git-tag-version "$NEW_VERSION"
    echo -e "${GREEN}✅ Updated package.json version to ${NEW_VERSION}${NC}"
fi

# Run tests if available
echo -e "${BLUE}🧪 Running tests...${NC}"
if [[ -f "pytest.ini" ]] || [[ -d "tests" ]] || python3 -c "import pytest" 2>/dev/null; then
    python3 -m pytest -v 2>/dev/null || echo -e "${YELLOW}⚠️  pytest not found or no tests available${NC}"
else
    echo -e "${YELLOW}⚠️  No test framework detected, skipping tests${NC}"
fi

# Clean previous builds
echo -e "${BLUE}🧹 Cleaning previous builds...${NC}"
rm -rf dist/ build/ *.egg-info/

# Build the package
echo -e "${BLUE}🔨 Building Python package...${NC}"
python3 -m build

# Verify build files
if [[ ! -d "dist" ]] || [[ -z "$(ls -A dist/)" ]]; then
    echo -e "${RED}❌ Error: Build failed or no files generated in dist/${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build completed. Generated files:${NC}"
ls -la dist/

# Check the built package
echo -e "${BLUE}🔍 Checking package integrity...${NC}"
python3 -m twine check dist/*

# Test installation (optional)
echo -e "${BLUE}🧪 Testing package installation...${NC}"
if command -v uv > /dev/null 2>&1; then
    # Use uv for faster testing
    TEMP_ENV=$(mktemp -d)
    python3 -m venv "$TEMP_ENV"
    source "$TEMP_ENV/bin/activate"
    pip install dist/*.whl
    python3 -c "import baas_sms_mcp; print('✅ Package imports successfully')"
    deactivate
    rm -rf "$TEMP_ENV"
else
    echo -e "${YELLOW}⚠️  uv not found, skipping installation test${NC}"
fi

# Commit version changes
echo -e "${BLUE}📝 Committing version bump...${NC}"
git add pyproject.toml
[[ -f "package.json" ]] && git add package.json package-lock.json
git commit -m "chore: bump Python version to ${NEW_VERSION}"

# Create git tag
echo -e "${BLUE}🏷️  Creating git tag...${NC}"
git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}"

# Configure repository URL
if [[ "$USE_TEST_PYPI" == true ]]; then
    REPO_URL="--repository testpypi"
    PACKAGE_URL="https://test.pypi.org/project/baas-sms-mcp"
    echo -e "${YELLOW}🧪 Uploading to Test PyPI...${NC}"
else
    REPO_URL=""
    PACKAGE_URL="https://pypi.org/project/baas-sms-mcp"
    echo -e "${BLUE}📦 Uploading to PyPI...${NC}"
fi

# Upload to PyPI
echo -e "${BLUE}📤 Publishing package...${NC}"
python3 -m twine upload $REPO_URL dist/*

# Push changes to git
echo -e "${BLUE}📤 Pushing changes and tags to remote...${NC}"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push origin $CURRENT_BRANCH --follow-tags

# Success message
echo -e "${GREEN}🎉 Successfully published v${NEW_VERSION} to PyPI!${NC}"
echo -e "${GREEN}📋 Summary:${NC}"
echo -e "   • Version: ${CURRENT_VERSION} → ${NEW_VERSION}"
if [[ "$USE_TEST_PYPI" == true ]]; then
    echo -e "   • Test PyPI Package: ${PACKAGE_URL}"
    echo -e "   • Install with: pip install -i https://test.pypi.org/simple/ baas-sms-mcp"
else
    echo -e "   • PyPI Package: ${PACKAGE_URL}"
    echo -e "   • Install with: pip install baas-sms-mcp"
fi
echo -e "   • Git Tag: v${NEW_VERSION}"

# Clean up build artifacts
echo -e "${BLUE}🧹 Cleaning up build artifacts...${NC}"
rm -rf build/ *.egg-info/

# Optional: Open PyPI package page
if command -v open > /dev/null 2>&1 && [[ "$OSTYPE" == "darwin"* ]]; then
    read -p "🌐 Open PyPI package page? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "$PACKAGE_URL"
    fi
fi

echo -e "${BLUE}✨ PyPI deployment completed successfully!${NC}"