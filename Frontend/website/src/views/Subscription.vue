<template>
  <div class="app-layout" :class="{ 'light-mode': !isDarkMode }">
    <Sidebar :isDarkMode="isDarkMode" />

    <div class="main-content">
      <AppHeader title="Subscription">
        <template #actions>
          <ThemeToggle :isDarkMode="isDarkMode" @toggle="toggleTheme" />
        </template>
      </AppHeader>

      <div class="sub-page">

        <!-- Success / Cancelled banners -->
        <transition name="slide-down">
          <div v-if="successBanner" class="alert alert-success">
            <i class="fas fa-check-circle"></i>
            Subscription upgraded successfully! Your plan is now <strong>{{ currentTier }}</strong>.
            <button @click="successBanner = false" class="alert-close"><i class="fas fa-times"></i></button>
          </div>
        </transition>
        <transition name="slide-down">
          <div v-if="cancelledBanner" class="alert alert-warning">
            <i class="fas fa-exclamation-circle"></i>
            Checkout was cancelled. No changes were made.
            <button @click="cancelledBanner = false" class="alert-close"><i class="fas fa-times"></i></button>
          </div>
        </transition>

        <!-- Current plan summary -->
        <div v-if="subData" class="current-plan-bar glass-card fade-in">
          <div class="plan-summary">
            <span class="plan-tier-label" :class="currentTier">
              <i :class="tierIcon(currentTier)"></i>
              {{ tierDisplayName(currentTier) }}
            </span>
            <span class="plan-status" :class="subData.status">{{ subData.status }}</span>
          </div>
          <div class="plan-usage">
            <span>Projects: <strong>{{ subData.usage?.projects }}</strong>
              <template v-if="subData.limits?.projects"> / {{ subData.limits.projects }}</template>
            </span>
            <span>Members: <strong>{{ subData.usage?.members }}</strong>
              <template v-if="subData.limits?.members"> / {{ subData.limits.members }}</template>
            </span>
            <span v-if="subData.current_period_end">
              Renews: <strong>{{ formatDate(subData.current_period_end) }}</strong>
            </span>
          </div>
          <button
            v-if="currentTier !== 'free'"
            class="portal-btn"
            @click="managePortal"
            :disabled="portalLoading"
          >
            <i class="fas fa-cog"></i>
            {{ portalLoading ? 'Opening...' : 'Manage Billing' }}
          </button>
        </div>

        <!-- Pricing Cards -->
        <h2 class="pricing-title">Choose your plan</h2>

        <div class="pricing-grid">
          <div
            v-for="plan in plans"
            :key="plan.id"
            class="pricing-card glass-card"
            :class="{ 'current-plan': currentTier === plan.id, 'popular': plan.popular }"
          >
            <div v-if="plan.popular" class="popular-badge">Most Popular</div>

            <div class="plan-header">
              <div class="plan-icon"><i :class="tierIcon(plan.id)"></i></div>
              <h3 class="plan-name">{{ plan.name }}</h3>
              <div class="plan-price">
                <span class="price-amount">${{ plan.price }}</span>
                <span class="price-period">{{ plan.period }}</span>
              </div>
              <div v-if="plan.id !== 'free'" class="price-kes">
                KES {{ plan.priceKes.toLocaleString() }}{{ plan.period }}
              </div>
            </div>

            <ul class="plan-features">
              <li v-for="feat in plan.features" :key="feat">
                <i class="fas fa-check feature-check"></i>
                {{ feat }}
              </li>
            </ul>

            <template v-if="currentTier === plan.id">
              <button class="plan-cta cta-current" disabled>Current Plan</button>
            </template>
            <template v-else-if="plan.id === 'free'">
              <button class="plan-cta cta-downgrade" @click="managePortal">Downgrade via Billing Portal</button>
            </template>
            <template v-else>
              <!-- Two payment buttons for paid plans -->
              <div class="payment-btns">
                <button
                  class="plan-cta cta-upgrade"
                  :disabled="checkoutLoading === plan.id + '_stripe'"
                  @click="selectPlanStripe(plan)"
                >
                  <i v-if="checkoutLoading === plan.id + '_stripe'" class="fas fa-spinner fa-spin"></i>
                  <template v-else><i class="fas fa-credit-card"></i> Card / Google Pay</template>
                </button>
                <button
                  class="plan-cta cta-mpesa"
                  :disabled="checkoutLoading === plan.id + '_mpesa'"
                  @click="openMpesaModal(plan)"
                >
                  <i v-if="checkoutLoading === plan.id + '_mpesa'" class="fas fa-spinner fa-spin"></i>
                  <template v-else><i class="fas fa-mobile-alt"></i> Pay via M-Pesa</template>
                </button>
              </div>
            </template>
          </div>
        </div>

        <!-- Payment methods note -->
        <div class="payment-methods-row">
          <div class="pm-item">
            <img src="https://pay.google.com/about/static/images/logos/google_pay_logo.svg" alt="Google Pay" class="pm-logo" />
            <span>Google Pay</span>
          </div>
          <div class="pm-item">
            <i class="fas fa-credit-card pm-icon"></i>
            <span>Visa / Mastercard</span>
          </div>
          <div class="pm-item mpesa-badge">
            <i class="fas fa-mobile-alt pm-icon mpesa-green"></i>
            <span>M-Pesa (Kenya)</span>
          </div>
        </div>

        <!-- M-Pesa STK Push Modal -->
        <div v-if="mpesaModal.show" class="modal-overlay" @click.self="mpesaModal.show = false">
          <div class="mpesa-modal glass-card">
            <div class="mpesa-header">
              <i class="fas fa-mobile-alt mpesa-icon"></i>
              <h3>Pay with M-Pesa</h3>
              <button class="modal-close" @click="mpesaModal.show = false"><i class="fas fa-times"></i></button>
            </div>
            <p class="mpesa-desc">
              You'll receive an STK Push on your phone. Enter your M-Pesa PIN to complete the payment.
            </p>
            <div class="mpesa-amount">
              <span>Amount:</span>
              <strong>KES {{ mpesaModal.plan?.priceKes?.toLocaleString() }}/month</strong>
            </div>
            <div class="form-group">
              <label>M-Pesa Phone Number</label>
              <div class="phone-input-wrap">
                <span class="phone-prefix">🇰🇪 +254</span>
                <input
                  v-model="mpesaModal.phone"
                  type="tel"
                  placeholder="7XXXXXXXX"
                  maxlength="9"
                  class="phone-input"
                />
              </div>
              <small>Enter the 9 digits after +254 (e.g. 712345678)</small>
            </div>
            <button
              class="plan-cta cta-upgrade mpesa-submit"
              :disabled="mpesaLoading || mpesaModal.phone.length < 9"
              @click="submitMpesaPayment"
            >
              <i v-if="mpesaLoading" class="fas fa-spinner fa-spin"></i>
              <template v-else>Send Payment Request</template>
            </button>
            <div v-if="mpesaResult" class="mpesa-result" :class="mpesaResult.type">
              <i :class="mpesaResult.type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'"></i>
              {{ mpesaResult.message }}
            </div>
          </div>
        </div>

        <!-- Error -->
        <div v-if="errorMsg" class="alert alert-error">
          <i class="fas fa-exclamation-triangle"></i> {{ errorMsg }}
          <button @click="errorMsg = ''" class="alert-close"><i class="fas fa-times"></i></button>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from '@/components/layout/Sidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import { subscriptionService } from '@/services/subscription'
