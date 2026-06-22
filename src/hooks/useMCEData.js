import { useState, useEffect } from 'react';
import { useOrg62Data } from './useOrg62Data';

// Import static data as fallback
import {
  mceSummaryStats as staticStats,
  topMCETenants as staticTopTenants,
  mceRegionalBreakdown as staticRegional,
  mceMonthlyGrowth as staticGrowth,
  signatureLeveragedAccounts as staticLeveraged,
  signatureNotLeveragedAccounts as staticNotLeveraged,
  nonSignatureWithPromAccounts as staticNonSignature,
} from '../data/mceRealData';

/**
 * Master hook that combines live Org62 data with UTDP CSV data
 * Mimics the extension's data flow
 */
export function useMCEData() {
  const {
    contracts,
    contractCount,
    loading: org62Loading,
    error: org62Error,
    isExtensionMode,
    refreshData
  } = useOrg62Data();

  const [utdpData, setUtdpData] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  // Load UTDP data (from CSVs in extension mode, or static data in web mode)
  useEffect(() => {
    if (isExtensionMode) {
      // In extension mode: load CSVs from data/ folder
      loadUTDPFromExtension();
    } else {
      // In web mode: use static pre-generated data
      setUtdpData({
        stats: staticStats,
        topTenants: staticTopTenants,
        regional: staticRegional,
        growth: staticGrowth,
      });
    }
  }, [isExtensionMode]);

  // Cross-reference Org62 contracts with UTDP data
  useEffect(() => {
    if (!utdpData) return;

    if (contracts.length > 0 && window.ProM) {
      // Use the ProM core.js logic to cross-reference
      const leverageData = window.ProM.crossReference(utdpData, contracts);

      setDashboardData({
        ...utdpData,
        contracts: contracts,
        contractCount: contractCount,
        leveraged: leverageData.leveraged,
        notLeveraged: leverageData.notLeveraged,
        nonSignature: leverageData.nonSignature,
        leverageRate: leverageData.leverageRate,
      });
    } else {
      // No contracts yet, use static data
      setDashboardData({
        ...utdpData,
        contracts: [],
        contractCount: 0,
        leveraged: staticLeveraged,
        notLeveraged: staticNotLeveraged,
        nonSignature: staticNonSignature,
        leverageRate: staticStats.leverageRate,
      });
    }

    setLastUpdated(new Date());
  }, [utdpData, contracts, contractCount]);

  async function loadUTDPFromExtension() {
    try {
      // This would load CSVs from chrome.runtime.getURL('data/...')
      // For now, fall back to static data
      setUtdpData({
        stats: staticStats,
        topTenants: staticTopTenants,
        regional: staticRegional,
        growth: staticGrowth,
      });
    } catch (err) {
      console.error('[UTDP] Load failed:', err);
    }
  }

  return {
    data: dashboardData,
    loading: org62Loading,
    error: org62Error,
    isExtensionMode,
    contractCount,
    lastUpdated,
    refreshData,
  };
}
