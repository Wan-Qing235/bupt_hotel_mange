<template>
  <div class="checkout-page">
    <div class="container-grid">
      
      <div class="info-panel fade-in-left">
        <div class="welcome-text">
          <h1>结账服务</h1>
          <p>感谢您选择 BUPT Hotel。请核对右侧账单详情，确认无误后发起结账申请。</p>
        </div>

        <div class="stay-timeline">
          <div class="timeline-item">
            <div class="dot active"></div>
            <div class="content">
              <span class="label">当前时间 (Current Time)</span>
              <span class="time highlight">{{ currentTime }}</span>
            </div>
          </div>
          <div class="line"></div>
          <div class="timeline-item">
            <div class="dot current"></div>
            <div class="content">
              <span class="label">住宿时长 (Duration)</span>
              <span class="time">共入住 {{ stayDays }} 晚</span>
            </div>
          </div>
        </div>

        <div class="support-card">
          <div class="icon-box">
            <i class="fas fa-headset"></i>
          </div>
          <div class="text">
            <h4>需要帮助？</h4>
            <p>如对费用有疑问，请联系前台 <strong>8000</strong></p>
          </div>
        </div>
      </div>

      <div class="action-panel fade-in-right">
        
        <div v-if="myRoom?.checkout_pending" class="glass-card success-card">
          <div class="icon-wrapper">
            <i class="fas fa-check-circle"></i>
          </div>
          <h2>请求已发送</h2>
          <p class="sub-text">系统已锁定账单，请前往前台完成最后支付。</p>
          
          <div class="total-preview-box">
            <span>预计总费用</span>
            <span class="amount">¥ {{ totalFee.toFixed(2) }}</span>
          </div>
          
          <div class="status-steps">
            <div class="step done">1. 发起申请</div>
            <div class="step active">2. 前台核验</div>
            <div class="step">3. 完成退房</div>
          </div>
        </div>

        <div v-else-if="myRoom" class="receipt-card">
          <div class="stamp">UNPAID</div>

          <div class="receipt-header">
            <div class="brand-icon">
              <i class="fas fa-file-invoice-dollar"></i>
            </div>
            <h2 class="title">Checkout Bill</h2>
            <p class="subtitle">客房结账确认单</p>

            <div class="guest-info">
              <div class="guest-item">
                <span class="g-label">Room</span>
                <span class="g-val"><i class="fas fa-door-closed"></i> {{ myRoom.id }}</span>
              </div>
              <div class="guest-item right">
                <span class="g-label">Guest</span>
                <span class="g-val">{{ myRoom.guest?.name }} <i class="fas fa-user"></i></span>
              </div>
            </div>

            <div class="bill-details">
              <div class="bill-row">
                <span><i class="fas fa-bed"></i> 住宿费 ({{ stayDays }}天 × {{ roomRate }})</span>
                <strong>¥ {{ roomFee.toFixed(2) }}</strong>
              </div>
              <div class="bill-row">
                <span><i class="fas fa-wind"></i> 空调使用费</span>
                <strong>¥ {{ myRoom.currentCost.toFixed(2) }}</strong>
              </div>
            </div>
          </div>

          <div class="receipt-cutout">
            <div class="dashed-line"></div>
          </div>

          <div class="receipt-footer">
            <div class="total-wrapper">
              <div class="total-label">Total Payment</div>
              <div class="total-amount"><span class="currency">¥</span>{{ totalFee.toFixed(2) }}</div>
            </div>

            <div class="tip-capsule">
              <i class="fas fa-info-circle"></i>
              <span>发起结账后，空调将自动关闭且无法再次开启。</span>
            </div>

            <button class="pay-btn" @click="handleSubmit">
              <span>确认并发起申请</span>
              <i class="fas fa-paper-plane"></i>
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useHotelStore } from '@/store/modules/hotel'

const hotelStore = useHotelStore()
const myRoom = computed(() => hotelStore.currentUserRoom)

const currentTime = ref('')
let timer = null

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit', 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit',
    hour12: false
  })
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

// === 费用计算逻辑 ===
const stayDays = computed(() => {
  return (myRoom.value?.ac_cycles && myRoom.value.ac_cycles > 0) ? myRoom.value.ac_cycles : 1
})

