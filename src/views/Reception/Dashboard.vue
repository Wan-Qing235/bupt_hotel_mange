<template>
  <div class="dashboard-container">
    
    <div class="main-area">
      <header class="header">
        <h1>
          <i class="ph-duotone ph-desktop"></i> 
          前台工作台
        </h1>
        <div class="date-badge">{{ currentDate }}</div>
      </header>

      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-content">
            <div class="label">空闲房间 (Available)</div>
            <div class="value">{{ freeCount }}</div>
            <div class="trend up">
              <i class="ph-bold ph-trend-up"></i> 房源充足
            </div>
          </div>
          <div class="icon-box bg-green">
            <i class="ph-fill ph-door-open"></i>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-content">
            <div class="label">今日入住 (Check-in)</div>
            <div class="value">{{ todayCheckInCount }}</div>
            <div class="trend">
              <i class="ph-bold ph-users"></i> 实时统计
            </div>
          </div>
          <div class="icon-box bg-blue">
            <i class="ph-fill ph-sign-in"></i>
          </div>
        </div>

        <div class="stat-card">
          <div class="stat-content">
            <div class="label">使用中 (Occupied)</div>
            <div class="value">{{ occupiedCount }}</div>
            <div class="trend down">
              <i class="ph-bold ph-warning-circle"></i> 运行中
            </div>
          </div>
          <div class="icon-box bg-orange">
            <i class="ph-fill ph-key"></i>
          </div>
        </div>
      </div>

      <div>
        <div class="section-title">
          <i class="ph-bold ph-lightning"></i> 快捷操作
        </div>
        <div class="quick-actions">
          <div class="action-card" @click="$router.push('/reception/checkin')">
            <div class="action-icon"><i class="ph-bold ph-user-plus"></i></div>
            <div>
              <div class="action-label">办理入住</div>
              <div class="action-desc">Check-in Registration</div>
            </div>
          </div>
          <div class="action-card" @click="$router.push('/reception/checkout')">
            <div class="action-icon"><i class="ph-bold ph-receipt"></i></div>
            <div>
              <div class="action-label">办理结账</div>
              <div class="action-desc">Check-out & Payment</div>
            </div>
          </div>
          <div class="action-card" @click="$router.push('/reception/room-status')">
            <div class="action-icon"><i class="ph-bold ph-squares-four"></i></div>
            <div>
              <div class="action-label">房态视图</div>
              <div class="action-desc">Full Room Matrix</div>
            </div>
          </div>
        </div>
      </div>

      <div class="room-matrix-container">
        <div class="matrix-header">
          <div class="section-title" style="margin-bottom:0;">
            <i class="ph-bold ph-grid-four"></i> 实时房态概览
          </div>
          <div class="matrix-legend">
            <div class="legend-item"><div class="dot available"></div> 空闲</div>
            <div class="legend-item"><div class="dot occupied"></div> 在住</div>
          </div>
        </div>
        
        <div class="room-grid">
          <div 
            v-for="room in allRooms" 
            :key="room.id" 
            class="room-cell"
            :class="getRoomStatusClass(room)"
          >
            <div class="room-num">{{ room.id }}</div>
            <div class="room-type">{{ room.status === 'occupied' ? '使用中' : '空闲' }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="sidebar-right">
      <div class="notification-panel">
        <div class="section-title">
          <i class="ph-bold ph-bell-ringing"></i> 实时动态
        </div>
        <div class="log-list">
          <transition-group name="list">
            <div 
              v-for="(log, index) in logs" 
              :key="index" 
              class="log-item"
              :class="log.type"
            >
              <div class="log-icon">
                <i v-if="log.type === 'checkin'" class="ph-bold ph-check"></i>
                <i v-else-if="log.type === 'checkout'" class="ph-bold ph-sign-out"></i>
                <i v-else-if="log.type === 'request'" class="ph-fill ph-hand-waving"></i>
                <i v-else class="ph-bold ph-info"></i>
              </div>
              <div class="log-content">
                <div class="log-title">{{ log.title }}</div>
                <div class="log-time">{{ log.time }} · {{ log.desc }}</div>
              </div>
            </div>
          </transition-group>
          
          <div v-if="logs.length === 0" class="empty-log">
            暂无动态数据...
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useHotelStore } from '@/store/modules/hotel'
import socket from '@/utils/socket' 

const hotelStore = useHotelStore()

// 1. 核心数据
const freeCount = computed(() => hotelStore.freeRooms.length)
const occupiedCount = computed(() => hotelStore.occupiedRooms.length)
const todayCheckInCount = computed(() => hotelStore.stats.today_checkins)
const allRooms = computed(() => hotelStore.rooms || [])

// 2. 日期显示
const currentDate = ref('')
onMounted(() => {
  const now = new Date()
  currentDate.value = now.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })
})

// ============================================
// 3. 实时日志系统 (包含历史记录回显)
// ============================================
const logs = ref([])

onMounted(() => {
  // 1. 先放入一条本地的“连接成功”提示 (显示在最前面)
  const systemMsg = { 
    type: 'system', 
    title: '系统连接成功', 
    time: new Date().toLocaleTimeString('zh-CN', {hour:'2-digit', minute:'2-digit'}), 
    desc: '服务已就绪' 
  }
  logs.value.push(systemMsg)

  // 2. 监听历史日志 (后端连接成功后发送)
  socket.on('log_history', (historyList) => {
    if (historyList && historyList.length > 0) {
      // 逻辑：将历史记录追加到当前列表后面
      // (保持 "系统连接成功" 在最上面，告诉用户那是当前时刻的分界线)
      logs.value.push(...historyList)
    }
  })

  // 3. 监听实时新日志
  socket.on('new_log', (logData) => {
    // 新日志插到最前面
    logs.value.unshift(logData)
    // 保持列表长度不超过 30 条
    if (logs.value.length > 30) logs.value.pop()
  })
})

