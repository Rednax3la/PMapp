<template>
  <div class="admin-dashboard" :class="{ dark: isDark, light: !isDark }">  
    <!-- Sidebar -->
    <Sidebar />
    
    <!-- Main Content -->
    <div class="main-content">
      <AppHeader title="Dashboard">
        <template #actions>
          <ThemeToggle :is-dark="isDark" @toggle="toggleTheme" />
          <AppButton variant="primary" icon="fas fa-plus">
            New Project
          </AppButton>
          <AppButton variant="success" icon="fas fa-plus">
            Add Task
          </AppButton>
        </template>
      </AppHeader>
      
      <!-- Stats Overview -->
      <div class="stats-grid">
        <div class="stat-card" v-for="stat in stats" :key="stat.label">
          <div class="stat-label">{{ stat.label }}</div>
          <div class="stat-value">{{ stat.value }}</div>
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
              :key="project.title"
            >
              <div class="task-info">
                <div class="task-title">{{ project.title }}</div>
                <div class="task-meta">
                  <span><i class="far fa-calendar"></i> {{ project.dates }}</span>
                  <span><i class="fas fa-tasks"></i> {{ project.tasks }}</span>
                </div>
              </div>
              <StateBadge :status="project.status" />
            </div>
          </div>
        </div>
        
        <!-- Recent Tasks -->
        <div class="card">
          <div class="card-header">
            <span>Recent Tasks</span>
            <AppButton variant="primary" size="small">View All</AppButton>
          </div>
          <div class="card-body">
            <div 
              class="task-item" 
              v-for="task in tasks" 
              :key="task.title"
            >
              <div class="task-info">
                <div class="task-title">{{ task.title }}</div>
                <div class="task-meta">
                  <span><i class="far fa-calendar"></i> {{ task.dates }}</span>
                  <span :class="task.priorityClass">{{ task.priority }}</span>
                </div>
              </div>
              <StateBadge :status="task.status" />
            </div>
          </div>
        </div>
        
        <!-- Task Status Distribution -->
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
              <div 
                class="member-tag" 
                v-for="member in teamMembers" 
                :key="member"
              >
                <i class="fas fa-user"></i> {{ member }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Upcoming Deadlines -->
      <div class="card">
        <div class="card-header">
          <span>Upcoming Deadlines</span>
        </div>
        <div class="card-body">
          <div class="grid">
            <div 
              class="task-item" 
              v-for="deadline in deadlines" 
              :key="deadline.title"
            >
              <div class="task-info">
                <div class="task-title">{{ deadline.title }}</div>
                <div class="task-meta">
                  <span><i class="far fa-calendar"></i> Due: {{ deadline.dueDate }}</span>
                  <span>Project: {{ deadline.project }}</span>
                </div>
              </div>
              <StateBadge :status="deadline.status" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch, computed } from 'vue';
import Chart from 'chart.js/auto';
import Sidebar from '@/components/layout/Sidebar.vue';
import AppHeader from '@/components/layout/AppHeader.vue';
import ThemeToggle from '@/components/layout/ThemeToggle.vue';
import AppButton from '@/components/ui/AppButton.vue';
import StateBadge from '@/components/ui/StateBadge.vue';

