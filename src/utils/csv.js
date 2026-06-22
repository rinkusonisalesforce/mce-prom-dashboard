'use strict';

/*
 * Dependency-free CSV parsing + UTDP/contract mappers. Works in browser
 * (window.ProMData) and Node (module.exports). No npm packages so it can ship
 * inside the extension as-is.
 */
(function (root, factory) {
  const api = factory();
  root.ProMData = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis, function () {
  /** Parse CSV text into an array of objects keyed by header row. */
  function parseCsv(text) {
    const rows = parseRows(String(text == null ? '' : text));
    if (!rows.length) return [];
    const headers = rows[0].map((h) => h.trim());
    const out = [];
    for (let i = 1; i < rows.length; i += 1) {
      const cells = rows[i];
      if (cells.length === 1 && cells[0] === '') continue; // blank line
      const rec = {};
      headers.forEach((h, idx) => {
        rec[h] = (cells[idx] !== undefined ? cells[idx] : '').trim();
      });
      out.push(rec);
    }
    return out;
  }

  /** RFC-4180-ish row tokenizer: handles quotes, escaped quotes, CRLF, commas. */
  function parseRows(text) {
    const rows = [];
    let row = [];
    let field = '';
    let inQuotes = false;
    let i = 0;
    const n = text.length;

    if (text.charCodeAt(0) === 0xfeff) i = 1; // strip BOM

    while (i < n) {
      const ch = text[i];
      if (inQuotes) {
        if (ch === '"') {
          if (text[i + 1] === '"') {
            field += '"';
            i += 2;
            continue;
          }
          inQuotes = false;
          i += 1;
          continue;
        }
        field += ch;
        i += 1;
        continue;
      }
      if (ch === '"') {
        inQuotes = true;
        i += 1;
        continue;
      }
      if (ch === ',') {
        row.push(field);
        field = '';
        i += 1;
        continue;
      }
      if (ch === '\r') {
        i += 1;
        continue;
      }
      if (ch === '\n') {
        row.push(field);
        rows.push(row);
        row = [];
        field = '';
        i += 1;
        continue;
      }
      field += ch;
      i += 1;
    }
    row.push(field);
    rows.push(row);
    return rows;
  }

  function normHeader(h) {
    return String(h || '').toLowerCase().replace(/[^a-z0-9]/g, '');
  }

  /** Pick a value by fuzzy header match. */
  function pick(record, candidates) {
    const wanted = candidates.map(normHeader);
    const entries = Object.keys(record).map((k) => [normHeader(k), record[k]]);
    for (const w of wanted) {
      const exact = entries.find((e) => e[0] === w);
      if (exact) return (exact[1] == null ? '' : exact[1]).toString();
    }
    for (const w of wanted) {
      const partial = entries.find((e) => w.length >= 3 && e[0].includes(w));
      if (partial) return (partial[1] == null ? '' : partial[1]).toString();
    }
    return '';
  }

  function mapContractRecord(r) {
    return {
      accountName: pick(r, ['Account Name', 'Account', 'AccountName']),
      serviceProvider: pick(r, ['ServiceProvider', 'Service Provider', 'Provider']),
      contractName: pick(r, ['Contract Name', 'ContractName', 'Name']),
      tenantId: pick(r, ['Tenant Id: Name', 'Tenant Id', 'TenantId', 'Tenant', 'EID']),
      status: pick(r, [
        'Service Contract Status',
        'Service_Contract_Status__c',
        'Status',
      ]),
      endDate: pick(r, ['End Date', 'EndDate', 'Expiration Date', 'Expiry Date']),
      cancelledDate: pick(r, [
        'Cancelled Date',
        'Canceled Date',
        'Cancellation Date',
        'Cancelled_Date__c',
      ]),
    };
  }

  function parseContractsCsv(text) {
    return parseCsv(text).map(mapContractRecord);
  }

  function parseUtdp(text, region) {
    return parseCsv(text).map((r) => ({
      customerName: pick(r, ['Customer_Name', 'Customer Name', 'Customer']),
      eid: pick(r, ['EID', 'Tenant Id', 'TenantId']),
      totalMonitorsEnabled:
        Number(
          pick(r, [
            'Total_Monitors_Enabled',
            'Total Monitors Enabled',
            'Monitors Enabled',
            'Monitors',
          ])
        ) || 0,
      region: region || '',
    }));
  }

  return { parseCsv, pick, normHeader, mapContractRecord, parseContractsCsv, parseUtdp };
});
