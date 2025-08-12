#!/bin/bash

# 통합 배포 스크립트 - NPM과 PyPI 동시 배포
# Usage: ./scripts/deploy.sh [patch|minor|major] [--test] [--npm-only] [--pypi-only]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Default values
VERSION_TYPE="patch"
USE_TEST_PYPI=false
DEPLOY_NPM=true
DEPLOY_PYPI=true
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        patch|minor|major)
            VERSION_TYPE="$1"
            shift
            ;;
        --test)
            USE_TEST_PYPI=true
            shift
            ;;
        --npm-only)
            DEPLOY_NPM=true
            DEPLOY_PYPI=false
            shift
            ;;
        --pypi-only)
            DEPLOY_NPM=false
            DEPLOY_PYPI=true
            shift
            ;;
        --help|-h)
            echo "통합 배포 스크립트 - NPM과 PyPI 동시 배포"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Arguments:"
            echo "  patch|minor|major    Version bump type (default: patch)"
            echo ""
            echo "Options:"
            echo "  --test              Use Test PyPI instead of production PyPI"
            echo "  --npm-only          Only deploy to NPM"
            echo "  --pypi-only         Only deploy to PyPI"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 minor            Deploy minor version to both NPM and PyPI"
            echo "  $0 patch --test     Deploy patch version, using Test PyPI"
            echo "  $0 major --npm-only Deploy major version only to NPM"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Error: Unknown argument '$1'${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Banner
echo -e "${PURPLE}╔══════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║          🚀 BaaS MCP 통합 배포           ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}📦 Configuration:${NC}"
echo -e "   • Version type: ${VERSION_TYPE}"
echo -e "   • Deploy to NPM: $([[ $DEPLOY_NPM == true ]] && echo "✅" || echo "❌")"
echo -e "   • Deploy to PyPI: $([[ $DEPLOY_PYPI == true ]] && echo "✅" || echo "❌")"
if [[ $DEPLOY_PYPI == true ]]; then
    echo -e "   • PyPI target: $([[ $USE_TEST_PYPI == true ]] && echo "Test PyPI 🧪" || echo "Production PyPI 🌍")"
fi
echo ""

# Confirm before proceeding
if [[ $DEPLOY_NPM == true ]] && [[ $DEPLOY_PYPI == true ]]; then
    DEPLOY_TARGET="NPM and PyPI"
elif [[ $DEPLOY_NPM == true ]]; then
    DEPLOY_TARGET="NPM only"
else
    DEPLOY_TARGET="PyPI only"
fi

echo -e "${YELLOW}⚠️  You are about to deploy ${VERSION_TYPE} version to ${DEPLOY_TARGET}${NC}"
read -p "Do you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🛑 Deployment cancelled${NC}"
    exit 0
fi

# Pre-deployment checks
echo -e "${BLUE}🔍 Running pre-deployment checks...${NC}"

# Check if we're in the right directory
if [[ ! -f "package.json" ]] || [[ ! -f "pyproject.toml" ]]; then
    echo -e "${RED}❌ Error: package.json or pyproject.toml not found. Please run this script from the project root.${NC}"
    exit 1
fi

# Check git status
if [[ -n $(git status --porcelain) ]]; then
    echo -e "${RED}❌ Error: Git working directory is not clean. Please commit or stash changes first.${NC}"
    git status --short
    exit 1
fi

# Check current branch
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

# Pull latest changes
echo -e "${BLUE}⬇️  Pulling latest changes from remote...${NC}"
git pull origin $CURRENT_BRANCH

echo -e "${GREEN}✅ Pre-deployment checks passed${NC}"
echo ""

# Deploy to NPM
if [[ $DEPLOY_NPM == true ]]; then
    echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              📦 NPM 배포                ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
    echo ""
    
    if [[ -x "$SCRIPT_DIR/deploy-npm.sh" ]]; then
        bash "$SCRIPT_DIR/deploy-npm.sh" "$VERSION_TYPE"
        NPM_SUCCESS=$?
    else
        echo -e "${RED}❌ Error: NPM deployment script not found or not executable${NC}"
        NPM_SUCCESS=1
    fi
    
    if [[ $NPM_SUCCESS -eq 0 ]]; then
        echo -e "${GREEN}✅ NPM deployment completed successfully${NC}"
    else
        echo -e "${RED}❌ NPM deployment failed${NC}"
        if [[ $DEPLOY_PYPI == true ]]; then
            echo -e "${YELLOW}⚠️  Continue with PyPI deployment? (y/N)${NC}"
            read -p "" -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        else
            exit 1
        fi
    fi
    echo ""
fi

# Deploy to PyPI
if [[ $DEPLOY_PYPI == true ]]; then
    echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              🐍 PyPI 배포               ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
    echo ""
    
    PYPI_ARGS="$VERSION_TYPE"
    if [[ $USE_TEST_PYPI == true ]]; then
        PYPI_ARGS="$PYPI_ARGS --test"
    fi
    
    if [[ -x "$SCRIPT_DIR/deploy-pypi.sh" ]]; then
        bash "$SCRIPT_DIR/deploy-pypi.sh" $PYPI_ARGS
        PYPI_SUCCESS=$?
    else
        echo -e "${RED}❌ Error: PyPI deployment script not found or not executable${NC}"
        PYPI_SUCCESS=1
    fi
    
    if [[ $PYPI_SUCCESS -eq 0 ]]; then
        echo -e "${GREEN}✅ PyPI deployment completed successfully${NC}"
    else
        echo -e "${RED}❌ PyPI deployment failed${NC}"
        exit 1
    fi
    echo ""
fi

# Final summary
echo -e "${PURPLE}╔══════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║           🎉 배포 완료 요약              ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════╝${NC}"
echo ""

# Get the deployed version
DEPLOYED_VERSION=$(node -p "require('./package.json').version" 2>/dev/null || \
                  python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])" 2>/dev/null || \
                  grep '^version = ' pyproject.toml | cut -d'"' -f2)

