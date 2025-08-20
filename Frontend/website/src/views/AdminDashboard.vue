//Frontend/website/src/views/AdminDashboard.vue
<template>
  <div class="admin-dashboard" :class="{ dark: isDark, light: !isDark }">
    <!-- Sidebar -->
    <Sidebar />

    <!-- Main Content -->
    <div class="main-content">
      <AppHeader title="Dashboard">
        <template #actions>
          <ThemeToggle :is-dark="isDark" @toggle="toggleTheme" />
        </template>
      </AppHeader>

      <!-- Stats Overview -->
      <div class="stats-grid">
        <div
          class="stat-card"
          v-for="stat in displayStats"
          :key="stat.label"
          :class="{ 'stat-placeholder': stat.isPlaceholder }"
        >
          <div class="stat-label">{{ stat.label }}</div>
          <div class="stat-value" :style="{ color: stat.color }">
            {{ stat.value ?? '0' }}
          </div>
        </div>
      </div>

      <!-- State Legend -->
      <div class="state-legend">
        <div class="legend-item" v-for="item in legendItems" :key="item.label">
          <div class="legend-color" :style="{ background: item.color }"></div>
          <span>{{ item.label }}</span>
        </div>
      </div>

      <!-- Dashboard Content -->
      <div class="grid">
        <!-- Active Projects -->
        <div class="card">
          <div class="card-header">
            <span>Active Projects</span>
            <router-link to="/projects" class="btn btn-primary btn-sm">View All</router-link>
          </div>
          <div class="card-body">
            <div
              class="task-item"
              v-for="project in projects"
              :key="project.id || project.project_name"
            >
              <div class="task-info">
                <div class="task-title">{{ project.project_name || project.name }}</div>
                <div class="task-meta">
                  <span><i class="far fa-calendar"></i>
                    {{ formatDate(project.start_date || project.startDate) }}
                    <span v-if="project.end_date || project.endDate"> - {{ formatDate(project.end_date || project.endDate) }}</span>
                  </span>
                  <span><i class="fas fa-tasks"></i> {{ (project.tasks && project.tasks.length) || project.tasks || '—' }}</span>
                </div>
              </div>
              <StateBadge :state="project.state || project.status" />
            </div>
          </div>
        </div>

        <!-- Recent Tasks -->
        <div class="card">
          <div class="card-header">
            <span>Recent Tasks</span>
            <router-link to="/tasks" class="btn btn-primary btn-sm">View All</router-link>
          </div>
          <div class="card-body">
            <div
              class="task-item"
              v-for="task in tasks"
              :key="task.id || task.task_name"
            >
              <div class="task-info">
                <div class="task-title">{{ task.title || task.task_name }}</div>
                <div class="task-meta">
                  <span><i class="far fa-calendar"></i>
                    <span v-if="task.start_time">{{ formatDate(task.start_time) }}</span>
                    <span v-else>—</span>
                  </span>
                  <span :class="priorityClass(task.priority)">{{ task.priority || '—' }}</span>
                </div>
              </div>
              <StateBadge :state="task.state" />
            </div>
          </div>
        </div>

        <!-- Task Status Distribution (chart) -->
        <div class="card">
          <div class="card-header">
            <span>Task Status Distribution</span>
          </div>
          <div class="card-body">
            <div class="chart-container">
              <canvas ref="chartCanvas"></canvas>
            </div>
          </div>
        </div>

        <!-- Team Members -->
        <div class="card">
          <div class="card-header">
            <span>Team Members</span>
          </div>
          <div class="card-body">
            <div class="member-list">
              <div class="member-tag" v-for="member in uniqueTeamMembers" :key="member">
                <i class="fas fa-user"></i> {{ member }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Upcoming Deadlines -->
      <div class="card" style="margin-top: 16px;">
        <div class="card-header">
          <span>Upcoming Deadlines</span>
        </div>
        <div class="card-body">
          <div class="grid">
            <div
              class="task-item"
              v-for="deadline in deadlines"
              :key="deadline.title + (deadline.dueDate || '')"
            >
              <div class="task-info">
                <div class="task-title">{{ deadline.title }}</div>
                <div class="task-meta">
                  <span><i class="far fa-calendar"></i> Due: {{ deadline.dueDate }}</span>
                  <span>Project: {{ deadline.project }}</span>
                </div>
              </div>
              <StateBadge :state="deadline.status" />
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto'
import Sidebar from '@/components/layout/Sidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import StateBadge from '@/components/ui/StateBadge.vue'
import { projectService } from '@/services/projects'
import { authService } from '@/services/auth'

export default {
  name: 'AdminDashboard',
  components: { Sidebar, AppHeader, ThemeToggle, StateBadge },

  data() {
    return {
      isDark: true,
      stats: [],
      projects: [],
      tasks: [],
      teamMembers: [],
      deadlines: [],
      loading: false,
      error: null,
      chartInstance: null
    }
  },

  computed: {
    legendItems() {
      const a = this.isDark ? 0.2 : 0.5
      return [
        { label: 'Tentative',   color: `rgba(108,117,125,${a})` },
        { label: 'Delayed',     color: `rgba(230,57,70,${a})` },
        { label: 'In Progress', color: `rgba(73,80,246,${a})` },
        { label: 'Overdue',     color: `rgba(247,37,133,${a})` },
        { label: 'Complete',    color: `rgba(76,201,240,${a})` }
      ]
    },

    uniqueTeamMembers() {
      return [...new Set(this.teamMembers || [])]
    },
    displayStats() {
      if (Array.isArray(this.stats) && this.stats.length >= 4) {
        // normal path: if API supplied at least four cards, use them
        return this.stats
      }

      // default placeholder skeleton — keeps labels and colors consistent with your UI
      const defaults = [
        { label: 'Active Projects', value: 0, color: 'var(--primary)' },
        { label: 'Total Tasks', value: 0, color: 'var(--primary)' },
        { label: 'Team Members', value: 0, color: 'var(--success)' },
        { label: 'Completion Rate', value: '0%', color: 'var(--warning)' }
      ]

      // if you have some stat values but <4, merge them into defaults
      if (Array.isArray(this.stats) && this.stats.length > 0) {
        return defaults.map((d, i) => {
          const s = this.stats[i]
          return s ? { ...d, ...s, isPlaceholder: false } : { ...d, isPlaceholder: true }
        })
      }

      // no stats at all -> placeholders
      return defaults.map(d => ({ ...d, isPlaceholder: true }))
    }
  },

  methods: {
    toggleTheme() {
      this.isDark = !this.isDark
      localStorage.setItem('zainpm-theme', this.isDark ? 'dark' : 'light')
      // Recreate chart to respect color alpha / theme differences
      this.$nextTick(() => this.initChart())
    },

    async fetchDashboardData() {
      this.loading = true
      this.error = null
      try {
        const user = authService.getCurrentUser()
        if (!user?.company_name) throw new Error('Missing company info')

        // Fetch projects
        const projectsResp = await projectService.getProjects(user.company_name)
        this.projects = projectsResp.projects || []

        // Fetch latest updates / tasks (backend endpoint returns updates/tasks)
        const updatesResp = await projectService.getLatestUpdates(user.company_name)
        // projectService.getLatestUpdates returns either { updates: [...] } or an array depending on backend
        this.tasks = Array.isArray(updatesResp) ? updatesResp : (updatesResp.updates || updatesResp || [])

        // Flatten members from projects (or rely on member API if you add one later)
        this.teamMembers = this.projects.flatMap(p => p.team || [])

        // Deadlines: take tasks that contain due_date / deadline fields
        this.deadlines = (this.tasks || []).filter(t => t.due_date || t.deadline || t.dueDate)
          .map(t => ({
            title: t.title || t.task_name || t.description || 'Untitled',
            dueDate: new Date(t.due_date || t.deadline || t.dueDate).toLocaleDateString(),
            project: t.project_name || t.project || 'Unassigned',
            status: this.computeDeadlineStatus(t.due_date || t.deadline || t.dueDate)
          }))

        // Stats
        const activeProjects = (this.projects.filter(p => (p.state || p.status || '').toLowerCase() === 'active')).length
        const totalTasks = (this.tasks || []).length
        const totalMembers = this.uniqueTeamMembers.length
        const completedTasks = (this.tasks || []).filter(t => (t.state || '').toLowerCase() === 'complete').length
        const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

        this.stats = [
          { label: 'Active Projects', value: activeProjects, color: 'var(--primary)' },
          { label: 'Total Tasks', value: totalTasks, color: 'var(--primary)' },
          { label: 'Team Members', value: totalMembers, color: 'var(--success)' },
          { label: 'Completion Rate', value: `${completionRate}%`, color: 'var(--warning)' }
        ]

        // ensure chart is created after DOM update
        this.$nextTick(() => this.initChart())
      } catch (err) {
        this.error = err.message || 'Failed to fetch dashboard data'
      } finally {
        this.loading = false
      }
    },

    computeDeadlineStatus(dueDate) {
      if (!dueDate) return 'Unknown'
      const now = new Date()
      const d = new Date(dueDate)
      const diff = (d - now) / (1000 * 60 * 60 * 24)
      if (diff < 0) return 'Overdue'
      if (diff <= 2) return `${Math.ceil(diff)} days left`
      return `${Math.ceil(diff)} days left`
    },

    initChart() {
      const canvas = this.$refs.chartCanvas
      if (!canvas) return

      // destroy previous instance
      if (this.chartInstance) {
        try { this.chartInstance.destroy() } catch (e) { /* ignore */ }
        this.chartInstance = null
      }

      const ctx = canvas.getContext('2d')
      // Compute counts by state (lowercase keys)
      const stateCounts = (this.projects || []).reduce((acc, p) => {
        const state = (p.state || p.status || 'unknown').toLowerCase()
        acc[state] = (acc[state] || 0) + 1
        return acc
      }, {})

      const labels = Object.keys(stateCounts)
      const data = Object.values(stateCounts)

      // Provide a consistent palette length — map labels to the palette in order
      const palette = [
        'rgba(108, 117, 125, 0.7)', // tentative / neutral
        'rgba(230, 57, 70, 0.7)',   // delayed / danger
        'rgba(73, 80, 246, 0.7)',   // in progress / primary
        'rgba(247, 37, 133, 0.7)',  // overdue
        'rgba(76, 201, 240, 0.7)'   // complete
      ]

      const bg = labels.map((_, i) => palette[i % palette.length])

      this.chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels,
          datasets: [{
            data,
            backgroundColor: bg,
            borderWidth: 0
          }]
        },
        options: {
          plugins: { legend: { display: false } },
          cutout: '60%'
        }
      })
    },

    formatDate(date) {
      if (!date) return 'N/A'
      try {
        const d = (date instanceof Date) ? date : new Date(date)
        return d.toLocaleDateString()
      } catch (e) {
        return String(date)
      }
    },

    formatDateKey(date) {
      if (!date) return ''
      try {
        const d = (date instanceof Date) ? date : new Date(date)
        return d.toISOString().slice(0, 10)
      } catch (e) {
        return String(date)
      }
    },

    priorityClass(priority) {
      if (!priority) return ''
      const p = String(priority).toLowerCase()
      if (p.includes('high')) return 'priority-high'
      if (p.includes('medium')) return 'priority-medium'
      return 'priority-low'
    }
  },

  mounted() {
    const saved = localStorage.getItem('zainpm-theme')
    this.isDark = saved ? saved === 'dark' : this.isDark
    this.fetchDashboardData()
  },

  beforeUnmount() {
    if (this.chartInstance) {
      try {
        this.chartInstance.destroy()
      } catch (e) {
        /* ignore destroy errors */
      }
      this.chartInstance = null
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  display: flex;
  height: 100vh;
  background-color: var(--bg-base);
  color: var(--text-primary);
  line-height: 1.6;
  top: 0;
}

.main-content {
  flex: 1;
  margin-left: 260px;
  padding: 20px;
  overflow-y: auto;
  height: 100%;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
}

.stat-card {
  background: var(--bg-section);
  border-radius: 10px;
  box-shadow: var(--shadow);
  padding: 20px;
  text-align: center;
  border: 1px solid var(--border-color);
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  margin: 10px 0;
  color: var(--primary);
}

.stat-label {
  color: var(--text-primary);
  font-size: 20px;
}

.state-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin: 20px 0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.task-item {
  padding: 15px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-primary);
}

.task-item:last-child {
  border-bottom: none;
}

.task-info {
  flex: 1;
}

.task-title {
  font-weight: 600;
  margin-bottom: 5px;
}

.task-meta {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: var(--text-secondary);
}

.priority-high {
  color: var(--danger);
  font-weight: 600;
}

.priority-medium {
  color: var(--warning);
  font-weight: 600;
}

.priority-low {
  color: var(--success);
  font-weight: 600;
}

.chart-container {
  height: 300px;
  position: relative;
}

.member-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.member-tag {
  background: rgba(0, 0, 0, 0.1);
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--text-primary);
}

@media (max-width: 992px) {
  .main-content {
    margin-left: 80px;
  }
}

@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>