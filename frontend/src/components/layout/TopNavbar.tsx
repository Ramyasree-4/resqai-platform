import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Menu,
  Search,
  Sun,
  Moon,
  User,
  Settings,
  LogOut,
  ChevronDown,
} from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { useTheme } from '@/contexts/ThemeContext'
import { NotificationBell } from '@/components/common/NotificationBell'
import { cn } from '@/utils/cn'

const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/report': 'Report Incident',
  '/my-reports': 'My Reports',
  '/authority': 'Operations Dashboard',
  '/authority/incidents': 'Incident Queue',
  '/authority/resources': 'Resource Management',
  '/authority/analytics': 'Analytics',
  '/authority/map': 'Map View',
  '/admin': 'Admin Dashboard',
  '/notifications': 'Notifications',
  '/profile': 'Profile',
  '/settings': 'Settings',
}

interface TopNavbarProps {
  onMenuClick: () => void
  sidebarCollapsed?: boolean
}

export function TopNavbar({ onMenuClick }: TopNavbarProps) {
  const { user, logout } = useAuth()
  const { resolvedTheme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const location = useLocation()
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const pageTitle =
    PAGE_TITLES[location.pathname] ??
    (location.pathname.startsWith('/track/') ? 'Track Incident' : 'ResQAI')

  const handleLogout = async () => {
    setUserMenuOpen(false)
    await logout()
    navigate('/login')
  }

  return (
    <header className="sticky top-0 z-10 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 h-16 flex items-center px-4 gap-3">
      {/* Hamburger */}
      <button
        onClick={onMenuClick}
        className="lg:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800"
      >
        <Menu className="w-5 h-5" />
      </button>

      {/* Page title */}
      <h1 className="text-lg font-semibold text-gray-900 dark:text-white hidden sm:block">
        {pageTitle}
      </h1>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Search */}
      <div className="hidden md:flex items-center bg-gray-100 dark:bg-gray-800 rounded-lg px-3 py-2 gap-2 w-64">
        <Search className="w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search incidents..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="bg-transparent text-sm text-gray-700 dark:text-gray-300 placeholder-gray-400 outline-none flex-1"
        />
      </div>

      {/* Notification bell */}
      <NotificationBell />

      {/* Dark mode toggle */}
      <button
        onClick={toggleTheme}
        className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        title={resolvedTheme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
      >
        {resolvedTheme === 'dark' ? (
          <Sun className="w-5 h-5" />
        ) : (
          <Moon className="w-5 h-5" />
        )}
      </button>

      {/* User avatar dropdown */}
      <div className="relative">
        <button
          onClick={() => setUserMenuOpen((o) => !o)}
          className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-bold">
            {user?.displayName?.charAt(0).toUpperCase() ?? 'U'}
          </div>
          <ChevronDown className="w-4 h-4 text-gray-500 hidden sm:block" />
        </button>

        {userMenuOpen && (
          <>
            <div
              className="fixed inset-0 z-10"
              onClick={() => setUserMenuOpen(false)}
            />
            <div className={cn(
              'absolute right-0 top-full mt-1 w-56 bg-white dark:bg-gray-900',
              'rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 z-20',
              'py-1 animate-slide-in'
            )}>
              <div className="px-4 py-2.5 border-b border-gray-100 dark:border-gray-800">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {user?.displayName}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                  {user?.email}
                </p>
              </div>
              <button
                onClick={() => { setUserMenuOpen(false); navigate('/profile') }}
                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800"
              >
                <User className="w-4 h-4" />
                Profile
              </button>
              <button
                onClick={() => { setUserMenuOpen(false); navigate('/settings') }}
                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800"
              >
                <Settings className="w-4 h-4" />
                Settings
              </button>
              <div className="border-t border-gray-100 dark:border-gray-800 mt-1" />
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
              >
                <LogOut className="w-4 h-4" />
                Sign out
              </button>
            </div>
          </>
        )}
      </div>
    </header>
  )
}
