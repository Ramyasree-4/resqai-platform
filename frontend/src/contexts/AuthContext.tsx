import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { authService } from '@/services/auth.service'
import type { User, RegisterRequest } from '@/types'
import { toast } from 'sonner'

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<User>
  register: (data: RegisterRequest) => Promise<User>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

function loadStoredUser(): User | null {
  try {
    const stored = localStorage.getItem('resqai_user')
    return stored ? (JSON.parse(stored) as User) : null
  } catch {
    return null
  }
}

function hasStoredToken(): boolean {
  const token = localStorage.getItem('resqai_token')
  if (!token) return false
  // Basic JWT expiry check — don't treat expired tokens as valid
  try {
    const [, payload] = token.split('.')
    const decoded = JSON.parse(atob(payload))
    if (decoded.exp && decoded.exp * 1000 < Date.now()) {
      localStorage.removeItem('resqai_token')
      localStorage.removeItem('resqai_user')
      return false
    }
    return true
  } catch {
    return !!token
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(loadStoredUser)
  const [isLoading, setIsLoading] = useState(true)

  const saveSession = useCallback((userData: User, token: string, refreshToken?: string) => {
    localStorage.setItem('resqai_token', token)
    if (refreshToken) localStorage.setItem('resqai_refresh_token', refreshToken)
    localStorage.setItem('resqai_user', JSON.stringify(userData))
    setUser(userData)
  }, [])

  const clearSession = useCallback(() => {
    localStorage.removeItem('resqai_token')
    localStorage.removeItem('resqai_refresh_token')
    localStorage.removeItem('resqai_user')
    setUser(null)
  }, [])

  // On mount: validate stored session
  useEffect(() => {
    const init = async () => {
      const storedUser = loadStoredUser()
      const hasToken = hasStoredToken()

      if (storedUser && hasToken) {
        // Verify token is still valid by fetching profile
        try {
          const profile = await authService.getMe()
          saveSession(profile, localStorage.getItem('resqai_token')!)
        } catch {
          // Token invalid or backend down — keep stored user for UI but clear on 401
          setUser(storedUser)
        }
      } else {
        // Try Firebase auth state as fallback
        try {
          const { onAuthStateChanged } = await import('@/firebase/auth')
          const unsub = onAuthStateChanged(async (firebaseUser) => {
            if (firebaseUser) {
              try {
                const token = await firebaseUser.getIdToken(true)
                localStorage.setItem('resqai_token', token)
                const profile = await authService.getMe()
                saveSession(profile, token)
              } catch {
                setUser(null)
              }
            } else {
              setUser(null)
            }
            setIsLoading(false)
            unsub()
          })
          return
        } catch {
          setUser(null)
        }
      }
      setIsLoading(false)
    }

    init()
  }, [saveSession])

  const login = useCallback(async (email: string, password: string): Promise<User> => {
    setIsLoading(true)
    try {
      const response = await authService.login(email, password)
      const userData = response.user as User
      saveSession(userData, response.token, response.refreshToken)
      return userData
    } finally {
      setIsLoading(false)
    }
  }, [saveSession])

  const register = useCallback(async (data: RegisterRequest): Promise<User> => {
    setIsLoading(true)
    try {
      const response = await authService.register(data)
      const userData = response.user as User
      saveSession(userData, response.token, response.refreshToken)
      return userData
    } finally {
      setIsLoading(false)
    }
  }, [saveSession])

  const logout = useCallback(async () => {
    try { await authService.logout() } catch { /* best effort */ }
    // Also sign out of Firebase if available
    try {
      const { signOut } = await import('@/firebase/auth')
      await signOut()
    } catch { /* ignore */ }
    clearSession()
    toast.success('Logged out successfully')
  }, [clearSession])

  const refreshUser = useCallback(async () => {
    try {
      const profile = await authService.getMe()
      localStorage.setItem('resqai_user', JSON.stringify(profile))
      setUser(profile)
    } catch { /* ignore */ }
  }, [])

  const isAuthenticated = !!user && hasStoredToken()

  return (
    <AuthContext.Provider value={{
      user,
      isLoading,
      isAuthenticated,
      login,
      register,
      logout,
      refreshUser,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuthContext() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuthContext must be used within AuthProvider')
  return ctx
}
