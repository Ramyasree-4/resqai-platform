import api from './api'
import { API_ENDPOINTS } from '@/utils/constants'
import type {
  DashboardStats,
  MapData,
  IncidentTrendData,
  AnalyticsSummary,
  DashboardParams,
  AnalyticsParams,
  TrendParams,
} from '@/types'

interface ApiResponse<T> {
  success: boolean
  data: T
}

export interface SystemStats {
  totalUsers: number
  totalIncidents: number
  totalResources: number
  systemHealth: 'HEALTHY' | 'DEGRADED' | 'DOWN'
  geminiApiUsage: { requestsToday: number; costUSD: number }
}

export const analyticsService = {
  async getDashboardStats(params?: DashboardParams): Promise<ApiResponse<DashboardStats>> {
    const res = await api.get<ApiResponse<DashboardStats>>(
      API_ENDPOINTS.DASHBOARD_STATS,
      { params }
    )
    return res.data
  },

  async getMapData(params?: {
    district?: string
    state?: string
    includeResolved?: boolean
  }): Promise<ApiResponse<MapData>> {
    const res = await api.get<ApiResponse<MapData>>(API_ENDPOINTS.DASHBOARD_MAP, { params })
    return res.data
  },

  async getIncidentTrend(params?: TrendParams): Promise<IncidentTrendData> {
    const res = await api.get<ApiResponse<IncidentTrendData>>(
      API_ENDPOINTS.DASHBOARD_TREND,
      { params }
    )
    return res.data.data
  },

  async getAnalyticsSummary(params?: AnalyticsParams): Promise<ApiResponse<AnalyticsSummary>> {
    const res = await api.get<ApiResponse<AnalyticsSummary>>(
      API_ENDPOINTS.ANALYTICS_SUMMARY,
      { params }
    )
    return res.data
  },

  async getResponseTime(): Promise<ApiResponse<{ byType: Record<string, { avg: number; count: number }> }>> {
    const res = await api.get<ApiResponse<{ byType: Record<string, { avg: number; count: number }> }>>(
      API_ENDPOINTS.ANALYTICS_RESPONSE_TIME
    )
    return res.data
  },

  async getResourceUtilization(): Promise<ApiResponse<{
    totalResources: number
    deployed: number
    utilizationRate: number
    byType: Record<string, Record<string, number>>
  }>> {
    const res = await api.get(API_ENDPOINTS.ANALYTICS_RESOURCE_UTIL)
    return res.data
  },

  async exportAnalytics(params: {
    format: 'PDF' | 'CSV' | 'BOTH'
    from: string
    to: string
    district?: string
    includeCharts?: boolean
  }): Promise<ApiResponse<{ reportId: string; message: string }>> {
    const res = await api.post<ApiResponse<{ reportId: string; message: string }>>(
      API_ENDPOINTS.ANALYTICS_EXPORT,
      params
    )
    return res.data
  },

  async getSystemStats(): Promise<ApiResponse<SystemStats>> {
    const res = await api.get<ApiResponse<SystemStats>>(API_ENDPOINTS.ADMIN_STATS)
    return res.data
  },
}
