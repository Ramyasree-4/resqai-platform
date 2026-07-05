import type { SeverityBand, IncidentType, IncidentStatus, UserRole } from '@/types'

export const API_ENDPOINTS = {
  // Auth
  AUTH_LOGIN: '/auth/login',
  AUTH_REGISTER: '/auth/register',
  AUTH_LOGOUT: '/auth/logout',
  AUTH_REFRESH: '/auth/refresh',
  AUTH_ME: '/auth/me',
  AUTH_PROFILE: '/auth/profile',
  AUTH_FORGOT_PASSWORD: '/auth/forgot-password',
  AUTH_FCM_TOKEN: '/auth/fcm-token',

  // Incidents
  INCIDENTS: '/incidents',
  INCIDENTS_MY: '/incidents/my',
  INCIDENTS_SOS: '/incidents/sos',
  INCIDENT_BY_ID: (id: string) => `/incidents/${id}`,
  INCIDENT_STATUS: (id: string) => `/incidents/${id}/status`,
  INCIDENT_ASSIGN: (id: string) => `/incidents/${id}/assign`,
  INCIDENT_ESCALATE: (id: string) => `/incidents/${id}/escalate`,
  INCIDENT_COMMENTS: (id: string) => `/incidents/${id}/comments`,
  INCIDENT_MEDIA: (id: string) => `/incidents/${id}/media`,

  // AI
  AI_ANALYSIS: (id: string) => `/ai/analysis/${id}`,
  AI_FEEDBACK: (id: string) => `/ai/feedback/${id}`,

  // Resources
  RESOURCES: '/resources',
  RESOURCES_NEARBY: '/resources/nearby',
  RESOURCE_BY_ID: (id: string) => `/resources/${id}`,
  RESOURCE_STATUS: (id: string) => `/resources/${id}/status`,
  RESOURCE_LOCATION: (id: string) => `/resources/${id}/location`,

  // Dashboard
  DASHBOARD_STATS: '/dashboard/stats',
  DASHBOARD_MAP: '/dashboard/map-data',
  DASHBOARD_TREND: '/dashboard/incident-trend',

  // Analytics
  ANALYTICS_SUMMARY: '/analytics/summary',
  ANALYTICS_RESPONSE_TIME: '/analytics/response-time',
  ANALYTICS_RESOURCE_UTIL: '/analytics/resource-utilization',
  ANALYTICS_EXPORT: '/analytics/export',

  // Notifications
  NOTIFICATIONS: '/notifications',
  NOTIFICATION_READ: (id: string) => `/notifications/${id}/read`,
  NOTIFICATIONS_READ_ALL: '/notifications/read-all',
  NOTIFICATIONS_BROADCAST: '/notifications/broadcast',

  // Admin
  ADMIN_USERS: '/admin/users',
  ADMIN_STATS: '/admin/system-stats',
  ADMIN_AUDIT: '/admin/audit-logs',
} as const

export const SEVERITY_COLORS: Record<SeverityBand, { bg: string; text: string; border: string; dot: string }> = {
  CRITICAL: {
    bg: 'bg-red-100 dark:bg-red-900/30',
    text: 'text-red-700 dark:text-red-400',
    border: 'border-red-200 dark:border-red-800',
    dot: 'bg-red-600',
  },
  HIGH: {
    bg: 'bg-orange-100 dark:bg-orange-900/30',
    text: 'text-orange-700 dark:text-orange-400',
    border: 'border-orange-200 dark:border-orange-800',
    dot: 'bg-orange-500',
  },
  MEDIUM: {
    bg: 'bg-yellow-100 dark:bg-yellow-900/30',
    text: 'text-yellow-700 dark:text-yellow-400',
    border: 'border-yellow-200 dark:border-yellow-800',
    dot: 'bg-yellow-500',
  },
  LOW: {
    bg: 'bg-green-100 dark:bg-green-900/30',
    text: 'text-green-700 dark:text-green-400',
    border: 'border-green-200 dark:border-green-800',
    dot: 'bg-green-500',
  },
}

export const INCIDENT_TYPE_LABELS: Record<IncidentType, { label: string; emoji: string }> = {
  FLOOD: { label: 'Flood', emoji: '🌊' },
  CYCLONE: { label: 'Cyclone', emoji: '🌪️' },
  EARTHQUAKE: { label: 'Earthquake', emoji: '⚡' },
  LANDSLIDE: { label: 'Landslide', emoji: '🏔️' },
  FIRE: { label: 'Fire', emoji: '🔥' },
  MEDICAL: { label: 'Medical', emoji: '🏥' },
  INDUSTRIAL: { label: 'Industrial', emoji: '🏭' },
  DROUGHT: { label: 'Drought', emoji: '☀️' },
  CIVIL_UNREST: { label: 'Civil Unrest', emoji: '⚠️' },
  OTHER: { label: 'Other', emoji: '➕' },
}

export const STATUS_LABELS: Record<IncidentStatus, { label: string; color: string }> = {
  DRAFT: { label: 'Draft', color: 'bg-gray-100 text-gray-600' },
  SUBMITTED: { label: 'Submitted', color: 'bg-blue-100 text-blue-700' },
  AI_PROCESSING: { label: 'AI Processing', color: 'bg-purple-100 text-purple-700' },
  TRIAGED: { label: 'Triaged', color: 'bg-indigo-100 text-indigo-700' },
  ASSIGNED: { label: 'Assigned', color: 'bg-orange-100 text-orange-700' },
  IN_PROGRESS: { label: 'In Progress', color: 'bg-yellow-100 text-yellow-700' },
  RESOLVED: { label: 'Resolved', color: 'bg-green-100 text-green-700' },
  CLOSED: { label: 'Closed', color: 'bg-gray-100 text-gray-500' },
  ARCHIVED: { label: 'Archived', color: 'bg-gray-100 text-gray-400' },
}

export const USER_ROLES: Record<UserRole, string> = {
  CITIZEN: 'Citizen',
  AUTHORITY: 'Authority',
  NGO: 'NGO',
  VOLUNTEER: 'Volunteer',
  DISTRICT_OFFICER: 'District Officer',
  STATE_OFFICER: 'State Officer',
  ADMIN: 'Admin',
}

export const AUTHORITY_ROLES: UserRole[] = [
  'AUTHORITY',
  'DISTRICT_OFFICER',
  'STATE_OFFICER',
  'ADMIN',
]

export const INDIA_CENTER = { lat: 20.5937, lng: 78.9629 }

export const RESOURCE_TYPE_ICONS: Record<string, string> = {
  RESCUE_TEAM: '🚑',
  AMBULANCE: '🚑',
  FIRE_TRUCK: '🚒',
  RESCUE_BOAT: '⛵',
  HELICOPTER: '🚁',
  POLICE_UNIT: '🚔',
  MEDICAL_UNIT: '🏥',
  NGO_UNIT: '🤝',
  SHELTER: '🏠',
  HOSPITAL: '🏥',
  RELIEF_CAMP: '⛺',
}

export const RESOURCE_STATUS_COLORS: Record<string, string> = {
  AVAILABLE: 'bg-green-100 text-green-700',
  DEPLOYED: 'bg-orange-100 text-orange-700',
  MAINTENANCE: 'bg-yellow-100 text-yellow-700',
  UNAVAILABLE: 'bg-red-100 text-red-700',
}
