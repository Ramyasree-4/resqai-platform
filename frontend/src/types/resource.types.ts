import type { Coordinates } from './incident.types'

export type ResourceType =
  | 'RESCUE_TEAM'
  | 'AMBULANCE'
  | 'FIRE_TRUCK'
  | 'RESCUE_BOAT'
  | 'HELICOPTER'
  | 'POLICE_UNIT'
  | 'MEDICAL_UNIT'
  | 'NGO_UNIT'
  | 'SHELTER'
  | 'HOSPITAL'
  | 'RELIEF_CAMP'

export type ResourceStatus =
  | 'AVAILABLE'
  | 'DEPLOYED'
  | 'MAINTENANCE'
  | 'UNAVAILABLE'

export type ResourceAssignmentStatus =
  | 'DISPATCHED'
  | 'EN_ROUTE'
  | 'ON_SCENE'
  | 'RETURNING'

export interface ResourceCapacity {
  total?: number
  current?: number
  available?: number
}

export interface ResourceBaseLocation {
  address: string
  district: string
  coordinates: Coordinates
}

export interface ResourceCurrentLocation {
  coordinates: Coordinates
  updatedAt?: string
  updatedBy: string
}

export interface ResourceCurrentAssignment {
  incidentId?: string
  incidentTitle?: string
  assignedAt?: string
  estimatedReturn?: string
}

export interface ResourceResponse {
  /** Firestore document ID */
  _firestoreId?: string
  resourceId: string
  name: string
  type: ResourceType
  subType?: string
  organizationId: string
  organizationName: string
  district: string
  state: string
  contactName: string
  contactPhone: string
  contactEmail?: string
  status: ResourceStatus
  statusUpdatedAt?: string
  capacity?: ResourceCapacity
  currentAssignment: ResourceCurrentAssignment
  baseLocation: ResourceBaseLocation
  currentLocation?: ResourceCurrentLocation
  capabilities: string[]
  isActive: boolean
  notes?: string
  registeredAt?: string
  updatedAt?: string
}

export interface ResourceCreate {
  name: string
  type: ResourceType
  subType?: string
  organizationId: string
  organizationName: string
  district: string
  state: string
  contactName: string
  contactPhone: string
  contactEmail?: string
  capabilities: string[]
  baseLocation: ResourceBaseLocation
  capacity?: ResourceCapacity
  notes?: string
}

export interface ResourceUpdate {
  name?: string
  contactName?: string
  contactPhone?: string
  contactEmail?: string
  capabilities?: string[]
  capacity?: ResourceCapacity
  notes?: string
}

export interface ResourceStatusUpdate {
  status: ResourceStatus
  note?: string
}

export interface ResourceLocationUpdate {
  coordinates: Coordinates
  updatedBy?: string
}

export interface ResourceNearby {
  resourceId: string
  name: string
  type: ResourceType
  status: ResourceStatus
  distanceKm: number
  estimatedArrivalMinutes: number
  coordinates?: Coordinates
}

export interface ResourceFilters {
  district?: string
  type?: ResourceType
  status?: ResourceStatus
  page?: number
  limit?: number
}