export default {
  name: 'AdminDashboard',
  components: {
    Sidebar,
    AppHeader, 
    ThemeToggle,
    AppButton,
    StateBadge
  },
  setup() {
    // Theme Management
    const isDark = ref(true);
    const toggleTheme = () => {
      isDark.value = !isDark.value;
      localStorage.setItem("zainpm-theme", isDark.value ? "dark" : "light");
    };

    // Stats Data
    const stats = reactive([
      { label: 'Active Projects', value: '12', color: 'var(--primary)' },
      { label: 'Total Tasks', value: '84', color: 'var(--primary)' },
      { label: 'Team Members', value: '23', color: 'var(--success)' },
      { label: 'Completion Rate', value: '42%', color: 'var(--warning)' }
    ]);

    // Legend Items
    const legendItems = computed(() => {
      const a = isDark.value ? 0.2 : 0.5;
      return [
        { label: 'Tentative',    color: `rgba(108, 117, 125, ${a})` },
        { label: 'Delayed',      color: `rgba(230, 57,   70,  ${a})` },
        { label: 'In Progress',  color: `rgba(73,  80,  246, ${a})` },
        { label: 'Overdue',      color: `rgba(247, 37,  133, ${a})` },
        { label: 'Complete',     color: `rgba(76,  201, 240, ${a})` }
      ];
    });

    // Sample Data
    const projects = reactive([
      { title: 'Website Redesign', dates: 'Jun 1 - Jul 15', tasks: '18 tasks', status: 'In Progress' },
      { title: 'Mobile App Development', dates: 'Jun 10 - Aug 5', tasks: '24 tasks', status: 'Tentative' },
      { title: 'Marketing Campaign', dates: 'May 15 - Jun 30', tasks: '12 tasks', status: 'Overdue' }
    ]);

    const tasks = reactive([
      { title: 'Design Homepage', dates: 'Jun 1 - Jun 5', priority: 'High Priority', priorityClass: 'priority-high', status: 'Complete' },
      { title: 'API Integration', dates: 'Jun 10 - Jun 15', priority: 'Medium Priority', priorityClass: 'priority-medium', status: 'Delayed' },
      { title: 'User Testing', dates: 'Jun 5 - Jun 8', priority: 'Low Priority', priorityClass: 'priority-low', status: 'In Progress' },
      { title: 'Content Creation', dates: 'Jun 3 - Jun 7', priority: 'Medium Priority', priorityClass: 'priority-medium', status: 'Overdue' }
    ]);

    const teamMembers = reactive([
      'Sarah Johnson', 'Michael Chen', 'Emma Rodriguez', 
      'David Kim', 'Priya Patel', 'James Wilson'
    ]);

    const deadlines = reactive([
      { title: 'Finalize Design Mockups', dueDate: 'Jun 12, 2023', project: 'Website Redesign', status: '2 days left' },
      { title: 'Backend API Completion', dueDate: 'Jun 15, 2023', project: 'Mobile App', status: '5 days left' },
      { title: 'Marketing Plan Presentation', dueDate: 'Jun 8, 2023', project: 'Marketing Campaign', status: 'Overdue' }
    ]);

    // Chart Logic
    const chartCanvas = ref(null);
    let chartInstance = null;

    const initChart = () => {
      if (chartInstance) {
        chartInstance.destroy();
      }
      
      const ctx = chartCanvas.value.getContext('2d');
      chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Tentative', 'Delayed', 'In Progress', 'Overdue', 'Complete'],
          datasets: [{
            data: [15, 10, 30, 8, 37],
            backgroundColor: [
              'rgba(108, 117, 125, 0.7)',
              'rgba(230, 57, 70, 0.7)',
              'rgba(73, 80, 246, 0.7)',
              'rgba(247, 37, 133, 0.7)',
              'rgba(76, 201, 240, 0.7)'
            ],
            borderColor: [
              'rgba(108, 117, 125, 1)',
              'rgba(230, 57, 70, 1)',
              'rgba(73, 80, 246, 1)',
              'rgba(247, 37, 133, 1)',
              'rgba(76, 201, 240, 1)'
            ],
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right',
              labels: {
                color: isDark.value ? '#ffffff' : '#102530'
              }
            },
            tooltip: {
              callbacks: {
                label: function(context) {
                  return `${context.label}: ${context.parsed}%`;
                }
              }
            }
          }
        }
      });
    };

    onMounted(() => {
      // Load theme preference
      const savedTheme = localStorage.getItem("zainpm-theme");
      if (savedTheme === "light") {
        isDark.value = false;
      }
      
      // Initialize chart
      initChart();
    });

    // Update chart when theme changes
    watch(isDark, () => {
      initChart();
    });

    return {
      isDark,
      toggleTheme,
      stats,
      legendItems,
      projects,
      tasks,
      teamMembers,
      deadlines,
      chartCanvas
    };
  }
};
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