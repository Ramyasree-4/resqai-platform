import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import type { UserRole } from '@/types'

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRoles?: UserRole[]
  redirectTo?: string
}

export function ProtectedRoute({
  children,
  requiredRoles,
  redirectTo = '/login',
}: ProtectedRouteProps) {
  const { user, isLoading, isAuthenticated } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return <LoadingSpinner fullScreen />
  }

  if (!isAuthenticated) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />
  }

  if (requiredRoles && user && !requiredRoles.includes(user.role)) {
    // Redirect to their appropriate dashboard
    if (user.role === 'CITIZEN') return <Navigate to="/dashboard" replace />
    if (['AUTHORITY', 'DISTRICT_OFFICER', 'STATE_OFFICER', 'NGO', 'VOLUNTEER'].includes(user.role)) {
      return <Navigate to="/authority" replace />
    }
    if (user.role === 'ADMIN') return <Navigate to="/admin" replace />
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}