import { useUserStore } from '@/store/user'

export default {
  name: 'SubscriptionPage',
  components: { Sidebar, AppHeader, ThemeToggle },

  setup() {
    const route = useRoute()
    const userStore = useUserStore()
    const isDarkMode = ref(localStorage.getItem('theme') !== 'light')

    const subData = ref(null)
    const checkoutLoading = ref('')
    const portalLoading = ref(false)
    const errorMsg = ref('')
    const successBanner = ref(false)
    const cancelledBanner = ref(false)

    // M-Pesa state
    const mpesaModal = ref({ show: false, plan: null, phone: '' })
    const mpesaLoading = ref(false)
    const mpesaResult = ref(null)

    const currentTier = computed(() => subData.value?.tier || userStore.subscriptionTier || 'free')

    const plans = [
      {
        id: 'free',
        name: 'Free',
        price: 0,
        period: '',
        popular: false,
        features: [
          '3 Projects',
          '10 Tasks per Project',
          '2 Team Members',
          'Basic Dashboard',
          'Gantt & Timetable Views',
        ]
      },
      {
        id: 'pro',
        name: 'Pro',
        price: 29,
        priceKes: 3500,
        period: '/month',
        popular: true,
        features: [
          'Unlimited Projects',
          'Unlimited Tasks',
          '50 Team Members',
          'Full Analytics & Reports',
          'CSV Export',
          'Priority Email Support',
        ]
      },
      {
        id: 'enterprise',
        name: 'Enterprise',
        price: 99,
        priceKes: 12000,
        period: '/month',
        popular: false,
        features: [
          'Everything in Pro',
          'Unlimited Members',
          'Custom Integrations',
          'Dedicated Account Manager',
          'SLA Guarantee',
          'Priority Phone Support',
        ]
      }
    ]

    function tierDisplayName(tier) {
      return { free: 'Free Plan', pro: 'Pro', enterprise: 'Enterprise' }[tier] || 'Free Plan'
    }

    function tierIcon(tier) {
      return { free: 'fas fa-leaf', pro: 'fas fa-rocket', enterprise: 'fas fa-crown' }[tier] || 'fas fa-leaf'
    }

    function planCtaLabel(plan) {
      if (currentTier.value === plan.id) return 'Current Plan'
      if (plan.id === 'free') return 'Downgrade to Free'
      return `Upgrade to ${plan.name}`
    }

    function formatDate(iso) {
      if (!iso) return ''
      return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
    }

    function toggleTheme() {
      isDarkMode.value = !isDarkMode.value
      localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
    }

    async function loadSubscription() {
      try {
        subData.value = await subscriptionService.getSubscription()
        userStore.subscriptionTier = subData.value.tier || 'free'
      } catch (e) {
        console.warn('Could not load subscription:', e)
      }
    }

    async function selectPlanStripe(plan) {
      if (currentTier.value === plan.id) return
      checkoutLoading.value = plan.id + '_stripe'
      errorMsg.value = ''
      try {
        const { checkout_url } = await subscriptionService.createCheckoutSession(plan.id)
        window.location.href = checkout_url
      } catch (e) {
        errorMsg.value = e.response?.data?.error || 'Could not start checkout. Please try again.'
      } finally {
        checkoutLoading.value = ''
      }
    }

    function openMpesaModal(plan) {
      mpesaModal.value = { show: true, plan, phone: '' }
      mpesaResult.value = null
    }

    async function submitMpesaPayment() {
      const rawPhone = mpesaModal.value.phone.replace(/\D/g, '')
      const phone = '254' + rawPhone.replace(/^0/, '')
      if (phone.length !== 12) {
        mpesaResult.value = { type: 'error', message: 'Enter a valid Kenyan phone number (9 digits after +254)' }
        return
      }

      mpesaLoading.value = true
      mpesaResult.value = null
      try {
        const { default: api } = await import('@/services/api')
        const res = await api.post('/mpesa/stk-push', {
          phone,
          tier: mpesaModal.value.plan.id
        })
        mpesaResult.value = {
          type: 'success',
          message: res.data.message || 'STK Push sent! Check your phone and enter your M-Pesa PIN.'
        }
      } catch (e) {
        mpesaResult.value = {
          type: 'error',
          message: e.response?.data?.error || 'M-Pesa request failed. Please try again.'
        }
      } finally {
        mpesaLoading.value = false
      }
    }

    async function managePortal() {
      portalLoading.value = true
      try {
        const { portal_url } = await subscriptionService.createPortalSession()
        window.location.href = portal_url
      } catch (e) {
        errorMsg.value = e.response?.data?.error || 'Could not open billing portal.'
      } finally {
        portalLoading.value = false
      }
    }

    onMounted(async () => {
      // Detect Stripe redirect params
      if (route.query.success === '1') {
        successBanner.value = true
        await userStore.refreshSubscription()
      }
      if (route.query.cancelled === '1') {
        cancelledBanner.value = true
      }
      await loadSubscription()
    })

    return {
      isDarkMode, subData, currentTier, plans, checkoutLoading, portalLoading,
      errorMsg, successBanner, cancelledBanner,
      mpesaModal, mpesaLoading, mpesaResult,
      tierDisplayName, tierIcon, planCtaLabel, formatDate,
      toggleTheme, selectPlanStripe, openMpesaModal, submitMpesaPayment, managePortal
    }
  }
}
</script>

