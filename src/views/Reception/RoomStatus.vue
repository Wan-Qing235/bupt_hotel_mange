<template>
  <h1>1111111111 测试测试</h1>
  <div class="page-container">
    
    <div class="header-section">
      <div class="header-title">
        <h1><i class="ph-duotone ph-squares-four"></i> 实时房态视图</h1>
        <p class="subtitle">Real-time Room Status Monitor</p>
      </div>
      
      <div class="status-legend">
        <div class="legend-item"><span class="dot free"></span> 空闲 (Free)</div>
        <div class="legend-item"><span class="dot occupied"></span> 入住中 (Occupied)</div>
        <div class="legend-item"><span class="dot request"></span> 申请入住 (Pending)</div>
        <div class="legend-item"><span class="dot checkout"></span> 申请结账 (Checkout)</div>
      </div>
    </div>

    <div class="monitor-grid">
      <div 
        v-for="room in hotelStore.rooms" 
        :key="room.id" 
        class="room-card" 
        :class="getCardClass(room)"
      >
        <div class="status-bar"></div>

        <div class="card-content">
          <div class="card-header">
            <span class="room-id">{{ room.id }}</span>
            <span class="status-icon">
              <i v-if="room.status === 'free' && !room.request" class="ph-bold ph-check-circle"></i>
              <i v-else-if="room.status === 'occupied' && !room.checkout_pending" class="ph-bold ph-user"></i>
              <i v-else-if="room.request" class="ph-fill ph-hand-waving"></i>
              <i v-else-if="room.checkout_pending" class="ph-fill ph-sign-out"></i>
            </span>
          </div>

          <div class="card-body">
            <div class="info-row guest-row">
              <span class="label">住户</span>
              <span class="val" :title="room.guest?.name">
                {{ room.guest ? room.guest.name : '— 空置 —' }}
              </span>
            </div>
            <div class="info-row cost-row">
              <span class="label">消费</span>
              <span class="val money">¥ {{ room.currentCost.toFixed(0) }}</span>
            </div>
          </div>

          <div class="card-actions">
            <button v-if="room.request" class="btn-action btn-approve" @click="goCheckIn">
              <i class="ph-bold ph-check"></i> 批准入住
            </button>
            
            <button v-else-if="room.checkout_pending" class="btn-action btn-checkout" @click="goCheckOut">
              <i class="ph-bold ph-receipt"></i> 办理结账
            </button>
            
            <div v-else class="status-badge">
              {{ getStatusText(room) }}
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { useHotelStore } from '@/store/modules/hotel'
import { useRouter } from 'vue-router'

const hotelStore = useHotelStore()
const router = useRouter()

// 获取卡片样式类
const getCardClass = (room) => {
  if (room.checkout_pending) return 'card-checkout'
  if (room.request) return 'card-request'
  if (room.status === 'occupied') return 'card-occupied'
  return 'card-free'
}

// 获取状态文字
const getStatusText = (room) => {
  if (room.status === 'occupied') return '已入住'
  return '可预订'
}

const goCheckIn = () => router.push('/reception/checkin')
const goCheckOut = () => router.push('/reception/checkout')
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
  font-family: 'Inter', -apple-system, sans-serif;
  color: #1E293B;
  animation: fadeIn 0.5s ease-out;
}

/* =========================
   1. 顶部 Header
   ========================= */
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 40px;
  border-bottom: 1px solid #E2E8F0;
  padding-bottom: 20px;
}

