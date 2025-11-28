<template>
  <div class="login-container">
    <div class="login-box">
      <h2 class="login-title"><i class="fas fa-hotel"></i> 波普特酒店管理系统</h2>
      
      <div v-if="errorMsg" class="status-message status-error" style="display: block">
        {{ errorMsg }}
      </div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label><i class="fas fa-user-tag"></i> 登录身份</label>
          <select v-model="form.role" class="form-control" required @change="handleRoleChange">
            <option value="resident">住户 (客房端)</option>
            <option value="reception">前台 (营业端)</option>
            <option value="admin">管理员 (监控端)</option>
          </select>
        </div>

        <div class="form-group" v-if="form.role === 'resident'">
          <label><i class="fas fa-door-open"></i> 选择房间</label>
          <select v-model="form.roomId" class="form-control" required>
            <option value="" disabled>请选择您要入住/管理的房间</option>
            <option v-for="room in hotelStore.rooms" :key="room.id" :value="room.id">
              {{ room.id }}号房 - {{ getRoomStatusText(room) }}
            </option>
          </select>
        </div>

        <div class="form-group" v-if="form.role !== 'resident'">
          <label><i class="fas fa-user"></i> 用户名</label>
          <input type="text" v-model="form.username" class="form-control" placeholder="admin / reception" required>
        </div>

        <div class="form-group" v-if="form.role !== 'resident'">
          <label><i class="fas fa-lock"></i> 密码</label>
          <input type="password" v-model="form.password" class="form-control" placeholder="默认: password" required>
        </div>

        <button type="submit" class="btn" :disabled="loading">
          <i class="fas" :class="loading ? 'fa-spinner fa-spin' : 'fa-sign-in-alt'"></i> 
          {{ loading ? '登录中...' : '进入系统' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth'
import { useHotelStore } from '@/store/modules/hotel'

const router = useRouter()
const authStore = useAuthStore()
const hotelStore = useHotelStore()

const loading = ref(false)
const errorMsg = ref('')

const form = reactive({
  role: 'resident',
  roomId: '',
  username: '',
  password: ''
})

const getRoomStatusText = (room) => {
  if (room.status === 'free') return '空闲 (可预订)'
  if (room.status === 'occupied') return `使用中 (${room.guest?.name || '未知'})`
  return '未知状态'
}

const handleRoleChange = () => {
  // 切换角色时清空不相关数据
  if (form.role === 'resident') {
    form.username = 'resident'
    form.password = '123'
  } else {
    form.roomId = ''
    form.username = ''
    form.password = ''
  }
}

const handleLogin = async () => {
  loading.value = true
  errorMsg.value = ''
  
  try {
    // 如果是住户，用户名直接设为房间号，方便记忆
    if (form.role === 'resident') {
      form.username = `Room ${form.roomId}`
    }

    await authStore.login(form)
    
    const redirectMap = {
      resident: '/resident/dashboard',
      reception: '/reception/dashboard',
      admin: '/admin/dashboard'
    }
    router.push(redirectMap[form.role] || '/')
  } catch (error) {
    errorMsg.value = '登录失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>