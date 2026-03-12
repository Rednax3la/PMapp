import { defineStore } from 'pinia'
import { authService } from '@/services/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    subscriptionTier: 'free',
    loading: false,
    error: null
  }),

  getters: {
    currentUser: (state) => state.user,
    userRole: (state) => state.user?.role || null,
    companyName: (state) => state.user?.company_name || null,
    isAdmin: (state) => state.user?.role === 'admin',
    isManager: (state) => ['admin', 'manager'].includes(state.user?.role),
    isMember: (state) => state.user?.role === 'member',
    isFree: (state) => state.subscriptionTier === 'free',
    isPro: (state) => state.subscriptionTier === 'pro',
    isEnterprise: (state) => state.subscriptionTier === 'enterprise',
  },

  actions: {
    initializeAuth() {
      try {
        const userData = JSON.parse(localStorage.getItem('user_data') || 'null')
        const tier = localStorage.getItem('subscription_tier') || 'free'

        if (userData && userData.username && userData.company_name) {
          this.user = userData
          this.isAuthenticated = true
          this.subscriptionTier = tier
        } else {
          const restoredUser = authService.getCurrentUser()
          if (restoredUser && restoredUser.company_name) {
            this.user = restoredUser
            this.isAuthenticated = true
            this.subscriptionTier = restoredUser.subscription_tier || tier
          } else {
            this.clearAuth()
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error)
        this.clearAuth()
      }
    },

    async login(username, password) {
      this.loading = true
      this.error = null

      try {
        const response = await authService.login(username, password)

        this.user = {
          username: response.username || username,
          company_name: response.company_name,
          role: response.role
        }
        this.isAuthenticated = true
        this.subscriptionTier = response.subscription_tier || 'free'

        localStorage.setItem('subscription_tier', this.subscriptionTier)

        return response
      } catch (error) {
        this.error = error
        this.clearAuth()
        throw error
      } finally {
        this.loading = false
      }
    },

    async logout() {
      await authService.logout()
      this.clearAuth()
      localStorage.removeItem('user_data')
      localStorage.removeItem('subscription_tier')
    },

    clearAuth() {
      this.user = null
      this.isAuthenticated = false
      this.subscriptionTier = 'free'
      this.error = null
    },

    updateUser(userData) {
      if (this.user) {
        this.user = { ...this.user, ...userData }
        localStorage.setItem('user_data', JSON.stringify(this.user))
      }
    },

    async refreshSubscription() {
      try {
        const { subscriptionService } = await import('@/services/subscription')
        const data = await subscriptionService.getSubscription()
        this.subscriptionTier = data.tier || 'free'
        localStorage.setItem('subscription_tier', this.subscriptionTier)
        return data
      } catch (e) {
        console.warn('Could not refresh subscription:', e)
      }
    },

    clearError() {
      this.error = null
    }
  }
})
