// MCE (Marketing Cloud Engagement) Proactive Monitoring Data
// Auto-generated on 2026-06-20
// Source: UTDP Exports + Org62 Service Contracts

// ============================================================================
// SUMMARY STATISTICS
// ============================================================================

export const mceSummaryStats = {
  "promEnabledTenants": 836,
  "totalAccounts": 658,
  "totalMonitors": 2428,
  "totalAlerts": 2428,
  "avgMonitorsPerTenant": 2.9,
  "totalSignatureContracts": 3,
  "signatureLeveraged": 2,
  "leverageRate": 66.7,
  "signatureNotLeveraged": 1,
  "nonSignatureWithProm": 834,
  "naRegion": {
    "tenants": 724,
    "monitors": 2148,
    "percentage": 86.6
  },
  "euRegion": {
    "tenants": 112,
    "monitors": 280,
    "percentage": 13.4
  }
};

// ============================================================================
// MONTHLY GROWTH TREND
// ============================================================================

export const mceMonthlyGrowth = [
  {
    "month": "Jun 2026",
    "tenants": 836,
    "monitors": 2428,
    "accounts": 658,
    "signatureLeveraged": 2
  }
];

// ============================================================================
// TOP MCE TENANTS BY MONITOR COUNT
// ============================================================================

export const topMCETenants = [
  {
    "rank": 1,
    "customerName": "ALSAC",
    "tenantId": "E524004459",
    "monitors": 12,
    "alerts": 12,
    "region": "NA",
    "isSignature": true,
    "status": "Active"
  },
  {
    "rank": 2,
    "customerName": "NBC_Sports_Group",
    "tenantId": "E7208686",
    "monitors": 12,
    "alerts": 12,
    "region": "NA",
    "isSignature": false,
    "status": "Active"
  },
  {
    "rank": 3,
    "customerName": "AxosFinancial",
    "tenantId": "E6241641",
    "monitors": 11,
    "alerts": 11,
    "region": "NA",
    "isSignature": false,
    "status": "Active"
  },
  {
    "rank": 4,
    "customerName": "Trends_International",
    "tenantId": "E546003944",
    "monitors": 11,
    "alerts": 11,
    "region": "NA",
    "isSignature": false,
    "status": "Active"
  },
  {
    "rank": 5,
    "customerName": "Bloomingdales",
    "tenantId": "E110007381",
    "monitors": 10,
    "alerts": 10,
    "region": "NA",
    "isSignature": false,
    "status": "Active"
  },
  {
    "rank": 6,
    "customerName": "Geico",
    "tenantId": "E523010029",
    "monitors": 10,
    "alerts": 10,
    "region": "NA",
    "isSignature": true,
    "status": "Active"
  },
  {
    "rank": 7,
    "customerName": "RoyalBankofCanada",
    "tenantId": "E1065704",
    "monitors": 10,
    "alerts": 10,
    "region": "NA",
    "isSignature": false,
    "status": "Active"
  },
  {
    "rank": 8,
    "customerName": "Takeda",
    "tenantId": "E515002200",
    "monitors": 10,
    "alerts": 10,
    "region": "NA",
    "isSignature": false,
    "status": "Active"
  },
  {
    "rank": 9,
    "customerName": "WSI",
    "tenantId": "E514023470",
    "monitors": 10,
    "alerts": 10,
    "region": "NA",
    "isSignature": false,
    "status": "Active"
  },
  {
    "rank": 10,
    "customerName": "BOA",
    "tenantId": "E522000104",
    "monitors": 9,
    "alerts": 9,
    "region": "NA",
    "isSignature": false,
    "status": "Active"
  }
];

// ============================================================================
// SIGNATURE LEVERAGE ANALYSIS
// ============================================================================

