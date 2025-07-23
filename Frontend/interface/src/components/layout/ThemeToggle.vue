<template>
  <button class="theme-toggle" @click="$emit('toggle')">
    <i :class="isDark ? 'fas fa-sun' : 'fas fa-moon'"></i>
    {{ isDark ? 'Light Mode' : 'Dark Mode' }}
  </button>
</template>

<script>
export default {
  name: 'ThemeToggle',
  props: {
    isDark: { type: Boolean, required: true }
  }
};
</script>

<style scoped>
.theme-toggle {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.theme-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
}
</style>