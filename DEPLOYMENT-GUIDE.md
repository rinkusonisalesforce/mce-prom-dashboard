# 🚀 MCE Dashboard - Complete Deployment Guide

## Overview

This dashboard uses the **exact same deployment pattern as the GitHub Proactive Monitoring Dashboard**:

1. Owner exports data monthly (CSVs)
2. Owner runs Python script to generate JavaScript
3. Owner commits and pushes to GitHub
4. GitHub Pages auto-deploys
5. **Everyone sees updated dashboard instantly!**

---

## Part 1: One-Time Setup (15 minutes)

### Step 1: Install Dependencies

```bash
cd /Users/rinku.soni/mce-prom-dashboard

# Install Node dependencies
npm install
# or
bun install

# Verify Python is installed
python3 --version
```

### Step 2: Test Locally

```bash
# Generate data from current CSVs
python3 generateMCEData.py

# Start dev server
npm run dev

# Open http://localhost:5173
# ✅ Dashboard should load with your data
```

### Step 3: Create GitHub Repository

```bash
# Initialize Git
git init
git add .
git commit -m "Initial commit - MCE ProM Dashboard"

# Create repo on GitHub
# Go to: https://github.com/new
# Repo name: mce-prom-dashboard
# Visibility: Private (for internal use)
# Click "Create repository"

# Link local to remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/mce-prom-dashboard.git
git branch -M main
git push -u origin main
```

### Step 4: Deploy to GitHub Pages

```bash
# Build and deploy
npm run deploy

# This command:
# 1. Builds production files (dist/)
# 2. Pushes to gh-pages branch
# 3. GitHub Pages auto-deploys
```

### Step 5: Enable GitHub Pages

1. Go to your repo on GitHub
2. Click **Settings** → **Pages**
3. Under "Source":
   - Branch: `gh-pages`
   - Folder: `/ (root)`
4. Click **Save**
5. Wait 1-2 minutes for deployment

### Step 6: Access Dashboard

```
https://YOUR_USERNAME.github.io/mce-prom-dashboard/
```

**Share this URL with your team!** ✅

---

## Part 2: Monthly Update Workflow (5 minutes)

### Owner's Routine

```bash
# 1. Export fresh data (First Monday of each month)
# From UTDP:
#   - NA_July2026.csv
#   - EU_July2026.csv
# From Org62:
#   - contracts.csv

# Save to: /Users/rinku.soni/prom-signature-extension/data/

# 2. Update the Python script if needed (file names)
# Edit generateMCEData.py lines 11-13:
#   NA_FILE = Path('/path/to/data/NA_July2026.csv')
#   EU_FILE = Path('/path/to/data/EU_July2026.csv')

# 3. Generate new JavaScript data
cd /Users/rinku.soni/mce-prom-dashboard
python3 generateMCEData.py

# ✅ Check output: src/data/mceRealData.js updated

# 4. Test locally (optional but recommended)
npm run dev
# Open http://localhost:5173 and verify numbers look correct

# 5. Deploy
git add src/data/mceRealData.js
git commit -m "Update MCE data - July 2026"
git push origin main
npm run deploy

# Done! Dashboard updates for everyone in 1-2 minutes
```

### Everyone Else

```
1. Open: https://YOUR_USERNAME.github.io/mce-prom-dashboard/
2. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
3. See updated data!
```

---

## Part 3: Advanced Setup (Optional)

### Automated Monthly Updates

Create a script to streamline the process:

```bash
# File: update-dashboard.sh
#!/bin/bash

echo "🔄 MCE Dashboard Monthly Update"
echo "================================"
echo ""

# Check for new CSV files
echo "Step 1: Checking CSV files..."
DATA_DIR="/Users/rinku.soni/prom-signature-extension/data"

if [ ! -f "$DATA_DIR/NA_$(date +%B%Y).csv" ]; then
    echo "⚠️  Missing NA CSV for current month"
    echo "   Please export from UTDP first"
    exit 1
fi

if [ ! -f "$DATA_DIR/EU_$(date +%B%Y).csv" ]; then
    echo "⚠️  Missing EU CSV for current month"
    echo "   Please export from UTDP first"
    exit 1
fi

if [ ! -f "$DATA_DIR/contracts.csv" ]; then
    echo "⚠️  Missing contracts CSV"
    echo "   Please export from Org62 first"
    exit 1
fi

echo "✅ All CSV files found"
echo ""

# Generate data
echo "Step 2: Generating JavaScript data..."
cd /Users/rinku.soni/mce-prom-dashboard
python3 generateMCEData.py

if [ $? -ne 0 ]; then
    echo "❌ Data generation failed"
    exit 1
fi

echo "✅ Data generated successfully"
echo ""

# Show what changed
echo "Step 3: Checking changes..."
git diff --stat src/data/mceRealData.js

echo ""
read -p "Does this look correct? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborting. Please review the data."
    exit 1
fi

# Commit and deploy
echo "Step 4: Deploying..."
git add src/data/mceRealData.js
git commit -m "Update MCE data - $(date +%B\ %Y)"
git push origin main
npm run deploy

echo ""
echo "✅ Dashboard updated successfully!"
echo ""
echo "View at: https://YOUR_USERNAME.github.io/mce-prom-dashboard/"
echo ""
```

