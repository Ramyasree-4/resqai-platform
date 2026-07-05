import { cn } from '@/utils/cn'
import { SEVERITY_COLORS } from '@/utils/constants'
import type { SeverityBand } from '@/types'

interface SeverityBadgeProps {
  band: SeverityBand
  score?: number
  size?: 'sm' | 'md' | 'lg'
  showDot?: boolean
  className?: string
}

export function SeverityBadge({ band, score, size = 'md', showDot = true, className }: SeverityBadgeProps) {
  const colors = SEVERITY_COLORS[band]
  const sizes = { sm: 'text-xs px-2 py-0.5', md: 'text-sm px-2.5 py-1', lg: 'text-base px-3 py-1.5' }
  const dotSizes = { sm: 'h-1.5 w-1.5', md: 'h-2 w-2', lg: 'h-2.5 w-2.5' }

  const labels: Record<SeverityBand, string> = {
    CRITICAL: 'Critical',
    HIGH: 'High',
    MEDIUM: 'Medium',
    LOW: 'Low',
  }

  return (
    <span className={cn(
      'inline-flex items-center gap-1.5 rounded-full font-semibold',
      colors.bg, colors.text,
      sizes[size],
      className
    )}>
      {showDot && (
        <span className={cn('rounded-full', colors.dot, dotSizes[size])} />
      )}
      {labels[band]}
      {score !== undefined && ` ${score}/10`}
    </span>
  )
}
