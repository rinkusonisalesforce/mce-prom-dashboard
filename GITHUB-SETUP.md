# 🚀 Push to GitHub - Step by Step

## ✅ Current Status

Your local Git repository is ready:
- ✅ Git initialized
- ✅ All files committed
- ✅ Branch renamed to `main`

---

## 📝 Step 1: Create GitHub Repository

### Option A: Via GitHub Website (Easiest)

1. Go to https://github.com/new

2. Fill in:
   ```
   Repository name: mce-prom-dashboard
   Description: MCE Proactive Monitoring Dashboard with live Org62 integration
   Visibility: ● Private (recommended - then add specific collaborators)
   ```
   
   **Private is recommended** because:
   - ✅ Contains Salesforce internal tool references (Org62, UTDP)
   - ✅ You can control exactly who has access
   - ✅ You can add specific team members as collaborators

3. **Important:** Do NOT check these boxes:
   - ❌ Add a README file
   - ❌ Add .gitignore
   - ❌ Choose a license
   
   (We already have these files!)

4. Click **"Create repository"**

5. You'll see a page with commands - **Copy the URL** that looks like:
   ```
   https://github.com/YOUR_USERNAME/mce-prom-dashboard.git
   ```

### Option B: Via GitHub CLI (If you have `gh` installed)

```bash
cd /Users/rinku.soni/mce-prom-dashboard
gh repo create mce-prom-dashboard --private --source=. --remote=origin
```

---

## 📤 Step 2: Push to GitHub

Once you have the GitHub repo URL, run:

```bash
cd /Users/rinku.soni/mce-prom-dashboard

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/mce-prom-dashboard.git

# Push to GitHub
git push -u origin main
```

**Example:**
```bash
# If your username is "johndoe":
git remote add origin https://github.com/johndoe/mce-prom-dashboard.git
git push -u origin main
```

---

## ✅ Step 3: Verify

Once pushed, visit:
```
https://github.com/YOUR_USERNAME/mce-prom-dashboard
```

You should see:
- ✅ All your files
- ✅ README.md displayed
- ✅ 33 files committed
- ✅ "Initial commit - MCE ProM Dashboard..." message

---

## 🌐 Step 4: Deploy to GitHub Pages (Optional)

If you want to deploy the **web version** (static data, no Org62):

```bash
cd /Users/rinku.soni/mce-prom-dashboard

# Install dependencies (if not already)
npm install

# Deploy
npm run deploy
```

This will:
1. Build production version
2. Create `gh-pages` branch
3. Push to GitHub
4. Auto-deploy to: `https://YOUR_USERNAME.github.io/mce-prom-dashboard/`

### Enable GitHub Pages

1. Go to your repo → **Settings** → **Pages**
2. Under "Source":
   - Branch: `gh-pages`
   - Folder: `/ (root)`
3. Click **Save**
4. Wait 1-2 minutes
5. Access at: `https://YOUR_USERNAME.github.io/mce-prom-dashboard/`

---

## 🔐 Security Note

### What's Safe to Commit?

✅ **Safe (already committed):**
- Source code
- Static data (mceRealData.js - aggregated metrics)
- Documentation
- Configuration (Org62 URL, SOQL query)

❌ **NEVER commit:**
- Raw CSV files with customer data
- Session cookies
- Access tokens
- Credentials

**Good news:** Your `.gitignore` is already set up to block CSV files!

---

## 📊 Repository Structure

Once on GitHub, you'll have:

```
mce-prom-dashboard/
├── README.md (displayed on GitHub)
├── EXTENSION-MODE.md (extension guide)
├── DEPLOYMENT-GUIDE.md (GitHub Pages guide)
├── QUICK-START.md (quick reference)
├── src/ (React components)
├── public/ (static assets)
├── package.json
└── ... (all your files)
```

---

## 🤝 Sharing with Team

### Share Extension

**Option 1: Via GitHub Releases**

1. Go to your repo → **Releases** → **Create a new release**
2. Tag: `v1.0.0`
3. Title: `MCE ProM Dashboard v1.0.0`
4. Upload: `dist.zip` (created by build-extension.sh)
5. Publish release

Team downloads, unzips, loads in Chrome.

**Option 2: Direct Clone**

Team members can:
```bash
git clone https://github.com/YOUR_USERNAME/mce-prom-dashboard.git
cd mce-prom-dashboard
npm install
./build-extension.sh
# Load dist/ in Chrome
```

### Share Web Version

Just share the URL:
```
https://YOUR_USERNAME.github.io/mce-prom-dashboard/
```

---

## 🔄 Future Updates

### Push Updates

```bash
cd /Users/rinku.soni/mce-prom-dashboard

# Make changes...

# Commit
git add .
git commit -m "Update MCE data for July 2026"

# Push
git push origin main
```

### Update Web Version

```bash
# Regenerate data
python3 generateMCEData.py

# Redeploy
npm run deploy
```

---

## 🆘 Troubleshooting

### "remote origin already exists"

```bash
# Remove existing remote
git remote remove origin

# Add correct one
git remote add origin https://github.com/YOUR_USERNAME/mce-prom-dashboard.git
```

### "failed to push"

```bash
# Pull first (if repo has files)
git pull origin main --allow-unrelated-histories

# Then push
git push -u origin main
```

### "Authentication failed"

```bash
# Use GitHub CLI
gh auth login

# Or use SSH instead of HTTPS
git remote set-url origin git@github.com:YOUR_USERNAME/mce-prom-dashboard.git
```

---

## ✅ Quick Commands Reference

```bash
# Check status
git status

# View remote
git remote -v

# Push updates
git add .
git commit -m "Your message"
git push

# Deploy web version
npm run deploy
```

---

## 🎯 What's Next After Pushing?

1. ✅ **Test the extension build**
   ```bash
   ./build-extension.sh
   ```

2. ✅ **Load in Chrome**
   - chrome://extensions/
   - Load unpacked → dist/

3. ✅ **Click "Refresh data"**
   - Verify live Org62 connection works

4. ✅ **Share with team**
   - Send GitHub URL
   - Or deploy web version

---

**Ready to push? Just need your GitHub repository URL!** 🚀

Once you create the repo on GitHub, come back and run:
```bash
git remote add origin https://github.com/YOUR_USERNAME/mce-prom-dashboard.git
git push -u origin main
```
