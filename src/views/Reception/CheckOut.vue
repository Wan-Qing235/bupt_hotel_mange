<template>
  <div class="page-container">
    
    <div v-if="!billData">
      <div class="header-section">
        <div class="title-group">
          <h1><i class="ph-duotone ph-invoice"></i> 结账处理中心</h1>
          <p class="subtitle">Processing & Financial Settlement</p>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon-box icon-orange">
            <i class="ph-bold ph-receipt"></i>
          </div>
          <div class="stat-content">
            <div class="stat-label">待结账单</div>
            <div class="stat-value">{{ pendingList.length }} <span class="stat-unit">笔</span></div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon-box icon-green">
            <i class="ph-bold ph-currency-yen"></i>
          </div>
          <div class="stat-content">
            <div class="stat-label">今日实收</div>
            <div class="stat-value">{{ totalIncomeFormatted }} <span class="stat-unit">元</span></div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon-box icon-blue">
            <i class="ph-bold ph-chart-bar"></i>
          </div>
          <div class="stat-content">
            <div class="stat-label">客单均价</div>
            <div class="stat-value">{{ avgIncomeFormatted }} <span class="stat-unit">元</span></div>
          </div>
        </div>
      </div>

      <div class="list-container">
        <div class="list-header">
          <div class="list-title">待处理列表 <span class="badge-count">{{ pendingList.length }}</span></div>
        </div>

        <div class="table-header" v-if="pendingList.length > 0">
          <div>Room</div>
          <div>Guest Info</div>
          <div>AC Cost</div>
          <div>Stay Cost</div>
          <div>Total</div>
          <div style="text-align:right">Action</div>
        </div>

        <ul class="bill-list" v-if="pendingList.length > 0">
          <li v-for="room in pendingList" :key="room.id" class="bill-item">
            
            <div class="col-room">{{ room.id }}</div>
            
            <div class="col-guest">
              <span class="guest-name">{{ room.guest?.name }}</span>
              <span class="guest-id">ID: {{ room.guest?.idCard || '未知' }}</span>
            </div>
            
            <div class="col-money">¥ {{ room.currentCost.toFixed(2) }}</div>
            
            <div class="col-money">
              ¥ {{ calculateStayFee(room).toFixed(2) }}
              <span style="font-size:12px; color:#94A3B8">({{ room.ac_cycles || 1 }}天)</span>
            </div>
            
            <div class="col-total">
              ¥ {{ (room.currentCost + calculateStayFee(room)).toFixed(2) }}
            </div>
            
            <div class="col-action">
              <button class="btn-settle" @click="handleCheckOut(room.id)">
                <i class="ph-bold ph-check"></i> 确认收款
              </button>
            </div>
          </li>
        </ul>

        <div v-else class="empty-state">
          <div class="empty-icon"><i class="ph-duotone ph-check-circle"></i></div>
          <div class="empty-text">暂无待结账单</div>
          <div style="color:#64748B; font-size:14px; margin-top:5px;">所有客房账单均已结清，今日工作很棒！</div>
        </div>
      </div>
    </div>

    <div v-else class="receipt-overlay">
      <div class="receipt-card">
        <div class="receipt-header">
          <div class="brand-icon"><i class="ph-bold ph-receipt"></i></div>
          <h2 class="title">Bill Detail</h2>
          <p class="subtitle">结账确认单</p>
        </div>

        <div class="bill-content">
          <div class="row">
            <span class="label">房间号</span>
            <span class="val">{{ billData.roomId }}</span>
          </div>
          <div class="row">
            <span class="label">住户姓名</span>
            <span class="val">{{ billData.guest }}</span>
          </div>
          <div class="row">
            <span class="label">入住时间</span>
            <span class="val time">{{ formatDate(billData.checkIn) }}</span>
          </div>
          <div class="row">
            <span class="label">退房时间</span>
            <span class="val time">{{ formatDate(billData.checkOut) }}</span>
          </div>
          
          <div class="dashed-divider"></div>
          
          <div class="row">
            <span class="label">入住天数</span>
            <span class="val">{{ billData.days }} 天</span>
          </div>
          <div class="row">
            <span class="label">住宿费</span>
            <span class="val">¥ {{ billData.roomCost.toFixed(2) }}</span>
          </div>
          <div class="row">
            <span class="label">空调费</span>
            <span class="val">¥ {{ billData.acCost.toFixed(2) }}</span>
          </div>
          
          <div class="total-row">
            <span>总计应收</span>
            <span class="total-price">¥ {{ billData.totalCost.toFixed(2) }}</span>
          </div>
        </div>

        <div class="receipt-footer">
          <a :href="`http://localhost:5000/export/bill/${billData.roomId}`" target="_blank" class="btn-print">
            <i class="ph-bold ph-printer"></i> 打印/导出
          </a>
          <button class="btn-confirm" @click="confirmFinish">
            完成结账 <i class="ph-bold ph-check"></i>
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useHotelStore } from '@/store/modules/hotel'

