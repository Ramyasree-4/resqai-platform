import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { notificationService } from '@/services/notification.service'
import type { NotificationFilters } from '@/types'
import { toast } from 'sonner'

export const notificationKeys = {
  all: ['notifications'] as const,
  list: (filters?: NotificationFilters) => [...notificationKeys.all, 'list', filters] as const,
}

/** Full hook — returns notifications list + helpers in one object */
export function useNotifications(filters?: NotificationFilters) {
  const qc = useQueryClient()

  const query = useQuery({
    queryKey: notificationKeys.list(filters),
    queryFn: () => notificationService.getNotifications(filters),
    refetchInterval: 30000,
    select: (data) => data?.data?.items ?? [],
  })

  const markReadMutation = useMutation({
    mutationFn: (id: string) => notificationService.markAsRead(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: notificationKeys.all }),
  })

  const markAllMutation = useMutation({
    mutationFn: () => notificationService.markAllRead(),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: notificationKeys.all })
      toast.success('All notifications marked as read')
    },
  })

  const notifications = query.data ?? []
  const unreadCount = notifications.filter(n => !n.isRead).length

  return {
    notifications,
    unreadCount,
    isLoading: query.isLoading,
    markAsRead: (id: string) => markReadMutation.mutate(id),
    markAllRead: () => markAllMutation.mutate(),
  }
}

/** Lightweight unread count for topbar badge */
export function useUnreadCount() {
  const query = useQuery({
    queryKey: notificationKeys.list({ isRead: false, limit: 100 }),
    queryFn: () => notificationService.getNotifications({ isRead: false, limit: 100 }),
    refetchInterval: 30000,
    select: (data) => (data?.data?.items ?? []).filter(n => !n.isRead).length,
  })
  return { count: query.data ?? 0, isLoading: query.isLoading }
}
