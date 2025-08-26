// src/components/ui/StateBadge.vue
<template>
  <span :class="badgeClass">
    {{ displayStatus }}
  </span>
</template>

<script>
export default {
  name: 'StateBadge',
  props: {
    status: {
      type: String,
      default: 'unknown'
    }
  },
  computed: {
    badgeClass() {
      const status = (this.status || 'unknown').toLowerCase()
      const baseClass = 'state-badge'

      switch (status) {
        case 'complete':
        case 'completed':
          return `${baseClass} state-complete`
        case 'active':
        case 'in progress':
        case 'in-progress':
          return `${baseClass} state-active`
        case 'tentative':
        case 'planning':
          return `${baseClass} state-tentative`
        case 'delayed':
        case 'overdue':
          return `${baseClass} state-delayed`
        case 'not started':
        case 'not-started':
          return `${baseClass} state-not-started`
        default:
          return `${baseClass} state-unknown`
      }
    },
    displayStatus() {
      const status = this.status || 'Unknown'
      return status.charAt(0).toUpperCase() + status.slice(1)
    }
  }
}
</script>


<style scoped>
.state-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

/* === Consistent with chart colors === */
.state-complete {
  background: rgba(76, 201, 240, 0.15);
  color: rgb(76, 201, 240);
  border: 1px solid rgba(76, 201, 240, 0.4);
}

.state-active {
  background: rgba(73, 80, 246, 0.15);
  color: rgb(73, 80, 246);
  border: 1px solid rgba(73, 80, 246, 0.4);
}

.state-tentative {
  background: rgba(108, 117, 125, 0.15);
  color: rgb(108, 117, 125);
  border: 1px solid rgba(108, 117, 125, 0.4);
}

.state-delayed {
  background: rgba(230, 57, 70, 0.15);
  color: rgb(230, 57, 70);
  border: 1px solid rgba(230, 57, 70, 0.4);
}

.state-not-started {
  background: rgba(156, 163, 175, 0.15);
  color: #9ca3af;
  border: 1px solid rgba(156, 163, 175, 0.4);
}

.state-unknown {
  background: rgba(107, 114, 128, 0.15);
  color: #6b7280;
  border: 1px solid rgba(107, 114, 128, 0.4);
}

/* Dark mode adjustments (slightly stronger backgrounds) */
.dark .state-complete {
  background: rgba(76, 201, 240, 0.25);
  color: rgb(125, 220, 250);
}

.dark .state-active {
  background: rgba(73, 80, 246, 0.25);
  color: rgb(120, 130, 250);
}

.dark .state-tentative {
  background: rgba(108, 117, 125, 0.25);
  color: rgb(180, 185, 190);
}

.dark .state-delayed {
  background: rgba(230, 57, 70, 0.25);
  color: rgb(240, 100, 115);
}

.dark .state-not-started {
  background: rgba(156, 163, 175, 0.25);
  color: #d1d5db;
}

.dark .state-unknown {
  background: rgba(107, 114, 128, 0.25);
  color: #d1d5db;
}
</style>