<template>
  <div class="monitor-page">
    <div class="page-container">
      
      <div class="header-section">
        <div class="header-title">
          <h1><i class="ph-duotone ph-buildings"></i> 全局房间监控</h1>
          <p class="subtitle">实时环境与能耗监测系统</p>
        </div>
        <div class="header-actions">
          <button class="refresh-btn">
            <i class="ph-bold ph-arrows-clockwise"></i> 数据同步中
          </button>
        </div>
      </div>

      <div class="hud-grid">
        <div class="hud-card">
          <div class="hud-icon blue"><i class="ph-fill ph-door-open"></i></div>
          <div class="hud-info">
            <div class="label">管理房间</div>
            <div class="value">{{ hotelStore.rooms.length }}<span class="unit">间</span></div>
          </div>
        </div>
        <div class="hud-card">
          <div class="hud-icon green"><i class="ph-fill ph-fan"></i></div>
          <div class="hud-info">
            <div class="label">运行中空调</div>
            <div class="value">{{ runningCount }}<span class="unit">台</span></div>
          </div>
        </div>
        <div class="hud-card">
          <div class="hud-icon orange"><i class="ph-fill ph-lightning"></i></div>
          <div class="hud-info">
            <div class="label">累计总能耗</div>
            <div class="value">{{ (hotelStore.stats?.total_energy || 0).toFixed(1) }}<span class="unit">kWh</span></div>
          </div>
        </div>
        <div class="hud-card">
          <div class="hud-icon purple"><i class="ph-fill ph-currency-yen"></i></div>
          <div class="hud-info">
            <div class="label">实时总费用</div>
            <div class="value">{{ totalCost.toFixed(2) }}<span class="unit">元</span></div>
          </div>
        </div>
      </div>

      <div class="toolbar">
        <div class="filter-group">
          <button 
            v-for="filter in filters" 
            :key="filter.key"
            class="filter-btn" 
            :class="{ active: currentFilter === filter.key }"
            @click="currentFilter = filter.key"
          >
            {{ filter.label }}
          </button>
        </div>
        <div class="legend-group">
          <span class="legend-item"><span class="dot run"></span>运行</span>
          <span class="legend-item"><span class="dot free"></span>空闲</span>
          <span class="legend-item"><span class="dot off"></span>关机</span>
        </div>
      </div>

      <transition-group name="list" tag="div" class="room-grid">
        <div 
          v-for="room in filteredRooms" 
          :key="room.id" 
          class="room-card" 
          :class="getCardClass(room)"
        >
          <div class="status-bar"></div>

          <div class="card-header">
            <div class="room-id">{{ room.id }}</div>
            <div class="room-badge">
              <span class="status-dot"></span>
              {{ getStatusText(room) }}
            </div>
          </div>

          <div class="card-body">
            <div class="data-row main-data">
              <div class="temp-box">
                <span class="label"><i class="ph-fill ph-thermometer-simple"></i> 室温</span>
                <span class="val-temp">{{ room.temp.toFixed(1) }}°</span>
              </div>
              <div class="target-box" v-if="room.isOn">
                <span class="label">目标</span>
                <span class="val-target">{{ room.target }}°</span>
              </div>
              <div class="target-box" v-else>
                <span class="label">状态</span>
                <span class="val-target" style="color:#94A3B8">OFF</span>
              </div>
            </div>

            <div class="widgets-row">
              <div class="widget" :class="{'active': room.isOn}">
                <i class="ph-bold ph-wind"></i>
                <span>{{ room.isOn ? getSpeedLabel(room.speed) : '--' }}</span>
              </div>
              <div class="widget" :class="{'active': room.isOn}">
                <i class="ph-bold ph-snowflake"></i>
                <span>{{ room.isOn ? '制冷' : '--' }}</span>
              </div>
            </div>

            <div class="divider"></div>

            <div class="data-row footer-data">
              <div class="guest-info">
                <i class="ph-fill ph-user"></i>
                <span>{{ room.guest ? room.guest.name : '空置' }}</span>
              </div>
              <div class="cost-info">
                <span class="cost-val">¥ {{ room.currentCost.toFixed(2) }}</span>
              </div>
            </div>
          </div>
          
          </div>
      </transition-group>

      <div v-if="filteredRooms.length === 0" class="empty-state">
        <i class="ph-duotone ph-magnifying-glass"></i>
        <p>没有符合该筛选条件的房间</p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useHotelStore } from '@/store/modules/hotel'

