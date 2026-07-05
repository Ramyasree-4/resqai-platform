import { CheckCircle2, Clock, Circle } from 'lucide-react'
import { cn } from '@/utils/cn'
import { STATUS_LABELS } from '@/utils/constants'
import { formatRelativeTime } from '@/utils/formatters'
import type { IncidentStatus } from '@/types'

interface TimelineEntry {
  fromStatus?: string | null
  toStatus: string
  changedBy: string
  changedAt?: string
  note?: string | null
}

interface Props { entries: TimelineEntry[]; currentStatus: IncidentStatus }

const ORDER: IncidentStatus[] = ['SUBMITTED','AI_PROCESSING','TRIAGED','ASSIGNED','IN_PROGRESS','RESOLVED','CLOSED']

export function IncidentTimeline({ entries, currentStatus }: Props) {
  const sorted = [...entries].sort((a, b) =>
    new Date(a.changedAt || 0).getTime() - new Date(b.changedAt || 0).getTime()
  )

  return (
    <div className="space-y-0">
      {sorted.map((entry, i) => {
        const isLast = i === sorted.length - 1
        const meta = STATUS_LABELS[entry.toStatus as IncidentStatus]
        return (
          <div key={i} className="flex gap-3">
            {/* Connector */}
            <div className="flex flex-col items-center">
              <div className={cn(
                'flex h-7 w-7 shrink-0 items-center justify-center rounded-full',
                isLast ? 'bg-blue-100 dark:bg-blue-900/30' : 'bg-gray-100 dark:bg-gray-700'
              )}>
                {isLast
                  ? <CheckCircle2 className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                  : <Circle className="h-3 w-3 text-gray-400 fill-gray-300" />
                }
              </div>
              {!isLast && <div className="w-px flex-1 bg-gray-200 dark:bg-gray-700 my-1" />}
            </div>
            {/* Content */}
            <div className={cn('pb-4 flex-1', isLast && 'pb-0')}>
              <div className="flex items-center gap-2">
                <span className={cn('text-xs font-semibold px-2 py-0.5 rounded-full', meta?.color || 'bg-gray-100 text-gray-600')}>
                  {meta?.label || entry.toStatus}
                </span>
                <span className="text-xs text-gray-400">{formatRelativeTime(entry.changedAt)}</span>
              </div>
              {entry.note && (
                <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">{entry.note}</p>
              )}
              <p className="mt-0.5 text-[10px] text-gray-400">by {entry.changedBy === 'SYSTEM' ? '🤖 AI System' : entry.changedBy}</p>
            </div>
          </div>
        )
      })}
    </div>
  )
}
