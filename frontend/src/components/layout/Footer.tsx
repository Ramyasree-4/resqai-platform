import { Shield } from 'lucide-react'

export function Footer() {
  return (
    <footer className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 py-4 px-6">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <Shield className="w-4 h-4 text-red-600" />
          <span className="font-semibold text-gray-900 dark:text-white">
            ResQ<span className="text-blue-600">AI</span>
          </span>
          <span>— AI-Powered Disaster Response</span>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-500">
          © {new Date().getFullYear()} ResQAI. All rights reserved.
        </p>
      </div>
    </footer>
  )
}
