//Frontend/website/src/views/Reports.vue
<template>
  <div class="reports-page" :class="{ dark: isDark, light: !isDark }">
    <!-- Sidebar -->
    <Sidebar :active-nav="activeNav" @nav-change="setActiveNav" />
    
    <!-- Main Content -->
    <div class="main-content">
      <AppHeader title="Reports">
        <template #actions>
          <ThemeToggle :is-dark="isDark" @toggle="toggleTheme" />
          <AppButton variant="primary" icon="fas fa-download">
            Export Reports
          </AppButton>
        </template>
      </AppHeader>
      
      <!-- Key Metrics -->
      <div class="metrics-grid">
        <div class="metric-card" v-for="metric in keyMetrics" :key="metric.label">
          <div class="metric-icon">
            <i :class="metric.icon"></i>
          </div>
          <div class="metric-content">
            <div class="metric-value">{{ metric.value }}</div>
            <div class="metric-label">{{ metric.label }}</div>
            <div class="metric-change" :class="metric.changeClass">
              <i :class="metric.changeIcon"></i>
              {{ metric.change }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- Charts Section -->
      <div class="charts-section">
        <!-- Project Progress Chart -->
        <div class="chart-card">
          <div class="card-header">
            <h3>Project Progress Overview</h3>
            <div class="chart-controls">
              <button 
                v-for="period in chartPeriods" 
                :key="period"
                :class="['period-btn', { active: activePeriod === period }]"
                @click="activePeriod = period"
              >
                {{ period }}
              </button>
            </div>
          </div>
          <div class="chart-container">
            <canvas ref="progressChart"></canvas>
          </div>
        </div>
        
        <!-- Task Distribution Chart -->
        <div class="chart-card">
          <div class="card-header">
            <h3>Task Status Distribution</h3>
          </div>
          <div class="chart-container">
            <canvas ref="distributionChart"></canvas>
          </div>
        </div>
        
        <!-- Team Performance Chart -->
        <div class="chart-card">
          <div class="card-header">
            <h3>Team Performance</h3>
          </div>
          <div class="chart-container">
            <canvas ref="performanceChart"></canvas>
          </div>
        </div>
        
        <!-- Timeline Chart -->
        <div class="chart-card full-width">
          <div class="card-header">
            <h3>Project Timeline</h3>
          </div>
          <div class="chart-container">
            <canvas ref="timelineChart"></canvas>
          </div>
        </div>
      </div>
      
      <!-- Report Filters -->
      <div class="filters-section">
        <div class="filter-group">
          <label>Date Range:</label>
          <div class="date-range">
            <input type="date" v-model="startDate" class="date-input">
            <span>to</span>
            <input type="date" v-model="endDate" class="date-input">
          </div>
        </div>
        
        <div class="filter-group">
          <label>Project:</label>
          <select v-model="selectedProject" class="filter-select">
            <option value="">All Projects</option>
            <option v-for="project in projects" :key="project" :value="project">
              {{ project }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Team Member:</label>
          <select v-model="selectedMember" class="filter-select">
            <option value="">All Members</option>
            <option v-for="member in teamMembers" :key="member" :value="member">
              {{ member }}
            </option>
          </select>
        </div>
      </div>

      <!-- Detailed Reports Table -->
      <div class="table-section">
        <div class="card">
          <div class="card-header">
            <h3>Detailed Project Reports</h3>
            <div class="table-controls">
              <div class="search-box">
                <i class="fas fa-search"></i>
                <input 
                  type="text" 
                  v-model="searchQuery" 
                  placeholder="Search reports..."
                >
              </div>
            </div>
          </div>
          
          <div class="table-container">
            <table class="reports-table">
              <thead>
                <tr>
                  <th @click="sortBy('project')">
                    Project
                    <i class="fas fa-sort"></i>
                  </th>
                  <th @click="sortBy('progress')">
                    Progress
                    <i class="fas fa-sort"></i>
                  </th>
                  <th @click="sortBy('tasks')">
                    Tasks
                    <i class="fas fa-sort"></i>
                  </th>
                  <th @click="sortBy('budget')">
                    Budget
                    <i class="fas fa-sort"></i>
                  </th>
                  <th @click="sortBy('spent')">
                    Spent
                    <i class="fas fa-sort"></i>
                  </th>
                  <th @click="sortBy('efficiency')">
                    Efficiency
                    <i class="fas fa-sort"></i>
                  </th>
                  <th @click="sortBy('deadline')">
                    Deadline
                    <i class="fas fa-sort"></i>
                  </th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="report in filteredReports" :key="report.id">
                  <td class="project-cell">
                    <div class="project-info">
                      <div class="project-name">{{ report.project }}</div>
                      <div class="project-lead">{{ report.lead }}</div>
                    </div>
                  </td>
                  <td>
                    <div class="progress-cell">
                      <div class="progress-bar">
                        <div 
                          class="progress-fill" 
                          :style="{ width: report.progress + '%', background: getProgressColor(report.progress) }"
                        ></div>
                      </div>
                      <span class="progress-text">{{ report.progress }}%</span>
                    </div>
                  </td>
                  <td>
                    <div class="tasks-cell">
                      <span class="completed">{{ report.completedTasks }}</span>
                      /
                      <span class="total">{{ report.totalTasks }}</span>
                    </div>
                  </td>
                  <td class="budget-cell">${{ formatNumber(report.budget) }}</td>
                  <td class="spent-cell">${{ formatNumber(report.spent) }}</td>
                  <td>
                    <div class="efficiency-cell" :class="getEfficiencyClass(report.efficiency)">
                      {{ report.efficiency }}%
                    </div>
                  </td>
                  <td class="deadline-cell">{{ formatDate(report.deadline) }}</td>
                  <td>
                    <StateBadge :status="report.status" />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Sidebar from '@/components/layout/Sidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import { projectService } from '@/services/projects'
import { authService } from '@/services/auth'

export default {
  name: 'ReportsPage',
  components: { Sidebar, AppHeader, ThemeToggle },

  data() {
    return {
      // Theme
      isDark: true,

      // Data
      reports: [],
      projects: [],

      // State
      loading: false,
      error: null,

      // Filters
      selectedProject: '',
      filters: {
        dateRange: null,
        status: 'all'
      }
    }
  },

  computed: {
    filteredReports() {
      let results = this.reports.slice()

      // filter by project
      if (this.selectedProject) {
        results = results.filter(r => r.project === this.selectedProject)
      }

      // filter by status
      if (this.filters.status !== 'all') {
        results = results.filter(r => r.status === this.filters.status)
      }

      // filter by date range
      if (this.filters.dateRange && this.filters.dateRange.length === 2) {
        const [start, end] = this.filters.dateRange
        const startDate = new Date(start)
        const endDate = new Date(end)
        results = results.filter(r => {
          const d = new Date(r.date)
          return d >= startDate && d <= endDate
        })
      }

      return results
    }
  },

  methods: {
    toggleTheme() {
      this.isDark = !this.isDark
      localStorage.setItem('zainpm-theme', this.isDark ? 'dark' : 'light')
    },

    async fetchProjects() {
      try {
        const user = authService.getCurrentUser()
        if (!user?.company_name) throw new Error('Missing company information')
        this.projects = await projectService.getProjects(user.company_name)
      } catch (err) {
        this.error = err.message || 'Failed to fetch projects'
      }
    },

    async fetchReports() {
      this.loading = true
      this.error = null
      try {
        const user = authService.getCurrentUser()
        if (!user?.company_name) throw new Error('Missing company information')
        // latest updates serve as reports
        this.reports = await projectService.getLatestUpdates(user.company_name)
      } catch (err) {
        this.error = err.message || 'Failed to fetch reports'
      } finally {
        this.loading = false
      }
    },

    applyFilters() {
      // no-op: computed handles it
    },

    formatDate(d) {
      return d ? new Date(d).toLocaleDateString() : 'N/A'
    }
  },

  mounted() {
    const saved = localStorage.getItem('zainpm-theme')
    this.isDark = saved ? saved === 'dark' : this.isDark
    this.fetchProjects()
    this.fetchReports()
  }
}
</script>

<style scoped>
@import '@/assets/css/main.css';

.reports-page {
  display: flex;
  height: 100vh;
  background-color: var(--bg-base);
  color: var(--text-primary);
  line-height: 1.6;
}

.filters-section {
  display: flex;
  gap: 20px;
  margin-bottom: 25px;
  padding: 20px;
  background: var(--bg-section);
  border-radius: 10px;
  border: 1px solid var(--border-color);
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-group label {
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
}

.date-range {
  display: flex;
  align-items: center;
  gap: 10px;
}

.date-input,
.filter-select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-base);
  color: var(--text-primary);
  font-size: 14px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  background: var(--bg-section);
  border-radius: 10px;
  padding: 20px;
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 15px;
}

.metric-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  background: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: var(--dark-base);
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 5px;
}

