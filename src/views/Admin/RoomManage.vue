<template>
  <div>
    <h2 class="section-title"><i class="fas fa-door-open"></i> 全局房间监控</h2>
    
    <div class="monitor-grid">
      <div 
        v-for="room in hotelStore.rooms" 
        :key="room.id" 
        class="room-card"
        :class="getCardClass(room)"
      >
        <div class="room-header">
          <span class="room-id">{{ room.id }}</span>
          <span class="room-status">{{ getStatusText(room) }}</span>
        </div>
        
        <div class="room-body">
          <div class="metric-row">
            <span><i class="fas fa-thermometer-half"></i> 室温</span>
            <strong>{{ room.temp }}℃</strong>
          </div>
          <div class="metric-row">
            <span><i class="fas fa-bullseye"></i> 目标</span>
            <strong>{{ room.target }}℃</strong>
          </div>
          <div class="metric-row">
            <span><i class="fas fa-wind"></i> 风速</span>
            <strong>{{ getSpeedLabel(room.speed) }}</strong>
          </div>
          <div class="metric-row cost">
            <span><i class="fas fa-yen-sign"></i> 费用</span>
            <strong>{{ room.currentCost.toFixed(2) }}</strong>
          </div>
        </div>

        <div class="room-footer">
          <span v-if="room.isOn && room.isRunning" class="badge running">
            <i class="fas fa-fan fa-spin"></i> 送风中
          </span>
          <span v-else-if="room.isOn && !room.isRunning" class="badge waiting">
            <i class="fas fa-clock"></i> 调度排队
          </span>
          <span v-else class="badge off">已关机</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useHotelStore } from '@/store/modules/hotel'
const hotelStore = useHotelStore()

const getSpeedLabel = (speed) => {
  const map = { low: '低', medium: '中', high: '高' }
  return map[speed] || '-'
}

const getStatusText = (room) => {
  if (room.request) return '申请中'
  if (room.checkout_pending) return '待结账'
  if (room.status === 'free') return '空闲'
  return room.guest ? room.guest.name : '入住中'
}

const getCardClass = (room) => {
  if (room.status === 'free' && !room.request) return 'is-free'
  if (room.checkout_pending) return 'is-checkout'
  if (room.request) return 'is-request'
  return 'is-occupied'
}
</script>

<style scoped>
.monitor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.room-card {
  background: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid #eee;
  transition: all 0.3s;
}

.room-header {
  padding: 12px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
}
.room-id { font-weight: bold; font-size: 18px; color: #333; }
.room-status { font-size: 12px; padding: 2px 8px; border-radius: 4px; background: #eee; }

.room-body { padding: 15px; }
.metric-row { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px; color: #666; }
.metric-row.cost { margin-top: 10px; padding-top: 10px; border-top: 1px dashed #eee; color: #333; }
.metric-row.cost strong { color: #e74c3c; font-size: 16px; }

.room-footer { padding: 10px 15px; background: #f9f9f9; text-align: center; font-size: 12px; }
.badge { display: inline-flex; align-items: center; gap: 5px; font-weight: 600; }
.badge.running { color: #2ecc71; }
.badge.waiting { color: #f39c12; }
.badge.off { color: #ccc; }

/* 状态颜色 */
.is-free .room-header { background: #e8f5e9; }
.is-free .room-status { background: #c8e6c9; color: #2e7d32; }

.is-occupied .room-header { background: #e3f2fd; }
.is-occupied .room-status { background: #bbdefb; color: #1565c0; }

.is-request .room-header { background: #fff3e0; }
.is-request .room-status { background: #ffe0b2; color: #ef6c00; }

.is-checkout .room-header { background: #ffebee; }
.is-checkout .room-status { background: #ffcdd2; color: #c62828; }
</style>