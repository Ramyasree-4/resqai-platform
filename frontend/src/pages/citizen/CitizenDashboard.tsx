import { Link } from 'react-router-dom'
import { AlertTriangle, FileText, CheckCircle2, MapPin, Phone, Bell, Plus } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { useMyIncidents } from '@/hooks/useIncidents'
import { useNotifications } from '@/hooks/useNotifications'
import { PageHeader } from '@/components/common/PageHeader'
import { StatsCard } from '@/components/ui/StatsCard'
import { IncidentCard } from '@/components/incident/IncidentCard'
import { EmptyState } from '@/components/ui/EmptyState'
import { SkeletonCard } from '@/components/ui/LoadingSpinner'
import type { IncidentStatus } from '@/types'

const NEARBY = [
  { type: '🏥', label: 'AIIMS Hospital', dist: '1.2 km', status: 'Open', color: 'text-green-600' },
  { type: '🏠', label: 'District Shelter', dist: '2.1 km', status: '342/500', color: 'text-blue-600' },
  { type: '👮', label: 'Police Station', dist: '0.8 km', status: 'Available', color: 'text-green-600' },
  { type: '🚒', label: 'Fire Station', dist: '3.0 km', status: 'Available', color: 'text-green-600' },
]

export default function CitizenDashboard() {
  const { user } = useAuth()
  const { data: myIncidents, isLoading } = useMyIncidents()
  const { unreadCount } = useNotifications()

  const incidents = myIncidents || []
  const active = incidents.filter(i => !(['RESOLVED','CLOSED','ARCHIVED'] as IncidentStatus[]).includes(i.status))
  const resolved = incidents.filter(i => i.status === 'RESOLVED')

  return (
    <div className="space-y-6">
      <PageHeader
        title={`Welcome, ${user?.displayName?.split(' ')[0] || 'Citizen'} 👋`}
        subtitle={`${user?.district}, ${user?.state} · ${user?.role}`}
        action={
          <Link to="/report" className="flex items-center gap-2 rounded-lg bg-blue-600 hover:bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white transition-colors shadow-sm">
            <Plus className="h-4 w-4" /> Report Incident
          </Link>
        }
      />

      {/* SOS Button */}
      <div className="rounded-2xl bg-gradient-to-r from-red-600 to-red-700 p-6 text-white shadow-lg shadow-red-200 dark:shadow-red-900/30">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold">Emergency SOS</h2>
            <p className="mt-0.5 text-sm text-red-100">One tap to alert all nearby rescue units instantly</p>
          </div>
          <Link
            to="/report"
            state={{ isSOS: true }}
            className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-white text-red-600 text-sm font-black shadow-xl hover:scale-105 active:scale-95 transition-transform animate-pulse hover:animate-none"
          >
            🆘 SOS
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatsCard title="Active Reports" value={active.length} icon={AlertTriangle} variant={active.length > 0 ? 'warning' : 'default'} />
        <StatsCard title="Resolved" value={resolved.length} icon={CheckCircle2} variant="success" />
        <StatsCard title="Total Reports" value={incidents.length} icon={FileText} />
        <StatsCard title="Notifications" value={unreadCount} icon={Bell} variant={unreadCount > 0 ? 'critical' : 'default'} />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Recent Reports */}
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-gray-900 dark:text-white">My Recent Reports</h2>
            <Link to="/my-reports" className="text-sm font-medium text-blue-600 dark:text-blue-400 hover:underline">View all</Link>
          </div>
          {isLoading ? (
            <div className="space-y-3">{Array.from({length: 3}).map((_,i) => <SkeletonCard key={i} />)}</div>
          ) : incidents.length === 0 ? (
            <EmptyState icon={FileText} title="No reports yet" description="Submit your first emergency report when needed." action={
              <Link to="/report" className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
                <Plus className="h-4 w-4" /> Report Incident
              </Link>
            } />
          ) : (
            <div className="space-y-3">
              {incidents.slice(0, 5).map(inc => (
                <IncidentCard key={inc.incidentId} incident={inc} href={`/track/${inc._firestoreId || inc.incidentId}`} />
              ))}
            </div>
          )}
        </div>

        {/* Nearby Resources */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-gray-900 dark:text-white">Nearby Resources</h2>
            <Link to="/authority/map" className="text-sm font-medium text-blue-600 dark:text-blue-400 hover:underline">Map</Link>
          </div>
          <div className="space-y-3">
            {NEARBY.map((r, i) => (
              <div key={i} className="flex items-center gap-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-3 shadow-sm">
                <span className="text-2xl">{r.type}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{r.label}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="flex items-center gap-1 text-xs text-gray-500"><MapPin className="h-3 w-3" />{r.dist}</span>
                    <span className={`text-xs font-medium ${r.color}`}>{r.status}</span>
                  </div>
                </div>
                <button className="flex h-7 w-7 items-center justify-center rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors">
                  <Phone className="h-3.5 w-3.5 text-gray-500 dark:text-gray-400" />
                </button>
              </div>
            ))}
          </div>

          {/* Emergency Contacts */}
          {user?.emergencyContacts && user.emergencyContacts.length > 0 && (
            <div className="mt-4">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Emergency Contacts</h3>
              <div className="space-y-2">
                {user.emergencyContacts.slice(0, 3).map((c, i) => (
                  <div key={i} className="flex items-center gap-2 rounded-lg bg-gray-50 dark:bg-gray-800 px-3 py-2">
                    <span className="text-sm text-gray-900 dark:text-white font-medium flex-1">{c.name}</span>
                    <span className="text-xs text-gray-500">{c.relationship}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
