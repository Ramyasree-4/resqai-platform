export interface DashboardStats {
  activeIncidents: number
  criticalIncidents: number
  resolvedToday: number
  avgResponseTimeMinutes: number
  resourcesDeployed: number
  resourcesAvailable: number
  pendingAssignment: number
  sosReceived: number
  aiAccuracyRate: number
}

export interface MapIncidentPoint {
  incidentId: string
  title: string
  incidentType: string
  status: string
  latitude: number
  longitude: number
  severityBand?: string
  severityScore?: number
}

export interface MapResourcePoint {
  resourceId: string
  name: string
  type: string
  status: string
  latitude?: number
  longitude?: number
}

export interface HeatmapPoint {
  lat: number
  lng: number
  weight: number
}

export interface MapData {
  incidents: MapIncidentPoint[]
  resources: MapResourcePoint[]
  heatmapData: HeatmapPoint[]
}

export interface IncidentTrendDataset {
  total: number[]
  critical: number[]
  resolved: number[]
}

export interface IncidentTrendData {
  labels: string[]
  datasets: IncidentTrendDataset
}

export interface IncidentTypeBreakdown {
  FLOOD: number
  CYCLONE: number
  EARTHQUAKE: number
  LANDSLIDE: number
  FIRE: number
  MEDICAL: number
  INDUSTRIAL: number
  DROUGHT: number
  CIVIL_UNREST: number
  OTHER: number
}

export interface SeverityBreakdown {
  LOW: number
  MEDIUM: number
  HIGH: number
  CRITICAL: number
}

export interface AnalyticsSummary {
  total: number
  critical: number
  avgResponseTime: number
  aiAccuracyRate: number
  resolvedRate: number
  byType: IncidentTypeBreakdown
  bySeverity: SeverityBreakdown
}

export interface ResponseTimeEntry {
  type: string
  avgMinutes: number
  count: number
}

export interface ResourceUtilizationEntry {
  type: string
  total: number
  deployed: number
  available: number
  utilizationRate: number
}

export interface DashboardParams {
  district?: string
  state?: string
  period?: 'today' | 'week' | 'month'
}

export interface AnalyticsParams {
  district?: string
  state?: string
  from?: string
  to?: string
  granularity?: 'hourly' | 'daily' | 'weekly'
}

export interface TrendParams {
  district?: string
  days?: number
}
