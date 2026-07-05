import { useParams, Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, MapPin, Users, Clock, AlertTriangle, MessageCircle, Send, ChevronDown } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'
import { useIncident, useUpdateStatus, useAssignIncident } from '@/hooks/useIncidents'
import { useResources } from '@/hooks/useResources'
import { AIAnalysisPanel } from '@/components/incident/AIAnalysisPanel'
import { IncidentTimeline } from '@/components/incident/IncidentTimeline'
import { ResourceAssignmentPanel } from '@/components/incident/ResourceAssignmentPanel'
import { SeverityBadge } from '@/components/ui/SeverityBadge'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { SkeletonCard } from '@/components/ui/LoadingSpinner'
import { incidentService } from '@/services/incident.service'
import { formatRelativeTime } from '@/utils/formatters'
import { INCIDENT_TYPE_LABELS } from '@/utils/constants'
import { useAuth } from '@/hooks/useAuth'
import type { IncidentStatus } from '@/types'

const NEXT_STATUSES: Record<string, IncidentStatus[]> = {
  TRIAGED: ['ASSIGNED'],
  ASSIGNED: ['IN_PROGRESS'],
  IN_PROGRESS: ['RESOLVED'],
  RESOLVED: ['CLOSED'],
}

export default function IncidentDetailsPage() {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const navigate = useNavigate()
  const { data: incident, isLoading, refetch } = useIncident(id!)
  const { data: resourcesData } = useResources({ limit: 50 })
  const updateStatus = useUpdateStatus()
  const assignIncident = useAssignIncident()
  const [comment, setComment] = useState('')
  const [sendingComment, setSendingComment] = useState(false)
  const [statusNote, setStatusNote] = useState('')

  if (isLoading) return <div className="space-y-4">{Array.from({length:3}).map((_,i)=><SkeletonCard key={i}/>)}</div>
  if (!incident) return <div className="text-center py-20 text-gray-500">Incident not found</div>

  const typeInfo = INCIDENT_TYPE_LABELS[incident.incidentType] || { emoji:'⚠️', label: incident.incidentType }
  const nextStatuses = NEXT_STATUSES[incident.status] || []
  const resources = resourcesData?.data?.items || []

  const handleStatusUpdate = async (newStatus: IncidentStatus) => {
    try {
      await updateStatus.mutateAsync({ id: id!, status: newStatus, note: statusNote })
      toast.success(`Status updated to ${newStatus}`)
      refetch()
    } catch { toast.error('Failed to update status') }
  }

  const handleAssign = async (resourceIds: string[]) => {
    try {
      await assignIncident.mutateAsync({ id: id!, authorityId: user!.uid, resourceIds })
      toast.success(`${resourceIds.length} resource(s) dispatched`)
      refetch()
    } catch { toast.error('Assignment failed') }
  }

  const handleAIFeedback = async (positive: boolean) => {
    try {
      await incidentService.submitAIFeedback(id!, { feedback: positive ? 'ACCEPTED' : 'OVERRIDDEN' })
      toast.success('Feedback recorded')
    } catch {}
  }

  const sendComment = async () => {
    if (!comment.trim()) return
    setSendingComment(true)
    try {
      await incidentService.addComment(id!, { content: comment, isInternal: true })
      setComment('')
      toast.success('Note added')
    } catch { toast.error('Failed') }
    finally { setSendingComment(false) }
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-3 flex-wrap">
        <Link to="/authority/incidents" className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-blue-600 transition-colors">
          <ArrowLeft className="h-4 w-4" /> Incident Queue
        </Link>
        <span className="text-gray-300">·</span>
        <span className="font-mono text-sm text-gray-600 dark:text-gray-400">{incident.incidentId}</span>
        <div className="flex items-center gap-2">
          {incident.aiAnalysis?.severityBand && <SeverityBadge band={incident.aiAnalysis.severityBand} score={incident.aiAnalysis.severityScore} />}
          <StatusBadge status={incident.status} />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        {/* LEFT: Incident Info */}
        <div className="space-y-6 lg:col-span-3">
          {/* Main card */}
          <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 shadow-sm">
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gray-50 dark:bg-gray-700 text-2xl">{typeInfo.emoji}</div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">{incident.title}</h1>
                <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-500 dark:text-gray-400">
                  <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5"/>{incident.location.address}</span>
                  <span className="flex items-center gap-1"><Users className="h-3.5 w-3.5"/>{incident.affectedPeople} affected</span>
                  <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5"/>{formatRelativeTime(incident.createdAt)}</span>
                </div>
              </div>
            </div>
            <p className="mt-4 text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{incident.description}</p>

            {/* Media */}
            {incident.mediaFiles.length > 0 && (
              <div className="mt-4 grid grid-cols-4 gap-2">
                {incident.mediaFiles.map((f, i) => (
                  <a key={i} href={f.url} target="_blank" rel="noopener noreferrer"
                    className="aspect-square overflow-hidden rounded-lg bg-gray-100 dark:bg-gray-700">
                    {f.type === 'image' ? <img src={f.url} alt="" className="h-full w-full object-cover" /> : <div className="flex h-full items-center justify-center text-2xl">🎬</div>}
                  </a>
                ))}
              </div>
            )}

            {/* Reporter */}
            {!incident.isAnonymous && incident.reporterName && (
              <div className="mt-4 flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <span>Reported by:</span>
                <span className="font-medium text-gray-700 dark:text-gray-300">{incident.reporterName}</span>
              </div>
            )}
          </div>

          {/* Status Update */}
          {nextStatuses.length > 0 && (
            <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 shadow-sm">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Update Status</h3>
              <input
                value={statusNote} onChange={e => setStatusNote(e.target.value)}
                placeholder="Optional note (e.g., NDRF Team dispatched, ETA 20 min)"
                className="w-full mb-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
              />
              <div className="flex gap-2">
                {nextStatuses.map(s => (
                  <button key={s} onClick={() => handleStatusUpdate(s)} disabled={updateStatus.isPending}
                    className="flex-1 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white py-2 text-sm font-semibold transition-colors">
                    → {s.replace('_', ' ')}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Comments */}
          <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 shadow-sm">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
              <MessageCircle className="inline h-4 w-4 mr-1.5" />Internal Notes
            </h3>
            <div className="flex gap-2">
              <input value={comment} onChange={e => setComment(e.target.value)}
                placeholder="Add coordination note…"
                className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white"
                onKeyDown={e => e.key === 'Enter' && sendComment()}
              />
              <button onClick={sendComment} disabled={!comment.trim() || sendingComment}
                className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white transition-colors">
                <Send className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        {/* RIGHT: AI + Resources + Timeline */}
        <div className="space-y-6 lg:col-span-2">
          {incident.aiAnalysis ? (
            <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">AI Analysis</h3>
              <AIAnalysisPanel
                analysis={incident.aiAnalysis}
                onFeedback={handleAIFeedback}
                onAccept={() => handleAIFeedback(true)}
              />
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-gray-300 dark:border-gray-700 p-6 text-center">
              <AlertTriangle className="h-6 w-6 text-gray-400 mx-auto mb-2" />
              <p className="text-sm text-gray-500">AI analysis pending</p>
            </div>
          )}

          {/* Resource Assignment */}
          <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 shadow-sm">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Assign Resources</h3>
            <ResourceAssignmentPanel
              resources={resources}
              onAssign={handleAssign}
              incidentId={id!}
            />
          </div>

          {/* Timeline */}
          <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 shadow-sm">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">Status Timeline</h3>
            <IncidentTimeline
              entries={[{ toStatus: incident.status, changedBy: incident.reportedBy, changedAt: incident.createdAt, note: 'Incident submitted' }]}
              currentStatus={incident.status}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
