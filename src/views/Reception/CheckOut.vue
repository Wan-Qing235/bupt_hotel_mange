<template>
  <div>
    <h2 class="section-title"><i class="fas fa-check-out"></i> 结账处理中心</h2>

    <div class="table-container" v-if="!billData">
      <table>
        <thead>
          <tr>
            <th>房间号</th>
            <th>客人</th>
            <th>空调费</th>
            <th>住宿费(天)</th> <th>总应收</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="room in hotelStore.pendingCheckoutRooms" :key="room.id">
            <td style="font-weight: bold; color: #2a5298;">{{ room.id }}</td>
            <td>{{ room.guest?.name }}</td>
            <td>¥{{ room.currentCost.toFixed(2) }}</td>
            <td>
              ¥{{ (calculateStayFee(room)).toFixed(2) }} 
              <small style="color:#999">({{ room.ac_cycles || 1 }}天)</small>
            </td>
            <td style="color: #e74c3c; font-weight: bold;">¥{{ (room.currentCost + calculateStayFee(room)).toFixed(2) }}</td>
            <td>
              <button class="btn-checkout" @click="handleCheckOut(room.id)">
                <i class="fas fa-gavel"></i> 确认结账
              </button>
            </td>
          </tr>
          </tbody>
      </table>
    </div>

    <div class="card bill-details" v-else>
      <div class="card-title"><i class="fas fa-receipt"></i> 账单详情</div>
      
      <div class="print-area">
        <h2 style="text-align: center; margin-bottom: 20px;">波普特酒店 - 结账单</h2>
        <table class="bill-table">
          <tr><td>房间号</td><td>{{ billData.roomId }}</td></tr>
          <tr><td>客人姓名</td><td>{{ billData.guest }}</td></tr>
          <tr><td>入住时间</td><td>{{ formatDate(billData.checkIn) }}</td></tr>
          <tr><td>退房时间</td><td>{{ formatDate(billData.checkOut) }}</td></tr>
          <tr><td colspan="2" style="background:#eee; height:10px;"></td></tr>
          <tr><td>入住天数</td><td>{{ billData.days }} 天 (按开关机次数)</td></tr>
          <tr><td>住宿费</td><td>¥{{ billData.roomCost.toFixed(2) }}</td></tr>
          <tr><td>空调费</td><td>¥{{ billData.acCost.toFixed(2) }}</td></tr>
          <tr><td>总费用</td><td style="font-size: 20px; font-weight: bold; color: #e74c3c;">¥{{ billData.totalCost.toFixed(2) }}</td></tr>
        </table>
      </div>

      <div class="print-actions">
        <a :href="`http://localhost:5000/export/bill/${billData.roomId}`" target="_blank" class="print-btn" style="text-decoration:none; display:inline-flex;">
          <i class="fas fa-file-export"></i> 导出账单文件(TXT)
        </a>
        <button class="print-btn secondary" @click="confirmFinish">完成并关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useHotelStore } from '@/store/modules/hotel'

const hotelStore = useHotelStore()
const billData = ref(null)

const calculateStayFee = (room) => {
  // 规则：一次开关机 = 1天，1天 = 100元
  const days = room.ac_cycles > 0 ? room.ac_cycles : 1
  return days * 100.0
}

const formatDate = (date) => date ? new Date(date * 1000).toLocaleString() : '-'

const handleCheckOut = (roomId) => {
  const room = hotelStore.getRoomById(roomId)
  const days = room.ac_cycles > 0 ? room.ac_cycles : 1
  const roomCost = days * 100.0
  
  // 生成本地预览数据
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
  // 发送确认指令给后端，真正清除房间数据
  hotelStore.confirmCheckout(billData.value.roomId)
  billData.value = null
}
</script>

<style scoped>
/* 保持原有样式，新增 secondary 按钮样式 */
.print-btn.secondary { background: #999; }
.bill-table { width: 100%; border-collapse: collapse; }
.bill-table td { padding: 10px; border-bottom: 1px solid #eee; }
</style>