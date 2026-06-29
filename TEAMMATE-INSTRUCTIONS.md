# MCE ProM Dashboard — How to Update UTDP Data

## Your job (weekly, ~2 minutes)

Drop the two CSV files from Centro into the shared Google Drive folder.

---

## Shared Google Drive Folder

```
MCE-ProM-Data/
```

👉 Rinku will share this folder with you directly in Google Drive.

---

## File Naming Convention

Files MUST follow this exact format:

```
NA_<day><Month><year>.csv
EU_<day><Month><year>.csv
```

**Examples:**
```
NA_29June2026.csv
EU_29June2026.csv

NA_6July2026.csv
EU_6July2026.csv
```

---

## Steps Each Week

1. **Connect to Centro** via RoyalTSX
2. **Download the NA CSV** → rename to `NA_<date>.csv` if needed
3. **Download the EU CSV** → rename to `EU_<date>.csv` if needed
4. **Drop both files** into the shared `MCE-ProM-Data` Google Drive folder
5. **Notify Rinku** (Slack message: "NA/EU files dropped for <date>")

That's it! Rinku runs the update script and the dashboard updates automatically.

---

## Important Notes

- Keep **both NA and EU** files for the same date — the script needs both
- Don't delete old files from the folder (they're used for trend history)
- File naming matters — use the format above exactly

---

## Questions?

Contact: rinku.soni@salesforce.com
