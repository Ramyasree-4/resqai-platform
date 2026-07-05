import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Shield, ArrowLeft, Mail, CheckCircle2, Loader2 } from 'lucide-react'
import { authService } from '@/services/auth.service'
import { toast } from 'sonner'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) return
    setLoading(true)
    try {
      await authService.forgotPassword(email)
      setSent(true)
    } catch {
      toast.error('Failed to send reset email. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950 px-4">
      <div className="w-full max-w-md">
        <Link to="/landing" className="flex items-center justify-center gap-2 mb-8">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600">
            <Shield className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold text-gray-900 dark:text-white">ResQAI</span>
        </Link>

        <div className="rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-8 shadow-sm">
          {sent ? (
            <div className="text-center py-4">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/20 mb-4">
                <CheckCircle2 className="h-8 w-8 text-green-600" />
              </div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Check your email</h2>
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                We've sent a password reset link to <strong>{email}</strong>
              </p>
              <Link to="/login" className="mt-6 inline-flex items-center gap-2 text-sm font-medium text-blue-600 dark:text-blue-400 hover:underline">
                <ArrowLeft className="h-4 w-4" /> Back to sign in
              </Link>
            </div>
          ) : (
            <>
              <div className="flex items-center gap-3 mb-6">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-900/20">
                  <Mail className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900 dark:text-white">Forgot password?</h1>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Enter your email to receive a reset link</p>
                </div>
              </div>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Email address</label>
                  <input
                    type="email" value={email} onChange={e => setEmail(e.target.value)}
                    placeholder="you@example.com" required
                    className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-3 text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <button type="submit" disabled={loading || !email}
                  className="w-full flex items-center justify-center gap-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white py-3 text-sm font-semibold transition-colors">
                  {loading ? <><Loader2 className="h-4 w-4 animate-spin" /> Sending…</> : 'Send Reset Link'}
                </button>
              </form>
              <Link to="/login" className="mt-4 flex items-center justify-center gap-1.5 text-sm text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                <ArrowLeft className="h-3.5 w-3.5" /> Back to sign in
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
