export type UserRole =
  | 'CITIZEN'
  | 'AUTHORITY'
  | 'NGO'
  | 'VOLUNTEER'
  | 'DISTRICT_OFFICER'
  | 'STATE_OFFICER'
  | 'ADMIN'

export interface NotificationPreferences {
  pushEnabled: boolean
  smsEnabled: boolean
  emailEnabled: boolean
  language: string
}

export interface EmergencyContact {
  name: string
  phone: string
  relationship: string
}

export interface User {
  uid: string
  email: string
  displayName: string
  phoneNumber?: string
  role: UserRole
  district: string
  state: string
  pincode?: string
  isVerified: boolean
  isActive: boolean
  hasDisability?: boolean
  disabilityDetails?: string
  organizationId?: string
  organizationName?: string
  designation?: string
  badgeNumber?: string
  address?: string
  emergencyContacts: EmergencyContact[]
  notificationPreferences: NotificationPreferences
  mfaEnabled: boolean
  createdAt?: string
  updatedAt?: string
  lastLoginAt?: string
}

export interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  isAuthenticated: boolean
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  displayName: string
  phoneNumber?: string
  district: string
  state: string
  role: UserRole
  address?: string
}

export interface TokenResponse {
  uid: string
  token: string
  refreshToken: string
  expiresIn: number
  user: User
}

export interface RefreshTokenRequest {
  refreshToken: string
}

export interface ForgotPasswordRequest {
  email: string
}

export interface UpdateProfileRequest {
  displayName?: string
  phoneNumber?: string
  district?: string
  state?: string
  address?: string
  notificationPreferences?: Partial<NotificationPreferences>
  emergencyContacts?: EmergencyContact[]
}
