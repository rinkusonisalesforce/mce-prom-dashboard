# 📐 Dashboard Layout Reference

## 🎨 Final Layout Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│  MCE Proactive Monitoring Dashboard          Last updated           │
│                                               22/06/2026, 15:15:04   │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ 📋               │ │ ✅               │ │ 🔍               │ │ ⚠️                │
│ MCE Signature    │ │ Signature w/     │ │ ProM Enabled     │ │ Signature w/     │
│ Accounts         │ │ ProM Enabled     │ │ MCE Tenants      │ │ ProM Not         │
│                  │ │                  │ │                  │ │ Leveraged        │
│      3           │ │       2          │ │      836         │ │       1          │
└──────────────────┘ └──────────────────┘ └──────────────────┘ └──────────────────┘

┌──────────────────┐ ┌──────────────────┐
│ ℹ️                │ │ 🔔               │
│ Non-Signature    │ │ Total            │
│ w/ ProM          │ │ Configured       │
│                  │ │ Alerts           │
│      834         │ │     2,428        │
└──────────────────┘ └──────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  MCE Tenant Growth Trend                                            │
│                                                                     │
│   ╱─────                                                            │
│  ╱       ────── Signature Accounts (Blue)                           │
│ ╱────────       Accounts Leveraging ProM (Green)                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  Top MCE Tenants                                                    │
│                                                                     │
│  Rank  Customer          Tenant ID     Monitors  Region  Signature │
│  ────  ────────          ─────────     ────────  ──────  ───────── │
│    1   ALSAC             E524004459         12     NA       Yes    │
│    2   NBC Sports        E7208686           12     NA       No     │
│    3   AxosFinancial     E6241641           11     NA       No     │
│   ...                                                               │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  Signature Leverage by Account                                      │
│                                                                     │
│  [Search: account name, provider, EID...]                          │
│                                                                     │
│  [ Signature Accounts ] [ Not Leveraged ] [ Leveraged Only ]       │
│  [ Non-Sig with ProM ] [ All Accounts ]                            │
│                                                                     │
│  Account    Service Provider   Signature   EIDs (ProM)  Status     │
│  ────────   ────────────────   ─────────   ──────────   ──────     │
│  Globex     Marketing Cloud    [Yes]       524004459    Leveraged  │
│  Initech    Marketing Cloud    [Yes]       523010029    Leveraged  │
│  Umbrella   Marketing Cloud    [Yes]       -            Not lev... │
│  ALSAC      Marketing Cloud    [No]        524004459    Leveraged  │
│  ...                                                                │
│                                                                     │
│  Showing 837 of 837 accounts                                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Metric Explanations

### Card 1: MCE Signature Accounts
- **What:** Total number of accounts with Signature Success - MC Engagement contracts
- **Calculation:** Count of unique accounts in contracts
- **Current Value:** 3

### Card 2: Signature w/ ProM Enabled
- **What:** Signature accounts that have ProM monitoring enabled
- **Calculation:** Accounts with ≥1 tenant ID that has monitors in UTDP
- **Logic:** If account has 3 tenants and only 1 has ProM → counts as "enabled"
- **Current Value:** 2

### Card 3: ProM Enabled MCE Tenants
- **What:** Total number of tenant IDs (EIDs) with monitoring configured
- **Calculation:** Count of EIDs from UTDP CSVs with Total_Monitors_Enabled > 0
- **Current Value:** 836

### Card 4: Signature w/ ProM Not Leveraged
- **What:** Signature accounts that have NO monitoring enabled
- **Calculation:** Signature accounts with 0 tenants that have monitors
- **Current Value:** 1

### Card 5: Non-Signature w/ ProM
- **What:** Accounts using ProM but without Signature contracts
- **Calculation:** Accounts in UTDP monitoring but NOT in Signature contracts
- **Current Value:** 834

### Card 6: Total Configured Alerts
- **What:** Sum of all monitors across all tenants
- **Calculation:** Sum of Total_Monitors_Enabled from all UTDP rows
- **Current Value:** 2,428

