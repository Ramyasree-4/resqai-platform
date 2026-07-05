import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Layers, AlertTriangle, X } from 'lucide-react'
import { useMapData } from '@/hooks/useDashboard'
import { ResQAIMap } from '@/components/map/ResQAIMap'
import { SeverityBadge } from '@/components/ui/SeverityBadge'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { INCIDENT_TYPE_LABELS } from '@/utils/constants'
import type { MapIncidentPoint } from '@/types'

export default function MapViewPage() {
  const navigate = useNavigate()
  const { data: mapData, isLoading } = useMapData()
  const [selected, setSelected] = useState<MapIncidentPoint | null>(null)

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] -mx-4 sm:-mx-6 -mb-6">
      {/* Toolbar */}
      <div className="flex items-center justify-between gap-4 px-4 sm:px-6 py-3 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shrink-0">
        <div className="flex items-center gap-3">
          <h1 className="text-base font-semibold text-gray-900 dark:text-white">Operations Map</h1>
          {mapData && (
            <>
              <span className="text-xs text-gray-500">📍 {mapData.incidents.length} incidents</span>
              <span className="text-xs text-gray-500">🚁 {mapData.resources.length} resources</span>
            </>
          )}
        </div>
        <div className="flex items-center gap-2">
          {/* Legend */}
          <div className="hidden sm:flex items-center gap-3 text-xs text-gray-500">
            {[['🔴','Critical'],['🟠','High'],['🟡','Medium'],['🟢','Low']].map(([dot,label]) => (
              <span key={label} className="flex items-center gap-1">{dot} {label}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Map + Side panel */}
      <div className="flex flex-1 overflow-hidden">
        <ResQAIMap
          data={mapData}
          height="100%"
          onIncidentClick={id => {
            const inc = mapData?.incidents.find(i => i.incidentId === id || i.incidentId === id)
            if (inc) setSelected(inc as any)
          }}
          className="flex-1"
        />

        {/* Selected incident panel */}
        {selected && (
          <div className="w-72 shrink-0 border-l border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b border-gray-100 dark:border-gray-700">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white">Incident Details</h3>
              <button onClick={() => setSelected(null)} className="rounded-lg p-1 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-400">
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="p-4 space-y-3">
              <div className="flex items-start gap-2">
                <span className="text-2xl">{INCIDENT_TYPE_LABELS[selected.incidentType as keyof typeof INCIDENT_TYPE_LABELS]?.emoji || '⚠️'}</span>
                <div>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">{selected.title}</p>
                  <div className="flex flex-wrap gap-1.5 mt-1">
                    {selected.severityBand && <SeverityBadge band={selected.severityBand as any} score={selected.severityScore} size="sm" />}
                    <StatusBadge status={selected.status as any} />
                  </div>
                </div>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                📍 Lat: {selected.latitude?.toFixed(4)}, Lng: {selected.longitude?.toFixed(4)}
              </p>
              <button
                onClick={() => navigate(`/authority/incidents/${selected.incidentId}`)}
                className="w-full rounded-lg bg-blue-600 hover:bg-blue-700 text-white py-2 text-sm font-semibold transition-colors"
              >
                View Full Details →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
