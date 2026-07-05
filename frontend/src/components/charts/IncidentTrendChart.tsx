import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import type { IncidentTrendData } from '@/types'

interface Props { data?: IncidentTrendData; height?: number }

export function IncidentTrendChart({ data, height = 260 }: Props) {
  if (!data) {
    return <div className="flex items-center justify-center" style={{ height }}><p className="text-sm text-gray-400">Loading chart…</p></div>
  }

  const chartData = data.labels.map((label, i) => ({
    date: label,
    total: data.datasets.total[i] ?? 0,
    critical: data.datasets.critical[i] ?? 0,
    resolved: data.datasets.resolved[i] ?? 0,
  }))

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={chartData} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
        <defs>
          <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="colorCritical" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#EF4444" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="colorResolved" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#22C55E" stopOpacity={0.2} />
            <stop offset="95%" stopColor="#22C55E" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
        <Tooltip
          contentStyle={{ borderRadius: 8, border: '1px solid #e5e7eb', fontSize: 12 }}
          cursor={{ stroke: '#e5e7eb' }}
        />
        <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 12 }} />
        <Area type="monotone" dataKey="total" name="Total" stroke="#3B82F6" strokeWidth={2} fill="url(#colorTotal)" />
        <Area type="monotone" dataKey="critical" name="Critical" stroke="#EF4444" strokeWidth={2} fill="url(#colorCritical)" />
        <Area type="monotone" dataKey="resolved" name="Resolved" stroke="#22C55E" strokeWidth={2} fill="url(#colorResolved)" />
      </AreaChart>
    </ResponsiveContainer>
  )
}
