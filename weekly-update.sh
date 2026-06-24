#!/bin/bash
# =============================================================================
# MCE ProM Dashboard — Weekly Update Script
# =============================================================================
# Run this once per week after downloading your NA/EU CSVs from Centro.
#
# What this script does:
#   1. Finds the latest NA/EU CSVs from ~/Downloads and moves them to data folder
#   2. Finds the latest Contracts Excel from ~/Downloads (if present)
#   3. Regenerates dashboard data
#   4. Saves a dated snapshot for the trend chart history
#   5. Commits and pushes to both GitHub and git.soma
#   6. GitHub Actions auto-deploys both Pages
#
# Usage:
#   ./weekly-update.sh
#
# Before running:
#   - Download NA_<date>.csv from Centro via RoyalTSX → ~/Downloads
#   - Download EU_<date>.csv from Centro via RoyalTSX → ~/Downloads
#   - (Optional) Export Contracts report from Org62 → ~/Downloads as Contracts_<date>.xlsx
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="/Users/rinku.soni/prom-signature-extension/data"
DOWNLOADS_DIR="$HOME/Downloads"
TODAY=$(date +%Y-%m-%d)

echo "=============================================="
echo "  MCE ProM Dashboard — Weekly Update"
echo "  Date: $TODAY"
echo "=============================================="
echo ""

# ------------------------------------------------------------------------------
# STEP 1: Find and move latest UTDP CSVs from Downloads
# ------------------------------------------------------------------------------
echo "📂 Step 1: Looking for UTDP CSV files in ~/Downloads..."

# Find latest NA CSV (matches NA_*.csv or na_*.csv)
NA_FILE=$(ls -t "$DOWNLOADS_DIR"/NA_*.csv "$DOWNLOADS_DIR"/na_*.csv 2>/dev/null | head -1)
EU_FILE=$(ls -t "$DOWNLOADS_DIR"/EU_*.csv "$DOWNLOADS_DIR"/eu_*.csv 2>/dev/null | head -1)

if [ -z "$NA_FILE" ] || [ -z "$EU_FILE" ]; then
    echo ""
    echo "⚠️  UTDP CSV files not found in ~/Downloads"
    echo ""
    echo "   Please download from Centro via RoyalTSX:"
    echo "   - NA_<date>.csv  (e.g. NA_24June2026.csv)"
    echo "   - EU_<date>.csv  (e.g. EU_24June2026.csv)"
    echo "   Then re-run this script."
    echo ""
    read -p "   Press Enter to continue WITHOUT new UTDP data, or Ctrl+C to cancel: "
else
    NA_FILENAME=$(basename "$NA_FILE")
    EU_FILENAME=$(basename "$EU_FILE")

    echo "   ✅ Found NA: $NA_FILENAME"
    echo "   ✅ Found EU: $EU_FILENAME"

    # Move to data folder (keep original filename)
    cp "$NA_FILE" "$DATA_DIR/$NA_FILENAME"
    cp "$EU_FILE" "$DATA_DIR/$EU_FILENAME"

    echo "   📁 Copied to: $DATA_DIR/"
fi

# ------------------------------------------------------------------------------
# STEP 2: Fetch latest Contracts from Org62 via Chrome session cookie
# ------------------------------------------------------------------------------
echo ""
echo "📋 Step 2: Fetching contracts from Org62 (using Chrome session)..."

cd "$SCRIPT_DIR"
python3 fetchOrg62.py

if [ $? -ne 0 ]; then
    echo ""
    echo "   ⚠️  Org62 auto-fetch failed."
    echo "   Falling back: checking ~/Downloads for manually exported Contracts file..."

    CONTRACTS_DL=$(ls -t "$DOWNLOADS_DIR"/Contracts_*.xlsx "$DOWNLOADS_DIR"/contracts_*.xlsx 2>/dev/null | head -1)
    if [ -n "$CONTRACTS_DL" ]; then
        CONTRACTS_FILENAME=$(basename "$CONTRACTS_DL")
        cp "$CONTRACTS_DL" "$DATA_DIR/$CONTRACTS_FILENAME"
        echo "   ✅ Found and copied from Downloads: $CONTRACTS_FILENAME"
    else
        echo "   ℹ️  No new Contracts file found — using existing file in data folder"
    fi
fi

# ------------------------------------------------------------------------------
# STEP 3: Regenerate dashboard data
# ------------------------------------------------------------------------------
echo ""
echo "⚙️  Step 3: Regenerating dashboard data..."

cd "$SCRIPT_DIR"
python3 generateMCEData.py

if [ $? -ne 0 ]; then
    echo "❌ Data generation failed! Check the error above."
    exit 1
fi

# ------------------------------------------------------------------------------
# STEP 4: Save dated snapshot for trend history
# ------------------------------------------------------------------------------
echo ""
echo "📸 Step 4: Saving trend history snapshot for $TODAY..."

