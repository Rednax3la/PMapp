<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal" @click.stop>
      <h3>Create New Task</h3>
      
      <form @submit.prevent="createTask">
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
          <div class="members-input">
            <input 
              v-model="memberInput" 
              type="text" 
              placeholder="Enter member name and press Enter"
              @keyup.enter="addMember"
            />
            <div class="members-list">
              <span 
                v-for="(member, index) in taskData.members" 
                :key="index"
                class="member-tag"
              >
                {{ member }}
                <button type="button" @click="removeMember(index)">&times;</button>
              </span>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>Dependencies</label>
          <div class="dependencies-input">
            <input 
              v-model="dependencyInput" 
              type="text" 
              placeholder="Enter task name and press Enter"
              @keyup.enter="addDependency"
            />
            <div class="dependencies-list">
              <span 
                v-for="(dep, index) in taskData.dependencies" 
                :key="index"
                class="dependency-tag"
              >
                {{ dep }}
                <button type="button" @click="removeDependency(index)">&times;</button>
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
import { taskService } from '@/services/tasks'
import { authService } from '@/services/auth'
import AppButton from '@/components/ui/AppButton.vue'

export default {
  name: 'CreateTaskModal',
  components: {
    AppButton
  },
  props: {
    projects: {
      type: Array,
      default: () => []
    }
  },
  emits: ['close', 'task-created'],
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
      if (this.memberInput.trim() && !this.taskData.members.includes(this.memberInput.trim())) {
        this.taskData.members.push(this.memberInput.trim())
        this.memberInput = ''
      }
    },

    removeMember(index) {
      this.taskData.members.splice(index, 1)
    },

    addDependency() {
      if (this.dependencyInput.trim() && !this.taskData.dependencies.includes(this.dependencyInput.trim())) {
        this.taskData.dependencies.push(this.dependencyInput.trim())
        this.dependencyInput = ''
      }
    },

    removeDependency(index) {
      this.taskData.dependencies.splice(index, 1)
    },

    async createTask() {
      this.loading = true
      
      try {
        const user = authService.getCurrentUser()
        const taskPayload = {
          ...this.taskData,
          company_name: user.company_name
        }
        
        // Convert start_time to proper format if provided
        if (taskPayload.start_time) {
          taskPayload.start_time = new Date(taskPayload.start_time).toISOString()
        }
        
        const result = await taskService.createTask(taskPayload)
        this.$emit('task-created', result)
        this.$emit('close')
        
      } catch (error) {
        alert('Failed to create task: ' + error)
      } finally {
        this.loading = false
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
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.members-input,
.dependencies-input {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.members-list,
.dependencies-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.member-tag,
.dependency-tag {
  background: var(--primary);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 16px;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.member-tag button,
.dependency-tag button {
  background: none;
  border: none;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  padding: 0;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.member-tag button:hover,
.dependency-tag button:hover {
  background: rgba(255,255,255,0.2);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}
</style>