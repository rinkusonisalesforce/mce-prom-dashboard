# MCE Proactive Monitoring Dashboard

A modern React dashboard for tracking Marketing Cloud Engagement (MCE) Proactive Monitoring adoption metrics and signature leverage analysis.

Built with the **same data approach as the internal Proactive Monitoring Dashboard** - static JavaScript exports from CSV data.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ or Bun
- Python 3.8+ (for data generation)

### Installation

```bash
# Install dependencies
npm install
# or
bun install
```

### Development

```bash
# Start dev server
npm run dev
# or
bun dev

# Open http://localhost:5173
```

## 📊 Features

### MCE Adoption Metrics
- Total tenants with monitoring enabled
- Unique accounts count
- Total monitors configured
- Average monitors per tenant
- Regional breakdown (NA/EU)
- Monthly growth trend
- Top 10 tenants leaderboard

### Signature Leverage Analysis
- Total Signature contracts (from Org62)
- Leverage rate calculation
- Leveraged accounts (entitled + using)
- Not leveraged accounts (follow-up list)
- Non-signature accounts using ProM

## 🔄 Monthly Data Update Process

**Same workflow as the GitHub Proactive Monitoring Dashboard!**

### Step 1: Export Data (5 minutes)

```bash
# From UTDP (Monitoring Data):
# - Export NA monitoring → NA_June2026.csv
# - Export EU monitoring → EU_June2026.csv

# From Org62 (Contracts):
# - Export Signature contracts → contracts.csv

# Save all CSVs to: /Users/rinku.soni/prom-signature-extension/data/
```

### Step 2: Generate JavaScript Data

```bash
cd /Users/rinku.soni/mce-prom-dashboard
python3 generateMCEData.py
```

This creates `src/data/mceRealData.js` with all the calculated metrics.

### Step 3: Deploy

```bash
# Commit and push
git add .
git commit -m "Update MCE data - June 2026"
git push origin main

# Auto-deploys to GitHub Pages!
```

## 🌐 GitHub Pages Deployment

### One-Time Setup

1. **Create GitHub repository**
   ```bash
   cd /Users/rinku.soni/mce-prom-dashboard
   git init
   git add .
   git commit -m "Initial commit - MCE ProM Dashboard"
   ```

2. **Push to GitHub**
   ```bash
   # Create repo on GitHub first, then:
   git remote add origin https://github.com/YOUR_USERNAME/mce-prom-dashboard.git
   git branch -M main
   git push -u origin main
   ```

3. **Configure GitHub Pages**
   ```bash
   # Install gh-pages (already in package.json)
   npm install

   # Deploy
   npm run deploy
   ```

4. **Enable GitHub Pages**
   - Go to your repo → Settings → Pages
   - Source: `gh-pages` branch
   - Save

5. **Access dashboard**
   ```
   https://YOUR_USERNAME.github.io/mce-prom-dashboard/
   ```

### Monthly Updates (After Setup)

```bash
# 1. Export new CSVs (Org62 + UTDP)
# 2. Generate data
python3 generateMCEData.py

# 3. Deploy
npm run deploy

# Done! Dashboard auto-updates for all users
```

## 📁 Project Structure

```
mce-prom-dashboard/
├── src/
│   ├── components/
│   │   ├── StatCard.jsx           # Stat cards
│   │   ├── AdoptionChart.jsx      # Growth chart
│   │   ├── RegionalBreakdown.jsx  # Regional bars
│   │   ├── TopTenantsTable.jsx    # Top 10 table
│   │   └── LeverageTable.jsx      # Leverage tables
│   ├── data/
│   │   └── mceRealData.js         # ← Generated data (ES6 exports)
│   ├── App.jsx                    # Main component
│   ├── main.jsx                   # Entry point
│   └── index.css                  # Styles
├── generateMCEData.py             # Data generator script
├── package.json
├── vite.config.js
└── README.md
```

## 🔧 Data Generation Details

The `generateMCEData.py` script:

