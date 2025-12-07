<template>
  <div class="dashboard-page">
    <div class="page-container">
      
      <div class="header-section">
        <div class="header-title">
          <h1><i class="ph-duotone ph-chart-line-up"></i> 系统监控仪表盘</h1>
        </div>
        <div class="header-actions">
          <div class="live-badge">
            <div class="dot"></div> 系统运行正常
          </div>
        </div>
      </div>

      <div class="metrics-grid">
        <div class="metric-card card-income">
          <div class="metric-header">
            <span class="metric-label">总收入 (含当前)</span>
            <div class="metric-icon"><i class="ph-bold ph-currency-yen"></i></div>
          </div>
          <div>
            <div class="metric-value">¥ {{ totalRealtimeIncome }}</div>
          </div>
        </div>

        <div class="metric-card card-active">
          <div class="metric-header">
            <span class="metric-label">当前运行空调</span>
            <div class="metric-icon"><i class="ph-bold ph-fan"></i></div>
          </div>
          <div>
            <div class="metric-value">{{ runningCount }} <span class="unit">台</span></div>
          </div>
        </div>

        <div class="metric-card card-energy">
          <div class="metric-header">
            <span class="metric-label">总能耗</span>
            <div class="metric-icon"><i class="ph-bold ph-lightning"></i></div>
          </div>
          <div>
            <div class="metric-value">{{ hotelStore.stats.total_energy.toFixed(1) }} <span class="unit">kWh</span></div>
          </div>
        </div>

        <div class="metric-card card-temp">
          <div class="metric-header">
            <span class="metric-label">平均室温</span>
            <div class="metric-icon"><i class="ph-bold ph-thermometer"></i></div>
          </div>
          <div>
            <div class="metric-value">{{ avgTemp }}<span class="unit">°C</span></div>
          </div>
        </div>
      </div>

      <div class="dashboard-split">
        
        <div class="panel queue-panel">
          <div class="panel-header">
            <div class="panel-title"><i class="ph-bold ph-list-numbers"></i> 调度队列</div>
            <span class="badge-count">{{ activeRooms.length }} 任务</span>
          </div>
          
          <div class="table-wrapper">
            <table class="queue-table" v-if="activeRooms.length > 0">
              <thead>
                <tr>
                  <th>房间</th>
                  <th>状态</th>
                  <th>风速</th>
                  <th>优先级</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="room in activeRooms" :key="room.id">
                  <td class="room-id">{{ room.id }}</td>
                  <td>
                    <span v-if="room.isRunning" class="status-text serving">服务中</span>
                    <span v-else class="status-text waiting">等待中</span>
                  </td>
                  <td>{{ getSpeedLabel(room.speed) }}</td>
                  <td>{{ getPriority(room.speed) }}</td>
                </tr>
              </tbody>
            </table>
            
            <div v-else class="empty-state">
              <i class="ph-duotone ph-coffee"></i>
              <p>当前无空调运行</p>
            </div>
          </div>
        </div>

        <div class="panel param-panel">
          <div class="panel-header">
            <div class="panel-title"><i class="ph-bold ph-sliders"></i> 运行参数</div>
          </div>

          <div class="param-list">
            <div class="param-item">
              <span class="param-label">模式</span>
              <span class="param-value" :class="hotelStore.config.mode === 'cool' ? 'mode-cool' : 'mode-heat'">
                {{ hotelStore.config.mode === 'cool' ? '制冷' : '制热' }}
              </span>
            </div>
            <div class="param-item">
              <span class="param-label">最大并发</span>
              <span class="param-value">{{ hotelStore.config.maxServices }} 台</span>
            </div>
            <div class="param-item">
              <span class="param-label">费率</span>
              <span class="param-value">{{ hotelStore.config.baseRate }} x</span>
            </div>
            <div class="param-item">
              <span class="param-label">时间片</span>
              <span class="param-value">{{ hotelStore.config.timeSlice }} 秒</span>
            </div>
          </div>
        </div>

      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useHotelStore } from '@/store/modules/hotel'

const hotelStore = useHotelStore()

// 1. 实时总收入逻辑
const totalRealtimeIncome = computed(() => {
  const currentPending = hotelStore.occupiedRooms.reduce((sum, r) => sum + r.currentCost + 100, 0)
  return (hotelStore.stats.total_income + currentPending).toFixed(2)
})

// 2. 运行中与等待中数量
const activeRooms = computed(() => hotelStore.rooms.filter(r => r.isOn && r.status === 'occupied'))
const runningCount = computed(() => activeRooms.value.filter(r => r.isRunning).length)
const waitingCount = computed(() => activeRooms.value.filter(r => !r.isRunning).length)

