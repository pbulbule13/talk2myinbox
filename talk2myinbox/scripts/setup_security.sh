#!/bin/bash

# ============================================================================
# Security Setup Script
# Configures security measures for the talk2myinbox project
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Security Setup for talk2myinbox${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ============================================================================
# 1. VERIFY .gitignore
# ============================================================================

echo -e "${YELLOW}[1/7] Verifying .gitignore configuration...${NC}"

if [ -f ".gitignore" ]; then
    if grep -q "^\.env$" .gitignore; then
        echo -e "${GREEN}  ✓ .gitignore properly configured${NC}"
    else
        echo -e "${RED}  ✗ .env not found in .gitignore${NC}"
        echo "  Adding .env to .gitignore..."
        echo ".env" >> .gitignore
        echo -e "${GREEN}  ✓ Added .env to .gitignore${NC}"
    fi
else
    echo -e "${RED}  ✗ .gitignore not found${NC}"
    exit 1
fi
echo ""

# ============================================================================
# 2. CREATE .env FROM TEMPLATE
# ============================================================================

echo -e "${YELLOW}[2/7] Setting up environment file...${NC}"

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}  ✓ Created .env from .env.example${NC}"
        echo -e "  ${YELLOW}⚠ Remember to add your actual API keys to .env${NC}"
    else
        echo -e "${RED}  ✗ .env.example not found${NC}"
    fi
else
    echo -e "${GREEN}  ✓ .env already exists${NC}"
fi
echo ""

# ============================================================================
# 3. VERIFY .env IS IGNORED
# ============================================================================

echo -e "${YELLOW}[3/7] Verifying .env is ignored by git...${NC}"

if git check-ignore .env > /dev/null 2>&1; then
    echo -e "${GREEN}  ✓ .env is properly ignored by git${NC}"
else
    echo -e "${RED}  ✗ WARNING: .env is NOT ignored by git!${NC}"
    echo "  Please check your .gitignore configuration"
fi
echo ""

# ============================================================================
# 4. INSTALL PRE-COMMIT HOOKS
# ============================================================================

echo -e "${YELLOW}[4/7] Setting up pre-commit hooks...${NC}"

if command -v pre-commit &> /dev/null; then
    if [ -f ".pre-commit-config.yaml" ]; then
        pre-commit install
        echo -e "${GREEN}  ✓ Pre-commit hooks installed${NC}"
    else
        echo -e "${YELLOW}  ⚠ .pre-commit-config.yaml not found${NC}"
        echo "  Skipping pre-commit installation"
    fi
else
    echo -e "${YELLOW}  ⚠ pre-commit not installed${NC}"
    echo "  Install with: pip install pre-commit"
    echo "  Then run: pre-commit install"
fi
echo ""

# ============================================================================
# 5. CREATE GIT HOOKS
# ============================================================================

echo -e "${YELLOW}[5/7] Creating git hooks...${NC}"

# Create hooks directory
mkdir -p .git/hooks

# Pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook to prevent committing secrets

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "Running pre-commit security checks..."

# Check for .env files
if git diff --cached --name-only | grep -qE "^\.env$|^\.env\..*$" | grep -v ".env.example"; then
    echo -e "${RED}ERROR: Attempting to commit .env file!${NC}"
    echo "Remove with: git reset HEAD .env"
    exit 1
fi

# Check for credentials
if git diff --cached --name-only | grep -qE "credentials\.json|token\.json|\.key$|\.pem$"; then
    echo -e "${RED}ERROR: Attempting to commit credentials!${NC}"
    exit 1
fi

# Check for API keys in content
if git diff --cached | grep -iE "(api_key|secret|password)\s*[:=]\s*['\"][a-zA-Z0-9]{20,}" > /dev/null; then
    echo -e "${RED}ERROR: Potential API key found in staged files!${NC}"
    echo "Use environment variables instead of hardcoding secrets."
    exit 1
fi

echo -e "${GREEN}✓ Pre-commit checks passed${NC}"
exit 0
EOF

chmod +x .git/hooks/pre-commit
echo -e "${GREEN}  ✓ Pre-commit hook created${NC}"

# Pre-push hook
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
# Pre-push hook to run security checks

echo "Running pre-push security checks..."

# Run secret scanner if available
if [ -f "scripts/check_secrets.sh" ]; then
    bash scripts/check_secrets.sh
else
    echo "Secret scanner not found, skipping..."
fi
EOF

chmod +x .git/hooks/pre-push
echo -e "${GREEN}  ✓ Pre-push hook created${NC}"
echo ""

# ============================================================================
# 6. MAKE SCRIPTS EXECUTABLE
# ============================================================================

echo -e "${YELLOW}[6/7] Making security scripts executable...${NC}"

if [ -f "scripts/check_secrets.sh" ]; then
    chmod +x scripts/check_secrets.sh
    echo -e "${GREEN}  ✓ check_secrets.sh is executable${NC}"
fi

if [ -f "scripts/run_tests.sh" ]; then
    chmod +x scripts/run_tests.sh
    echo -e "${GREEN}  ✓ run_tests.sh is executable${NC}"
fi
echo ""

# ============================================================================
# 7. CREATE CONFIG DIRECTORY
# ============================================================================

echo -e "${YELLOW}[7/7] Setting up config directory...${NC}"

mkdir -p config/credentials
touch config/.gitkeep
touch config/credentials/.gitkeep

echo -e "${GREEN}  ✓ Config directory created${NC}"
echo ""

# ============================================================================
# VERIFY NO SECRETS ARE CURRENTLY TRACKED
# ============================================================================

echo -e "${YELLOW}Checking for currently tracked secrets...${NC}"

TRACKED_SECRETS=false

# Check for .env in git
if git ls-files | grep -q "^\.env$"; then
    echo -e "${RED}  ✗ .env is currently tracked by git!${NC}"
    echo "  Remove with: git rm --cached .env"
    TRACKED_SECRETS=true
fi

# Check for credentials
if git ls-files | grep -qE "credentials\.json|token\.json"; then
    echo -e "${RED}  ✗ Credential files are tracked by git!${NC}"
    echo "  Remove with: git rm --cached config/*.json"
    TRACKED_SECRETS=true
fi

if [ "$TRACKED_SECRETS" = false ]; then
    echo -e "${GREEN}  ✓ No secrets currently tracked${NC}"
fi
echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Security Setup Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo "✅ Configured:"
echo "  • .gitignore for sensitive files"
echo "  • Git pre-commit hooks"
echo "  • Git pre-push hooks"
echo "  • Environment file template"
echo "  • Config directory structure"
echo ""

echo "📝 Next Steps:"
echo ""
echo "  1. Edit .env and add your actual API keys"
echo "     (NEVER commit this file!)"
echo ""
echo "  2. Install pre-commit framework (optional but recommended):"
echo "     pip install pre-commit"
echo "     pre-commit install"
echo ""
echo "  3. Test the hooks:"
echo "     git add .env  # Should be prevented"
echo ""
echo "  4. Run security check:"
echo "     bash scripts/check_secrets.sh"
echo ""
echo "  5. Enable GitHub secret scanning:"
echo "     Settings → Security → Code security and analysis"
echo ""

if [ "$TRACKED_SECRETS" = true ]; then
    echo -e "${RED}⚠️  WARNING: Secrets are currently tracked by git!${NC}"
    echo "   Follow the removal instructions above."
    echo ""
fi

echo -e "${GREEN}🔒 Your repository is now protected!${NC}"
echo ""
