#!/usr/bin/env python3
"""
resolve-mids.py — Resolve MID → EID mappings using the Slack support bot.

UTDP exports sometimes use MIDs (member IDs, M-prefix) instead of EIDs
(enterprise IDs, E-prefix).  Contracts are always stored by EID.  This tool:

  1. Scans all UTDP CSVs for M-prefix IDs
  2. Checks which ones are NOT yet in the cache (mid_to_eid_cache.json)
  3. For each unknown MID, prompts you to look it up in Slack and enter the EID
  4. Saves the result to the cache for all future runs

Slack lookup (takes ~5 seconds per MID):
  Open the Slack SupportBot channel and type:  .mcmember <number>
  e.g.:  .mcmember 546010497
  The bot returns:  EnterpriseID: <eid>

Usage:
  python3 resolve-mids.py          # interactive — prompts for unknowns
  python3 resolve-mids.py --check  # just report how many are unresolved
  python3 resolve-mids.py --show   # print the full cache
"""

import json
import re
import sys
from pathlib import Path

DATA_DIR   = Path('/Users/rinku.soni/prom-signature-extension/data')
CACHE_FILE = Path(__file__).parent / 'mid_to_eid_cache.json'

# -----------------------------------------------------------------------
# Cache helpers
# -----------------------------------------------------------------------

def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2, sort_keys=True)
    print(f"   💾 Cache saved → {CACHE_FILE.name}  ({len(cache)} entries)")


# -----------------------------------------------------------------------
# CSV scanning
# -----------------------------------------------------------------------

def find_all_mids():
    """Return dict: {mid_number: [(customer_name, monitors, region, source_file), ...]}"""
    mids = {}
    patterns = ['NA_*.csv', 'EU_*.csv', 'NAandEU_*.csv']

    for pattern in patterns:
        for csv_file in sorted(DATA_DIR.glob(pattern)):
            region = 'EU' if csv_file.name.startswith('EU_') else \
                     'NA' if csv_file.name.startswith('NA_') else 'Combined'
            with open(csv_file, encoding='utf-8') as f:
                import csv
                reader = csv.DictReader(f)
                for row in reader:
                    eid_raw = row.get('EID', '').strip()
                    if re.match(r'^M\d+$', eid_raw):
                        mid_num = eid_raw[1:]  # strip the M
                        customer = row.get('Customer_Name', '').strip()
                        monitors = int(row.get('Total_Monitors_Enabled', 0) or 0)
                        if mid_num not in mids:
                            mids[mid_num] = []
                        mids[mid_num].append((customer, monitors, region, csv_file.name))

    return mids


# -----------------------------------------------------------------------
# Interactive resolution
# -----------------------------------------------------------------------

def resolve_interactively(unknown_mids):
    """Prompt user to look up each unknown MID in Slack and enter the EID."""
    cache = load_cache()
    resolved = 0
    skipped = 0

    total = len(unknown_mids)
    print()
    print(f"   Found {total} MID(s) with no cached EID.")
    print()
    print("   For each one, look it up in the Slack SupportBot channel:")
    print("   → Type in SupportBot:  .mcmember <number>")
    print("   → Copy the 'EnterpriseID:' value from the bot reply")
    print()
    print("   Press ENTER (blank) to skip a MID for now.")
    print("   Type 'q' to quit and save what you've entered so far.")
    print()

    for i, (mid_num, occurrences) in enumerate(sorted(unknown_mids.items()), 1):
        # Summarise where this MID appears
        customers = list({occ[0] for occ in occurrences})
        total_monitors = sum(occ[1] for occ in occurrences)
        sources = list({occ[3] for occ in occurrences})

        print(f"   [{i}/{total}]  MID: M{mid_num}")
        print(f"           Customer(s):  {', '.join(customers)}")
        print(f"           Monitors:     {total_monitors}")
        print(f"           Seen in:      {', '.join(sources)}")
        print(f"           Slack lookup: .mcmember {mid_num}")

        while True:
            try:
                ans = input(f"           EnterpriseID → ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                ans = 'q'

            if ans.lower() == 'q':
                save_cache(cache)
                print(f"\n   ✅ Saved {resolved} new mapping(s). Run again to resolve the rest.")
                return cache

            if ans == '':
                skipped += 1
                print(f"           ⏩ Skipped")
                break

            # Accept with or without E prefix
            eid_clean = re.sub(r'^[Ee]', '', ans).strip()
            if not re.match(r'^\d+$', eid_clean):
                print(f"           ⚠️  That doesn't look like an EID (should be digits only). Try again.")
                continue

            cache[mid_num] = eid_clean
            resolved += 1
            print(f"           ✅ Mapped M{mid_num} → {eid_clean}")
            break

        print()

    save_cache(cache)
    print(f"   ✅ Done.  Resolved: {resolved}   Skipped: {skipped}")
    return cache


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def main():
    args = sys.argv[1:]

    cache = load_cache()

    if '--show' in args:
        print(f"\n📋 MID → EID Cache ({len(cache)} entries):\n")
        if not cache:
            print("   (empty)")
        else:
            for mid, eid in sorted(cache.items(), key=lambda x: int(x[0])):
                print(f"   M{mid}  →  {eid}")
        print()
        return

    # Scan all CSVs for M-prefixed IDs
    all_mids = find_all_mids()

    if not all_mids:
        print("✅ No M-prefix IDs found in any UTDP CSV files.")
        return

    unknown = {mid: occ for mid, occ in all_mids.items() if mid not in cache}

    print(f"\n📊 MID summary:")
    print(f"   Total unique MIDs across all CSVs:  {len(all_mids)}")
    print(f"   Already resolved (in cache):         {len(all_mids) - len(unknown)}")
    print(f"   Needs lookup:                        {len(unknown)}")

    if '--check' in args:
        if unknown:
            print(f"\n⚠️  {len(unknown)} MID(s) are unresolved.  Run without --check to fix them.\n")
            for mid in sorted(unknown.keys()):
                customers = list({occ[0] for occ in unknown[mid]})
                print(f"   M{mid}  ({', '.join(customers)})")
        else:
            print("\n✅ All MIDs resolved — good to go!\n")
        return

    if not unknown:
        print("\n✅ All MIDs are already in cache — nothing to do!\n")
        return

    resolve_interactively(unknown)


if __name__ == '__main__':
    main()
