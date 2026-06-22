import { useState } from 'react';

function SignatureLeverageTable({ accounts }) {
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

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

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Signature Leverage by Account</h2>

      {/* Search Bar */}
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search account name, provider, EID..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-4 flex-wrap">
        <button
          onClick={() => setFilter('signature')}
          className={`px-4 py-2 rounded-md font-medium transition-colors ${
            filter === 'signature'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Signature Accounts
        </button>
        <button
          onClick={() => setFilter('not-leveraged')}
          className={`px-4 py-2 rounded-md font-medium transition-colors ${
            filter === 'not-leveraged'
              ? 'bg-yellow-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Not Leveraged
        </button>
        <button
          onClick={() => setFilter('leveraged')}
          className={`px-4 py-2 rounded-md font-medium transition-colors ${
            filter === 'leveraged'
              ? 'bg-green-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Leveraged Only
        </button>
        <button
          onClick={() => setFilter('non-sig')}
          className={`px-4 py-2 rounded-md font-medium transition-colors ${
            filter === 'non-sig'
              ? 'bg-indigo-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Non-Sig with ProM
        </button>
        <button
          onClick={() => setFilter('all')}
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
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Account
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Service Provider
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Signature
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                EIDs (ProM)
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Operational Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Reason
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredAccounts.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                  No accounts found
                </td>
              </tr>
            ) : (
              filteredAccounts.map((account, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {account.accountName || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {account.serviceProvider || 'Marketing Cloud'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
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
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {(account.eids && account.eids.length > 0) ? (
                      <div className="flex flex-wrap gap-2">
                        {account.eids.map((eid, i) => (
                          <span key={i} className="flex items-center gap-1">
                            <span className="text-green-500 font-bold">●</span>
                            <span className="text-gray-700">{eid}</span>
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
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
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {account.reason || '-'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-4 text-sm text-gray-500">
        Showing {filteredAccounts.length} of {accounts.length} accounts
      </div>
    </div>
  );
}

export default SignatureLeverageTable;
