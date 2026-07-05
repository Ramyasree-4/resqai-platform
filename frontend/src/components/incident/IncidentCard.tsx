import { Clock, MapPin, Users, ChevronRight, Zap } from 'lucide-react'
import { Link } from 'react-router-dom'
import { SeverityBadge } from '@/components/ui/SeverityBadge'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { cn } from '@/utils/cn'
import { formatRelativeTime } from '@/utils/formatters'
import { INCIDENT_TYPE_LABELS } from '@/utils/constants'
import type { IncidentListItem } from '@/types'

interface Props {
  incident: IncidentListItem
  href?: string
  compact?: boolean
  className?: string
}

export function IncidentCard({ incident, href, compact, className }: Props) {
  const typeInfo = INCIDENT_TYPE_LABELS[incident.incidentType] || { emoji: '⚠️', label: incident.incidentType }

  return (
    <div className={cn(
      'rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800',
      'hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-md transition-all duration-200',
      incident.severityBand === 'CRITICAL' && 'border-l-4 border-l-red-500',
      incident.severityBand === 'HIGH' && 'border-l-4 border-l-orange-500',
      compact ? 'p-3' : 'p-4',
      className
    )}>
      <div className="flex items-start gap-3">
        {/* Type icon */}
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gray-50 dark:bg-gray-700 text-xl">
          {typeInfo.emoji}
        </div>

        <div className="flex-1 min-w-0">
          {/* Title row */}
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm font-semibold text-gray-900 dark:text-white line-clamp-1">{incident.title}</p>
            <div className="flex shrink-0 items-center gap-1.5">
              {incident.severityBand && (
                <SeverityBadge band={incident.severityBand} score={incident.severityScore} size="sm" />
              )}
              <StatusBadge status={incident.status} />
            </div>
          </div>

          {/* Meta row */}
          <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-gray-500 dark:text-gray-400">
            <span className="flex items-center gap-1">
              <MapPin className="h-3 w-3" /> {incident.district}, {incident.state}
            </span>
            <span className="flex items-center gap-1">
              <Users className="h-3 w-3" /> {incident.affectedPeople.toLocaleString()} affected
            </span>
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" /> {formatRelativeTime(incident.createdAt)}
            </span>
            {incident.incidentId && (
              <span className="font-mono text-[10px] bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded">
                {incident.incidentId}
              </span>
            )}
          </div>

          {/* AI Score */}
          {incident.severityScore !== undefined && !compact && (
            <div className="mt-2 flex items-center gap-2">
              <div className="flex items-center gap-1 text-xs text-purple-600 dark:text-purple-400">
                <Zap className="h-3 w-3" />
                <span>AI Score: <strong>{incident.severityScore}/10</strong></span>
              </div>
              <div className="flex-1 h-1.5 rounded-full bg-gray-100 dark:bg-gray-700">
                <div
                  className="h-1.5 rounded-full bg-gradient-to-r from-green-500 via-yellow-500 to-red-600"
                  style={{ width: `${(incident.severityScore / 10) * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Action */}
        {href && (
          <Link
            to={href}
            className="shrink-0 flex h-8 w-8 items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-blue-600 transition-colors"
          >
            <ChevronRight className="h-4 w-4" />
          </Link>
        )}
      </div>
    </div>
  )
}
