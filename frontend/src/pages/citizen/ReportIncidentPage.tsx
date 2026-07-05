import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Upload, X, MapPin, CheckCircle2, Loader2, ArrowLeft, ArrowRight } from 'lucide-react'
import { useCreateIncident } from '@/hooks/useIncidents'
import { useGeolocation } from '@/hooks/useGeolocation'
import { PageHeader } from '@/components/common/PageHeader'
import type { IncidentType, UrgencyLevel } from '@/types'
import { INCIDENT_TYPE_LABELS } from '@/utils/constants'

const schema = z.object({
  incidentType: z.string().min(1, 'Select incident type'),
  title: z.string().min(5, 'Min 5 chars'),
  description: z.string().min(20, 'Min 20 chars').max(2000),
  urgencyLevel: z.enum(['LOW','MEDIUM','HIGH','CRITICAL']),
  affectedPeople: z.coerce.number().int().min(1),
  address: z.string().min(5, 'Address required'),
  district: z.string().min(2),
  state: z.string().min(2),
  latitude: z.coerce.number(),
  longitude: z.coerce.number(),
  isAnonymous: z.boolean().default(false),
})
type FormData = z.infer<typeof schema>

const TYPES: IncidentType[] = ['FLOOD','FIRE','CYCLONE','EARTHQUAKE','LANDSLIDE','MEDICAL','INDUSTRIAL','OTHER']
const URGENCY: { value: UrgencyLevel; label: string; color: string }[] = [
  { value: 'LOW', label: 'Low', color: 'border-green-300 text-green-700 dark:text-green-400' },
  { value: 'MEDIUM', label: 'Medium', color: 'border-yellow-300 text-yellow-700 dark:text-yellow-400' },
  { value: 'HIGH', label: 'High', color: 'border-orange-300 text-orange-700 dark:text-orange-400' },
  { value: 'CRITICAL', label: 'Critical', color: 'border-red-400 text-red-700 dark:text-red-400' },
]
const STEPS = ['Type', 'Location', 'Details', 'Media', 'Review']

