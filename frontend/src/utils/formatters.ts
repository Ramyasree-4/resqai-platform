import { formatDistanceToNow, format, parseISO } from 'date-fns'
import type { SeverityBand, IncidentStatus, IncidentType } from '@/types'
import { INCIDENT_TYPE_LABELS, STATUS_LABELS } from './constants'

export function formatDate(dateStr: string | undefined, pattern = 'dd MMM yyyy, HH:mm'): string {
  if (!dateStr) return '—'
  try {
    return format(parseISO(dateStr), pattern)
  } catch {
    return dateStr
  }
}

export function formatRelativeTime(dateStr: string | undefined): string {
  if (!dateStr) return '—'
  try {
    return formatDistanceToNow(parseISO(dateStr), { addSuffix: true })
  } catch {
    return dateStr
  }
}

export function formatSeverityBand(band: SeverityBand | string | undefined): string {
  if (!band) return 'Unknown'
  return band.charAt(0) + band.slice(1).toLowerCase()
}

export function formatIncidentStatus(status: IncidentStatus | string | undefined): string {
  if (!status) return 'Unknown'
  return STATUS_LABELS[status as IncidentStatus]?.label ?? status
}

export function formatIncidentType(type: IncidentType | string | undefined): string {
  if (!type) return 'Unknown'
  return INCIDENT_TYPE_LABELS[type as IncidentType]?.label ?? type
}

export function formatDistance(km: number): string {
  if (km < 1) return `${Math.round(km * 1000)}m`
  return `${km.toFixed(1)}km`
}

export function formatNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return n.toString()
}

export function formatResponseTime(minutes: number): string {
  if (minutes < 60) return `${Math.round(minutes)}m`
  const hours = Math.floor(minutes / 60)
  const mins = Math.round(minutes % 60)
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
}

export function formatPercentage(value: number, decimals = 1): string {
  return `${(value * 100).toFixed(decimals)}%`
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

export function formatIncidentId(id: string): string {
  return id.toUpperCase()
}

export function getInitials(name: string): string {
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}
