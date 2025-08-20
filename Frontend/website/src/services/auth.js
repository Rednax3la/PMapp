// Frontend/website/src/services/auth.js
import api from './api'

export const authService = {
  // Login: server sets HttpOnly cookie; we persist user metadata from /login response.
  async login(username, password) {
    try {
      const resp = await api.post('/login', { username, password })
      const data = resp.data || {}
      const userData = {
        username: data.username || username,
        company_name: data.company_name || null,
        role: data.role || null,
      }
      localStorage.setItem('user_data', JSON.stringify(userData))
      console.log('Login successful, stored user data:', userData)
      return userData
    } catch (error) {
      console.error('Login error:', error)
      if (error.response) {
        const status = error.response.status
        switch (status) {
          case 401: throw 'Invalid username or password'
          case 422: throw 'Missing required fields'
          case 500: throw 'Server error. Please try again later.'
          default: throw error.response.data?.message || `Login failed (${status})`
        }
      } else if (error.request) {
        throw 'Unable to connect to server. Please check your connection.'
      } else {
        throw 'An unexpected error occurred'
      }
    }
  },

  // Register then (optionally) auto-login to set cookies
  async register(userData) {
    try {
      const response = await api.post('/register', userData)
      try {
        await this.login(userData.username, userData.password)
      } catch (e) {
        console.warn('Auto-login after registration failed:', e)
      }
      return response.data
    } catch (error) {
      console.error('Registration error:', error)
      if (error.response) {
        const status = error.response.status
        const data = error.response.data
        switch (status) {
          case 409: throw 'Username already exists. Please choose another.'
          case 422: throw 'Please fill in all required fields correctly'
          case 400: throw data?.message || 'Invalid registration data'
          case 500: throw 'Server error. Please try again later.'
          default: throw data?.message || `Registration failed (${status})`
        }
      } else if (error.request) {
        throw 'Unable to connect to server. Please check your connection.'
      } else {
        throw 'An unexpected error occurred during registration'
      }
    }
  },

  async logout() {
    try {
      await api.post('/logout')
    } catch (e) {
      console.warn('Server logout failed (continuing to clear local state):', e)
    }
    localStorage.removeItem('user_data')
    localStorage.removeItem('app_preferences')
    window.location.href = '/auth'
  },

  // ⬇️ Synchronous again; no /whoami call
  getCurrentUser() {
    try {
      const s = localStorage.getItem('user_data')
      if (!s) return null
      const u = JSON.parse(s)
      if (u && u.username && u.company_name) return u
      return null
    } catch {
      return null
    }
  },

  isAuthenticated() {
    return Boolean(localStorage.getItem('user_data'))
  },

  getAuthHeaders() {
    return {}
  },

  // Optional: if you don’t have a /refresh endpoint, either remove this or keep it as a no-op
  async refreshToken() {
    // No refresh endpoint in backend; just return cached user
    return this.getCurrentUser()
  }
}
