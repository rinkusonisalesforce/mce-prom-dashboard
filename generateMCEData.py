#!/usr/bin/env python3
"""
Generate MCE Real Data from UTDP CSVs and Org62 Contracts
Updated to match new dashboard requirements
"""

import csv
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# -----------------------------------------------------------------------
# MID → EID cache (populated by resolve-mids.py)
# MIDs are member-level IDs (M-prefix) used in UTDP.
# Contracts store EIDs (enterprise-level). The cache maps
# the numeric part of a MID to its parent EID numeric part.
# -----------------------------------------------------------------------
def load_mid_cache():
    cache_file = Path(__file__).parent / 'mid_to_eid_cache.json'
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    return {}

MID_TO_EID = load_mid_cache()

# Try to import pandas for Excel support
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Note: Install pandas for Excel support: pip3 install pandas openpyxl")

# Configuration — reads DATA_DIR from local.env if present, else uses default
def _load_data_dir():
    import os
    local_env = Path(__file__).parent / 'local.env'
    if local_env.exists():
        for line in local_env.read_text().splitlines():
            line = line.strip()
            if line.startswith('DATA_DIR='):
                return Path(os.path.expanduser(line.split('=', 1)[1].strip()))
    return Path(os.path.expanduser('~/prom-signature-extension/data'))

DATA_DIR = _load_data_dir()
CSV_DIR = DATA_DIR
HISTORY_DIR = DATA_DIR / 'history'
OUTPUT_FILE = Path(__file__).parent / 'src' / 'data' / 'mceRealData.js'

SIGNATURE_PATTERNS = [
    'Signature Success - MC Engagement',
    'Signature Success Plan- MC Engagement',
    'Signature Success - US Only - MC Engagement',
]

