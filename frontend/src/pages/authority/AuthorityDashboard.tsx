import { Link } from 'react-router-dom'
import { AlertTriangle, CheckCircle2, Clock, Zap, Activity, Users, MapPin } from 'lucide-react'
import { useDashboardStats, useMapData, useIncidentTrend } from '@/hooks/useDashboard'
import { usePriorityQueue } from '@/hooks/useIncidents'
import { StatsCard } from '@/components/ui/StatsCard'
import { IncidentCard } from '@/components/incident/IncidentCard'
import { IncidentTrendChart } from '@/components/charts/IncidentTrendChart'
import { SeverityDonutChart } from '@/components/charts/SeverityDonutChart'
import { ResQAIMap } from '@/components/map/ResQAIMap'
import { SkeletonCard } from '@/components/ui/LoadingSpinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { useAuth } from '@/hooks/useAuth'

export default function AuthorityDashboard() {
  const { user } = useAuth()
  const { data: stats, isLoading: statsLoading } = useDashboardStats()
  const { data: mapData } = useMapData()
  const { data: trend } = useIncidentTrend(7)
  const { data: queue, isLoading: queueLoading } = usePriorityQueue()

  const severityDist = mapData?.incidents.reduce((acc, inc) => {
    const band = inc.severityBand as string || 'LOW'
    acc[band] = (acc[band] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Operations Dashboard</h1>
          <p className="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
            {user?.district}, {user?.state} · {user?.role?.replace('_', ' ')}
          </p>
        </div>
        <div className="flex items-center gap-2 rounded-full bg-green-100 dark:bg-green-900/20 px-3 py-1.5 text-xs font-semibold text-green-700 dark:text-green-400">
          <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
          LIVE
        </div>
      </div>

      {/* KPI Cards */}
      {statsLoading ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          <StatsCard title="Active Incidents" value={stats?.activeIncidents ?? 0} icon={Activity}
            variant={stats?.activeIncidents && stats.activeIncidents > 20 ? 'critical' : 'default'} />
          <StatsCard title="Critical" value={stats?.criticalIncidents ?? 0} icon={AlertTriangle} variant="critical" />
          <StatsCard title="Pending" value={stats?.pendingAssignment ?? 0} icon={Clock}
            variant={stats?.pendingAssignment && stats.pendingAssignment > 0 ? 'warning' : 'default'} />
          <StatsCard title="Deployed" value={`${stats?.resourcesDeployed ?? 0}/${(stats?.resourcesDeployed ?? 0) + (stats?.resourcesAvailable ?? 0)}`} icon={Zap} variant="info" />
          <StatsCard title="Resolved Today" value={stats?.resolvedToday ?? 0} icon={CheckCircle2} variant="success" />
          <StatsCard title="Avg Response" value={`${stats?.avgResponseTimeMinutes ?? 0}m`} icon={Clock} subtitle="minutes" />
        </div>
      )}

      {/* Main grid: Queue + Map */}
      <div className="grid gap-6 lg:grid-cols-5">
        {/* Priority Queue */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-gray-900 dark:text-white">Priority Queue</h2>
            <Link to="/authority/incidents" className="text-sm text-blue-600 dark:text-blue-400 hover:underline">View all</Link>
          </div>
          {queueLoading ? (
            <div className="space-y-3">{Array.from({length:4}).map((_,i)=><SkeletonCard key={i}/>)}</div>
          ) : !queue || queue.length === 0 ? (
            <EmptyState icon={CheckCircle2} title="No active incidents" description="All clear in your jurisdiction." />
          ) : (
            <div className="space-y-3">
              {queue.slice(0, 5).map(inc => (
                <IncidentCard key={inc.incidentId} incident={inc}
                  href={`/authority/incidents/${inc._firestoreId || inc.incidentId}`}
                  compact />
              ))}
            </div>
          )}
        </div>

        {/* Map */}
        <div className="lg:col-span-3">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-gray-900 dark:text-white">Operations Map</h2>
            <Link to="/authority/map" className="text-sm text-blue-600 dark:text-blue-400 hover:underline">Full map</Link>
          </div>
          <ResQAIMap
            data={mapData}
            height="340px"
            onIncidentClick={id => window.location.href = `/authority/incidents/${id}`}
            className="rounded-xl border border-gray-200 dark:border-gray-700"
          />
        </div>
      </div>

      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">Incident Trend (7 days)</h3>
          <IncidentTrendChart data={trend} />
        </div>
        <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">Active Severity Distribution</h3>
          <SeverityDonutChart data={severityDist as any} />
        </div>
      </div>
    </div>
  )
}
