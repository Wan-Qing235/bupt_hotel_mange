<template>
  <div>
    <h2 class="section-title"><i class="fas fa-check-in"></i> 入住申请处理</h2>
    
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>房间号</th>
            <th>申请人姓名</th>
            <th>身份证号</th>
            <th>申请时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="room in pendingRequests" :key="room.id">
            <td style="font-weight: bold; color: #2a5298;">{{ room.id }}</td>
            <td>{{ room.request.name }}</td>
            <td>{{ room.request.idCard }}</td>
            <td>刚刚</td>
            <td>
              <button class="btn-approve" @click="handleApprove(room.id)">
                <i class="fas fa-check"></i> 批准入住
              </button>
            </td>
          </tr>
          
          <tr v-if="pendingRequests.length === 0">
            <td colspan="5" class="empty-text">
              <i class="fas fa-inbox"></i> 当前没有待处理的入住申请
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useHotelStore } from '@/store/modules/hotel'

const hotelStore = useHotelStore()

// 只显示有 request 的房间
const pendingRequests = computed(() => {
  return hotelStore.rooms.filter(r => r.request !== null && r.status === 'free')
})

const handleApprove = (roomId) => {
  if (confirm(`确认批准房间 ${roomId} 的入住申请吗？`)) {
    hotelStore.approveCheckIn(roomId)
  }
}
</script>

<style scoped>
.btn-approve {
  background: #2ecc71;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
  display: flex; align-items: center; gap: 5px;
}
.btn-approve:hover { background: #27ae60; transform: translateY(-1px); }

.empty-text { text-align: center; padding: 40px; color: #999; font-size: 16px; }
.empty-text i { display: block; font-size: 32px; margin-bottom: 10px; color: #eee; }
</style>