# -----------------------------------------------------------------------
# Auto-discover latest contracts file (newest .xlsx or .csv in data dir)
# -----------------------------------------------------------------------
def find_latest_contracts():
    candidates = sorted(
        list(DATA_DIR.glob('Contracts_*.xlsx')) +
        list(DATA_DIR.glob('contracts*.xlsx')) +
        list(DATA_DIR.glob('Contracts_*.csv')) +
        list(DATA_DIR.glob('contracts*.csv')),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    if candidates:
        return candidates[0]
    fallback = Path.home() / 'prom-signature-extension' / 'sample' / 'contracts.csv'
    return fallback if fallback.exists() else None

CONTRACTS_FILE = find_latest_contracts()

# -----------------------------------------------------------------------
# Auto-discover UTDP CSV files: find all NA_*.csv / EU_*.csv / NAandEU_*.csv
# Build MONTHS list dynamically from what files actually exist
# -----------------------------------------------------------------------
def discover_utdp_months():
    """Scan data directory and build MONTHS list from available CSV files."""
    import re
    from datetime import datetime

    found = {}  # key: (date_str, month_str, year_str) → entry dict

    # Match combined files: NAandEU_6April2026.csv
    for f in DATA_DIR.glob('NAandEU_*.csv'):
        m = re.match(r'NAandEU_(\d+)([A-Za-z]+)(\d{4})\.csv', f.name)
        if m:
            d, mo, yr = m.group(1), m.group(2), m.group(3)
            key = f"{yr}-{mo}-{d}"
            dt = datetime.strptime(f"{d} {mo} {yr}", "%d %B %Y")
            found[key] = {
                'date': d, 'month': mo, 'year': yr,
                'label': dt.strftime('%b %-d, %Y'),
                'combined': True,
                'sort_key': dt
            }

    # Match separate NA/EU files: NA_7June2026.csv + EU_7June2026.csv
    na_files = {}
    eu_files = {}
    for f in DATA_DIR.glob('NA_*.csv'):
        m = re.match(r'NA_(\d+)([A-Za-z]+)(\d{4})\.csv', f.name)
        if m:
            d, mo, yr = m.group(1), m.group(2), m.group(3)
            na_files[f"{yr}-{mo}-{d}"] = (d, mo, yr)
    for f in DATA_DIR.glob('EU_*.csv'):
        m = re.match(r'EU_(\d+)([A-Za-z]+)(\d{4})\.csv', f.name)
        if m:
            d, mo, yr = m.group(1), m.group(2), m.group(3)
            eu_files[f"{yr}-{mo}-{d}"] = (d, mo, yr)

    # Only include dates where BOTH NA and EU exist
    for key in set(na_files) & set(eu_files):
        if key not in found:
            d, mo, yr = na_files[key]
            dt = datetime.strptime(f"{d} {mo} {yr}", "%d %B %Y")
            found[key] = {
                'date': d, 'month': mo, 'year': yr,
                'label': dt.strftime('%b %-d, %Y'),
                'combined': False,
                'sort_key': dt
            }

    # Sort by date, return only the most recent one (current snapshot)
    sorted_months = sorted(found.values(), key=lambda x: x['sort_key'])
    return sorted_months

MONTHS = discover_utdp_months()
if not MONTHS:
    print("⚠️  No UTDP CSV files found in data directory!")
    print(f"   Expected: NA_<date><month><year>.csv / EU_<date><month><year>.csv")
    print(f"   In: {DATA_DIR}")
    sys.exit(1)

# Use only the latest snapshot for current metrics
CURRENT_MONTH = MONTHS[-1]

def parse_csv(filepath):
    """Parse CSV file"""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def normalize_eid(eid):
    """Strip E/M prefix and get numeric part.

    For M-prefix IDs (MIDs / member tenants): look up the parent EID
    from the cache populated by resolve-mids.py.  If not in cache,
    returns '' so the row is treated as unresolved (not matched to
    any contract, shows in non-signature section with a note).
    """
    import re
    if not eid:
        return ''
    s = str(eid).strip()

    if s.upper().startswith('M'):
        mid_num = re.sub(r'[^0-9]', '', s)
        if mid_num in MID_TO_EID:
            # Resolved — use the parent EID
            return MID_TO_EID[mid_num].lstrip('0') or '0'
        else:
            # Unresolved MID — keep as-is with 'mid:' prefix so we can
            # identify it in match_data() and flag it separately
            return f'mid:{mid_num}'

    # E-prefix or bare number
    digits = re.sub(r'[^0-9]', '', s)
    return digits.lstrip('0') or '0'

def normalize_contract_tenant_id(tenant_id):
    """Validate and normalize contract tenant ID (must be purely numeric)"""
    if not tenant_id:
        return ''

    s = str(tenant_id).strip()

    # Reject DELETED_* and 00D* (Salesforce org IDs)
    if 'DELETED_' in s.upper() or s.startswith('00D'):
        return ''

    # Must be purely numeric
    if not s.isdigit():
        return ''

    return s.lstrip('0') or '0'

def is_signature_contract(contract_name):
    """Check if contract name matches Signature patterns"""
    if not contract_name:
        return False

    name = contract_name.strip()

    # Exact match
    if name in SIGNATURE_PATTERNS:
        return True

    # Regex match
    if 'signature' in name.lower() and 'mc engagement' in name.lower():
        return True

    return False

def load_monitoring_data(date, month, year, combined=False):
    """Load monitoring data for a specific date

    File naming: NAandEU_6April2026.csv (combined) or NA_7June2026.csv / EU_7June2026.csv (separate)
    """
    data = []

    if combined:
        # Load combined file: NAandEU_6April2026.csv
        combined_file = CSV_DIR / f'NAandEU_{date}{month}{year}.csv'
        if combined_file.exists():
            rows = parse_csv(combined_file)
            for row in rows:
                # No region specified in combined file
                data.append({**row, 'region': 'Combined'})
        else:
            print(f'   ⚠️  Combined file not found: {combined_file}')
    else:
        # Load separate NA and EU files: NA_7June2026.csv, EU_7June2026.csv
        na_file = CSV_DIR / f'NA_{date}{month}{year}.csv'
        eu_file = CSV_DIR / f'EU_{date}{month}{year}.csv'

        if na_file.exists():
            rows = parse_csv(na_file)
            for row in rows:
                data.append({**row, 'region': 'NA'})
        else:
            print(f'   ⚠️  NA file not found: {na_file}')

        if eu_file.exists():
            rows = parse_csv(eu_file)
            for row in rows:
                data.append({**row, 'region': 'EU'})
        else:
            print(f'   ⚠️  EU file not found: {eu_file}')

    # Process and filter
    processed = []
    for row in data:
        monitors = int(row.get('Total_Monitors_Enabled', 0) or 0)
        if monitors > 0:
            processed.append({
                'customerName': row.get('Customer_Name', ''),
                'tenantId': row.get('EID', ''),
                'normalizedEid': normalize_eid(row.get('EID', '')),
                'monitors': monitors,
                'alerts': monitors,
                'region': row.get('region', '')
            })

    return processed

def load_contracts():
    """Load contracts from CSV or Excel"""
    if not CONTRACTS_FILE.exists():
        print(f'⚠️  Contracts file not found: {CONTRACTS_FILE}')
        return []

    # Determine if Excel or CSV
    file_ext = CONTRACTS_FILE.suffix.lower()

    contracts = []

    if file_ext in ['.xlsx', '.xls'] and HAS_PANDAS:
        # Read Excel - skip Salesforce report header rows (metadata at top)
        print(f'Reading Excel file: {CONTRACTS_FILE}')

        # Try to find the header row automatically
        temp_df = pd.read_excel(CONTRACTS_FILE, header=None, nrows=20)
        header_row = None

        for idx, row in temp_df.iterrows():
            # Look for row containing "Account Name" and "Contract Name"
            row_str = ' '.join(str(x).lower() for x in row.values if pd.notna(x))
            if 'account name' in row_str and 'contract name' in row_str:
                header_row = idx
                break

        # Read the full file with correct header
        if header_row is not None:
            print(f'   Found header at row {header_row}, skipping {header_row} rows...')
            df = pd.read_excel(CONTRACTS_FILE, skiprows=header_row)
        else:
            df = pd.read_excel(CONTRACTS_FILE)

        for _, row in df.iterrows():
            # Get tenant ID - handle various column name formats
            tenant_id = None
            for col_name in ['Tenant Id: Name', 'TenantId', 'Tenant_Id__r.Name']:
                if col_name in row:
                    tenant_id = row[col_name]
                    break

            if pd.isna(tenant_id):
                tenant_id = ''

            # Get contract name - handle various column name formats
            contract_name = None
            for col_name in ['Contract Name', 'ContractName', 'Name']:
                if col_name in row:
                    contract_name = row[col_name]
                    break

            if pd.isna(contract_name):
                contract_name = ''

            normalized_id = normalize_contract_tenant_id(tenant_id)

            if normalized_id and is_signature_contract(contract_name):
                # Get account name
                account_name = None
                for col_name in ['Account Name: Account Name', 'Account Name', 'AccountName']:
                    if col_name in row:
                        account_name = row[col_name]
                        break

                if pd.isna(account_name):
                    account_name = ''

                # Get status - check multiple column name variations
                status = None
                for status_col in ['Service Contract Status', 'Service_Contract_Status__c', 'Status']:
                    if status_col in row:
                        status = row[status_col]
                        break

                if pd.isna(status):
                    status = 'Active'  # Default if missing

                # Store ALL signature contracts (Active, Expired, Cancelled, etc.)
                # We'll filter by status later when needed
                contracts.append({
                    'accountName': str(account_name),
                    'tenantId': str(tenant_id),
                    'normalizedTenantId': normalized_id,
                    'contractName': str(contract_name),
                    'status': str(status).strip(),
                    'signaturePlan': str(contract_name),
                    'endDate': str(row.get('EndDate') or ''),
                    'isSignature': True
                })
    else:
        # Read CSV
        print(f'Reading CSV file: {CONTRACTS_FILE}')
        rows = parse_csv(CONTRACTS_FILE)

        for row in rows:
            tenant_id = (row.get('Tenant Id: Name') or
                        row.get('TenantId') or
                        row.get('Tenant_Id__r.Name') or '')

            contract_name = (row.get('Contract Name') or
                            row.get('ContractName') or
                            row.get('Name') or '')

            normalized_id = normalize_contract_tenant_id(tenant_id)

            if normalized_id and is_signature_contract(contract_name):
                contracts.append({
                    'accountName': row.get('Account Name') or row.get('AccountName') or '',
                    'tenantId': tenant_id,
                    'normalizedTenantId': normalized_id,
                    'contractName': contract_name,
                    'status': row.get('Status') or row.get('Service_Contract_Status__c') or 'Active',
                    'signaturePlan': contract_name,
                    'endDate': row.get('EndDate') or '',
                    'isSignature': True
                })

    return contracts

def match_data(monitoring_data, contracts):
    """Match monitoring data to contracts - NEW LOGIC"""
    # Build lookups
    monitoring_by_eid = defaultdict(list)
    for m in monitoring_data:
        monitoring_by_eid[m['normalizedEid']].append(m)

    # Group contracts by account
    account_map = {}
    for contract in contracts:
        acc_name = contract['accountName']
        if acc_name not in account_map:
            account_map[acc_name] = {
                'accountName': acc_name,
                'tenantIds': [],
                'contracts': [],
                'hasActiveContract': False
            }

        account_map[acc_name]['tenantIds'].append(contract['tenantId'])
        account_map[acc_name]['contracts'].append(contract)
        if contract['status'].lower() == 'active':
            account_map[acc_name]['hasActiveContract'] = True

    # Match each account to monitoring
    signature_leveraged = []
    signature_not_leveraged = []

    for account in account_map.values():
        total_monitors = 0
        has_monitoring = False
        eids_with_prom = []

        for tenant_id in account['tenantIds']:
            normalized_id = normalize_contract_tenant_id(tenant_id)
            if normalized_id in monitoring_by_eid:
                has_monitoring = True
                eids_with_prom.append(tenant_id)
                for m in monitoring_by_eid[normalized_id]:
                    total_monitors += m['monitors']

        # NEW LOGIC: Minimum 1 tenant with ProM = enabled
        if account['hasActiveContract']:
            if has_monitoring:  # At least 1 tenant has ProM
                signature_leveraged.append({
                    **account,
                    'monitors': total_monitors,
                    'isLeveraged': True,
                    'eidsWithProm': eids_with_prom
                })
            else:
                signature_not_leveraged.append({
                    **account,
                    'monitors': 0,
                    'isLeveraged': False,
                    'eidsWithProm': []
                })

    # Find non-signature accounts with monitoring
    # ONLY exclude specific EIDs that have ACTIVE signature contracts
    active_signature_tenant_ids = set(
        normalize_contract_tenant_id(c['tenantId'])
        for c in contracts
        if c['status'].lower() == 'active'
    )

    # Build a lookup: EID → Contract Status (for inactive contracts)
    eid_to_inactive_status = {}
    for c in contracts:
        normalized_id = normalize_contract_tenant_id(c['tenantId'])
        if c['status'].lower() != 'active' and normalized_id:
            # Store the most relevant inactive status
            eid_to_inactive_status[normalized_id] = c['status']

    # Get monitoring records where EID has NO active signature contract
    non_sig_monitoring = [
        m for m in monitoring_data
        if m['normalizedEid'] not in active_signature_tenant_ids
    ]

    # Group by account name to get unique ACCOUNTS (not EIDs)
    non_sig_accounts = {}
    for m in non_sig_monitoring:
        acc_name = m['customerName']
        normalized_eid = m['normalizedEid']

        # Determine reason
        if normalized_eid.startswith('mid:'):
            # Unresolved MID — parent EID unknown, cannot check contracts
            mid_num = normalized_eid[4:]
            reason = f"MID unresolved (run: python3 resolve-mids.py → .mcmember {mid_num} in SupportBot)"
        elif normalized_eid in eid_to_inactive_status:
            reason = f"Signature Contract {eid_to_inactive_status[normalized_eid]}"
        else:
            reason = "No Signature Contract"

        if acc_name not in non_sig_accounts:
            non_sig_accounts[acc_name] = {
                'customerName': acc_name,
                'tenantIds': [],
                'monitors': 0,
                'reason': reason  # Use first reason found
            }
        non_sig_accounts[acc_name]['tenantIds'].append(m['tenantId'])
        non_sig_accounts[acc_name]['monitors'] += m['monitors']

    non_signature_with_prom = list(non_sig_accounts.values())

    return {
        'signatureLeveraged': signature_leveraged,
        'signatureNotLeveraged': signature_not_leveraged,
        'nonSignatureWithProm': non_signature_with_prom
    }

def generate_summary_stats(monitoring_data, matched):
    """Generate summary statistics - NEW METRICS"""
    total_tenants = len(monitoring_data)
    total_monitors = sum(m['monitors'] for m in monitoring_data)
    total_alerts = total_monitors

    total_signature_accounts = (
        len(matched['signatureLeveraged']) +
        len(matched['signatureNotLeveraged'])
    )

    signature_with_prom = len(matched['signatureLeveraged'])
    signature_not_leveraged = len(matched['signatureNotLeveraged'])
    non_signature_with_prom = len(matched['nonSignatureWithProm'])

    return {
        'totalSignatureAccounts': total_signature_accounts,
        'signatureWithProm': signature_with_prom,
        'promEnabledTenants': total_tenants,
        'signatureNotLeveraged': signature_not_leveraged,
        'nonSignatureWithProm': non_signature_with_prom,
        'totalAlerts': total_alerts,
    }

def generate_growth_trend(contracts):
    """Generate growth trend from history snapshots directory.
    Reads all dated JSON snapshots from data/history/ folder.
    Falls back to computing from MONTHS if no history exists.
    """
    trend = []

    # Read from history snapshots if they exist
    if HISTORY_DIR.exists():
        snapshot_files = sorted(HISTORY_DIR.glob('*.json'))
        for snap_file in snapshot_files:
            try:
                with open(snap_file) as f:
                    snap = json.load(f)
                trend.append({
                    'date': snap.get('date', ''),
                    'month': snap['label'],
                    'signatureAccounts': snap['signatureAccounts'],
                    'accountsLeveragingProm': snap['signatureWithProm']
                })
            except Exception:
                pass

    # Fallback: compute from MONTHS CSV files if no history
    if not trend:
        for month_data in MONTHS:
            monitoring = load_monitoring_data(
                month_data['date'],
                month_data['month'],
                month_data['year'],
                month_data.get('combined', False)
            )
            if not monitoring:
                continue
            matched = match_data(monitoring, contracts)
            total_sig = len(matched['signatureLeveraged']) + len(matched['signatureNotLeveraged'])
            sort_key = month_data.get('sort_key')
            trend.append({
                'date': sort_key.strftime('%Y-%m-%d') if sort_key else '',
                'month': month_data['label'],
                'signatureAccounts': total_sig,
                'accountsLeveragingProm': len(matched['signatureLeveraged'])
            })

    return trend

def generate_top_tenants(monitoring_data, matched):
    """Generate top 10 tenants"""
    signature_eids = set()
    for account in matched['signatureLeveraged']:
        for contract in account['contracts']:
            eid = normalize_contract_tenant_id(contract['tenantId'])
            if eid:
                signature_eids.add(eid)

    sorted_tenants = sorted(monitoring_data, key=lambda x: x['monitors'], reverse=True)

    top10 = []
    for i, tenant in enumerate(sorted_tenants[:10]):
        top10.append({
            'rank': i + 1,
            'customerName': tenant['customerName'],
            'tenantId': tenant['tenantId'],
            'monitors': tenant['monitors'],
            'alerts': tenant['alerts'],
            'region': tenant['region'],
            'isSignature': tenant['normalizedEid'] in signature_eids,
            'status': 'Active'
        })

    return top10

def generate_leverage_accounts(matched, monitoring_by_eid):
    """Generate accounts for leverage table - NEW TABLE"""
    leverage_accounts = []

    # Signature accounts
    for acc in matched['signatureLeveraged']:
        leverage_accounts.append({
            'accountName': acc['accountName'],
            'serviceProvider': 'Marketing Cloud',
            'isSignature': True,
            'eids': acc.get('eidsWithProm', []),
            'isLeveraged': True,
            'hasMonitoring': True,
            'reason': None
        })

    for acc in matched['signatureNotLeveraged']:
        leverage_accounts.append({
            'accountName': acc['accountName'],
            'serviceProvider': 'Marketing Cloud',
            'isSignature': True,
            'eids': [],
            'isLeveraged': False,
            'hasMonitoring': False,
            'reason': None
        })

    # Non-signature accounts with ProM
    # Now matched['nonSignatureWithProm'] is already grouped by account
    for acc in matched['nonSignatureWithProm']:
        leverage_accounts.append({
            'accountName': acc['customerName'],
            'serviceProvider': 'Marketing Cloud',
            'isSignature': False,
            'eids': acc.get('tenantIds', []),
            'isLeveraged': True,
            'hasMonitoring': True,
            'reason': acc.get('reason', 'No Signature Contract')  # Use determined reason
        })

    return leverage_accounts

def generate_javascript_file(data):
    """Generate JavaScript file content"""
    timestamp = datetime.now().strftime('%Y-%m-%d')

    js_content = f'''// MCE (Marketing Cloud Engagement) Proactive Monitoring Data
// Auto-generated on {timestamp}
// Source: UTDP Exports + Org62 Service Contracts

// ============================================================================
// SUMMARY STATISTICS
// ============================================================================

export const mceSummaryStats = {json.dumps(data['summaryStats'], indent=2)};

// ============================================================================
// MONTHLY GROWTH TREND
// ============================================================================

export const mceMonthlyGrowth = {json.dumps(data['growthTrend'], indent=2)};

// ============================================================================
// TOP MCE TENANTS BY MONITOR COUNT
// ============================================================================

export const topMCETenants = {json.dumps(data['topTenants'], indent=2)};

// ============================================================================
// SIGNATURE LEVERAGE BY ACCOUNT
// ============================================================================

export const mceLeverageAccounts = {json.dumps(data['leverageAccounts'], indent=2)};

// ============================================================================
// DATA GENERATION METADATA
// ============================================================================

export const dataMetadata = {{
  "lastUpdated": "{timestamp}",
  "dataSource": {{
    "monitoring": "UTDP Exports (CSV files)",
    "contracts": "{data['contractsSource']}",
    "matchingLogic": "Tenant ID (EID) cross-reference"
  }},
  "generationScript": "generateMCEData.py",
  "stats": {{
    "totalMonitoring": {data['summaryStats']['promEnabledTenants']},
    "totalSignatureAccounts": {data['summaryStats']['totalSignatureAccounts']},
    "signatureWithProm": {data['summaryStats']['signatureWithProm']}
  }}
}};
'''
    return js_content

def main():
    print('=' * 80)
    print('MCE REAL DATA GENERATOR (Python)')
    print('=' * 80)
    print()

    print('Configuration:')
    print(f'  CSV Directory:    {CSV_DIR}')
    print(f'  Contracts Source: {CONTRACTS_FILE}')
    print(f'  Output File:      {OUTPUT_FILE}')
    print()

    # Load latest monitoring data
    latest = MONTHS[-1]
    print(f"📊 Loading monitoring data for {latest['label']}...")
    monitoring_data = load_monitoring_data(
        latest['date'],
        latest['month'],
        latest['year'],
        latest.get('combined', False)
    )
    print(f'   Found {len(monitoring_data)} tenants')
    print()

    # Load contracts
    print('📄 Loading contracts...')
    contracts = load_contracts()
    print(f'   Found {len(contracts)} Signature contracts')
    print()

    # Match data
    print('🔗 Matching monitoring to contracts...')
    matched = match_data(monitoring_data, contracts)
    print(f'   ✅ Signature w/ ProM:     {len(matched["signatureLeveraged"])}')
    print(f'   ⚠️  Signature Not Leveraged: {len(matched["signatureNotLeveraged"])}')
    print(f'   ℹ️  Non-Signature with ProM: {len(matched["nonSignatureWithProm"])}')
    print()

    # Generate all data structures
    print('⚙️  Generating data structures...')

    summary_stats = generate_summary_stats(monitoring_data, matched)
    growth_trend = generate_growth_trend(contracts)
    top_tenants = generate_top_tenants(monitoring_data, matched)

    # Build monitoring lookup for leverage accounts
    monitoring_by_eid = defaultdict(list)
    for m in monitoring_data:
        monitoring_by_eid[m['normalizedEid']].append(m)

    leverage_accounts = generate_leverage_accounts(matched, monitoring_by_eid)

    output_data = {
        'summaryStats': summary_stats,
        'growthTrend': growth_trend,
        'topTenants': top_tenants,
        'leverageAccounts': leverage_accounts,
        'contractsSource': str(CONTRACTS_FILE)
    }

    print('   ✅ Complete')
    print()

    # Generate JavaScript file
    print(f'📝 Writing output to {OUTPUT_FILE}...')
    js_content = generate_javascript_file(output_data)
    OUTPUT_FILE.write_text(js_content)
    print('   ✅ Complete')
    print()

    print('=' * 80)
    print('✅ GENERATION COMPLETE')
    print('=' * 80)
    print()
    print('Summary:')
    print(f'  Signature Accounts:         {summary_stats["totalSignatureAccounts"]}')
    print(f'  Signature w/ ProM:          {summary_stats["signatureWithProm"]}')
    print(f'  ProM Enabled Tenants:       {summary_stats["promEnabledTenants"]}')
    print(f'  Signature Not Leveraged:    {summary_stats["signatureNotLeveraged"]}')
    print(f'  Non-Signature w/ ProM:      {summary_stats["nonSignatureWithProm"]}')
    print(f'  Total Alerts:               {summary_stats["totalAlerts"]}')
    print()
    print(f'📄 Output file: {OUTPUT_FILE}')
    print()

    # Warn about unresolved MIDs
    unresolved = [
        m for m in monitoring_data
        if m['normalizedEid'].startswith('mid:')
    ]
    if unresolved:
        unresolved_mids = sorted({m['tenantId'] for m in unresolved})
        print('⚠️  UNRESOLVED MIDs (cannot match to contracts):')
        print(f'   Count: {len(unresolved_mids)}')
        print(f'   Run:   python3 resolve-mids.py')
        print(f'   Then:  look each up in Slack SupportBot using .mcmember <number>')
        print(f'   MIDs:  {", ".join(unresolved_mids[:10])}{"..." if len(unresolved_mids) > 10 else ""}')
        print()
    else:
        unresolved_count = sum(1 for v in MID_TO_EID.values() if v)
        if unresolved_count or load_mid_cache():
            print(f'✅ All MIDs resolved via cache ({len(MID_TO_EID)} mappings loaded)')
            print()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
