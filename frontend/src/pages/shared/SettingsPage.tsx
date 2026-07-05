import { useState } from 'react'
import { Bell, Palette, Globe, Shield, Sun, Moon, Monitor } from 'lucide-react'
import { useTheme } from '@/contexts/ThemeContext'
import { useAuth } from '@/hooks/useAuth'
import { PageHeader } from '@/components/common/PageHeader'
import { cn } from '@/utils/cn'

type Tab = 'notifications' | 'appearance' | 'language' | 'security'

const TABS = [
  { id: 'notifications' as Tab, label: 'Notifications', icon: Bell },
  { id: 'appearance' as Tab, label: 'Appearance', icon: Palette },
  { id: 'language' as Tab, label: 'Language', icon: Globe },
  { id: 'security' as Tab, label: 'Security', icon: Shield },
]

const THEMES = [
  { value: 'light', label: 'Light', icon: Sun },
  { value: 'dark', label: 'Dark', icon: Moon },
  { value: 'system', label: 'System', icon: Monitor },
] as const

const LANGUAGES = [
  { code: 'en', label: 'English', native: 'English' },
  { code: 'hi', label: 'Hindi', native: 'हिंदी' },
  { code: 'or', label: 'Odia', native: 'ଓଡ଼ିଆ' },
  { code: 'bn', label: 'Bengali', native: 'বাংলা' },
]

function Toggle({ checked, onChange, label }: { checked: boolean; onChange: (v: boolean) => void; label: string }) {
  return (
    <div className="flex items-center justify-between py-3">
      <span className="text-sm text-gray-700 dark:text-gray-300">{label}</span>
      <button
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={cn('relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors', checked ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700')}
      >
        <span className={cn('inline-block h-5 w-5 transform rounded-full bg-white shadow transition-transform', checked ? 'translate-x-5' : 'translate-x-0')} />
      </button>
    </div>
  )
}

export default function SettingsPage() {
  const [tab, setTab] = useState<Tab>('notifications')
  const { theme, setTheme } = useTheme()
  const { user } = useAuth()
  const [notifs, setNotifs] = useState({ push: true, sms: true, email: true, emergency: true })
  const [lang, setLang] = useState('en')

  return (
    <div className="max-w-2xl">
      <PageHeader title="Settings" subtitle="Manage your preferences and account settings" />

      <div className="flex gap-6">
        {/* Sidebar tabs */}
        <nav className="hidden sm:flex flex-col gap-1 w-44 shrink-0">
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={cn('flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm font-medium text-left transition-colors', tab === t.id
                ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400'
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700/50'
              )}>
              <t.icon className="h-4 w-4" />
              {t.label}
            </button>
          ))}
        </nav>

        {/* Mobile tabs */}
        <div className="flex sm:hidden gap-1 mb-4 flex-wrap">
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={cn('flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors', tab === t.id ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400')}>
              <t.icon className="h-3.5 w-3.5" />{t.label}
            </button>
          ))}
        </div>

        {/* Panel */}
        <div className="flex-1 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 shadow-sm">
          {tab === 'notifications' && (
            <div>
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1">Notification Preferences</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">Choose how you receive alerts</p>
              <div className="divide-y divide-gray-100 dark:divide-gray-700">
                <Toggle checked={notifs.push} onChange={v => setNotifs({...notifs, push: v})} label="Push Notifications" />
                <Toggle checked={notifs.sms} onChange={v => setNotifs({...notifs, sms: v})} label="SMS Alerts" />
                <Toggle checked={notifs.email} onChange={v => setNotifs({...notifs, email: v})} label="Email Updates" />
                <div className="flex items-center justify-between py-3">
                  <div>
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Emergency Broadcasts</span>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Cannot be disabled</p>
                  </div>
                  <span className="rounded-full bg-green-100 dark:bg-green-900/30 px-2 py-0.5 text-xs font-semibold text-green-700 dark:text-green-400">Always On</span>
                </div>
              </div>
            </div>
          )}

          {tab === 'appearance' && (
            <div>
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1">Appearance</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-5">Choose your preferred theme</p>
              <div className="grid grid-cols-3 gap-3">
                {THEMES.map(t => (
                  <button key={t.value} onClick={() => setTheme(t.value)}
                    className={cn('flex flex-col items-center gap-2 rounded-xl border-2 p-4 transition-all', theme === t.value
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                    )}>
                    <t.icon className={cn('h-6 w-6', theme === t.value ? 'text-blue-600' : 'text-gray-500')} />
                    <span className="text-sm font-medium text-gray-900 dark:text-white">{t.label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {tab === 'language' && (
            <div>
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1">Language</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-5">Select your preferred language</p>
              <div className="space-y-2">
                {LANGUAGES.map(l => (
                  <label key={l.code} className={cn('flex cursor-pointer items-center gap-3 rounded-xl border-2 p-3 transition-all', lang === l.code ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'border-gray-200 dark:border-gray-700 hover:border-gray-300')}>
                    <input type="radio" name="language" value={l.code} checked={lang === l.code} onChange={() => setLang(l.code)} className="sr-only" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">{l.label}</p>
                      <p className="text-xs text-gray-500">{l.native}</p>
                    </div>
                    {lang === l.code && <div className="h-4 w-4 rounded-full bg-blue-600 flex items-center justify-center"><div className="h-2 w-2 rounded-full bg-white" /></div>}
                  </label>
                ))}
              </div>
            </div>
          )}

          {tab === 'security' && (
            <div>
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1">Security</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-5">Manage your account security</p>
              <div className="space-y-3">
                <div className="flex items-center justify-between rounded-xl border border-gray-200 dark:border-gray-700 p-4">
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">Two-Factor Authentication</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Add an extra layer of security</p>
                  </div>
                  <span className={cn('rounded-full px-3 py-1 text-xs font-semibold', user?.mfaEnabled ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400')}>
                    {user?.mfaEnabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
                <button className="w-full rounded-xl border border-gray-200 dark:border-gray-700 p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">Change Password</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Update your account password</p>
                </button>
                <button className="w-full rounded-xl border border-red-200 dark:border-red-800 p-4 text-left hover:bg-red-50 dark:hover:bg-red-900/10 transition-colors">
                  <p className="text-sm font-medium text-red-600 dark:text-red-400">Delete Account</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Permanently delete your account and data</p>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
