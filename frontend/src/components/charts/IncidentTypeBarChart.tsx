import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { INCIDENT_TYPE_LABELS } from '@/utils/constants'

interface Props { data?: Record<string, number> | { [key: string]: number }; height?: number }

const BAR_COLORS = ['#3B82F6','#EF4444','#F59E0B','#10B981','#8B5CF6','#F97316','#06B6D4','#EC4899','#84CC16','#6B7280']

export function IncidentTypeBarChart({ data, height = 260 }: Props) {
  if (!data) return null

  const chartData = Object.entries(data)
    .filter(([, v]) => v > 0)
    .sort(([, a], [, b]) => b - a)
    .map(([key, value], i) => ({
      type: INCIDENT_TYPE_LABELS[key as keyof typeof INCIDENT_TYPE_LABELS]?.label || key,
      value,
      color: BAR_COLORS[i % BAR_COLORS.length],
    }))

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={chartData} layout="vertical" margin={{ top: 0, right: 20, left: 10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f0f0f0" />
        <XAxis type="number" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
        <YAxis type="category" dataKey="type" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} width={80} />
        <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e5e7eb', fontSize: 12 }} />
        <Bar dataKey="value" name="Incidents" radius={[0, 4, 4, 0]}>
          {chartData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