const hotelStore = useHotelStore()
const billData = ref(null)

// 1. 列表数据：从 Store 获取待结账房间
const pendingList = computed(() => hotelStore.pendingCheckoutRooms)

// 2. 统计数据
const totalIncomeFormatted = computed(() => {
  const val = hotelStore.stats.total_income || 0
  return val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
})

// 计算客单均价 (简单模拟：总收入 / (入住数 || 1))
const avgIncomeFormatted = computed(() => {
  const income = hotelStore.stats.total_income || 0
  const count = hotelStore.stats.today_checkins || 1 // 避免除以0，实际应为历史总结账数
  return (income / count).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
})

// 3. 业务逻辑
const calculateStayFee = (room) => {
  const days = (room.ac_cycles && room.ac_cycles > 0) ? room.ac_cycles : 1
  return days * 100.0
}

const formatDate = (date) => date ? new Date(date * 1000).toLocaleString() : '-'

const handleCheckOut = (roomId) => {
  const room = hotelStore.getRoomById(roomId)
  const days = (room.ac_cycles && room.ac_cycles > 0) ? room.ac_cycles : 1
  const roomCost = days * 100.0
  
  // 生成预览数据
  billData.value = {
    roomId: room.id,
    guest: room.guest?.name,
    checkIn: parseFloat(room.guest?.checkInTime),
    checkOut: Date.now() / 1000,
    acCost: room.currentCost,
    days: days,
    roomCost: roomCost,
    totalCost: room.currentCost + roomCost
  }
}

const confirmFinish = () => {
  hotelStore.confirmCheckout(billData.value.roomId)
  billData.value = null
}
</script>

<style scoped>
/* =========================
   全局容器
   ========================= */
.page-container {
  width: 100%;
  max-width: 1300px;
  margin: 0 auto;
  padding: 30px;
  font-family: 'Inter', -apple-system, sans-serif;
  color: #1E293B;
  animation: fadeIn 0.5s ease-out;
}

/* =========================
   1. Header
   ========================= */
.header-section { margin-bottom: 30px; }
.title-group h1 {
  font-size: 28px; font-weight: 800; color: #1E293B;
  display: flex; align-items: center; gap: 12px; margin: 0;
}
.subtitle { color: #64748B; margin-top: 6px; font-size: 14px; }

/* =========================
   2. 数据看板 (Stats Grid)
   ========================= */
.stats-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin-bottom: 40px;
}

.stat-card {
  background: #FFFFFF; border-radius: 20px; padding: 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03); border: 1px solid rgba(0,0,0,0.02);
  display: flex; align-items: center; gap: 20px; transition: transform 0.2s;
}
.stat-card:hover { transform: translateY(-3px); }