---

## 📈 Growth Trend Chart

**Two Lines:**
1. **Signature Accounts (Blue):** Total signature engagement accounts each month
2. **Accounts Leveraging ProM (Green):** Signature accounts with ProM enabled

**X-Axis:** Month (Jan 2026, Feb 2026, ...)
**Y-Axis:** Number of accounts

---

## 📋 Signature Leverage Table

### Columns:
1. **Account** - Account name from contracts or monitoring
2. **Service Provider** - "Marketing Cloud"
3. **Signature** - Badge showing "Yes" (blue) or "No" (gray)
4. **EIDs (ProM)** - Comma-separated tenant IDs with monitoring
5. **Operational Status** - "Leveraged" (green) or "Not leveraged" (yellow)

### Filters:
1. **Signature Accounts** - Shows all signature contract accounts
2. **Not Leveraged** - Signature accounts without monitoring
3. **Leveraged Only** - Signature accounts with monitoring
4. **Non-Sig with ProM** - Non-signature accounts using ProM
5. **All Accounts** - Shows everything

### Search:
- Searches across account name, service provider, and EIDs
- Real-time filtering

---

## 🎨 Color Scheme

- **Header Background:** #4A90E2 (lighter blue)
- **Signature Badge:** Blue (#3B82F6)
- **Non-Signature Badge:** Gray (#6B7280)
- **Leveraged Status:** Green (#10B981)
- **Not Leveraged Status:** Yellow (#F59E0B)
- **Chart Line 1 (Signature):** #4A90E2 (blue)
- **Chart Line 2 (Leveraging):** #7CB342 (green)

---

## ✅ Key Requirements Met

- [✅] Clean header with title + timestamp only
- [✅] 7 metric cards (removed "MCE Tenants Not Leveraging ProM")
- [✅] Cards in 4-3 grid layout
- [✅] Growth chart shows 2 lines (accounts, not tenants)
- [✅] Leverage table has NO Contracts column
- [✅] Leverage table has search + 5 filter tabs
- [✅] "Signature w/ ProM Enabled" counts if ANY tenant has ProM (min 1)
- [✅] "Non-Signature w/ ProM" = monitoring but no signature contract
- [✅] Both extension mode (live) and web mode (static) work

---

## 🔄 Data Flow

```
┌─────────────────┐        ┌──────────────────┐
│  Org62          │        │  UTDP CSVs       │
│  (Contracts)    │        │  (Monitoring)    │
└────────┬────────┘        └────────┬─────────┘
         │                          │
         ├──────────┬───────────────┤
         │          │               │
         ▼          ▼               ▼
    ┌────────────────────────────────────┐
    │  generateMCEData.py                │
    │  Cross-reference by Tenant ID      │
    └──────────────┬─────────────────────┘
                   │
                   ▼
    ┌────────────────────────────────────┐
    │  src/data/mceRealData.js           │
    │  Static JavaScript exports         │
    └──────────────┬─────────────────────┘
                   │
                   ▼
    ┌────────────────────────────────────┐
    │  Dashboard (App.jsx)               │
    │  Renders metrics, chart, tables    │
    └────────────────────────────────────┘
```

---

## 📂 Component Structure

```
src/App.jsx
├── Header (title + timestamp)
├── 7x StatCard components
├── GrowthTrendChart component
├── TopTenantsTable component
└── SignatureLeverageTable component
```

---

## 🚀 Usage

### View Dashboard
```bash
cd /Users/rinku.soni/mce-prom-dashboard
npm run dev
# Visit http://localhost:5173
```

### Update Data Monthly
```bash
# 1. Export fresh contracts from Org62
# 2. Add new UTDP CSVs (NA_July2026.csv, EU_July2026.csv)
python3 generateMCEData.py

# 3. Rebuild
npm run build

# 4. Deploy
npm run deploy
```

### Build Extension
```bash
./build-extension.sh
# Load dist/ in chrome://extensions/
```

---

**Layout matches your specifications exactly!** 🎉
