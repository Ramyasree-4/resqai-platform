import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Filter, SortDesc } from 'lucide-react'
import { useIncidents } from '@/hooks/useIncidents'
import { PageHeader } from '@/components/common/PageHeader'
import { IncidentCard } from '@/components/incident/IncidentCard'
import { SeverityBadge } from '@/components/ui/SeverityBadge'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { EmptyState } from '@/components/ui/EmptyState'
import { SkeletonCard } from '@/components/ui/LoadingSpinner'
import { AlertTriangle } from 'lucide-react'
import type { IncidentStatus, IncidentType, SeverityBand } from '@/types'

const STATUSES: IncidentStatus[] = ['SUBMITTED','AI_PROCESSING','TRIAGED','ASSIGNED','IN_PROGRESS','RESOLVED']
const TYPES: IncidentType[] = ['FLOOD','CYCLONE','EARTHQUAKE','LANDSLIDE','FIRE','MEDICAL','INDUSTRIAL','OTHER']
const SEVERITIES: SeverityBand[] = ['CRITICAL','HIGH','MEDIUM','LOW']

export default function IncidentQueuePage() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<IncidentStatus | ''>('')
  const [type, setType] = useState<IncidentType | ''>('')
  const [severity, setSeverity] = useState<SeverityBand | ''>('')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useIncidents({
    status: status || undefined,
    type: type || undefined,
    severity: severity || undefined,
    sort: 'severity',
    page,
    limit: 20,
  })

  const incidents = data?.data?.items || []
  const pagination = data?.data?.pagination

  const filtered = search
    ? incidents.filter(i =>
        i.title.toLowerCase().includes(search.toLowerCase()) ||
        i.district.toLowerCase().includes(search.toLowerCase()) ||
        i.incidentId.toLowerCase().includes(search.toLowerCase())
      )
    : incidents

  return (
    <div>
      <PageHeader
        title="Incident Queue"
        subtitle="All active incidents sorted by AI severity score"
        breadcrumbs={[{ label: 'Dashboard', href: '/authority' }, { label: 'Incidents' }]}
      />

      {/* Filters */}
      <div className="mb-6 flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search by ID, title, district…"
            className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
          />
        </div>
        <select
          value={status}
          onChange={e => setStatus(e.target.value as IncidentStatus | '')}
          className="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2.5 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Status</option>
          {STATUSES.map(s => <option key={s} value={s}>{s.replace('_', ' ')}</option>)}
        </select>
        <select
          value={type}
          onChange={e => setType(e.target.value as IncidentType | '')}
          className="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2.5 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Types</option>
          {TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <select
          value={severity}
          onChange={e => setSeverity(e.target.value as SeverityBand | '')}
          className="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2.5 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Severity</option>
          {SEVERITIES.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      {/* Results */}
      {isLoading ? (
        <div className="space-y-4">{Array.from({length:6}).map((_,i)=><SkeletonCard key={i}/>)}</div>
      ) : filtered.length === 0 ? (
        <EmptyState icon={AlertTriangle} title="No incidents found" description="Adjust filters or check back later." />
      ) : (
        <>
          <div className="mb-3 flex items-center justify-between">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {pagination ? `${pagination.total} total` : `${filtered.length} results`}
              {search && ` · filtered to ${filtered.length}`}
            </p>
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <SortDesc className="h-3.5 w-3.5" /> Sorted by AI severity
            </div>
          </div>
          <div className="space-y-3">
            {filtered.map(inc => (
              <IncidentCard
                key={inc.incidentId}
                incident={inc}
                href={`/authority/incidents/${inc._firestoreId || inc.incidentId}`}
              />
            ))}
          </div>

          {/* Pagination */}
          {pagination && pagination.totalPages > 1 && (
            <div className="mt-6 flex items-center justify-between">
              <p className="text-sm text-gray-500">{pagination.page} / {pagination.totalPages} pages</p>
              <div className="flex gap-2">
                <button
                  disabled={page === 1}
                  onClick={() => setPage(p => p - 1)}
                  className="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
                >
                  Previous
                </button>
                <button
                  disabled={page >= pagination.totalPages}
                  onClick={() => setPage(p => p + 1)}
                  className="rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 px-4 py-2 text-sm font-medium text-white"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
