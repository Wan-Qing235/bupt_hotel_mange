<template>
  <div>
    <h2 class="section-title"><i class="fas fa-chart-line"></i> 系统监控仪表盘</h2>
    
    <div class="stats-row">
      <div class="stat-box">
        <div class="title">总收入 (含当前)</div>
        <div class="number">¥{{ totalRealtimeIncome }}</div>
        <div class="sub">累计结账: ¥{{ hotelStore.stats.total_income.toFixed(2) }}</div>
      </div>
      <div class="stat-box">
        <div class="title">当前运行空调</div>
        <div class="number">{{ runningCount }} <span class="unit">台</span></div>
        <div class="sub">等待队列: {{ waitingCount }}</div>
      </div>
      <div class="stat-box">
        <div class="title">总能耗 (kWh)</div>
        <div class="number">{{ hotelStore.stats.total_energy.toFixed(1) }}</div>
      </div>
      <div class="stat-box">
        <div class="title">平均室温</div>
        <div class="number">{{ avgTemp }}℃</div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card" style="flex: 2">
        <h3><i class="fas fa-server"></i> 调度队列状态</h3>
        
        <div class="queue-list" v-if="activeRooms.length > 0">
          <div class="list-header">
            <span>房间</span>
            <span>当前状态</span>
            <span>风速</span>
            <span>优先级</span>
          </div>
          <div v-for="room in activeRooms" :key="room.id" class="list-item">
            <span style="font-weight:bold">{{ room.id }}</span>
            
            <span>
              <span v-if="room.isRunning" class="tag run">服务中</span>
              <span v-else class="tag wait">等待中</span>
            </span>
            
            <span>{{ getSpeedLabel(room.speed) }}</span>
            <span>{{ getPriority(room.speed) }}</span>
          </div>
        </div>
        <div v-else style="text-align:center; padding: 50px; color:#999;">
          当前没有开启空调的房间
        </div>
      </div>
      
      <div class="chart-card">
        <h3><i class="fas fa-info-circle"></i> 当前参数</h3>
        <div class="param-list">
          <div class="p-row"><span>模式:</span> <strong>{{ hotelStore.config.mode === 'cool' ? '制冷' : '制热' }}</strong></div>
          <div class="p-row"><span>最大服务:</span> <strong>{{ hotelStore.config.maxServices }}</strong></div>
          <div class="p-row"><span>费率:</span> <strong>{{ hotelStore.config.baseRate }}x</strong></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useHotelStore } from '@/store/modules/hotel'

const hotelStore = useHotelStore()

// 1. 实时总收入 = 已结账存入国库的钱 + 房间里正在跑还没结的钱 + 房费
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
  return { low: '低风', medium: '中风', high: '高风' }[speed]
}
function getPriority(speed) {
  return { low: '低', medium: '中', high: '高' }[speed]
}
</script>

<style scoped>
/* 复用之前的样式，略微调整 */
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px; }
.stat-box { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.stat-box .title { font-size: 13px; color: #888; margin-bottom: 5px; }
.stat-box .number { font-size: 28px; font-weight: bold; color: #2a5298; }
.stat-box .unit { font-size: 14px; font-weight: normal; color: #666; }
.sub { font-size: 12px; color: #e67e22; margin-top: 5px; }

.charts-row { display: flex; gap: 20px; }
.chart-card { background: white; padding: 20px; border-radius: 10px; flex: 1; min-height: 300px; }
.chart-card h3 { font-size: 16px; margin-bottom: 20px; color: #444; }

.queue-list { border: 1px solid #eee; border-radius: 8px; }
.list-header { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; padding: 10px; background: #f8f9fa; font-weight: bold; color: #666; font-size: 14px; }
.list-item { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; padding: 12px 10px; border-top: 1px solid #eee; align-items: center; font-size: 14px; }

.tag { font-size: 12px; padding: 2px 8px; border-radius: 10px; }
.tag.run { background: #e8f5e9; color: #2ecc71; }
.tag.wait { background: #fff3cd; color: #f1c40f; }

.param-list .p-row { display: flex; justify-content: space-between; padding: 15px 0; border-bottom: 1px solid #eee; }
</style>