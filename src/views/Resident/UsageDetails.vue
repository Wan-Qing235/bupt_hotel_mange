<template>
  <div class="usage-page">
    <div class="page-container">
      
      <header class="page-header">
        <div class="header-title">
          <h1>
            <i class="ph-duotone ph-list-dashes icon-main"></i>
            空调使用详单
            <span class="tag">房间 {{ myRoom?.id }}</span>
          </h1>
        </div>
        
        <button 
          class="print-req-btn" 
          :class="{ 'sent': isSent }"
          @click="handlePrintRequest"
          :disabled="isSent"
        >
          <i class="ph-bold" :class="isSent ? 'ph-check' : 'ph-printer'"></i>
          {{ isSent ? '请求已发送' : '申请打印报表' }}
        </button>
      </header>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="icon-circle bg-purple"><i class="ph-fill ph-coins"></i></div>
          <div class="stat-info">
            <div class="label">累计总费用</div>
            <div class="value"><span class="unit-prefix">¥</span>{{ myRoom?.currentCost.toFixed(2) }}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="icon-circle bg-blue"><i class="ph-fill ph-clock"></i></div>
          <div class="stat-info">
            <div class="label">累计运行时长</div>
            <div class="value">{{ totalRuntimeFormatted }}<span class="unit">分钟</span></div>
          </div>
        </div>
        <div class="stat-card">
          <div class="icon-circle bg-green"><i class="ph-fill ph-calendar-check"></i></div>
          <div class="stat-info">
            <div class="label">住宿天数</div>
            <div class="value">{{ stayDays }}<span class="unit">天</span></div>
          </div>
        </div>
      </div>

      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th><i class="ph-bold ph-calendar-blank"></i> 请求时间</th>
              <th>服务开始</th>
              <th>结束时间</th>
              <th>风速模式</th>
              <th>时长 (秒)</th>
              <th>当前费 (元)</th>
              <th>累计费 (元)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="myRoom?.active_log" class="active-row">
              <td class="time-cell">{{ myRoom.active_log.request_time_str }}</td>
              <td class="time-cell">{{ myRoom.active_log.start_time_str }}</td>
              <td><span class="status-running"><span class="dot"></span> 运行中</span></td>
              <td><span class="badge" :class="getSpeedClass(myRoom.active_log.speed)">{{ getSpeedLabel(myRoom.active_log.speed) }}</span></td>
              <td class="mono-font highlight">{{ Math.floor(currentDuration) }}</td>
              <td class="mono-font money">¥ {{ myRoom.active_log.current_fee.toFixed(2) }}</td>
              <td class="mono-font">-</td>
            </tr>
            <tr v-for="(item, index) in myRoom?.details" :key="index">
              <td class="time-cell">{{ item.request_time_str }}</td>
              <td class="time-cell">{{ item.start_time_str }}</td>
              <td class="time-cell">{{ item.end_time_str }}</td>
              <td><span class="badge" :class="getSpeedClass(item.speed)">{{ getSpeedLabel(item.speed) }}</span></td>
              <td class="mono-font">{{ item.duration }}</td>
              <td class="mono-font money">¥ {{ item.current_fee.toFixed(2) }}</td>
              <td class="mono-font total-money">¥ {{ item.cumulative_fee.toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="!myRoom?.active_log && (!myRoom?.details || myRoom.details.length === 0)" class="empty-state">
          暂无使用记录
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useHotelStore } from '@/store/modules/hotel'
import socket from '@/utils/socket' // 引入 socket 用于发送请求

const hotelStore = useHotelStore()
const myRoom = computed(() => hotelStore.currentUserRoom)

const now = ref(Date.now())
const isSent = ref(false) // 控制按钮状态
let timer = null

onMounted(() => { 
  timer = setInterval(() => { now.value = Date.now() }, 1000) 
})
onUnmounted(() => { if(timer) clearInterval(timer) })

const currentDuration = computed(() => {
  if (!myRoom.value?.active_log) return 0
  return (now.value / 1000) - myRoom.value.active_log.start_timestamp
})

const totalRuntimeFormatted = computed(() => {
  if (!myRoom.value) return 0
  let totalSeconds = myRoom.value.details?.reduce((sum, item) => sum + (item.duration || 0), 0) || 0
  if (myRoom.value.active_log) totalSeconds += currentDuration.value
  return (totalSeconds / 60).toFixed(0)
})

const stayDays = computed(() => (myRoom.value?.ac_cycles > 0) ? myRoom.value.ac_cycles : 1)

// [新增] 处理打印请求
const handlePrintRequest = () => {
  if (!myRoom.value) return
  if (confirm('确认通知前台为您打印详细报表吗？')) {
    // 发送指令给后端
    socket.emit('client_action', {
      roomId: myRoom.value.id,
      action: 'request_print_detail', // 新的 action 类型
      value: null
    })
    
    // 按钮反馈动画
    isSent.value = true
    setTimeout(() => { isSent.value = false }, 5000) // 5秒后恢复
  }
}

function getSpeedLabel(speed) { return { low: '低风', medium: '中风', high: '高风' }[speed] || speed }
function getSpeedClass(speed) { return { low: 'badge-low', medium: 'badge-mid', high: 'badge-high' }[speed] || 'badge-mid' }
</script>

<style scoped>
/* 保持原有布局样式 */
.usage-page { background-color: #F8FAFC; min-height: 100%; padding: 40px; font-family: 'Inter', system-ui, sans-serif; color: #1E293B; }
.page-container { max-width: 1200px; margin: 0 auto; animation: fadeIn 0.6s ease-out; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
.header-title h1 { font-size: 24px; font-weight: 800; color: #1E293B; display: flex; align-items: center; gap: 12px; margin: 0; }
.icon-main { color: #6366F1; font-size: 28px; }
.header-title .tag { font-size: 13px; background: #E0E7FF; color: #4F46E5; padding: 4px 12px; border-radius: 8px; font-weight: 600; letter-spacing: 0.5px; }

/* [修改] 打印请求按钮样式 */
.print-req-btn {
  background: white; color: #6366F1; border: 1px solid #6366F1;
  padding: 10px 20px; border-radius: 12px; font-size: 14px; font-weight: 600;
  cursor: pointer; display: flex; align-items: center; gap: 8px;
  transition: all 0.2s; box-shadow: 0 2px 5px rgba(99, 102, 241, 0.1);
}
.print-req-btn:hover { background: #EEF2FF; transform: translateY(-1px); }
.print-req-btn:active { transform: scale(0.98); }

/* 发送成功后的状态 */
.print-req-btn.sent {
  background: #10B981; color: white; border-color: #10B981; cursor: default;
}

/* 概览卡片 */
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
.stat-card { background: #fff; padding: 24px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.5); box-shadow: 0 4px 20px rgba(0,0,0,0.03); display: flex; align-items: center; gap: 20px; transition: transform 0.2s; }
.stat-card:hover { transform: translateY(-3px); }
.icon-circle { width: 56px; height: 56px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 28px; flex-shrink: 0; }
.bg-purple { background: #EEF2FF; color: #6366F1; }
.bg-green { background: #ECFDF5; color: #10B981; }
.bg-blue { background: #EFF6FF; color: #3B82F6; }
.stat-info .label { color: #64748B; font-size: 13px; font-weight: 600; margin-bottom: 4px; }
.stat-info .value { font-size: 28px; font-weight: 800; color: #1E293B; letter-spacing: -0.5px; }
.stat-info .unit { font-size: 14px; font-weight: 500; color: #64748B; margin-left: 4px; }
.unit-prefix { font-size: 18px; font-weight: 600; color: #64748B; margin-right: 4px; vertical-align: middle; }

/* 表格 */
.table-container { background: #fff; border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.04); padding: 0; overflow: hidden; border: 1px solid #F1F5F9; }
table { width: 100%; border-collapse: collapse; text-align: left; }
thead th { padding: 18px 24px; font-size: 12px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #E2E8F0; background: #F8FAFC; }
tbody tr { transition: background 0.2s; border-bottom: 1px solid #F1F5F9; }
tbody tr:last-child { border-bottom: none; }
tbody tr:hover { background: #F8FAFC; }
td { padding: 18px 24px; font-size: 14px; color: #334155; font-weight: 500; }
.active-row { background: #F0F9FF !important; }
.active-row td { color: #0369A1; }
.status-running { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 700; color: #0284C7; background: #E0F2FE; padding: 4px 10px; border-radius: 20px; }
.status-running .dot { width: 6px; height: 6px; background: #0EA5E9; border-radius: 50%; animation: pulse 1.5s infinite; }
.mono-font { font-family: 'Roboto Mono', monospace; font-weight: 600; }
.money { color: #334155; }
.total-money { color: #6366F1; font-weight: 700; }
.time-cell { color: #94A3B8; font-size: 13px; font-family: 'Roboto Mono', monospace; }
.badge { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; }
.badge-high { background: #FEF2F2; color: #EF4444; }
.badge-mid { background: #EFF6FF; color: #3B82F6; }
.badge-low { background: #ECFDF5; color: #10B981; }
.empty-state { text-align: center; padding: 40px; color: #94A3B8; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
@media (max-width: 900px) { .stats-grid { grid-template-columns: 1fr; } .table-container { overflow-x: auto; } .usage-page { padding: 20px; } }
</style>