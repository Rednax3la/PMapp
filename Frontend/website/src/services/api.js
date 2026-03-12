import axios from 'axios'

const api = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:5001',
  withCredentials: true, // required for HTTP-only cookie auth
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Response interceptor — handle auth errors and subscription limit errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear any stored auth metadata and send to auth page
      localStorage.removeItem('user_data')
      localStorage.removeItem('subscription_tier')
      window.location.href = '/auth'
    }
    // 402 (subscription limit) is handled per-component via SubscriptionBanner
    return Promise.reject(error)
  }
)

export default api