// [修改] 动态获取房间单价
const roomRate = computed(() => {
  return myRoom.value?.room_rate || 100.0
})

const roomFee = computed(() => stayDays.value * roomRate.value)

const totalFee = computed(() => (myRoom.value?.currentCost || 0) + roomFee.value)

const handleSubmit = () => {
  if(confirm(`确认要办理退房吗？\n\n房间单价: ¥${roomRate.value}/天\n空调费: ¥${myRoom.value.currentCost.toFixed(2)}\n房费: ¥${roomFee.value}\n总计: ¥${totalFee.value.toFixed(2)}`)) {
    hotelStore.requestCheckout(myRoom.value.id)
  }
}
</script>

<style scoped>
/* 样式代码保持不变，直接复用之前的即可 */
.checkout-page {
  width: 100%;
  height: 100%;
  position: relative;
  background: transparent;
  padding: 40px;
  box-sizing: border-box;
  overflow-y: auto; 
  font-family: 'Inter', system-ui, sans-serif;
  color: #1E293B;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.container-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  max-width: 1100px;
  width: 100%;
  position: relative;
  z-index: 10;
  align-items: end;
}

.info-panel { display: flex; flex-direction: column; gap: 40px; }

.welcome-text h1 { font-size: 42px; font-weight: 800; color: #0F172A; margin-bottom: 16px; letter-spacing: -1px; }
.welcome-text p { font-size: 16px; color: #64748B; line-height: 1.6; max-width: 420px; }

.stay-timeline { display: flex; flex-direction: column; gap: 0; padding-left: 10px; }
.timeline-item { display: flex; gap: 20px; align-items: flex-start; position: relative; }
.line { width: 2px; height: 30px; background: #E2E8F0; margin-left: 6px; margin-top: -5px; margin-bottom: -5px; }
.dot { width: 14px; height: 14px; border-radius: 50%; border: 3px solid #F8FAFC; box-shadow: 0 0 0 2px #E2E8F0; background: #CBD5E1; flex-shrink: 0; z-index: 1; }
.dot.active { background: #6366F1; box-shadow: 0 0 0 2px #6366F1; }
.dot.current { background: #10B981; box-shadow: 0 0 0 2px #10B981; }

.timeline-item .content { display: flex; flex-direction: column; margin-top: -4px; }
.timeline-item .label { font-size: 12px; font-weight: 700; color: #94A3B8; text-transform: uppercase; }
.timeline-item .time { font-size: 16px; font-weight: 600; color: #334155; margin-top: 2px; }
.timeline-item .time.highlight { color: #6366F1; font-family: 'Roboto Mono', monospace; font-weight: 700; }

.support-card {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.5);
  padding: 20px; border-radius: 16px;
  display: flex; gap: 16px; align-items: center;
  max-width: 360px;
}
.icon-box { width: 40px; height: 40px; background: #EFF6FF; color: #3B82F6; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.text h4 { margin: 0; font-size: 14px; color: #1E293B; }
.text p { margin: 2px 0 0 0; font-size: 13px; color: #64748B; }

.action-panel { display: flex; justify-content: center; width: 100%; }

.success-card {
  width: 100%; max-width: 400px;
  background: rgba(255,255,255,0.8);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 40px; text-align: center;
  box-shadow: 0 20px 40px rgba(0,0,0,0.05);
  border: 1px solid white;
}
.success-card .icon-wrapper { font-size: 60px; color: #10B981; margin-bottom: 20px; animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.success-card h2 { margin: 0 0 10px 0; color: #0F172A; }
.sub-text { color: #64748B; font-size: 14px; margin-bottom: 30px; }

.total-preview-box {
  background: #F0FDF4; border: 1px dashed #BBF7D0;
  padding: 15px; border-radius: 12px;
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 30px;
}
.total-preview-box span { color: #166534; font-size: 14px; font-weight: 600; }
.total-preview-box .amount { font-size: 20px; font-weight: 800; }

.status-steps { display: flex; justify-content: space-between; font-size: 12px; color: #94A3B8; }
.status-steps .step.done { color: #10B981; font-weight: 600; }
.status-steps .step.active { color: #3B82F6; font-weight: 600; }

.receipt-card {
  width: 100%; max-width: 400px;
  background: #fff;
  border-radius: 24px;
  overflow: hidden; position: relative;
  box-shadow: 0 20px 60px -10px rgba(0,0,0,0.1);
}

.stamp {
  position: absolute; top: 20px; right: 20px; width: 80px; height: 80px;
  border: 3px solid #E2E8F0; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; color: #CBD5E1;
  transform: rotate(-20deg); pointer-events: none; z-index: 0;
}

.receipt-header { padding: 40px 40px 10px 40px; text-align: center; background: rgba(255,255,255,0.95); position: relative; z-index: 1; }

.brand-icon {
  width: 60px; height: 60px;
  background: linear-gradient(135deg, #6366F1, #818CF8);
  border-radius: 18px; color: white; font-size: 28px;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 15px; box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3);
  transform: rotate(-5deg);
}

.title { font-size: 22px; font-weight: 800; color: #1E293B; margin-bottom: 4px; }
.subtitle { font-size: 13px; color: #64748B; }

.guest-info {
  margin-top: 25px; background: #F8FAFC; border: 1px dashed #CBD5E1;
  border-radius: 12px; padding: 12px;
  display: flex; justify-content: space-between; font-size: 13px;
}
.guest-item { display: flex; flex-direction: column; gap: 2px; text-align: left; }
.right { text-align: right; align-items: flex-end; }
.g-label { color: #94A3B8; font-size: 11px; font-weight: 600; text-transform: uppercase; }
.g-val { font-weight: 700; color: #1E293B; display: flex; align-items: center; gap: 5px; }

.bill-details { padding: 20px 0; }
.bill-row { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 12px; color: #64748B; }
.bill-row strong { color: #1E293B; font-weight: 600; font-family: 'Roboto Mono', monospace; }

.receipt-cutout {
  position: relative; height: 30px; background: rgba(255,255,255,0.95);
  display: flex; align-items: center; justify-content: center;
}
.receipt-cutout::before, .receipt-cutout::after {
  content: ''; position: absolute; top: 50%; transform: translateY(-50%);
  width: 20px; height: 20px; background-color: #EBF1F7;
  border-radius: 50%; box-shadow: inset 0 0 5px rgba(0,0,0,0.05);
}
.receipt-cutout::before { left: -10px; }
.receipt-cutout::after { right: -10px; }
.dashed-line { width: 80%; height: 1px; border-top: 2px dashed #E2E8F0; }

.receipt-footer {
  background: linear-gradient(to bottom, rgba(255,255,255,0.95), #fff);
  padding: 10px 40px 40px 40px; text-align: center; position: relative; z-index: 1;
}
.total-wrapper { margin-bottom: 25px; }
.total-label { font-size: 12px; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
.total-amount {
  font-size: 40px; font-weight: 800; color: #1E293B; margin-top: 4px;
  background: linear-gradient(135deg, #1E293B 0%, #475569 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.currency { font-size: 24px; vertical-align: top; margin-right: 4px; }

.tip-capsule {
  background: #FFF7ED; color: #C2410C; border: 1px solid #FFEDD5;
  padding: 10px 16px; border-radius: 30px; font-size: 12px; line-height: 1.4;
  margin-bottom: 24px; display: flex; align-items: flex-start; gap: 8px; text-align: left;
}
.tip-capsule i { font-size: 16px; flex-shrink: 0; margin-top: 2px; }

.pay-btn {
  width: 100%; padding: 16px; background: #1E293B; color: white;
  border: none; border-radius: 14px; font-size: 16px; font-weight: 600;
  cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px;
  transition: all 0.3s;
}
.pay-btn:hover { transform: translateY(-2px); background: #0F172A; box-shadow: 0 10px 20px rgba(15, 23, 42, 0.2); }

@keyframes fadeInLeft { from { opacity: 0; transform: translateX(-20px); } to { opacity: 1; transform: translateX(0); } }
@keyframes fadeInRight { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }
@keyframes popIn { from { transform: scale(0.5); opacity: 0; } to { transform: scale(1); opacity: 1; } }

@media (max-width: 900px) {
  .container-grid { grid-template-columns: 1fr; gap: 40px; padding-bottom: 40px; align-items: center; }
  .info-panel { text-align: center; align-items: center; }
  .stay-timeline { align-items: center; }
  .checkout-page { display: block; overflow-y: auto; }
}
</style>