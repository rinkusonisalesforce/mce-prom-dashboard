#!/usr/bin/env python3
"""
Generate MCE Real Data from UTDP CSVs and Org62 Contracts
Supports both .csv and .xlsx formats for contracts
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
for ext in ['.xlsx', '.csv']:
    candidate = DATA_DIR / f'contracts{ext}'
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
    na_file = CSV_DIR / f'na_{month_name}{year}.csv'
    eu_file = CSV_DIR / f'eu_{month_name}{year}.csv'

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
    """Load contracts from CSV"""
    if not CONTRACTS_FILE.exists():
        print(f'⚠️  Contracts file not found: {CONTRACTS_FILE}')
        return []

    rows = parse_csv(CONTRACTS_FILE)

    contracts = []
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
    """Match monitoring data to contracts"""
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

        for tenant_id in account['tenantIds']:
            normalized_id = normalize_contract_tenant_id(tenant_id)
            if normalized_id in monitoring_by_eid:
                has_monitoring = True
                for m in monitoring_by_eid[normalized_id]:
                    total_monitors += m['monitors']

        if account['hasActiveContract']:
            if has_monitoring:
                signature_leveraged.append({
                    **account,
                    'monitors': total_monitors,
                    'isLeveraged': True
                })
            else:
                signature_not_leveraged.append({
                    **account,
                    'monitors': 0,
                    'isLeveraged': False
                })

    # Find non-signature tenants with monitoring
    signature_tenant_ids = set(
        normalize_contract_tenant_id(c['tenantId'])
        for c in contracts
    )

    non_signature_with_prom = [
        m for m in monitoring_data
        if m['normalizedEid'] not in signature_tenant_ids
    ]

    return {
        'signatureLeveraged': signature_leveraged,
        'signatureNotLeveraged': signature_not_leveraged,
        'nonSignatureWithProm': non_signature_with_prom
    }

def generate_summary_stats(monitoring_data, matched):
    """Generate summary statistics"""
    total_tenants = len(monitoring_data)
    unique_accounts = len(set(m['customerName'] for m in monitoring_data))
    total_monitors = sum(m['monitors'] for m in monitoring_data)
    total_alerts = total_monitors

    na_data = [m for m in monitoring_data if m['region'] == 'NA']
    eu_data = [m for m in monitoring_data if m['region'] == 'EU']

    total_signature_contracts = (
        len(matched['signatureLeveraged']) +
        len(matched['signatureNotLeveraged'])
    )

    signature_leveraged = len(matched['signatureLeveraged'])
    leverage_rate = (
        (signature_leveraged / total_signature_contracts * 100)
        if total_signature_contracts > 0 else 0
    )

    return {
        'promEnabledTenants': total_tenants,
        'totalAccounts': unique_accounts,
        'totalMonitors': total_monitors,
        'totalAlerts': total_alerts,
        'avgMonitorsPerTenant': round(total_monitors / total_tenants, 1) if total_tenants > 0 else 0,
        'totalSignatureContracts': total_signature_contracts,
        'signatureLeveraged': signature_leveraged,
        'leverageRate': round(leverage_rate, 1),
        'signatureNotLeveraged': len(matched['signatureNotLeveraged']),
        'nonSignatureWithProm': len(matched['nonSignatureWithProm']),
        'naRegion': {
            'tenants': len(na_data),
            'monitors': sum(m['monitors'] for m in na_data),
            'percentage': round(len(na_data) / total_tenants * 100, 1) if total_tenants > 0 else 0
        },
        'euRegion': {
            'tenants': len(eu_data),
            'monitors': sum(m['monitors'] for m in eu_data),
            'percentage': round(len(eu_data) / total_tenants * 100, 1) if total_tenants > 0 else 0
        }
    }

def generate_growth_trend(contracts):
    """Generate monthly growth trend"""
    trend = []

    for month in MONTHS:
        monitoring = load_monitoring_data(month['name'], month['year'])

        if not monitoring:
            continue

        matched = match_data(monitoring, contracts)
        unique_accounts = len(set(m['customerName'] for m in monitoring))

        trend.append({
            'month': month['label'],
            'tenants': len(monitoring),
            'monitors': sum(m['monitors'] for m in monitoring),
            'accounts': unique_accounts,
            'signatureLeveraged': len(matched['signatureLeveraged'])
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
// SIGNATURE LEVERAGE ANALYSIS
// ============================================================================

export const signatureLeveragedAccounts = {json.dumps(data['signatureLeveraged'][:20], indent=2)};

export const signatureNotLeveragedAccounts = {json.dumps(data['signatureNotLeveraged'][:20], indent=2)};

export const nonSignatureWithPromAccounts = {json.dumps(data['nonSignatureWithProm'][:20], indent=2)};

// ============================================================================
// REGIONAL BREAKDOWN
// ============================================================================

export const mceRegionalBreakdown = {json.dumps(data['regionalBreakdown'], indent=2)};

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
    "totalContracts": {data['summaryStats']['totalSignatureContracts']},
    "matchedAccounts": {data['summaryStats']['signatureLeveraged']}
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
    print(f'   ✅ Signature Leveraged:     {len(matched["signatureLeveraged"])}')
    print(f'   ⚠️  Signature Not Leveraged: {len(matched["signatureNotLeveraged"])}')
    print(f'   ℹ️  Non-Signature with ProM: {len(matched["nonSignatureWithProm"])}')
    print()

    # Generate all data structures
    print('⚙️  Generating data structures...')

    summary_stats = generate_summary_stats(monitoring_data, matched)
    growth_trend = generate_growth_trend(contracts)
    top_tenants = generate_top_tenants(monitoring_data, matched)

    regional_breakdown = [
        {
            'region': 'North America',
            'code': 'NA',
            **summary_stats['naRegion']
        },
        {
            'region': 'Europe',
            'code': 'EU',
            **summary_stats['euRegion']
        }
    ]

    # Format accounts data
    signature_leveraged_accounts = []
    for acc in matched['signatureLeveraged'][:20]:
        signature_leveraged_accounts.append({
            'accountName': acc['accountName'],
            'tenantIds': acc['tenantIds'],
            'monitors': acc['monitors'],
            'contractStatus': 'Active',
            'signaturePlan': acc['contracts'][0]['signaturePlan'] if acc['contracts'] else ''
        })

    signature_not_leveraged_accounts = []
    for acc in matched['signatureNotLeveraged'][:20]:
        signature_not_leveraged_accounts.append({
            'accountName': acc['accountName'],
            'tenantIds': acc['tenantIds'],
            'contractStatus': 'Active',
            'reason': 'No monitoring configured',
            'signaturePlan': acc['contracts'][0]['signaturePlan'] if acc['contracts'] else ''
        })

    non_signature_accounts = []
    for m in matched['nonSignatureWithProm'][:20]:
        non_signature_accounts.append({
            'accountName': m['customerName'],
            'tenantIds': [m['tenantId']],
            'monitors': m['monitors'],
            'reason': 'No Signature Contract',
            'contractStatus': None
        })

    output_data = {
        'summaryStats': summary_stats,
        'growthTrend': growth_trend,
        'topTenants': top_tenants,
        'signatureLeveraged': signature_leveraged_accounts,
        'signatureNotLeveraged': signature_not_leveraged_accounts,
        'nonSignatureWithProm': non_signature_accounts,
        'regionalBreakdown': regional_breakdown,
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
    print(f'  Total Tenants:              {summary_stats["promEnabledTenants"]}')
    print(f'  Total Monitors:             {summary_stats["totalMonitors"]}')
    print(f'  Signature Contracts:        {summary_stats["totalSignatureContracts"]}')
    print(f'  Leverage Rate:              {summary_stats["leverageRate"]}%')
    print(f'  Leveraged Accounts:         {summary_stats["signatureLeveraged"]}')
    print(f'  Not Leveraged Accounts:     {summary_stats["signatureNotLeveraged"]}')
    print()
    print(f'📄 Output file: {OUTPUT_FILE}')
    print()
    print('Next steps:')
    print('  1. Create React dashboard (or use GitHub one as base)')
    print('  2. Copy mceRealData.js to dashboard/src/data/')
    print('  3. Update imports in App.jsx')
    print('  4. Run: npm run dev')
    print('  5. Deploy: npm run build && npm run deploy')
    print()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
