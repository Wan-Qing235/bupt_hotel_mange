import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const userRole = ref(localStorage.getItem('userRole') || '') 
  const username = ref(localStorage.getItem('username') || '')
  // [新增] 记录当前登录的房间号 (仅对 resident 有效)
  const roomId = ref(localStorage.getItem('roomId') || '')

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  
  const hasRole = (role) => userRole.value === role || userRole.value === 'admin'

  // Actions
  function login(loginForm) {
    return new Promise((resolve) => {
      setTimeout(() => {
        token.value = 'mock-token-123'
        userRole.value = loginForm.role
        username.value = loginForm.username
        // [新增] 保存房间号
        roomId.value = loginForm.roomId || ''
        
        // 持久化
        localStorage.setItem('token', token.value)
        localStorage.setItem('userRole', userRole.value)
        localStorage.setItem('username', username.value)
        localStorage.setItem('roomId', roomId.value)
        
        resolve(true)
      }, 500)
    })
  }

  function logout() {
    token.value = ''
    userRole.value = ''
    username.value = ''
    roomId.value = ''
    localStorage.clear()
    router.push('/login')
  }

  return { 
    token, userRole, username, roomId, // 记得导出 roomId
    isAuthenticated, hasRole, 
    login, logout 
  }
})