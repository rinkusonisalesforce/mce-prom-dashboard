#!/bin/bash
# =============================================================================
# MCE ProM Dashboard — Weekly Update Script
# =============================================================================
# Run this once per week after UTDP CSVs are dropped in the shared folder.
#
# UTDP CSV drop zone (Google Drive — share this folder with your teammate):
#   ~/Library/CloudStorage/GoogleDrive-rinku.soni@salesforce.com/My Drive/MCE-ProM-Data/
#
# What this script does:
#   1. Finds latest NA/EU CSVs from Google Drive shared folder (or ~/Downloads fallback)
#   2. Auto-fetches latest Org62 contracts via Chrome session cookie
#   3. Regenerates dashboard data
#   4. Saves a dated snapshot for the trend chart history
#   5. Commits and pushes to both GitHub and git.soma
#   6. GitHub Actions auto-deploys both Pages
#
# Usage:
#   ./weekly-update.sh
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="/Users/rinku.soni/prom-signature-extension/data"
DOWNLOADS_DIR="$HOME/Downloads"
GDRIVE_DIR="$HOME/Library/CloudStorage/GoogleDrive-rinku.soni@salesforce.com/My Drive/MCE-ProM-Data"
TODAY=$(date +%Y-%m-%d)

echo "=============================================="
echo "  MCE ProM Dashboard — Weekly Update"
echo "  Date: $TODAY"
echo "=============================================="
echo ""

# ------------------------------------------------------------------------------
# STEP 1: Find latest UTDP CSVs — check Google Drive first, then ~/Downloads
# ------------------------------------------------------------------------------
echo "📂 Step 1: Looking for UTDP CSV files..."
echo "   Primary:  Google Drive/MCE-ProM-Data/"
echo "   Fallback: ~/Downloads/"

find_csv() {
    local prefix=$1
    # Check Google Drive first
    local f=$(ls -t "$GDRIVE_DIR"/${prefix}_*.csv "$GDRIVE_DIR"/${prefix,,}_*.csv 2>/dev/null | head -1)
    if [ -n "$f" ]; then
        echo "$f"
        return
    fi
    # Fall back to Downloads
    ls -t "$DOWNLOADS_DIR"/${prefix}_*.csv "$DOWNLOADS_DIR"/${prefix,,}_*.csv 2>/dev/null | head -1
}

NA_FILE=$(find_csv "NA")
EU_FILE=$(find_csv "EU")

if [ -z "$NA_FILE" ] || [ -z "$EU_FILE" ]; then
    echo ""
    echo "⚠️  UTDP CSV files not found in Google Drive or ~/Downloads"
    echo ""
    echo "   Ask your teammate to drop files into the shared Google Drive folder:"
    echo "   📁 MCE-ProM-Data/"
    echo "   Files needed:"
    echo "   - NA_<date>.csv  (e.g. NA_29June2026.csv)"
    echo "   - EU_<date>.csv  (e.g. EU_29June2026.csv)"
    echo ""
    read -p "   Press Enter to continue WITHOUT new UTDP data, or Ctrl+C to cancel: "
else
    NA_FILENAME=$(basename "$NA_FILE")
    EU_FILENAME=$(basename "$EU_FILE")
    NA_SOURCE=$(echo "$NA_FILE" | grep -q "GoogleDrive" && echo "Google Drive" || echo "Downloads")
    EU_SOURCE=$(echo "$EU_FILE" | grep -q "GoogleDrive" && echo "Google Drive" || echo "Downloads")

    echo "   ✅ Found NA: $NA_FILENAME  (from $NA_SOURCE)"
    echo "   ✅ Found EU: $EU_FILENAME  (from $EU_SOURCE)"

    cp "$NA_FILE" "$DATA_DIR/$NA_FILENAME"
    cp "$EU_FILE" "$DATA_DIR/$EU_FILENAME"
    echo "   📁 Copied to data folder"
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
