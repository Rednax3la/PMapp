<template>
  <!-- brief welcome watermark -->
  <div
    v-if="showWelcome"
    class="welcome-watermark"
  >
    Welcome, {{ userStore.currentUser.username }}
  </div>
  <router-view class="full-page" />
</template>

<script>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/store/user'

export default {
  name: 'App',
  setup() {
    const userStore = useUserStore()
    const showWelcome = ref(!!userStore.currentUser)

    // hide watermark after 2s
    onMounted(() => {
      setTimeout(() => (showWelcome.value = false), 2000)
    })

    return { showWelcome, userStore }
  }
}
</script>

<style>
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: hidden;
}

@keyframes fadeAway {
  0%   { opacity: 1; }
  100% { opacity: 0; }
}
</style>

<style scoped>
/* let router‑view fill the viewport */
.full-page {
  display: block;
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
}

/* watermark styling + fade out */
.welcome-watermark {
  position: fixed;
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
  font-size: 1.5rem;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.1);
  pointer-events: none;
  animation: fadeAway 2s ease-out forwards;
}
</style>
