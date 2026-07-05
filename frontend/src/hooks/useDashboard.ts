import { useQuery } from '@tanstack/react-query'
import { analyticsService } from '@/services/analytics.service'
import type { DashboardParams, TrendParams } from '@/types'

export const dashboardKeys = {
  stats: (params?: DashboardParams) => ['dashboard', 'stats', params] as const,
  mapData: (params?: object) => ['dashboard', 'map', params] as const,
  trend: (params?: TrendParams) => ['dashboard', 'trend', params] as const,
}

export function useDashboardStats(params?: DashboardParams) {
  return useQuery({
    queryKey: dashboardKeys.stats(params),
    queryFn: () => analyticsService.getDashboardStats(params),
    select: (res) => res?.data,
    refetchInterval: 30000,
  })
}

export function useMapData(params?: { district?: string; state?: string; includeResolved?: boolean }) {
  return useQuery({
    queryKey: dashboardKeys.mapData(params),
    queryFn: () => analyticsService.getMapData(params),
    select: (res) => res?.data,
    refetchInterval: 60000,
  })
}

export function useIncidentTrend(days = 7, district?: string) {
  return useQuery({
    queryKey: dashboardKeys.trend({ days, district }),
    queryFn: () => analyticsService.getIncidentTrend({ days, district }),
  })
}

export function useAnalyticsSummary(params?: Parameters<typeof analyticsService.getAnalyticsSummary>[0]) {
  return useQuery({
    queryKey: ['analytics', 'summary', params],
    queryFn: () => analyticsService.getAnalyticsSummary(params),
    select: (res) => res?.data,
  })
}

export function useResponseTime() {
  return useQuery({
    queryKey: ['analytics', 'response-time'],
    queryFn: () => analyticsService.getResponseTime(),
    select: (res) => res?.data,
  })
}

export function useResourceUtilization() {
  return useQuery({
    queryKey: ['analytics', 'resource-utilization'],
    queryFn: () => analyticsService.getResourceUtilization(),
    select: (res) => res?.data,
  })
}
