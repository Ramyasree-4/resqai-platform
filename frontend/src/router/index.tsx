import { Routes, Route, Navigate } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import { ProtectedRoute } from './ProtectedRoute'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { AppShell } from '@/components/layout/AppShell'
import { useAuth } from '@/hooks/useAuth'

// Public pages
const LandingPage = lazy(() => import('@/pages/public/LandingPage'))
const LoginPage = lazy(() => import('@/pages/public/LoginPage'))
const RegisterPage = lazy(() => import('@/pages/public/RegisterPage'))
const ForgotPasswordPage = lazy(() => import('@/pages/public/ForgotPasswordPage'))

// Citizen pages
const CitizenDashboard = lazy(() => import('@/pages/citizen/CitizenDashboard'))
const ReportIncidentPage = lazy(() => import('@/pages/citizen/ReportIncidentPage'))
const MyReportsPage = lazy(() => import('@/pages/citizen/MyReportsPage'))
const IncidentTrackerPage = lazy(() => import('@/pages/citizen/IncidentTrackerPage'))

// Authority pages
const AuthorityDashboard = lazy(() => import('@/pages/authority/AuthorityDashboard'))
const IncidentQueuePage = lazy(() => import('@/pages/authority/IncidentQueuePage'))
const IncidentDetailsPage = lazy(() => import('@/pages/authority/IncidentDetailsPage'))
const ResourceManagementPage = lazy(() => import('@/pages/authority/ResourceManagementPage'))
const AnalyticsPage = lazy(() => import('@/pages/authority/AnalyticsPage'))
const MapViewPage = lazy(() => import('@/pages/authority/MapViewPage'))

// Admin
const AdminDashboard = lazy(() => import('@/pages/admin/AdminDashboard'))

// Shared pages
const NotificationsPage = lazy(() => import('@/pages/shared/NotificationsPage'))
const ProfilePage = lazy(() => import('@/pages/shared/ProfilePage'))
const SettingsPage = lazy(() => import('@/pages/shared/SettingsPage'))
const NotFoundPage = lazy(() => import('@/pages/shared/NotFoundPage'))

const AUTHORITY_ROLES = [
  'AUTHORITY',
  'DISTRICT_OFFICER',
  'STATE_OFFICER',
  'NGO',
  'VOLUNTEER',
  'ADMIN',
] as const

function RootRedirect() {
  const { user, isAuthenticated, isLoading } = useAuth()
  // Show loading spinner briefly, then redirect
  if (isLoading) return <LoadingSpinner fullScreen text="Starting ResQAI..." />
  if (!isAuthenticated) return <Navigate to="/landing" replace />
  if (user?.role === 'CITIZEN') return <Navigate to="/dashboard" replace />
  if (user?.role === 'ADMIN') return <Navigate to="/admin" replace />
  return <Navigate to="/authority" replace />
}

export function AppRoutes() {
  return (
    <Suspense fallback={<LoadingSpinner fullScreen />}>
      <Routes>
        {/* Root */}
        <Route path="/" element={<RootRedirect />} />

        {/* Public */}
        <Route path="/landing" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />

        {/* Authenticated layout */}
        <Route
          element={
            <ProtectedRoute>
              <AppShell />
            </ProtectedRoute>
          }
        >
          {/* Citizen routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute requiredRoles={['CITIZEN']}>
                <CitizenDashboard />
              </ProtectedRoute>
            }
          />
          <Route path="/report" element={<ReportIncidentPage />} />
          <Route path="/my-reports" element={<MyReportsPage />} />
          <Route path="/track/:id" element={<IncidentTrackerPage />} />

          {/* Authority routes */}
          <Route
            path="/authority"
            element={
              <ProtectedRoute requiredRoles={[...AUTHORITY_ROLES]}>
                <AuthorityDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/authority/incidents"
            element={
              <ProtectedRoute requiredRoles={[...AUTHORITY_ROLES]}>
                <IncidentQueuePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/authority/incidents/:id"
            element={
              <ProtectedRoute requiredRoles={[...AUTHORITY_ROLES]}>
                <IncidentDetailsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/authority/resources"
            element={
              <ProtectedRoute requiredRoles={[...AUTHORITY_ROLES]}>
                <ResourceManagementPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/authority/analytics"
            element={
              <ProtectedRoute requiredRoles={[...AUTHORITY_ROLES]}>
                <AnalyticsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/authority/map"
            element={
              <ProtectedRoute requiredRoles={[...AUTHORITY_ROLES]}>
                <MapViewPage />
              </ProtectedRoute>
            }
          />

          {/* Admin routes */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute requiredRoles={['ADMIN']}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />

          {/* Shared routes */}
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>

        {/* 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Suspense>
  )
}
