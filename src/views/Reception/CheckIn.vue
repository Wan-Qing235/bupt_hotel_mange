<template>
  <div class="page-container">
    
    <div class="header-section">
      <div class="header-title">
        <h1><i class="ph-duotone ph-user-plus"></i> 入住申请处理</h1>
        <p class="header-subtitle">Check-in Requests</p>
      </div>
      <div class="status-pill">
        <span class="live-dot"></span> 系统实时监控中
      </div>
    </div>

    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon icon-orange"><i class="ph-bold ph-hourglass"></i></div>
        <div class="stat-info">
          <div class="label">待处理申请</div>
          <div class="value">{{ pendingRequests.length }} <span class="unit">单</span></div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon icon-green"><i class="ph-bold ph-check-circle"></i></div>
        <div class="stat-info">
          <div class="label">今日已办理</div>
          <div class="value">{{ todayCheckIns }} <span class="unit">单</span></div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon icon-blue"><i class="ph-bold ph-bed"></i></div>
        <div class="stat-info">
          <div class="label">当前空闲房间</div>
          <div class="value">{{ freeRoomCount }} <span class="unit">间</span></div>
        </div>
      </div>
    </div>

    <div class="request-panel">
      <div class="panel-header">
        <span class="panel-title">申请列表 (Pending List)</span>
        <button class="refresh-btn" @click="refreshData">
          <i class="ph-bold ph-arrows-clockwise"></i> 刷新列表
        </button>
      </div>

      <ul class="request-list" v-if="pendingRequests.length > 0">
        <li v-for="room in pendingRequests" :key="room.id" class="request-item">
          
          <div class="room-col">
            <div class="room-badge">{{ room.id }}</div>
          </div>
          
          <div class="user-col">
            <div class="user-name">
              {{ room.request.name }} 
              <i class="ph-fill ph-check-circle verified-icon"></i>
            </div>
            <div class="user-id">ID: {{ room.request.idCard }}</div>
          </div>

          <div class="time-col">
            <i class="ph-bold ph-clock"></i> 刚刚提交
          </div>
          
          <div class="status-col">
            <span class="status-tag">
              <i class="ph-fill ph-warning-circle"></i> 待审核
            </span>
          </div>

          <div class="action-col">
            <div class="action-group">
              <button class="btn btn-reject" title="拒绝申请">
                <i class="ph-bold ph-x"></i>
              </button>
              
              <button class="btn btn-approve" @click="handleApprove(room.id)">
                <i class="ph-bold ph-check"></i>
                <span>批准入住</span>
              </button>
            </div>
          </div>
        </li>
      </ul>

      <div class="empty-state" v-else>
        <div class="empty-icon"><i class="ph-duotone ph-inbox"></i></div>
        <div class="empty-text">暂时没有新申请</div>
        <div class="empty-sub">当前所有入住请求已处理完毕，请稍后刷新或留意系统通知。</div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useHotelStore } from '@/store/modules/hotel'

const hotelStore = useHotelStore()

// 1. 列表数据：只显示有 request 且状态为 free 的房间
const pendingRequests = computed(() => {
  return hotelStore.rooms.filter(r => r.request !== null && r.status === 'free')
})

// 2. 统计数据
const freeRoomCount = computed(() => hotelStore.freeRooms.length)
const todayCheckIns = computed(() => hotelStore.stats.today_checkins || 0)

// 3. 业务逻辑
const handleApprove = (roomId) => {
  if (confirm(`确认批准房间 ${roomId} 的入住申请吗？`)) {
    hotelStore.approveCheckIn(roomId)
  }
}

const refreshData = () => {
  // 视觉反馈逻辑
  console.log('Refreshing data...')
}
</script>

<style scoped>
/* =========================
   全局容器
   ========================= */
.page-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px;
  animation: fadeIn 0.5s ease-out;
  font-family: 'Inter', -apple-system, sans-serif;
  color: #1E293B;
}

/* =========================
   1. 顶部 Header & 看板
   ========================= */
