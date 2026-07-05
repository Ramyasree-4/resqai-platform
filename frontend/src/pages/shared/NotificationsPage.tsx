import { useState } from 'react'
import { Bell, AlertTriangle, Info, Shield, CheckCheck } from 'lucide-react'
import { useNotifications } from '@/hooks/useNotifications'
import { PageHeader } from '@/components/common/PageHeader'
import { EmptyState } from '@/components/ui/EmptyState'
import { SkeletonCard } from '@/components/ui/LoadingSpinner'
import { cn } from '@/utils/cn'
import { formatRelativeTime } from '@/utils/formatters'

type Filter = 'all' | 'unread' | 'critical' | 'system'

const typeIcons: Record<string, React.ReactNode> = {
  NEW_INCIDENT: <AlertTriangle className="h-5 w-5 text-red-500" />,
  INCIDENT_STATUS: <Info className="h-5 w-5 text-blue-500" />,
  ASSIGNMENT: <Shield className="h-5 w-5 text-orange-500" />,
  BROADCAST: <AlertTriangle className="h-5 w-5 text-yellow-500" />,
  CLUSTER_ALERT: <AlertTriangle className="h-5 w-5 text-red-600" />,
  SYSTEM: <Info className="h-5 w-5 text-gray-500" />,
}

const priorityBorder: Record<string, string> = {
  URGENT: 'border-l-red-500',
  HIGH: 'border-l-orange-500',
  NORMAL: 'border-l-blue-500',
  LOW: 'border-l-gray-300',
}

export default function NotificationsPage() {
  const [filter, setFilter] = useState<Filter>('all')
  const { notifications, isLoading, unreadCount, markAsRead, markAllRead } = useNotifications()

  const items = (notifications || []).filter(n => {
    if (filter === 'unread') return !n.isRead
    if (filter === 'critical') return n.priority === 'URGENT' || n.priority === 'HIGH'
    if (filter === 'system') return n.type === 'SYSTEM' || n.type === 'BROADCAST'
    return true
  })

  return (
    <div>
      <PageHeader
        title="Notifications"
        subtitle={`${unreadCount} unread`}
        breadcrumbs={[{ label: 'Notifications' }]}
        action={
          unreadCount > 0 ? (
            <button onClick={() => markAllRead()} className="flex items-center gap-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              <CheckCheck className="h-4 w-4" /> Mark All Read
            </button>
          ) : undefined
        }
      />

      {/* Filter tabs */}
      <div className="flex gap-1 rounded-xl bg-gray-100 dark:bg-gray-800 p-1 mb-6 w-fit">
        {(['all','unread','critical','system'] as Filter[]).map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={cn('rounded-lg px-4 py-1.5 text-sm font-medium capitalize transition-colors', filter === f
              ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
              : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
            )}>
            {f === 'all' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1)}
            {f === 'unread' && unreadCount > 0 && (
              <span className="ml-1.5 rounded-full bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5">{unreadCount}</span>
            )}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="space-y-3">{Array.from({length:5}).map((_,i)=><SkeletonCard key={i}/>)}</div>
      ) : items.length === 0 ? (
        <EmptyState icon={Bell} title="No notifications" description="You're all caught up." />
      ) : (
        <div className="space-y-2">
          {items.map(n => (
            <div
              key={n.notificationId}
              onClick={() => !n.isRead && markAsRead(n._firestoreId || n.notificationId)}
              className={cn(
                'flex cursor-pointer items-start gap-4 rounded-xl border border-l-4 bg-white dark:bg-gray-800 p-4 shadow-sm transition-colors hover:bg-gray-50 dark:hover:bg-gray-700/50',
                priorityBorder[n.priority] || 'border-l-gray-300',
                !n.isRead && 'bg-blue-50/50 dark:bg-blue-900/5'
              )}
            >
              <div className="mt-0.5 shrink-0">
                {typeIcons[n.type] || <Info className="h-5 w-5 text-gray-400" />}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <p className={cn('text-sm text-gray-900 dark:text-white', !n.isRead && 'font-semibold')}>
                    {n.title}
                  </p>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-xs text-gray-400">{formatRelativeTime(n.createdAt)}</span>
                    {!n.isRead && <div className="h-2 w-2 rounded-full bg-blue-500" />}
                  </div>
                </div>
                <p className="mt-0.5 text-sm text-gray-600 dark:text-gray-400">{n.body}</p>
                {n.priority === 'URGENT' && (
                  <span className="mt-1.5 inline-block rounded-full bg-red-100 dark:bg-red-900/30 px-2 py-0.5 text-xs font-semibold text-red-700 dark:text-red-400">
                    URGENT
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
