<template>
  <div class="settings-page">
    <div class="page-container">
      
      <div class="header-section">
        <div class="header-title">
          <h1><i class="ph-duotone ph-gear-six"></i> 系统参数配置</h1>
        </div>
        <p class="subtitle">Global Configuration & Dispatch Strategy</p>
      </div>

      <div class="settings-card">
        
        <span class="section-label">Operation Mode / 工作模式</span>
        <div class="mode-grid">
          <div 
            class="mode-option cool" 
            :class="{ active: localConfig.mode === 'cool' }"
            @click="localConfig.mode = 'cool'"
          >
            <div class="mode-icon"><i class="ph-fill ph-snowflake"></i></div>
            <div class="mode-text">
              <h3>制冷模式 (Cool)</h3>
              <p>适用于夏季，空调提供冷风服务</p>
            </div>
            <i class="ph-bold ph-check-circle check-mark"></i>
          </div>

          <div 
            class="mode-option heat" 
            :class="{ active: localConfig.mode === 'heat' }"
            @click="localConfig.mode = 'heat'"
          >
            <div class="mode-icon"><i class="ph-fill ph-fire"></i></div>
            <div class="mode-text">
              <h3>制热模式 (Heat)</h3>
              <p>适用于冬季，空调提供暖风服务</p>
            </div>
            <i class="ph-bold ph-check-circle check-mark"></i>
          </div>
        </div>

        <span class="section-label">Dispatch Parameters / 调度参数</span>
        <div class="params-grid">
          
          <div class="form-group">
            <label class="form-label">最大并发数 (Max Services)</label>
            <div class="input-wrapper">
              <i class="ph-bold ph-users-three input-icon"></i>
              <input 
                type="number" 
                v-model.number="localConfig.maxServices" 
                class="form-input" 
                min="1" max="10"
              >
              <span class="input-suffix">台 (Rooms)</span>
            </div>
            <p class="helper-text">系统允许同时运行空调的最大房间数量，超过将进入等待队列。</p>
          </div>

          <div class="form-group">
            <label class="form-label">时间片长度 (Time Slice)</label>
            <div class="input-wrapper">
              <i class="ph-bold ph-timer input-icon"></i>
              <input 
                type="number" 
                v-model.number="localConfig.timeSlice" 
                class="form-input" 
                step="10"
              >
              <span class="input-suffix">秒 (Seconds)</span>
            </div>
            <p class="helper-text">当等待队列中有同级请求时，服务中房间运行超过此时长将触发轮转。</p>
          </div>

          <div class="form-group full-width">
            <label class="form-label">基础计费倍率 (Base Fee Rate)</label>
            <div class="input-wrapper">
              <i class="ph-bold ph-currency-yen input-icon"></i>
              <input 
                type="number" 
                v-model.number="localConfig.baseRate" 
                class="form-input" 
                step="0.1"
              >
              <span class="input-suffix">x 倍 (Multiplier)</span>
            </div>
            <p class="helper-text">调整全局计费标准。例如设置为 1.5，则所有费用计算增加 50%。</p>
          </div>

        </div>

        <div class="footer-actions">
          <div class="alert-box">
            <i class="ph-fill ph-warning-circle"></i>
            <span>注意：修改参数将即时影响当前调度策略。</span>
          </div>
          <button class="save-btn" @click="saveSettings">
            <i class="ph-bold ph-floppy-disk"></i>
            保存全局配置
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useHotelStore } from '@/store/modules/hotel'

const hotelStore = useHotelStore()
// 初始化本地配置副本，避免直接修改 Store
const localConfig = ref({ ...hotelStore.config })

// 监听 Store 变化，保持同步 (例如后端推送了新配置)
watch(() => hotelStore.config, (newVal) => {
  if (newVal) localConfig.value = { ...newVal }
}, { deep: true, immediate: true })

const saveSettings = () => {
  if (confirm('确认要更新系统全局参数吗？这可能会影响当前运行的空调。')) {
    hotelStore.updateSystemSettings(localConfig.value)
    // 简单的视觉反馈，也可以换成 Toast
    // alert('系统设置已下发到服务器！') 
  }
}
</script>

<style scoped>
/* ========================
   全局容器
   ======================== */
