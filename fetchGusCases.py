#!/usr/bin/env python3
"""
fetchGusCases.py — Read GUS (or orgcs) Cases using the Chrome session cookie.

Mirrors fetchOrg62.py exactly, but targets the GUS org so we can pull the
"delete" Cases for MCE ProM Monitoring Jobs and use them to exclude stale
(offboarded) accounts from the Non-SIG ProM Leveraged count.

Modes:
  python3 fetchGusCases.py --case 500EE00001wbZheYAE   # dump one case's fields (discovery)
  python3 fetchGusCases.py --describe                  # list Case fields (schema)
  python3 fetchGusCases.py                             # run the delete-case query (default)

Requirements: pip3 install cryptography requests pandas openpyxl
"""

import os
import sys
import shutil
import sqlite3
import tempfile
import json
import subprocess
import hashlib
import argparse
import requests
from pathlib import Path
from datetime import datetime

# -----------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------
GUS_HOST       = os.environ.get('GUS_HOST', 'gus.my.salesforce.com')
GUS_URL        = f'https://{GUS_HOST}'
SF_API_VERSION = '59.0'

CHROME_PROFILE = os.path.expanduser(
    '~/Library/Application Support/Google/Chrome/Default'
)


def _load_data_dir():
    local_env = Path(__file__).parent / 'local.env'
    if local_env.exists():
        for line in local_env.read_text().splitlines():
            line = line.strip()
            if line.startswith('DATA_DIR='):
                return Path(os.path.expanduser(line.split('=', 1)[1].strip()))
    return Path(os.path.expanduser('~/prom-signature-extension/data'))


DATA_DIR = _load_data_dir()

# -----------------------------------------------------------------------
# Step 1: Extract + decrypt Chrome cookie  (identical to fetchOrg62.py)
# -----------------------------------------------------------------------

