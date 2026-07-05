import { Bell, CheckCheck, AlertTriangle, Info, Shield } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useNotifications } from '@/hooks/useNotifications'
import { cn } from '@/utils/cn'
import { formatRelativeTime } from '@/utils/formatters'

const typeIcons: Record<string, React.ReactNode> = {
  NEW_INCIDENT: <AlertTriangle className="h-4 w-4 text-red-500" />,
  INCIDENT_STATUS: <Info className="h-4 w-4 text-blue-500" />,
  ASSIGNMENT: <Shield className="h-4 w-4 text-orange-500" />,
  BROADCAST: <AlertTriangle className="h-4 w-4 text-yellow-500" />,
  CLUSTER_ALERT: <AlertTriangle className="h-4 w-4 text-red-600" />,
  SYSTEM: <Info className="h-4 w-4 text-gray-500" />,
}

export function NotificationBell() {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const { notifications, unreadCount, markAsRead, markAllRead } = useNotifications()
  const recent = (notifications || []).slice(0, 6)

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="relative flex h-9 w-9 items-center justify-center rounded-lg text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700 transition-colors"
        aria-label="Notifications"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute -right-0.5 -top-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-11 z-50 w-80 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-xl">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-gray-100 dark:border-gray-700 px-4 py-3">
            <span className="text-sm font-semibold text-gray-900 dark:text-white">
              Notifications {unreadCount > 0 && <span className="ml-1 text-xs text-red-500">({unreadCount} new)</span>}
            </span>
            {unreadCount > 0 && (
              <button
                onClick={() => markAllRead()}
                className="flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400 hover:underline"
              >
                <CheckCheck className="h-3.5 w-3.5" /> Mark all read
              </button>
            )}
          </div>

          {/* List */}
          <div className="max-h-72 overflow-y-auto">
            {recent.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-10 text-center">
                <Bell className="h-8 w-8 text-gray-300 dark:text-gray-600 mb-2" />
                <p className="text-sm text-gray-500 dark:text-gray-400">No notifications yet</p>
              </div>
            ) : (
              recent.map((n) => (
                <div
                  key={n.notificationId}
                  onClick={() => { markAsRead(n._firestoreId || n.notificationId); setOpen(false) }}
                  className={cn(
                    'flex cursor-pointer gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors',
                    !n.isRead && 'bg-blue-50/50 dark:bg-blue-900/10'
                  )}
                >
                  <div className="mt-0.5 shrink-0">
                    {typeIcons[n.type] || <Info className="h-4 w-4 text-gray-400" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className={cn('text-xs font-medium text-gray-900 dark:text-white line-clamp-1', !n.isRead && 'font-semibold')}>
                      {n.title}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 mt-0.5">{n.body}</p>
                    <p className="text-[10px] text-gray-400 mt-1">{formatRelativeTime(n.createdAt)}</p>
                  </div>
                  {!n.isRead && <div className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-blue-500" />}
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="border-t border-gray-100 dark:border-gray-700 px-4 py-2">
            <Link
              to="/notifications"
              onClick={() => setOpen(false)}
              className="block text-center text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline py-1"
            >
              View all notifications
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}
