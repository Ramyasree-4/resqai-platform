import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, MapPin, Users, Clock, MessageCircle, Send } from 'lucide-react'
import { useState } from 'react'
import { useIncident } from '@/hooks/useIncidents'
import { incidentService } from '@/services/incident.service'
import { AIAnalysisPanel } from '@/components/incident/AIAnalysisPanel'
import { IncidentTimeline } from '@/components/incident/IncidentTimeline'
import { SeverityBadge } from '@/components/ui/SeverityBadge'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { SkeletonCard } from '@/components/ui/LoadingSpinner'
import { formatRelativeTime } from '@/utils/formatters'
import { INCIDENT_TYPE_LABELS } from '@/utils/constants'
import { toast } from 'sonner'

export default function IncidentTrackerPage() {
  const { id } = useParams<{ id: string }>()
  const { data: incident, isLoading } = useIncident(id!)
  const [comment, setComment] = useState('')
  const [sending, setSending] = useState(false)

  const sendComment = async () => {
    if (!comment.trim() || !id) return
    setSending(true)
    try {
      await incidentService.addComment(id, { content: comment, isInternal: false })
      setComment('')
      toast.success('Comment sent')
    } catch { toast.error('Failed to send') }
    finally { setSending(false) }
  }

  if (isLoading) return (
    <div className="space-y-4"><SkeletonCard /><SkeletonCard /></div>
  )
  if (!incident) return (
    <div className="text-center py-20 text-gray-500">Incident not found.</div>
  )

  const typeInfo = INCIDENT_TYPE_LABELS[incident.incidentType] || { emoji: '⚠️', label: incident.incidentType }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/my-reports" className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-blue-600 transition-colors">
          <ArrowLeft className="h-4 w-4" /> My Reports
        </Link>
        <span className="text-gray-300">·</span>
        <span className="font-mono text-sm text-gray-600 dark:text-gray-400">{incident.incidentId}</span>
      </div>

      {/* Summary card */}
      <div className="rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 shadow-sm">
        <div className="flex items-start gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gray-50 dark:bg-gray-700 text-2xl">
            {typeInfo.emoji}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-1">
              {incident.aiAnalysis?.severityBand && (
                <SeverityBadge band={incident.aiAnalysis.severityBand} score={incident.aiAnalysis.severityScore} />
              )}
              <StatusBadge status={incident.status} />
            </div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">{incident.title}</h1>
            <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-500 dark:text-gray-400">
              <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" />{incident.location.district}, {incident.location.state}</span>
              <span className="flex items-center gap-1"><Users className="h-3.5 w-3.5" />{incident.affectedPeople} affected</span>
              <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" />{formatRelativeTime(incident.createdAt)}</span>
            </div>
          </div>
        </div>
        <p className="mt-4 text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{incident.description}</p>

        {/* Assignment */}
        {incident.assignedTo?.authorityId && (
          <div className="mt-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 p-3">
            <p className="text-xs font-semibold text-blue-700 dark:text-blue-400 mb-1">Assigned Response Team</p>
            <p className="text-sm font-medium text-gray-900 dark:text-white">{incident.assignedTo.authorityName}</p>
            {incident.assignedTo.resources.map((r, i) => (
              <div key={i} className="mt-1 flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                {r.resourceName} — {r.status}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* AI Analysis */}
      {incident.aiAnalysis && (
        <div>
          <h2 className="text-base font-semibold text-gray-900 dark:text-white mb-3">AI Analysis</h2>
          <AIAnalysisPanel analysis={incident.aiAnalysis} readOnly />
        </div>
      )}

      {/* Timeline */}
      <div className="rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 shadow-sm">
        <h2 className="text-base font-semibold text-gray-900 dark:text-white mb-4">Status Timeline</h2>
        <IncidentTimeline
          entries={[{ toStatus: incident.status, changedBy: 'SYSTEM', changedAt: incident.createdAt }]}
          currentStatus={incident.status}
        />
      </div>

      {/* Comments */}
      <div className="rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 shadow-sm">
        <h2 className="text-base font-semibold text-gray-900 dark:text-white mb-4">
          <MessageCircle className="inline h-4 w-4 mr-1.5" />
          Updates & Comments
        </h2>
        <div className="flex gap-3">
          <input
            value={comment} onChange={e => setComment(e.target.value)}
            placeholder="Add a comment or question..."
            className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2.5 text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyDown={e => e.key === 'Enter' && sendComment()}
          />
          <button onClick={sendComment} disabled={!comment.trim() || sending}
            className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white transition-colors">
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
