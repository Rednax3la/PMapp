//Frontend/website/src/components/projects/ProjectModal.vue
<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <header class="modal-header">
        <h3>{{ project.name }}</h3>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </header>
      
      <div class="modal-body">
        <div class="project-description">
          <p>{{ project.description }}</p>
        </div>
        
        <div class="project-details">
          <div class="detail-row">
            <span class="detail-label">Status:</span>
            <StateBadge :status="project.status" />
          </div>
          
          <div class="detail-row">
            <span class="detail-label">Progress:</span>
            <div class="progress-info">
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: project.progress + '%', background: project.progressColor }"
                ></div>
              </div>
              <span class="progress-value">{{ project.progress }}%</span>
            </div>
          </div>
          
          <div class="detail-row">
            <span class="detail-label">Duration:</span>
            <span>{{ formatDateRange(project.startDate, project.endDate) }}</span>
          </div>
          
          <div class="detail-row">
            <span class="detail-label">Tasks:</span>
            <span>{{ project.tasks }} tasks</span>
          </div>
          
          <div class="detail-row">
            <span class="detail-label">Team:</span>
            <div class="team-members">
              <span v-for="member in project.team" :key="member" class="member-tag">
                <i class="fas fa-user"></i> {{ member }}
              </span>
            </div>
          </div>
          
          <div class="detail-row" v-if="project.budget">
            <span class="detail-label">Budget:</span>
            <div class="budget-info">
              <span class="budget-total">${{ project.budget.toLocaleString() }}</span>
              <span class="budget-spent">Spent: ${{ project.spent.toLocaleString() }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <footer class="modal-footer">
        <AppButton variant="primary" @click="$emit('close')">Close</AppButton>
        <AppButton variant="success" icon="fas fa-edit">Edit Project</AppButton>
      </footer>
    </div>
  </div>
</template>

<script>
import { format } from 'date-fns'
import AppButton from '@/components/ui/AppButton.vue'
import StateBadge from '@/components/ui/StateBadge.vue'

export default {
  name: 'ProjectModal',
  components: { AppButton, StateBadge },
  props: {
    project: { type: Object, required: true }
  },
  emits: ['close'],
  methods: {
    formatDateRange(startDate, endDate) {
      try {
        const start = startDate ? new Date(startDate) : null
        const end = endDate ? new Date(endDate) : null

        if (!start || isNaN(start.getTime())) {
          return 'Invalid start date'
        }
        if (!end || isNaN(end.getTime())) {
          return 'Invalid end date'
        }

        return `${format(start, 'MMM dd, yyyy')} - ${format(end, 'MMM dd, yyyy')}`
      } catch (error) {
        console.error('Date formatting error:', error)
        return 'Invalid date range'
      }
    }
  }
}
</script>


<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal-content {
  background: var(--bg-section);
  color: var(--text-primary);
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  box-shadow: var(--shadow);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 20px;
  background: rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 2rem;
  line-height: 1;
  cursor: pointer;
  color: var(--text-secondary);
  transition: color 0.2s ease;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: var(--danger);
}

.modal-body {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.project-description {
  margin-bottom: 20px;
}

.project-description p {
  color: var(--text-secondary);
  line-height: 1.6;
}

.project-details {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 15px;
}

.detail-label {
  font-weight: 600;
  min-width: 80px;
  color: var(--text-primary);
}

.progress-info {
  display: flex;
  align-items: center;
  gap: 15px;
  flex: 1;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-value {
  font-weight: 600;
  font-size: 14px;
  min-width: 40px;
}

.team-members {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.member-tag {
  background: rgba(0, 0, 0, 0.1);
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-primary);
}

.budget-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.budget-total {
  font-weight: 600;
  color: var(--success);
}

.budget-spent {
  font-size: 12px;
  color: var(--text-secondary);
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  background: rgba(0, 0, 0, 0.05);
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .detail-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .detail-label {
    min-width: auto;
  }
  
  .progress-info {
    width: 100%;
  }
}
</style>