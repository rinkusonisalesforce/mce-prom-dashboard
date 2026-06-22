# 📊 Contracts File Setup - Excel Format

## 📁 Where to Put Contracts File

Place your Excel file here:
```
/Users/rinku.soni/prom-signature-extension/data/contracts.xlsx
```

Or alternatively:
```
/Users/rinku.soni/mce-prom-dashboard/data/contracts.xlsx
```

---

## 📋 Required Excel Format

Your Excel file should have these columns:

| Column Name | Example | Description |
|-------------|---------|-------------|
| **Account Name** | Globex Corporation | Customer account name |
| **ServiceProvider** | Marketing Cloud | Should be "Marketing Cloud" |
| **Contract Name** | Signature Success - MC Engagement | Contract type |
| **Tenant Id: Name** | 524004459 | Tenant ID (numeric) |
| **Service_Contract_Status__c** | Active | Status: Active/Cancelled/Expired |
| **EndDate** | 2027-12-31 | Contract end date (optional) |

---

## 📄 Example Excel Structure

```
┌─────────────────┬──────────────────┬────────────────────────────────────┬────────────────┬──────────┐
│ Account Name    │ ServiceProvider  │ Contract Name                      │ Tenant Id: Name│ Status   │
├─────────────────┼──────────────────┼────────────────────────────────────┼────────────────┼──────────┤
│ Globex Corp     │ Marketing Cloud  │ Signature Success - MC Engagement  │ 524004459      │ Active   │
│ Initech Inc     │ Marketing Cloud  │ Signature Success Plan- MC Eng...  │ 523010029      │ Active   │
│ Umbrella Corp   │ Marketing Cloud  │ Signature Success - US Only - MC..│ 777000111      │ Cancelled│
└─────────────────┴──────────────────┴────────────────────────────────────┴────────────────┴──────────┘
```

---

## 🔧 Install Excel Support (One-Time)

The script needs pandas to read Excel files:

```bash
# Install pandas and openpyxl
pip3 install pandas openpyxl
```

---

## 🚀 Generate Data with Excel File

```bash
cd /Users/rinku.soni/mce-prom-dashboard

# The script will automatically find contracts.xlsx
python3 generateMCEData.py
```

Output:
```
Reading Excel file: /Users/rinku.soni/prom-signature-extension/data/contracts.xlsx
Loaded 450 contracts from contracts.xlsx
✓ Generated mceRealData.js
```

---

## 📥 Where to Get Contracts File

### Option 1: Export from Org62 (Recommended)

1. Log into **Org62**: https://org62.my.salesforce.com

2. Go to **Service Contracts** report or use SOQL:
   ```sql
   SELECT Account.Name, ServiceProvider__c, Name,
          Tenant_Id__r.Name, Service_Contract_Status__c, EndDate
   FROM ServiceContract
   WHERE Name LIKE '%MC Engagement%'
     AND ServiceProvider__c = 'Marketing Cloud'
   ```

3. Export to Excel

4. Save as: `contracts.xlsx`

5. Put in: `/Users/rinku.soni/prom-signature-extension/data/`

### Option 2: Use Chrome Extension (Live Data)

If you have the extension installed, it already pulls contracts live!
- No Excel file needed for extension mode
- Excel file only needed for static web version

---

## 🔄 Script Auto-Detection

The script automatically looks for contracts in this order:

1. `/Users/rinku.soni/prom-signature-extension/data/contracts.xlsx` ✨
2. `/Users/rinku.soni/prom-signature-extension/data/contracts.csv`
3. `/Users/rinku.soni/prom-signature-extension/sample/contracts.csv` (fallback)

**Just put your file there and run the script!**

---

## ⚠️ Important Notes

### Column Names

The script looks for these column patterns (case-insensitive):
- "Account Name" or "AccountName" or "Account.Name"
- "ServiceProvider" or "Service Provider" or "ServiceProvider__c"
- "Contract Name" or "Name"
- "Tenant Id: Name" or "Tenant_Id__r.Name" or "TenantId"

**Your Excel export from Salesforce should have these automatically!**

### Tenant ID Format

- ✅ Valid: `524004459` (numeric)
- ✅ Valid: `E524004459` (with E prefix - auto-stripped)
- ❌ Invalid: `DELETED_524004459` (rejected)
- ❌ Invalid: `00D37000000K0CP` (Salesforce org ID - rejected)

### Status Values

- **Active** - Contract is currently active
- **Cancelled** - Contract was cancelled
- **Expired** - Contract expired

---

## 🧪 Test Your Excel File

```bash
cd /Users/rinku.soni/mce-prom-dashboard

# Check if pandas is installed
python3 -c "import pandas; print('✓ pandas installed')"

# Check if your file exists
ls -lh /Users/rinku.soni/prom-signature-extension/data/contracts.xlsx

# Generate data
python3 generateMCEData.py
```

---

## 📊 CSV Format (Alternative)

If you prefer CSV, export as CSV instead:

```
Account Name,ServiceProvider,Contract Name,Tenant Id: Name,Status
Globex Corporation,Marketing Cloud,Signature Success - MC Engagement,524004459,Active
Initech Inc,Marketing Cloud,Signature Success Plan- MC Engagement,523010029,Active
```

Save as: `contracts.csv`

**Both formats work!** The script auto-detects which one you have.

---

## 🔄 Monthly Updates

When you get new contracts data:

```bash
# 1. Export fresh contracts.xlsx from Org62
# 2. Replace old file
cp ~/Downloads/contracts.xlsx /Users/rinku.soni/prom-signature-extension/data/

# 3. Regenerate
python3 generateMCEData.py

# 4. Commit and deploy
git add src/data/mceRealData.js
git commit -m "Update contracts - $(date +%B\ %Y)"
git push
npm run deploy
```

---

## ✅ Quick Checklist

- [ ] Exported contracts from Org62
- [ ] Saved as `contracts.xlsx`
- [ ] Put in `/Users/rinku.soni/prom-signature-extension/data/`
- [ ] Installed pandas: `pip3 install pandas openpyxl`
- [ ] Run: `python3 generateMCEData.py`
- [ ] Check output: `src/data/mceRealData.js` updated

---

**Place your contracts.xlsx file and run the script - it will auto-detect and process it!** 📊
