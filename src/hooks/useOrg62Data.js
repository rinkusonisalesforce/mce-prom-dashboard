import { useState, useEffect, useCallback } from 'react';

/**
 * Hook to fetch live data from Org62 (Chrome extension mode)
 * Falls back to static data if not in extension context
 */
export function useOrg62Data() {
  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isExtensionMode, setIsExtensionMode] = useState(false);
  const [contractCount, setContractCount] = useState(0);

  // Check if we're running as Chrome extension
  useEffect(() => {
    const inExtension = typeof chrome !== 'undefined' &&
                       typeof chrome.cookies !== 'undefined';
    setIsExtensionMode(inExtension);
  }, []);

  const fetchLiveData = useCallback(async () => {
    if (!isExtensionMode) {
      setError('Not running in Chrome extension mode');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Import the Org62 connector (loaded from extension files)
      if (typeof window.connectOrg === 'undefined') {
        throw new Error('Org62 connector not loaded. Make sure config.js and sf-orgs.js are loaded.');
      }

      // Connect to Org62 using session cookie
      const connection = await window.connectOrg('org62');

      // Fetch contracts using the SOQL from config.js
      const result = await window.fetchServiceContracts(connection);

      setContracts(result);
      setContractCount(result.length);
      console.log(`[Org62] Fetched ${result.length} contracts`);

    } catch (err) {
      console.error('[Org62] Fetch failed:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [isExtensionMode]);

  return {
    contracts,
    contractCount,
    loading,
    error,
    isExtensionMode,
    refreshData: fetchLiveData,
  };
}
