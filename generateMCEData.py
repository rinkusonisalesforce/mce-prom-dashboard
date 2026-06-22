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

# Try to import pandas for Excel support
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Note: Install pandas for Excel support: pip3 install pandas openpyxl")

# Configuration
DATA_DIR = Path('/Users/rinku.soni/prom-signature-extension/data')
CSV_DIR = DATA_DIR

# Try to find contracts file in multiple formats
CONTRACTS_FILE = None

# Try new filename first (with status column)
for filename in ['Contracts_June2026.xlsx', 'contracts.xlsx', 'contracts.csv']:
    candidate = DATA_DIR / filename
    if candidate.exists():
        CONTRACTS_FILE = candidate
        break

# Fallback to old location if not found
if not CONTRACTS_FILE:
    CONTRACTS_FILE = Path('/Users/rinku.soni/prom-signature-extension/sample/contracts.csv')

OUTPUT_FILE = Path(__file__).parent / 'src' / 'data' / 'mceRealData.js'

SIGNATURE_PATTERNS = [
    'Signature Success - MC Engagement',
    'Signature Success Plan- MC Engagement',
    'Signature Success - US Only - MC Engagement',
]

MONTHS = [
    {'name': 'january', 'year': 2026, 'label': 'Jan 2026'},
    {'name': 'february', 'year': 2026, 'label': 'Feb 2026'},
    {'name': 'march', 'year': 2026, 'label': 'Mar 2026'},
    {'name': 'april', 'year': 2026, 'label': 'Apr 2026'},
    {'name': 'may', 'year': 2026, 'label': 'May 2026'},
    {'name': 'june', 'year': 2026, 'label': 'Jun 2026'},
]

def parse_csv(filepath):
    """Parse CSV file"""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def normalize_eid(eid):
    """Strip E/M prefix and get numeric part"""
    if not eid:
        return ''
    # Remove E/M prefix and any non-numeric characters
    import re
    digits = re.sub(r'[^0-9]', '', str(eid))
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

def load_monitoring_data(month_name, year):
    """Load monitoring data for a specific month"""
    na_file = CSV_DIR / f'NA_{month_name}{year}.csv'
    eu_file = CSV_DIR / f'EU_{month_name}{year}.csv'

    data = []

    if na_file.exists():
        rows = parse_csv(na_file)
        for row in rows:
            data.append({**row, 'region': 'NA'})

    if eu_file.exists():
        rows = parse_csv(eu_file)
        for row in rows:
            data.append({**row, 'region': 'EU'})

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

                # ONLY include ACTIVE signature contracts
                if str(status).strip().lower() == 'active':
                    contracts.append({
                        'accountName': str(account_name),
                        'tenantId': str(tenant_id),
                        'normalizedTenantId': normalized_id,
                        'contractName': str(contract_name),
                        'status': str(status),
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

    # Get monitoring records where EID has NO active signature contract
    non_sig_monitoring = [
        m for m in monitoring_data
        if m['normalizedEid'] not in active_signature_tenant_ids
    ]

    # Group by account name to get unique ACCOUNTS (not EIDs)
    non_sig_accounts = {}
    for m in non_sig_monitoring:
        acc_name = m['customerName']
        if acc_name not in non_sig_accounts:
            non_sig_accounts[acc_name] = {
                'customerName': acc_name,
                'tenantIds': [],
                'monitors': 0
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
    """Generate monthly growth trend - NEW METRICS"""
    trend = []

    for month in MONTHS:
        monitoring = load_monitoring_data(month['name'], month['year'])

        if not monitoring:
            continue

        matched = match_data(monitoring, contracts)

        # NEW: signatureAccounts and accountsLeveragingProm
        total_signature_accounts = (
            len(matched['signatureLeveraged']) +
            len(matched['signatureNotLeveraged'])
        )

        trend.append({
            'month': month['label'],
            'signatureAccounts': total_signature_accounts,
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
            'hasMonitoring': True
        })

    for acc in matched['signatureNotLeveraged']:
        leverage_accounts.append({
            'accountName': acc['accountName'],
            'serviceProvider': 'Marketing Cloud',
            'isSignature': True,
            'eids': [],
            'isLeveraged': False,
            'hasMonitoring': False
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
            'hasMonitoring': True
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

    # Load latest month monitoring data
    latest_month = MONTHS[-1]
    print(f"📊 Loading monitoring data for {latest_month['label']}...")
    monitoring_data = load_monitoring_data(latest_month['name'], latest_month['year'])
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

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
