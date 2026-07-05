import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, Shield, Loader2, AlertCircle } from 'lucide-react'
import { toast } from 'sonner'
import { useAuth } from '@/hooks/useAuth'
import type { UserRole } from '@/types'

const schema = z.object({
  email: z.string().email('Valid email required'),
  password: z.string().min(6, 'Password required'),
  remember: z.boolean().optional(),
})
type FormData = z.infer<typeof schema>

const ROLE_REDIRECTS: Record<UserRole, string> = {
  CITIZEN: '/dashboard', AUTHORITY: '/authority', DISTRICT_OFFICER: '/authority',
  STATE_OFFICER: '/authority', NGO: '/authority', VOLUNTEER: '/authority', ADMIN: '/admin',
}

export default function LoginPage() {
  const [showPass, setShowPass] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const { register, handleSubmit, formState: { errors, isSubmitting }, setError } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    try {
      const user = await login(data.email, data.password)
      toast.success(`Welcome back, ${user.displayName}!`)
      navigate(ROLE_REDIRECTS[user.role] || '/dashboard', { replace: true })
    } catch (err: any) {
      const apiErr = err?.response?.data?.error
      const msg = apiErr?.message || err?.message || 'Login failed. Please try again.'
      setError('root', { message: msg })
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left — visual panel */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 p-12 text-white">
        <Link to="/landing" className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600">
            <Shield className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold">ResQAI</span>
        </Link>
        <div>
          <h2 className="text-4xl font-black leading-tight mb-4">
            Decision Intelligence<br />for Disaster Response
          </h2>
          <p className="text-blue-200 text-base leading-relaxed mb-8">
            AI-powered triage, real-time coordination, and explainable recommendations — all in one platform.
          </p>
          <div className="grid grid-cols-2 gap-4">
            {[
              { v: '47', l: 'Active Incidents' }, { v: '5s', l: 'AI Triage' },
              { v: '83%', l: 'Faster Response' }, { v: '99.9%', l: 'Uptime SLA' },
            ].map(s => (
              <div key={s.l} className="rounded-xl bg-white/10 p-4">
                <div className="text-2xl font-black text-white">{s.v}</div>
                <div className="text-sm text-blue-200">{s.l}</div>
              </div>
            ))}
          </div>
        </div>
        <p className="text-xs text-blue-300">Powered by Google Gemini · Firebase · Cloud Run</p>
      </div>

      {/* Right — form */}
      <div className="flex w-full lg:w-1/2 flex-col items-center justify-center px-6 py-12 bg-white dark:bg-gray-900">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <Link to="/landing" className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600">
              <Shield className="h-4 w-4 text-white" />
            </div>
            <span className="text-lg font-bold text-gray-900 dark:text-white">ResQAI</span>
          </Link>

          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Welcome back</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Sign in to your ResQAI account</p>

          <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-4">
            {errors.root && (
              <div className="flex items-center gap-2 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 px-4 py-3 text-sm text-red-700 dark:text-red-400">
                <AlertCircle className="h-4 w-4 shrink-0" />
                {errors.root.message}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Email address</label>
              <input
                {...register('email')}
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-3 text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
              />
              {errors.email && <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.email.message}</p>}
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
                <Link to="/forgot-password" className="text-xs text-blue-600 dark:text-blue-400 hover:underline">Forgot password?</Link>
              </div>
              <div className="relative">
                <input
                  {...register('password')}
                  type={showPass ? 'text' : 'password'}
                  autoComplete="current-password"
                  placeholder="••••••••"
                  className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-3 pr-11 text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                >
                  {showPass ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {errors.password && <p className="mt-1 text-xs text-red-600 dark:text-red-400">{errors.password.message}</p>}
            </div>

            <div className="flex items-center gap-2">
              <input {...register('remember')} id="remember" type="checkbox" className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
              <label htmlFor="remember" className="text-sm text-gray-600 dark:text-gray-400">Remember me</label>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white py-3 text-sm font-semibold transition-colors shadow-sm"
            >
              {isSubmitting ? <><Loader2 className="h-4 w-4 animate-spin" /> Signing in…</> : 'Sign In'}
            </button>

            <div className="relative flex items-center gap-3 py-2">
              <div className="flex-1 border-t border-gray-200 dark:border-gray-700" />
              <span className="text-xs text-gray-400">or continue with</span>
              <div className="flex-1 border-t border-gray-200 dark:border-gray-700" />
            </div>

            <button
              type="button"
              className="w-full flex items-center justify-center gap-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200 py-3 text-sm font-medium transition-colors"
            >
              <svg className="h-4 w-4" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
              Sign in with Google
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
            Don't have an account?{' '}
            <Link to="/register" className="font-medium text-blue-600 dark:text-blue-400 hover:underline">Sign up</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
