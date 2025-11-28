import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth'

// 懒加载函数：自动去 src/views 下找对应的文件
const lazyLoad = (view) => () => import(`@/views/${view}.vue`)

const routes = [
  // 1. 根路径
  {
    path: '/',
    redirect: '/login'
  },
  
  // 2. 登录页
  {
    path: '/login',
    name: 'Login',
    component: lazyLoad('Login'),
    meta: { title: '登录', requiresAuth: false, guestOnly: true }
  },
  
  // ============================
  // 3. 住户端路由 (Resident)
  // ============================
  {
    path: '/resident',
    component: lazyLoad('Layout/MainLayout'), // 使用带侧边栏的布局
    redirect: '/resident/dashboard',
    meta: { requiresAuth: true, role: 'resident' },
    children: [
      {
        path: 'dashboard',
        name: 'ResidentDashboard',
        component: lazyLoad('Resident/Dashboard'),
        meta: { title: '空调控制面板' }
      },
      // 这里的 CheckoutRequest 如果你还没建文件，记得新建一个空的，否则取消注释会报错
      {
        path: 'checkout-request',
        name: 'CheckoutRequest',
        // 暂时指向 Dashboard 或者你新建的 CheckoutRequest.vue
        component: lazyLoad('Resident/CheckoutRequest'), 
        meta: { title: '结账请求' }
      },
      {
        path: 'usage-details',
        name: 'UsageDetails',
        // 暂时指向 Dashboard 或者你新建的 UsageDetails.vue
        component: lazyLoad('Resident/UsageDetails'),
        meta: { title: '使用详单' }
      }
    ]
  },

  // ============================
  // 4. 前台端路由 (Reception)
  // ============================
  {
    path: '/reception',
    component: lazyLoad('Layout/MainLayout'),
    redirect: '/reception/dashboard',
    meta: { requiresAuth: true, role: 'reception' },
    children: [
      {
        path: 'dashboard',
        name: 'ReceptionDashboard',
        component: lazyLoad('Reception/Dashboard'),
        meta: { title: '前台工作台' }
      },
      {
        path: 'checkin',
        name: 'CheckIn',
        component: lazyLoad('Reception/CheckIn'), // 对应我们刚写的 CheckIn.vue
        meta: { title: '办理入住' }
      },
      {
        path: 'checkout',
        name: 'CheckOut',
        component: lazyLoad('Reception/CheckOut'), // 对应我们刚写的 CheckOut.vue
        meta: { title: '办理结账' }
      },
      {
        path: 'room-status',
        name: 'ReceptionRoomStatus',
        // 这里复用管理员的房间监控页面，或者你可以单独建一个 Reception/RoomStatus.vue
        component: lazyLoad('Admin/RoomManage'), 
        meta: { title: '房间状态' }
      }
    ]
  },

  // ============================
  // 5. 管理员路由 (Admin)
  // ============================
  {
    path: '/admin',
    component: lazyLoad('Layout/MainLayout'),
    redirect: '/admin/dashboard',
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: lazyLoad('Admin/Dashboard'),
        meta: { title: '管理员仪表盘' }
      },
      {
        path: 'room-manage',
        name: 'RoomManage',
        component: lazyLoad('Admin/RoomManage'), // 对应我们刚写的 RoomManage.vue
        meta: { title: '房间管理' }
      },
      {
        path: 'sys-manage',
        name: 'SysManage',
        component: lazyLoad('Admin/SysManage'), // 对应我们刚写的 SysManage.vue
        meta: { title: '系统设置' }
      }
    ]
  },

  // 6. 404 处理
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// === 路由守卫 ===
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 1. 设置网页标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 波普特酒店`
  }

  // 2. 登录页跳转逻辑（已登录则踢回首页）
  if (to.path === '/login') {
    if (authStore.isAuthenticated) {
      const role = authStore.userRole
      if (role === 'resident') return next('/resident/dashboard')
      if (role === 'reception') return next('/reception/dashboard')
      if (role === 'admin') return next('/admin/dashboard')
    }
    return next()
  }

  // 3. 权限拦截
  if (to.meta.requiresAuth) {
    // 未登录 -> 去登录
    if (!authStore.isAuthenticated) {
      return next({ path: '/login', query: { redirect: to.fullPath } })
    }
    
    // 角色权限检查 (简单版：管理员拥有所有权限，其他角色必须严格匹配)
    if (to.meta.role && authStore.userRole !== to.meta.role && authStore.userRole !== 'admin') {
      alert('无权访问该页面')
      // 如果权限不足，尝试跳转回自己的主页，防止死循环
      const role = authStore.userRole
      if (role === 'resident') return next('/resident/dashboard')
      if (role === 'reception') return next('/reception/dashboard')
      return next('/login')
    }
  }

  next()
})

export default router