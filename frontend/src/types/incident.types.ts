export type IncidentType =
  | 'FLOOD'
  | 'CYCLONE'
  | 'EARTHQUAKE'
  | 'LANDSLIDE'
  | 'FIRE'
  | 'MEDICAL'
  | 'INDUSTRIAL'
  | 'DROUGHT'
  | 'CIVIL_UNREST'
  | 'OTHER'

export type IncidentStatus =
  | 'DRAFT'
  | 'SUBMITTED'
  | 'AI_PROCESSING'
  | 'TRIAGED'
  | 'ASSIGNED'
  | 'IN_PROGRESS'
  | 'RESOLVED'
  | 'CLOSED'
  | 'ARCHIVED'

export type UrgencyLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

export type SeverityBand = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

export type ResourceUrgency = 'IMMEDIATE' | 'HIGH' | 'MEDIUM' | 'LOW'

export type AiFeedback = 'ACCEPTED' | 'OVERRIDDEN'

export type ResourceAssignmentStatus =
  | 'DISPATCHED'
  | 'EN_ROUTE'
  | 'ON_SCENE'
  | 'RETURNING'

export type IncidentSource = 'WEB' | 'MOBILE' | 'SMS' | 'API'

export type ResolutionOutcome =
  | 'RESCUED'
  | 'FALSE_ALARM'
  | 'REFERRED'
  | 'DECEASED'

export type LocationMethod = 'GPS' | 'MANUAL' | 'IP'

export interface Coordinates {
  latitude: number
  longitude: number
}

export interface IncidentLocation {
  address: string
  district: string
  state: string
  pincode?: string
  coordinates: Coordinates
  geohash?: string
  accuracy?: number
  locationMethod?: LocationMethod
}

export interface MediaFile {
  fileId: string
  url: string
  type: 'image' | 'video' | 'audio' | 'document'
  filename: string
  size: number
  uploadedAt?: string
}

export interface ResourceRecommendation {
  resourceType: string
  quantity: number
  urgency: ResourceUrgency
  reason: string
}

export interface AIAnalysis {
  analysisId: string
  processedAt?: string
  modelVersion: string
  classifiedType?: IncidentType
  classificationConfidence?: number
  severityScore?: number
  severityBand?: SeverityBand
  priorityRank?: number
  priorityScore?: number
  resourceRecommendations: ResourceRecommendation[]
  situationSummary?: string
  reasoning: string[]
  immediateActions: string[]
  risks: string[]
  isDuplicate: boolean
  duplicateOf?: string
  duplicateScore?: number
  dataQuality?: string
  dataQualityNote?: string
  fallbackUsed: boolean
  authorityFeedback?: AiFeedback
  feedbackNote?: string
}

export interface AssignedResource {
  resourceId: string
  resourceName: string
  resourceType: string
  assignedAt?: string
  status: ResourceAssignmentStatus
}

export interface Assignment {
  authorityId?: string
  authorityName?: string
  assignedAt?: string
  resources: AssignedResource[]
}

export interface Escalation {
  isEscalated: boolean
  escalatedAt?: string
  escalatedBy?: string
  escalatedTo?: string
  escalationReason?: string
  escalationCount: number
}

export interface Resolution {
  resolvedAt?: string
  resolvedBy?: string
  resolutionNote?: string
  outcome?: ResolutionOutcome
}

export interface IncidentListItem {
  /** Firestore document ID — used as URL param in authority routes */
  _firestoreId?: string
  incidentId: string
  title: string
  incidentType: IncidentType
  status: IncidentStatus
  urgencyLevel: UrgencyLevel
  severityScore?: number
  severityBand?: SeverityBand
  priorityRank?: number
  district: string
  state: string
  affectedPeople: number
  createdAt?: string
  reportedBy?: string
  reporterName?: string
}

export interface IncidentResponse {
  incidentId: string
  title: string
  description: string
  incidentType: IncidentType
  status: IncidentStatus
  urgencyLevel: UrgencyLevel
  affectedPeople: number
  fatalities?: number
  injuries?: number
  isAnonymous: boolean
  location: IncidentLocation
  mediaFiles: MediaFile[]
  aiAnalysis?: AIAnalysis
  assignedTo: Assignment
  escalation: Escalation
  resolution: Resolution
  linkedIncidents: string[]
  source: IncidentSource
  reportedBy: string
  reporterName?: string
  reporterPhone?: string
  responseTimeMinutes?: number
  version: number
  createdAt?: string
  updatedAt?: string
}

export interface IncidentCreate {
  title: string
  description: string
  incidentType: IncidentType
  urgencyLevel: UrgencyLevel
  affectedPeople: number
  location: IncidentLocation
  fatalities?: number
  injuries?: number
  isAnonymous?: boolean
  source?: IncidentSource
}

export interface SOSCreate {
  coordinates: Coordinates
  description?: string
  phoneNumber?: string
}

export interface IncidentStatusUpdate {
  status: IncidentStatus
  note?: string
}

export interface IncidentAssign {
  authorityId: string
  resourceIds: string[]
}

export interface IncidentEscalate {
  reason: string
  escalateTo: string
}

export interface IncidentComment {
  content: string
  isInternal?: boolean
}

export interface IncidentCommentResponse {
  commentId: string
  authorId: string
  authorName: string
  authorRole: string
  content: string
  isInternal: boolean
  createdAt?: string
  updatedAt?: string
}

export interface AIFeedbackRequest {
  feedback: AiFeedback
  classificationCorrect?: boolean
  severityAccurate?: boolean
  recommendationsUseful?: boolean
  summaryAccurate?: boolean
  comment?: string
}

export interface IncidentFilters {
  district?: string
  status?: IncidentStatus
  type?: IncidentType
  severity?: SeverityBand
  from?: string
  to?: string
  sort?: 'severity' | 'date'
  page?: number
  limit?: number
}

export interface PaginatedResponse<T> {
  incidents?: T[]
  pagination: {
    total: number
    page: number
    limit: number
    totalPages: number
  }
}

export interface IncidentCreateResponse {
  incidentId: string
  status: IncidentStatus
  message: string
  estimatedResponseTime: string
  trackingUrl: string
}
