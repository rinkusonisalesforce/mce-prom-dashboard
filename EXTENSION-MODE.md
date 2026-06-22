# 🚀 MCE Dashboard - Extension Mode with Live Org62 Data

## Overview

This dashboard now works in **TWO modes**:

### Mode 1: Chrome Extension (Live Org62 Data) ✨
- ✅ Pulls live contracts from Org62 via SOQL
- ✅ Reads UTDP CSVs from bundled `data/` folder
- ✅ **"Refresh data" button** - pulls fresh data
- ✅ Shows live contract count
- ✅ Cross-references in real-time
- ✅ **Same as your existing extension!**

### Mode 2: Web App (Static Data)
- ✅ Uses pre-generated JavaScript data
- ✅ No Org62 connection needed
- ✅ Deploy to GitHub Pages
- ✅ Share via URL

---

## 🔧 Building the Extension

```bash
cd /Users/rinku.soni/mce-prom-dashboard

# Install dependencies (first time only)
npm install

# Build extension
./build-extension.sh

# Or manually:
npm run build
cp public/manifest.json dist/
# ... (see script for details)
```

This creates a `dist/` folder with the complete extension.

---

## 📦 Installing the Extension

1. **Build the extension** (see above)

2. **Open Chrome Extensions**
   ```
   chrome://extensions/
   ```

3. **Enable Developer Mode**
   - Toggle switch in top-right corner

4. **Load Unpacked**
   - Click "Load unpacked" button
   - Select the `dist/` folder

5. **Done!** Click the extension icon to open dashboard

---

## 🔄 How It Works

### Data Flow (Extension Mode)

```
┌─────────────────────────────────────────────┐
│  User clicks "Refresh data"                 │
└─────────────────┬───────────────────────────┘
                  │
      ┌───────────┴───────────┐
      │                       │
      ▼                       ▼
┌─────────────┐         ┌─────────────┐
│   UTDP      │         │   Org62     │
│   CSVs      │         │   Live API  │
│  (bundled)  │         │  (SOQL)     │
└─────┬───────┘         └─────┬───────┘
      │                       │
      │  Read data/          │  Fetch via
      │  na_june2026.csv     │  JSForce +
      │  eu_june2026.csv     │  Session cookie
      │                       │
      └───────────┬───────────┘
                  │
                  ▼
          ┌───────────────┐
          │  ProM Core    │
          │  (core.js)    │
          │  Cross-ref    │
          │  + Calculate  │
          └───────┬───────┘
                  │
                  ▼
          ┌───────────────┐
          │  Dashboard    │
          │  Display      │
          └───────────────┘
```

### Code Structure

**Extension-specific files:**
- `public/manifest.json` - Extension manifest
- `public/jsforce.js` - Salesforce API library
- `src/utils/config.js` - Org62 config + SOQL
- `src/utils/sf-orgs.js` - Org62 connector
- `src/utils/core.js` - ProM cross-reference logic
- `src/utils/csv.js` - CSV parser

**React hooks:**
- `src/hooks/useOrg62Data.js` - Live Org62 fetcher
- `src/hooks/useMCEData.js` - Combines Org62 + UTDP data

**App:**
- `src/App.jsx` - Main dashboard component
  - Detects extension mode
  - Shows "Refresh data" button in extension mode
  - Falls back to static data in web mode

---

## 🎯 Features

### Extension Mode Features

✅ **Live Org62 Connection**
- Connects via session cookie (same as your existing extension)
- No manual login needed
- Uses JSForce library

✅ **SOQL Query**
```sql
SELECT Id, Name, ServiceProvider__c, Service_Contract_Status__c,
       AccountId, Account.Name, Tenant_Id__c, Tenant_Id__r.Name, EndDate
FROM ServiceContract
WHERE Name LIKE '%MC Engagement%'
  AND ServiceProvider__c = 'Marketing Cloud'
```

✅ **Refresh Data Button**
- Click to pull fresh data
- Shows loading state
- Displays contract count

✅ **Status Display**
```
Org62: 88353 contracts. UTDP latest: Jun 2026
Last updated: 20/06/2026, 20:40:32
```

✅ **Error Handling**
- Shows error banner if Org62 connection fails
- Prompts user to log in if no session cookie

---

