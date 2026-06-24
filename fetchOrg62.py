#!/usr/bin/env python3
"""
fetchOrg62.py — Extract Org62 service contracts using Chrome session cookie.

Works exactly like the Chrome extension:
  1. Reads the 'sid' cookie from Chrome's local cookie database (org62.my.salesforce.com)
  2. Decrypts it using macOS Keychain (same as Chrome)
  3. Uses it to query Org62 via SOQL REST API
  4. Saves contracts to data folder as Contracts_<date>.xlsx

Requirements:
  pip3 install cryptography requests pandas openpyxl

Usage:
  python3 fetchOrg62.py
  python3 fetchOrg62.py --report-id 00Oed000009bXHZEA2  (export report instead)
"""

import os
import sys
import shutil
import sqlite3
import tempfile
import json
import subprocess
import struct
import hmac
import hashlib
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

# -----------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------
ORG62_HOST     = 'org62.my.salesforce.com'
ORG62_URL      = f'https://{ORG62_HOST}'
SF_API_VERSION = '59.0'
DATA_DIR       = Path('/Users/rinku.soni/prom-signature-extension/data')
REPORT_ID      = '00Oed000009bXHZEA2'  # from your report URL

CHROME_PROFILE = os.path.expanduser(
    '~/Library/Application Support/Google/Chrome/Default'
)

SIGNATURE_PATTERNS = [
    'Signature Success - MC Engagement',
    'Signature Success Plan- MC Engagement',
    'Signature Success - US Only - MC Engagement',
]

# -----------------------------------------------------------------------
# Step 1: Extract + decrypt Chrome cookie
# -----------------------------------------------------------------------

def get_chrome_encryption_key():
    """Get Chrome's AES key from macOS Keychain."""
    # Try multiple service name variations Chrome uses
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
        # Check if permission was denied
        result = subprocess.run(
            ['security', 'find-generic-password', '-w', '-s', 'Chrome Safe Storage'],
            capture_output=True, text=True
        )
        if 'denied' in result.stderr.lower() or 'User denied' in result.stderr:
            raise RuntimeError(
                "macOS blocked Keychain access.\n\n"
                "Fix: Run this script directly from Terminal.app (not from an IDE):\n"
                "  1. Open Terminal.app\n"
                "  2. cd /Users/rinku.soni/mce-prom-dashboard\n"
                "  3. python3 fetchOrg62.py\n"
                "  4. Click 'Always Allow' on the Keychain popup"
            )
        raise RuntimeError(
            "Could not read Chrome Safe Storage from Keychain.\n"
            "Make sure Google Chrome is installed and you've opened it at least once."
        )
    password = result.stdout.strip().encode('utf-8')
    # Chrome derives key using PBKDF2
    key = hashlib.pbkdf2_hmac(
        'sha1', password, b'saltysalt', 1003, dklen=16
    )
    return key


def decrypt_cookie_value(encrypted_value, key):
    """Decrypt Chrome cookie value (AES-128-CBC)."""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend

    # Chrome v10+ prefix
    if encrypted_value[:3] != b'v10':
        # Old unencrypted format
        return encrypted_value.decode('utf-8', errors='ignore')

    iv = b' ' * 16  # Chrome uses spaces as IV
    payload = encrypted_value[3:]

    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(payload) + decryptor.finalize()

    # Remove PKCS7 padding
    pad_len = decrypted[-1]
    if pad_len < 1 or pad_len > 16:
        pad_len = 0
    result = decrypted[:-pad_len] if pad_len else decrypted
    # Strip to ASCII-safe characters only (session IDs are always ASCII)
    return result.decode('utf-8', errors='ignore').strip()\
                 .encode('ascii', errors='ignore').decode('ascii')


def get_org62_session_id():
    """Read and decrypt the Org62 'sid' cookie from Chrome."""
    cookie_db = os.path.join(CHROME_PROFILE, 'Cookies')
    if not os.path.exists(cookie_db):
        raise FileNotFoundError(
            f"Chrome cookies not found at: {cookie_db}\n"
            "Make sure Google Chrome is installed."
        )

    # Copy DB (Chrome locks it while running)
    tmp = tempfile.mktemp(suffix='.db')
    shutil.copy2(cookie_db, tmp)

    session_id = None
    try:
        conn = sqlite3.connect(tmp)
        c = conn.cursor()
        c.execute(
            "SELECT encrypted_value FROM cookies "
            "WHERE host_key = ? AND name = 'sid'",
            (ORG62_HOST,)
        )
        row = c.fetchone()
        conn.close()

        if not row or not row[0]:
            raise RuntimeError(
                f"No 'sid' cookie found for {ORG62_HOST}.\n"
                f"Please make sure you are logged into {ORG62_URL} in Chrome."
            )

        key = get_chrome_encryption_key()
        session_id = decrypt_cookie_value(row[0], key)

    finally:
        os.unlink(tmp)

    if not session_id or len(session_id) < 10:
        raise RuntimeError(
            "Could not decrypt Org62 session cookie.\n"
            "Try logging out and back into Org62 in Chrome, then re-run."
        )

    print(f"   ✅ Session cookie found and decrypted (len={len(session_id)})")
    return session_id


