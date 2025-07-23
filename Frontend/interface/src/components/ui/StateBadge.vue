<template>
  <span class="state-badge" :class="badgeClass">
    {{ status }}
  </span>
</template>

<script>
export default {
  name: 'StateBadge',
  props: {
    status: { type: String, required: true }
  },
  computed: {
    badgeClass() {
      return 'state-' + this.status.toLowerCase().replace(/\s+/g, '-');
    }
  }
};
</script>

<style scoped>
.state-badge {
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  display: inline-block;
}

.state-tentative {
  background: rgba(108, 117, 125, 0.2);
  color: var(--text-secondary);
}

.state-delayed {
  background: rgba(230, 57, 70, 0.2);
  color: var(--danger);
}

.state-in-progress {
  background: rgba(73, 80, 246, 0.2);
  color: var(--accent);
}

.state-overdue {
  background: rgba(247, 37, 133, 0.2);
  color: var(--warning);
}

.state-complete {
  background: rgba(76, 201, 240, 0.2);
  color: var(--success);
}
</style>