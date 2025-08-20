//Frontend/website/src/components/tasks/TaskUpdateModal.vue
<template>
  <div class="modal-overlay">
    <div class="modal">
      <h3>Create Update</h3>
      <form @submit.prevent="createUpdate">
        <div class="form-group">
          <label>Progress (%)</label>
          <input v-model.number="updateData.status_percentage" type="number" min="0" max="100" />
        </div>

        <div class="form-group">
          <label>Description</label>
          <textarea v-model="updateData.description" rows="3"></textarea>
        </div>

        <div class="form-group">
          <label>Attach Images</label>
          <input ref="fileInput" type="file" multiple @change="handleFileSelect" />
          <div class="file-list" v-if="selectedFiles.length">
            <ul>
              <li v-for="(f, i) in selectedFiles" :key="f.name">
                {{ f.name }} <button type="button" @click="removeFile(i)">&times;</button>
              </li>
            </ul>
          </div>
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
import { useUserStore } from '@/store/user'
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
      updateData: { status_percentage: this.task?.progress || 0, description: '' },
      currentProgress: this.task?.progress || 0
    }
  },
  methods: {
    handleFileSelect(e) {
      this.selectedFiles = Array.from(e.target.files || [])
    },
    removeFile(i) {
      this.selectedFiles.splice(i,1)
      if (this.$refs.fileInput) this.$refs.fileInput.value = ''
    },
    async createUpdate() {
      this.loading = true
      try {
        // get company
        const userStore = useUserStore()
        const userData = userStore?.currentUser || userStore?.user || authService.getCurrentUser() || {}
        const companyName = userData?.company_name || userData?.company
        if (!companyName) throw new Error('Missing company info')

        const payload = {
          ...this.updateData,
          company_name: companyName,
          project_name: this.task?.project,
          task_name: this.task?.name || this.task?.task_name || this.task?.title
        }

        const res = await taskService.createTaskUpdate(payload, this.selectedFiles)
        this.$emit('update-created', res)
        this.$emit('close')
      } catch (e) {
        alert('Failed to update task: ' + (e?.message || e))
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
