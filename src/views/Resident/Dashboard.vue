<template>
  <div>
    <div v-if="myRoom?.status === 'occupied'">
      <h2 class="section-title"><i class="fas fa-thermometer-half"></i> 空调控制面板 (房间: {{ myRoom.id }})</h2>
      
      <div class="stats-container">
        <div class="stat-card">
          <div class="stat-label">当前室温</div>
          <div class="stat-value">{{ myRoom.temp }}℃</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">目标温度</div>
          <div class="stat-value">{{ myRoom.target }}℃</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">累计费用</div>
          <div class="stat-value">¥{{ myRoom.currentCost.toFixed(2) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">住户</div>
          <div class="stat-value" style="font-size: 18px">{{ myRoom.guest?.name }}</div>
        </div>
      </div>

      <div class="ac-panel">
        <div class="ac-display" :class="{ 'is-off': !myRoom.isOn }">
          <div class="current-temp">{{ myRoom.target }}</div>
          <div class="temp-label">目标设定温度(℃)</div>
          <div class="status-text" v-if="!myRoom.isOn">已关机</div>
        </div>
        <div class="ac-controls">
          <div class="control-group">
            <span class="control-label">调节温度</span>
            <input type="range" min="18" max="30" :value="myRoom.target" @input="e => updateSettings('target', Number(e.target.value))" class="temp-slider">
            <span class="temp-value">{{ myRoom.target }}℃</span>
          </div>
          <div class="control-group">
            <span class="control-label">风速模式</span>
            <div class="fan-speed">
              <div v-for="speed in ['low', 'medium', 'high']" :key="speed" class="speed-btn" :class="{ active: myRoom.speed === speed }" @click="updateSettings('speed', speed)">
                {{ getSpeedLabel(speed) }}
              </div>
            </div>
          </div>
          <button class="power-btn" :class="myRoom.isOn ? 'on' : 'off'" @click="hotelStore.togglePower(myRoom.id)">
            <i class="fas fa-power-off"></i> {{ myRoom.isOn ? '关机' : '点击开机' }}
          </button>
        </div>
      </div>
    </div>

    <div v-else-if="myRoom?.request" class="waiting-box">
      <div class="icon-pulse"><i class="fas fa-hourglass-half"></i></div>
      <h2>已提交入住申请</h2>
      <p>请稍候，前台工作人员正在核验您的信息...</p>
      <div class="info-preview">
        <p>姓名：{{ myRoom.request.name }}</p>
        <p>证件：{{ myRoom.request.idCard }}</p>
      </div>
    </div>

    <div v-else class="checkin-box">
      <h2><i class="fas fa-hotel"></i> 自助办理入住 (房间 {{ myRoom?.id }})</h2>
      <p class="subtitle">欢迎光临波普特酒店，请完善以下信息以激活房间设施。</p>
      
      <div class="form-group">
        <label>您的姓名</label>
        <input type="text" v-model="form.name" class="form-control" placeholder="请输入真实姓名">
      </div>
      <div class="form-group">
        <label>身份证号</label>
        <input type="text" v-model="form.idCard" class="form-control" placeholder="请输入身份证号码">
      </div>
      
      <button class="btn-submit" @click="submitRequest" :disabled="!form.name || !form.idCard">
        提交入住申请
      </button>
    </div>

  </div>
</template>

<script setup>
import { computed, reactive } from 'vue'
import { useHotelStore } from '@/store/modules/hotel'

const hotelStore = useHotelStore()
const myRoom = computed(() => hotelStore.currentUserRoom)

const form = reactive({ name: '', idCard: '' })

function submitRequest() {
  if (myRoom.value) {
    hotelStore.submitCheckInRequest(myRoom.value.id, { ...form })
  }
}

function getSpeedLabel(speed) {
  const map = { low: '低风', medium: '中风', high: '高风' }
  return map[speed] || '-'
}

const updateSettings = (key, value) => {
  if (!myRoom.value) return
  hotelStore.updateRoomState(myRoom.value.id, { [key]: value })
}
</script>

<style scoped>
/* === 1. 统计卡片区域：2x2 网格 === */
.stats-container {
  display: grid;
  /* 强制两列，每列等宽 */
  grid-template-columns: repeat(2, 1fr) !important; 
  /* 卡片之间的间距 */
  gap: 20px; 
  /* 关键：宽度占满父容器，与下方对齐 */
  /*width: 100%; */
  box-sizing: border-box;
  margin-bottom: 25px;
}

.stat-card {
  background: white;
  padding: 25px;
  border-radius: 12px; /* 圆角与下方保持一致 */
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05); /* 阴影与下方保持一致 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 110px;
}

.stat-value { 
  font-size: 28px; 
  font-weight: 700; 
  color: #2a5298; 
  margin-top: 10px; 
}

.stat-label { 
  font-size: 14px; 
  color: #666; 
  font-weight: 500;
}

/* === 2. 下方控制面板 === */
.ac-panel { 
  /* 关键：宽度占满，强制使用 border-box 防止 padding 撑大 */
  width: 100%; 
  box-sizing: border-box; 
  
  background: white; 
  padding: 30px; 
  border-radius: 12px; 
  box-shadow: 0 4px 12px rgba(0,0,0,0.05); 
  margin-top: 0;
}

/* === 3. 面板内部元素样式 (保持精致) === */
.ac-display { 
  text-align: center; 
  margin-bottom: 30px; 
  padding: 25px; 
  background: #f8f9fa; 
  border-radius: 12px; 
  position: relative; 
  transition: all 0.3s; 
}
.ac-display.is-off { opacity: 0.6; filter: grayscale(100%); }

.status-text { 
  position: absolute; 
  top: 50%; 
  left: 50%; 
  transform: translate(-50%, -50%); 
  font-size: 24px; 
  font-weight: bold; 
  color: #555; 
  background: rgba(255,255,255,0.95); 
  padding: 12px 24px; 
  border-radius: 8px; 
  box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
  white-space: nowrap;
}

.current-temp { font-size: 64px; font-weight: 700; color: #2a5298; line-height: 1; letter-spacing: -2px; }
.temp-label { color: #888; margin-top: 8px; font-size: 14px; }

.ac-controls { display: flex; flex-direction: column; gap: 25px; }
.control-group { display: flex; align-items: center; justify-content: space-between; padding: 5px 0; }
.control-label { font-weight: 600; min-width: 80px; font-size: 15px; color: #333; }

.temp-slider { flex: 1; margin: 0 20px; cursor: pointer; height: 6px; }
.temp-value { font-weight: bold; color: #2a5298; min-width: 50px; text-align: right; font-size: 18px; }

.fan-speed { display: flex; gap: 15px; flex: 1; }
.speed-btn { 
  flex: 1; 
  text-align: center; 
  padding: 12px; 
  border: 1px solid #eee; 
  background: #fff; 
  border-radius: 8px; 
  cursor: pointer; 
  transition: all 0.2s; 
  font-size: 14px; 
  font-weight: 500;
  color: #555;
}
.speed-btn:hover { background: #f0f7ff; border-color: #d0e4ff; }
.speed-btn.active { background: #2a5298; color: white; border-color: #2a5298; box-shadow: 0 4px 10px rgba(42, 82, 152, 0.2); }

.power-btn { 
  width: 100%; 
  padding: 16px; 
  border: none; 
  border-radius: 10px; 
  font-size: 18px; 
  font-weight: 600; 
  cursor: pointer; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  gap: 10px; 
  margin-top: 15px; 
  transition: all 0.2s; 
}
.power-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(0,0,0,0.1); }
.power-btn.on { background: #e74c3c; color: white; }
.power-btn.off { background: #2a5298; color: white; }

/* === 其他页面样式 === */
.checkin-box, .waiting-box {
  background: white;
  padding: 40px;
  border-radius: 12px;
  text-align: center;
  max-width: 500px;
  margin: 50px auto;
  box-shadow: 0 10px 30px rgba(0,0,0,0.08);
}
.checkin-box h2 { color: #2a5298; margin-bottom: 10px; }
.subtitle { color: #666; margin-bottom: 30px; font-size: 14px; }
.form-group { text-align: left; margin-bottom: 20px; }
.form-group label { display: block; font-weight: 600; margin-bottom: 8px; color: #444; }
.form-control { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; }
.btn-submit { width: 100%; padding: 12px; background: #2a5298; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; }
.btn-submit:disabled { background: #ccc; cursor: not-allowed; }

.waiting-box .icon-pulse { font-size: 40px; color: #f39c12; margin-bottom: 20px; animation: pulse 1.5s infinite; }
.info-preview { background: #f9f9f9; padding: 15px; border-radius: 8px; margin-top: 20px; text-align: left; }
.info-preview p { margin: 5px 0; color: #555; }

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.7; }
  100% { transform: scale(1); opacity: 1; }
}

/* 响应式：手机竖屏变单列 */
@media (max-width: 480px) {
  .stats-container { grid-template-columns: 1fr !important; }
}
</style>