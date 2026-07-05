import api from './api'
import { API_ENDPOINTS } from '@/utils/constants'
import type {
  ResourceResponse,
  ResourceCreate,
  ResourceUpdate,
  ResourceStatusUpdate,
  ResourceLocationUpdate,
  ResourceNearby,
  ResourceFilters,
} from '@/types'

interface ApiResponse<T> {
  success: boolean
  data: T
}

interface PaginatedResources {
  resources: ResourceResponse[]
  pagination: {
    total: number
    page: number
    limit: number
    totalPages: number
  }
}

export const resourceService = {
  async getResources(filters?: ResourceFilters): Promise<PaginatedResources> {
    const res = await api.get<ApiResponse<PaginatedResources>>(
      API_ENDPOINTS.RESOURCES,
      { params: filters }
    )
    return res.data.data
  },

  async createResource(data: ResourceCreate): Promise<ResourceResponse> {
    const res = await api.post<ApiResponse<ResourceResponse>>(
      API_ENDPOINTS.RESOURCES,
      data
    )
    return res.data.data
  },

  async getResourceById(id: string): Promise<ResourceResponse> {
    const res = await api.get<ApiResponse<ResourceResponse>>(
      API_ENDPOINTS.RESOURCE_BY_ID(id)
    )
    return res.data.data
  },

  async updateResource(id: string, data: ResourceUpdate): Promise<ResourceResponse> {
    const res = await api.put<ApiResponse<ResourceResponse>>(
      API_ENDPOINTS.RESOURCE_BY_ID(id),
      data
    )
    return res.data.data
  },

  async updateResourceStatus(id: string, data: ResourceStatusUpdate): Promise<void> {
    await api.put(API_ENDPOINTS.RESOURCE_STATUS(id), data)
  },

  async updateResourceLocation(id: string, data: ResourceLocationUpdate): Promise<void> {
    await api.put(API_ENDPOINTS.RESOURCE_LOCATION(id), data)
  },

  async getNearbyResources(
    lat: number,
    lng: number,
    radius = 50,
    type?: string
  ): Promise<ResourceNearby[]> {
    const res = await api.get<ApiResponse<{ resources: ResourceNearby[] }>>(
      API_ENDPOINTS.RESOURCES_NEARBY,
      { params: { lat, lng, radiusKm: radius, type, status: 'AVAILABLE' } }
    )
    return res.data.data.resources
  },

  async deleteResource(id: string): Promise<void> {
    await api.delete(API_ENDPOINTS.RESOURCE_BY_ID(id))
  },
}
