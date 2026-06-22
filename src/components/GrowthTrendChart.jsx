import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function GrowthTrendChart({ data }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">MCE Tenant Growth Trend</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="signatureAccounts"
            stroke="#4A90E2"
            name="Signature Accounts"
            strokeWidth={2}
          />
          <Line
            type="monotone"
            dataKey="accountsLeveragingProm"
            stroke="#7CB342"
            name="Accounts Leveraging ProM"
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default GrowthTrendChart;