const hotelStore = useHotelStore()

// 1. 统计数据计算
const runningCount = computed(() => hotelStore.rooms.filter(r => r.isOn).length)
const totalCost = computed(() => hotelStore.rooms.reduce((sum, r) => sum + r.currentCost, 0))

// 2. 筛选逻辑
const currentFilter = ref('all')
const filters = [
  { key: 'all', label: '全部房间' },
  { key: 'running', label: '运行中' },
  { key: 'free', label: '空闲' },
  { key: 'off', label: '已关机' }
]

const filteredRooms = computed(() => {
  if (currentFilter.value === 'all') return hotelStore.rooms
  if (currentFilter.value === 'running') return hotelStore.rooms.filter(r => r.isOn)
  if (currentFilter.value === 'free') return hotelStore.rooms.filter(r => r.status === 'free')
  if (currentFilter.value === 'off') return hotelStore.rooms.filter(r => !r.isOn)
  return hotelStore.rooms
})

// 3. 辅助函数
const getCardClass = (room) => {
  if (room.isOn) return 'card-running'
  if (room.status === 'free') return 'card-free'
  return 'card-off'
}

const getStatusText = (room) => {
  if (room.isOn) return '运行中'
  if (room.status === 'free') return '空闲'
  return '待机'
}

const getSpeedLabel = (speed) => {
  const map = { low: '低风', medium: '中风', high: '高风' }
  return map[speed] || speed
}
</script>

<style scoped>
/* ========================
   全局容器
   ======================== */
.monitor-page {
  background-color: #F8FAFC; 
  min-height: 100%;
  padding: 40px;
  font-family: 'Inter', -apple-system, sans-serif;
  color: #1E293B;
}

.page-container {
  max-width: 1400px;
  margin: 0 auto;
  animation: fadeIn 0.5s ease-out;
}

/* ========================
   1. Header & HUD
   ======================== */
