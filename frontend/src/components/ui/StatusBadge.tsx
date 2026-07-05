import { cn } from '@/utils/cn'
import { STATUS_LABELS } from '@/utils/constants'
import type { IncidentStatus } from '@/types'

interface StatusBadgeProps {
  status: IncidentStatus
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const { label, color } = STATUS_LABELS[status] ?? { label: status, color: 'bg-gray-100 text-gray-600' }

  return (
    <span className={cn('inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium', color, className)}>
      {label}
    </span>
  )
}
