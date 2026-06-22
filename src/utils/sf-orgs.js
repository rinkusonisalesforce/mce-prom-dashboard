'use strict';

/*
 * Multi-org wrapper around the auth flow in jsforce.js.
 *
 * The user's jsforce.js is OrgCS-only (SALESFORCE_SERVER_URL is hard-coded), so
 * this mirrors the exact same pattern — read the `sid` cookie, build a
 * jsforce.Connection — but parametrized by org URL. It REUSES `getCookie` from
 * jsforce.js so the cookie access stays identical.
 *
 * Depends on globals: getCookie (jsforce.js), jsforce (vendor), SF_ORGS,
 * SF_API_VERSION (config.js).
 */

function resolveOrgUrl(org) {
  if (!org) throw new Error('resolveOrgUrl: org is required.');
  if (SF_ORGS[org]) return SF_ORGS[org];
  if (/^https?:\/\//.test(org)) return org;
  throw new Error('resolveOrgUrl: unknown org "' + org + '".');
}

async function getSessionIdForOrg(org) {
  const url = resolveOrgUrl(org);
  const cookie = await getCookie(url, 'sid');
  if (cookie && cookie.value) {
    console.log('[SF Session] Found session cookie at', url);
    return cookie.value;
  }
  throw new Error('No Salesforce session for ' + url + '. Please log in first.');
}

function createConnectionForOrg(org, sessionId, version) {
  if (!sessionId || typeof jsforce === 'undefined') {
    throw new Error('Session ID or jsforce library not available');
  }
  return new jsforce.Connection({
    serverUrl: resolveOrgUrl(org),
    sessionId: sessionId,
    version: version || SF_API_VERSION,
  });
}

/**
 * Connect to an org by reading its session cookie.
 * @param {('org62'|'orgcs'|string)} org
 * @returns {Promise<jsforce.Connection>}
 */
async function connectOrg(org) {
  const sessionId = await getSessionIdForOrg(org);
  return createConnectionForOrg(org, sessionId, SF_API_VERSION);
}

/**
 * Fetch Service Contracts via SOQL and normalize to ContractRow[].
 * @param {jsforce.Connection} connection
 * @param {string} [soql]
 * @returns {Promise<object[]>}
 */
async function fetchServiceContracts(connection, soql) {
  // autoFetch pages past the 2000-row cap; maxFetch caps total to be safe.
  const result = await connection.query(soql || DEFAULT_CONTRACTS_SOQL, {
    autoFetch: true,
    maxFetch: 100000,
  });
  const records = result.records || [];
  // Deterministic mapping for the known fields; fall back to fuzzy flatten for
  // custom/overridden SOQL that selects different columns.
  return records.map((r) =>
    isKnownShape(r) ? mapSObjectContract(r) : ProMData.mapContractRecord(flattenRecord(r))
  );
}

function isKnownShape(r) {
  return r && ('Tenant_Id__r' in r || 'Tenant_Id__c' in r || 'ServiceProvider__c' in r);
}

/** Deterministic mapper for the default SOQL field set. */
function mapSObjectContract(r) {
  return {
    accountName: (r.Account && r.Account.Name) || r.AccountId || '',
    serviceProvider: r.ServiceProvider__c || '',
    contractName: r.Name || '',
    // Tenant_Id__c is a lookup; the EID/tenant value is the related record's Name.
    tenantId: (r.Tenant_Id__r && r.Tenant_Id__r.Name) || r.Tenant_Id__c || '',
    status: r.Service_Contract_Status__c || '',
    // EndDate is the date used for both expired and cancelled reasons.
    endDate: dateOnly(r.EndDate),
    cancelledDate: dateOnly(r.EndDate),
  };
}

/** Reduce a Salesforce date/datetime to YYYY-MM-DD. */
function dateOnly(v) {
  return v ? String(v).slice(0, 10) : '';
}

/**
 * Flatten an SObject into report-like keys WITHOUT clobbering. Top-level scalar
 * fields keep their API name ("Name", "ServiceProvider__c"); relationship
 * fields are emitted as qualified labels ("Account Name", "Tenant Id Name") so a
 * related "Name" never overwrites the record's own "Name".
 */
function flattenRecord(rec) {
  const flat = {};
  for (const key of Object.keys(rec || {})) {
    if (key === 'attributes') continue;
    const val = rec[key];
    if (val && typeof val === 'object' && !Array.isArray(val)) {
      const relName = key.replace(/__r$/, '').replace(/_/g, ' '); // Tenant_Id__r -> "Tenant Id"
      for (const sub of Object.keys(val)) {
        if (sub === 'attributes') continue;
        const sv = val[sub];
        if (sv && typeof sv === 'object') continue; // skip deeper nesting
        flat[relName + ' ' + sub] = sv; // "Account Name", "Tenant Id Name"
      }
    } else {
      flat[key] = val;
    }
  }
  return flat;
}
