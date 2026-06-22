import { useEffect } from 'react';
import StatCard from './components/StatCard';
import AdoptionChart from './components/AdoptionChart';
import RegionalBreakdown from './components/RegionalBreakdown';
import TopTenantsTable from './components/TopTenantsTable';
import LeverageTable from './components/LeverageTable';
import { useMCEData } from './hooks/useMCEData';

// Load extension utilities globally
if (typeof window !== 'undefined') {
  // These will be loaded from the extension files
  import('./utils/config.js').catch(() => {});
  import('./utils/sf-orgs.js').catch(() => {});
  import('./utils/core.js').catch(() => {});
}

function App() {
  const {
    data,
    loading,
    error,
    isExtensionMode,
    contractCount,
    lastUpdated,
    refreshData
  } = useMCEData();

  useEffect(() => {
    // Auto-fetch on mount if in extension mode
    if (isExtensionMode) {
      refreshData();
    }
  }, [isExtensionMode, refreshData]);

  if (!data) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading MCE data...</p>
        </div>
      </div>
    );
  }

  const stats = data.stats || {};
  const topTenants = data.topTenants || [];
  const regional = data.regional || [];
  const growth = data.growth || [];
  const leveraged = data.leveraged || [];
  const notLeveraged = data.notLeveraged || [];
  const nonSignature = data.nonSignature || [];
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="shadow-sm" style={{ background: '#0176D3' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-white">
                Proactive Monitoring Dashboard
              </h1>
              <p className="text-sm text-white opacity-90 mt-1">
                Real-time adoption metrics and service health
              </p>
              <p className="text-xs text-white opacity-75 mt-1">
                {isExtensionMode ? (
                  <>Org62: {contractCount.toLocaleString()} contracts. UTDP latest: {lastUpdated.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}</>
                ) : (
                  'Offline mode - using static data'
                )}
              </p>
            </div>
            <div className="text-right space-y-2">
              <p className="text-sm text-white opacity-80">Last updated</p>
              <p className="text-sm font-medium text-white">
                {lastUpdated.toLocaleString()}
              </p>
              {isExtensionMode && (
                <button
                  onClick={refreshData}
                  disabled={loading}
                  className="px-4 py-2 bg-white text-blue-600 rounded-md font-medium hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? 'Loading...' : 'Refresh data'}
                </button>
              )}
              {!isExtensionMode && (
                <button
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md font-medium cursor-default"
                  disabled
                >
                  Load demo (offline)
                </button>
              )}
            </div>
          </div>
          {error && (
            <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              <strong>Error:</strong> {error}
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* Summary Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <StatCard
            title="ProM Enabled MCE Tenants"
            value={(stats.promEnabledTenants || 0).toLocaleString()}
            subtitle="Active tenant IDs"
            icon="🔍"
          />
          <StatCard
            title="MCE Accounts"
            value={(stats.totalAccounts || 0).toLocaleString()}
            subtitle="Unique accounts with MCE ProM"
            icon="🏢"
          />
          <StatCard
            title="Total Alert Configurations"
            value={(stats.totalMonitors || 0).toLocaleString()}
            subtitle="Monitors enabled (latest month)"
            icon="🔔"
          />
        </div>


        {/* Growth Chart */}
        {growth.length > 0 && (
          <div className="mb-8">
            <AdoptionChart data={growth} />
          </div>
        )}

        {/* Top MCE Tenants Table */}
        <div className="mb-8">
          <TopTenantsTable tenants={topTenants} />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            MCE ProM Dashboard © 2026 | Data source: UTDP Exports + Org62 Service Contracts
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
