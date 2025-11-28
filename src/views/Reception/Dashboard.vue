<template>
  <div>
    <h2 class="section-title"><i class="fas fa-tachometer-alt"></i> 前台工作台</h2>
    
    <div class="grid-cards">
      <div class="card status-card">
        <div class="icon-box blue"><i class="fas fa-bed"></i></div>
        <div class="text">
          <h3>空闲房间</h3>
          <p class="num">{{ freeCount }}</p>
        </div>
      </div>

      <div class="card status-card">
        <div class="icon-box green"><i class="fas fa-user-check"></i></div>
        <div class="text">
          <h3>今日入住</h3>
          <p class="num">{{ todayCheckInCount }}</p>
        </div>
      </div>

      <div class="card status-card">
        <div class="icon-box red"><i class="fas fa-door-open"></i></div>
        <div class="text">
          <h3>使用中</h3>
          <p class="num">{{ occupiedCount }}</p>
        </div>
      </div>
    </div>

    <h3 style="margin: 30px 0 15px; color: #444;">快捷操作</h3>
    <div class="quick-actions">
      <div class="action-btn" @click="$router.push('/reception/checkin')">
        <i class="fas fa-plus-circle"></i> 办理入住
      </div>
      <div class="action-btn" @click="$router.push('/reception/checkout')">
        <i class="fas fa-file-invoice"></i> 办理结账
      </div>
      <div class="action-btn" @click="$router.push('/reception/room-status')">
        <i class="fas fa-th-large"></i> 房态视图
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useHotelStore } from '@/store/modules/hotel'

const hotelStore = useHotelStore()

// 1. 实时计算空闲房间数
const freeCount = computed(() => hotelStore.freeRooms.length)

// 2. 实时计算使用中房间数
const occupiedCount = computed(() => hotelStore.occupiedRooms.length)

// 3. 实时计算“今日入住”数
// 逻辑：遍历所有已入住房间，看入住时间是不是“今天”
const todayCheckInCount = computed(() => hotelStore.stats.today_checkins)
</script>

<style scoped>
.grid-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.status-card { display: flex; align-items: center; padding: 25px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.icon-box { width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-right: 20px; }
.icon-box.blue { background: #e3f2fd; color: #1976d2; }
.icon-box.green { background: #e8f5e9; color: #388e3c; }
.icon-box.red { background: #ffebee; color: #d32f2f; }
.text h3 { font-size: 14px; color: #666; font-weight: normal; margin-bottom: 5px; }
.text .num { font-size: 28px; font-weight: bold; color: #333; }

.quick-actions { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.action-btn { background: white; padding: 25px; border-radius: 10px; text-align: center; cursor: pointer; transition: all 0.2s; border: 1px solid transparent; font-weight: 600; color: #555; display: flex; flex-direction: column; align-items: center; gap: 10px; }
.action-btn i { font-size: 32px; color: #2a5298; margin-bottom: 5px; }
.action-btn:hover { border-color: #2a5298; background: #f0f7ff; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(42, 82, 152, 0.1); }
</style>