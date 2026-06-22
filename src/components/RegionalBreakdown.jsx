import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function RegionalBreakdown({ data }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">Regional Distribution</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="region" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="tenants" fill="#0176D3" name="Tenants" />
          <Bar dataKey="monitors" fill="#06A59A" name="Monitors" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