.metric-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 5px;
}

.metric-change {
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 5px;
}

.metric-change.positive {
  color: var(--success);
}

.metric-change.negative {
  color: var(--danger);
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.chart-card {
  background: var(--bg-section);
  border-radius: 10px;
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.chart-card.full-width {
  grid-column: 1 / -1;
}

.card-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.05);
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.chart-controls {
  display: flex;
  gap: 5px;
}

.period-btn {
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
}

.period-btn:hover,
.period-btn.active {
  background: var(--primary);
  color: var(--dark-base);
  border-color: var(--primary);
}

.chart-container {
  padding: 20px;
  height: 300px;
  position: relative;
}

.table-section {
  margin-bottom: 30px;
}

.table-controls {
  display: flex;
  justify-content: flex-end;
}

.search-box {
  position: relative;
  width: 300px;
}

.search-box i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
}

.search-box input {
  width: 100%;
  padding: 8px 20px 8px 35px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-base);
  color: var(--text-primary);
  font-size: 14px;
}

.table-container {
  overflow-x: auto;
}

.reports-table {
  width: 100%;
  border-collapse: collapse;
}

.reports-table th {
  padding: 15px 12px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid var(--border-color);
  background: rgba(0, 0, 0, 0.05);
  cursor: pointer;
  user-select: none;
  position: relative;
}

