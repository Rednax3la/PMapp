// Frontend/website/src/services/api.js
import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:5001',
  withCredentials: true,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_data')
      // Redirect to login
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api