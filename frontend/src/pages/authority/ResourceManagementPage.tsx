import { useState } from 'react'
import { Plus, Search, MapPin, Phone } from 'lucide-react'
import { useResources, useUpdateResourceStatus } from '@/hooks/useResources'
import { PageHeader } from '@/components/common/PageHeader'
import { StatsCard } from '@/components/ui/StatsCard'
import { EmptyState } from '@/components/ui/EmptyState'
import { SkeletonCard } from '@/components/ui/LoadingSpinner'
import { cn } from '@/utils/cn'
import { RESOURCE_TYPE_ICONS, RESOURCE_STATUS_COLORS } from '@/utils/constants'
import { Package, Truck, Activity, AlertTriangle } from 'lucide-react'
import { toast } from 'sonner'
import type { ResourceStatus } from '@/types'

const STATUSES: ResourceStatus[] = ['AVAILABLE','DEPLOYED','MAINTENANCE','UNAVAILABLE']

export default function ResourceManagementPage() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<ResourceStatus | ''>('')
  const [typeFilter, setTypeFilter] = useState('')

  const { data, isLoading } = useResources({ status: statusFilter || undefined, limit: 100 })
  const updateStatus = useUpdateResourceStatus()

  const resources = data?.data?.items || []
  const filtered = resources.filter(r =>
    (!search || r.name.toLowerCase().includes(search.toLowerCase())) &&
    (!typeFilter || r.type === typeFilter)
  )

  const counts = resources.reduce((acc, r) => { acc[r.status] = (acc[r.status] || 0) + 1; return acc }, {} as Record<string, number>)

  const handleStatusChange = async (id: string, status: ResourceStatus) => {
    try {
      await updateStatus.mutateAsync({ id, status })
      toast.success(`Status updated to ${status}`)
    } catch { toast.error('Update failed') }
  }

  return (
    <div>
      <PageHeader
        title="Resource Management"
        subtitle="Track and manage all rescue resources"
        breadcrumbs={[{ label: 'Dashboard', href: '/authority' }, { label: 'Resources' }]}
        action={
          <button className="flex items-center gap-2 rounded-lg bg-blue-600 hover:bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white transition-colors">
            <Plus className="h-4 w-4" /> Add Resource
          </button>
        }
      />

      {/* Stats */}
      <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatsCard title="Total Resources" value={resources.length} icon={Package} />
        <StatsCard title="Available" value={counts.AVAILABLE || 0} icon={Activity} variant="success" />
        <StatsCard title="Deployed" value={counts.DEPLOYED || 0} icon={Truck} variant="warning" />
        <StatsCard title="Maintenance" value={counts.MAINTENANCE || 0} icon={AlertTriangle} />
      </div>

      {/* Filters */}
      <div className="mb-5 flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search resources…"
            className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white" />
        </div>
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value as ResourceStatus | '')}
          className="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2.5 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">All Status</option>
          {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{Array.from({length:6}).map((_,i)=><SkeletonCard key={i}/>)}</div>
      ) : filtered.length === 0 ? (
        <EmptyState icon={Package} title="No resources found" description="Add resources to start managing your rescue inventory." />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map(r => (
            <div key={r.resourceId} className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-start gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gray-50 dark:bg-gray-700 text-xl">
                  {RESOURCE_TYPE_ICONS[r.type] || '🚨'}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">{r.name}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{r.type.replace('_',' ')}</p>
                </div>
                <span className={cn('rounded-full px-2 py-0.5 text-xs font-semibold', RESOURCE_STATUS_COLORS[r.status] || 'bg-gray-100 text-gray-600')}>
                  {r.status}
                </span>
              </div>

              {/* Details */}
              <div className="mt-3 space-y-1 text-xs text-gray-500 dark:text-gray-400">
                <div className="flex items-center gap-1.5"><MapPin className="h-3 w-3"/>{r.district}, {r.state}</div>
                <div className="flex items-center gap-1.5"><Phone className="h-3 w-3"/>{r.contactName} · {r.contactPhone}</div>
              </div>

              {/* Capacity bar */}
              {r.capacity?.total && (
                <div className="mt-3">
                  <div className="flex justify-between text-xs text-gray-500 mb-1">
                    <span>Capacity</span>
                    <span>{r.capacity.current}/{r.capacity.total}</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-gray-100 dark:bg-gray-700">
                    <div className="h-1.5 rounded-full bg-blue-500"
                      style={{ width: `${((r.capacity.current || 0) / r.capacity.total) * 100}%` }} />
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="mt-4 flex gap-2">
                <select
                  value={r.status}
                  onChange={e => handleStatusChange(r._firestoreId || r.resourceId, e.target.value as ResourceStatus)}
                  className="flex-1 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700 px-2 py-1.5 text-xs text-gray-700 dark:text-gray-300 focus:outline-none"
                >
                  {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
