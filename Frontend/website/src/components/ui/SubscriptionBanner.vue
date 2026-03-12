<template>
  <transition name="slide-down">
    <div v-if="visible" class="sub-banner">
      <div class="banner-content">
        <i class="fas fa-lock banner-icon"></i>
        <div class="banner-text">
          <strong>Plan limit reached</strong>
          <span>{{ message || "You've hit your Free plan limit." }}</span>
        </div>
      </div>
      <div class="banner-actions">
        <router-link to="/subscription" class="upgrade-btn">
          <i class="fas fa-crown"></i>
          Upgrade Plan
        </router-link>
        <button class="close-btn" @click="visible = false">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'SubscriptionBanner',
  props: {
    message: { type: String, default: '' },
    show: { type: Boolean, default: false }
  },
  data() {
    return { visible: this.show }
  },
  watch: {
    show(val) { this.visible = val }
  }
}
</script>

<style scoped>
.sub-banner {
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 20px;
  border-radius: 12px;
  background: rgba(10, 15, 28, 0.92);
  border: 1px solid rgba(255, 0, 102, 0.4);
  box-shadow: 0 8px 32px rgba(255, 0, 102, 0.2);
  backdrop-filter: blur(12px);
  min-width: 340px;
  max-width: 600px;
}

.banner-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.banner-icon {
  color: var(--warning);
  font-size: 1.1rem;
}

.banner-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.banner-text strong {
  color: var(--text-primary);
  font-size: 0.9rem;
}

.banner-text span {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.banner-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.upgrade-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--primary);
  color: #0a0f1c;
  font-weight: 700;
  font-size: 0.8rem;
  padding: 7px 14px;
  border-radius: 8px;
  text-decoration: none;
  transition: opacity 0.2s ease;
}

.upgrade-btn:hover { opacity: 0.85; }

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 0.9rem;
  padding: 4px 8px;
  border-radius: 6px;
  transition: color 0.2s ease;
}

.close-btn:hover { color: var(--text-primary); }

/* Animation */
.slide-down-enter-active,
.slide-down-leave-active { transition: all 0.3s ease; }
.slide-down-enter-from,
.slide-down-leave-to { opacity: 0; transform: translateX(-50%) translateY(-20px); }
</style>
