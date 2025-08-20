//Frontend/website/src/components/tasks/CreateTaskModal.vue
<template>
  <div class="modal-overlay">
    <div class="modal">
      <h3>Create Task</h3>
      <form @submit.prevent="createTask">
        <!-- Project -->
        <div class="form-group">
          <label>Project *</label>
          <select v-model="taskData.project_name" required>
            <option value="" disabled>Select project</option>
            <option v-for="project in projects" :key="project.name || project.project_name" :value="project.name || project.project_name">
              {{ project.name || project.project_name }}
            </option>
          </select>
        </div>

        <!-- Task name -->
        <div class="form-group">
          <label>Task Name *</label>
          <input v-model="taskData.task_name" type="text" required />
        </div>

        <!-- Expected duration (in hours) -->
        <div class="form-group">
          <label>Duration (hours) *</label>
          <input v-model.number="taskData.expected_duration" type="number" min="0" step="0.5" required />
        </div>

        <!-- Start time -->
        <div class="form-group">
          <label>Start Time</label>
          <input v-model="taskData.start_time" type="datetime-local" />
        </div>

        <!-- Priority -->
        <div class="form-group">
          <label>Priority</label>
          <select v-model="taskData.priority">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>

        <!-- Description -->
        <div class="form-group">
          <label>Description</label>
          <textarea v-model="taskData.description" rows="3"></textarea>
        </div>

        <!-- Members -->
        <div class="form-group">
          <label>Assigned Members</label>
          <div class="tag-input">
            <input v-model="memberInput" type="email" placeholder="member@example.com and press Enter" @keyup.enter.prevent="addMember" />
            <div class="tags">
              <span v-for="(member, i) in taskData.members" :key="member + i" class="tag">
                {{ member }}
                <button type="button" @click="removeMember(i)">&times;</button>
              </span>
            </div>
          </div>
        </div>

        <!-- Dependencies -->
        <div class="form-group">
          <label>Dependencies</label>
          <div class="tag-input">
            <input v-model="dependencyInput" type="text" placeholder="Enter dependency and press Enter" @keyup.enter.prevent="addDependency" />
            <div class="tags">
              <span v-for="(dep, i) in taskData.dependencies" :key="dep + i" class="tag">
                {{ dep }}
                <button type="button" @click="removeDependency(i)">&times;</button>
              </span>
            </div>
          </div>
        </div>

        <!-- Estimated cost -->
        <div class="form-group">
          <label>Estimated Cost</label>
          <input v-model.number="taskData.estimated_cost" type="number" min="0" step="0.01" />
        </div>

        <!-- Error -->
        <div v-if="localError" class="text-red-500 text-sm mb-2">{{ localError }}</div>

        <!-- Actions -->
        <div class="modal-actions">
          <AppButton type="button" @click="$emit('close')">Cancel</AppButton>
          <AppButton type="submit" :disabled="loading" variant="primary">
            {{ loading ? 'Creating…' : 'Create Task' }}
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
  name: 'CreateTaskModal',
  components: { AppButton },
  props: {
    projects: { type: Array, default: () => [] },
    // optional prop so parent can explicitly pass company name if they prefer
    companyName: { type: String, default: '' }
  },
  emits: ['close','task-created'],
  data() {
    return {
      loading: false,
      memberInput: '',
      dependencyInput: '',
      localError: '',
      taskData: {
        project_name: '',
        task_name: '',
        expected_duration: '', 
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
      const m = (this.memberInput || '').trim().toLowerCase()
      const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!m) return
      if (!emailRe.test(m)) {
        this.localError = 'Enter a valid email for members'
        this.memberInput = ''
        setTimeout(() => { this.localError = '' }, 3000)
        return
      }
      if (!this.taskData.members.includes(m)) this.taskData.members.push(m)
      this.memberInput = ''
    },
    removeMember(i) { this.taskData.members.splice(i,1) },
    addDependency() {
      const d = (this.dependencyInput || '').trim()
      if (d && !this.taskData.dependencies.includes(d)) this.taskData.dependencies.push(d)
      this.dependencyInput = ''
    },
    removeDependency(i) { this.taskData.dependencies.splice(i,1) },

    // Attempt to resolve company name from several possible sources
    async resolveCompanyName() {
      // 1) explicit prop
      if (this.companyName) return this.companyName

      // 2) from user store
      try {
        const userStore = useUserStore()
        const candidate =
          (userStore && (userStore.currentUser?.company_name || userStore.user?.company_name || userStore.companyName || userStore.company)) ||
          null
        if (candidate) return candidate
        // If the store exposes initializeAuth, try it once to refresh
        if (typeof userStore.initializeAuth === 'function') {
          try {
            await userStore.initializeAuth()
            const refreshed =
              (userStore.currentUser?.company_name || userStore.user?.company_name || userStore.companyName || userStore.company) || null
            if (refreshed) return refreshed
          } catch (e) {
            // ignore initialize errors — we'll try other sources
          }
        }
      } catch (e) {
        // ignore - fall through to other methods
      }

      // 3) authService fallback
      try {
        const user = authService.getCurrentUser()
        if (user && (user.company_name || user.company)) return user.company_name || user.company
      } catch (e) {
        // ignore
      }

      // 4) localStorage fallback (some apps persist user data)
      try {
        const raw = localStorage.getItem('user_data') || localStorage.getItem('user') || localStorage.getItem('user_data_v2')
        if (raw) {
          try {
            const parsed = JSON.parse(raw)
            if (parsed && (parsed.company_name || parsed.company)) return parsed.company_name || parsed.company
          } catch (err) {
            // raw might be a JSON string inside another string — try a relaxed parse
            if (raw.includes('company')) {
              const m = raw.match(/"company_name"\s*:\s*"([^"]+)"/)
              if (m) return m[1]
            }
          }
        }
      } catch (e) {
        // ignore
      }

      // not found
      return ''
    },

    async createTask() {
      this.localError = ''
      this.loading = true
      try {
        // Validate minimal required fields
        if (!this.taskData.task_name || !this.taskData.project_name || this.taskData.expected_duration == null) {
          throw new Error('Please fill project, task name and expected duration.')
        }

        // Resolve company name robustly (same resolver as before)
        const companyName = await this.resolveCompanyName()
        if (!companyName) {
          throw new Error('No company info found for current user. Please log in again or ensure your account is associated with a company.')
        }

        const hoursNumber = Number(this.taskData.expected_duration)
        if (!Number.isFinite(hoursNumber) || hoursNumber < 0) {
          throw new Error('Expected duration must be a non-negative number')
        }

        // convert hours -> minutes (adjust if your API expects hours)
        const minutes = Math.round(hoursNumber * 60)
        const expectedDurationStr = String(minutes) // <- IMPORTANT: stringified

        const payload = {
          project_name: this.taskData.project_name,
          task_name: this.taskData.task_name,
          expected_duration: expectedDurationStr,
          priority: this.taskData.priority,
          description: this.taskData.description || undefined,
          members: Array.isArray(this.taskData.members) ? this.taskData.members : [],
          dependencies: Array.isArray(this.taskData.dependencies) ? this.taskData.dependencies : [],
          estimated_cost: this.taskData.estimated_cost ? Number(this.taskData.estimated_cost) : undefined,
          company_name: companyName
        }

        // normalize start_time -> ISO if provided
        if (this.taskData.start_time) {
          const dt = new Date(this.taskData.start_time)
          if (!isNaN(dt)) payload.start_time = dt.toISOString()
        }

        const response = await taskService.createTask(payload)
        this.$emit('task-created', response)
        this.$emit('close')
      } catch (err) {
        this.localError = err?.message || String(err)
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
