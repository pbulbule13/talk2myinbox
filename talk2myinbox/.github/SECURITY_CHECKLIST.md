# 🔒 GitHub Security Configuration Checklist

## Pre-Push Security Checklist

Before pushing code to GitHub, ensure you complete this checklist:

### ✅ Files & Configuration

- [ ] `.env` file is in `.gitignore`
- [ ] No `.env` file is tracked by git
- [ ] `config/*.json` files are ignored
- [ ] No API keys in code
- [ ] No credentials in git history
- [ ] `.env.example` has placeholder values only
- [ ] Pre-commit hooks are installed
- [ ] Security scripts are executable

### ✅ Local Verification

Run these commands before pushing:

```bash
# 1. Check what will be pushed
git status

# 2. Verify .env is ignored
git check-ignore .env

# 3. Check for tracked secrets
git ls-files | grep -E "\.env$|credentials|token"

# 4. Run secret scanner
bash scripts/check_secrets.sh

# 5. Review staged changes
git diff --cached
```

### ✅ GitHub Repository Settings

Once pushed, configure these GitHub settings:

#### 1. Secret Scanning
- Navigate to: **Settings → Security → Code security and analysis**
- Enable:
  - [x] **Secret scanning**
  - [x] **Push protection**
  - [x] **Secret scanning for GitHub Advanced Security**

#### 2. Dependency Management
- Enable:
  - [x] **Dependency graph**
  - [x] **Dependabot alerts**
  - [x] **Dependabot security updates**

#### 3. Code Scanning
- Enable:
  - [x] **Code scanning** (CodeQL analysis)

#### 4. Branch Protection
- Navigate to: **Settings → Branches**
- For `main` and `master` branches:
  - [x] Require pull request reviews
  - [x] Require status checks to pass
  - [x] Require branches to be up to date
  - [x] Include administrators

#### 5. Repository Visibility
- Set to:
  - [x] **Private** (recommended for projects with secrets)
  - [ ] **Public** (only if absolutely necessary and verified)

### ✅ GitHub Actions Security

If using GitHub Actions (CI/CD):

- [ ] Secrets stored in GitHub Secrets (not in code)
- [ ] Use `${{ secrets.API_KEY }}` in workflows
- [ ] Never echo secrets in logs
- [ ] Limit workflow permissions
- [ ] Review third-party actions

### ✅ Team Access

- [ ] Review collaborator access
- [ ] Use principle of least privilege
- [ ] Enable 2FA for all team members
- [ ] Regularly audit access logs

## Emergency Response

### If Secrets Are Exposed

1. **Immediately:**
   - [ ] Revoke/rotate all exposed credentials
   - [ ] Change all API keys
   - [ ] Update OAuth tokens

2. **Remove from Git:**
   ```bash
   # Remove from git history
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all

   # Force push (coordinate with team)
   git push --force --all
   ```

3. **Monitor:**
   - [ ] Check API usage logs
   - [ ] Review account activity
   - [ ] Set up alerts

4. **Document:**
   - [ ] Record incident
   - [ ] Document lessons learned
   - [ ] Update security procedures

## Regular Security Tasks

### Daily
- [ ] Review PR security checks
- [ ] Monitor Dependabot alerts

### Weekly
- [ ] Review access logs
- [ ] Check API usage

### Monthly
- [ ] Audit collaborator access
- [ ] Review and merge Dependabot PRs
- [ ] Run security audit

### Quarterly
- [ ] Rotate API keys
- [ ] Security training review
- [ ] Update security documentation

## Resources

- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [Dependabot](https://docs.github.com/en/code-security/dependabot)
- [Code Scanning](https://docs.github.com/en/code-security/code-scanning)
- [Security Best Practices](https://docs.github.com/en/code-security/getting-started/securing-your-organization)

---

**Last Updated:** November 2, 2025
**Review Date:** February 2, 2026
