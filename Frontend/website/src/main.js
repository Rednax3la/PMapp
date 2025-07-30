// src/main.js - Updated main file

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import './assets/css/main.css'

// Import stores
import { useUserStore } from './store/user'

const app = createApp(App)
const pinia = createPinia()

// Use plugins
app.use(pinia)
app.use(router)
app.use(ElementPlus)

// Register Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// Initialize authentication state
const userStore = useUserStore()
userStore.initializeAuth()

// Add global properties for easy access
app.config.globalProperties.$user = userStore

// Mount the app
app.mount('#app')