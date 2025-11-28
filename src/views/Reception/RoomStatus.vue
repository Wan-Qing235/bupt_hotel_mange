<template>
  <div>
    <h2 class="section-title"><i class="fas fa-th-large"></i> 实时房态视图</h2>
    
    <div class="legend">
      <span class="dot free"></span> 空闲
      <span class="dot occupied"></span> 入住中
      <span class="dot request"></span> 申请入住
      <span class="dot checkout"></span> 申请结账
    </div>

    <div class="monitor-grid">
      <div v-for="room in hotelStore.rooms" :key="room.id" class="room-card" :class="getCardClass(room)">
        <div class="card-inner">
          <h3>{{ room.id }}</h3>
          <p class="guest">{{ room.guest ? room.guest.name : 'Empty' }}</p>
          <p class="cost">¥{{ room.currentCost.toFixed(0) }}</p>
        </div>
        <div class="card-action" v-if="room.request">
          <button class="btn-mini approve" @click="goCheckIn">去批准</button>
        </div>
        <div class="card-action" v-else-if="room.checkout_pending">
          <button class="btn-mini checkout" @click="goCheckOut">去结账</button>
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

const getCardClass = (room) => {
  if (room.checkout_pending) return 'status-checkout'
  if (room.request) return 'status-request'
  if (room.status === 'occupied') return 'status-occupied'
  return 'status-free'
}

const goCheckIn = () => router.push('/reception/checkin')
const goCheckOut = () => router.push('/reception/checkout')
</script>

<style scoped>
.legend { margin-bottom: 20px; display: flex; gap: 15px; font-size: 14px; color: #666; }
.dot { width: 12px; height: 12px; display: inline-block; border-radius: 50%; margin-right: 5px; }
.dot.free { background: #2ecc71; }
.dot.occupied { background: #3498db; }
.dot.request { background: #f39c12; }
.dot.checkout { background: #e74c3c; }

.monitor-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 15px; }
.room-card { background: white; border-radius: 8px; text-align: center; padding: 15px 10px; border: 2px solid transparent; box-shadow: 0 2px 5px rgba(0,0,0,0.05); position: relative; }

.status-free { border-color: #2ecc71; background: #f0fff4; }
.status-occupied { border-color: #3498db; background: #f0f7ff; }
.status-request { border-color: #f39c12; background: #fef9e7; animation: pulse 2s infinite; }
.status-checkout { border-color: #e74c3c; background: #fff5f5; animation: pulse 2s infinite; }

.card-inner h3 { margin: 0; color: #333; font-size: 20px; }
.card-inner .guest { font-size: 12px; color: #666; margin: 5px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card-inner .cost { font-weight: bold; color: #555; }

.btn-mini { width: 100%; border: none; color: white; font-size: 12px; padding: 4px; border-radius: 4px; margin-top: 5px; cursor: pointer; }
.btn-mini.approve { background: #f39c12; }
.btn-mini.checkout { background: #e74c3c; }

@keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.02); } 100% { transform: scale(1); } }
</style>