onUnmounted(() => {
  socket.off('new_log')
  socket.off('log_history')
})

// 辅助函数：房间状态样式
const getRoomStatusClass = (room) => {
  if (room.status === 'occupied') return 'status-busy'
  return 'status-free'
}
</script>

<style scoped>
/* ========================
   全局布局
   ======================== */
.dashboard-container {
  width: 100%;
  height: 100%;
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 30px;
  padding: 10px;
  box-sizing: border-box;
  overflow: hidden;
  font-family: 'Inter', system-ui, sans-serif;
}

.main-area {
  display: flex;
  flex-direction: column;
  gap: 25px;
  overflow-y: auto;
  padding-right: 5px;
}

/* Header */
.header { display: flex; justify-content: space-between; align-items: center; }
.header h1 { font-size: 26px; font-weight: 800; color: #1E293B; display: flex; align-items: center; gap: 10px; margin: 0; }
.date-badge { font-size: 14px; font-weight: 600; color: #64748B; background: #fff; padding: 8px 16px; border-radius: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); }

/* 数据卡片 */
.stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.stat-card {
  background: #FFFFFF; padding: 24px; border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  display: flex; align-items: center; justify-content: space-between;
  border: 1px solid rgba(0,0,0,0.02); transition: transform 0.2s;
}
.stat-card:hover { transform: translateY(-3px); }
.stat-content .label { font-size: 13px; color: #64748B; margin-bottom: 6px; font-weight: 600; }
.stat-content .value { font-size: 32px; font-weight: 800; color: #1E293B; line-height: 1; }
.stat-content .trend { font-size: 12px; margin-top: 6px; font-weight: 500; display: flex; align-items: center; gap: 4px; }
.trend.up { color: #10B981; }
.trend.down { color: #F59E0B; }
.icon-box { width: 56px; height: 56px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 28px; }
.bg-blue { background: #EFF6FF; color: #3B82F6; }
.bg-green { background: #ECFDF5; color: #10B981; }
.bg-orange { background: #FFFBEB; color: #F59E0B; }

/* 快捷操作 */
.section-title { font-size: 16px; font-weight: 700; color: #1E293B; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }
.quick-actions { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.action-card {
  background: #FFFFFF; padding: 25px; border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  text-align: center; cursor: pointer; transition: all 0.2s;
  border: 1px solid transparent;
  display: flex; flex-direction: column; align-items: center; gap: 12px;
}
.action-card:hover { transform: translateY(-3px); border-color: #6366F1; box-shadow: 0 10px 30px rgba(99, 102, 241, 0.15); }
.action-icon { width: 56px; height: 56px; border-radius: 50%; background: #F8FAFC; color: #64748B; display: flex; align-items: center; justify-content: center; font-size: 24px; transition: 0.2s; }
.action-card:hover .action-icon { background: #6366F1; color: white; }
.action-label { font-size: 15px; font-weight: 700; color: #1E293B; }
.action-desc { font-size: 12px; color: #94A3B8; }

/* 房态视图 */
.room-matrix-container { background: #FFFFFF; padding: 24px; border-radius: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); flex: 1; }
.matrix-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.matrix-legend { display: flex; gap: 20px; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #64748B; font-weight: 600; }
.dot { width: 10px; height: 10px; border-radius: 50%; }
.dot.available { background: #10B981; }
.dot.occupied { background: #3B82F6; }
.room-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(90px, 1fr)); gap: 12px; }
.room-cell { background: #F8FAFC; padding: 12px; border-radius: 12px; text-align: center; cursor: pointer; transition: 0.2s; position: relative; overflow: hidden; border: 1px solid #E2E8F0; }
.room-cell:hover { transform: scale(1.05); border-color: #6366F1; }
.room-cell::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; }
.room-cell.status-free::before { background: #10B981; }
.room-cell.status-busy::before { background: #3B82F6; }
.room-num { font-size: 15px; font-weight: 800; color: #1E293B; }
.room-type { font-size: 11px; color: #94A3B8; margin-top: 2px; }

/* 右侧动态栏 */
.sidebar-right { display: flex; flex-direction: column; height: 100%; }
.notification-panel { background: #FFFFFF; border-radius: 24px; padding: 24px; height: 100%; box-shadow: 0 4px 20px rgba(0,0,0,0.03); display: flex; flex-direction: column; }
.log-list { display: flex; flex-direction: column; gap: 20px; margin-top: 10px; overflow-y: auto; padding-right: 5px; }
.log-item { display: flex; gap: 12px; align-items: flex-start; }
.log-icon { width: 36px; height: 36px; border-radius: 10px; background: #F8FAFC; color: #64748B; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
.log-content { flex: 1; }
.log-title { font-size: 13px; font-weight: 700; color: #1E293B; }
.log-time { font-size: 11px; color: #94A3B8; margin-top: 2px; }

.log-item.checkin .log-icon { background: #EFF6FF; color: #3B82F6; }
.log-item.checkout .log-icon { background: #FFFBEB; color: #F59E0B; }
.log-item.request .log-icon { background: #F5F3FF; color: #8B5CF6; }
.empty-log { text-align: center; color: #999; font-size: 13px; margin-top: 20px; }

/* 列表动画 */
.list-enter-active, .list-leave-active { transition: all 0.5s ease; }
.list-enter-from { opacity: 0; transform: translateX(20px); }
.list-leave-to { opacity: 0; transform: translateX(-20px); }

@media (max-width: 1100px) {
  .dashboard-container { grid-template-columns: 1fr; overflow-y: auto; }
  .sidebar-right { height: auto; margin-top: 30px; }
  .room-matrix-container { min-height: 200px; }
}
</style>