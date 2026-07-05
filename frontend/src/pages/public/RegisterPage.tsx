import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, Shield, Loader2, ArrowLeft, ArrowRight, CheckCircle2 } from 'lucide-react'
import { toast } from 'sonner'
import { useAuth } from '@/hooks/useAuth'
import type { UserRole } from '@/types'

const schema = z.object({
  displayName: z.string().min(2, 'Name required'),
  email: z.string().email('Valid email required'),
  phoneNumber: z.string().optional(),
  state: z.string().min(2, 'State required'),
  district: z.string().min(2, 'District required'),
  role: z.enum(['CITIZEN','AUTHORITY','NGO','VOLUNTEER'] as const),
  password: z.string().min(8, 'Minimum 8 characters').regex(/[A-Z]/, 'Must contain one uppercase letter').regex(/[0-9]/, 'Must contain one digit'),
  confirmPassword: z.string(),
}).refine(d => d.password === d.confirmPassword, { message: 'Passwords do not match', path: ['confirmPassword'] })

type FormData = z.infer<typeof schema>

const STEPS = ['Personal Info', 'Location', 'Role & Password']
const ROLE_OPTIONS: { value: UserRole; label: string; desc: string; emoji: string }[] = [
  { value: 'CITIZEN', label: 'Citizen', desc: 'Report emergencies and track rescue status', emoji: '👤' },
  { value: 'AUTHORITY', label: 'Authority', desc: 'Manage incidents and coordinate response', emoji: '🛡️' },
  { value: 'NGO', label: 'NGO Worker', desc: 'Coordinate relief and volunteer activities', emoji: '🤝' },
  { value: 'VOLUNTEER', label: 'Volunteer', desc: 'Receive nearby alerts and assist response', emoji: '🙋' },
]

const INDIA_STATES = ['Andhra Pradesh','Assam','Bihar','Chhattisgarh','Goa','Gujarat','Haryana','Himachal Pradesh','Jharkhand','Karnataka','Kerala','Madhya Pradesh','Maharashtra','Manipur','Meghalaya','Mizoram','Nagaland','Odisha','Punjab','Rajasthan','Sikkim','Tamil Nadu','Telangana','Tripura','Uttar Pradesh','Uttarakhand','West Bengal','Delhi']

