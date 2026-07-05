import { ThumbsUp, ThumbsDown, CheckCircle2, AlertTriangle, Zap, Shield, Info } from 'lucide-react'
import { useState } from 'react'
import { SeverityBadge } from '@/components/ui/SeverityBadge'
import { cn } from '@/utils/cn'
import type { AIAnalysis } from '@/types'
import { INCIDENT_TYPE_LABELS, RESOURCE_TYPE_ICONS } from '@/utils/constants'
import { formatRelativeTime } from '@/utils/formatters'

interface Props {
  analysis: AIAnalysis
  onAccept?: () => void
  onOverride?: () => void
  onFeedback?: (positive: boolean) => void
  readOnly?: boolean
}

export function AIAnalysisPanel({ analysis, onAccept, onOverride, onFeedback, readOnly }: Props) {
  const [feedbackGiven, setFeedbackGiven] = useState<boolean | null>(null)

  const handleFeedback = (positive: boolean) => {
    setFeedbackGiven(positive)
    onFeedback?.(positive)
  }

  const severityScore = analysis.severityScore ?? 0
  const severityBand = analysis.severityBand ?? 'MEDIUM'

  return (
    <div className="rounded-xl border border-purple-200 dark:border-purple-800 bg-gradient-to-br from-purple-50 to-white dark:from-purple-900/10 dark:to-gray-800 p-5 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-100 dark:bg-purple-900/30">
            <Zap className="h-4 w-4 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-900 dark:text-white">AI Assessment</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {analysis.modelVersion} • {formatRelativeTime(analysis.processedAt)}
            </p>
          </div>
        </div>
        {analysis.fallbackUsed && (
          <span className="rounded-full bg-yellow-100 dark:bg-yellow-900/30 px-2 py-0.5 text-xs font-medium text-yellow-700 dark:text-yellow-400">
            Fallback Mode
          </span>
        )}
      </div>

      {/* Severity Score */}
      <div className="flex items-center gap-4">
        <div className="flex flex-col items-center justify-center h-20 w-20 rounded-2xl bg-white dark:bg-gray-800 border-2 shadow-sm"
          style={{ borderColor: severityBand === 'CRITICAL' ? '#DC2626' : severityBand === 'HIGH' ? '#EA580C' : severityBand === 'MEDIUM' ? '#D97706' : '#16A34A' }}>
          <span className="text-3xl font-black text-gray-900 dark:text-white">{severityScore}</span>
          <span className="text-xs text-gray-500">/10</span>
        </div>
        <div className="flex-1">
          <SeverityBadge band={severityBand} size="lg" />
          <p className="mt-1.5 text-xs text-gray-600 dark:text-gray-400">{(analysis as any).severity?.justification || ''}</p>
          {analysis.classifiedType && (
            <div className="mt-1.5 flex items-center gap-1.5">
              <span className="text-sm">{INCIDENT_TYPE_LABELS[analysis.classifiedType]?.emoji}</span>
              <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                {INCIDENT_TYPE_LABELS[analysis.classifiedType]?.label}
              </span>
              {analysis.classificationConfidence && (
                <span className="text-xs text-gray-500">
                  ({Math.round(analysis.classificationConfidence * 100)}% confidence)
                </span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Situation Summary */}
      {analysis.situationSummary && (
        <div className="rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 p-3">
          <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">Situation Summary</p>
          <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{analysis.situationSummary}</p>
        </div>
      )}

      {/* Reasoning */}
      {analysis.reasoning.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">Why this rating</p>
          <ul className="space-y-1.5">
            {analysis.reasoning.map((r, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                <CheckCircle2 className="h-4 w-4 mt-0.5 shrink-0 text-green-500" />
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Immediate Actions */}
      {analysis.immediateActions.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">Immediate Actions</p>
          <ul className="space-y-1.5">
            {analysis.immediateActions.map((a, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
                <Shield className="h-4 w-4 mt-0.5 shrink-0 text-blue-500" />
                {a}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Resource Recommendations */}
      {analysis.resourceRecommendations.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">Recommended Resources</p>
          <div className="space-y-2">
            {analysis.resourceRecommendations.map((rec, i) => (
              <div key={i} className="flex items-center gap-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 px-3 py-2">
                <span className="text-lg">{RESOURCE_TYPE_ICONS[rec.resourceType] || '🚨'}</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {rec.quantity}× {rec.resourceType.replace('_', ' ')}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 line-clamp-1">{rec.reason}</p>
                </div>
                <span className={cn('rounded-full px-2 py-0.5 text-[10px] font-semibold',
                  rec.urgency === 'IMMEDIATE' ? 'bg-red-100 text-red-700' :
                  rec.urgency === 'HIGH' ? 'bg-orange-100 text-orange-700' :
                  rec.urgency === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-green-100 text-green-700'
                )}>
                  {rec.urgency}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Risks */}
      {analysis.risks.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2">Identified Risks</p>
          <ul className="space-y-1.5">
            {analysis.risks.map((r, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-orange-700 dark:text-orange-400">
                <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Action Buttons */}
      {!readOnly && (onAccept || onOverride) && (
        <div className="flex gap-3 pt-2 border-t border-gray-200 dark:border-gray-700">
          {onAccept && (
            <button
              onClick={onAccept}
              disabled={analysis.authorityFeedback === 'ACCEPTED'}
              className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white py-2 text-sm font-medium transition-colors"
            >
              <CheckCircle2 className="h-4 w-4" />
              {analysis.authorityFeedback === 'ACCEPTED' ? 'Accepted ✓' : 'Accept Recommendation'}
            </button>
          )}
          {onOverride && (
            <button
              onClick={onOverride}
              className="flex-1 flex items-center justify-center gap-2 rounded-lg border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 py-2 text-sm font-medium transition-colors"
            >
              Override
            </button>
          )}
        </div>
      )}

      {/* Feedback */}
      {!readOnly && (
        <div className="flex items-center gap-3 pt-1">
          <span className="text-xs text-gray-500 dark:text-gray-400">Was this accurate?</span>
          <button
            onClick={() => handleFeedback(true)}
            className={cn('flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs transition-colors',
              feedbackGiven === true ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500'
            )}
          >
            <ThumbsUp className="h-3.5 w-3.5" /> Yes
          </button>
          <button
            onClick={() => handleFeedback(false)}
            className={cn('flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs transition-colors',
              feedbackGiven === false ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500'
            )}
          >
            <ThumbsDown className="h-3.5 w-3.5" /> No
          </button>
        </div>
      )}
    </div>
  )
}
