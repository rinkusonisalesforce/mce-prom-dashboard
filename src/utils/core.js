'use strict';

/*
 * Pure cross-reference logic. Works in the browser (attaches to window.ProM)
 * and in Node (module.exports) so it can be unit-tested without a browser.
 *
 * In the browser, SIGNATURE_CONTRACT_NAMES comes from config.js (global). In
 * Node tests, a fallback list is used.
 */
(function (root, factory) {
  const signatureNames =
    typeof SIGNATURE_CONTRACT_NAMES !== 'undefined'
      ? SIGNATURE_CONTRACT_NAMES
      : [
          'Signature Success - MC Engagement',
          'Signature Success Plan- MC Engagement',
          'Signature Success - US Only - MC Engagement',
        ];
  const statusConfig =
    typeof SF_CONTRACT_STATUS !== 'undefined'
      ? SF_CONTRACT_STATUS
      : { active: 'Active', cancelled: 'Cancelled', expired: 'Expired' };
  const api = factory(signatureNames, statusConfig);
  root.ProM = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis, function (signatureNames, statusConfig) {
  const SIGNATURE_NAME_SET = new Set(signatureNames.map((n) => n.trim().toLowerCase()));
  const STATUS = {
    active: String(statusConfig.active || 'Active').toLowerCase(),
    cancelled: String(statusConfig.cancelled || 'Cancelled').toLowerCase(),
    expired: String(statusConfig.expired || 'Expired').toLowerCase(),
  };

  function statusLower(s) {
    return String(s == null ? '' : s).trim().toLowerCase();
  }

  // Blank status is treated as active (CSV without a Status column, or the
  // Active-only live query) so behaviour is unchanged until statuses are present.
  function isActiveStatus(s) {
    const v = statusLower(s);
    return v === '' ? true : v === STATUS.active;
  }

  function latestDate(dates) {
    const ds = dates.filter(Boolean).map(String).sort(); // ISO dates sort lexically
    return ds.length ? ds[ds.length - 1] : '';
  }

  /**
   * Explain why a non-signature account has no active signature plan, by looking
   * at its signature contracts across ALL statuses.
   */
  function signatureReason(accountContracts) {
    const sig = (accountContracts || []).filter((c) => isSignatureContract(c.contractName));
    if (!sig.length) return { code: 'none', label: 'No signature contract', date: '' };

    const cancelled = sig.filter((c) => statusLower(c.status) === STATUS.cancelled);
    if (cancelled.length) {
      const date = latestDate(cancelled.map((c) => c.cancelledDate || c.endDate || ''));
      return { code: 'cancelled', label: date ? 'Cancelled ' + date : 'Cancelled', date };
    }
    const expired = sig.filter((c) => statusLower(c.status) === STATUS.expired);
    if (expired.length) {
      const date = latestDate(expired.map((c) => c.endDate || c.cancelledDate || ''));
      return { code: 'expired', label: date ? 'Expired ' + date : 'Expired', date };
    }
    return { code: 'inactive', label: 'Signature contract inactive', date: '' };
  }

  /**
   * Normalize a UTDP EID to its numeric part. UTDP feeds prefix ids with a
   * letter (e.g. "E524004459", "M523010029"), which is valid — strip to digits.
   */
  function normalizeEid(value) {
    if (value === null || value === undefined) return '';
    const digits = String(value).replace(/\D/g, '');
    if (!digits) return '';
    const trimmed = digits.replace(/^0+/, '');
    return trimmed === '' ? '0' : trimmed;
  }

  /**
   * Normalize an Org62 contract tenant id (the "Tenant Id: Name"). Unlike the
   * UTDP feed, a valid contract tenant is PURELY NUMERIC. Anything containing
   * letters is invalid and rejected (returns '') — e.g. "DELETED_7207794",
   * "DELETED_546013159", "00D37000000K0CP" — so they never count as an EID.
   */
  function normalizeContractTenant(value) {
    if (value === null || value === undefined) return '';
    const s = String(value).trim();
    if (!s || !/^\d+$/.test(s)) return '';
    const trimmed = s.replace(/^0+/, '');
    return trimmed === '' ? '0' : trimmed;
  }

  function isSignatureContract(contractName) {
    if (!contractName) return false;
    const name = String(contractName).trim().toLowerCase();
    if (!name) return false;
    if (SIGNATURE_NAME_SET.has(name)) return true;
    return name.includes('signature');
  }

  function isActiveSignatureContract(c) {
    return isSignatureContract(c && c.contractName) && isActiveStatus(c && c.status);
  }

  // A Signature account has at least one ACTIVE signature contract. (A cancelled
  // or expired signature contract does not keep the account "Signature".)
  function isSignatureAccount(contracts) {
    if (!Array.isArray(contracts)) return false;
    return contracts.some(isActiveSignatureContract);
  }

  /**
   * Summarize ONE month of UTDP rows (NA + EU combined) for the MCE ProM cards,
   * the Top Tenants table, and one point on the growth trend.
   *
   * - tenants:      distinct EIDs with >=1 enabled monitor (a "ProM enabled tenant")
   * - accounts:     distinct Customer_Name among those enabled tenants
   * - alertConfigs: sum of Total_Monitors_Enabled (the "alert configurations")
   * - topTenants:   per-EID rows ranked by enabled monitors (desc)
   */
  function summarizeMonth(rows) {
    const byEid = new Map();
    const accounts = new Set();
    let alertConfigs = 0;

    for (const row of rows || []) {
      if (!row) continue;
      const monitors = Number(row.totalMonitorsEnabled) || 0;
      alertConfigs += monitors;
      if (monitors < 1) continue;
      const key = normalizeEid(row.eid);
      if (!key) continue;

      const name = (row.customerName || '').trim();
      if (name) accounts.add(name.toLowerCase());

      const existing = byEid.get(key);
      if (existing) {
        existing.alertConfigs += monitors;
        if (!existing.accountName && name) existing.accountName = name;
        if (row.region) existing.regions.add(row.region);
        // Prefer the prefixed/raw EID for display if we don't have one yet.
        if (!existing.eid && row.eid) existing.eid = row.eid;
      } else {
        byEid.set(key, {
          normalized: key,
          eid: row.eid || key,
          accountName: name,
          alertConfigs: monitors,
          regions: new Set(row.region ? [row.region] : []),
        });
      }
    }

    const topTenants = Array.from(byEid.values())
      .map((t) => ({
        eid: t.eid,
        normalized: t.normalized,
        accountName: t.accountName,
        alertConfigs: t.alertConfigs,
        regions: Array.from(t.regions),
      }))
      .sort(
        (a, b) => b.alertConfigs - a.alertConfigs || a.eid.localeCompare(b.eid)
      );

    return { tenants: byEid.size, accounts: accounts.size, alertConfigs, topTenants };
  }

  /** Build a lookup of EIDs that have >=1 monitor, keyed by normalized id. */
  function buildMonitoringIndex(rows) {
    const byEid = new Map();
    for (const row of rows || []) {
      if (!row) continue;
      const count = Number(row.totalMonitorsEnabled) || 0;
      if (count < 1) continue;
      const key = normalizeEid(row.eid);
      if (!key) continue;
      const existing = byEid.get(key);
      if (existing) {
        existing.total += count;
        if (row.region) existing.regions.add(row.region);
      } else {
        byEid.set(key, {
          total: count,
          regions: new Set(row.region ? [row.region] : []),
          customerName: row.customerName || '',
        });
      }
    }
    return { byEid };
  }

  function groupByAccount(contracts) {
    const map = new Map();
    for (const c of contracts || []) {
      if (!c) continue;
      const name = (c.accountName || '').trim() || '(Unknown Account)';
      if (!map.has(name)) map.set(name, []);
      map.get(name).push(c);
    }
    return map;
  }

  /** Cross-reference contracts + UTDP rows into dashboard data. */
  function buildDashboard(contracts, utdpRows) {
    const monitoring = buildMonitoringIndex(utdpRows);
    const byAccount = groupByAccount(contracts);
    const accounts = [];

    for (const [accountName, accountContracts] of byAccount) {
      const signature = isSignatureAccount(accountContracts);

      const eidMap = new Map();
      for (const c of accountContracts) {
        // Contract side: reject any tenant id containing letters.
        const key = normalizeContractTenant(c.tenantId);
        if (!key) continue;
        if (!eidMap.has(key)) {
          const info = monitoring.byEid.get(key);
          eidMap.set(key, {
            eid: c.tenantId,
            normalized: key,
            hasProM: Boolean(info),
            regions: info ? Array.from(info.regions) : [],
            monitors: info ? info.total : 0,
          });
        }
      }

      const eids = Array.from(eidMap.values());
      const hasProM = eids.some((e) => e.hasProM);
      const serviceProviders = Array.from(
        new Set(
          accountContracts.map((c) => (c.serviceProvider || '').trim()).filter(Boolean)
        )
      );

      accounts.push({
        accountName,
        serviceProviders,
        isSignature: signature,
        contractCount: accountContracts.length,
        signatureContractCount: accountContracts.filter((c) =>
          isSignatureContract(c.contractName)
        ).length,
        eids,
        eidCount: eids.length,
        hasProM,
        leveraged: signature && hasProM,
        // Why is a non-signature account (possibly) leveraging ProM? null for
        // signature accounts.
        reason: signature ? null : signatureReason(accountContracts),
      });
    }

    accounts.sort((a, b) => {
      if (a.isSignature !== b.isSignature) return a.isSignature ? -1 : 1;
      if (a.isSignature && a.leveraged !== b.leveraged) return a.leveraged ? 1 : -1;
      return a.accountName.localeCompare(b.accountName);
    });

    const signatureAccounts = accounts.filter((a) => a.isSignature);
    const leveraged = signatureAccounts.filter((a) => a.leveraged);
    const notLeveraged = signatureAccounts.filter((a) => !a.leveraged);

    const regionCounts = { NA: 0, EU: 0, both: 0 };
    for (const a of leveraged) {
      const regions = new Set();
      a.eids.forEach((e) => e.hasProM && e.regions.forEach((r) => regions.add(r)));
      if (regions.has('NA')) regionCounts.NA += 1;
      if (regions.has('EU')) regionCounts.EU += 1;
      if (regions.has('NA') && regions.has('EU')) regionCounts.both += 1;
    }

    // Which EIDs belong to a signature account? (only valid numeric contract
    // tenants made it into a.eids) Also map every EID -> owning account.
    const signatureEids = new Set();
    const eidToAccount = new Map();
    for (const a of accounts) {
      for (const e of a.eids) {
        const prev = eidToAccount.get(e.normalized);
        if (!prev || (a.isSignature && !prev.isSignature)) {
          eidToAccount.set(e.normalized, {
            accountName: a.accountName,
            isSignature: a.isSignature,
          });
        }
        if (a.isSignature) signatureEids.add(e.normalized);
      }
    }

    // Non-signature ProM: monitored EIDs (job enabled, >=1) NOT associated with
    // any signature plan. Includes EIDs only present in UTDP (no contract match).
    const reasonByAccount = new Map(accounts.map((a) => [a.accountName, a.reason]));
    const NO_SIG = { code: 'none', label: 'No signature contract', date: '' };
    const nonSignatureProM = [];
    for (const [key, info] of monitoring.byEid) {
      if (signatureEids.has(key)) continue;
      const acct = eidToAccount.get(key);
      const reason = acct ? reasonByAccount.get(acct.accountName) || NO_SIG : NO_SIG;
      nonSignatureProM.push({
        eid: key,
        accountName: acct ? acct.accountName : '',
        customerName: info.customerName || (acct ? acct.accountName : ''),
        inContracts: Boolean(acct),
        monitors: info.total,
        regions: Array.from(info.regions),
        reason,
      });
    }
    nonSignatureProM.sort(
      (a, b) => b.monitors - a.monitors || a.eid.localeCompare(b.eid)
    );

    const totalSignature = signatureAccounts.length;
    const summary = {
      totalAccounts: accounts.length,
      totalSignatureAccounts: totalSignature,
      totalNonSignatureAccounts: accounts.length - totalSignature,
      leveragedCount: leveraged.length,
      notLeveragedCount: notLeveraged.length,
      leveragePercent: totalSignature
        ? Math.round((leveraged.length / totalSignature) * 1000) / 10
        : 0,
      monitoredEidCount: monitoring.byEid.size,
      leveragedByRegion: regionCounts,
      nonSignatureProMEidCount: nonSignatureProM.length,
      nonSignatureProMAccountCount: accounts.filter(
        (a) => !a.isSignature && a.hasProM
      ).length,
    };

    return { summary, accounts, nonSignatureProM };
  }

  return {
    normalizeEid,
    normalizeContractTenant,
    isSignatureContract,
    isSignatureAccount,
    buildMonitoringIndex,
    groupByAccount,
    buildDashboard,
    summarizeMonth,
  };
});
