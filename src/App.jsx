import { useEffect } from 'react';
import StatCard from './components/StatCard';
import GrowthTrendChart from './components/GrowthTrendChart';
import SignatureLeverageTable from './components/SignatureLeverageTable';
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
  const growth = data.growth || [];
  const leverageAccounts = data.leverageAccounts || [];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="shadow-sm" style={{ background: '#4A90E2' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-white">
              MCE Proactive Monitoring Dashboard
            </h1>
            <div className="text-right">
              <p className="text-xs text-white opacity-80">Last updated</p>
              <p className="text-sm font-medium text-white">
                {lastUpdated.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric' })}, {lastUpdated.toLocaleTimeString('en-GB')}
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* 8 Metric Cards - 4 cols + 4 cols */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <StatCard
            title="Signature Accounts"
            value={(stats.totalSignatureAccounts || 0).toLocaleString()}
            subtitle="Total signature contract accounts"
            icon="📋"
          />
          <StatCard
            title="ProM Leveraged Accounts"
            value={(stats.signatureWithProm || 0).toLocaleString()}
            subtitle="Signature accounts leveraging ProM"
            icon="✅"
          />
          <StatCard
            title="ProM Not Leveraged Accounts"
            value={(stats.signatureNotLeveraged || 0).toLocaleString()}
            subtitle="Signature accounts without ProM"
            icon="⚠️"
          />
          <StatCard
            title="Non-SIG ProM Leveraged"
            value={(stats.nonSignatureWithProm || 0).toLocaleString()}
            subtitle="Non-signature accounts using ProM"
            icon="ℹ️"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Signature Tenants"
            value={(stats.totalSignatureTenants || 0).toLocaleString()}
            subtitle="Total MCE signature tenants"
            icon="🏢"
          />
          <StatCard
            title="ProM Leveraged Tenants"
            value={(stats.signatureTenantsLeveraged || 0).toLocaleString()}
            subtitle="Signature tenants with ProM monitoring"
            icon="🔍"
          />
          <StatCard
            title="ProM Not Leveraged Tenants"
            value={(stats.signatureTenantsNotLeveraged || 0).toLocaleString()}
            subtitle="Signature tenants without ProM monitoring"
            icon="🚫"
          />
          <StatCard
            title="Total Configured Alerts"
            value={(stats.totalAlerts || 0).toLocaleString()}
            subtitle="Total monitors configured"
            icon="🔔"
          />
        </div>

        {/* Growth Trend Chart */}
        {growth.length > 0 && (
          <div className="mb-8">
            <GrowthTrendChart data={growth} />
          </div>
        )}

        {/* Signature Leverage by Account Table */}
        <div className="mb-8">
          <SignatureLeverageTable accounts={leverageAccounts} />
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
