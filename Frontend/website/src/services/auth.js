import api from './api'

export const authService = {
  async login(username, password) {
    try {
      const response = await api.post('/login', {
        username,
        password
      })
      
      const { access_token, company_name, role } = response.data
      
      // Store token and user data
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('user_data', JSON.stringify({
        username,
        company_name,
        role
      }))
      
      return response.data
    } catch (error) {
      throw error.response?.data?.message || 'Login failed'
    }
  },

  async register(userData) {
    try {
      const response = await api.post('/register', userData)
      return response.data
    } catch (error) {
      throw error.response?.data?.message || 'Registration failed'
    }
  },

  logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_data')
  },

  getCurrentUser() {
    const userStr = localStorage.getItem('user_data')
    return userStr ? JSON.parse(userStr) : null
  },

  isAuthenticated() {
    return !!localStorage.getItem('access_token')
  }
}