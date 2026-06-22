/**
 * Org62 ServiceContract fetcher for MCE Dashboard
 * Adapted from prom-signature-extension
 */

const SF_API_VERSION = '60.0';
const ORG62_URL = 'https://org62.my.salesforce.com';

const DEFAULT_CONTRACTS_SOQL =
  "SELECT Id, Name, ServiceProvider__c, Service_Contract_Status__c, " +
  "AccountId, Account.Name, Tenant_Id__c, Tenant_Id__r.Name, EndDate " +
  "FROM ServiceContract " +
  "WHERE Name LIKE '%MC Engagement%' " +
  "AND ServiceProvider__c = 'Marketing Cloud'";

/**
 * Get session ID from org62 cookie
 * NOTE: This only works in a Chrome extension context with host_permissions
 */
async function getOrg62SessionId() {
  if (typeof chrome === 'undefined' || !chrome.cookies) {
    throw new Error('Chrome cookies API not available. This must run in an extension context.');
  }

  return new Promise((resolve, reject) => {
    chrome.cookies.get(
      { url: ORG62_URL, name: 'sid' },
      (cookie) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
        } else if (cookie && cookie.value) {
          console.log('[Org62] Found session cookie');
          resolve(cookie.value);
        } else {
          reject(new Error('No Salesforce session for Org62. Please log in first.'));
        }
      }
    );
  });
}

/**
 * Create JSForce connection to Org62
 */
function createOrg62Connection(sessionId) {
  if (!sessionId || typeof jsforce === 'undefined') {
    throw new Error('Session ID or jsforce library not available');
  }
  return new jsforce.Connection({
    serverUrl: ORG62_URL,
    sessionId: sessionId,
    version: SF_API_VERSION,
  });
}

/**
 * Fetch Service Contracts from Org62
 */
export async function fetchOrg62Contracts(soql) {
  const sessionId = await getOrg62SessionId();
  const conn = createOrg62Connection(sessionId);

  const result = await conn.query(soql || DEFAULT_CONTRACTS_SOQL, {
    autoFetch: true,
    maxFetch: 100000,
  });

  const records = result.records || [];
  return records.map(mapContract);
}

/**
 * Map Salesforce contract record to our format
 */
function mapContract(r) {
  return {
    accountName: (r.Account && r.Account.Name) || r.AccountId || '',
    serviceProvider: r.ServiceProvider__c || '',
    contractName: r.Name || '',
    tenantId: (r.Tenant_Id__r && r.Tenant_Id__r.Name) || r.Tenant_Id__c || '',
    status: r.Service_Contract_Status__c || '',
    endDate: dateOnly(r.EndDate),
  };
}

function dateOnly(v) {
  return v ? String(v).slice(0, 10) : '';
}

/**
 * Check if we can access Org62 (are we in extension context?)
 */
export function canAccessOrg62() {
  return typeof chrome !== 'undefined' && typeof chrome.cookies !== 'undefined';
}
