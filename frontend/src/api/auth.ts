import request from './request'
import type { LoginResponse, UserInfo } from './types'

export const authApi = {
  login(data: { username: string; password: string }): Promise<LoginResponse> {
    return request.post('/auth/login', data)
  },

  getMe(): Promise<UserInfo> {
    return request.get('/auth/me')
  },
}
