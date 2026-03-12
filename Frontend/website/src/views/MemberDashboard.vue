<template>
  <div class="app-layout" :class="{ 'light-mode': !isDarkMode }">
    <Sidebar :isDarkMode="isDarkMode" />

    <div class="main-content">
      <AppHeader title="My Dashboard">
        <template #actions>
          <ThemeToggle :isDarkMode="isDarkMode" @toggle="toggleTheme" />
        </template>
      </AppHeader>

      <div class="page-content">
        <!-- Stats Row -->
        <div class="stats-grid">
          <template v-if="loading">
            <div v-for="n in 4" :key="n" class="stat-card glass-card skeleton" style="height:100px"></div>
          </template>
          <template v-else>
            <div class="stat-card glass-card fade-in">
              <div class="stat-icon">📋</div>
              <div class="stat-info">
                <span class="stat-value">{{ stats.activeTasks }}</span>
                <span class="stat-label">Active Tasks</span>
              </div>
            </div>
            <div class="stat-card glass-card fade-in">
              <div class="stat-icon">⏰</div>
              <div class="stat-info">
                <span class="stat-value">{{ stats.dueToday }}</span>
                <span class="stat-label">Due Today</span>
              </div>
            </div>
            <div class="stat-card glass-card fade-in">
              <div class="stat-icon">🗂️</div>
              <div class="stat-info">
                <span class="stat-value">{{ stats.myProjects }}</span>
                <span class="stat-label">My Projects</span>
              </div>
            </div>
            <div class="stat-card glass-card fade-in">
              <div class="stat-icon">✅</div>
              <div class="stat-info">
                <span class="stat-value">{{ stats.completionRate }}%</span>
                <span class="stat-label">Completion Rate</span>
              </div>
            </div>
          </template>
        </div>

        <!-- Tasks & Projects Row -->
        <div class="content-grid">
          <!-- My Tasks -->
          <div class="card glass-card fade-in">
            <div class="card-header">
              <h3>My Tasks</h3>
              <span class="count-badge">{{ myTasks.length }}</span>
            </div>
            <div v-if="loading" class="skeleton-list">
              <div v-for="n in 4" :key="n" class="skeleton sk-row"></div>
            </div>
            <div v-else-if="myTasks.length === 0" class="empty-state">
              <p>No tasks assigned to you yet.</p>
            </div>
            <div v-else class="task-list">
              <div v-for="task in myTasks" :key="task.id" class="task-item">
                <div class="task-header">
                  <span class="task-name">{{ task.task_name || task.name }}</span>
                  <StateBadge :status="task.state || 'tentative'" />
                </div>
                <div class="task-meta">
                  <span class="task-project">{{ task.project_name || '' }}</span>
                </div>
                <div class="task-progress">
                  <div class="progress-label">
                    <span>Progress</span>
                    <span>{{ taskProgress[task.id] ?? task.progress ?? 0 }}%</span>
                  </div>
                  <input
                    type="range"
                    :value="taskProgress[task.id] ?? task.progress ?? 0"
                    min="0" max="100" step="5"
                    class="progress-slider"
                    @change="(e) => updateTaskProgress(task, parseInt(e.target.value))"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- My Projects -->
          <div class="card glass-card fade-in">
            <div class="card-header">
              <h3>My Projects</h3>
              <span class="count-badge">{{ myProjects.length }}</span>
            </div>
            <div v-if="loading" class="skeleton-list">
              <div v-for="n in 3" :key="n" class="skeleton sk-row" style="height:70px"></div>
            </div>
            <div v-else-if="myProjects.length === 0" class="empty-state">
              <p>You're not assigned to any projects yet.</p>
            </div>
            <div v-else class="project-list">
              <div v-for="proj in myProjects" :key="proj.id" class="project-item">
                <div class="project-header">
                  <span class="project-name">{{ proj.name }}</span>
                  <StateBadge :status="proj.state || 'tentative'" />
                </div>
                <div class="project-meta">
                  <span>{{ proj.task_count || 0 }} tasks</span>
                  <span>{{ proj.completed_tasks || 0 }} completed</span>
                </div>
                <div class="mini-progress-bar">
                  <div
                    class="mini-progress-fill"
                    :style="{ width: projCompletionRate(proj) + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Success/Error notification -->
        <transition name="slide-up">
          <div v-if="notification.message" :class="['notification', notification.type]">
            {{ notification.message }}
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import api from '@/services/api'
import Sidebar from '@/components/layout/Sidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import StateBadge from '@/components/ui/StateBadge.vue'

