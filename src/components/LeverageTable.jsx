export default function LeverageTable({ title, subtitle, accounts, type }) {
  const colorScheme = {
    leveraged: { bg: 'bg-green-50', border: 'border-green-500', text: 'text-green-700' },
    notLeveraged: { bg: 'bg-yellow-50', border: 'border-yellow-500', text: 'text-yellow-700' },
    nonSignature: { bg: 'bg-blue-50', border: 'border-blue-500', text: 'text-blue-700' }
  };

  const colors = colorScheme[type] || colorScheme.nonSignature;

  return (
    <div className={`${colors.bg} shadow rounded-lg overflow-hidden border-l-4 ${colors.border}`}>
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className={`text-xl font-semibold ${colors.text}`}>{title}</h2>
        <p className="text-sm text-gray-600 mt-1">{subtitle}</p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-white bg-opacity-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Account Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tenant IDs</th>
              {type !== 'notLeveraged' && (
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Monitors</th>
              )}
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {type === 'notLeveraged' ? 'Reason' : 'Status'}
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {accounts.length === 0 ? (
              <tr>
                <td colSpan="4" className="px-6 py-8 text-center text-sm text-gray-500">
                  No accounts in this category
                </td>
              </tr>
            ) : (
              accounts.slice(0, 10).map((account, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {account.accountName.replace(/_/g, ' ')}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 font-mono">
                    {account.tenantIds.join(', ')}
                  </td>
                  {type !== 'notLeveraged' && (
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-blue-600">
                      {account.monitors}
                    </td>
                  )}
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      type === 'leveraged' ? 'bg-green-100 text-green-800' :
                      type === 'notLeveraged' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {account.reason || 'Active'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
        {accounts.length > 10 && (
          <div className="px-6 py-3 bg-gray-50 text-center text-sm text-gray-500">
            ... and {accounts.length - 10} more accounts
          </div>
        )}
      </div>
    </div>
  );
}
