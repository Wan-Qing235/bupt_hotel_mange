<template>
  <div class="dashboard-wrapper">
    <div v-if="myRoom?.status === 'occupied'" class="main-layout fade-in">
      
      <div class="clean-card main-card">
        <div class="card-header">
          <div class="title-section">
            <h1>房间 {{ myRoom.id }}</h1>
            <div class="status-tag" :class="{ 'active': myRoom.isOn }">
              <div class="dot"></div>
              {{ myRoom.isOn ? '舒适运行中' : '设备待机' }}
            </div>
          </div>
          <p class="subtitle">智能环境控制终端</p>
        </div>

        <div class="dial-area">
          <div class="dial-ring" :class="{ 'is-off': !myRoom.isOn }">
            <div class="dial-content">
              <div class="temp-big">
                {{ myRoom.target }}<span class="unit">°C</span>
              </div>
              <div class="mode-label">{{ myRoom.isOn ? '制冷模式' : '已关机' }}</div>
            </div>
            <svg class="dial-svg" viewBox="0 0 200 200">
              <circle class="bg-ring" cx="100" cy="100" r="90" />
              <circle class="progress-ring" cx="100" cy="100" r="90" :stroke-dasharray="calculateStroke(myRoom.target)" />
            </svg>
          </div>
        </div>

        <div class="controls-row" :class="{ 'disabled': !myRoom.isOn }">
          <div class="control-cell flex-2">
            <label><i class="ph-bold ph-thermometer"></i> 温度调节</label>
            <div class="slider-container">
              <span>18°</span>
              <input type="range" min="18" max="25" :value="myRoom.target" @input="e => updateSettings('target', Number(e.target.value))">
              <span>25°</span>
            </div>
          </div>
          <div class="divider"></div>
          <div class="control-cell flex-1">
            <label><i class="ph-bold ph-fan"></i> 风速</label>
            <div class="fan-selector">
              <div v-for="s in ['low', 'medium', 'high']" :key="s" 
                   class="fan-opt" :class="{ active: myRoom.speed === s }"
                   @click="updateSettings('speed', s)">
                {{ getSpeedLabel(s) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="clean-card side-card">
        <div class="power-wrapper">
          <button class="power-btn" :class="{ 'active': myRoom.isOn }" @click="hotelStore.togglePower(myRoom.id)">
            <i class="ph-bold ph-power"></i>
          </button>
          <span>{{ myRoom.isOn ? '点击关闭空调' : '点击开启空调' }}</span>
        </div>

        <div class="info-list">
          <div class="info-row">
            <div class="icon-square blue"><i class="ph-fill ph-thermometer-simple"></i></div>
            <div class="info-detail">
              <span class="label">实时室温</span>
              <span class="val">{{ myRoom.temp }}°C</span>
            </div>
          </div>
          
          <div class="info-row">
            <div class="icon-square purple"><i class="ph-fill ph-coins"></i></div>
            <div class="info-detail">
              <span class="label">累计电费</span>
              <span class="val">¥ {{ myRoom.currentCost.toFixed(2) }}</span>
            </div>
          </div>

          <div class="info-row">
            <div class="icon-square green"><i class="ph-fill ph-user"></i></div>
            <div class="info-detail">
              <span class="label">登记住户</span>
              <span class="val">{{ myRoom.guest?.name || '--' }}</span>
            </div>
          </div>
        </div>

        <div class="eco-card">
          <i class="ph-duotone ph-leaf"></i>
          <div>
            <strong>节能托管</strong>
            <p>已优化能耗策略</p>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="center-layout fade-in">
      <div class="clean-card form-card">
        <div v-if="myRoom?.request">
           <div class="status-icon warning"><i class="ph-fill ph-hourglass"></i></div>
           <h2>申请审核中</h2>
           <p class="desc">前台正在处理您的入住请求...</p>
        </div>
        <div v-else>
           <div class="status-icon primary"><i class="ph-fill ph-house-line"></i></div>
           <h2>欢迎入住</h2>
           <p class="desc">房间 {{ myRoom?.id }} · 请完善信息激活设施</p>
           
           <div class="form-body">
             <div class="input-box">
               <label>姓名</label>
               <input type="text" v-model="form.name" placeholder="请输入真实姓名">
             </div>
             <div class="input-box">
               <label>身份证号</label>
               <input type="text" v-model="form.idCard" placeholder="请输入证件号码">
             </div>
           </div>
           
           <button class="submit-btn" @click="submitRequest" :disabled="!form.name || !form.idCard">
             立即激活 <i class="ph-bold ph-arrow-right"></i>
           </button>
        </div>
      </div>
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
  if (myRoom.value) hotelStore.submitCheckInRequest(myRoom.value.id, { ...form })
}

function getSpeedLabel(speed) {
  const map = { low: '低', medium: '中', high: '高' }
  return map[speed] || '-'
}

const updateSettings = (key, value) => {
  if (!myRoom.value) return
  hotelStore.updateRoomState(myRoom.value.id, { [key]: value })
}

const calculateStroke = (temp) => {
  const min = 18, max = 30;
  const percent = Math.max(0, Math.min(1, (temp - min) / (max - min))); 
  const circumference = 2 * Math.PI * 90; 
  return `${percent * circumference} ${circumference}`; 
}
</script>

<style scoped>
/* =========================================
   1. 全局容器：改为 Flex 布局，解决高度截断问题
   ========================================= */
.dashboard-wrapper {
  width: 100%;
  /* 关键修改：从 height: 100% 改为 min-height: 100% 
     这样当内容多时会自动撑开，不会被截断 */
  min-height: 100%; 
  
  /* 关键修改：使用 flex 布局让内部元素自动撑满高度 */
  display: flex;
  flex-direction: column;
  
  position: relative;
  background: transparent; 
  padding: 40px; 
  box-sizing: border-box;
  font-family: 'Inter', -apple-system, sans-serif;
  color: #1E293B;
  
  /* 去掉 overflow: hidden，否则内容多了会被切掉 */
  /* overflow: hidden;  <-- 删除这行 */
}

/* =========================================
   2. 主布局：撑满剩余空间
   ========================================= */
.main-layout {
  position: relative; 
  z-index: 1;
  display: flex; 
  gap: 40px;
  
  /* 关键修改：flex: 1 让它占据所有垂直空间 */
  flex: 1; 
  /* 删掉 height: 100%，避免限制死高度 */
}

/* =========================================
   3. 卡片通用样式：确保拉伸对齐
   ========================================= */
.clean-card {
  background: #FFFFFF; 
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); 
  border-radius: 32px;
  border: 1px solid rgba(0,0,0,0.02);
  padding: 40px;
  
  /* 关键：让卡片也是 Flex 布局，保证内部元素分布 */
  display: flex; 
  flex-direction: column;
  
  /* 确保卡片高度自动拉伸，左右卡片等高 */
  height: auto; 
}

