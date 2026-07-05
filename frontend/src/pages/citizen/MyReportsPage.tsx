import { Link } from 'react-router-dom'
import { Plus, FileText } from 'lucide-react'
import { useMyIncidents } from '@/hooks/useIncidents'
import { PageHeader } from '@/components/common/PageHeader'
import { IncidentCard } from '@/components/incident/IncidentCard'
import { EmptyState } from '@/components/ui/EmptyState'
import { SkeletonCard } from '@/components/ui/LoadingSpinner'

export default function MyReportsPage() {
  const { data: incidents, isLoading } = useMyIncidents()

  return (
    <div>
      <PageHeader
        title="My Reports"
        subtitle="All emergency reports you have submitted"
        breadcrumbs={[{ label: 'Dashboard', href: '/dashboard' }, { label: 'My Reports' }]}
        action={
          <Link to="/report" className="flex items-center gap-2 rounded-lg bg-blue-600 hover:bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white transition-colors">
            <Plus className="h-4 w-4" /> New Report
          </Link>
        }
      />

      {isLoading ? (
        <div className="space-y-4">{Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}</div>
      ) : !incidents || incidents.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No reports yet"
          description="When you submit an emergency report it will appear here with real-time status updates."
          action={
            <Link to="/report" className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
              <Plus className="h-4 w-4" /> Report Incident
            </Link>
          }
        />
      ) : (
        <div className="space-y-4">
          {incidents.map(inc => (
            <IncidentCard
              key={inc.incidentId}
              incident={inc}
              href={`/track/${inc._firestoreId || inc.incidentId}`}
            />
          ))}
        </div>
      )}
    </div>
  )
}
