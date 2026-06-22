# ⚡ Quick Start Guide

## First Time Setup (5 minutes)

```bash
cd /Users/rinku.soni/mce-prom-dashboard

# 1. Install dependencies
npm install

# 2. Generate data from your CSVs
python3 generateMCEData.py

# 3. Start development server
npm run dev

# 4. Open browser
# Visit: http://localhost:5173
```

## Monthly Update (2 minutes)

```bash
cd /Users/rinku.soni/mce-prom-dashboard

# 1. Update CSVs in /Users/rinku.soni/prom-signature-extension/data/
#    - NA_July2026.csv
#    - EU_July2026.csv
#    - contracts.csv

# 2. Run update script
./update-data.sh

# 3. Deploy to GitHub Pages
npm run deploy
```

## Deploy to GitHub Pages (One-time, 10 minutes)

```bash
# 1. Create GitHub repo
git init
git add .
git commit -m "Initial commit"

# 2. Push to GitHub (create repo first on github.com)
git remote add origin https://github.com/YOUR_USERNAME/mce-prom-dashboard.git
git push -u origin main

# 3. Deploy
npm run deploy

# 4. Enable GitHub Pages
# Go to repo Settings → Pages
# Source: gh-pages branch
# Save

# 5. Access dashboard
# https://YOUR_USERNAME.github.io/mce-prom-dashboard/
```

## Commands Reference

```bash
# Development
npm run dev          # Start dev server (http://localhost:5173)
npm run build        # Build for production
npm run preview      # Preview production build

# Data
python3 generateMCEData.py  # Generate JavaScript from CSVs
./update-data.sh            # Helper script with validation

# Deployment
npm run deploy       # Build + deploy to GitHub Pages
```

## Data Sources

**Monitoring Data (UTDP):**
- `/Users/rinku.soni/prom-signature-extension/data/NA_June2026.csv`
- `/Users/rinku.soni/prom-signature-extension/data/EU_June2026.csv`

**Contracts (Org62):**
- `/Users/rinku.soni/prom-signature-extension/data/contracts.csv`

**Generated Output:**
- `src/data/mceRealData.js` (ES6 module exports)

## Troubleshooting

**Dashboard shows old data?**
```bash
# Hard refresh browser
Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
```

**Wrong numbers?**
```bash
# Check CSV files
head -10 /Users/rinku.soni/prom-signature-extension/data/NA_June2026.csv

# Regenerate
python3 generateMCEData.py

# Test locally
npm run dev
```

**Deployment failed?**
```bash
# Reinstall dependencies
rm -rf node_modules
npm install

# Try again
npm run deploy
```

## Architecture

This dashboard uses the **exact same pattern as the GitHub Proactive Monitoring Dashboard**:

1. **Static data exports** (CSV → JavaScript)
2. **ES6 module imports** (same as `import { summaryStats } from './data/realData'`)
3. **React + Vite** (modern build setup)
4. **GitHub Pages deployment** (free hosting)

```
CSVs (UTDP + Org62)
    ↓
Python Script (generateMCEData.py)
    ↓
JavaScript File (mceRealData.js)
    ↓
React App (imports data)
    ↓
GitHub Pages (deployed)
    ↓
Users (view in browser)
```

## Need Help?

1. Check README.md for detailed docs
2. Check DEPLOYMENT-GUIDE.md for setup help
3. Review generateMCEData.py for data logic
4. Check src/data/mceRealData.js for actual data

---

**You're ready to go!** 🚀