/* 左侧卡片 */
.main-card {
  flex: 2;
  justify-content: space-between;
}

/* 右侧卡片 */
.side-card {
  flex: 1;
  min-width: 320px;
  gap: 24px;
  /* 删掉 justify-content: center，让内容自然排列 */
}

/* =========================================
   4. 内部元素 (保持不变)
   ========================================= */
.card-header { margin-bottom: 20px; }
.title-section h1 { margin: 0; font-size: 36px; font-weight: 800; letter-spacing: -1px; color: #0f172a; }
.subtitle { color: #64748B; margin-top: 8px; font-size: 14px; }

.status-tag {
  display: inline-flex; align-items: center; gap: 8px; margin-top: 10px;
  padding: 6px 14px; border-radius: 20px; background: #F1F5F9;
  font-size: 13px; font-weight: 600; color: #64748B;
}
.status-tag.active { background: #DCFCE7; color: #166534; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: currentColor; }

.dial-area { flex: 1; display: flex; align-items: center; justify-content: center; position: relative; min-height: 360px; /* 防止高度塌陷 */ }
.dial-ring {
  width: 340px; height: 340px; border-radius: 50%;
  position: relative; display: flex; align-items: center; justify-content: center;
  background: #F8FAFC;
  box-shadow: 20px 20px 60px rgba(0,0,0,0.03), inset 0 0 0 1px rgba(0,0,0,0.02);
  transition: all 0.5s;
}
.dial-ring.is-off { filter: grayscale(100%); opacity: 0.6; }

.dial-content { text-align: center; z-index: 2; }
.temp-big { font-size: 96px; font-weight: 800; color: #334155; line-height: 1; letter-spacing: -4px; }
.temp-big .unit { font-size: 28px; color: #94A3B8; vertical-align: top; margin-top: 12px; display: inline-block; }
.mode-label { font-size: 18px; color: #64748B; margin-top: 10px; font-weight: 600; }

.dial-svg { position: absolute; inset: 0; width: 100%; height: 100%; transform: rotate(-90deg); pointer-events: none; }
.bg-ring { fill: none; stroke: #E2E8F0; stroke-width: 12; stroke-linecap: round; }
.progress-ring { fill: none; stroke: #6366F1; stroke-width: 12; stroke-linecap: round; transition: stroke-dasharray 0.5s ease; }

.controls-row {
  display: flex; align-items: center; gap: 30px;
  background: #F8FAFC; 
  padding: 24px; border-radius: 24px;
  margin-top: auto; /* 确保它沉底 */
}
.controls-row.disabled { opacity: 0.5; pointer-events: none; }
.control-cell { display: flex; flex-direction: column; gap: 12px; }
.flex-2 { flex: 2; } .flex-1 { flex: 1; }
.control-cell label { font-size: 14px; font-weight: 600; color: #64748B; display: flex; gap: 8px; align-items: center; }

.slider-container { display: flex; align-items: center; gap: 15px; color: #94A3B8; font-weight: 600; font-size: 15px; }
input[type=range] { flex: 1; -webkit-appearance: none; height: 6px; background: #E2E8F0; border-radius: 3px; cursor: pointer; }
input[type=range]::-webkit-slider-thumb {
  -webkit-appearance: none; width: 24px; height: 24px; background: #6366F1; border-radius: 50%;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4); border: 3px solid #fff; cursor: pointer; transition: transform 0.1s;
}
input[type=range]::-webkit-slider-thumb:hover { transform: scale(1.1); }
.divider { width: 1px; height: 50px; background: #E2E8F0; }

.fan-selector { display: flex; background: #E2E8F0; padding: 5px; border-radius: 14px; }
.fan-opt {
  flex: 1; text-align: center; padding: 10px; font-size: 14px; color: #64748B; border-radius: 10px; cursor: pointer; transition: 0.2s; font-weight: 500;
}
.fan-opt.active { background: #fff; color: #6366F1; font-weight: 700; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }

/* 右侧元素 */
.power-wrapper { text-align: center; margin-bottom: 20px; }
.power-btn {
  width: 100px; height: 100px; border-radius: 50%; border: none; margin: 0 auto 15px;
  background: #fff; box-shadow: 0 10px 30px rgba(0,0,0,0.05); border: 1px solid #f1f5f9;
  font-size: 40px; color: #94A3B8; cursor: pointer; transition: 0.3s;
  display: flex; align-items: center; justify-content: center;
}
.power-btn:hover { transform: scale(1.05); border-color: #6366F1; color: #6366F1; }
.power-btn.active { 
  background: linear-gradient(135deg, #6366F1, #818CF8); 
  color: #fff; border: none;
  box-shadow: 0 15px 40px rgba(99, 102, 241, 0.3); 
}
.power-wrapper span { font-size: 15px; color: #64748B; font-weight: 500; }

.info-list { display: flex; flex-direction: column; gap: 20px; width: 100%; flex: 1; /* 让列表占据中间空间 */ }
.info-row {
  display: flex; align-items: center; gap: 20px; padding: 20px;
  background: #F8FAFC; border-radius: 20px; 
  transition: transform 0.2s;
}
.info-row:hover { transform: translateX(5px); background: #f1f5f9; }

.icon-square { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 22px; }
.blue { background: #E0F2FE; color: #0EA5E9; }
.purple { background: #F3E8FF; color: #A855F7; }
.green { background: #DCFCE7; color: #22C55E; }
.info-detail { display: flex; flex-direction: column; }
.info-detail .label { font-size: 13px; color: #64748B; margin-bottom: 2px; }
.info-detail .val { font-size: 20px; font-weight: 700; color: #1E293B; }

.eco-card {
  margin-top: auto; /* 关键：强制推到最底部 */
  background: #ECFDF5; color: #065F46;
  padding: 20px; border-radius: 20px; display: flex; align-items: center; gap: 16px;
}
.eco-card i { font-size: 28px; }
.eco-card strong { font-size: 15px; display: block; margin-bottom: 4px; }
.eco-card p { margin: 0; font-size: 13px; opacity: 0.9; }

/* 居中表单 */
.center-layout { display: flex; align-items: center; justify-content: center; height: 100%; }
.form-card { 
  width: 500px; text-align: center; 
  background: #fff; box-shadow: 0 20px 50px rgba(0,0,0,0.05);
  border-radius: 30px; padding: 40px;
} 
.status-icon { width: 70px; height: 70px; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; font-size: 32px; }
.primary { background: #EEF2FF; color: #6366F1; }
.warning { background: #FFFBEB; color: #F59E0B; }
.desc { color: #64748B; margin-bottom: 30px; font-size: 15px; }
.form-body { text-align: left; display: flex; flex-direction: column; gap: 20px; margin-bottom: 30px; }
.input-box label { display: block; font-size: 14px; font-weight: 600; color: #475569; margin-bottom: 8px; }
.input-box input { width: 100%; padding: 14px; border: 1px solid #E2E8F0; background: #F8FAFC; border-radius: 12px; box-sizing: border-box; outline: none; transition: 0.2s; }
.input-box input:focus { background: #fff; border-color: #6366F1; box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1); }
.submit-btn { width: 100%; padding: 16px; background: #6366F1; color: white; border: none; border-radius: 14px; font-size: 16px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; transition: 0.2s; }
.submit-btn:hover:not(:disabled) { background: #4F46E5; box-shadow: 0 8px 16px rgba(99, 102, 241, 0.3); transform: translateY(-2px); }
.submit-btn:disabled { background: #CBD5E1; cursor: not-allowed; }

.fade-in { animation: fadeIn 0.5s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>