def get_chrome_encryption_key():
    password = None
    for args in [
        ['security', 'find-generic-password', '-w', '-s', 'Chrome Safe Storage'],
        ['security', 'find-generic-password', '-w', '-s', 'Chrome Safe Storage', '-a', 'Chrome'],
        ['security', 'find-generic-password', '-w', '-s', 'Chromium Safe Storage'],
    ]:
        result = subprocess.run(args, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            password = result.stdout.strip()
            break

    if not password:
        result = subprocess.run(
            ['security', 'find-generic-password', '-w', '-s', 'Chrome Safe Storage'],
            capture_output=True, text=True
        )
        if 'denied' in result.stderr.lower():
            raise RuntimeError(
                "macOS blocked Keychain access.\n\n"
                "Fix: Run this script directly from Terminal.app (not from an IDE):\n"
                "  1. Open Terminal.app\n"
                "  2. cd ~/mce-prom-dashboard\n"
                "  3. python3 fetchGusCases.py\n"
                "  4. Click 'Always Allow' on the Keychain popup"
            )
        raise RuntimeError(
            "Could not read Chrome Safe Storage from Keychain.\n"
            "Make sure Google Chrome is installed and you've opened it at least once."
        )
    password = password.encode('utf-8')
    return hashlib.pbkdf2_hmac('sha1', password, b'saltysalt', 1003, dklen=16)


def decrypt_cookie_value(encrypted_value, key):
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend

    if encrypted_value[:3] != b'v10':
        return encrypted_value.decode('utf-8', errors='ignore')

    iv = b' ' * 16
    payload = encrypted_value[3:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(payload) + decryptor.finalize()

    pad_len = decrypted[-1]
    if pad_len < 1 or pad_len > 16:
        pad_len = 0
    raw = decrypted[:-pad_len] if pad_len else decrypted

    import re as _re
    match = _re.search(rb'00D[A-Za-z0-9]{12,}![A-Za-z0-9._\-/+=]+', raw)
    if match:
        return match.group(0).decode('ascii', errors='ignore')

    if len(raw) > 32:
        raw = raw[32:]
    return raw.decode('utf-8', errors='ignore').strip() \
              .encode('ascii', errors='ignore').decode('ascii')


def get_session_id(host):
    """Read and decrypt the 'sid' cookie for a specific Salesforce host."""
    cookie_db = os.path.join(CHROME_PROFILE, 'Cookies')
    if not os.path.exists(cookie_db):
        raise FileNotFoundError(f"Chrome cookies not found at: {cookie_db}")

    tmp = tempfile.mktemp(suffix='.db')
    shutil.copy2(cookie_db, tmp)
    try:
        conn = sqlite3.connect(tmp)
        c = conn.cursor()
        c.execute(
            "SELECT encrypted_value FROM cookies WHERE host_key = ? AND name = 'sid'",
            (host,)
        )
        row = c.fetchone()
        conn.close()
        if not row or not row[0]:
            raise RuntimeError(
                f"No 'sid' cookie found for {host}.\n"
                f"Please make sure you are logged into https://{host} in Chrome.\n"
                f"(If GUS lives on a different host, set GUS_HOST env var.)"
            )
        key = get_chrome_encryption_key()
        session_id = decrypt_cookie_value(row[0], key)
    finally:
        os.unlink(tmp)

    if not session_id or len(session_id) < 10:
        raise RuntimeError("Could not decrypt GUS session cookie. Re-login and retry.")
    print(f"   ✅ Session cookie found and decrypted (len={len(session_id)})")
    return session_id


# -----------------------------------------------------------------------
# Step 2: REST helpers
# -----------------------------------------------------------------------

def sf_get(session_id, endpoint, params=None):
    url = f"{GUS_URL}/services/data/v{SF_API_VERSION}/{endpoint}"
    headers = {'Authorization': f'Bearer {session_id}', 'Content-Type': 'application/json'}
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    if resp.status_code == 401:
        raise RuntimeError(
            f"GUS session expired (401 Unauthorized).\n"
            f"Please log back into https://{GUS_HOST} in Chrome and re-run."
        )
    if resp.status_code != 200:
        raise RuntimeError(f"GUS API error {resp.status_code}: {resp.text[:300]}")
    return resp.json()


# -----------------------------------------------------------------------
# Discovery modes
# -----------------------------------------------------------------------

def dump_case(session_id, case_id):
    """Fetch one Case and print all populated fields (schema discovery)."""
    print(f"   Fetching Case {case_id} ...")
    rec = sf_get(session_id, f'sobjects/Case/{case_id}')
    print("\n=== Populated fields on Case %s ===" % case_id)
    for k in sorted(rec.keys()):
        v = rec[k]
        if v in (None, '', [], {}):
            continue
        s = str(v)
        if len(s) > 400:
            s = s[:400] + '…(truncated)'
        print(f"  {k}: {s}")
    print("\n(Full raw JSON saved to /tmp/gus_case_dump.json)")
    Path('/tmp/gus_case_dump.json').write_text(json.dumps(rec, indent=2))


def describe_case(session_id):
    """List Case object fields (API name + label + type)."""
    print("   Describing Case object ...")
    meta = sf_get(session_id, 'sobjects/Case/describe')
    print("\n=== Case fields (apiName | label | type) ===")
    for f in meta.get('fields', []):
        print(f"  {f['name']} | {f['label']} | {f['type']}")


# -----------------------------------------------------------------------
# Default: fetch all "MCE ProM Monitoring Jobs" cases and save to disk
# -----------------------------------------------------------------------

# Subject must contain this to be an MCE ProM Monitoring Jobs case.
SUBJECT_MATCH = 'MCE ProM Monitoring Jobs'


def fetch_prom_cases(session_id):
    """Fetch every Case whose Subject mentions MCE ProM Monitoring Jobs.

    We pull BOTH create and delete cases (not just deletes) so the
    downstream logic can decide, per job name, whether the *most recent*
    case is a deletion.
    """
    print(f"   Querying GUS for Cases with '{SUBJECT_MATCH}' in subject...")
    soql = (
        "SELECT Id, CaseNumber, Subject, Description, Status, "
        "CreatedDate, ClosedDate "
        "FROM Case "
        f"WHERE Subject LIKE '%{SUBJECT_MATCH}%' "
        "ORDER BY CreatedDate ASC"
    )
    records = []
    result = sf_get(session_id, 'query', params={'q': soql})
    records.extend(result.get('records', []))
    while result.get('nextRecordsUrl'):
        next_url = result['nextRecordsUrl'].replace(
            f'/services/data/v{SF_API_VERSION}/', ''
        )
        result = sf_get(session_id, next_url)
        records.extend(result.get('records', []))
        print(f"   Fetched {len(records)} cases so far...")
    print(f"   ✅ Total MCE ProM Monitoring Jobs cases: {len(records)}")
    return records


def save_cases(records, output_path):
    rows = []
    for r in records:
        rows.append({
            'Id': r.get('Id', ''),
            'CaseNumber': r.get('CaseNumber', ''),
            'Subject': r.get('Subject', '') or '',
            'Description': r.get('Description', '') or '',
            'Status': r.get('Status', '') or '',
            'CreatedDate': r.get('CreatedDate', '') or '',
            'ClosedDate': r.get('ClosedDate', '') or '',
        })
    Path(output_path).write_text(json.dumps(rows, indent=2))
    n_delete = sum(1 for r in rows if 'delet' in r['Subject'].lower())
    print(f"   ✅ Saved {len(rows)} cases ({n_delete} look like deletions) to: {output_path}")
    return output_path


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--case', help='Dump a single Case by Id (discovery)')
    ap.add_argument('--describe', action='store_true', help='Describe Case object fields')
    args = ap.parse_args()

    print("=" * 60)
    print("  GUS Case Fetcher — Chrome session cookie")
    print(f"  Host: {GUS_HOST}")
    print("=" * 60)
    print()
    print("🔑 Reading Chrome session cookie for GUS...")
    try:
        session_id = get_session_id(GUS_HOST)
    except Exception as e:
        print(f"\n❌ {e}")
        sys.exit(1)
    print()

    if args.case:
        dump_case(session_id, args.case)
        return
    if args.describe:
        describe_case(session_id)
        return

    # Default: fetch all ProM cases and save for the data generator.
    print("📋 Fetching MCE ProM Monitoring Jobs cases from GUS...")
    try:
        records = fetch_prom_cases(session_id)
    except Exception as e:
        print(f"\n❌ {e}")
        sys.exit(1)
    print()
    today = datetime.now().strftime('%d%B%Y')  # e.g. 14August2026
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_file = DATA_DIR / f'GusProMCases_{today}.json'
    save_cases(records, output_file)
    print()
    print("=" * 60)
    print(f"  ✅ Done. Cases saved to {output_file}")
    print("=" * 60)


if __name__ == '__main__':
    main()
