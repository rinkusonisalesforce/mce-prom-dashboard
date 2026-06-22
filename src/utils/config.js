'use strict';

/*
 * Global config for the extension. Loaded BEFORE jsforce.js so that the global
 * `SF_API_VERSION` referenced by the user's createSalesforceConnection exists.
 */
// eslint-disable-next-line no-var, no-unused-vars
var SF_API_VERSION = '60.0';

// Salesforce orgs we read the `sid` cookie from / query.
var SF_ORGS = {
  org62: 'https://org62.my.salesforce.com',
  orgcs: 'https://orgcs.my.salesforce.com',
};

// Contract names explicitly classified as Signature (case-insensitive). Any
// name containing "signature" is also treated as Signature (see core.js).
var SIGNATURE_CONTRACT_NAMES = [
  'Signature Success - MC Engagement',
  'Signature Success Plan- MC Engagement',
  'Signature Success - US Only - MC Engagement',
];

// Service_Contract_Status__c picklist values. CONFIRM exact strings per org.
// Used to (a) decide whether a signature contract is currently active, and
// (b) explain why a non-signature ProM account lost its signature plan.
var SF_CONTRACT_STATUS = {
  active: 'Active',
  cancelled: 'Cancelled',
  expired: 'Expired',
};

// Default SOQL for live fetches, mirroring the report filters:
//   Contract Name contains "MC Engagement", ServiceProvider = Marketing Cloud.
// NOTE: the Status = Active filter is intentionally NOT applied here — we fetch
// ALL statuses so we can explain WHY a ProM account lost its signature plan
// (cancelled/expired). Active-vs-not is then decided in code (core.js).
// Tenant_Id__c is a lookup, so the matchable tenant/EID is Tenant_Id__r.Name.
// EndDate (standard) is used for both the expired and cancelled reason dates.
var DEFAULT_CONTRACTS_SOQL =
  "SELECT Id, Name, ServiceProvider__c, Service_Contract_Status__c, " +
  "AccountId, Account.Name, Tenant_Id__c, Tenant_Id__r.Name, EndDate " +
  "FROM ServiceContract " +
  "WHERE Name LIKE '%MC Engagement%' " +
  "AND ServiceProvider__c = 'Marketing Cloud'";

// The dashboard fetches contracts directly from Org62 only.
var DEFAULT_ORG = 'org62';

// UTDP CSVs live in this bundled folder, named na_<month><year>.csv /
// eu_<month><year>.csv (e.g. na_june2026.csv). Files are auto-discovered by
// probing this many months back from the current month — no index to maintain.
var DATA_DIR = 'data';
var DATA_PROBE_MONTHS = 24;
