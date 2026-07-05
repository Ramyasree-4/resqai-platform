import { useState } from 'react'
import { Search, MapPin, CheckSquare, Square, Loader2 } from 'lucide-react'
import { cn } from '@/utils/cn'
import { RESOURCE_TYPE_ICONS, RESOURCE_STATUS_COLORS } from '@/utils/constants'
import type { ResourceResponse } from '@/types'

interface Props {
  resources: ResourceResponse[]
  isLoading?: boolean
  onAssign: (resourceIds: string[]) => Promise<void>
  incidentId: string
}

export function ResourceAssignmentPanel({ resources, isLoading, onAssign, incidentId }: Props) {
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [search, setSearch] = useState('')
  const [assigning, setAssigning] = useState(false)

  const available = resources.filter(r =>
    r.status === 'AVAILABLE' &&
    (r.name.toLowerCase().includes(search.toLowerCase()) ||
     r.type.toLowerCase().includes(search.toLowerCase()))
  )

  const toggle = (id: string) => {
    const next = new Set(selected)
    next.has(id) ? next.delete(id) : next.add(id)
    setSelected(next)
  }

  const handleAssign = async () => {
    if (selected.size === 0) return
    setAssigning(true)
    try {
      await onAssign(Array.from(selected))
      setSelected(new Set())
    } finally {
      setAssigning(false)
    }
  }

  return (
    <div className="space-y-3">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Search resources…"
          className="w-full rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 pl-9 pr-3 py-2 text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* List */}
      {isLoading ? (
        <div className="flex justify-center py-6"><Loader2 className="h-6 w-6 animate-spin text-blue-500" /></div>
      ) : available.length === 0 ? (
        <div className="py-6 text-center text-sm text-gray-500 dark:text-gray-400">No available resources found</div>
      ) : (
        <div className="max-h-64 space-y-2 overflow-y-auto pr-1">
          {available.map(r => {
            const isSelected = selected.has(r._firestoreId || r.resourceId)
            return (
              <div
                key={r.resourceId}
                onClick={() => toggle(r._firestoreId || r.resourceId)}
                className={cn(
                  'flex cursor-pointer items-center gap-3 rounded-lg border p-3 transition-all',
                  isSelected
                    ? 'border-blue-300 dark:border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-300'
                )}
              >
                {isSelected
                  ? <CheckSquare className="h-5 w-5 shrink-0 text-blue-600" />
                  : <Square className="h-5 w-5 shrink-0 text-gray-400" />
                }
                <span className="text-xl">{RESOURCE_TYPE_ICONS[r.type] || '🚨'}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{r.name}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className={cn('text-[10px] rounded-full px-1.5 py-0.5 font-medium', RESOURCE_STATUS_COLORS[r.status] || 'bg-gray-100 text-gray-600')}>
                      {r.status}
                    </span>
                    <span className="flex items-center gap-0.5 text-[10px] text-gray-500">
                      <MapPin className="h-3 w-3" />{r.district}
                    </span>
                  </div>
                </div>
                {(r as any).distanceKm !== undefined && (
                  <span className="text-xs font-medium text-gray-500">{(r as any).distanceKm} km</span>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Assign Button */}
      <button
        onClick={handleAssign}
        disabled={selected.size === 0 || assigning}
        className="w-full flex items-center justify-center gap-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 dark:disabled:bg-gray-700 text-white disabled:text-gray-500 py-2.5 text-sm font-semibold transition-colors"
      >
        {assigning
          ? <><Loader2 className="h-4 w-4 animate-spin" /> Assigning…</>
          : `Assign & Dispatch ${selected.size > 0 ? `(${selected.size})` : ''}`
        }
      </button>
    </div>
  )
}