## 📊 Data Sources

### UTDP CSVs (Bundled)

Place CSV files in `data/` folder:
```
data/
├── na_june2026.csv
├── eu_june2026.csv
├── na_july2026.csv
├── eu_july2026.csv
└── ...
```

Format:
```csv
Customer_Name,EID,Total_Monitors_Enabled
ALSAC,E524004459,12
NBC_Sports_Group,E7208686,12
...
```

### Org62 Contracts (Live)

Fetched via SOQL on button click:
- Service Provider: Marketing Cloud
- Contract Name contains: "MC Engagement"
- All statuses (Active, Cancelled, Expired)

---

## 🔄 Monthly Updates

### Extension Mode

```bash
# 1. Export new UTDP CSVs
#    Save as: data/na_july2026.csv, data/eu_july2026.csv

# 2. Rebuild extension
./build-extension.sh

# 3. Reload extension in Chrome
#    Chrome Extensions → Click reload icon

# 4. Open dashboard
#    Click extension icon

# 5. Refresh data
#    Click "Refresh data" button
```

### Web Mode (Static)

```bash
# 1. Export CSVs + contracts.csv

# 2. Generate static data
python3 generateMCEData.py

# 3. Deploy
npm run deploy
```

---

## 🆚 Comparison: Extension vs Original

| Feature | Your Original Extension | This New Version |
|---------|-------------------------|------------------|
| **Framework** | Vanilla JS | React + Vite |
| **Org62 Connection** | ✅ JSForce + cookie | ✅ JSForce + cookie |
| **UTDP CSVs** | ✅ Bundled in data/ | ✅ Bundled in data/ |
| **Cross-reference** | ✅ core.js | ✅ Same core.js |
| **Refresh Button** | ✅ Yes | ✅ Yes |
| **Live Contract Count** | ✅ Yes | ✅ Yes |
| **Growth Trend Chart** | ✅ Yes | ✅ Yes |
| **Top Tenants** | ✅ Yes | ✅ Yes |
| **Deploy as Web App** | ❌ No | ✅ Yes (bonus!) |
| **Modern UI** | Basic | ✅ Tailwind CSS |
| **TypeScript Support** | No | ✅ Can add |

---

## 🐛 Troubleshooting

### "No Salesforce session for Org62"

**Solution:**
1. Open https://org62.my.salesforce.com in Chrome
2. Log in
3. Click "Refresh data" again

### "Org62 connector not loaded"

**Solution:**
```bash
# Make sure you built the extension correctly
./build-extension.sh

# Check that these files exist in dist/:
ls dist/src/config.js
ls dist/src/sf-orgs.js
ls dist/src/core.js
ls dist/jsforce.js
```

### Extension not showing new data

**Solution:**
```bash
# Rebuild extension
./build-extension.sh

# Hard reload in Chrome
# Chrome Extensions → Click reload icon on your extension
```

### CSV files not found

**Solution:**
```bash
# Make sure CSVs are in data/ folder
ls data/na_june2026.csv
ls data/eu_june2026.csv

# Rebuild
./build-extension.sh
```

---

## 🚀 Next Steps

### Option A: Use as Extension (Recommended)

```bash
cd /Users/rinku.soni/mce-prom-dashboard
./build-extension.sh
# Install in Chrome
# Done!
```

### Option B: Use as Web App

```bash
# Deploy to GitHub Pages
npm run deploy
# Share URL with team
```

### Option C: Both!

Use extension for personal use (live data) + deploy web version for team (static data)

---

## 📝 Development

### Run in dev mode

```bash
npm run dev
# Opens on http://localhost:5173
# Will detect it's not in extension mode
# Shows "Offline mode - using static data"
```

### Build for production

```bash
# Web version
npm run build
# Output: dist/

# Extension version
./build-extension.sh
# Output: dist/ (with manifest.json)
```

---

## ✅ Success Checklist

Extension mode working if you see:

- [x] "Refresh data" button in header
- [x] "Org62: X contracts. UTDP latest: ..." status line
- [x] Clicking "Refresh data" fetches live contracts
- [x] Contract count updates
- [x] Dashboard shows fresh data

---

**You now have the exact same live Org62 functionality as your original extension, plus the ability to deploy as a web app!** 🎉
