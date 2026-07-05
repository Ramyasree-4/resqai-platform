import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface Props { data?: { LOW: number; MEDIUM: number; HIGH: number; CRITICAL: number }; height?: number }

const COLORS = { CRITICAL: '#DC2626', HIGH: '#EA580C', MEDIUM: '#D97706', LOW: '#16A34A' }
const LABELS = { CRITICAL: 'Critical', HIGH: 'High', MEDIUM: 'Medium', LOW: 'Low' }

export function SeverityDonutChart({ data, height = 260 }: Props) {
  if (!data) return null

  const chartData = Object.entries(data)
    .filter(([, v]) => v > 0)
    .map(([key, value]) => ({ name: LABELS[key as keyof typeof LABELS] || key, value, key }))

  const total = chartData.reduce((s, d) => s + d.value, 0)

  return (
    <div className="relative">
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={65}
            outerRadius={95}
            paddingAngle={3}
            dataKey="value"
          >
            {chartData.map((entry) => (
              <Cell key={entry.key} fill={COLORS[entry.key as keyof typeof COLORS] || '#9CA3AF'} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ borderRadius: 8, border: '1px solid #e5e7eb', fontSize: 12 }}
            formatter={(value: number) => [`${value} (${total ? Math.round((value / total) * 100) : 0}%)`, '']}
          />
          <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 12 }} />
        </PieChart>
      </ResponsiveContainer>
      {total > 0 && (
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none" style={{ top: -8 }}>
          <span className="text-2xl font-bold text-gray-900 dark:text-white">{total}</span>
          <span className="text-xs text-gray-500">Active</span>
        </div>
      )}
    </div>
  )
}
