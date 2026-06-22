# 📦 Git Repositories

Your MCE ProM Dashboard is now on **TWO** repositories!

---

## 🌐 Repository URLs

### GitHub (Public/External)
**URL:** https://github.com/rinkusonisalesforce/mce-prom-dashboard  
**Use for:** External sharing, backup, CI/CD  
**Live Dashboard:** https://rinkusonisalesforce.github.io/mce-prom-dashboard/

### git.soma (Internal Salesforce)
**URL:** https://git.soma.salesforce.com/rinku-soni/mce-prom-dashboard  
**Use for:** Internal team collaboration, secure access  
**Access:** Salesforce employees only

---

## 🚀 How to Push Changes

### Push to Both Repositories at Once
```bash
cd /Users/rinku.soni/mce-prom-dashboard
./push-both.sh
```

### Push to Individual Repositories
```bash
# GitHub only
git push origin main

# git.soma only
git push soma main
```

---

## 📋 Your Git Remotes

```bash
origin → https://github.com/rinkusonisalesforce/mce-prom-dashboard.git
soma   → git@git.soma.salesforce.com:rinku-soni/mce-prom-dashboard.git
```

### View Remotes
```bash
git remote -v
```

---

## 🔄 Regular Workflow

### 1. Make Changes
```bash
# Edit files...
python3 generateMCEData.py  # Regenerate data
npm run dev                 # Test locally
```

### 2. Commit Changes
```bash
git add .
git commit -m "Update dashboard - July 2026 data"
```

### 3. Push to Both Repos
```bash
./push-both.sh
```

### 4. Deploy GitHub Pages
```bash
npm run deploy
```

---

## 🎯 Shareable Links

### For External Users (Anyone)
Share the **GitHub Pages** live dashboard:
```
https://rinkusonisalesforce.github.io/mce-prom-dashboard/
```

### For Salesforce Team (Internal Only)
Share the **git.soma** repository:
```
https://git.soma.salesforce.com/rinku-soni/mce-prom-dashboard
```

Team members can clone:
```bash
git clone git@git.soma.salesforce.com:rinku-soni/mce-prom-dashboard.git
```

### For GitHub Collaborators
Share the **GitHub** repository:
```
https://github.com/rinkusonisalesforce/mce-prom-dashboard
```

---

## 🔧 Troubleshooting

### Permission Denied (git.soma)
Make sure your SSH key is added:
1. Copy your public key: `cat ~/.ssh/id_ed25519.pub`
2. Add to: https://git.soma.salesforce.com/settings/keys

### GitHub Pages Not Updating
```bash
npm run deploy  # Redeploy
```

### See Both Repo Status
```bash
git remote -v
git branch -a
```

---

## ✅ Current Status

- ✅ GitHub repository: **Active**
- ✅ git.soma repository: **Active**
- ✅ GitHub Pages: **Deployed**
- ✅ Push helper script: **Created** (`push-both.sh`)

---

**Last Updated:** 2026-06-22
