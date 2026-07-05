import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { incidentService } from '@/services/incident.service'
import { toast } from 'sonner'
import type {
  IncidentFilters,
  IncidentCreate,
  IncidentStatus,
  IncidentAssign,
  IncidentEscalate,
} from '@/types'

export const incidentKeys = {
  all: ['incidents'] as const,
  lists: () => [...incidentKeys.all, 'list'] as const,
  list: (filters?: IncidentFilters) => [...incidentKeys.lists(), filters] as const,
  my: () => [...incidentKeys.all, 'my'] as const,
  priority: () => [...incidentKeys.all, 'priority'] as const,
  detail: (id: string) => [...incidentKeys.all, 'detail', id] as const,
  comments: (id: string) => [...incidentKeys.all, 'comments', id] as const,
}

/**
 * Returns { data: { data: { items, pagination } } }
 * Pages access: data?.data?.items and data?.data?.pagination
 */
export function useIncidents(filters?: IncidentFilters) {
  return useQuery({
    queryKey: incidentKeys.list(filters),
    queryFn: () => incidentService.getIncidents(filters),
  })
}

export function useIncident(id: string) {
  return useQuery({
    queryKey: incidentKeys.detail(id),
    queryFn: () => incidentService.getIncidentById(id),
    enabled: !!id,
  })
}

export function useMyIncidents() {
  return useQuery({
    queryKey: incidentKeys.my(),
    queryFn: () => incidentService.getMyIncidents(),
    // returns IncidentListItem[]
  })
}

export function usePriorityQueue() {
  return useQuery({
    queryKey: incidentKeys.priority(),
    queryFn: () => incidentService.getPriorityQueue(),
    refetchInterval: 60000,
  })
}

export function useIncidentComments(id: string) {
  return useQuery({
    queryKey: incidentKeys.comments(id),
    queryFn: () => incidentService.getComments(id),
    enabled: !!id,
  })
}

export function useCreateIncident() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: IncidentCreate) => incidentService.createIncident(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: incidentKeys.lists() })
      qc.invalidateQueries({ queryKey: incidentKeys.my() })
    },
    onError: () => toast.error('Failed to submit incident report'),
  })
}

export function useUpdateStatus() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, status, note }: { id: string; status: IncidentStatus; note?: string }) =>
      incidentService.updateStatus(id, { status, note }),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: incidentKeys.detail(id) })
      qc.invalidateQueries({ queryKey: incidentKeys.lists() })
      qc.invalidateQueries({ queryKey: incidentKeys.priority() })
    },
    onError: () => toast.error('Failed to update status'),
  })
}

export function useAssignIncident() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({
      id,
      authorityId,
      resourceIds,
    }: {
      id: string
      authorityId: string
      resourceIds: string[]
    }) => incidentService.assignIncident(id, { authorityId, resourceIds }),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: incidentKeys.detail(id) })
      qc.invalidateQueries({ queryKey: incidentKeys.lists() })
      toast.success('Resources assigned successfully')
    },
    onError: () => toast.error('Failed to assign resources'),
  })
}

export function useEscalateIncident() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: IncidentEscalate }) =>
      incidentService.escalateIncident(id, data),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: incidentKeys.detail(id) })
      toast.success('Incident escalated')
    },
    onError: () => toast.error('Failed to escalate incident'),
  })
}

export function useAddComment(incidentId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: { content: string; isInternal?: boolean }) =>
      incidentService.addComment(incidentId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: incidentKeys.comments(incidentId) }),
    onError: () => toast.error('Failed to add comment'),
  })
}