Make it executable:
```bash
chmod +x update-dashboard.sh
```

Use it:
```bash
./update-dashboard.sh
```

### Custom Domain (Optional)

If you want a custom URL like `mce-dashboard.salesforce.com`:

1. Create file: `public/CNAME`
   ```
   mce-dashboard.salesforce.com
   ```

2. Add DNS record (via Salesforce IT):
   ```
   Type: CNAME
   Name: mce-dashboard
   Value: YOUR_USERNAME.github.io
   ```

3. In repo Settings → Pages:
   - Custom domain: `mce-dashboard.salesforce.com`
   - Enforce HTTPS: ✅

---

## Part 4: Troubleshooting

### Issue: Dashboard shows old data after update

**Solution:**
```bash
# Clear browser cache
Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

# Or clear cache manually:
# Chrome: Settings → Privacy → Clear browsing data
```

### Issue: GitHub Pages not updating

**Solution:**
```bash
# Check deployment status
# Go to repo → Actions tab
# Look for latest workflow run

# Force redeploy
npm run deploy

# Check gh-pages branch exists
git branch -a
# Should see: remotes/origin/gh-pages
```

### Issue: "Module not found" error

**Solution:**
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Or clear npm cache
npm cache clean --force
npm install
```

### Issue: Data looks wrong

**Solution:**
```bash
# 1. Check CSV files
head -10 /Users/rinku.soni/prom-signature-extension/data/NA_June2026.csv
head -10 /Users/rinku.soni/prom-signature-extension/data/EU_June2026.csv
head -10 /Users/rinku.soni/prom-signature-extension/data/contracts.csv

# 2. Check generated data
head -100 src/data/mceRealData.js

# 3. Regenerate
python3 generateMCEData.py

# 4. Test locally
npm run dev
```

### Issue: Only 3 Signature contracts showing

**You're using sample data!**

Get real contracts from Org62:

```sql
SELECT Account.Name, ServiceProvider__c, Name, Tenant_Id__r.Name
FROM ServiceContract
WHERE Name LIKE '%Signature%MC Engagement%'
  AND ServiceProvider__c = 'Marketing Cloud'
  AND Status = 'Active'
```

Export as CSV, save as `contracts.csv`, regenerate.

---

## Part 5: Security & Access Control

### Who Can Access?

**Public repo** = Anyone with URL can view dashboard  
**Private repo** = Only people with repo access

Recommendation: **Private repo** for internal use

### Managing Access

```bash
# Repo Settings → Collaborators
# Add team members:
# - Read access: View dashboard only
# - Write access: Can update data
# - Admin access: Full control
```

### Data Privacy

- ❌ **Never commit CSV files** (contains customer data)
- ✅ **Only commit generated JavaScript** (aggregated data)
- ✅ **Use `.gitignore`** (already configured)

---

## Part 6: Handoff to New Owner

When transitioning ownership:

### Knowledge Transfer Checklist

- [ ] Share GitHub repo access
- [ ] Share data source access (UTDP, Org62)
- [ ] Walk through CSV export process
- [ ] Run update script together once
- [ ] Share this deployment guide
- [ ] Add them as repo admin

### Documentation to Share

1. This guide (DEPLOYMENT-GUIDE.md)
2. README.md
3. CSV export instructions
4. GitHub repo URL
5. Dashboard URL

---

## 🎉 You're Done!

Your MCE Dashboard is now:

✅ Deployed to GitHub Pages  
✅ Accessible via public URL  
✅ Auto-updates when you push  
✅ Uses same pattern as GitHub Proactive Monitoring Dashboard  
✅ Ready for monthly updates  

**Dashboard URL:**
```
https://YOUR_USERNAME.github.io/mce-prom-dashboard/
```

**Monthly routine:**
1. Export CSVs (5 min)
2. Run `python3 generateMCEData.py` (10 sec)
3. Run `npm run deploy` (30 sec)
4. Done! ✅

---

**Questions?** Check the troubleshooting section or review the README.md
