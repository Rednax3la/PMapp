// src/components/ui/StateBadge.vue
<template>
  <span :class="badgeClass">
    {{ displayStatus }}
  </span>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'StateBadge',
  props: {
    status: {
      type: String,
      default: 'unknown'
    }
  },
  setup(props) {
    const badgeClass = computed(() => {
      const status = (props.status || 'unknown').toLowerCase()
      
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
    })

    const displayStatus = computed(() => {
      const status = props.status || 'Unknown'
      return status.charAt(0).toUpperCase() + status.slice(1)
    })

    return {
      badgeClass,
      displayStatus
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

.state-complete {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.state-active {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.state-tentative {
  background: rgba(251, 191, 36, 0.1);
  color: #fbbf24;
  border: 1px solid rgba(251, 191, 36, 0.2);
}

.state-delayed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.state-not-started {
  background: rgba(156, 163, 175, 0.1);
  color: #9ca3af;
  border: 1px solid rgba(156, 163, 175, 0.2);
}

.state-unknown {
  background: rgba(107, 114, 128, 0.1);
  color: #6b7280;
  border: 1px solid rgba(107, 114, 128, 0.2);
}

/* Dark mode adjustments */
.dark .state-complete {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
}

.dark .state-active {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

.dark .state-tentative {
  background: rgba(251, 191, 36, 0.2);
  color: #fcd34d;
}

.dark .state-delayed {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
}

.dark .state-not-started {
  background: rgba(156, 163, 175, 0.2);
  color: #d1d5db;
}

.dark .state-unknown {
  background: rgba(107, 114, 128, 0.2);
  color: #d1d5db;
}
</style>