export default {
  name: 'MemberDashboard',
  components: { Sidebar, AppHeader, ThemeToggle, StateBadge },

  setup() {
    const userStore = useUserStore()
    const isDarkMode = ref(localStorage.getItem('theme') !== 'light')
    const loading = ref(true)
    const myTasks = ref([])
    const myProjects = ref([])
    const taskProgress = ref({})
    const notification = ref({ message: '', type: 'success' })

    const stats = computed(() => {
      const today = new Date().toISOString().split('T')[0]
      const activeTasks = myTasks.value.filter(t => !['complete'].includes(t.state)).length
      const dueToday = myTasks.value.filter(t => {
        const due = (t.start_time || '').split('T')[0]
        return due === today
      }).length
      const completed = myTasks.value.filter(t => t.state === 'complete').length
      const total = myTasks.value.length
      return {
        activeTasks,
        dueToday,
        myProjects: myProjects.value.length,
        completionRate: total ? Math.round((completed / total) * 100) : 0
      }
    })

    function projCompletionRate(proj) {
      if (!proj.task_count) return 0
      return Math.round(((proj.completed_tasks || 0) / proj.task_count) * 100)
    }

    function showNotification(message, type = 'success') {
      notification.value = { message, type }
      setTimeout(() => { notification.value.message = '' }, 3000)
    }

    async function updateTaskProgress(task, progress) {
      taskProgress.value[task.id] = progress
      try {
        const formData = new FormData()
        formData.append('task_name', task.task_name || task.name)
        formData.append('project_name', task.project_name || '')
        formData.append('status_percentage', progress)
        formData.append('description', `Progress updated to ${progress}%`)

        await api.post('/tasks/updates', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        showNotification(`Task progress updated to ${progress}%`)
      } catch (e) {
        showNotification('Failed to update progress', 'error')
        taskProgress.value[task.id] = task.progress || 0
      }
    }

    function toggleTheme() {
      isDarkMode.value = !isDarkMode.value
      localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
    }

    onMounted(async () => {
      loading.value = true
      try {
        const email = userStore.currentUser?.username || ''

        // Fetch tasks assigned to the current member
        const [tasksRes, projRes] = await Promise.all([
          api.post('/tasks/member', {
            member: email,
            company_name: userStore.companyName
          }),
          api.post('/projects/view')
        ])

        myTasks.value = (tasksRes.data.tasks || tasksRes.data || []).map(t => ({
          ...t,
          progress: t.latest_status || 0
        }))

        // Initialise local progress state
        myTasks.value.forEach(t => {
          taskProgress.value[t.id] = t.progress || 0
        })

        // Filter projects to those where current user is a team member
        myProjects.value = (projRes.data.projects || []).filter(
          p => (p.team || []).includes(email)
        )
      } catch (e) {
        console.error('Error loading member dashboard:', e)
      } finally {
        loading.value = false
      }
    })

    return {
      isDarkMode, loading, myTasks, myProjects,
      taskProgress, stats, notification,
      projCompletionRate, updateTaskProgress, toggleTheme
    }
  }
}
</script>

<style scoped>
.page-content {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.stat-icon { font-size: 2rem; }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--primary);
}

.stat-label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 768px) {
  .content-grid { grid-template-columns: 1fr; }
}

.card { padding: 20px; }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 600;
}

.count-badge {
  background: rgba(0,255,247,0.15);
  color: var(--primary);
  border: 1px solid rgba(0,255,247,0.3);
  border-radius: 20px;
  padding: 2px 10px;
  font-size: 0.8rem;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 32px 0;
  color: var(--text-secondary);
}

/* Tasks */
.task-list { display: flex; flex-direction: column; gap: 12px; max-height: 420px; overflow-y: auto; }

.task-item {
  background: rgba(0,0,0,0.15);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 10px;
  padding: 14px;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.task-name { font-weight: 600; color: var(--text-primary); font-size: 0.9rem; }

.task-meta { font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 10px; }

.task-progress {}

.progress-label {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.progress-slider {
  width: 100%;
  accent-color: var(--primary);
  cursor: pointer;
}

/* Projects */
.project-list { display: flex; flex-direction: column; gap: 12px; max-height: 420px; overflow-y: auto; }

.project-item {
  background: rgba(0,0,0,0.15);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 10px;
  padding: 14px;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.project-name { font-weight: 600; color: var(--text-primary); font-size: 0.9rem; }

.project-meta {
  display: flex;
  gap: 12px;
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.mini-progress-bar {
  height: 4px;
  background: rgba(255,255,255,0.1);
  border-radius: 2px;
  overflow: hidden;
}

.mini-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  border-radius: 2px;
  transition: width 0.4s ease;
}

/* Skeleton rows */
.skeleton-list { display: flex; flex-direction: column; gap: 10px; }
.sk-row { height: 80px; border-radius: 10px; }

/* Notification */
.notification {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  z-index: 9999;
  box-shadow: 0 4px 16px rgba(0,0,0,0.3);
}

.notification.success {
  background: rgba(0,255,179,0.2);
  border: 1px solid var(--success);
  color: var(--success);
}

.notification.error {
  background: rgba(255,0,102,0.2);
  border: 1px solid var(--danger);
  color: var(--danger);
}

.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s ease; }
.slide-up-enter-from, .slide-up-leave-to { opacity: 0; transform: translateY(20px); }
</style>
