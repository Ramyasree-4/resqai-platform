import { useState, useCallback } from 'react'
import { Layers, Thermometer } from 'lucide-react'
import { cn } from '@/utils/cn'
import type { MapData } from '@/types'
import { SEVERITY_COLORS, INCIDENT_TYPE_LABELS, INDIA_CENTER } from '@/utils/constants'

interface Props {
  data?: MapData
  height?: string
  onIncidentClick?: (id: string) => void
  onResourceClick?: (id: string) => void
  className?: string
}

// Severity colors for map markers
const MARKER_COLORS: Record<string, string> = {
  CRITICAL: '#DC2626', HIGH: '#EA580C', MEDIUM: '#D97706', LOW: '#16A34A'
}

export function ResQAIMap({ data, height = '500px', onIncidentClick, onResourceClick, className }: Props) {
  const [showHeatmap, setShowHeatmap] = useState(false)
  const [showResources, setShowResources] = useState(true)
  const [selectedIncident, setSelectedIncident] = useState<string | null>(null)
  const [selectedResource, setSelectedResource] = useState<string | null>(null)

  const mapsKey = import.meta.env.VITE_MAPS_API_KEY

  // If no Maps API key, render a styled placeholder
  if (!mapsKey || mapsKey === 'your-google-maps-api-key') {
    return (
      <div
        className={cn('relative rounded-xl overflow-hidden bg-gray-100 dark:bg-gray-800 flex flex-col', className)}
        style={{ height }}
      >
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-6">
          <div className="text-6xl mb-3">🗺️</div>
          <p className="text-base font-semibold text-gray-700 dark:text-gray-300">Operations Map</p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Add VITE_MAPS_API_KEY to .env to enable Google Maps
          </p>
          {data && (
            <div className="mt-4 flex gap-4 text-xs text-gray-500">
              <span>📍 {data.incidents.length} incidents</span>
              <span>🚁 {data.resources.length} resources</span>
            </div>
          )}
        </div>
        {/* Visual placeholder grid */}
        <div className="absolute inset-0 opacity-20">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="absolute border-b border-gray-400" style={{ top: `${(i + 1) * 16}%`, left: 0, right: 0 }} />
          ))}
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="absolute border-r border-gray-400" style={{ left: `${(i + 1) * 12}%`, top: 0, bottom: 0 }} />
          ))}
        </div>
        {/* Incident dots overlay */}
        {data?.incidents.map((inc) => {
          const color = MARKER_COLORS[inc.severityBand || 'MEDIUM'] || '#6B7280'
          const x = Math.abs(((inc.longitude || 78) - 68) / 30) * 100
          const y = Math.abs(((inc.latitude || 20) - 37) / 31) * 100
          return (
            <div
              key={inc.incidentId}
              className="absolute cursor-pointer transform -translate-x-1/2 -translate-y-1/2 z-10"
              style={{ left: `${x}%`, top: `${y}%` }}
              onClick={() => onIncidentClick?.(inc.incidentId)}
            >
              <div
                className="h-3 w-3 rounded-full border-2 border-white shadow-md"
                style={{ backgroundColor: color }}
                title={`${inc.title} (${inc.severityBand})`}
              />
            </div>
          )
        })}
      </div>
    )
  }

  // Google Maps iframe embed (works without JS API key restrictions for basic display)
  return (
    <div className={cn('relative rounded-xl overflow-hidden', className)} style={{ height }}>
      <iframe
        title="ResQAI Operations Map"
        width="100%"
        height="100%"
        style={{ border: 0 }}
        loading="lazy"
        allowFullScreen
        referrerPolicy="no-referrer-when-downgrade"
        src={`https://www.google.com/maps/embed/v1/view?key=${mapsKey}&center=${INDIA_CENTER.lat},${INDIA_CENTER.lng}&zoom=5`}
      />
      {/* Layer controls */}
      <div className="absolute top-3 right-3 flex flex-col gap-2">
        <button
          onClick={() => setShowHeatmap(!showHeatmap)}
          className={cn(
            'flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium shadow-md transition-colors',
            showHeatmap
              ? 'bg-orange-500 text-white'
              : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:bg-gray-50'
          )}
        >
          <Thermometer className="h-3.5 w-3.5" /> Heatmap
        </button>
        <button
          onClick={() => setShowResources(!showResources)}
          className={cn(
            'flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium shadow-md transition-colors',
            showResources
              ? 'bg-blue-600 text-white'
              : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:bg-gray-50'
          )}
        >
          <Layers className="h-3.5 w-3.5" /> Resources
        </button>
      </div>
      {/* Incident count overlay */}
      {data && (
        <div className="absolute bottom-3 left-3 flex gap-2">
          <div className="rounded-lg bg-white/90 dark:bg-gray-800/90 px-3 py-1.5 text-xs font-medium shadow-md">
            📍 {data.incidents.length} incidents
          </div>
          {showResources && (
            <div className="rounded-lg bg-white/90 dark:bg-gray-800/90 px-3 py-1.5 text-xs font-medium shadow-md">
              🚁 {data.resources.length} resources
            </div>
          )}
        </div>
      )}
    </div>
  )
}
