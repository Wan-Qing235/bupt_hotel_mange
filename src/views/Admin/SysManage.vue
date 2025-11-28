<template>
  <div>
    <h2 class="section-title"><i class="fas fa-cogs"></i> 系统参数设置</h2>
    
    <div class="form-container">
      <div class="card">
        <div class="form-group">
          <label class="form-label">工作模式</label>
          <select v-model="localConfig.mode" class="form-control">
            <option value="cool">制冷模式 (夏季)</option>
            <option value="heat">制热模式 (冬季)</option>
          </select>
        </div>

        <div class="form-group">
          <label class="form-label">最大同时服务房间数 (y)</label>
          <input type="number" v-model.number="localConfig.maxServices" class="form-control">
        </div>

        <div class="form-group">
          <label class="form-label">时间片调度长度 (S 秒)</label>
          <input type="number" v-model.number="localConfig.timeSlice" class="form-control">
          <small style="color: #666">当等待队列中有同级请求等待超过 S 秒时，触发轮转。</small>
        </div>

        <div class="form-group">
          <label class="form-label">计费倍率</label>
          <input type="number" v-model.number="localConfig.baseRate" step="0.1" class="form-control">
        </div>

        <button class="btn" @click="saveSettings">
          <i class="fas fa-save"></i> 保存全局设置
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useHotelStore } from '@/store/modules/hotel'

const hotelStore = useHotelStore()
const localConfig = ref({ ...hotelStore.config })

// 同步 Store 的配置
watch(() => hotelStore.config, (newVal) => {
  if (newVal) localConfig.value = { ...newVal }
}, { deep: true, immediate: true })

const saveSettings = () => {
  hotelStore.updateSystemSettings(localConfig.value)
  alert('系统设置已下发到服务器！')
}
</script>

<style scoped>
.form-label { display: block; margin-bottom: 8px; font-weight: 600; }
</style>