.header-section {
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.header-title h1 {
  font-size: 26px; font-weight: 800; color: #1E293B;
  display: flex; align-items: center; gap: 12px; margin: 0;
}
.header-subtitle { font-size: 14px; color: #64748B; margin-top: 6px; }

.status-pill {
  background: #EEF2FF; color: #6366F1;
  padding: 8px 16px; border-radius: 20px;
  font-size: 13px; font-weight: 600;
  display: flex; align-items: center; gap: 8px;
}
.live-dot { width: 8px; height: 8px; background: #6366F1; border-radius: 50%; animation: pulse 2s infinite; }

/* 统计卡片 */
.stats-row {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px;
}
.stat-card {
  background: #FFFFFF; padding: 24px; border-radius: 20px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
  border: 1px solid #E2E8F0;
  display: flex; align-items: center; gap: 20px; transition: transform 0.2s;
}
.stat-card:hover { transform: translateY(-3px); }

.stat-icon {
  width: 52px; height: 52px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center; font-size: 26px;
}
.icon-blue { background: #EFF6FF; color: #3B82F6; }
.icon-orange { background: #FFFBEB; color: #F59E0B; }
.icon-green { background: #ECFDF5; color: #10B981; }

.stat-info .label { font-size: 13px; color: #64748B; margin-bottom: 4px; font-weight: 600; }
.stat-info .value { font-size: 28px; font-weight: 700; color: #1E293B; }
.stat-info .unit { font-size: 14px; color: #94A3B8; font-weight: 400; margin-left: 4px; }

/* =========================
   2. 申请列表面板
   ========================= */
.request-panel {
  background: #FFFFFF; border-radius: 24px;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.03);
  overflow: hidden; border: 1px solid #E2E8F0;
}

.panel-header {
  padding: 20px 30px; border-bottom: 1px solid #F1F5F9;
  display: flex; justify-content: space-between; align-items: center;
  background: #FCFCFD;
}
.panel-title { font-size: 16px; font-weight: 700; color: #1E293B; }
.refresh-btn {
  border: 1px solid #E2E8F0; background: white; padding: 8px 14px;
  border-radius: 8px; cursor: pointer; font-size: 13px; color: #64748B;
  display: flex; align-items: center; gap: 6px; transition: 0.2s;
}
.refresh-btn:hover { background: #F8FAFC; color: #1E293B; border-color: #CBD5E1; }

/* 列表项布局 Grid */
.request-list { padding: 0; margin: 0; list-style: none; }

.request-item {
  display: grid;
  /* 定义列宽：徽章 | 姓名ID | 时间 | 状态 | 操作区 */
  grid-template-columns: 80px 2fr 1.5fr 1.5fr auto; 
  align-items: center; 
  padding: 24px 30px;
  border-bottom: 1px solid #F1F5F9; 
  transition: background 0.2s;
}
.request-item:last-child { border-bottom: none; }
.request-item:hover { background: #F8FAFC; }

/* 列表内容样式 */
.room-badge {
  background: #F1F5F9; color: #1E293B; font-weight: 800;
  padding: 8px 12px; border-radius: 8px; text-align: center; font-size: 16px; width: fit-content;
  font-family: 'Roboto Mono', monospace;
}

.user-name { font-size: 16px; font-weight: 700; color: #1E293B; display: flex; align-items: center; gap: 8px; }
.verified-icon { color: #10B981; font-size: 14px; }
.user-id { font-size: 13px; color: #94A3B8; margin-top: 4px; font-family: 'Roboto Mono', monospace; }

.time-col { color: #64748B; font-size: 14px; display: flex; align-items: center; gap: 6px; }

.status-tag {
  background: #FEF3C7; color: #D97706; padding: 6px 12px; border-radius: 20px;
  font-size: 12px; font-weight: 700; display: inline-flex; align-items: center; gap: 6px;
}

/* =========================
   3. 核心修复：操作按钮组
   ========================= */
.action-group {
  display: flex; align-items: center; gap: 12px; justify-content: flex-end;
}

.btn {
  border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  font-family: 'Inter', sans-serif;
}

/* 批准按钮 - 渐变风格 */
.btn-approve {
  background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
  color: white;
  padding: 10px 20px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  gap: 8px;
}
.btn-approve:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4); }
.btn-approve:active { transform: scale(0.98); }

/* 拒绝按钮 - 极简图标风格 */
.btn-reject {
  width: 40px; height: 40px;
  border-radius: 12px;
  background: #fff;
  border: 1px solid #E2E8F0;
  color: #94A3B8;
  font-size: 18px;
}
.btn-reject:hover { background: #FEF2F2; border-color: #FECACA; color: #EF4444; }

/* 4. 空状态 */
.empty-state {
  padding: 80px 20px; text-align: center;
  display: flex; flex-direction: column; align-items: center;
}
.empty-icon {
  font-size: 64px; color: #CBD5E1; margin-bottom: 20px;
  background: #F8FAFC; width: 120px; height: 120px;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
}
.empty-text { font-size: 18px; font-weight: 700; color: #1E293B; margin-bottom: 8px; }
.empty-sub { font-size: 14px; color: #64748B; max-width: 350px; line-height: 1.6; }

@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* 响应式适配 */
@media (max-width: 900px) {
  .stats-row { grid-template-columns: 1fr; }
  .request-item { grid-template-columns: 1fr; gap: 15px; text-align: left; }
  .action-group { justify-content: flex-start; margin-top: 10px; }
  .btn-approve { width: 100%; justify-content: center; }
}
</style>