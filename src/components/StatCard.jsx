export default function StatCard({ title, value, subtitle, icon }) {
  return (
    <div className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg transition-shadow duration-200">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <span className="text-3xl">{icon}</span>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate uppercase tracking-wide">
                {title}
              </dt>
              <dd className="flex items-baseline">
                <div className="text-3xl font-bold text-blue-600">
                  {value}
                </div>
              </dd>
              {subtitle && (
                <dd className="mt-1 text-sm text-gray-500">
                  {subtitle}
                </dd>
              )}
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}
