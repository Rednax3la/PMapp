<template>
  <button
    :class="['btn', variantClass, sizeClass]"
    v-bind="tooltipAttrs"
    @click="$emit('click')"
  >
    <i v-if="icon" :class="icon"></i>
    <slot />
  </button>
</template>

<script>
export default {
  name: 'AppButton',
  props: {
    variant: { type: String, default: 'primary' },
    size: { type: String, default: 'normal' },
    icon: { type: String, default: '' },
    tooltip: { type: String, default: '' }
  },
  emits: ['click'],
  computed: {
    variantClass() {
      return this.variant === 'icon' ? 'btn-icon' : `btn-${this.variant}`;
    },
    sizeClass() {
      return this.size === 'small' ? 'btn-sm' : '';
    },
    tooltipAttrs() {
      return this.tooltip ? { title: this.tooltip } : {};
    }
  }
};
</script>

<style scoped>
.btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  text-decoration: none;
}

.btn-primary {
  background: var(--primary);
  color: var(--dark-base);
}

.btn-success {
  background: var(--success);
  color: var(--dark-base);
}

.btn-warning {
  background: var(--warning);
  color: var(--dark-base);
}

.btn-danger {
  background: var(--danger);
  color: var(--dark-base);
}

.btn-sm {
  padding: 6px 12px;
  font-size: 14px;
}

.btn-icon {
  background: transparent;
  color: var(--text-secondary);
  padding: 8px;
  border-radius: 50%;
  width: 36px;
  height: 36px;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--accent);
}

.btn:hover {
  opacity: 0.9;
  transform: translateY(-2px);
}

.btn:active {
  transform: translateY(0);
}
</style>