export default function ReportIncidentPage() {
  const [step, setStep] = useState(0)
  const [files, setFiles] = useState<File[]>([])
  const [submitted, setSubmitted] = useState<{ incidentId: string; estimatedResponseTime: string } | null>(null)
  const navigate = useNavigate()
  const { latitude, longitude, loading: geoLoading } = useGeolocation()
  const createIncident = useCreateIncident()

  const { register, handleSubmit, watch, setValue, trigger, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { urgencyLevel: 'HIGH', affectedPeople: 1, isAnonymous: false },
  })

  const selected = watch('incidentType')
  const urgency = watch('urgencyLevel')

  const fillGPS = () => {
    if (latitude && longitude) {
      setValue('latitude', latitude)
      setValue('longitude', longitude)
      toast.success('GPS location captured')
    }
  }

  const handleFiles = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = Array.from(e.target.files || [])
    setFiles(prev => [...prev, ...f].slice(0, 5))
  }

  const nextStep = async () => {
    const fieldsByStep: (keyof FormData)[][] = [
      ['incidentType'],
      ['address', 'district', 'state', 'latitude', 'longitude'],
      ['title', 'description', 'urgencyLevel', 'affectedPeople'],
      [],
    ]
    const valid = await trigger(fieldsByStep[step])
    if (valid) setStep(s => s + 1)
  }

  const onSubmit = async (data: FormData) => {
    try {
      const result = await createIncident.mutateAsync({
        title: data.title,
        description: data.description,
        incidentType: data.incidentType as IncidentType,
        urgencyLevel: data.urgencyLevel,
        affectedPeople: data.affectedPeople,
        isAnonymous: data.isAnonymous,
        location: {
          address: data.address,
          district: data.district,
          state: data.state,
          coordinates: { latitude: data.latitude, longitude: data.longitude },
        },
        source: 'WEB',
      })
      setSubmitted({ incidentId: result.incidentId, estimatedResponseTime: result.estimatedResponseTime })
    } catch (err: any) {
      toast.error(err?.response?.data?.error?.message || 'Failed to submit report')
    }
  }

  if (submitted) {
    return (
      <div className="flex min-h-[70vh] flex-col items-center justify-center text-center px-4">
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/20 mb-6">
          <CheckCircle2 className="h-10 w-10 text-green-600" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Report Submitted!</h2>
        <p className="mt-2 text-gray-500 dark:text-gray-400 max-w-sm">
          Your report is being analyzed by Gemini AI. Rescue teams will be dispatched shortly.
        </p>
        <div className="mt-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 px-6 py-4 text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Incident ID</p>
          <p className="text-lg font-bold text-blue-700 dark:text-blue-400 font-mono">{submitted.incidentId}</p>
          <p className="mt-1 text-xs text-gray-500">Estimated response: {submitted.estimatedResponseTime}</p>
        </div>
        <div className="mt-6 flex gap-3">
          <button onClick={() => navigate('/my-reports')} className="rounded-lg bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 text-sm font-semibold">
            Track Report
          </button>
          <button onClick={() => { setSubmitted(null); setStep(0) }} className="rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 px-6 py-2.5 text-sm font-medium">
            Report Another
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <PageHeader title="Report Emergency" subtitle="Submit a new incident report" breadcrumbs={[{ label: 'Dashboard', href: '/dashboard' }, { label: 'Report Incident' }]} />

      {/* Step progress */}
      <div className="flex items-center gap-1 mb-6">
        {STEPS.map((s, i) => (
          <div key={i} className="flex items-center gap-1 flex-1">
            <div className={`flex-1 flex items-center gap-1.5`}>
              <div className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                i < step ? 'bg-green-500 text-white' : i === step ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-500'
              }`}>
                {i < step ? '✓' : i + 1}
              </div>
              <span className={`text-xs font-medium hidden sm:block ${i === step ? 'text-blue-600 dark:text-blue-400' : 'text-gray-400'}`}>{s}</span>
            </div>
            {i < STEPS.length - 1 && <div className={`h-px w-4 sm:w-8 ${i < step ? 'bg-green-400' : 'bg-gray-200 dark:bg-gray-700'}`} />}
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 shadow-sm">
          {/* Step 1: Type */}
          {step === 0 && (
            <div>
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4">Select Incident Type</h3>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {TYPES.map(t => {
                  const info = INCIDENT_TYPE_LABELS[t]
                  return (
                    <label key={t} className={`flex cursor-pointer flex-col items-center gap-2 rounded-xl border-2 p-4 text-center transition-all ${
                      selected === t ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    }`}>
                      <input {...register('incidentType')} type="radio" value={t} className="sr-only" />
                      <span className="text-3xl">{info.emoji}</span>
                      <span className="text-xs font-semibold text-gray-900 dark:text-white">{info.label}</span>
                    </label>
                  )
                })}
              </div>
              {errors.incidentType && <p className="mt-2 text-xs text-red-600">{errors.incidentType.message}</p>}
            </div>
          )}

          {/* Step 2: Location */}
          {step === 1 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-semibold text-gray-900 dark:text-white">Location</h3>
                <button type="button" onClick={fillGPS} disabled={geoLoading}
                  className="flex items-center gap-1.5 text-sm text-blue-600 dark:text-blue-400 hover:underline disabled:opacity-50">
                  {geoLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <MapPin className="h-3.5 w-3.5" />}
                  Use My GPS
                </button>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Address *</label>
                <input {...register('address')} placeholder="Street address or landmark" className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white" />
                {errors.address && <p className="mt-1 text-xs text-red-600">{errors.address.message}</p>}
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">District *</label>
                  <input {...register('district')} placeholder="e.g. Khurda" className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white" />
                  {errors.district && <p className="mt-1 text-xs text-red-600">{errors.district.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">State *</label>
                  <input {...register('state')} placeholder="e.g. Odisha" className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white" />
                  {errors.state && <p className="mt-1 text-xs text-red-600">{errors.state.message}</p>}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Latitude</label>
                  <input {...register('latitude')} type="number" step="any" placeholder="20.2961" className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Longitude</label>
                  <input {...register('longitude')} type="number" step="any" placeholder="85.8245" className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white" />
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Details */}
          {step === 2 && (
            <div className="space-y-4">
              <h3 className="text-base font-semibold text-gray-900 dark:text-white">Incident Details</h3>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Title *</label>
                <input {...register('title')} placeholder="Brief title of the incident" className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white" />
                {errors.title && <p className="mt-1 text-xs text-red-600">{errors.title.message}</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Description * <span className="text-gray-400">(20–2000 chars)</span></label>
                <textarea {...register('description')} rows={5} placeholder="Describe the emergency in detail. Include: what's happening, how many people are affected, any immediate dangers, access routes, special needs..." className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white resize-none" />
                {errors.description && <p className="mt-1 text-xs text-red-600">{errors.description.message}</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Your Urgency Assessment *</label>
                <div className="grid grid-cols-4 gap-2">
                  {URGENCY.map(u => (
                    <label key={u.value} className={`flex cursor-pointer flex-col items-center gap-1 rounded-lg border-2 p-3 text-center transition-all ${
                      urgency === u.value ? `border-current ${u.color} bg-current/5` : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                    }`}>
                      <input {...register('urgencyLevel')} type="radio" value={u.value} className="sr-only" />
                      <span className={`text-xs font-bold ${urgency === u.value ? u.color : 'text-gray-600 dark:text-gray-400'}`}>{u.label}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">People Affected *</label>
                <input {...register('affectedPeople')} type="number" min="1" placeholder="Estimated number of people" className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white" />
                {errors.affectedPeople && <p className="mt-1 text-xs text-red-600">{errors.affectedPeople.message}</p>}
              </div>
              <label className="flex items-center gap-2 cursor-pointer">
                <input {...register('isAnonymous')} type="checkbox" className="h-4 w-4 rounded border-gray-300 text-blue-600" />
                <span className="text-sm text-gray-600 dark:text-gray-400">Submit anonymously</span>
              </label>
            </div>
          )}

          {/* Step 4: Media */}
          {step === 3 && (
            <div>
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4">Attach Media <span className="text-gray-400 font-normal">(optional, up to 5 files)</span></h3>
              <label className="flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/30 p-8 cursor-pointer hover:border-blue-400 transition-colors">
                <Upload className="h-8 w-8 text-gray-400" />
                <div className="text-center">
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Click to upload or drag & drop</p>
                  <p className="text-xs text-gray-500 mt-0.5">Images, videos up to 50MB each</p>
                </div>
                <input type="file" multiple accept="image/*,video/*" onChange={handleFiles} className="sr-only" />
              </label>
              {files.length > 0 && (
                <div className="mt-4 grid grid-cols-3 gap-2">
                  {files.map((file, i) => (
                    <div key={i} className="relative rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700 aspect-square">
                      {file.type.startsWith('image/') ? (
                        <img src={URL.createObjectURL(file)} alt={file.name} className="h-full w-full object-cover" />
                      ) : (
                        <div className="flex h-full items-center justify-center text-2xl">🎬</div>
                      )}
                      <button type="button" onClick={() => setFiles(prev => prev.filter((_, j) => j !== i))}
                        className="absolute top-1 right-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-white hover:bg-red-600">
                        <X className="h-3 w-3" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Step 5: Review */}
          {step === 4 && (
            <div>
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4">Review & Submit</h3>
              <div className="space-y-3 rounded-xl bg-gray-50 dark:bg-gray-700/30 p-4 text-sm">
                {[
                  { label: 'Type', value: INCIDENT_TYPE_LABELS[watch('incidentType') as IncidentType]?.label || watch('incidentType') },
                  { label: 'Location', value: `${watch('address')}, ${watch('district')}, ${watch('state')}` },
                  { label: 'Description', value: watch('description')?.slice(0, 100) + (watch('description')?.length > 100 ? '…' : '') },
                  { label: 'Urgency', value: watch('urgencyLevel') },
                  { label: 'People Affected', value: watch('affectedPeople')?.toString() },
                  { label: 'Media Files', value: `${files.length} file(s)` },
                ].map(row => (
                  <div key={row.label} className="flex gap-3">
                    <span className="w-28 shrink-0 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">{row.label}</span>
                    <span className="text-gray-900 dark:text-white">{row.value}</span>
                  </div>
                ))}
              </div>
              <p className="mt-4 text-xs text-gray-500 dark:text-gray-400">
                By submitting you confirm this is a genuine emergency report. False reports are a criminal offence.
              </p>
            </div>
          )}

          {/* Navigation */}
          <div className="mt-6 flex gap-3">
            {step > 0 && (
              <button type="button" onClick={() => setStep(s => s - 1)}
                className="flex items-center gap-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-5 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                <ArrowLeft className="h-4 w-4" /> Back
              </button>
            )}
            {step < 4 ? (
              <button type="button" onClick={nextStep}
                className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white py-2.5 text-sm font-semibold transition-colors">
                Continue <ArrowRight className="h-4 w-4" />
              </button>
            ) : (
              <button type="submit" disabled={createIncident.isPending}
                className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white py-2.5 text-sm font-bold transition-colors">
                {createIncident.isPending
                  ? <><Loader2 className="h-4 w-4 animate-spin" /> AI is analyzing your report…</>
                  : '🆘 Submit Emergency Report'}
              </button>
            )}
          </div>
        </div>
      </form>
    </div>
  )
}
