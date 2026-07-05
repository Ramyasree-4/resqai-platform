import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer } from 'recharts'

interface Props { data?: { labels: string[]; values: number[] }; slaMinutes?: number; height?: number }

export function ResponseTimeChart({ data, slaMinutes = 60, height = 260 }: Props) {
  if (!data) return null

  const chartData = data.labels.map((label, i) => ({ date: label, minutes: data.values[i] ?? 0 }))

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={chartData} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
        <YAxis tick={{ fontSize: 11 }} tickLine={false} axisLine={false} unit="m" />
        <Tooltip
          contentStyle={{ borderRadius: 8, border: '1px solid #e5e7eb', fontSize: 12 }}
          formatter={(v: number) => [`${v} min`, 'Avg Response Time']}
        />
        <ReferenceLine y={slaMinutes} stroke="#EF4444" strokeDasharray="4 4" label={{ value: 'SLA', fontSize: 11, fill: '#EF4444' }} />
        <Line type="monotone" dataKey="minutes" name="Avg Response" stroke="#3B82F6" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 5 }} />
      </LineChart>
    </ResponsiveContainer>
  )
}