# -----------------------------------------------------------------------
# Step 2: Query Org62 via REST API using session ID
# -----------------------------------------------------------------------

def make_sf_request(session_id, endpoint, params=None):
    """Make authenticated request to Org62 REST API."""
    url = f"{ORG62_URL}/services/data/v{SF_API_VERSION}/{endpoint}"
    headers = {
        'Authorization': f'Bearer {session_id}',
        'Content-Type': 'application/json',
    }
    resp = requests.get(url, headers=headers, params=params, timeout=30)

    if resp.status_code == 401:
        raise RuntimeError(
            "Org62 session expired (401 Unauthorized).\n"
            "Please log back into org62.my.salesforce.com in Chrome and re-run."
        )
    if resp.status_code != 200:
        raise RuntimeError(
            f"Org62 API error {resp.status_code}: {resp.text[:200]}"
        )
    return resp.json()


def fetch_contracts_via_soql(session_id):
    """Fetch all signature service contracts via SOQL."""
    print("   Querying Org62 SOQL for signature contracts...")

    # Build SOQL — fetch all contracts matching signature patterns
    like_clauses = " OR ".join(
        f"Name LIKE '%{p}%'" for p in SIGNATURE_PATTERNS
    )
    soql = (
        "SELECT Id, Account.Name, Name, "
        "Tenant_Id__r.Name, Service_Contract_Status__c, EndDate "
        f"FROM ServiceContract WHERE ({like_clauses}) "
        "ORDER BY Account.Name ASC"
    )

    records = []
    result = make_sf_request(
        session_id, 'query',
        params={'q': soql}
    )
    records.extend(result.get('records', []))

    # Paginate through all results
    while result.get('nextRecordsUrl'):
        next_url = result['nextRecordsUrl'].replace(
            f'/services/data/v{SF_API_VERSION}/', ''
        )
        result = make_sf_request(session_id, next_url)
        records.extend(result.get('records', []))
        print(f"   Fetched {len(records)} contracts so far...")

    print(f"   ✅ Total contracts fetched: {len(records)}")
    return records


def fetch_report(session_id, report_id):
    """Export Org62 report by ID."""
    print(f"   Fetching Org62 report {report_id}...")
    result = make_sf_request(
        session_id,
        f'analytics/reports/{report_id}',
        params={'includeDetails': 'true'}
    )
    return result


# -----------------------------------------------------------------------
# Step 3: Save contracts to Excel
# -----------------------------------------------------------------------

def save_contracts_to_excel(records, output_path):
    """Convert SOQL records to Excel file."""
    rows = []
    for rec in records:
        account_name = ''
        if rec.get('Account') and rec['Account'].get('Name'):
            account_name = rec['Account']['Name']

        tenant_id = ''
        if rec.get('Tenant_Id__r') and rec['Tenant_Id__r'].get('Name'):
            tenant_id = rec['Tenant_Id__r']['Name']

        rows.append({
            'Account Name: Account Name': account_name,
            'Contract Name': rec.get('Name', ''),
            'Tenant Id: Name': tenant_id,
            'Service Contract Status': rec.get('Service_Contract_Status__c', ''),
            'EndDate': rec.get('EndDate', ''),
        })

    df = pd.DataFrame(rows)
    df.to_excel(output_path, index=False)
    print(f"   ✅ Saved {len(rows)} contracts to: {output_path}")
    return len(rows)


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def main():
    print("=" * 60)
    print("  Org62 Contract Fetcher")
    print("  Using Chrome session cookie (no password needed)")
    print("=" * 60)
    print()

    # Step 1: Get session
    print("🔑 Step 1: Reading Chrome session cookie for Org62...")
    try:
        session_id = get_org62_session_id()
    except Exception as e:
        print(f"\n❌ {e}")
        sys.exit(1)
    print()

    # Step 2: Fetch contracts
    print("📋 Step 2: Fetching contracts from Org62...")
    try:
        records = fetch_contracts_via_soql(session_id)
    except Exception as e:
        print(f"\n❌ {e}")
        sys.exit(1)
    print()

    # Step 3: Save to Excel
    print("💾 Step 3: Saving to Excel...")
    today = datetime.now().strftime('%d%B%Y')  # e.g. 24June2026
    output_file = DATA_DIR / f'Contracts_{today}.xlsx'
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        count = save_contracts_to_excel(records, output_file)
    except Exception as e:
        print(f"\n❌ Failed to save Excel: {e}")
        sys.exit(1)

    print()
    print("=" * 60)
    print(f"  ✅ Done! {count} contracts saved.")
    print(f"  📄 File: {output_file}")
    print("=" * 60)
    return str(output_file)


if __name__ == '__main__':
    main()
