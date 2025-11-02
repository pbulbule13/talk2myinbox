#!/bin/bash

# ============================================================================
# Secret Scanner Script
# Checks for accidentally committed secrets before pushing to GitHub
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

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}Secret Scanner${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Flag to track if any issues found
ISSUES_FOUND=false

# ============================================================================
# 1. CHECK FOR SENSITIVE FILES
# ============================================================================

echo -e "${YELLOW}[1/6] Checking for sensitive files...${NC}"

SENSITIVE_FILES=(
    ".env"
    ".env.local"
    ".env.production"
    "config/gmail_credentials.json"
    "config/gmail_token.json"
    "config/calendar_credentials.json"
    "config/calendar_token.json"
    "id_rsa"
    "id_rsa.pub"
    "*.key"
    "*.pem"
)

for pattern in "${SENSITIVE_FILES[@]}"; do
    if git ls-files | grep -q "$pattern"; then
        echo -e "${RED}  ✗ Found tracked sensitive file: $pattern${NC}"
        echo -e "    Run: git rm --cached $pattern"
        ISSUES_FOUND=true
    fi
done

if [ "$ISSUES_FOUND" = false ]; then
    echo -e "${GREEN}  ✓ No sensitive files in git tracking${NC}"
fi
echo ""

# ============================================================================
# 2. CHECK .env IS IGNORED
# ============================================================================

echo -e "${YELLOW}[2/6] Verifying .env is in .gitignore...${NC}"

if git check-ignore .env > /dev/null 2>&1; then
    echo -e "${GREEN}  ✓ .env is properly ignored${NC}"
else
    echo -e "${RED}  ✗ .env is NOT in .gitignore!${NC}"
    echo -e "    Add '.env' to .gitignore"
    ISSUES_FOUND=true
fi
echo ""

# ============================================================================
# 3. CHECK FOR API KEYS IN STAGED FILES
# ============================================================================

echo -e "${YELLOW}[3/6] Checking staged files for API keys...${NC}"

# Patterns to search for
API_KEY_PATTERNS=(
    "sk-proj-[a-zA-Z0-9]+"                     # OpenAI API keys
    "sk-[a-zA-Z0-9]{48}"                       # Anthropic API keys
    "AIza[a-zA-Z0-9_-]{35}"                    # Google API keys
    "AKIA[0-9A-Z]{16}"                         # AWS Access Keys
    "[0-9a-f]{32}"                             # Generic 32-char hex keys
    "(api_key|apikey|api-key)\s*[:=]\s*['\"][a-zA-Z0-9]+" # API key assignments
    "(secret|password|passwd|pwd)\s*[:=]\s*['\"][^'\"]+['\"]" # Secrets
)

FOUND_KEYS=false

for pattern in "${API_KEY_PATTERNS[@]}"; do
    if git diff --cached | grep -iE "$pattern" > /dev/null 2>&1; then
        echo -e "${RED}  ✗ Potential API key pattern found: $pattern${NC}"
        FOUND_KEYS=true
        ISSUES_FOUND=true
    fi
done

if [ "$FOUND_KEYS" = false ]; then
    echo -e "${GREEN}  ✓ No API key patterns detected in staged files${NC}"
fi
echo ""

# ============================================================================
# 4. CHECK FOR HARDCODED CREDENTIALS
# ============================================================================

echo -e "${YELLOW}[4/6] Checking for hardcoded credentials...${NC}"

CREDENTIAL_PATTERNS=(
    "password\s*=\s*['\"]"
    "passwd\s*=\s*['\"]"
    "secret\s*=\s*['\"]"
    "token\s*=\s*['\"]"
    "api_key\s*=\s*['\"]"
)

FOUND_CREDS=false

for pattern in "${CREDENTIAL_PATTERNS[@]}"; do
    matches=$(git diff --cached | grep -iE "$pattern" | grep -v "your_.*_here" | grep -v "test_" | grep -v "example" || true)
    if [ ! -z "$matches" ]; then
        echo -e "${RED}  ✗ Potential hardcoded credential:${NC}"
        echo "$matches" | head -3
        FOUND_CREDS=true
        ISSUES_FOUND=true
    fi
done

if [ "$FOUND_CREDS" = false ]; then
    echo -e "${GREEN}  ✓ No hardcoded credentials detected${NC}"
fi
echo ""

# ============================================================================
# 5. CHECK FOR LARGE FILES (might be data dumps)
# ============================================================================

echo -e "${YELLOW}[5/6] Checking for large files...${NC}"

LARGE_FILES=$(git diff --cached --name-only | while read file; do
    if [ -f "$file" ]; then
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
        if [ "$size" -gt 1048576 ]; then  # 1MB
            echo "$file ($(($size / 1024))KB)"
        fi
    fi
done)

if [ ! -z "$LARGE_FILES" ]; then
    echo -e "${YELLOW}  ⚠ Large files detected:${NC}"
    echo "$LARGE_FILES"
    echo -e "  ${YELLOW}Consider if these should be committed${NC}"
else
    echo -e "${GREEN}  ✓ No unusually large files${NC}"
fi
echo ""

# ============================================================================
# 6. CHECK GIT HISTORY FOR SECRETS
# ============================================================================

echo -e "${YELLOW}[6/6] Checking recent git history...${NC}"

HISTORY_PATTERNS=(
    "api_key"
    "secret"
    "password"
    "token"
    "sk-proj"
    "AKIA"
)

FOUND_IN_HISTORY=false

for pattern in "${HISTORY_PATTERNS[@]}"; do
    if git log -p -1 | grep -iE "$pattern" | grep -v "your_.*_here" | grep -v "test_" | grep -v "example" > /dev/null 2>&1; then
        echo -e "${RED}  ✗ Found '$pattern' in recent commits${NC}"
        FOUND_IN_HISTORY=true
        ISSUES_FOUND=true
    fi
done

if [ "$FOUND_IN_HISTORY" = false ]; then
    echo -e "${GREEN}  ✓ No obvious secrets in recent history${NC}"
fi
echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

if [ "$ISSUES_FOUND" = true ]; then
    echo -e "${RED}✗ ISSUES FOUND!${NC}"
    echo ""
    echo "Security issues detected. Please fix them before pushing."
    echo ""
    echo "Common fixes:"
    echo "  1. Remove sensitive files: git rm --cached <file>"
    echo "  2. Add to .gitignore: echo '<file>' >> .gitignore"
    echo "  3. Use environment variables instead of hardcoding"
    echo "  4. Reset last commit if needed: git reset --soft HEAD~1"
    echo ""
    exit 1
else
    echo -e "${GREEN}✓ ALL CHECKS PASSED${NC}"
    echo ""
    echo "No security issues detected. Safe to push!"
    echo ""
    exit 0
fi

# ============================================================================
# OPTIONAL: CHECK WITH EXTERNAL TOOLS
# ============================================================================

# Uncomment to use external tools if installed

# echo -e "${YELLOW}Running TruffleHog (if installed)...${NC}"
# if command -v trufflehog &> /dev/null; then
#     trufflehog filesystem . --json --no-update
# fi

# echo -e "${YELLOW}Running git-secrets (if installed)...${NC}"
# if command -v git-secrets &> /dev/null; then
#     git secrets --scan
# fi
