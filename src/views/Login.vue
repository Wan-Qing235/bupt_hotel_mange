<template>
  <div class="login-wrapper">
    <!-- 动态背景装饰 -->
    <div class="bg-shape shape-1"></div>
    <div class="bg-shape shape-2"></div>

    <div class="login-card">
      <!-- 左侧品牌区 -->
      <div class="brand-side">
        <div class="logo-container">
          <i class="fas fa-wind logo-icon"></i>
        </div>
        <h1 class="brand-title">BUPT HOTEL</h1>
        <p class="brand-subtitle">智能中央温控管理系统</p>
        <div class="brand-footer">
          <p>© 2025 Smart Control</p>
        </div>
      </div>
      
      <!-- 右侧表单区 -->
      <div class="form-side">
        <div class="form-header">
          <h2>欢迎登录</h2>
          <p>请选择您的身份以继续</p>
        </div>

        <!-- 错误提示 -->
        <transition name="fade">
          <div v-if="errorMsg" class="error-banner">
            <i class="fas fa-exclamation-circle"></i>
            <span>{{ errorMsg }}</span>
          </div>
        </transition>

        <form @submit.prevent="handleLogin" class="login-form">
          <!-- 1. 角色选择 -->
          <div class="input-group">
            <label>登录身份</label>
            <div class="input-wrapper select-wrapper">
              <i class="fas fa-user-tag input-icon"></i>
              <select v-model="form.role" class="custom-input" @change="handleRoleChange">
                <option value="resident">住户 (Guest)</option>
                <option value="reception">前台 (Reception)</option>
                <option value="admin">管理员 (Admin)</option>
              </select>
              <i class="fas fa-chevron-down select-arrow"></i>
            </div>
          </div>

          <!-- 2. 房间选择 (仅住户) -->
          <transition name="slide-down">
            <div class="input-group" v-if="form.role === 'resident'">
              <label>选择房间</label>
              <div class="input-wrapper select-wrapper">
                <i class="fas fa-door-open input-icon"></i>
                <select v-model="form.roomId" class="custom-input">
                  <option value="" disabled>请选择房间...</option>
                  <option v-for="room in hotelStore.rooms" :key="room.id" :value="room.id">
                    {{ room.id }} 号房 - {{ getRoomStatusText(room) }}
                  </option>
                </select>
                <i class="fas fa-chevron-down select-arrow"></i>
              </div>
            </div>
          </transition>

          <!-- 3. 账号密码 (非住户) -->
          <transition name="slide-down">
            <div v-if="form.role !== 'resident'">
              <div class="input-group">
                <label>管理账号</label>
                <div class="input-wrapper">
                  <i class="fas fa-user input-icon"></i>
                  <input 
                    type="text" 
                    v-model="form.username" 
                    class="custom-input" 
                    placeholder="请输入用户名"
                    required
                  >
                </div>
              </div>

              <div class="input-group">
                <label>密码</label>
                <div class="input-wrapper">
                  <i class="fas fa-lock input-icon"></i>
                  <input 
                    type="password" 
                    v-model="form.password" 
                    class="custom-input" 
                    placeholder="请输入密码"
                    required
                  >
                </div>
              </div>
            </div>
          </transition>

          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="!loading">进入系统 <i class="fas fa-arrow-right"></i></span>
            <span v-else><i class="fas fa-circle-notch fa-spin"></i> 登录中...</span>
          </button>
        </form>
      </div>
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
  if (room.status === 'free') return '空闲'
  if (room.status === 'occupied') return '使用中'
  return '未知'
}

const handleRoleChange = () => {
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
    if (form.role === 'resident') {
      if (!form.roomId) throw new Error('请选择一个房间')
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
    errorMsg.value = error.message || '登录失败，请检查网络或账号'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 1. 整体布局与背景 */
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  position: relative;
  overflow: hidden;
  padding: 20px;
}

/* 动态背景球 */
.bg-shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: 0;
  opacity: 0.6;
}
.shape-1 {
  width: 400px;
  height: 400px;
  background: #4f46e5;
  top: -100px;
  left: -100px;
  animation: float 10s infinite ease-in-out;
}
.shape-2 {
  width: 300px;
  height: 300px;
  background: #818cf8;
  bottom: -50px;
  right: -50px;
  animation: float 15s infinite ease-in-out reverse;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, 50px); }
}

/* 2. 登录卡片 (左右布局) */
.login-card {
  display: flex;
  width: 900px;
  height: 550px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  z-index: 1;
  backdrop-filter: blur(20px);
}

/* 左侧品牌区 */
.brand-side {
  flex: 0.8;
  background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 40px;
  text-align: center;
}

.logo-container {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  backdrop-filter: blur(5px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.logo-icon { font-size: 40px; color: white; }
.brand-title { font-size: 2.5rem; font-weight: 800; letter-spacing: 2px; margin-bottom: 10px; }
.brand-subtitle { font-size: 1.1rem; opacity: 0.9; font-weight: 300; letter-spacing: 1px; }
.brand-footer { position: absolute; bottom: 30px; font-size: 0.8rem; opacity: 0.6; }

/* 右侧表单区 */
.form-side {
  flex: 1.2;
  padding: 50px 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: white;
}

.form-header h2 { font-size: 2rem; color: #1e293b; margin-bottom: 5px; font-weight: 700; }
.form-header p { color: #64748b; margin-bottom: 30px; }

/* 3. 表单组件 */
.input-group { margin-bottom: 20px; }
.input-group label { display: block; font-size: 0.9rem; font-weight: 600; color: #374151; margin-bottom: 8px; }

.input-wrapper { position: relative; display: flex; align-items: center; }
.input-icon { position: absolute; left: 16px; color: #9ca3af; font-size: 1.1rem; z-index: 2; }

.custom-input {
  width: 100%;
  padding: 14px 16px 14px 45px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 1rem;
  color: #1e293b;
  background: #f8fafc;
  transition: all 0.3s ease;
  appearance: none; /* 去除原生select样式 */
}

.custom-input:focus {
  outline: none;
  border-color: #4f46e5;
  background: white;
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1);
}

.select-wrapper .select-arrow {
  position: absolute; right: 16px; color: #64748b; pointer-events: none; font-size: 0.9rem;
}

/* 按钮 */
.submit-btn {
  width: 100%;
  padding: 16px;
  margin-top: 10px;
  background: #4f46e5;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.3);
}

.submit-btn:hover {
  background: #4338ca;
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.4);
}

.submit-btn:disabled { background: #94a3b8; transform: none; box-shadow: none; cursor: not-allowed; }

/* 错误提示 */
.error-banner {
  background: #fee2e2; color: #ef4444; padding: 12px 16px; border-radius: 8px; margin-bottom: 20px;
  display: flex; align-items: center; gap: 10px; font-size: 0.9rem; border: 1px solid #fca5a5;
}

/* 响应式 */
@media (max-width: 900px) {
  .login-card { width: 100%; height: auto; flex-direction: column; margin: 20px; }
  .brand-side { padding: 40px 20px; }
  .form-side { padding: 40px 30px; }
}

/* 动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.3s ease; max-height: 200px; opacity: 1; overflow: hidden; }
.slide-down-enter-from, .slide-down-leave-to { max-height: 0; opacity: 0; transform: translateY(-10px); }
</style>