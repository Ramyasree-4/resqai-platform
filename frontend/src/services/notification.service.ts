import api from './api'
import { API_ENDPOINTS } from '@/utils/constants'
import type { Notification, NotificationFilters, BroadcastRequest } from '@/types'

interface ApiResponse<T> {
  success: boolean
  data: T
}

// Backend returns { data: { items: [], pagination: {} } } (paginated shape)
interface PaginatedResult<T> {
  items: T[]
  pagination: {
    total: number
    page: number
    limit: number
    totalPages: number
  }
}

export const notificationService = {
  async getNotifications(
    params?: NotificationFilters
  ): Promise<ApiResponse<PaginatedResult<Notification>>> {
    const res = await api.get<ApiResponse<PaginatedResult<Notification>>>(
      API_ENDPOINTS.NOTIFICATIONS,
      { params }
    )
    // Backend may return different shape — normalise here
    const raw = res.data
    if (!raw.data?.items && (raw.data as any)?.notifications) {
      // Legacy shape fallback
      return {
        success: raw.success,
        data: {
          items: (raw.data as any).notifications ?? [],
          pagination: (raw.data as any).pagination ?? { total: 0, page: 1, limit: 20, totalPages: 1 },
        },
      }
    }
    return raw
  },

  async markAsRead(id: string): Promise<void> {
    await api.put(API_ENDPOINTS.NOTIFICATION_READ(id))
  },

  async markAllRead(): Promise<void> {
    await api.put(API_ENDPOINTS.NOTIFICATIONS_READ_ALL)
  },

  async sendBroadcast(
    data: BroadcastRequest
  ): Promise<{ recipientCount: number; deliveryStatus: string }> {
    const res = await api.post<ApiResponse<{ recipientCount: number; deliveryStatus: string }>>(
      API_ENDPOINTS.NOTIFICATIONS_BROADCAST,
      data
    )
    return res.data.data
  },
}