echo -e "${GREEN}📦 Deployed Version: ${DEPLOYED_VERSION}${NC}"
echo ""

if [[ $DEPLOY_NPM == true ]] && [[ $NPM_SUCCESS -eq 0 ]]; then
    echo -e "${GREEN}✅ NPM Package: https://www.npmjs.com/package/baas-sms-mcp${NC}"
    echo -e "   📥 Install: ${BLUE}npm install -g baas-sms-mcp${NC}"
fi

if [[ $DEPLOY_PYPI == true ]] && [[ $PYPI_SUCCESS -eq 0 ]]; then
    if [[ $USE_TEST_PYPI == true ]]; then
        echo -e "${GREEN}✅ Test PyPI Package: https://test.pypi.org/project/baas-sms-mcp${NC}"
        echo -e "   📥 Install: ${BLUE}pip install -i https://test.pypi.org/simple/ baas-sms-mcp${NC}"
    else
        echo -e "${GREEN}✅ PyPI Package: https://pypi.org/project/baas-sms-mcp${NC}"
        echo -e "   📥 Install: ${BLUE}pip install baas-sms-mcp${NC}"
    fi
fi

echo ""
echo -e "${GREEN}🏷️  Git Tag: v${DEPLOYED_VERSION}${NC}"
echo -e "${GREEN}📤 Changes pushed to: ${CURRENT_BRANCH}${NC}"
echo ""

# Post-deployment tasks
echo -e "${BLUE}🔄 Post-deployment tasks:${NC}"
echo -e "   • Update documentation if needed"
echo -e "   • Announce release in relevant channels"
echo -e "   • Monitor deployment for issues"
echo -e "   • Update changelog"
echo ""

echo -e "${PURPLE}✨ 통합 배포가 성공적으로 완료되었습니다! ✨${NC}"

# Optional: Create GitHub release
if command -v gh > /dev/null 2>&1; then
    echo ""
    read -p "🐙 Create GitHub release? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}📝 Creating GitHub release...${NC}"
        
        # Generate release notes
        RELEASE_NOTES=$(cat <<EOF
## 🚀 Release v${DEPLOYED_VERSION}

### 📦 Installation

**NPM:**
\`\`\`bash
npm install -g baas-sms-mcp
\`\`\`

**PyPI:**
\`\`\`bash
pip install baas-sms-mcp
\`\`\`

### 🔧 MCP Configuration

\`\`\`json
{
  "mcpServers": {
    "baas-sms-mcp": {
      "command": "npx",
      "args": ["baas-sms-mcp"],
      "env": {
        "BAAS_API_KEY": "your_api_key_here"
      }
    }
  }
}
\`\`\`

### 📋 What's Changed

- Version bump to ${DEPLOYED_VERSION}
- Bug fixes and improvements
- Updated dependencies

### 🔗 Links

- 📚 [Documentation](https://github.com/jjunmomo/BaaS-MCP#readme)
- 🐛 [Report Issues](https://github.com/jjunmomo/BaaS-MCP/issues)
- 💬 [Discussions](https://github.com/jjunmomo/BaaS-MCP/discussions)
EOF
)
        
        gh release create "v${DEPLOYED_VERSION}" \
            --title "Release v${DEPLOYED_VERSION}" \
            --notes "$RELEASE_NOTES" \
            --latest
            
        echo -e "${GREEN}✅ GitHub release created successfully${NC}"
    fi
fi