<style scoped>
.sub-page {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1100px;
}

/* Alerts */
.alert {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  border-radius: 10px;
  font-size: 0.9rem;
  position: relative;
}

.alert-success {
  background: rgba(0, 255, 179, 0.12);
  border: 1px solid var(--success);
  color: var(--success);
}

.alert-warning {
  background: rgba(255, 179, 0, 0.12);
  border: 1px solid var(--warning);
  color: var(--warning);
}

.alert-error {
  background: rgba(255, 0, 102, 0.12);
  border: 1px solid var(--danger);
  color: var(--danger);
}

.alert-close {
  background: none;
  border: none;
  cursor: pointer;
  color: inherit;
  margin-left: auto;
  opacity: 0.7;
  font-size: 0.85rem;
}

/* Current plan bar */
.current-plan-bar {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px 24px;
  flex-wrap: wrap;
}

.plan-summary {
  display: flex;
  align-items: center;
  gap: 12px;
}

.plan-tier-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 700;
  font-size: 1rem;
  padding: 4px 12px;
  border-radius: 20px;
}

.plan-tier-label.free    { color: rgba(255,255,255,0.6); background: rgba(255,255,255,0.05); }
.plan-tier-label.pro     { color: var(--primary); background: rgba(0,255,247,0.1); }
.plan-tier-label.enterprise { color: #ffb300; background: rgba(255,179,0,0.1); }

.plan-status {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 2px 8px;
  border-radius: 10px;
}

.plan-status.active   { background: rgba(0,255,179,0.15); color: var(--success); }
.plan-status.past_due { background: rgba(255,179,0,0.15); color: var(--warning); }
.plan-status.cancelled{ background: rgba(255,0,102,0.15); color: var(--danger);  }

.plan-usage {
  display: flex;
  gap: 20px;
  flex: 1;
  flex-wrap: wrap;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.portal-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(0,255,247,0.1);
  border: 1px solid rgba(0,255,247,0.3);
  color: var(--primary);
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.portal-btn:hover { background: rgba(0,255,247,0.18); }
.portal-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* Pricing */
.pricing-title {
  text-align: center;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.pricing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.pricing-card {
  position: relative;
  padding: 28px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.pricing-card:hover {
  transform: translateY(-4px);
}

.pricing-card.current-plan {
  border-color: rgba(0, 255, 247, 0.5) !important;
  box-shadow: 0 0 0 2px rgba(0,255,247,0.2), 0 16px 40px rgba(0,0,0,0.4) !important;
}

.pricing-card.popular {
  border-color: rgba(0, 255, 247, 0.3) !important;
}

.popular-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(90deg, var(--primary), var(--accent));
  color: #0a0f1c;
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 4px 14px;
  border-radius: 20px;
  white-space: nowrap;
}

.plan-header {
  text-align: center;
}

.plan-icon {
  font-size: 2rem;
  margin-bottom: 8px;
  color: var(--primary);
}

.plan-name {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 10px;
}

.plan-price {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
}

.price-amount {
  font-size: 2.4rem;
  font-weight: 800;
  color: var(--primary);
}

.price-period {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.plan-features {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.plan-features li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.88rem;
  color: var(--text-secondary);
}

.feature-check { color: var(--success); font-size: 0.8rem; }

.plan-cta {
  width: 100%;
  padding: 12px;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: all 0.25s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.cta-current {
  background: rgba(0,255,247,0.08);
  color: var(--primary);
  border: 1px solid rgba(0,255,247,0.2);
  cursor: default;
}

.cta-upgrade {
  background: var(--primary);
  color: #0a0f1c;
}

.cta-upgrade:hover { opacity: 0.9; transform: scale(1.02); }

.cta-downgrade {
  background: rgba(255,255,255,0.05);
  color: var(--text-secondary);
  border: 1px solid rgba(255,255,255,0.1);
}

.cta-downgrade:hover { border-color: rgba(255,255,255,0.2); }

button:disabled { opacity: 0.5; cursor: not-allowed; transform: none !important; }

/* KES price line */
.price-kes {
  font-size: 0.82rem;
  color: var(--text-secondary);
  margin-top: 2px;
}

/* Payment buttons */
.payment-btns {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.cta-mpesa {
  background: #4caf50;
  color: #fff !important;
  border: none;
}

.cta-mpesa:hover { opacity: 0.88; transform: scale(1.02); }

/* Payment methods row */
.payment-methods-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  flex-wrap: wrap;
  padding: 12px 0;
  border-top: 1px solid rgba(255,255,255,0.07);
}

.pm-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.pm-logo { height: 18px; filter: brightness(0.75); }
.pm-icon { font-size: 1rem; }
.mpesa-green { color: #4caf50; }
.mpesa-badge { color: #4caf50; }

/* M-Pesa Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(6px);
  z-index: 9000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.mpesa-modal {
  width: 100%;
  max-width: 420px;
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
}

.mpesa-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.mpesa-icon {
  font-size: 1.6rem;
  color: #4caf50;
}

.mpesa-header h3 {
  flex: 1;
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.modal-close {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 1rem;
  padding: 4px;
}

.modal-close:hover { color: var(--text-primary); }

.mpesa-desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

.mpesa-amount {
  display: flex;
  justify-content: space-between;
  padding: 10px 14px;
  background: rgba(76, 175, 80, 0.1);
  border: 1px solid rgba(76, 175, 80, 0.3);
  border-radius: 8px;
  font-size: 0.9rem;
}

.mpesa-amount strong { color: #4caf50; }

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 0.82rem;
  color: var(--text-secondary);
  font-weight: 600;
}

.form-group small {
  font-size: 0.75rem;
  color: var(--text-secondary);
  opacity: 0.7;
}

.phone-input-wrap {
  display: flex;
  align-items: center;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 8px;
  overflow: hidden;
}

.phone-prefix {
  padding: 10px 12px;
  background: rgba(255,255,255,0.04);
  border-right: 1px solid rgba(255,255,255,0.1);
  font-size: 0.85rem;
  color: var(--text-secondary);
  white-space: nowrap;
}

.phone-input {
  flex: 1;
  background: none;
  border: none;
  padding: 10px 12px;
  color: var(--text-primary);
  font-size: 0.95rem;
  outline: none;
}

.phone-input::placeholder { color: rgba(255,255,255,0.3); }

.mpesa-submit { width: 100%; }

.mpesa-result {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 0.85rem;
}

.mpesa-result.success {
  background: rgba(76,175,80,0.12);
  border: 1px solid rgba(76,175,80,0.4);
  color: #4caf50;
}

.mpesa-result.error {
  background: rgba(255,0,102,0.12);
  border: 1px solid rgba(255,0,102,0.4);
  color: var(--danger);
}

/* Animations */
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.3s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-12px); }
</style>
