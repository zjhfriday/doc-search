import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { UserInfo } from '@/api/types'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const user = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() =>
    user.value?.role === 'super_admin' || user.value?.role === 'manager'
  )

  async function login(username: string, password: string) {
    const res = await authApi.login({ username, password })
    token.value = res.access_token
    user.value = res.user
    localStorage.setItem('token', res.access_token)
  }

  async function fetchUserInfo() {
    if (!token.value) return
    try {
      user.value = await authApi.getMe()
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return { token, user, isLoggedIn, isAdmin, login, fetchUserInfo, logout }
})