.settings-page {
  background-color: #F8FAFC; 
  min-height: 100vh;
  padding: 40px;
  font-family: 'Inter', -apple-system, sans-serif;
  color: #1E293B;
  display: flex; justify-content: center;
}

.page-container {
  width: 100%;
  max-width: 900px;
  animation: fadeIn 0.6s ease-out;
}

/* 1. Header */
.header-section { margin-bottom: 30px; text-align: center; }
.header-title h1 {
  font-size: 28px; font-weight: 800; color: #1E293B;
  display: flex; align-items: center; justify-content: center; gap: 12px; margin: 0;
}
.subtitle { color: #64748B; margin-top: 8px; font-size: 14px; }

/* 2. 设置卡片 */
.settings-card {
  background: #FFFFFF; border-radius: 24px;
  box-shadow: 0 10px 40px -10px rgba(0,0,0,0.05);
  border: 1px solid #E2E8F0; padding: 40px;
}

.section-label {
  font-size: 14px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 1px;
  margin-bottom: 16px; display: block;
}

/* A. 模式选择 */
.mode-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 40px;
}

.mode-option {
  border: 2px solid #E2E8F0; border-radius: 16px; padding: 20px;
  cursor: pointer; transition: all 0.2s;
  display: flex; align-items: center; gap: 16px; position: relative; overflow: hidden;
}
.mode-option:hover { border-color: #CBD5E1; }

/* 选中状态 */
.mode-option.cool.active {
  border-color: #3B82F6; background: #EFF6FF;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}
.mode-option.heat.active {
  border-color: #F97316; background: #FFF7ED;
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.2);
}

.mode-icon {
  width: 48px; height: 48px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center; font-size: 24px;
  background: white; border: 1px solid #E2E8F0; transition: 0.2s;
}
.mode-option.cool.active .mode-icon { color: #3B82F6; border-color: #3B82F6; }
.mode-option.heat.active .mode-icon { color: #F97316; border-color: #F97316; }

.mode-text h3 { font-size: 16px; margin: 0 0 4px 0; font-weight: 700; }
.mode-text p { font-size: 12px; color: #64748B; margin: 0; }

.check-mark {
  position: absolute; top: 12px; right: 12px; font-size: 20px; opacity: 0; transform: scale(0.5); transition: 0.2s;
}
.mode-option.active .check-mark { opacity: 1; transform: scale(1); }
.mode-option.cool.active .check-mark { color: #3B82F6; }
.mode-option.heat.active .check-mark { color: #F97316; }

/* B. 参数表单 */
.params-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 30px;
}
.full-width { grid-column: 1 / -1; }

.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-label { font-size: 14px; font-weight: 600; color: #1E293B; }

.input-wrapper { position: relative; display: flex; align-items: center; }
.input-icon { position: absolute; left: 16px; color: #64748B; font-size: 20px; pointer-events: none; }

.form-input {
  width: 100%; padding: 14px 16px 14px 48px;
  border: 1px solid #E2E8F0; border-radius: 12px; background: #F8FAFC;
  font-size: 15px; font-weight: 600; color: #1E293B; transition: 0.2s; outline: none;
}
.form-input:focus { background: white; border-color: #6366F1; box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1); }

.input-suffix {
  position: absolute; right: 16px; color: #64748B; font-size: 13px; font-weight: 500; pointer-events: none;
}
.helper-text { font-size: 12px; color: #64748B; line-height: 1.4; margin-top: 4px; }

/* C. 底部操作 */
.footer-actions {
  border-top: 1px solid #E2E8F0; padding-top: 30px;
  display: flex; align-items: center; justify-content: space-between;
}

.alert-box {
  background: #FFFBEB; border: 1px solid #FEF3C7; color: #B45309;
  padding: 10px 16px; border-radius: 10px; font-size: 13px;
  display: flex; align-items: center; gap: 8px;
}

.save-btn {
  background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
  color: white; border: none; padding: 14px 32px; border-radius: 12px;
  font-size: 15px; font-weight: 600; cursor: pointer;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3); transition: 0.2s;
  display: flex; align-items: center; gap: 8px;
}
.save-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4); }
.save-btn:active { transform: scale(0.98); }

@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>