// 3. 平均室温
const avgTemp = computed(() => {
  const occupied = hotelStore.occupiedRooms
  if (occupied.length === 0) return '-'
  const total = occupied.reduce((sum, r) => sum + r.temp, 0)
  return (total / occupied.length).toFixed(1)
})

function getSpeedLabel(speed) {
  return { low: '低', medium: '中', high: '高' }[speed]
}
function getPriority(speed) {
  return { low: '低', medium: '中', high: '高' }[speed]
}
</script>

<style scoped>
/* ========================
   全局容器
   ======================== */
.dashboard-page {
  background-color: #F8FAFC; 
  min-height: 100vh;
  padding: 30px;
  font-family: 'Inter', -apple-system, sans-serif;
  color: #1E293B;
  overflow-x: hidden;
}

.page-container {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  animation: fadeIn 0.6s ease-out;
}

/* 1. Header */
.header-section {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;
}
.header-title h1 {
  font-size: 26px; font-weight: 800; color: #1E293B; display: flex; align-items: center; gap: 10px; margin: 0;
}

.live-badge {
  background: #ECFDF5; color: #059669; padding: 6px 12px; border-radius: 20px;
  font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px; white-space: nowrap;
}
.dot { width: 8px; height: 8px; background: #10B981; border-radius: 50%; animation: pulse 2s infinite; }

/* 2. 核心指标卡片 */
.metrics-grid {
  display: grid; 
  /* 自动适应宽度，每张卡片最窄 200px */
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
  gap: 20px; 
  margin-bottom: 30px;
}

.metric-card {
  background: #FFFFFF; border-radius: 16px; padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); border: 1px solid #E2E8F0;
  display: flex; flex-direction: column; justify-content: center;
  height: 120px; position: relative; overflow: hidden; transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-4px); box-shadow: 0 10px 20px -5px rgba(0,0,0,0.05); }

.metric-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.metric-label { font-size: 13px; font-weight: 600; color: #64748B; white-space: nowrap; }
.metric-icon { font-size: 20px; padding: 8px; border-radius: 10px; display: flex; align-items: center; justify-content: center; }

.metric-value { 
  font-size: 32px; font-weight: 800; color: #1E293B; line-height: 1;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.unit { font-size: 14px; font-weight: 500; color: #94A3B8; margin-left: 4px; }

/* 卡片配色 */
.card-income .metric-icon { background: #EEF2FF; color: #6366F1; }
.card-active .metric-icon { background: #FFFBEB; color: #F59E0B; }
.card-energy .metric-icon { background: #ECFDF5; color: #10B981; }
.card-temp .metric-icon { background: #F5F3FF; color: #8B5CF6; }

/* 3. 下半部分布局 */
.dashboard-split { 
  display: flex; 
  flex-wrap: wrap; 
  gap: 24px; 
}

.panel {
  background: #FFFFFF; border-radius: 16px; padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); border: 1px solid #E2E8F0;
  display: flex; flex-direction: column;
}

/* 调整面板比例 */
.queue-panel { flex: 2; min-width: 400px; }
.param-panel { flex: 1; min-width: 250px; }

@media (max-width: 768px) {
  .queue-panel, .param-panel { min-width: 100%; flex: 100%; }
}

.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.panel-title { font-size: 16px; font-weight: 700; color: #1E293B; display: flex; align-items: center; gap: 8px; white-space: nowrap; }
.badge-count { background: #F1F5F9; color: #64748B; padding: 4px 10px; border-radius: 10px; font-size: 12px; font-weight: 600; }

/* 列表与表格 */
.table-wrapper { overflow-x: auto; }
.queue-table { width: 100%; border-collapse: collapse; min-width: 400px; }
.queue-table th { text-align: left; font-size: 12px; color: #64748B; padding: 10px 0; border-bottom: 1px solid #E2E8F0; }
.queue-table td { padding: 14px 0; font-size: 14px; color: #1E293B; border-bottom: 1px solid #F8FAFC; }
.queue-table tr:last-child td { border-bottom: none; }

.room-id { font-weight: 700; font-family: monospace; }
.status-text { font-weight: 600; font-size: 13px; }
.serving { color: #10B981; }
.waiting { color: #F59E0B; }

.empty-state { text-align: center; padding: 40px; color: #94A3B8; }
.empty-state i { font-size: 32px; margin-bottom: 8px; display: block; }

/* 参数列表 */
.param-list { display: flex; flex-direction: column; gap: 12px; }
.param-item { display: flex; justify-content: space-between; align-items: center; padding: 12px; background: #F8FAFC; border-radius: 10px; }
.param-label { font-size: 13px; color: #64748B; font-weight: 500; }
.param-value { font-size: 14px; font-weight: 700; color: #1E293B; }
.mode-cool { color: #3B82F6; }
.mode-heat { color: #F59E0B; }

@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>