.header-section {
  display: flex; justify-content: space-between; align-items: flex-end;
  margin-bottom: 30px;
}
.header-title h1 {
  font-size: 28px; font-weight: 800; color: #1E293B;
  display: flex; align-items: center; gap: 12px; margin: 0;
}
.subtitle { color: #64748B; margin-top: 4px; font-size: 14px; }

.refresh-btn {
  background: white; border: 1px solid #E2E8F0; color: #64748B;
  padding: 10px 16px; border-radius: 10px; font-weight: 600; cursor: default;
  display: flex; align-items: center; gap: 6px; 
}

/* HUD Grid */
.hud-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px;
}
.hud-card {
  background: white; border-radius: 16px; padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); border: 1px solid #F1F5F9;
  display: flex; align-items: center; gap: 16px;
}
.hud-icon {
  width: 50px; height: 50px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; font-size: 24px;
}
.blue { background: #EFF6FF; color: #3B82F6; }
.green { background: #ECFDF5; color: #10B981; }
.orange { background: #FFF7ED; color: #F97316; }
.purple { background: #F5F3FF; color: #8B5CF6; }

.hud-info .label { font-size: 12px; color: #64748B; margin-bottom: 2px; font-weight: 600; }
.hud-info .value { font-size: 24px; font-weight: 800; color: #1E293B; }
.hud-info .unit { font-size: 12px; font-weight: 500; color: #94A3B8; margin-left: 2px; }

/* ========================
   2. 工具栏 (Toolbar)
   ======================== */
.toolbar {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 24px; background: white; padding: 8px 20px; border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}
.filter-group { display: flex; gap: 8px; }
.filter-btn {
  border: none; background: transparent; padding: 8px 16px; border-radius: 8px;
  color: #64748B; font-weight: 600; cursor: pointer; transition: 0.2s;
}
.filter-btn:hover { background: #F1F5F9; }
.filter-btn.active { background: #1E293B; color: white; }

.legend-group { display: flex; gap: 16px; font-size: 13px; color: #64748B; }
.legend-item { display: flex; align-items: center; gap: 6px; }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot.run { background: #3B82F6; }
.dot.free { background: #10B981; }
.dot.off { background: #CBD5E1; }

/* ========================
   3. 房间卡片网格
   ======================== */
.room-grid {
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); 
  gap: 24px;
}

.room-card {
  background: white; border-radius: 20px; 
  border: 1px solid #E2E8F0;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
  overflow: hidden; position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex; flex-direction: column;
}
.room-card:hover { transform: translateY(-5px); box-shadow: 0 12px 24px -5px rgba(0,0,0,0.08); }

/* 状态条 */
.status-bar { height: 6px; width: 100%; position: absolute; top: 0; left: 0; }

/* 头部 */
.card-header {
  padding: 24px 24px 0 24px; display: flex; justify-content: space-between; align-items: center;
}
.room-id { font-size: 24px; font-weight: 800; color: #1E293B; letter-spacing: -0.5px; }
.room-badge {
  font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 20px;
  display: flex; align-items: center; gap: 6px;
}
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }

/* 主体内容 */
.card-body { padding: 20px 24px 24px 24px; /* 底部 padding 增加一点 */ }
.main-data { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px; }
.temp-box { display: flex; flex-direction: column; }
.target-box { display: flex; flex-direction: column; text-align: right; }
.label { font-size: 12px; color: #94A3B8; margin-bottom: 4px; display: flex; align-items: center; gap: 4px; }
.val-temp { font-size: 32px; font-weight: 800; color: #1E293B; line-height: 1; }
.val-target { font-size: 16px; font-weight: 600; color: #64748B; }

.widgets-row { display: flex; gap: 10px; margin-bottom: 20px; }
.widget {
  flex: 1; background: #F8FAFC; padding: 8px; border-radius: 10px;
  font-size: 12px; color: #94A3B8; font-weight: 600;
  display: flex; align-items: center; justify-content: center; gap: 6px;
}
.widget.active { background: #EFF6FF; color: #3B82F6; }

.divider { height: 1px; background: #F1F5F9; margin-bottom: 16px; }

.footer-data { display: flex; justify-content: space-between; align-items: center; }
.guest-info { font-size: 13px; color: #64748B; display: flex; align-items: center; gap: 6px; font-weight: 500; }
.cost-val { font-family: 'Roboto Mono', monospace; font-weight: 700; color: #F59E0B; font-size: 16px; }

/* --- 状态配色 --- */
.card-running .status-bar { background: #3B82F6; }
.card-running .room-badge { background: #EFF6FF; color: #3B82F6; }
.card-running .status-dot { animation: pulse 1.5s infinite; }

.card-free .status-bar { background: #10B981; }
.card-free .room-badge { background: #ECFDF5; color: #10B981; }

.card-off .status-bar { background: #94A3B8; }
.card-off .room-badge { background: #F1F5F9; color: #64748B; }

/* 空状态 */
.empty-state { text-align: center; padding: 60px; color: #94A3B8; grid-column: 1 / -1; }
.empty-state i { font-size: 48px; margin-bottom: 10px; }

@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* 响应式 */
@media (max-width: 900px) {
  .hud-grid { grid-template-columns: 1fr 1fr; }
  .toolbar { flex-direction: column; align-items: flex-start; gap: 10px; }
}
</style>