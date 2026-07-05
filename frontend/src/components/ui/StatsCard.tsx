import { type LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { cn } from '@/utils/cn'

interface StatsCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: LucideIcon
  iconColor?: string
  iconBg?: string
  trend?: number
  trendLabel?: string
  variant?: 'default' | 'critical' | 'warning' | 'success' | 'info'
  className?: string
}

const variants = {
  default: { icon: 'text-blue-600 dark:text-blue-400', iconBg: 'bg-blue-50 dark:bg-blue-900/20', value: 'text-gray-900 dark:text-white' },
  critical: { icon: 'text-red-600 dark:text-red-400', iconBg: 'bg-red-50 dark:bg-red-900/20', value: 'text-red-600 dark:text-red-400' },
  warning: { icon: 'text-orange-600 dark:text-orange-400', iconBg: 'bg-orange-50 dark:bg-orange-900/20', value: 'text-orange-600 dark:text-orange-400' },
  success: { icon: 'text-green-600 dark:text-green-400', iconBg: 'bg-green-50 dark:bg-green-900/20', value: 'text-green-600 dark:text-green-400' },
  info: { icon: 'text-indigo-600 dark:text-indigo-400', iconBg: 'bg-indigo-50 dark:bg-indigo-900/20', value: 'text-gray-900 dark:text-white' },
}

export function StatsCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendLabel,
  variant = 'default',
  className,
}: StatsCardProps) {
  const v = variants[variant]

  return (
    <div className={cn(
      'rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6',
      'shadow-sm hover:shadow-md transition-shadow duration-200',
      className
    )}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</p>
          <p className={cn('mt-2 text-3xl font-bold tracking-tight', v.value)}>{value}</p>
          {subtitle && (
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{subtitle}</p>
          )}
        </div>
        <div className={cn('flex h-12 w-12 items-center justify-center rounded-xl', v.iconBg)}>
          <Icon className={cn('h-6 w-6', v.icon)} />
        </div>
      </div>

      {trend !== undefined && (
        <div className="mt-4 flex items-center gap-1">
          {trend > 0 ? (
            <TrendingUp className="h-4 w-4 text-red-500" />
          ) : trend < 0 ? (
            <TrendingDown className="h-4 w-4 text-green-500" />
          ) : (
            <Minus className="h-4 w-4 text-gray-400" />
          )}
          <span className={cn('text-xs font-medium',
            trend > 0 ? 'text-red-500' : trend < 0 ? 'text-green-500' : 'text-gray-400'
          )}>
            {Math.abs(trend)}%
          </span>
          {trendLabel && <span className="text-xs text-gray-400">{trendLabel}</span>}
        </div>
      )}
    </div>
  )
}
