import api from './api'

export const subscriptionService = {
  async getSubscription() {
    const res = await api.get('/stripe/subscription')
    return res.data
  },

  async createCheckoutSession(tier) {
    const res = await api.post('/stripe/create-checkout-session', { tier })
    return res.data
  },

  async createPortalSession() {
    const res = await api.post('/stripe/create-portal-session')
    return res.data
  }
}
