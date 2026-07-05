import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { resourceService } from '@/services/resource.service'
import { toast } from 'sonner'
import type { ResourceCreate, ResourceFilters, ResourceStatus, ResourceUpdate } from '@/types'

export const resourceKeys = {
  all: ['resources'] as const,
  list: (filters?: ResourceFilters) => [...resourceKeys.all, 'list', filters] as const,
  detail: (id: string) => [...resourceKeys.all, 'detail', id] as const,
  nearby: (lat: number, lng: number, radius?: number) =>
    [...resourceKeys.all, 'nearby', lat, lng, radius] as const,
}

export function useResources(filters?: ResourceFilters) {
  return useQuery({
    queryKey: resourceKeys.list(filters),
    queryFn: () => resourceService.getResources(filters),
    select: (data) => ({
      data: {
        items: data?.resources ?? [],
        pagination: data?.pagination,
      },
    }),
  })
}

export function useResource(id: string) {
  return useQuery({
    queryKey: resourceKeys.detail(id),
    queryFn: () => resourceService.getResourceById(id),
    enabled: !!id,
  })
}

export function useNearbyResources(lat?: number, lng?: number, radius = 50) {
  return useQuery({
    queryKey: resourceKeys.nearby(lat ?? 0, lng ?? 0, radius),
    queryFn: () => resourceService.getNearbyResources(lat!, lng!, radius),
    enabled: !!lat && !!lng,
  })
}

export function useCreateResource() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: ResourceCreate) => resourceService.createResource(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: resourceKeys.all })
      toast.success('Resource created successfully')
    },
    onError: () => toast.error('Failed to create resource'),
  })
}

export function useUpdateResource() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ResourceUpdate }) =>
      resourceService.updateResource(id, data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: resourceKeys.detail(id) })
      qc.invalidateQueries({ queryKey: resourceKeys.all })
    },
    onError: () => toast.error('Failed to update resource'),
  })
}

export function useUpdateResourceStatus() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, status, note }: { id: string; status: ResourceStatus; note?: string }) =>
      resourceService.updateResourceStatus(id, { status, note }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: resourceKeys.all })
    },
    onError: () => toast.error('Failed to update status'),
  })
}
