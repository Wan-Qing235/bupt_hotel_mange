import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { io } from 'socket.io-client'
import { useAuthStore } from './auth'

export const useHotelStore = defineStore('hotel', () => {
  const rooms = ref([])
  const config = ref({})
  // [新增] 全局统计数据
  const stats = ref({ today_checkins: 0, total_income: 0, total_energy: 0 })
  
  // 请确保这里改成你的局域网 IP，方便多端测试
  const socket = io('http://localhost:5000') 

  socket.on('sync_data', (data) => {
    if (data.rooms) rooms.value = data.rooms
    if (data.config) config.value = data.config
    // [新增] 同步统计数据
    if (data.stats) stats.value = data.stats
  })

  // Getters
  const getRoomById = (id) => rooms.value.find(r => r.id === String(id)) || rooms.value.find(r => r.id == id)
  
  const currentUserRoom = computed(() => {
    const authStore = useAuthStore()
    if (authStore.userRole === 'resident' && authStore.roomId) {
      return getRoomById(authStore.roomId)
    }
    return null
  })

  const freeRooms = computed(() => rooms.value.filter(r => r.status === 'free'))
  const occupiedRooms = computed(() => rooms.value.filter(r => r.status === 'occupied'))
  const pendingCheckoutRooms = computed(() => rooms.value.filter(r => r.status === 'occupied' && r.checkout_pending))

  // Actions
  function sendAction(roomId, action, value) {
    socket.emit('client_action', { roomId, action, value })
  }

  // [新增] 管理员：更新系统设置
  function updateSystemSettings(newConfig) {
    // 不传 roomId，直接传 action 和 value
    socket.emit('client_action', { action: 'update_settings', value: newConfig })
  }

  function submitCheckInRequest(roomId, guestInfo) {
    sendAction(roomId, 'submit_checkin', guestInfo)
  }

  function approveCheckIn(roomId) {
    sendAction(roomId, 'approve_checkin', true)
  }

  function requestCheckout(roomId) {
    sendAction(roomId, 'request_checkout', true)
  }

  function confirmCheckout(roomId) {
    const room = getRoomById(roomId)
    const bill = {
      roomId: room.id,
      guest: room.guest?.name,
      acCost: room.currentCost,
      roomCost: 100.00,
      totalCost: room.currentCost + 100.00,
      checkIn: room.guest?.checkInTime,
      checkOut: new Date()
    }
    sendAction(roomId, 'confirm_checkout', true)
    return bill
  }

  function togglePower(roomId) {
    const room = getRoomById(roomId)
    if(room) sendAction(roomId, 'power', !room.isOn)
  }

  function updateRoomState(roomId, newState) {
    if (newState.target !== undefined) sendAction(roomId, 'temp', newState.target)
    if (newState.speed !== undefined) sendAction(roomId, 'speed', newState.speed)
  }

  return { 
    rooms, config, stats, currentUserRoom, 
    freeRooms, occupiedRooms, pendingCheckoutRooms,
    submitCheckInRequest, approveCheckIn,
    requestCheckout, confirmCheckout,
    togglePower, updateRoomState, updateSystemSettings,
    getRoomById
  }
})