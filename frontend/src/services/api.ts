import axios, { type AxiosInstance, type AxiosError } from 'axios'
import { toast } from 'sonner'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/v1'

export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ── Request Interceptor ──────────────────────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('resqai_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ── Response Interceptor ─────────────────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const status = error.response?.status

    if (status === 401) {
      // Clear auth and redirect to login
      localStorage.removeItem('resqai_token')
      localStorage.removeItem('resqai_refresh_token')
      localStorage.removeItem('resqai_user')

      // Only redirect if not already on an auth page
      if (!window.location.pathname.startsWith('/login') &&
          !window.location.pathname.startsWith('/register')) {
        window.location.href = '/login'
      }
    } else if (status === 403) {
      toast.error('Access denied. You do not have permission to perform this action.')
    } else if (status === 429) {
      toast.error('Too many requests. Please slow down.')
    } else if (status && status >= 500) {
      toast.error('Server error. Please try again later.')
    }

    return Promise.reject(error)
  }
)

export default api
