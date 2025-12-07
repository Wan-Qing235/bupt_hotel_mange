<template>
  <div class="layout-wrapper">
    <!-- 顶部导航 -->
    <header class="top-header">
      <div class="logo-area">
        <div class="logo-box">
          <i class="fas fa-wind"></i>
        </div>
        <span class="logo-text">BUPT <span class="highlight">HOTEL</span></span>
      </div>
      
      <div class="user-area">
        <span class="role-tag" :class="authStore.userRole">{{ roleName }}</span>
        <div class="user-meta">
          <span class="username">{{ authStore.username }}</span>
        </div>
        <button class="logout-btn" @click="handleLogout" title="退出登录">
          <i class="fas fa-sign-out-alt"></i> 退出
        </button>
      </div>
    </header>
    
    <div class="main-body">
      <!-- 左侧边栏 -->
      <aside class="sidebar">
        <div class="menu-list">
          <div 
            v-for="item in menuItems" 
            :key="item.path"
            class="menu-item"
            :class="{ active: currentRoute.path.includes(item.path) }"
            @click="navigate(item.path)"
          >
            <div class="icon-box">
              <i :class="item.icon"></i>
            </div>
            <span class="menu-text">{{ item.title }}</span>
            
            <!-- 激活时的光晕背景 -->
            <div class="active-glow" v-if="currentRoute.path.includes(item.path)"></div>
          </div>
        </div>
      </aside>
      
      <!-- 右侧内容区 -->
      <main class="content-area">
        <div class="content-wrapper">
          <router-view v-slot="{ Component }">
            <transition name="fade-slide" mode="out-in">
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

// === 菜单列表 ===
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
/* =========================================
   1. 布局容器 (保持原尺寸和结构)
   ========================================= */
.layout-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background-color: #f8fafc; /* 更干净的云白色背景 */
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  color: #334155;
}

/* =========================================
   2. 顶部导航 (美化：玻璃拟态 + 阴影)
   ========================================= */
.top-header {
  height: 60px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px); /* 磨砂玻璃效果 */
  box-shadow: 0 4px 20px rgba(0,0,0,0.03); /* 极柔和的高级阴影 */
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px; /* 稍微增加内边距 */
  z-index: 100;
  flex-shrink: 0;
  border-bottom: 1px solid rgba(0,0,0,0.02);
}

/* Logo 区域 */
.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-box {
  width: 32px; height: 32px;
  background: linear-gradient(135deg, #4f46e5, #818cf8); /* 品牌渐变色 */
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 16px;
  box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3); /* 发光投影 */
}

.logo-text {
  font-size: 20px; font-weight: 800; color: #1e293b; letter-spacing: -0.5px;
}
.highlight { color: #4f46e5; }

/* 用户区域 */
.user-area { display: flex; align-items: center; gap: 16px; }

.role-tag {
  padding: 4px 10px; border-radius: 6px; 
  font-size: 11px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;
}
.role-tag.resident { background: #eff6ff; color: #3b82f6; }
.role-tag.reception { background: #ecfdf5; color: #10b981; }
.role-tag.admin { background: #fef2f2; color: #ef4444; }

.username { font-weight: 600; font-size: 14px; color: #334155; }

.logout-btn {
  border: 1px solid #e2e8f0;
  background: white;
  padding: 6px 14px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px; font-weight: 500; color: #64748b;
  display: flex; align-items: center; gap: 6px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.logout-btn:hover {
  background: #fff1f2; color: #e11d48; border-color: #fecdd3;
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(225, 29, 72, 0.1);
}

/* =========================================
   3. 主体区域 (保持结构)
   ========================================= */
.main-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* =========================================
   4. 左侧边栏 (位置大小不变，改为深色高级模式)
   ========================================= */
.sidebar {
  width: 240px;
  /* 这里的改动最大：从白色改为深蓝灰，瞬间提升专业感 */
  background: #0f172a; 
  border-right: none;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  
  /* 保持您要求的布局属性 */
  position: static !important;
  top: auto !important;
  height: auto !important;
  margin: 0 !important;
  border-radius: 0 !important;
  box-shadow: 4px 0 20px rgba(0,0,0,0.05) !important;
  padding: 20px 12px 0 12px !important; /* 调整padding让菜单不贴边 */
}

.menu-list {
  display: flex; flex-direction: column; gap: 4px;
}

.menu-item {
  position: relative;
  padding: 14px 16px;
  display: flex; align-items: center; gap: 14px;
  color: #94a3b8; /* 未选中文字颜色：柔和灰 */
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 10px; /* 圆角菜单 */
  border-left: none; /* 去掉旧的边框 */
  overflow: hidden;
  font-size: 14px; font-weight: 500;
}

.icon-box {
  width: 24px; text-align: center; font-size: 18px;
  transition: transform 0.3s ease;
}

.menu-item:hover {
  background-color: rgba(255,255,255,0.08); /* 悬停微亮 */
  color: #f8fafc;
  transform: translateX(4px); /* 悬停微动效果 */
}

/* 选中状态：高级渐变高亮 */
.menu-item.active {
  color: white;
  background: transparent; /* 背景由伪元素接管 */
}

.menu-item.active .icon-box {
  color: #818cf8; /* 图标高亮 */
  transform: scale(1.1); /* 图标微放大 */
}

/* 激活背景光晕 (绝对定位背景，不影响布局) */
.active-glow {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(90deg, rgba(79, 70, 229, 0.2), rgba(79, 70, 229, 0.05));
  border-left: 3px solid #6366f1; /* 左侧亮条 */
  z-index: -1;
  border-radius: 8px;
}

/* =========================================
   5. 右侧内容区 (位置大小不变)
   ========================================= */
.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
  background-color: #f8fafc;
  position: relative;
}

/* 内容容器宽度限制 */
.content-wrapper {
  width: 100%;
  max-width: 1200px;
  min-width: 800px;
  margin: 0 auto;
}

/* 页面切换动画：平滑上浮 + 淡入 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(15px); /* 从下方15px处浮现 */
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-15px);
}
</style>