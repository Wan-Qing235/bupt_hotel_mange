<template>
  <div class="layout-wrapper">
    <header class="top-header">
      <div class="logo-area">
        <i class="fas fa-wind"></i>
        <span>波普特酒店</span>
      </div>
      
      <div class="user-area">
        <span class="role-tag">{{ roleName }}</span>
        <span class="username">{{ authStore.username }}</span>
        <button class="logout-btn" @click="handleLogout">
          <i class="fas fa-sign-out-alt"></i> 退出
        </button>
      </div>
    </header>
    
    <div class="main-body">
      <aside class="sidebar">
        <div class="menu-list">
          <div 
            v-for="item in menuItems" 
            :key="item.path"
            class="menu-item"
            :class="{ active: currentRoute.path.includes(item.path) }"
            @click="navigate(item.path)"
          >
            <i :class="item.icon"></i>
            <span>{{ item.title }}</span>
          </div>
        </div>
      </aside>
      
      <main class="content-area">
        <div class="content-wrapper">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/store/modules/auth'
import { useRouter, useRoute } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const currentRoute = useRoute()

// 角色名称映射
const roleName = computed(() => {
  const map = { resident: '住户端', reception: '前台端', admin: '管理端' }
  return map[authStore.userRole] || '访客'
})

// === 关键修改：更新菜单列表以匹配最新路由 ===
const menuItems = computed(() => {
  const role = authStore.userRole
  const menus = []

  if (role === 'resident') {
    menus.push(
      { title: '空调控制', icon: 'fas fa-thermometer-half', path: '/resident/dashboard' },
      { title: '结账请求', icon: 'fas fa-file-invoice-dollar', path: '/resident/checkout-request' },
      { title: '使用详单', icon: 'fas fa-receipt', path: '/resident/usage-details' }
    )
  } else if (role === 'reception') {
    menus.push(
      { title: '工作台', icon: 'fas fa-tachometer-alt', path: '/reception/dashboard' },
      { title: '办理入住', icon: 'fas fa-check-in', path: '/reception/checkin' },
      { title: '办理结账', icon: 'fas fa-check-out', path: '/reception/checkout' },
      // 新增：房间状态监控
      { title: '房间状态', icon: 'fas fa-door-open', path: '/reception/room-status' }
    )
  } else if (role === 'admin') {
    menus.push(
      { title: '系统仪表盘', icon: 'fas fa-tachometer-alt', path: '/admin/dashboard' },
      { title: '房间管理', icon: 'fas fa-door-open', path: '/admin/room-manage' },
      { title: '系统设置', icon: 'fas fa-cogs', path: '/admin/sys-manage' }
    )
  }
  return menus
})

const navigate = (path) => {
  router.push(path)
}

const handleLogout = () => {
  authStore.logout()
}
</script>

<style scoped>
/* 1. 布局容器 */
.layout-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background-color: #f5f7fa;
}

/* 2. 顶部导航 */
.top-header {
  height: 60px;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  z-index: 100;
  flex-shrink: 0;
}

.logo-area {
  font-size: 20px;
  font-weight: bold;
  color: #2a5298;
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 15px;
}

.role-tag {
  background: #e6efff;
  color: #2a5298;
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: 600;
}

.logout-btn {
  border: 1px solid #eee;
  background: white;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

/* 3. 主体区域 */
.main-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 左侧边栏 (样式已重置) */
.sidebar {
  width: 240px;
  background: white;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  
  position: static !important;
  top: auto !important;
  height: auto !important;
  margin: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  padding: 10px 0 0 0 !important;
}

.menu-item {
  padding: 15px 25px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #666;
  cursor: pointer;
  transition: all 0.3s;
  border-left: 3px solid transparent;
}

.menu-item:hover {
  background-color: #f8f9fa;
  color: #2a5298;
}

.menu-item.active {
  background-color: #e6efff;
  color: #2a5298;
  border-left-color: #2a5298;
  font-weight: 600;
}

/* 4. 右侧内容区 */
.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f7fa;
}

/* 内容容器宽度限制 */
.content-wrapper {
  width: 60%;
  max-width: 800px;
  min-width: 500px;
  margin: 0 auto;
}

/* 动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>