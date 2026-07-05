import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Save, Loader2, User, Phone, MapPin, Shield } from 'lucide-react'
import { toast } from 'sonner'
import { useAuth } from '@/hooks/useAuth'
import { authService } from '@/services/auth.service'
import { PageHeader } from '@/components/common/PageHeader'
import { Avatar } from '@/components/ui/Avatar'
import { USER_ROLES } from '@/utils/constants'

const schema = z.object({
  displayName: z.string().min(2, 'Min 2 chars'),
  phoneNumber: z.string().optional(),
  district: z.string().min(2),
  state: z.string().min(2),
  address: z.string().optional(),
})
type FormData = z.infer<typeof schema>

export default function ProfilePage() {
  const { user, refreshUser } = useAuth()
  const [saving, setSaving] = useState(false)

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      displayName: user?.displayName || '',
      phoneNumber: user?.phoneNumber || '',
      district: user?.district || '',
      state: user?.state || '',
      address: user?.address || '',
    },
  })

  const onSubmit = async (data: FormData) => {
    setSaving(true)
    try {
      await authService.updateProfile(data)
      await refreshUser?.()
      toast.success('Profile updated successfully')
    } catch { toast.error('Failed to update profile') }
    finally { setSaving(false) }
  }

  if (!user) return null

  return (
    <div className="max-w-2xl">
      <PageHeader title="Profile" subtitle="Manage your account information" />

      <div className="space-y-6">
        {/* Avatar card */}
        <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <Avatar name={user.displayName} size="xl" />
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">{user.displayName}</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">{user.email}</p>
              <div className="mt-2 flex items-center gap-2">
                <span className="flex items-center gap-1 rounded-full bg-blue-100 dark:bg-blue-900/30 px-3 py-1 text-xs font-semibold text-blue-700 dark:text-blue-400">
                  <Shield className="h-3 w-3" /> {USER_ROLES[user.role] || user.role}
                </span>
                {user.isVerified && (
                  <span className="rounded-full bg-green-100 dark:bg-green-900/30 px-3 py-1 text-xs font-semibold text-green-700 dark:text-green-400">
                    ✓ Verified
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Edit form */}
        <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 shadow-sm">
          <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-5 flex items-center gap-2">
            <User className="h-4 w-4" /> Personal Information
          </h3>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Full Name</label>
                <input {...register('displayName')} className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white" />
                {errors.displayName && <p className="mt-1 text-xs text-red-600">{errors.displayName.message}</p>}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Phone</label>
                <input {...register('phoneNumber')} className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">District</label>
                <input {...register('district')} className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">State</label>
                <input {...register('state')} className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Address</label>
              <input {...register('address')} placeholder="Optional full address" className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 dark:text-white" />
            </div>
            <div className="pt-2">
              <button type="submit" disabled={saving}
                className="flex items-center gap-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-2.5 text-sm font-semibold transition-colors">
                {saving ? <><Loader2 className="h-4 w-4 animate-spin" /> Saving…</> : <><Save className="h-4 w-4" /> Save Changes</>}
              </button>
            </div>
          </form>
        </div>

        {/* Account info */}
        <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 shadow-sm">
          <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Shield className="h-4 w-4" /> Account Details
          </h3>
          <dl className="grid grid-cols-2 gap-4 text-sm">
            <div><dt className="text-gray-500 dark:text-gray-400">User ID</dt><dd className="font-mono text-xs text-gray-700 dark:text-gray-300 mt-0.5">{user.uid}</dd></div>
            <div><dt className="text-gray-500 dark:text-gray-400">Role</dt><dd className="font-medium text-gray-900 dark:text-white mt-0.5">{USER_ROLES[user.role]}</dd></div>
            <div><dt className="text-gray-500 dark:text-gray-400">2FA</dt><dd className={`font-medium mt-0.5 ${user.mfaEnabled ? 'text-green-600' : 'text-gray-500'}`}>{user.mfaEnabled ? 'Enabled' : 'Disabled'}</dd></div>
            <div><dt className="text-gray-500 dark:text-gray-400">Member Since</dt><dd className="text-gray-700 dark:text-gray-300 mt-0.5">{user.createdAt ? new Date(user.createdAt).toLocaleDateString() : '—'}</dd></div>
          </dl>
        </div>
      </div>
    </div>
  )
}
