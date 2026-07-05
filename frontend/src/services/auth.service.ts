import api from './api'
import { API_ENDPOINTS } from '@/utils/constants'
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
  UpdateProfileRequest,
} from '@/types'

export const authService = {
  async login(email: string, password: string): Promise<TokenResponse> {
    const res = await api.post<{ success: boolean; data: TokenResponse }>(
      API_ENDPOINTS.AUTH_LOGIN,
      { email, password }
    )
    return res.data.data
  },

  async register(data: RegisterRequest): Promise<TokenResponse> {
    const res = await api.post<{ success: boolean; data: TokenResponse }>(
      API_ENDPOINTS.AUTH_REGISTER,
      data
    )
    return res.data.data
  },

  async refreshToken(refreshToken: string): Promise<{ token: string; expiresIn: number }> {
    const res = await api.post<{
      success: boolean
      data: { token: string; expiresIn: number }
    }>(API_ENDPOINTS.AUTH_REFRESH, { refreshToken })
    return res.data.data
  },

  async logout(): Promise<void> {
    await api.post(API_ENDPOINTS.AUTH_LOGOUT)
    localStorage.removeItem('resqai_token')
    localStorage.removeItem('resqai_refresh_token')
    localStorage.removeItem('resqai_user')
  },

  async getMe(): Promise<User> {
    const res = await api.get<{ success: boolean; data: User }>(API_ENDPOINTS.AUTH_ME)
    return res.data.data
  },

  async updateProfile(data: UpdateProfileRequest): Promise<User> {
    const res = await api.put<{ success: boolean; data: User }>(
      API_ENDPOINTS.AUTH_PROFILE,
      data
    )
    return res.data.data
  },

  async forgotPassword(email: string): Promise<void> {
    await api.post(API_ENDPOINTS.AUTH_FORGOT_PASSWORD, { email })
  },

  async registerFcmToken(token: string): Promise<void> {
    await api.post(API_ENDPOINTS.AUTH_FCM_TOKEN, { token })
  },
}
