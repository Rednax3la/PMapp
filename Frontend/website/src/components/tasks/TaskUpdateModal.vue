//Frontend/website/src/components/tasks/TaskUpdateModal.vue
<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal" @click.stop>
      <h3>Update Task: {{ task.name }}</h3>
      
      <form @submit.prevent="createUpdate" class="task-form">
        <div class="form-group">
          <label>Status Percentage (0–100) *</label>
          <input 
            v-model="updateData.status_percentage" 
            type="number" min="0" max="100" required 
          />
        </div>

        <div class="form-group">
          <label>Description</label>
          <textarea v-model="updateData.description" rows="4" placeholder="Describe progress…"></textarea>
        </div>

        <div class="form-group">
          <label>Upload Images</label>
          <input ref="fileInput" type="file" multiple accept="image/*" @change="handleFileSelect" />
          <div v-if="selectedFiles.length" class="file-list">
            <h4>Selected Files</h4>
            <ul>
              <li v-for="(f,i) in selectedFiles" :key="i">
                {{ f.name }}
                <button type="button" @click="removeFile(i)">&times;</button>
              </li>
            </ul>
          </div>
        </div>

        <div class="form-group">
          <label>Current Progress</label>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: currentProgress+'%' }"></div>
          </div>
          <small>{{ currentProgress }}%</small>
        </div>

        <div class="modal-actions">
          <AppButton type="button" @click="$emit('close')">Cancel</AppButton>
          <AppButton type="submit" :disabled="loading" variant="primary">
            {{ loading ? 'Updating…' : 'Create Update' }}
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
  name: 'TaskUpdateModal',
  components: { AppButton },
  props: { task: Object },
  emits: ['close','update-created'],
  data() {
    return {
      loading: false,
      selectedFiles: [],
      updateData: { status_percentage: this.task.progress||0, description: '' },
      currentProgress: this.task.progress||0
    }
  },
  methods: {
    handleFileSelect(e) {
      this.selectedFiles = Array.from(e.target.files)
    },
    removeFile(i) {
      this.selectedFiles.splice(i,1)
      this.$refs.fileInput.value = ''
    },
    async createUpdate() {
      this.loading = true
      try {
        const user = authService.getCurrentUser()
        const payload = {
          ...this.updateData,
          company_name: user.company_name,
          project_name: this.task.project,
          task_name: this.task.name
        }
        const res = await taskService.createTaskUpdate(payload, this.selectedFiles)
        this.$emit('update-created', res)
        this.$emit('close')
      } catch (e) {
        alert('Failed to update task: '+e)
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
  width: 90%; max-width: 500px;
  max-height: 90vh; overflow-y: auto;
  box-shadow: var(--shadow);
}
.form-group {
  margin-bottom: 1.5rem;
}
.form-group label {
  font-weight: 500;
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}
.form-group input,
.form-group textarea {
  width:100%;
  padding:0.75rem;
  border:1px solid var(--border-color);
  border-radius:6px;
  font-size:1rem;
  background: var(--bg-base);
  color: var(--text-primary);
}
.file-list ul {
  list-style:none; padding:0; margin-top:0.5rem;
}
.file-list li {
  display:flex; justify-content:space-between; align-items:center; padding:0.25rem 0;
}
.file-list button {
  background: var(--danger); color:#fff;
  border:none; border-radius:50%; width:20px; height:20px;
  cursor:pointer; font-size:0.8rem;
}
.progress-bar {
  width:100%; height:12px; background: var(--border-color);
  border-radius:6px; overflow:hidden; margin-bottom:0.5rem;
}
.progress-fill {
  height:100%; background: var(--accent);
  transition: width 0.3s ease;
}
.modal-actions {
  display:flex; justify-content:flex-end; gap:1rem; margin-top:2rem;
}
</style>
