import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import './assets/style.css'

// 1. 注意这里不要加花括号 {}，且路径要对
import router from './router' 

const app = createApp(App)

app.use(createPinia())

// 2. 这里做一个防御性检查，方便调试
if (router) {
    app.use(router)
} else {
    console.error('路由实例加载失败！请检查 router/index.js 是否有 export default')
}

app.mount('#app')