# Git Setup Guide - RealtyAI

## ✅ Project is Ready for Git!

The repository has been initialized and the initial commit has been created.

### **Current Status:**
```
✅ Git repository initialized
✅ Initial commit created (100 files)
✅ .gitignore configured (root, backend, frontend, docker)
✅ Sensitive files excluded (.env, uploads, .db, __pycache__)
✅ LICENSE added (MIT)
✅ README.md updated
✅ Documentation complete
```

### **Next Steps:**

#### **1. Create GitHub Repository**

```bash
# Go to GitHub and create a new repository:
# 1. Go to github.com
# 2. Click "New" (or "+" → "New repository")
# 3. Name: realtyai
# 4. Description: AI-powered real estate listing platform
# 5. Public/Private: Your choice
# 6. DO NOT initialize with README, .gitignore, or license
# 7. Click "Create repository"
```

#### **2. Push to GitHub**

```bash
# Copy the repository URL from GitHub
# Example: https://github.com/yourusername/realtyai.git

# Add remote
git remote add origin https://github.com/yourusername/realtyai.git

# Verify remote
git remote -v

# Push to GitHub
git push -u origin main

# If using SSH:
git remote add origin git@github.com:yourusername/realtyai.git
git push -u origin main
```

#### **3. Deploy to Render (Optional)**

After pushing to GitHub:

```bash
# 1. Go to render.com
# 2. Sign up with GitHub
# 3. New → Import from GitHub
# 4. Select "realtyai" repository
# 5. Render will auto-detect render.yaml
# 6. Add environment variables
# 7. Deploy!
```

[See deployment guide →](DEPLOYMENT.md)

---

## 📋 Git Commands Reference

### **Basic Commands**

```bash
# Check status
git status

# View changes
git diff

# Add files
git add .

# Add specific file
git add README.md

# Commit changes
git commit -m "Your commit message"

# View commit history
git log --oneline

# View detailed log
git log --graph --oneline --all
```

### **Branching**

```bash
# Create new branch
git checkout -b feature/amazing-feature

# Switch branch
git checkout feature/amazing-feature

# Or (Git 2.23+)
git switch feature/amazing-feature

# List branches
git branch -a

# Create and switch (Git 2.23+)
git switch -c feature/amazing-feature

# Merge branch
git checkout main
git merge feature/amazing-feature

# Delete branch (after merge)
git branch -d feature/amazing-feature
```

### **Remote**

```bash
# Add remote
git remote add origin https://github.com/username/repo.git

# View remotes
git remote -v

# Push to remote
git push origin main

# Pull from remote
git pull origin main

# Fetch without merge
git fetch origin

# Remove remote
git remote remove origin
```

### **Undo Changes**

```bash
# Unstage file
git reset HEAD file.txt

# Discard changes in file
git checkout -- file.txt

# Or (Git 2.23+)
git restore file.txt

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

### **Stashing**

```bash
# Save changes without commit
git stash

# View stashes
git stash list

# Apply stash
git stash pop

# Apply and keep
git stash apply

# Delete stash
git stash drop
```

---

## 🔐 Security Checklist

### **Files Excluded from Git:**

```bash
✅ .env (environment variables)
✅ backend/.env
✅ docker/.env
✅ uploads/ (user files)
✅ *.db (databases)
✅ __pycache__/
✅ venv/ (virtual environments)
✅ *.log (logs)
✅ .DS_Store (Mac files)
```

### **Before Every Commit:**

```bash
# 1. Check for sensitive files
git status

# 2. Verify .env files are NOT staged
git status | grep .env

# 3. Check what will be committed
git diff --cached

# 4. Look for secrets
grep -r "password\|secret\|key" --cached 2>/dev/null
```

### **If You Accidentally Committed Secrets:**

```bash
# 1. Revoke the secret immediately!
# 2. Remove from git history:
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/secret" \
  --prune-empty --tag-name-filter cat -- --all

# 3. Force push (WARNING: rewrites history!)
git push origin main --force

# 4. Rotate the secret (generate new API key, password, etc.)
```

---

## 📝 Commit Message Guidelines

### **Format:**
```
<type>(<scope>): <subject>

<body optional>

<footer optional>
```

### **Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Formatting (no code changes)
- `refactor` - Code refactoring
- `test` - Adding tests
- `chore` - Maintenance tasks

### **Examples:**

```bash
# Good
git commit -m "feat(auth): add password validation"

git commit -m "fix(docker): resolve health check timeout"

git commit -m "docs: update deployment guide"

git commit -m "refactor(models): simplify user model"

# Great (with body)
git commit -m "feat(api): add rate limiting

- Add slowapi for rate limiting
- Limit login to 5 attempts/minute
- Limit registration to 3 attempts/minute
- Add rate limit headers to responses"
```

---

## 🌿 Branching Strategy

### **Main Branches:**
```
main          - Production-ready code
develop       - Development branch (optional)
```

### **Feature Branches:**
```
feature/user-profiles
feature/saved-searches
feature/mobile-app
```

### **Bug Fix Branches:**
```
fix/login-issue
fix/payment-error
fix/cors-error
```

### **Hotfix Branches:**
```
hotfix/security-patch
hotfix/payment-bug
```

---

## 🔄 Workflow Example

### **1. Start New Feature**

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/amazing-feature
```

### **2. Make Changes**

```bash
# Edit files
# ...

# Check what changed
git status
git diff

# Add changes
git add .

# Commit
git commit -m "feat: add amazing feature"
```

### **3. Push & Create PR**

```bash
# Push branch
git push -u origin feature/amazing-feature

# Go to GitHub → Pull Requests → New Pull Request
# Select your branch → Create PR
```

### **4. Review & Merge**

```bash
# After approval, merge on GitHub
# Then update local:
git checkout main
git pull origin main

# Delete feature branch
git branch -d feature/amazing-feature
git push origin --delete feature/amazing-feature
```

---

## 🎯 Best Practices

### **✅ DO:**
- Commit often with clear messages
- Use feature branches
- Pull before pushing
- Review your changes before commit
- Keep commits focused (one feature per commit)
- Update main branch regularly

### **❌ DON'T:**
- Commit sensitive data (.env, passwords, keys)
- Commit large files (images, videos, etc.)
- Force push to shared branches
- Commit unfinished code to main
- Write "fix" or "update" as commit messages
- Ignore merge conflicts

---

## 🛠️ Troubleshooting

### **"fatal: not a git repository"**
```bash
# Initialize git
git init
```

### **"fatal: the upstream branch of your current branch does not exist"**
```bash
# Set upstream
git push -u origin main
```

### **"Permission denied (publickey)"**
```bash
# Use HTTPS instead of SSH
git remote set-url origin https://github.com/username/repo.git
# Or configure SSH keys
```

### **"error: failed to push some refs"**
```bash
# Pull first
git pull origin main
# Then push again
git push
```

### **"hint: These lines were added by a merge tool"**
```bash
# Resolve conflicts manually
# Then:
git add resolved-file.txt
git commit
```

---

## 📚 Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Git Cheat Sheet](https://github.com/git-guides/git-cheat-sheet)
- [Happy Git and GitHub](https://happylittleman.io/git/)

---

## ✅ Ready to Push?

```bash
# Final check
git status
git log --oneline -1

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/realtyai.git

# Push!
git push -u origin main

# 🎉 Done!
```

---

**Your repository is ready!** 🚀

Next step: Create GitHub repository and push!
