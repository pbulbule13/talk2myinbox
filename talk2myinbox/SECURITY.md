# Security Policy

## 🔒 Security Overview

This document outlines security best practices for the **talk2myinbox** project to ensure no sensitive information (API keys, credentials, tokens) is exposed when pushing code to GitHub or other repositories.

---

## ⚠️ **CRITICAL: Never Commit These Files**

### Files That MUST Be Ignored

The following files contain sensitive information and should **NEVER** be committed:

```
# Environment Files
.env
.env.local
.env.development
.env.production
.env.*

# Credentials & Tokens
config/gmail_credentials.json
config/gmail_token.json
config/calendar_credentials.json
config/calendar_token.json
config/*.json (all JSON in config/)
*token.json
*.credentials.json

# SSH Keys
id_rsa
*.key
*.pem

# API Keys
Any file containing:
- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- GOOGLE_API_KEY
- ELEVENLABS_API_KEY
- Database passwords
- OAuth client secrets
```

---

## ✅ Verified Protection

### .gitignore Configuration

Our `.gitignore` file is configured to prevent committing sensitive files:

```gitignore
# Environment Variables (API Keys, Secrets)
.env
.env.*
!.env.example  # ← Only .env.example is allowed
.env.local
.env.production

# Credentials and Tokens
config/*.json
!config/.gitkeep
*.credentials.json
*token.json
*.key
*.pem
secrets/

# OAuth & API Keys
gmail_credentials.json
gmail_token.json
client_secret*.json
```

**✅ Protection Active** - These patterns prevent accidental commits.

---

## 🛡️ Security Checklist

### Before Every Commit

Run this checklist to ensure no secrets are exposed:

```bash
# 1. Check what files will be committed
git status

# 2. Review changes before staging
git diff

# 3. Verify no sensitive files are staged
git diff --cached

# 4. Check for secrets in staged files
make security-check

# 5. Run pre-commit checks
git commit  # (will trigger pre-commit hooks if configured)
```

### Required Actions

- [ ] Verify `.env` is in `.gitignore`
- [ ] Ensure `.env.example` has NO real values
- [ ] Confirm `config/*.json` files are ignored
- [ ] Check that tokens are in `.gitignore`
- [ ] Review git history for accidentally committed secrets
- [ ] Enable GitHub secret scanning
- [ ] Set up pre-commit hooks

---

## 🔍 How to Check for Exposed Secrets

### 1. Check Current Repository

```bash
# Search for potential secrets in tracked files
git grep -i "api_key"
git grep -i "secret"
git grep -i "password"
git grep -i "token"

# Check if sensitive files are tracked
git ls-files | grep ".env"
git ls-files | grep "credentials"
git ls-files | grep "token"
```

**Expected Result:** No sensitive files should appear.

### 2. Check Git History

```bash
# Check entire git history for secrets
git log --all --full-history --source --grep="api_key" -S "OPENAI_API_KEY"

# Find deleted files that might have contained secrets
git log --all --full-history -- .env
git log --all --full-history -- config/credentials.json
```

### 3. Use Automated Tools

```bash
# Install git-secrets
pip install git-secrets

# Scan repository
git secrets --scan

# Install truffleHog
pip install truffleHog

# Scan for secrets
trufflehog filesystem . --json
```

---

## 🚨 What to Do If Secrets Are Exposed

### If You Haven't Pushed Yet

```bash
# Remove from staging
git reset HEAD .env

# Remove from last commit
git reset --soft HEAD~1

# Remove from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

### If You Already Pushed to GitHub

**⚠️ CRITICAL: Assume the secret is compromised!**

1. **Immediately Rotate All Exposed Secrets**
   ```bash
   # Revoke and regenerate:
   - OpenAI API keys
   - Anthropic API keys
   - Google API credentials
   - ElevenLabs API keys
   - OAuth tokens
   - Database passwords
   ```

2. **Remove from Git History**
   ```bash
   # Use BFG Repo-Cleaner (recommended)
   brew install bfg  # or download from https://rtyley.github.io/bfg-repo-cleaner/

   bfg --delete-files .env
   bfg --replace-text passwords.txt  # File containing secrets to remove

   # Clean up
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive

   # Force push (⚠️ coordinate with team)
   git push --force --all
   git push --force --tags
   ```

3. **Notify Your Team**
   - Alert all developers
   - Update local repositories
   - Verify new secrets are in place

4. **Monitor for Unauthorized Access**
   - Check API usage logs
   - Review account activity
   - Set up alerts for unusual behavior

---

## 🔐 Best Practices

### 1. Use Environment Variables

**✅ CORRECT:**
```python
import os
api_key = os.getenv("OPENAI_API_KEY")
```

**❌ INCORRECT:**
```python
api_key = "sk-proj-abc123..."  # ← NEVER hardcode!
```

### 2. Use .env.example Template

**File: `.env.example`**
```bash
# DO use placeholder values
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# DON'T use real values
# OPENAI_API_KEY=sk-proj-abc123...  ← WRONG!
```

### 3. Separate Configs by Environment

```bash
.env.example           # Template (commit this)
.env                   # Local development (DON'T commit)
.env.development       # Dev environment (DON'T commit)
.env.staging           # Staging (DON'T commit)
.env.production        # Production (DON'T commit)
```

### 4. Use Secret Management Services

For production, use:
- **AWS Secrets Manager**
- **Azure Key Vault**
- **Google Secret Manager**
- **HashiCorp Vault**
- **GitHub Secrets** (for CI/CD)

### 5. Rotate Secrets Regularly

- Rotate API keys every 90 days
- Use short-lived tokens when possible
- Implement automated rotation
- Log rotation events

---

## 🔧 Setup Instructions

### 1. Configure Git Hooks (Prevent Commits)

Create a pre-commit hook:

```bash
# Create hooks directory
mkdir -p .git/hooks

# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

# Check for .env files
if git diff --cached --name-only | grep -q "\.env$"; then
    echo "❌ ERROR: Attempting to commit .env file!"
    echo "Remove it with: git reset HEAD .env"
    exit 1
fi

# Check for credentials
if git diff --cached --name-only | grep -q "credentials\.json"; then
    echo "❌ ERROR: Attempting to commit credentials!"
    exit 1
fi

# Check for API keys in staged files
if git diff --cached | grep -iE "(api_key|secret|password|token)\s*=\s*['\"][a-zA-Z0-9]"; then
    echo "❌ ERROR: Potential API key or secret found!"
    echo "Please use environment variables instead."
    exit 1
fi

echo "✅ Pre-commit checks passed"
EOF

# Make executable
chmod +x .git/hooks/pre-commit
```

### 2. Install Pre-commit Framework

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml (see below)

# Install hooks
pre-commit install
```

### 3. Configure GitHub Secret Scanning

1. Go to your GitHub repository
2. Navigate to **Settings → Security → Code security and analysis**
3. Enable:
   - **Secret scanning**
   - **Push protection**
   - **Dependency graph**
   - **Dependabot alerts**
   - **Dependabot security updates**

---

## 📋 Pre-commit Configuration

**File: `.pre-commit-config.yaml`**

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key
      - id: check-json
      - id: check-yaml

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
```

---

## 📝 Environment Variable Template

**File: `.env.example`** (Safe to commit)

```bash
# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

# Server Configuration
HOST=0.0.0.0
PORT=8000
ENV=development

# ============================================================================
# LLM API KEYS (Choose one or more)
# ============================================================================

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google Gemini
GOOGLE_API_KEY=your_google_api_key_here

# ============================================================================
# EMAIL PROVIDER (Gmail)
# ============================================================================

# Gmail API Credentials
GMAIL_CREDENTIALS_PATH=./config/gmail_credentials.json
GMAIL_TOKEN_PATH=./config/gmail_token.json

# Set to 'true' for demo mode without real Gmail
EMAIL_MOCK_MODE=false

# ============================================================================
# CALENDAR PROVIDER (Google Calendar)
# ============================================================================

# Google Calendar API Credentials
CALENDAR_CREDENTIALS_PATH=./config/calendar_credentials.json
CALENDAR_TOKEN_PATH=./config/calendar_token.json

# Set to 'true' for demo mode without real Calendar
CALENDAR_MOCK_MODE=false

# ============================================================================
# VOICE PROVIDER (ElevenLabs)
# ============================================================================

# ElevenLabs Text-to-Speech
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Voice Settings
TTS_PROVIDER=elevenlabs
STT_PROVIDER=whisper

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

# Logging
LOG_LEVEL=INFO
DEBUG_MODE=false

# Agent Settings
AGENT_NAME=Communications Assistant
DEFAULT_USER_ID=default_user

# ============================================================================
# SECURITY NOTES
# ============================================================================

# NEVER commit the actual .env file!
# NEVER share API keys publicly
# NEVER hardcode secrets in code
# USE this file as a template only
# COPY to .env and fill in real values
# KEEP .env in .gitignore

# ============================================================================
```

---

## 🎯 Quick Security Audit

Run this command to audit your repository:

```bash
# Check for ignored files being tracked
git ls-files -i --exclude-standard

# Search for potential secrets
grep -r "sk-" . --exclude-dir={.git,node_modules,venv}
grep -r "AKIA" . --exclude-dir={.git,node_modules,venv}  # AWS keys
grep -r "AIza" . --exclude-dir={.git,node_modules,venv}  # Google API keys

# Verify .env is ignored
git check-ignore .env

# Check if any sensitive files are staged
git status --porcelain | grep -E "(\.env|credentials|token)"
```

**Expected:** No sensitive files should be found.

---

## 📞 Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** create a public GitHub issue
2. **DO NOT** post in public forums
3. **DO** email security concerns privately
4. **DO** follow responsible disclosure

Contact: [Your security contact email]

---

## 🔄 Regular Security Tasks

### Weekly
- [ ] Review access logs
- [ ] Check for unauthorized API usage
- [ ] Monitor cost/usage metrics

### Monthly
- [ ] Audit user access permissions
- [ ] Review API key usage
- [ ] Update dependencies
- [ ] Run security scanner

### Quarterly
- [ ] Rotate API keys
- [ ] Review and update security policies
- [ ] Conduct security training
- [ ] Audit git history

### Annually
- [ ] Complete security audit
- [ ] Penetration testing
- [ ] Update incident response plan
- [ ] Review compliance requirements

---

## 📚 Additional Resources

- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Git Secrets Tool](https://github.com/awslabs/git-secrets)
- [TruffleHog](https://github.com/trufflesecurity/trufflehog)
- [pre-commit Framework](https://pre-commit.com/)

---

## ✅ Security Compliance Status

- [x] .gitignore configured
- [x] .env.example template created
- [x] Security documentation complete
- [ ] Pre-commit hooks installed
- [ ] GitHub secret scanning enabled
- [ ] Team training completed
- [ ] Incident response plan documented

---

**Last Updated:** November 2, 2025
**Security Policy Version:** 1.0
**Next Review:** February 2, 2026

---

## 🚀 Getting Started Securely

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Add your API keys to .env** (never commit this file)

3. **Verify .env is ignored:**
   ```bash
   git check-ignore .env  # Should output: .env
   ```

4. **Never commit sensitive files:**
   ```bash
   git status  # Check before committing
   ```

5. **Use the security checklist before every push**

---

**Remember: Security is everyone's responsibility! 🔒**
