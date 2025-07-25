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
import { ref, computed, onMounted, watch } from 'vue';
import { format } from 'date-fns';
import Chart from 'chart.js/auto';
import Sidebar from '@/components/layout/Sidebar.vue';
import AppHeader from '@/components/layout/AppHeader.vue';
import ThemeToggle from '@/components/layout/ThemeToggle.vue';
import StateBadge from '@/components/ui/StateBadge.vue';
import AppButton from '@/components/ui/AppButton.vue';

export default {
  name: 'ReportsPage',
  components: {
    Sidebar,
    AppHeader,
    ThemeToggle,
    StateBadge,
    AppButton
  },
  setup() {
    // Theme Management
    const isDark = ref(true);
    const toggleTheme = () => {
      isDark.value = !isDark.value;
      localStorage.setItem("zainpm-theme", isDark.value ? "dark" : "light");
    };

    // Navigation
    const activeNav = ref('reports');
    const setActiveNav = (target) => {
      activeNav.value = target;
    };

    // Filter State
    const startDate = ref(format(new Date(2023, 4, 1), 'yyyy-MM-dd'));
    const endDate = ref(format(new Date(), 'yyyy-MM-dd'));
    const selectedProject = ref('');
    const selectedMember = ref('');
    const searchQuery = ref('');
    const activePeriod = ref('Month');

    // Data
    const projects = ref([
      'Website Redesign', 'Mobile App', 'Marketing Campaign', 
      'API Integration', 'Database Migration'
    ]);

    const teamMembers = ref([
      'Sarah Johnson', 'Michael Chen', 'Emma Rodriguez', 
      'David Kim', 'Priya Patel', 'James Wilson'
    ]);

    const chartPeriods = ref(['Week', 'Month', 'Quarter', 'Year']);

    const keyMetrics = ref([
      {
        label: 'Active Projects',
        value: '12',
        change: '+2 from last month',
        changeClass: 'positive',
        changeIcon: 'fas fa-arrow-up',
        icon: 'fas fa-project-diagram'
      },
      {
        label: 'Completion Rate',
        value: '68%',
        change: '+5% from last month',
        changeClass: 'positive',
        changeIcon: 'fas fa-arrow-up',
        icon: 'fas fa-chart-line'
      },
      {
        label: 'Budget Utilization',
        value: '72%',
        change: '-3% from last month',
        changeClass: 'negative',
        changeIcon: 'fas fa-arrow-down',
        icon: 'fas fa-dollar-sign'
      },
      {
        label: 'Team Efficiency',
        value: '89%',
        change: '+7% from last month',
        changeClass: 'positive',
        changeIcon: 'fas fa-arrow-up',
        icon: 'fas fa-users'
      }
    ]);

    const reportData = ref([
      {
        id: 1,
        project: 'Website Redesign',
        lead: 'Sarah Johnson',
        progress: 75,
        completedTasks: 15,
        totalTasks: 20,
        budget: 25000,
        spent: 18750,
        efficiency: 92,
        deadline: new Date(2023, 6, 15),
        status: 'In Progress'
      },
      {
        id: 2,
        project: 'Mobile App',
        lead: 'David Kim',
        progress: 45,
        completedTasks: 9,
        totalTasks: 20,
        budget: 40000,
        spent: 22000,
        efficiency: 78,
        deadline: new Date(2023, 7, 30),
        status: 'In Progress'
      },
      {
        id: 3,
        project: 'Marketing Campaign',
        lead: 'Emma Rodriguez',
        progress: 90,
        completedTasks: 18,
        totalTasks: 20,
        budget: 15000,
        spent: 14200,
        efficiency: 95,
        deadline: new Date(2023, 5, 30),
        status: 'Nearly Complete'
      },
      {
        id: 4,
        project: 'API Integration',
        lead: 'Michael Chen',
        progress: 30,
        completedTasks: 6,
        totalTasks: 20,
        budget: 20000,
        spent: 8000,
        efficiency: 85,
        deadline: new Date(2023, 8, 15),
        status: 'In Progress'
      },
      {
        id: 5,
        project: 'Database Migration',
        lead: 'Priya Patel',
        progress: 60,
        completedTasks: 12,
        totalTasks: 20,
        budget: 30000,
        spent: 19500,
        efficiency: 88,
        deadline: new Date(2023, 7, 10),
        status: 'In Progress'
      }
    ]);

    // Chart Refs
    const progressChart = ref(null);
    const distributionChart = ref(null);
    const performanceChart = ref(null);
    const timelineChart = ref(null);

    let chartInstances = {};

    // Computed Properties
    const filteredReports = computed(() => {
      let result = [...reportData.value];
      
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        result = result.filter(r => 
          r.project.toLowerCase().includes(query) || 
          r.lead.toLowerCase().includes(query)
        );
      }
      
      if (selectedProject.value) {
        result = result.filter(r => r.project === selectedProject.value);
      }
      
      if (selectedMember.value) {
        result = result.filter(r => r.lead === selectedMember.value);
      }
      
      return result;
    });

    // Helper Functions
    const formatNumber = (num) => {
      return new Intl.NumberFormat().format(num);
    };

    const formatDate = (date) => {
      return format(date, 'MMM d, yyyy');
    };

    const getProgressColor = (progress) => {
      if (progress >= 80) return 'var(--success)';
      if (progress >= 60) return 'var(--primary)';
      if (progress >= 40) return 'var(--warning)';
      return 'var(--danger)';
    };

    const getEfficiencyClass = (efficiency) => {
      if (efficiency >= 90) return 'excellent';
      if (efficiency >= 80) return 'good';
      if (efficiency >= 70) return 'average';
      return 'poor';
    };

    const sortBy = (field) => {
      console.log('Sorting by:', field);
      // Implementation for table sorting
    };

    // Chart Initialization
    const initCharts = () => {
      // Destroy existing charts
      Object.values(chartInstances).forEach(chart => {
        if (chart) chart.destroy();
      });

      const textColor = isDark.value ? '#ffffff' : '#102530';
      const gridColor = isDark.value ? '#1e2f3a' : '#c7e3ec';

      // Progress Chart
      if (progressChart.value) {
        chartInstances.progress = new Chart(progressChart.value, {
          type: 'line',
          data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
              label: 'Project Progress',
              data: [20, 35, 45, 60, 70, 75],
              borderColor: 'var(--primary)',
              backgroundColor: 'rgba(0, 255, 247, 0.1)',
              tension: 0.4,
              fill: true
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { labels: { color: textColor } }
            },
            scales: {
              x: { 
                ticks: { color: textColor },
                grid: { color: gridColor }
              },
              y: { 
                ticks: { color: textColor },
                grid: { color: gridColor }
              }
            }
          }
        });
      }

      // Distribution Chart
      if (distributionChart.value) {
        chartInstances.distribution = new Chart(distributionChart.value, {
          type: 'doughnut',
          data: {
            labels: ['Complete', 'In Progress', 'Delayed', 'Not Started'],
            datasets: [{
              data: [45, 30, 15, 10],
              backgroundColor: [
                'var(--success)',
                'var(--primary)',
                'var(--warning)',
                'var(--danger)'
              ]
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { 
                position: 'right',
                labels: { color: textColor }
              }
            }
          }
        });
      }

      // Performance Chart
      if (performanceChart.value) {
        chartInstances.performance = new Chart(performanceChart.value, {
          type: 'bar',
          data: {
            labels: teamMembers.value.slice(0, 5),
            datasets: [{
              label: 'Tasks Completed',
              data: [12, 19, 8, 15, 10],
              backgroundColor: 'var(--accent)',
              borderColor: 'var(--primary)',
              borderWidth: 1
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { labels: { color: textColor } }
            },
            scales: {
              x: { 
                ticks: { color: textColor },
                grid: { color: gridColor }
              },
              y: { 
                ticks: { color: textColor },
                grid: { color: gridColor }
              }
            }
          }
        });
      }

      // Timeline Chart
      if (timelineChart.value) {
        chartInstances.timeline = new Chart(timelineChart.value, {
          type: 'bar',
          data: {
            labels: projects.value,
            datasets: [{
              label: 'Planned',
              data: [100, 100, 100, 100, 100],
              backgroundColor: 'rgba(108, 117, 125, 0.3)'
            }, {
              label: 'Actual',
              data: [75, 45, 90, 30, 60],
              backgroundColor: 'var(--primary)'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
              legend: { labels: { color: textColor } }
            },
            scales: {
              x: { 
                ticks: { color: textColor },
                grid: { color: gridColor }
              },
              y: { 
                ticks: { color: textColor },
                grid: { color: gridColor }
              }
            }
          }
        });
      }
    };

    onMounted(() => {
      const savedTheme = localStorage.getItem("zainpm-theme");
      if (savedTheme === "light") {
        isDark.value = false;
      }
      
      setTimeout(initCharts, 100);
    });

    watch(isDark, () => {
      setTimeout(initCharts, 100);
    });

    return {
      isDark,
      toggleTheme,
      activeNav,
      setActiveNav,
      startDate,
      endDate,
      selectedProject,
      selectedMember,
      searchQuery,
      activePeriod,
      projects,
      teamMembers,
      chartPeriods,
      keyMetrics,
      reportData,
      filteredReports,
      progressChart,
      distributionChart,
      performanceChart,
      timelineChart,
      formatNumber,
      formatDate,
      getProgressColor,
      getEfficiencyClass,
      sortBy
    };
  }
};
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