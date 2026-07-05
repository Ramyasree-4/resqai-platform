import { Users, Activity, Zap, Package, Settings, AlertTriangle } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { analyticsService } from '@/services/analytics.service'
import { PageHeader } from '@/components/common/PageHeader'
import { StatsCard } from '@/components/ui/StatsCard'
import { SkeletonCard } from '@/components/ui/LoadingSpinner'
import { Link } from 'react-router-dom'

export default function AdminDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-system-stats'],
    queryFn: () => analyticsService.getSystemStats(),
    refetchInterval: 60000,
  })

  const stats = data?.data

  const quickLinks = [
    { icon: Users, label: 'User Management', desc: 'Manage accounts and roles', href: '#', color: 'text-blue-600', bg: 'bg-blue-50 dark:bg-blue-900/20' },
    { icon: Package, label: 'Resource Registry', desc: 'Manage rescue resources', href: '/authority/resources', color: 'text-green-600', bg: 'bg-green-50 dark:bg-green-900/20' },
    { icon: Activity, label: 'Platform Analytics', desc: 'System-wide metrics', href: '/authority/analytics', color: 'text-purple-600', bg: 'bg-purple-50 dark:bg-purple-900/20' },
    { icon: Settings, label: 'System Settings', desc: 'Configure AI thresholds', href: '/settings', color: 'text-orange-600', bg: 'bg-orange-50 dark:bg-orange-900/20' },
  ]

  return (
    <div className="space-y-6">
      <PageHeader title="Admin Dashboard" subtitle="Platform health and management" />

      {/* System health banner */}
      <div className={`rounded-xl p-4 border ${stats?.systemHealth === 'HEALTHY'
        ? 'bg-green-50 dark:bg-green-900/10 border-green-200 dark:border-green-800'
        : 'bg-red-50 dark:bg-red-900/10 border-red-200 dark:border-red-800'
      }`}>
        <div className="flex items-center gap-3">
          <span className={`h-3 w-3 rounded-full ${stats?.systemHealth === 'HEALTHY' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
          <span className="text-sm font-semibold text-gray-900 dark:text-white">
            System Status: {stats?.systemHealth || 'Checking…'}
          </span>
          <span className="text-xs text-gray-500 dark:text-gray-400 ml-auto">Last checked just now</span>
        </div>
      </div>

      {/* Stats */}
      {isLoading ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">{Array.from({length:4}).map((_,i)=><SkeletonCard key={i}/>)}</div>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatsCard title="Total Users" value={stats?.totalUsers?.toLocaleString() || '0'} icon={Users} />
          <StatsCard title="Total Incidents" value={stats?.totalIncidents?.toLocaleString() || '0'} icon={AlertTriangle} variant="warning" />
          <StatsCard title="Total Resources" value={stats?.totalResources?.toLocaleString() || '0'} icon={Package} variant="success" />
          <StatsCard title="AI Calls Today" value={stats?.geminiApiUsage?.requestsToday?.toLocaleString() || '0'} icon={Zap} variant="info" subtitle={`$${stats?.geminiApiUsage?.costUSD?.toFixed(2) || '0.00'} cost`} />
        </div>
      )}

      {/* Quick links */}
      <div>
        <h2 className="text-base font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {quickLinks.map((link, i) => (
            <Link key={i} to={link.href}
              className="flex items-start gap-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 hover:shadow-md transition-shadow group">
              <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${link.bg}`}>
                <link.icon className={`h-5 w-5 ${link.color}`} />
              </div>
              <div>
                <p className="text-sm font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">{link.label}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{link.desc}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* AI Usage */}
      {stats?.geminiApiUsage && (
        <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 shadow-sm">
          <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Zap className="h-4 w-4 text-purple-500" /> Gemini AI Usage
          </h3>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">{stats.geminiApiUsage.requestsToday}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Requests Today</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">${stats.geminiApiUsage.costUSD?.toFixed(2)}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Cost Today</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">✓</p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Circuit Closed</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
