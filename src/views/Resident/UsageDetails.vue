<template>
  <div>
    <h2 class="section-title"><i class="fas fa-receipt"></i> 空调使用详单 (房间: {{ myRoom?.id }})</h2>
    
    <div class="card detail-card">
      <div class="header-actions">
        <div class="info">
          <span>总费用: <strong class="highlight">¥{{ myRoom?.currentCost.toFixed(2) }}</strong></span>
        </div>
        <a :href="`http://localhost:5000/export/detail/${myRoom?.id}`" target="_blank" class="btn-export">
          <i class="fas fa-download"></i> 导出详单(CSV)
        </a>
      </div>

      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>请求时间</th>
              <th>服务开始</th>
              <th>结束时间</th>
              <th>风速</th>
              <th>时长(秒)</th>
              <th>当前费(元)</th>
              <th>累积费(元)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="myRoom?.active_log" class="active-row">
              <td>{{ myRoom.active_log.request_time_str }}</td>
              <td>{{ myRoom.active_log.start_time_str }}</td>
              <td><span class="tag-running">运行中</span></td>
              <td>{{ getSpeedLabel(myRoom.active_log.speed) }}</td>
              <td>{{ formatDuration(currentDuration) }}</td>
              <td>¥{{ myRoom.active_log.current_fee.toFixed(2) }}</td>
              <td>-</td>
            </tr>

            <tr v-for="(item, index) in myRoom?.details" :key="index">
              <td>{{ item.request_time_str }}</td>
              <td>{{ item.start_time_str }}</td>
              <td>{{ item.end_time_str }}</td>
              <td>{{ getSpeedLabel(item.speed) }}</td>
              <td>{{ item.duration }}</td>
              <td>¥{{ item.current_fee.toFixed(2) }}</td>
              <td>¥{{ item.cumulative_fee.toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useHotelStore } from '@/store/modules/hotel'

const hotelStore = useHotelStore()
const myRoom = computed(() => hotelStore.currentUserRoom)

// 本地计时器用于动态显示“运行中”的时长
const now = ref(Date.now())
let timer = null
onMounted(() => { timer = setInterval(() => { now.value = Date.now() }, 1000) })
onUnmounted(() => { if(timer) clearInterval(timer) })

const currentDuration = computed(() => {
  if (!myRoom.value?.active_log) return 0
  return Math.floor((now.value / 1000) - myRoom.value.active_log.start_timestamp)
})

function getSpeedLabel(speed) { return { low: '低', medium: '中', high: '高' }[speed] || speed }
function formatDuration(s) { return s + '秒' }
</script>

<style scoped>
.header-actions { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding: 0 10px; }
.highlight { color: #e74c3c; font-size: 20px; }
.btn-export { text-decoration: none; background: #27ae60; color: white; padding: 8px 15px; border-radius: 5px; font-size: 14px; display: flex; align-items: center; gap: 5px; transition: 0.2s; }
.btn-export:hover { background: #219150; }
.table-container { border: 1px solid #eee; border-radius: 8px; overflow: hidden; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px; text-align: left; border-bottom: 1px solid #f5f5f5; font-size: 13px; }
th { background: #f8f9fa; color: #666; }
.active-row { background: #f0f9ff; color: #2a5298; font-weight: bold; }
.tag-running { color: #e74c3c; font-size: 12px; animation: pulse 1s infinite; }
@keyframes pulse { 50% { opacity: 0.5; } }
</style>