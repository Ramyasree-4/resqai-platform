import api from './api'
import { API_ENDPOINTS } from '@/utils/constants'
import type {
  IncidentCreate,
  IncidentCreateResponse,
  IncidentResponse,
  IncidentListItem,
  IncidentFilters,
  IncidentStatusUpdate,
  IncidentAssign,
  IncidentEscalate,
  IncidentComment,
  IncidentCommentResponse,
  AIFeedbackRequest,
  SOSCreate,
  PaginatedResponse,
} from '@/types'

interface ApiResponse<T> {
  success: boolean
  data: T
}

export const incidentService = {
  async createIncident(data: IncidentCreate): Promise<IncidentCreateResponse> {
    const res = await api.post<ApiResponse<IncidentCreateResponse>>(
      API_ENDPOINTS.INCIDENTS,
      data
    )
    return res.data.data
  },

  async getIncidents(
    filters?: IncidentFilters
  ): Promise<ApiResponse<{ items: IncidentListItem[]; pagination: PaginatedResponse<IncidentListItem>['pagination'] }>> {
    const res = await api.get<ApiResponse<{
      items?: IncidentListItem[]
      incidents?: IncidentListItem[]
      pagination: PaginatedResponse<IncidentListItem>['pagination']
    }>>(API_ENDPOINTS.INCIDENTS, { params: filters })
    const d = res.data.data
    return {
      success: res.data.success,
      data: {
        items: d.items ?? d.incidents ?? [],
        pagination: d.pagination,
      },
    }
  },

  async getIncidentById(id: string): Promise<IncidentResponse> {
    const res = await api.get<ApiResponse<IncidentResponse>>(
      API_ENDPOINTS.INCIDENT_BY_ID(id)
    )
    return res.data.data
  },

  async getMyIncidents(
    page = 1,
    limit = 50
  ): Promise<IncidentListItem[]> {
    const res = await api.get<ApiResponse<{
      items?: IncidentListItem[]
      incidents?: IncidentListItem[]
      pagination: PaginatedResponse<IncidentListItem>['pagination']
    }>>(API_ENDPOINTS.INCIDENTS_MY, { params: { page, limit } })
    const d = res.data.data
    return d.items ?? d.incidents ?? []
  },

  async getPriorityQueue(): Promise<IncidentListItem[]> {
    const res = await api.get<ApiResponse<{
      items?: IncidentListItem[]
      incidents?: IncidentListItem[]
      pagination: PaginatedResponse<IncidentListItem>['pagination']
    }>>(API_ENDPOINTS.INCIDENTS, {
      params: { sort: 'severity', limit: 20 },
    })
    const d = res.data.data
    return d.items ?? d.incidents ?? []
  },

  async updateStatus(id: string, data: IncidentStatusUpdate): Promise<void> {
    await api.put(API_ENDPOINTS.INCIDENT_STATUS(id), data)
  },

  async assignIncident(id: string, data: IncidentAssign): Promise<void> {
    await api.put(API_ENDPOINTS.INCIDENT_ASSIGN(id), data)
  },

  async escalateIncident(id: string, data: IncidentEscalate): Promise<void> {
    await api.post(API_ENDPOINTS.INCIDENT_ESCALATE(id), data)
  },

  async addComment(id: string, data: IncidentComment): Promise<IncidentCommentResponse> {
    const res = await api.post<ApiResponse<IncidentCommentResponse>>(
      API_ENDPOINTS.INCIDENT_COMMENTS(id),
      data
    )
    return res.data.data
  },

  async getComments(id: string): Promise<IncidentCommentResponse[]> {
    const res = await api.get<ApiResponse<IncidentCommentResponse[]>>(
      API_ENDPOINTS.INCIDENT_COMMENTS(id)
    )
    return res.data.data
  },

  async submitSOS(data: SOSCreate): Promise<IncidentCreateResponse> {
    const res = await api.post<ApiResponse<IncidentCreateResponse>>(
      API_ENDPOINTS.INCIDENTS_SOS,
      data
    )
    return res.data.data
  },

  async submitAIFeedback(analysisId: string, data: AIFeedbackRequest): Promise<void> {
    await api.post(API_ENDPOINTS.AI_FEEDBACK(analysisId), data)
  },

  async uploadMedia(
    id: string,
    files: File[]
  ): Promise<{ uploaded: { fileId: string; url: string; type: string }[] }> {
    const formData = new FormData()
    files.forEach((file) => formData.append('files', file))
    const res = await api.post<ApiResponse<{ uploaded: { fileId: string; url: string; type: string }[] }>>(
      API_ENDPOINTS.INCIDENT_MEDIA(id),
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
    return res.data.data
  },
}