export default function RegisterPage() {
  const [step, setStep] = useState(0)
  const [showPass, setShowPass] = useState(false)
  const { register: authRegister } = useAuth()
  const navigate = useNavigate()

  const { register, handleSubmit, watch, trigger, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { role: 'CITIZEN' },
  })

  const role = watch('role')

  const nextStep = async () => {
    const fields: (keyof FormData)[][] = [
      ['displayName', 'email', 'phoneNumber'],
      ['state', 'district'],
      ['role', 'password', 'confirmPassword'],
    ]
    const valid = await trigger(fields[step])
    if (valid) setStep(s => s + 1)
  }

  const onSubmit = async (data: FormData) => {
    try {
      const user = await authRegister({
        email: data.email,
        password: data.password,
        displayName: data.displayName,
        phoneNumber: data.phoneNumber || undefined,
        district: data.district,
        state: data.state,
        role: data.role,
      })
      toast.success('Account created! Welcome to ResQAI.')
      navigate(user.role === 'CITIZEN' ? '/dashboard' : '/authority', { replace: true })
    } catch (err: any) {
      const apiErr = err?.response?.data?.error
      if (apiErr?.details?.fields?.length) {
        const fieldMsg = apiErr.details.fields.map((f: any) => f.message).join(', ')
        toast.error(`Validation: ${fieldMsg}`)
      } else {
        toast.error(apiErr?.message || 'Registration failed. Please try again.')
      }
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 px-4 py-12">
      <div className="w-full max-w-lg">
        {/* Logo */}
        <Link to="/landing" className="flex items-center justify-center gap-2 mb-8">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600">
            <Shield className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold text-gray-900 dark:text-white">ResQAI</span>
        </Link>

        <div className="rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-8 shadow-sm">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Create your account</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Step {step + 1} of {STEPS.length} — {STEPS[step]}</p>

          {/* Step indicators */}
          <div className="mt-4 flex items-center gap-2">
            {STEPS.map((s, i) => (
              <div key={i} className="flex items-center gap-2">
                <div className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold transition-colors ${
                  i < step ? 'bg-green-500 text-white' : i === step ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-500'
                }`}>
                  {i < step ? <CheckCircle2 className="h-4 w-4" /> : i + 1}
                </div>
                {i < STEPS.length - 1 && <div className={`h-px flex-1 w-8 ${i < step ? 'bg-green-400' : 'bg-gray-200 dark:bg-gray-700'}`} />}
              </div>
            ))}
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="mt-6">
            {/* Step 1 */}
            {step === 0 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Full Name *</label>
                  <input {...register('displayName')} placeholder="Rajesh Kumar" className="input-field" />
                  {errors.displayName && <p className="mt-1 text-xs text-red-600">{errors.displayName.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Email *</label>
                  <input {...register('email')} type="email" placeholder="you@example.com" className="input-field" />
                  {errors.email && <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Phone (optional)</label>
                  <input {...register('phoneNumber')} type="tel" placeholder="+91 9876543210" className="input-field" />
                </div>
              </div>
            )}

            {/* Step 2 */}
            {step === 1 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">State *</label>
                  <select {...register('state')} className="input-field">
                    <option value="">Select state</option>
                    {INDIA_STATES.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                  {errors.state && <p className="mt-1 text-xs text-red-600">{errors.state.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">District *</label>
                  <input {...register('district')} placeholder="e.g. Khurda" className="input-field" />
                  {errors.district && <p className="mt-1 text-xs text-red-600">{errors.district.message}</p>}
                </div>
              </div>
            )}

            {/* Step 3 */}
            {step === 2 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">I am registering as *</label>
                  <div className="grid grid-cols-2 gap-2.5">
                    {ROLE_OPTIONS.map(opt => (
                      <label key={opt.value} className={`flex cursor-pointer flex-col gap-1 rounded-xl border-2 p-3 transition-all ${
                        role === opt.value
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                      }`}>
                        <input {...register('role')} type="radio" value={opt.value} className="sr-only" />
                        <span className="text-2xl">{opt.emoji}</span>
                        <span className="text-sm font-semibold text-gray-900 dark:text-white">{opt.label}</span>
                        <span className="text-xs text-gray-500 dark:text-gray-400 leading-tight">{opt.desc}</span>
                      </label>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Password *</label>
                  <div className="relative">
                    <input {...register('password')} type={showPass ? 'text' : 'password'} placeholder="••••••••" className="input-field pr-11" />
                    <button type="button" onClick={() => setShowPass(!showPass)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                      {showPass ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  <p className="mt-1 text-xs text-gray-400">Min 8 chars · 1 uppercase · 1 number · 1 special character (!@#$...)</p>
                  {errors.password && <p className="mt-1 text-xs text-red-600">{errors.password.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Confirm Password *</label>
                  <input {...register('confirmPassword')} type="password" placeholder="••••••••" className="input-field" />
                  {errors.confirmPassword && <p className="mt-1 text-xs text-red-600">{errors.confirmPassword.message}</p>}
                </div>
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
              {step < 2 ? (
                <button type="button" onClick={nextStep}
                  className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white py-2.5 text-sm font-semibold transition-colors">
                  Continue <ArrowRight className="h-4 w-4" />
                </button>
              ) : (
                <button type="submit" disabled={isSubmitting}
                  className="flex-1 flex items-center justify-center gap-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white py-2.5 text-sm font-semibold transition-colors">
                  {isSubmitting ? <><Loader2 className="h-4 w-4 animate-spin" /> Creating account…</> : 'Create Account'}
                </button>
              )}
            </div>
          </form>

          <p className="mt-5 text-center text-sm text-gray-500 dark:text-gray-400">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-blue-600 dark:text-blue-400 hover:underline">Sign in</Link>
          </p>
        </div>
      </div>

      <style>{`.input-field { width: 100%; border-radius: 0.5rem; border: 1px solid #d1d5db; background: white; padding: 0.75rem 1rem; font-size: 0.875rem; outline: none; transition: box-shadow 0.15s; } .input-field:focus { box-shadow: 0 0 0 2px #3B82F6; border-color: transparent; } @media (prefers-color-scheme: dark) { .input-field { background: #1f2937; border-color: #374151; color: white; } }`}</style>
    </div>
  )
}
