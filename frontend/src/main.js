import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import axios from 'axios'
import './assets/tailwind.css'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 配置axios
axios.defaults.baseURL = 'http://localhost:8000'

// 配置axios拦截器
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

axios.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

const app = createApp(App)
app.use(router)
app.use(createPinia())
app.config.globalProperties.$axios = axios
app.use(ElementPlus)
app.mount('#app')