python3 - <<PYEOF
import json
import os
import re

# Read the generated JS file to extract current stats
js_file = "$SCRIPT_DIR/src/data/mceRealData.js"
history_dir = "$DATA_DIR/history"
today = "$TODAY"

os.makedirs(history_dir, exist_ok=True)

# Parse stats from the JS file using regex
with open(js_file, 'r') as f:
    content = f.read()

def extract(key):
    match = re.search(rf'"{key}":\s*(\d+)', content)
    return int(match.group(1)) if match else 0

snapshot = {
    "date": today,
    "label": __import__('datetime').datetime.strptime(today, '%Y-%m-%d').strftime('%b %-d, %Y'),
    "signatureAccounts": extract("totalSignatureAccounts"),
    "signatureWithProm": extract("signatureWithProm"),
    "signatureNotLeveraged": extract("signatureNotLeveraged"),
    "promEnabledTenants": extract("promEnabledTenants"),
    "nonSignatureWithProm": extract("nonSignatureWithProm"),
    "totalAlerts": extract("totalAlerts")
}

snapshot_file = os.path.join(history_dir, f"{today}.json")
with open(snapshot_file, 'w') as f:
    json.dump(snapshot, f, indent=2)

print(f"   ✅ Snapshot saved: {snapshot_file}")
print(f"   📊 Signature Accounts: {snapshot['signatureAccounts']}")
print(f"   📊 Leveraging ProM:    {snapshot['signatureWithProm']}")
print(f"   📊 Not Leveraged:      {snapshot['signatureNotLeveraged']}")
print(f"   📊 ProM Tenants:       {snapshot['promEnabledTenants']}")
print(f"   📊 Non-Sig w/ ProM:    {snapshot['nonSignatureWithProm']}")
print(f"   📊 Total Alerts:       {snapshot['totalAlerts']}")
PYEOF

if [ $? -ne 0 ]; then
    echo "❌ Snapshot saving failed!"
    exit 1
fi

# ------------------------------------------------------------------------------
# STEP 5: Rebuild trend data from all history snapshots
# ------------------------------------------------------------------------------
echo ""
echo "📈 Step 5: Rebuilding trend chart from all history snapshots..."

python3 - <<PYEOF
import json
import os
import re

history_dir = "$DATA_DIR/history"
js_file = "$SCRIPT_DIR/src/data/mceRealData.js"

# Load all snapshots sorted by date
snapshots = []
for fname in sorted(os.listdir(history_dir)):
    if fname.endswith('.json'):
        with open(os.path.join(history_dir, fname)) as f:
            snapshots.append(json.load(f))

print(f"   Found {len(snapshots)} historical snapshots")

# Build JS array
growth_js = json.dumps([{
    "month": s["label"],
    "signatureAccounts": s["signatureAccounts"],
    "accountsLeveragingProm": s["signatureWithProm"]
} for s in snapshots], indent=2)

# Replace the mceMonthlyGrowth array in the JS file
with open(js_file, 'r') as f:
    content = f.read()

new_export = f"export const mceMonthlyGrowth = {growth_js};"
content = re.sub(
    r'export const mceMonthlyGrowth = \[.*?\];',
    new_export,
    content,
    flags=re.DOTALL
)

with open(js_file, 'w') as f:
    f.write(content)

print(f"   ✅ Trend chart updated with {len(snapshots)} data points")
for s in snapshots:
    print(f"      {s['label']}: {s['signatureWithProm']} leveraging ProM")
PYEOF

# ------------------------------------------------------------------------------
# STEP 6: Commit and push to both repos
# ------------------------------------------------------------------------------
echo ""
echo "🚀 Step 6: Committing and pushing to both repos..."

cd "$SCRIPT_DIR"

# Check if there are changes to commit
if git diff --quiet && git diff --staged --quiet; then
    echo "   ℹ️  No changes to commit — dashboard is already up to date"
else
    git add src/data/mceRealData.js
    git commit -m "Weekly update: MCE ProM data for $TODAY

- Updated UTDP monitoring data
- Refreshed Org62 contract status
- Added trend snapshot for $TODAY

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

    echo "   Pushing to GitHub..."
    git push origin main

    echo "   Pushing to git.soma..."
    git push soma main

    echo "   ✅ Pushed to both repos — GitHub Actions will auto-deploy Pages"
fi

echo ""
echo "=============================================="
echo "  ✅ Weekly Update Complete!"
echo "=============================================="
echo ""
echo "  GitHub Pages will update in ~2 minutes:"
echo "  🌐 https://rinkusonisalesforce.github.io/mce-prom-dashboard/"
echo ""
echo "  git.soma Pages will update in ~2 minutes:"
echo "  🌐 https://git.soma.salesforce.com/pages/rinku-soni/mce-prom-dashboard/"
echo ""
