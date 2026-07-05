import { useState } from 'react'
import { Download, BarChart2, Clock, Activity, Zap } from 'lucide-react'
import { useDashboardStats, useIncidentTrend } from '@/hooks/useDashboard'
import { useQuery } from '@tanstack/react-query'
import { analyticsService } from '@/services/analytics.service'
import { PageHeader } from '@/components/common/PageHeader'
import { StatsCard } from '@/components/ui/StatsCard'
import { IncidentTrendChart } from '@/components/charts/IncidentTrendChart'
import { SeverityDonutChart } from '@/components/charts/SeverityDonutChart'
import { IncidentTypeBarChart } from '@/components/charts/IncidentTypeBarChart'
import { ResponseTimeChart } from '@/components/charts/ResponseTimeChart'
import { SkeletonCard } from '@/components/ui/LoadingSpinner'

type Period = 'today' | 'week' | 'month'

export default function AnalyticsPage() {
  const [period, setPeriod] = useState<Period>('week')

  const { data: stats } = useDashboardStats({ period })
  const { data: trend } = useIncidentTrend(period === 'today' ? 1 : period === 'week' ? 7 : 30)
  const { data: summary } = useQuery({
    queryKey: ['analytics-summary', period],
    queryFn: () => analyticsService.getAnalyticsSummary({}),
  })
  const { data: responseTime } = useQuery({
    queryKey: ['response-time'],
    queryFn: () => analyticsService.getResponseTime(),
  })
  const { data: utilization } = useQuery({
    queryKey: ['resource-util'],
    queryFn: () => analyticsService.getResourceUtilization(),
  })

  const summaryData = summary?.data
  const rtData = responseTime?.data

  return (
    <div>
      <PageHeader
        title="Analytics"
        subtitle="Platform-wide incident and response metrics"
        breadcrumbs={[{ label: 'Dashboard', href: '/authority' }, { label: 'Analytics' }]}
        action={
          <div className="flex items-center gap-3">
            {/* Period selector */}
            <div className="flex rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 overflow-hidden">
              {(['today','week','month'] as Period[]).map(p => (
                <button key={p} onClick={() => setPeriod(p)}
                  className={`px-4 py-2 text-sm font-medium capitalize transition-colors ${
                    period === p ? 'bg-blue-600 text-white' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}>
                  {p === 'today' ? 'Today' : p === 'week' ? '7 Days' : '30 Days'}
                </button>
              ))}
            </div>
            <button className="flex items-center gap-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              <Download className="h-4 w-4" /> Export
            </button>
          </div>
        }
      />

      {/* KPI row */}
      <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-5">
        <StatsCard title="Total Incidents" value={summaryData?.total ?? 0} icon={Activity} />
        <StatsCard title="Critical" value={summaryData?.bySeverity?.CRITICAL ?? 0} icon={BarChart2} variant="critical" />
        <StatsCard title="Avg Response" value={`${stats?.avgResponseTimeMinutes ?? 0}m`} icon={Clock} />
        <StatsCard title="AI Accuracy" value={`${Math.round((summaryData?.aiAccuracyRate ?? 0) * 100)}%`} icon={Zap} variant="success" />
        <StatsCard title="Resolved" value={summaryData?.bySeverity ? Object.values(summaryData.bySeverity).reduce((a,b)=>a+b,0) : 0} icon={Activity} />
      </div>

      {/* Charts 2x2 */}
      <div className="grid gap-6 lg:grid-cols-2 mb-6">
        <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">
            Incident Trend ({period === 'today' ? 'Today' : period === 'week' ? '7 Days' : '30 Days'})
          </h3>
          <IncidentTrendChart data={trend} />
        </div>

        <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">Severity Distribution</h3>
          <SeverityDonutChart data={summaryData?.bySeverity as any} />
        </div>

        <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">Incidents by Type</h3>
          <IncidentTypeBarChart data={summaryData?.byType as unknown as Record<string, number>} />
        </div>

        <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">Response Time Trend</h3>
          <ResponseTimeChart
            data={trend ? { labels: trend.labels, values: trend.datasets.total.map(() => stats?.avgResponseTimeMinutes || 0) } : undefined}
          />
        </div>
      </div>

      {/* Response time by type table */}
      {rtData?.byType && (
        <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100 dark:border-gray-700">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Response Time by Incident Type</h3>
          </div>
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th className="text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase px-5 py-3">Type</th>
                <th className="text-right text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase px-5 py-3">Avg (min)</th>
                <th className="text-right text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase px-5 py-3">Count</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {Object.entries(rtData.byType).map(([type, val]: any) => (
                <tr key={type} className="hover:bg-gray-50 dark:hover:bg-gray-700/30">
                  <td className="px-5 py-3 text-sm text-gray-900 dark:text-white font-medium">{type}</td>
                  <td className="px-5 py-3 text-sm text-gray-600 dark:text-gray-400 text-right">{val.avg} min</td>
                  <td className="px-5 py-3 text-sm text-gray-600 dark:text-gray-400 text-right">{val.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