export const signatureLeveragedAccounts = [
  {
    "accountName": "Globex",
    "tenantIds": [
      "524004459"
    ],
    "monitors": 12,
    "contractStatus": "Active",
    "signaturePlan": "Signature Success - MC Engagement"
  },
  {
    "accountName": "Initech",
    "tenantIds": [
      "523010029"
    ],
    "monitors": 10,
    "contractStatus": "Active",
    "signaturePlan": "Signature Success Plan- MC Engagement"
  }
];

export const signatureNotLeveragedAccounts = [
  {
    "accountName": "Umbrella",
    "tenantIds": [
      "777000111"
    ],
    "contractStatus": "Active",
    "reason": "No monitoring configured",
    "signaturePlan": "Signature Success - US Only - MC Engagement"
  }
];

export const nonSignatureWithPromAccounts = [
  {
    "accountName": "NBC_Sports_Group",
    "tenantIds": [
      "E7208686"
    ],
    "monitors": 12,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "AxosFinancial",
    "tenantIds": [
      "E6241641"
    ],
    "monitors": 11,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "Trends_International",
    "tenantIds": [
      "E546003944"
    ],
    "monitors": 11,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "Bloomingdales",
    "tenantIds": [
      "E110007381"
    ],
    "monitors": 10,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "RoyalBankofCanada",
    "tenantIds": [
      "E1065704"
    ],
    "monitors": 10,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "Takeda",
    "tenantIds": [
      "E515002200"
    ],
    "monitors": 10,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "WSI",
    "tenantIds": [
      "E514023470"
    ],
    "monitors": 10,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "BOA",
    "tenantIds": [
      "E522000104"
    ],
    "monitors": 9,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "Eli_Lilly",
    "tenantIds": [
      "E6195267"
    ],
    "monitors": 9,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "Gap",
    "tenantIds": [
      "E7000682"
    ],
    "monitors": 9,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "Lululemon",
    "tenantIds": [
      "E514002114"
    ],
    "monitors": 9,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "Sirius_XM",
    "tenantIds": [
      "E546000856"
    ],
    "monitors": 9,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "TheReinalt-Thomas",
    "tenantIds": [
      "E1045947"
    ],
    "monitors": 9,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "Woolworths",
    "tenantIds": [
      "E6370104"
    ],
    "monitors": 9,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "AXS",
    "tenantIds": [
      "E514035855"
    ],
    "monitors": 8,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "BGRetail",
    "tenantIds": [
      "E7221103"
    ],
    "monitors": 8,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "CapitalOne",
    "tenantIds": [
      "E7257764"
    ],
    "monitors": 8,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "CrateBarrel",
    "tenantIds": [
      "E7200632"
    ],
    "monitors": 8,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "Fidelity",
    "tenantIds": [
      "E1050979"
    ],
    "monitors": 8,
    "reason": "No Signature Contract",
    "contractStatus": null
  },
  {
    "accountName": "JPMorganChaseBank",
    "tenantIds": [
      "E514003104"
    ],
    "monitors": 8,
    "reason": "No Signature Contract",
    "contractStatus": null
  }
];

// ============================================================================
// REGIONAL BREAKDOWN
// ============================================================================

export const mceRegionalBreakdown = [
  {
    "region": "North America",
    "code": "NA",
    "tenants": 724,
    "monitors": 2148,
    "percentage": 86.6
  },
  {
    "region": "Europe",
    "code": "EU",
    "tenants": 112,
    "monitors": 280,
    "percentage": 13.4
  }
];

// ============================================================================
// DATA GENERATION METADATA
// ============================================================================

export const dataMetadata = {
  "lastUpdated": "2026-06-20",
  "dataSource": {
    "monitoring": "UTDP Exports (CSV files)",
    "contracts": "/Users/rinku.soni/prom-signature-extension/sample/contracts.csv",
    "matchingLogic": "Tenant ID (EID) cross-reference"
  },
  "generationScript": "generateMCEData.py",
  "stats": {
    "totalMonitoring": 836,
    "totalContracts": 3,
    "matchedAccounts": 2
  }
};
