# Running the Weekly Update on Your Machine

Use this guide if Rinku is away and the cron job on their Mac doesn't run.

---

## Prerequisites (one-time, ~10 minutes)

### 1. Clone the repo

```bash
git clone https://github.com/rinkusonisalesforce/mce-prom-dashboard.git
cd mce-prom-dashboard
```

### 2. Install Python dependencies

```bash
pip3 install pandas openpyxl requests cryptography
```

### 3. Create your local config

```bash
cp local.env.template local.env
```

Open `local.env` and set:

```
DATA_DIR=/Users/<your-username>/prom-signature-extension/data
GDRIVE_EMAIL=<your-email>@salesforce.com
GDRIVE_FOLDER=MCE-ProM-Data
```

Create the data folder if it doesn't exist:

```bash
mkdir -p ~/prom-signature-extension/data
mkdir -p ~/prom-signature-extension/data/history
```

### 4. Install Node.js dependencies (for the dashboard build)

```bash
npm install
```

### 5. Set up git remotes (push to both GitHub and git.soma)

```bash
git remote -v   # should show "origin" pointing to GitHub
# Add git.soma if not already there:
git remote add soma git@git.soma.salesforce.com:rinku-soni/mce-prom-dashboard.git
```

### 6. Get push access

Ask Rinku to add you as a collaborator on:
- GitHub: `rinkusonisalesforce/mce-prom-dashboard`
- git.soma: `rinku-soni/mce-prom-dashboard`

---

## Every week (when Rinku is away)

### Step 1 — Drop the CSV files

Download NA + EU UTDP CSVs from Centro via RoyalTSX and upload to the shared Google Drive folder:

📁 [MCE-ProM-Data on Google Drive](https://drive.google.com/drive/folders/1WczHUM4SyWOwt0XXwiEDqWUdkZxuTFSH)

File naming:
```
NA_<day><Month><year>.csv    e.g.  NA_4July2026.csv
EU_<day><Month><year>.csv    e.g.  EU_4July2026.csv
```

### Step 2 — Make sure you're logged into Org62 in Chrome

Open Chrome and visit: `https://org62.my.salesforce.com`  
Log in with your Salesforce SSO if not already logged in.

### Step 3 — Run the script

```bash
cd mce-prom-dashboard
./weekly-update.sh
```

The first time you run `fetchOrg62.py` (called automatically by the script),
macOS will show a **Keychain popup** — click **"Always Allow"**.

### Step 4 — Done

GitHub Actions auto-deploys the dashboard within ~2 minutes.
Dashboard: https://rinkusonisalesforce.github.io/mce-prom-dashboard/

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `No local.env found` | Run `cp local.env.template local.env` and edit it |
| `Org62 session expired (401)` | Log into org62.my.salesforce.com in Chrome and re-run |
| `No 'sid' cookie found` | Same as above — log into Org62 in Chrome first |
| `Keychain permission denied` | Run the script from Terminal.app (not an IDE) |
| `NA/EU files not found` | Check Google Drive folder has the correctly named files |
| `git push` fails | Check you have collaborator access (ask Rinku) |

---

## Questions?

Contact: rinku.soni@salesforce.com
