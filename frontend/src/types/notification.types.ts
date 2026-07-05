export type NotificationType =
  | 'INCIDENT_STATUS'
  | 'NEW_INCIDENT'
  | 'ASSIGNMENT'
  | 'ESCALATION'
  | 'BROADCAST'
  | 'RESOURCE_UPDATE'
  | 'SYSTEM'
  | 'CLUSTER_ALERT'

export type NotificationPriority = 'LOW' | 'NORMAL' | 'HIGH' | 'URGENT'

export interface Notification {
  notificationId: string
  /** Firestore document ID — used for mark-as-read API calls */
  _firestoreId?: string
  recipientId?: string
  type: NotificationType
  title: string
  body: string
  isRead: boolean
  priority: NotificationPriority
  relatedIncidentId?: string
  relatedResourceId?: string
  actionUrl?: string
  createdAt?: string
  readAt?: string
}

export interface NotificationFilters {
  isRead?: boolean
  type?: NotificationType
  page?: number
  limit?: number
}

export interface BroadcastRequest {
  title: string
  body: string
  targetDistrict?: string
  targetState?: string
  channels: ('push' | 'sms' | 'email')[]
  priority: NotificationPriority
}
