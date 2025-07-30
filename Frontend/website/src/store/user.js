// src/stores/user.js - Pinia store for user management

import { defineStore } from 'pinia'
import { authService } from '@/services/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    loading: false,
    error: null
  }),

  getters: {
    currentUser: (state) => state.user,
    userRole: (state) => state.user?.role || null,
    companyName: (state) => state.user?.company_name || null,
    isAdmin: (state) => state.user?.role === 'admin',
    isManager: (state) => ['admin', 'manager'].includes(state.user?.role),
  },

  actions: {
    // Initialize user state from localStorage
    initializeAuth() {
      try {
        const token = localStorage.getItem('access_token')
        const userData = JSON.parse(localStorage.getItem('user_data') || 'null')
        if (token && userData) {
          this.user = userData
          this.isAuthenticated = true
        } else {
          this.clearAuth()
        }
      } catch (error) {
        console.error('Error initializing auth:', error)
        this.clearAuth()
      }
    },

    // Login action
    async login(username, password) {
      this.loading = true
      this.error = null

      try {
        const response = await authService.login(username, password)

        // Update store state
        this.user = {
          username: username,
          company_name: response.company_name,
          role: response.role
        }
        this.isAuthenticated = true

        // Persist to localStorage
        localStorage.setItem('access_token', response.access_token)
        localStorage.setItem('user_data', JSON.stringify(this.user))

        return response
      } catch (error) {
        this.error = error
        this.clearAuth()
        throw error
      } finally {
        this.loading = false
      }
    },

    // Logout action
    logout() {
      authService.logout()
      this.clearAuth()
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_data')
    },

    // Clear authentication state
    clearAuth() {
      this.user = null
      this.isAuthenticated = false
      this.error = null
    },

    // Update user data
    updateUser(userData) {
      if (this.user) {
        this.user = { ...this.user, ...userData }
        localStorage.setItem('user_data', JSON.stringify(this.user))
      }
    },

    // Clear error
    clearError() {
      this.error = null
    }
  }
})