.header-title h1 {
  font-size: 28px; font-weight: 800; color: #1E293B;
  display: flex; align-items: center; gap: 12px; margin: 0;
}
.subtitle { color: #64748B; margin-top: 6px; font-size: 14px; }

.status-legend { display: flex; gap: 20px; }
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #64748B; font-weight: 500; }
.dot { width: 10px; height: 10px; border-radius: 50%; }
.dot.free { background: #10B981; box-shadow: 0 0 0 2px #ECFDF5; }
.dot.occupied { background: #3B82F6; box-shadow: 0 0 0 2px #EFF6FF; }
.dot.request { background: #F59E0B; box-shadow: 0 0 0 2px #FFFBEB; }
.dot.checkout { background: #EF4444; box-shadow: 0 0 0 2px #FEF2F2; }

/* =========================
   2. 网格布局
   ========================= */
.monitor-grid {
  display: grid;
  /* 自适应列宽，最小 220px，填满屏幕 */
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 24px;
}

/* =========================
   3. 房间卡片设计
   ========================= */
.room-card {
  background: #FFFFFF;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
  border: 1px solid #E2E8F0;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  display: flex;
  flex-direction: column;
}

.room-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 20px -5px rgba(0,0,0,0.08);
}

/* 顶部状态条装饰 */
.status-bar { height: 6px; width: 100%; }

.card-content { padding: 20px; flex: 1; display: flex; flex-direction: column; }

/* 头部: ID 和 图标 */
.card-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
}
.room-id { font-size: 24px; font-weight: 800; color: #1E293B; letter-spacing: -0.5px; }
.status-icon { font-size: 22px; }

/* 中间: 信息 */
.card-body { margin-bottom: 20px; flex: 1; }
.info-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: 13px; }
.info-row .label { color: #94A3B8; }
.info-row .val { font-weight: 600; color: #334155; }
.info-row .money { font-family: 'Roboto Mono', monospace; font-size: 15px; }

/* 底部: 操作或状态 */
.card-actions { margin-top: auto; }

/* --- 不同状态的配色方案 --- */

/* A. 空闲 (Free) */
.card-free .status-bar { background: #10B981; }
.card-free .status-icon { color: #10B981; }
.card-free .status-badge { 
  background: #ECFDF5; color: #059669; 
  text-align: center; padding: 8px; border-radius: 8px; font-size: 13px; font-weight: 600;
}

/* B. 入住中 (Occupied) */
.card-occupied .status-bar { background: #3B82F6; }
.card-occupied .status-icon { color: #3B82F6; }
.card-occupied .status-badge { 
  background: #EFF6FF; color: #1D4ED8; 
  text-align: center; padding: 8px; border-radius: 8px; font-size: 13px; font-weight: 600;
}

/* C. 申请入住 (Request) - 带呼吸动画 */
.card-request { border-color: #FCD34D; animation: pulse-border 2s infinite; }
.card-request .status-bar { background: #F59E0B; }
.card-request .status-icon { color: #F59E0B; }
.btn-approve {
  width: 100%; border: none; padding: 10px; border-radius: 10px; cursor: pointer;
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
  color: white; font-weight: 600; font-size: 13px;
  display: flex; align-items: center; justify-content: center; gap: 6px;
  box-shadow: 0 4px 10px rgba(245, 158, 11, 0.3); transition: 0.2s;
}
.btn-approve:hover { transform: translateY(-1px); box-shadow: 0 6px 15px rgba(245, 158, 11, 0.4); }

/* D. 申请结账 (Checkout) - 带呼吸动画 */
.card-checkout { border-color: #FCA5A5; animation: pulse-border-red 2s infinite; }
.card-checkout .status-bar { background: #EF4444; }
.card-checkout .status-icon { color: #EF4444; }
.btn-checkout {
  width: 100%; border: none; padding: 10px; border-radius: 10px; cursor: pointer;
  background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
  color: white; font-weight: 600; font-size: 13px;
  display: flex; align-items: center; justify-content: center; gap: 6px;
  box-shadow: 0 4px 10px rgba(239, 68, 68, 0.3); transition: 0.2s;
}
.btn-checkout:hover { transform: translateY(-1px); box-shadow: 0 6px 15px rgba(239, 68, 68, 0.4); }

/* 动画定义 */
@keyframes pulse-border {
  0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4); }
  70% { box-shadow: 0 0 0 6px rgba(245, 158, 11, 0); }
  100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
}
@keyframes pulse-border-red {
  0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  70% { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
  100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>