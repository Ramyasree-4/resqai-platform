import { Link } from 'react-router-dom'
import { Shield, ArrowLeft, Home } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'

export default function NotFoundPage() {
  const { isAuthenticated, user } = useAuth()
  const home = !isAuthenticated ? '/landing' : user?.role === 'CITIZEN' ? '/dashboard' : user?.role === 'ADMIN' ? '/admin' : '/authority'

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-950 px-4 text-center">
      <Link to="/landing" className="flex items-center gap-2 mb-10">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600">
          <Shield className="h-5 w-5 text-white" />
        </div>
        <span className="text-xl font-bold text-gray-900 dark:text-white">ResQAI</span>
      </Link>

      <div className="text-8xl font-black text-gray-200 dark:text-gray-800 mb-4">404</div>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Page Not Found</h1>
      <p className="text-gray-500 dark:text-gray-400 max-w-sm mb-8">
        The page you're looking for doesn't exist or has been moved.
      </p>

      <div className="flex gap-3">
        <button onClick={() => window.history.back()}
          className="flex items-center gap-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-5 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
          <ArrowLeft className="h-4 w-4" /> Go Back
        </button>
        <Link to={home}
          className="flex items-center gap-2 rounded-lg bg-blue-600 hover:bg-blue-700 px-5 py-2.5 text-sm font-semibold text-white transition-colors">
          <Home className="h-4 w-4" /> Go Home
        </Link>
      </div>
    </div>
  )
}
