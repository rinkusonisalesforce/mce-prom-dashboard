import { useMemo, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const RANGE_OPTIONS = [
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'quarterly', label: 'Quarterly' },
  { value: 'yearly', label: 'Yearly' },
];

function parseDate(point) {
  if (point.date) {
    const d = new Date(point.date);
    if (!isNaN(d.getTime())) return d;
  }
  // Fall back to parsing the display label (e.g. "Jun 29, 2026")
  const d = new Date(point.month);
  return isNaN(d.getTime()) ? null : d;
}

function getWeekKey(d) {
  // ISO-ish week key: year + week number (Monday-start weeks)
  const date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  const dayNum = (date.getUTCDay() + 6) % 7; // 0 = Monday
  date.setUTCDate(date.getUTCDate() - dayNum + 3);
  const firstThursday = new Date(Date.UTC(date.getUTCFullYear(), 0, 4));
  const week = 1 + Math.round(((date - firstThursday) / 86400000 - 3 + ((firstThursday.getUTCDay() + 6) % 7)) / 7);
  return `${date.getUTCFullYear()}-W${String(week).padStart(2, '0')}`;
}

function getBucketKey(d, range) {
  const year = d.getFullYear();
  switch (range) {
    case 'weekly':
      return getWeekKey(d);
    case 'quarterly':
      return `${year}-Q${Math.floor(d.getMonth() / 3) + 1}`;
    case 'yearly':
      return `${year}`;
    case 'monthly':
    default:
      return `${year}-${String(d.getMonth() + 1).padStart(2, '0')}`;
  }
}

function getBucketLabel(d, range) {
  const year = d.getFullYear();
  switch (range) {
    case 'weekly':
      return `Wk ${getWeekKey(d).split('-W')[1]} '${String(year).slice(-2)}`;
    case 'quarterly':
      return `Q${Math.floor(d.getMonth() / 3) + 1} ${year}`;
    case 'yearly':
      return `${year}`;
    case 'monthly':
    default:
      return d.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
  }
}

/**
 * Aggregate raw growth points into weekly/monthly/quarterly/yearly buckets.
 * Each bucket takes the LAST data point within that bucket (most recent
 * snapshot in the period), since these are cumulative counts, not sums.
 */
function aggregate(data, range) {
  if (!data || data.length === 0) return [];

  const withDates = data
    .map((point) => ({ point, date: parseDate(point) }))
    .filter((p) => p.date !== null)
    .sort((a, b) => a.date - b.date);

  if (withDates.length === 0) return data; // no parseable dates, show as-is

  const buckets = new Map();
  for (const { point, date } of withDates) {
    const key = getBucketKey(date, range);
    buckets.set(key, {
      key,
      label: getBucketLabel(date, range),
      date,
      signatureAccounts: point.signatureAccounts,
      accountsLeveragingProm: point.accountsLeveragingProm,
    });
  }

  return Array.from(buckets.values())
    .sort((a, b) => a.date - b.date)
    .map((b) => ({
      month: b.label,
      signatureAccounts: b.signatureAccounts,
      accountsLeveragingProm: b.accountsLeveragingProm,
    }));
}

function GrowthTrendChart({ data }) {
  const [range, setRange] = useState('monthly');

  const chartData = useMemo(() => aggregate(data, range), [data, range]);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
        <h2 className="text-xl font-semibold">MCE Tenant Growth Trend</h2>
        <div className="flex items-center gap-2">
          <label htmlFor="trend-range" className="text-sm text-gray-500">
            View by
          </label>
          <select
            id="trend-range"
            value={range}
            onChange={(e) => setRange(e.target.value)}
            className="text-sm border border-gray-300 rounded-md px-3 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {RANGE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
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
