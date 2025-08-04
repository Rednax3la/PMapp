// Frontend/website/src/services/auth.js

import api from './api'

export const authService = {
  async login(username, password) {
    try {
      const response = await api.post('/login', {
        username,
        password
      })
      
      const { access_token, username: returnedUsername, company_name, role } = response.data
      
      // Create complete user data object
      const userData = {
        username: returnedUsername || username,
        company_name: company_name,
        role: role
      }
      
      // Store token and user data
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('user_data', JSON.stringify(userData))
      
      console.log('Login successful, stored user data:', userData) // Debug log
      
      return { ...response.data, user: userData }
    } catch (error) {
      console.error('Login error:', error)
      
      // Handle different types of errors
      if (error.response) {
        // Server responded with error status
        const status = error.response.status
        const data = error.response.data
        
        switch (status) {
          case 401:
            throw 'Invalid username or password'
          case 422:
            throw 'Missing required fields'
          case 500:
            throw 'Server error. Please try again later.'
          default:
            throw data?.message || `Login failed (${status})`
        }
      } else if (error.request) {
        // Request was made but no response received
        throw 'Unable to connect to server. Please check your connection.'
      } else {
        // Something else happened
        throw 'An unexpected error occurred'
      }
    }
  },

  async register(userData) {
    try {
      const response = await api.post('/register', userData)
      return response.data
    } catch (error) {
      console.error('Registration error:', error)
      
      if (error.response) {
        const status = error.response.status
        const data = error.response.data
        
        switch (status) {
          case 409:
            throw 'Username already exists. Please choose another.'
          case 422:
            throw 'Please fill in all required fields correctly'
          case 400:
            throw data?.message || 'Invalid registration data'
          case 500:
            throw 'Server error. Please try again later.'
          default:
            throw data?.message || `Registration failed (${status})`
        }
      } else if (error.request) {
        throw 'Unable to connect to server. Please check your connection.'
      } else {
        throw 'An unexpected error occurred during registration'
      }
    }
  },

  logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_data')
    
    // Optionally clear any other stored data
    localStorage.removeItem('app_preferences')
    
    // Redirect to auth page
    window.location.href = '/auth'
  },

  // Add method to decode JWT and extract claims
  decodeJWTClaims(token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      return {
        username: payload.sub || payload.identity,
        company_name: payload.company_name,
        role: payload.role,
        exp: payload.exp
      }
    } catch (error) {
      console.error('Failed to decode JWT:', error)
      return null
    }
  },

  getCurrentUser() {
    try {
      // First try localStorage
      const userStr = localStorage.getItem('user_data')
      if (userStr) {
        const userData = JSON.parse(userStr)
        // Verify userData has required fields
        if (userData.username && userData.company_name) {
          return userData
        }
      }
      
      // Fallback: decode from JWT
      const token = localStorage.getItem('access_token')
      if (token) {
        const claims = this.decodeJWTClaims(token)
        if (claims && claims.company_name) {
          // Update localStorage with decoded claims
          localStorage.setItem('user_data', JSON.stringify(claims))
          console.log('Restored user data from JWT:', claims) // Debug log
          return claims
        }
      }
      
      return null
    } catch (error) {
      console.error('Error getting current user:', error)
      this.logout() // Clear invalid data
      return null
    }
  },

  isAuthenticated() {
    const token = localStorage.getItem('access_token')
    const userData = this.getCurrentUser()
    
    // Check if both token and user data exist
    if (!token || !userData) {
      return false
    }
    
    try {
      // Basic JWT token validation (check if it's not expired)
      const payload = JSON.parse(atob(token.split('.')[1]))
      const currentTime = Date.now() / 1000
      
      if (payload.exp && payload.exp < currentTime) {
        // Token is expired
        this.logout()
        return false
      }
      
      return true
    } catch (error) {
      // Invalid token format
      console.error('Invalid token format:', error)
      this.logout()
      return false
    }
  },

  getAuthHeaders() {
    const token = localStorage.getItem('access_token')
    return token ? { Authorization: `Bearer ${token}` } : {}
  },

  // Method to refresh token if your backend supports it
  async refreshToken() {
    try {
      const response = await api.post('/refresh')
      const { access_token } = response.data
      
      localStorage.setItem('access_token', access_token)
      return access_token
    } catch (error) {
      console.error('Token refresh failed:', error)
      this.logout()
      throw error
    }
  }
}