1. **Reads CSVs**
   - `NA_June2026.csv` - North America monitoring data
   - `EU_June2026.csv` - Europe monitoring data
   - `contracts.csv` - Org62 Signature contracts

2. **Processes Data**
   - Normalizes tenant IDs (strips E/M prefixes)
   - Matches monitoring to contracts
   - Calculates leverage metrics
   - Generates summary statistics

3. **Outputs JavaScript**
   - `src/data/mceRealData.js` - ES6 module exports
   - Same pattern as GitHub dashboard's `realData.js`

### Data File Format

The generated JavaScript file exports:

```javascript
export const mceSummaryStats = {
  promEnabledTenants: 836,
  totalAccounts: 658,
  totalMonitors: 2428,
  avgMonitorsPerTenant: 2.9,
  totalSignatureContracts: 3,
  leverageRate: 66.7,
  signatureLeveraged: 2,
  signatureNotLeveraged: 1,
  ...
};

export const topMCETenants = [ ... ];
export const signatureLeveragedAccounts = [ ... ];
// ... and more
```

## 🎯 Key Metrics Explained

### Adoption Metrics
- **Total MCE Tenants**: Count of unique tenant IDs with monitors > 0
- **Total Accounts**: Count of unique customer names
- **Total Monitors**: Sum of all monitors across all tenants
- **Avg Monitors/Tenant**: Total monitors ÷ total tenants

### Leverage Metrics
- **Signature Contracts**: Accounts with active Signature plans (from Org62)
- **Leveraged**: Signature accounts WITH monitoring enabled
- **Not Leveraged**: Signature accounts WITHOUT monitoring (follow-up list)
- **Leverage Rate**: (Leveraged ÷ Total Signature) × 100

### Matching Logic
- Contract tenant IDs (numeric) matched to UTDP EIDs (E/M prefix stripped)
- Invalid IDs rejected: `DELETED_*`, `00D*` (Salesforce org IDs)
- An account counts as leveraged if ANY of its tenant IDs has monitoring

## 🆘 Troubleshooting

### Dashboard shows "wrong data"

1. Check CSV files are in correct location:
   ```bash
   ls -la /Users/rinku.soni/prom-signature-extension/data/
   ```

2. Verify CSV format:
   ```
   # Monitoring CSVs:
   Customer_Name,EID,Total_Monitors_Enabled
   ALSAC,E524004459,12
   
   # Contracts CSV:
   Account Name,ServiceProvider,Contract Name,Tenant Id: Name
   Globex,Marketing Cloud,Signature Success - MC Engagement,524004459
   ```

3. Regenerate data:
   ```bash
   python3 generateMCEData.py
   ```

4. Check generated file:
   ```bash
   head -50 src/data/mceRealData.js
   ```

### Only 3 Signature contracts showing?

You're using **sample data**. Get real contracts from Org62:

```sql
SELECT Account.Name, ServiceProvider__c, Name, Tenant_Id__r.Name
FROM ServiceContract
WHERE Name LIKE '%Signature%MC Engagement%'
  AND ServiceProvider__c = 'Marketing Cloud'
  AND Status = 'Active'
```

Save as `contracts.csv` and regenerate.

## 🔐 Data Privacy

- CSVs contain customer data - **DO NOT commit to Git**
- Only commit the generated `mceRealData.js` (aggregated/anonymized)
- Keep CSVs in a separate, secure location

## 📈 Future Enhancements

- [ ] Add monthly comparison view
- [ ] Add export to Excel functionality
- [ ] Add filtering by region
- [ ] Add search functionality
- [ ] Add drill-down by customer

## 📝 License

Internal Salesforce tool - Not for external distribution

## 👥 Support

For questions or issues:
- Check this README first
- Review the generated data file: `src/data/mceRealData.js`
- Verify your CSV data sources
- Contact the dashboard owner for access/setup help

---

**Built with the same approach as the Proactive Monitoring Dashboard** 🚀
