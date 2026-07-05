import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  AlertTriangle,
  FileText,
  Map,
  Bell,
  Users,
  BarChart3,
  Settings,
  Shield,
  Package,
  ChevronLeft,
  ChevronRight,
  X,
  Megaphone,
} from 'lucide-react'
import { cn } from '@/utils/cn'
import { useAuth } from '@/hooks/useAuth'
import { USER_ROLES } from '@/utils/constants'

interface NavItem {
  label: string
  icon: React.ComponentType<{ className?: string }>
  to: string
}

const citizenNav: NavItem[] = [
  { label: 'Dashboard', icon: LayoutDashboard, to: '/dashboard' },
  { label: 'Report Incident', icon: AlertTriangle, to: '/report' },
  { label: 'My Reports', icon: FileText, to: '/my-reports' },
  { label: 'Notifications', icon: Bell, to: '/notifications' },
]

const authorityNav: NavItem[] = [
  { label: 'Dashboard', icon: LayoutDashboard, to: '/authority' },
  { label: 'Incident Queue', icon: AlertTriangle, to: '/authority/incidents' },
  { label: 'Resources', icon: Package, to: '/authority/resources' },
  { label: 'Analytics', icon: BarChart3, to: '/authority/analytics' },
  { label: 'Map View', icon: Map, to: '/authority/map' },
  { label: 'Notifications', icon: Bell, to: '/notifications' },
]

const adminNav: NavItem[] = [
  { label: 'Dashboard', icon: LayoutDashboard, to: '/admin' },
  { label: 'Manage Users', icon: Users, to: '/admin/users' },
  { label: 'Resources', icon: Package, to: '/authority/resources' },
  { label: 'Analytics', icon: BarChart3, to: '/authority/analytics' },
  { label: 'Broadcast', icon: Megaphone, to: '/notifications' },
  { label: 'Settings', icon: Settings, to: '/settings' },
]

interface SidebarProps {
  isOpen: boolean
  isCollapsed: boolean
  onClose: () => void
  onToggleCollapse: () => void
}

export function Sidebar({ isOpen, isCollapsed, onClose, onToggleCollapse }: SidebarProps) {
  const { user } = useAuth()
  const location = useLocation()

  let navItems: NavItem[] = citizenNav
  if (user?.role === 'ADMIN') navItems = adminNav
  else if (
    ['AUTHORITY', 'DISTRICT_OFFICER', 'STATE_OFFICER', 'NGO', 'VOLUNTEER'].includes(
      user?.role ?? ''
    )
  ) {
    navItems = authorityNav
  }

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-30 h-full bg-white dark:bg-gray-900',
        'border-r border-gray-200 dark:border-gray-800',
        'flex flex-col transition-all duration-300',
        // Desktop
        'hidden lg:flex',
        isCollapsed ? 'lg:w-16' : 'lg:w-64',
        // Mobile
        'lg:relative lg:translate-x-0',
        isOpen
          ? 'flex translate-x-0 w-64'
          : '-translate-x-full'
      )}
    >
      {/* Logo */}
      <div className="flex items-center justify-between px-4 py-4 border-b border-gray-200 dark:border-gray-800 min-h-[64px]">
        <div className={cn('flex items-center gap-3', isCollapsed && 'lg:justify-center')}>
          <div className="w-9 h-9 rounded-full bg-red-600 flex items-center justify-center flex-shrink-0">
            <Shield className="w-5 h-5 text-white" />
          </div>
          {!isCollapsed && (
            <span className="text-lg font-bold text-gray-900 dark:text-white">
              ResQ<span className="text-blue-600">AI</span>
            </span>
          )}
        </div>
        <button
          onClick={onClose}
          className="lg:hidden p-1 rounded-md text-gray-400 hover:text-gray-600"
        >
          <X className="w-5 h-5" />
        </button>
        <button
          onClick={onToggleCollapse}
          className="hidden lg:flex p-1 rounded-md text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        >
          {isCollapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronLeft className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto scrollbar-thin">
        {navItems.map((item) => {
          const isActive =
            item.to === location.pathname ||
            (item.to !== '/dashboard' &&
              item.to !== '/authority' &&
              item.to !== '/admin' &&
              location.pathname.startsWith(item.to))

          return (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={onClose}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isCollapsed && 'lg:justify-center lg:px-2',
                isActive
                  ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400'
                  : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
              )}
              title={isCollapsed ? item.label : undefined}
            >
              <item.icon
                className={cn(
                  'flex-shrink-0 w-5 h-5',
                  isActive ? 'text-blue-600 dark:text-blue-400' : ''
                )}
              />
              {!isCollapsed && <span>{item.label}</span>}
            </NavLink>
          )
        })}
      </nav>

      {/* User role badge */}
      {!isCollapsed && user && (
        <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
              {user.displayName.charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                {user.displayName}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {USER_ROLES[user.role]}
              </p>
            </div>
          </div>
        </div>
      )}
    </aside>
  )
}
