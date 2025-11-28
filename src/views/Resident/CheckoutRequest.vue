<template>
  <div>
    <h2 class="section-title"><i class="fas fa-file-invoice-dollar"></i> 结账请求</h2>
    
    <div class="card request-card" v-if="myRoom">
      <div v-if="myRoom.checkout_pending" class="pending-state">
        <i class="fas fa-check-circle" style="color: #2ecc71; font-size: 48px; margin-bottom: 15px;"></i>
        <h3>请求已发送</h3>
        <p>请前往前台办理最后的结算手续。</p>
        <p class="total-preview">预计总费用: ¥{{ totalFee.toFixed(2) }}</p>
      </div>

      <div v-else>
        <div class="info-row"><span>当前房间</span><span class="value">{{ myRoom.id }}</span></div>
        <div class="info-row"><span>住户姓名</span><span class="value">{{ myRoom.guest?.name }}</span></div>
        
        <div class="bill-breakdown">
          <div class="info-row">
            <span>空调使用费</span>
            <span class="value">¥{{ myRoom.currentCost.toFixed(2) }}</span>
          </div>
          <div class="info-row">
            <span>住宿费 ({{ stayDays }}天 × ¥100)</span>
            <span class="value">¥{{ roomFee.toFixed(2) }}</span>
          </div>
          <div class="divider"></div>
          <div class="info-row highlight">
            <span>结账总金额</span>
            <span class="value total">¥{{ totalFee.toFixed(2) }}</span>
          </div>
        </div>
        
        <div class="tips">
          <i class="fas fa-info-circle"></i> 发起结账请求后，空调将自动关闭且无法再次开启。
        </div>
        
        <button class="btn-submit" @click="handleSubmit">
          <i class="fas fa-paper-plane"></i> 确认发起结账请求
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useHotelStore } from '@/store/modules/hotel'

const hotelStore = useHotelStore()
const myRoom = computed(() => hotelStore.currentUserRoom)

// [新增] 计算住宿天数 (最少1天)
const stayDays = computed(() => {
  return (myRoom.value?.ac_cycles && myRoom.value.ac_cycles > 0) ? myRoom.value.ac_cycles : 1
})

// [新增] 计算住宿费
const roomFee = computed(() => stayDays.value * 100.0)

// [新增] 计算总费
const totalFee = computed(() => (myRoom.value?.currentCost || 0) + roomFee.value)

const handleSubmit = () => {
  if(confirm(`当前空调费 ¥${myRoom.value.currentCost.toFixed(2)}，房费 ¥${roomFee.value}，总计 ¥${totalFee.value.toFixed(2)}。\n确定要发起结账吗？`)) {
    hotelStore.requestCheckout(myRoom.value.id)
  }
}
</script>

<style scoped>
/* 样式保持不变 */
.request-card { background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; }
.info-row { display: flex; justify-content: space-between; padding: 12px 0; color: #555; }
.value { font-weight: 600; color: #333; }
.bill-breakdown { background: #f9f9f9; padding: 15px; border-radius: 8px; margin: 20px 0; }
.divider { border-bottom: 1px dashed #ccc; margin: 10px 0; }
.info-row.highlight { margin-top: 5px; }
.value.total { color: #e74c3c; font-size: 24px; font-weight: bold; }
.tips { background: #fff3cd; color: #856404; padding: 15px; border-radius: 6px; margin: 20px 0; font-size: 14px; display: flex; align-items: center; gap: 10px; }
.btn-submit { width: 100%; padding: 15px; background: #2a5298; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; transition: all 0.3s; }
.btn-submit:hover { background: #1e3c72; }
.pending-state { text-align: center; padding: 40px 0; }
.total-preview { margin-top: 15px; font-size: 18px; color: #2a5298; font-weight: bold; }
</style>