.stat-icon-box {
  width: 60px; height: 60px; border-radius: 16px;
  display: flex; align-items: center; justify-content: center; font-size: 28px; flex-shrink: 0;
}
.icon-orange { background: #FFF7ED; color: #EA580C; }
.icon-green { background: #ECFDF5; color: #059669; }
.icon-blue { background: #EFF6FF; color: #3B82F6; }

.stat-content { display: flex; flex-direction: column; }
.stat-label { font-size: 13px; color: #64748B; font-weight: 600; margin-bottom: 4px; }
.stat-value { font-size: 28px; font-weight: 800; color: #1E293B; letter-spacing: -0.5px; }
.stat-unit { font-size: 14px; color: #94A3B8; font-weight: 500; margin-left: 2px; }

/* =========================
   3. 列表区域
   ========================= */
.list-container {
  background: #FFFFFF; border-radius: 24px;
  box-shadow: 0 10px 30px -10px rgba(0,0,0,0.05);
  padding: 30px; border: 1px solid #E2E8F0;
}

.list-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #E2E8F0;
}
.list-title { font-size: 18px; font-weight: 700; display: flex; align-items: center; gap: 8px; }
.badge-count { background: #6366F1; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px; }

/* 表头 */
.table-header {
  display: grid;
  grid-template-columns: 80px 1.5fr 1fr 1fr 1fr 1.5fr; /* 栅格定义 */
  padding: 0 30px 15px 30px;
  color: #64748B; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
}

/* 列表项 */
.bill-list { list-style: none; padding: 0; margin: 0; }

.bill-item {
  display: grid;
  grid-template-columns: 80px 1.5fr 1fr 1fr 1fr 1.5fr; /* 对齐表头 */
  align-items: center;
  background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px;
  padding: 20px 30px; margin-bottom: 15px; transition: all 0.2s;
  position: relative; overflow: hidden;
}
.bill-item:hover {
  transform: scale(1.01);
  box-shadow: 0 8px 25px rgba(0,0,0,0.06); border-color: #6366F1; z-index: 1;
}
/* 左侧装饰条 */
.bill-item::before {
  content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 6px;
  background: #F59E0B; opacity: 0.8;
}

/* 列样式 */
.col-room { font-size: 18px; font-weight: 800; color: #1E293B; }
.col-guest { display: flex; flex-direction: column; }
.guest-name { font-weight: 600; color: #1E293B; font-size: 15px; }
.guest-id { font-size: 12px; color: #64748B; margin-top: 2px; font-family: monospace; }
.col-money { font-family: 'Roboto Mono', monospace; font-size: 15px; color: #64748B; }
.col-total { font-family: 'Roboto Mono', monospace; font-size: 20px; font-weight: 800; color: #6366F1; }
.col-action { text-align: right; }

/* 按钮 */
.btn-settle {
  background: linear-gradient(135deg, #6366F1 0%, #4338CA 100%);
  color: white; border: none; padding: 10px 24px; border-radius: 12px;
  font-size: 14px; font-weight: 600; cursor: pointer;
  box-shadow: 0 4px 10px rgba(99, 102, 241, 0.3); transition: 0.2s;
  display: inline-flex; align-items: center; gap: 8px;
}
.btn-settle:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(99, 102, 241, 0.4); }

/* 空状态 */
.empty-state { padding: 80px; text-align: center; display: flex; flex-direction: column; align-items: center; }
.empty-icon { font-size: 64px; color: #CBD5E1; margin-bottom: 20px; background: #F8FAFC; width: 120px; height: 120px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.empty-text { font-size: 18px; font-weight: 600; color: #1E293B; margin-bottom: 8px; }

/* =========================
   4. 账单详情叠加层 (Receipt Overlay)
   ========================= */
.receipt-overlay {
  position: fixed; inset: 0; background: rgba(255,255,255,0.9); z-index: 100;
  display: flex; align-items: center; justify-content: center;
  animation: fadeIn 0.3s ease-out;
}

.receipt-card {
  background: white; width: 400px; border-radius: 24px;
  box-shadow: 0 20px 60px -10px rgba(0,0,0,0.1); overflow: hidden;
  border: 1px solid #E2E8F0;
}

.receipt-header {
  text-align: center; padding: 40px 40px 10px; background: #F8FAFC;
}
.brand-icon {
  width: 50px; height: 50px; background: #6366F1; color: white;
  border-radius: 14px; display: flex; align-items: center; justify-content: center;
  font-size: 24px; margin: 0 auto 15px;
}
.title { margin: 0; font-size: 20px; font-weight: 800; color: #1E293B; }
.subtitle { margin: 5px 0 0; font-size: 13px; color: #64748B; }

.bill-content { padding: 30px; }
.row { display: flex; justify-content: space-between; margin-bottom: 12px; font-size: 14px; color: #334155; }
.label { color: #64748B; }
.val { font-weight: 600; }
.dashed-divider { border-top: 2px dashed #E2E8F0; margin: 20px 0; }
.total-row { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 16px; font-weight: 700; }
.total-price { font-size: 24px; color: #6366F1; }

.receipt-footer {
  padding: 20px 30px; background: #F8FAFC; display: flex; gap: 10px;
}
.btn-print, .btn-confirm {
  flex: 1; padding: 12px; border-radius: 12px; border: none; font-weight: 600; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 6px; font-size: 14px;
}
.btn-print { background: white; border: 1px solid #E2E8F0; color: #64748B; text-decoration: none; }
.btn-print:hover { background: #F1F5F9; }
.btn-confirm { background: #10B981; color: white; }
.btn-confirm:hover { background: #059669; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

/* 响应式 */
@media (max-width: 900px) {
  .stats-grid { grid-template-columns: 1fr; }
  .table-header { display: none; } /* 移动端隐藏表头 */
  .bill-item { grid-template-columns: 1fr; gap: 10px; text-align: left; }
  .col-action { text-align: left; margin-top: 10px; }
}
</style>