.reports-table th:hover {
  background: rgba(0, 0, 0, 0.1);
}

.reports-table th i {
  margin-left: 5px;
  opacity: 0.5;
}

.reports-table td {
  padding: 15px 12px;
  border-bottom: 1px solid var(--border-color);
}

.project-cell {
  min-width: 180px;
}

.project-name {
  font-weight: 600;
  margin-bottom: 2px;
}

.project-lead {
  font-size: 12px;
  color: var(--text-secondary);
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 120px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  font-weight: 600;
  min-width: 35px;
}

.tasks-cell {
  font-weight: 600;
}

.tasks-cell .completed {
  color: var(--success);
}

.tasks-cell .total {
  color: var(--text-secondary);
}

.budget-cell,
.spent-cell {
  font-weight: 600;
  color: var(--text-primary);
}

.efficiency-cell {
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 12px;
  text-align: center;
}

.efficiency-cell.excellent {
  background: rgba(0, 255, 179, 0.2);
  color: var(--success);
}

.efficiency-cell.good {
  background: rgba(0, 255, 247, 0.2);
  color: var(--primary);
}

.efficiency-cell.average {
  background: rgba(255, 179, 0, 0.2);
  color: var(--warning);
}

.efficiency-cell.poor {
  background: rgba(255, 0, 102, 0.2);
  color: var(--danger);
}

.deadline-cell {
  white-space: nowrap;
}

@media (max-width: 992px) {
  .filters-section {
    flex-direction: column;
  }
  
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .search-box {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .metric-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>