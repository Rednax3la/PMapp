//Frontend/website/src/components/tasks/CreateTaskModal.vue
<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal" @click.stop>
      <h3>Create New Task</h3>
      
      <form @submit.prevent="createTask" class="task-form">
        <div class="form-group">
          <label>Project *</label>
          <select v-model="taskData.project_name" required>
            <option value="">Select Project</option>
            <option v-for="project in projects" :key="project.id" :value="project.name">
              {{ project.name }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>Task Name *</label>
          <input v-model="taskData.task_name" type="text" required />
        </div>

        <div class="form-group">
          <label>Duration (hours) *</label>
          <input v-model="taskData.duration" type="number" min="1" required />
        </div>

        <div class="form-group">
          <label>Start Time</label>
          <input v-model="taskData.start_time" type="datetime-local" />
        </div>

        <div class="form-group">
          <label>Priority</label>
          <select v-model="taskData.priority">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>

        <div class="form-group">
          <label>Description</label>
          <textarea v-model="taskData.description" rows="3"></textarea>
        </div>

        <div class="form-group">
          <label>Assigned Members</label>
          <div class="tag-input">
            <input 
              v-model="memberInput" 
              type="text" 
              placeholder="Enter member and press Enter"
              @keyup.enter="addMember"
            />
            <div class="tags">
              <span 
                v-for="(member, i) in taskData.members" 
                :key="i"
                class="tag"
              >
                {{ member }}
                <button type="button" @click="removeMember(i)">&times;</button>
              </span>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>Dependencies</label>
          <div class="tag-input">
            <input 
              v-model="dependencyInput" 
              type="text" 
              placeholder="Enter dependency and press Enter"
              @keyup.enter="addDependency"
            />
            <div class="tags">
              <span 
                v-for="(dep, i) in taskData.dependencies" 
                :key="i"
                class="tag"
              >
                {{ dep }}
                <button type="button" @click="removeDependency(i)">&times;</button>
              </span>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>Estimated Cost</label>
          <input v-model="taskData.estimated_cost" type="number" min="0" step="0.01" />
        </div>

        <div class="modal-actions">
          <AppButton type="button" @click="$emit('close')">Cancel</AppButton>
          <AppButton type="submit" :disabled="loading" variant="primary">
            {{ loading ? 'Creating...' : 'Create Task' }}
          </AppButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import AppButton from '@/components/ui/AppButton.vue'
import { taskService } from '@/services/tasks'
import { authService } from '@/services/auth'

export default {
  name: 'CreateTaskModal',
  components: { AppButton },
  props: { projects: Array },
  emits: ['close','task-created'],
  data() {
    return {
      loading: false,
      memberInput: '',
      dependencyInput: '',
      taskData: {
        project_name: '',
        task_name: '',
        duration: 1,
        start_time: '',
        priority: 'medium',
        description: '',
        members: [],
        dependencies: [],
        estimated_cost: 0
      }
    }
  },
  methods: {
    addMember() {
      const m = this.memberInput.trim()
      if (m && !this.taskData.members.includes(m)) {
        this.taskData.members.push(m)
      }
      this.memberInput = ''
    },
    removeMember(i) { this.taskData.members.splice(i,1) },
    addDependency() {
      const d = this.dependencyInput.trim()
      if (d && !this.taskData.dependencies.includes(d)) {
        this.taskData.dependencies.push(d)
      }
      this.dependencyInput = ''
    },
    removeDependency(i) { this.taskData.dependencies.splice(i,1) },

    async createTask() {
      this.loading = true
      try {
        const user = authService.getCurrentUser()
        const payload = {
          ...this.taskData,
          company_name: user.company_name,
          start_time: this.taskData.start_time 
            ? new Date(this.taskData.start_time).toISOString() 
            : undefined
        }
        const res = await taskService.createTask(payload)
        this.$emit('task-created', res)
        this.$emit('close')
      } catch (e) {
        alert('Failed to create task: '+e)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.5);
  display:flex; align-items:center; justify-content:center;
  z-index:1000;
}
.modal {
  background: var(--bg-section);
  border-radius: 8px;
  padding: 2rem;
  width: 90%; max-width: 600px;
  max-height: 90vh; overflow-y: auto;
  box-shadow: var(--shadow);
}
.form-group {
  margin-bottom: 1.5rem;
}
.form-group label {
  font-weight: 500;
  display: block;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}
.form-group input,
.form-group select,
.form-group textarea {
  width:100%;
  padding:0.75rem;
  border:1px solid var(--border-color);
  border-radius:6px;
  font-size:1rem;
  background: var(--bg-base);
  color: var(--text-primary);
}
.tag-input .tags {
  display:flex; flex-wrap:wrap; gap:0.5rem; margin-top:0.5rem;
}
.tag {
  background: var(--accent);
  color: var(--dark-base);
  padding:0.25rem 0.5rem;
  border-radius:12px;
  display:flex; align-items:center; gap:0.25rem;
}
.tag button {
  background:none; border:none; cursor:pointer;
  font-size:1rem; line-height:1;
}
.modal-actions {
  display:flex; justify-content:flex-end; gap:1rem; margin-top:2rem;
}
</style>
