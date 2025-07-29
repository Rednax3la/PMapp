<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal" @click.stop>
      <h3>Update Task: {{ task.name }}</h3>
      
      <form @submit.prevent="createUpdate">
        <div class="form-group">
          <label>Status Percentage (0-100) *</label>
          <input 
            v-model="updateData.status_percentage" 
            type="number" 
            min="0" 
            max="100" 
            required 
          />
        </div>

        <div class="form-group">
          <label>Description</label>
          <textarea 
            v-model="updateData.description" 
            rows="4"
            placeholder="Describe the progress made..."
          ></textarea>
        </div>

        <div class="form-group">
          <label>Upload Images</label>
          <input 
            ref="fileInput"
            type="file" 
            multiple 
            accept="image/*"
            @change="handleFileSelect"
          />
          <div v-if="selectedFiles.length > 0" class="selected-files">
            <h4>Selected Files:</h4>
            <ul>
              <li v-for="(file, index) in selectedFiles" :key="index">
                {{ file.name }}
                <button type="button" @click="removeFile(index)">&times;</button>
              </li>
            </ul>
          </div>
        </div>

        <div class="current-progress">
          <h4>Current Progress: {{ currentProgress }}%</h4>
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: `${currentProgress}%` }"
            ></div>
          </div>
        </div>

        <div class="modal-actions">
          <AppButton type="button" @click="$emit('close')">Cancel</AppButton>
          <AppButton type="submit" :disabled="loading" variant="primary">
            {{ loading ? 'Creating Update...' : 'Create Update' }}
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
  name: 'TaskUpdateModal',
  components: {
    AppButton
  },
  props: {
    task: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'update-created'],
  data() {
    return {
      loading: false,
      selectedFiles: [],
      updateData: {
        status_percentage: this.task.progress || 0,
        description: ''
      },
      currentProgress: this.task.progress || 0
    }
  },
  methods: {
    handleFileSelect(event) {
      const files = Array.from(event.target.files)
      this.selectedFiles = files
    },

    removeFile(index) {
      this.selectedFiles.splice(index, 1)
      // Reset file input
      this.$refs.fileInput.value = ''
    },

    async createUpdate() {
      this.loading = true
      
      try {
        const user = authService.getCurrentUser()
        const updatePayload = {
          ...this.updateData,
          company_name: user.company_name,
          project_name: this.task.project,
          task_name: this.task.name
        }
        
        const result = await taskService.createTaskUpdate(
          updatePayload, 
          this.selectedFiles.length > 0 ? this.selectedFiles : null
        )
        
        this.$emit('update-created', result)
        this.$emit('close')
        
      } catch (error) {
        alert('Failed to create update: ' + error)
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
  max-width: 500px;
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
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.selected-files {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #f9f9f9;
  border-radius: 4px;
}

.selected-files ul {
  list-style: none;
  padding: 0;
  margin: 0.5rem 0 0 0;
}

.selected-files li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0;
}

.selected-files button {
  background: var(--danger);
  color: white;
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  cursor: pointer;
  font-size: 0.8rem;
}

.current-progress {
  margin: 1rem 0;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 4px;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background: #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
  margin-top: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: var(--success);
  transition: width 0.3s ease;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}
</style>