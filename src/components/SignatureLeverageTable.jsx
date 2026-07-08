import { useState } from 'react';

function toCsvValue(value) {
  const str = value === null || value === undefined ? '' : String(value);
  if (/[",\n]/.test(str)) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

function exportAccountsToCsv(accounts, filename) {
  const headers = ['Account', 'Service Provider', 'Signature', 'EIDs (ProM)', 'Operational Status', 'Reason'];
  const rows = accounts.map((account) => [
    account.accountName || '',
    account.serviceProvider || 'Marketing Cloud',
    account.isSignature ? 'Yes' : 'No',
    (account.eids || []).join('; '),
    account.isLeveraged ? 'Leveraged' : 'Not leveraged',
    account.reason || '',
  ]);

  const csvContent = [headers, ...rows]
    .map((row) => row.map(toCsvValue).join(','))
    .join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function SignatureLeverageTable({ accounts }) {
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Filter accounts based on selected filter
  let filteredAccounts = accounts || [];

  switch (filter) {
    case 'signature':
      filteredAccounts = filteredAccounts.filter(acc => acc.isSignature && !acc.isLeveraged);
      break;
    case 'not-leveraged':
      filteredAccounts = filteredAccounts.filter(acc => acc.isSignature && !acc.isLeveraged);
      break;
    case 'leveraged':
      filteredAccounts = filteredAccounts.filter(acc => acc.isLeveraged);
      break;
    case 'non-sig':
      filteredAccounts = filteredAccounts.filter(acc => !acc.isSignature && acc.hasMonitoring);
      break;
    case 'all':
    default:
      // Show all accounts
      break;
  }

  // Apply search filter
  if (searchTerm) {
    const lowerSearch = searchTerm.toLowerCase();
    filteredAccounts = filteredAccounts.filter(acc =>
      (acc.accountName || '').toLowerCase().includes(lowerSearch) ||
      (acc.serviceProvider || '').toLowerCase().includes(lowerSearch) ||
      (acc.eids || []).some(eid => String(eid).includes(searchTerm))
    );
  }

  // Pagination
  const totalPages = Math.ceil(filteredAccounts.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedAccounts = filteredAccounts.slice(startIndex, endIndex);

  // Reset to page 1 when filter or search changes
  const handleFilterChange = (newFilter) => {
    setFilter(newFilter);
    setCurrentPage(1);
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  const handleExport = () => {
    const date = new Date().toISOString().slice(0, 10);
    exportAccountsToCsv(filteredAccounts, `mce-signature-leverage-${filter}-${date}.csv`);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
        <h2 className="text-xl font-semibold">Signature Leverage by Account</h2>
        <button
          onClick={handleExport}
          disabled={filteredAccounts.length === 0}
          className="flex items-center gap-2 px-4 py-2 rounded-md font-medium text-sm bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          ⬇ Export CSV
        </button>
      </div>

      {/* Search Bar */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search account name, provider, EID..."
          value={searchTerm}
          onChange={handleSearchChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-4 flex-wrap">
        <button
          onClick={() => handleFilterChange('signature')}
          className={`px-4 py-2 rounded-md font-medium transition-colors ${
            filter === 'signature'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Signature Accounts
        </button>
        <button
          onClick={() => handleFilterChange('not-leveraged')}
          className={`px-4 py-2 rounded-md font-medium transition-colors ${
            filter === 'not-leveraged'
              ? 'bg-yellow-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Not Leveraged
        </button>
        <button
          onClick={() => handleFilterChange('leveraged')}
          className={`px-4 py-2 rounded-md font-medium transition-colors ${
            filter === 'leveraged'
              ? 'bg-green-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Leveraged Only
        </button>
        <button
          onClick={() => handleFilterChange('non-sig')}
          className={`px-4 py-2 rounded-md font-medium transition-colors ${
            filter === 'non-sig'
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Non-Sig with ProM
        </button>
        <button
          onClick={() => handleFilterChange('all')}
          className={`px-4 py-2 rounded-md font-medium transition-colors ${
            filter === 'all'
              ? 'bg-gray-700 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          All Accounts
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/6">
                Account
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/8">
                Service Provider
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-20">
                Signature
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/5">
                EIDs (ProM)
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-32">
                Operational Status
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-40">
                Reason
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {paginatedAccounts.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-4 py-4 text-center text-gray-500">
                  No accounts found
                </td>
              </tr>
            ) : (
              paginatedAccounts.map((account, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">
                    {account.accountName || '-'}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                    {account.serviceProvider || 'Marketing Cloud'}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm">
                    {account.isSignature ? (
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        Yes
                      </span>
                    ) : (
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                        No
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {(account.eids && account.eids.length > 0) ? (
                      <div className="flex flex-wrap gap-1">
                        {account.eids.map((eid, i) => (
                          <span key={i} className="text-gray-700">
                            {eid}{i < account.eids.length - 1 ? ',' : ''}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-sm">
                    {account.isLeveraged ? (
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                        Leveraged
                      </span>
                    ) : (
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                        Not leveraged
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500 whitespace-nowrap">
                    {account.reason || '-'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      <div className="mt-4 flex items-center justify-between">
        <div className="text-sm text-gray-500">
          Showing {startIndex + 1}-{Math.min(endIndex, filteredAccounts.length)} of {filteredAccounts.length} accounts
        </div>

        {totalPages > 1 && (
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>

            <div className="px-3 py-1 text-sm font-medium text-gray-700">
              Page {currentPage} of {totalPages}
            </div>

            <button
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default SignatureLeverageTable;
