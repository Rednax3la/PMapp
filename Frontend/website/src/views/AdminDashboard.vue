<template>
  <div class="admin-dashboard" :class="{ dark: isDark, light: !isDark }">
    <!-- Sidebar -->
    <div class="sidebar">
      <div class="logo">
        <img class="logo-img" src="../assets/Zain-clear2.png" alt="ZainPM Logo"/>
        <h1>ZainPM</h1>
      </div>
      <div class="nav-links">
        <div 
          v-for="item in navItems" 
          :key="item.target"
          class="nav-item" 
          :class="{ active: activeNav === item.target }"
          @click="setActiveNav(item.target)"
        >
          <i :class="item.icon"></i>
          <span>{{ item.label }}</span>
        </div>
      </div>
    </div>
    
    <!-- Main Content -->
    <div class="main-content">
      <div class="header">
        <h2>Dashboard</h2>
        <div class="header-actions">
          <button class="theme-toggle" @click="toggleTheme">
            <i :class="isDark ? 'fas fa-sun' : 'fas fa-moon'"></i>
            {{ isDark ? "Light Mode" : "Dark Mode" }}
          </button>
          <button class="btn btn-primary">
            <i class="fas fa-plus"></i> New Project
          </button>
          <button class="btn btn-success">
            <i class="fas fa-plus"></i> Add Task
          </button>
        </div>
      </div>
      
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
            <button class="btn btn-primary btn-sm">View All</button>
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
              <div class="state-badge" :class="project.statusClass">
                {{ project.status }}
              </div>
            </div>
          </div>
        </div>
        
        <!-- Recent Tasks -->
        <div class="card">
          <div class="card-header">
            <span>Recent Tasks</span>
            <button class="btn btn-primary btn-sm">View All</button>
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
              <div class="state-badge" :class="task.statusClass">
                {{ task.status }}
              </div>
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
              <div class="state-badge" :class="deadline.statusClass">
                {{ deadline.status }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch } from 'vue';
import Chart from 'chart.js/auto';
import { computed } from 'vue';

export default {
  setup() {
    // Theme Management
    const isDark = ref(true);
    const toggleTheme = () => {
      isDark.value = !isDark.value;
      localStorage.setItem("zainpm-theme", isDark.value ? "dark" : "light");
    };

    // Navigation
    const activeNav = ref('dashboard');
    const navItems = reactive([
      { target: 'dashboard', icon: 'fas fa-home', label: 'Dashboard' },
      { target: 'projects', icon: 'fas fa-project-diagram', label: 'Projects' },
      { target: 'tasks', icon: 'fas fa-tasks', label: 'Tasks' },
      { target: 'gantt', icon: 'fas fa-chart-bar', label: 'Gantt Chart' },
      { target: 'timetable', icon: 'fas fa-calendar-day', label: 'Timetable' },
      { target: 'reports', icon: 'fas fa-chart-pie', label: 'Reports' },
      { target: 'members', icon: 'fas fa-users', label: 'Team Members' },
      { target: 'settings', icon: 'fas fa-cog', label: 'Settings' },
      { target: 'help', icon: 'fas fa-question-circle', label: 'Help' },
      { target: 'logout', path: '/logout', icon: 'fas fa-sign-out-alt', label: 'Logout' }
    ]);
    
    const setActiveNav = (target) => {
      activeNav.value = target;
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
      // use a higher alpha in light mode for contrast
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
      { title: 'Website Redesign', dates: 'Jun 1 - Jul 15', tasks: '18 tasks', status: 'In Progress', statusClass: 'state-in-progress' },
      { title: 'Mobile App Development', dates: 'Jun 10 - Aug 5', tasks: '24 tasks', status: 'Tentative', statusClass: 'state-tentative' },
      { title: 'Marketing Campaign', dates: 'May 15 - Jun 30', tasks: '12 tasks', status: 'Overdue', statusClass: 'state-overdue' }
    ]);

    const tasks = reactive([
      { title: 'Design Homepage', dates: 'Jun 1 - Jun 5', priority: 'High Priority', priorityClass: 'priority-high', status: 'Complete', statusClass: 'state-complete' },
      { title: 'API Integration', dates: 'Jun 10 - Jun 15', priority: 'Medium Priority', priorityClass: 'priority-medium', status: 'Delayed', statusClass: 'state-delayed' },
      { title: 'User Testing', dates: 'Jun 5 - Jun 8', priority: 'Low Priority', priorityClass: 'priority-low', status: 'In Progress', statusClass: 'state-in-progress' },
      { title: 'Content Creation', dates: 'Jun 3 - Jun 7', priority: 'Medium Priority', priorityClass: 'priority-medium', status: 'Overdue', statusClass: 'state-overdue' }
    ]);

    const teamMembers = reactive([
      'Sarah Johnson', 'Michael Chen', 'Emma Rodriguez', 
      'David Kim', 'Priya Patel', 'James Wilson'
    ]);

    const deadlines = reactive([
      { title: 'Finalize Design Mockups', dueDate: 'Jun 12, 2023', project: 'Website Redesign', status: '2 days left', statusClass: 'state-in-progress' },
      { title: 'Backend API Completion', dueDate: 'Jun 15, 2023', project: 'Mobile App', status: '5 days left', statusClass: 'state-tentative' },
      { title: 'Marketing Plan Presentation', dueDate: 'Jun 8, 2023', project: 'Marketing Campaign', status: 'Overdue', statusClass: 'state-overdue' }
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
      activeNav,
      navItems,
      setActiveNav,
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

<style>
/* ZainPM Color Variables */
:root {
  --primary: #00fff7;
  --accent: #00e0ff;
  --highlight: #00ffb3;
  --dark-base: #0a0f1c;
  --soft-grid: #1e2f3a;
  --shadow-glow: #006b80;
  --success: #00ffb3;
  --warning: #ffb300;
  --danger: #ff0066;
  --info: #00e0ff;
  --light-gray: #e9ecef;
  --border: #1e2f3a;
  --shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  --sfinal:#03bde2;
}

/* Light mode — only main content & buttons, sidebar 100% untouched */
.light {
  /* MAIN BACKGROUNDS */
  --bg-base:        #d8e3e7;   /* soft pale cyan */
  --bg-section:     #bccdd1;   /* muted slate‑blue panels */
  /* TEXT */
  --text-primary:    #1e303b;  /* charcoal */
  --text-secondary:  #5f7a85;  /* muted slate */

  /* BORDERS & GRID */
  --border-color:    #798489;  /* gentle blue‑grey */
  --soft-grid:       #b4c7cc;  /* faint grid lines */

  /* CARD SURFACE & SHADOW */
  --card-bg:         #424647;  
  --card-shadow:     0 2px 8px rgba(0, 0, 0, 0.06);

  /* HOVER/ACTIVE STATES */
  --hover-bg:        rgba(0, 0, 0, 0.02);
  --active-bg:       rgba(0, 0, 0, 0.04);

  /* BUTTON & STATS ACCENTS */
  --primary:         #006b80;  /* deep teal‑blue */
  --success:         #227a5b;  /* muted emerald */
  --warning:         #d58c1a;  /* warm amber */
  --danger:          #3080b3;  /* shift red → cobalt blue */
  --info:            #3399cc;  /* sky blue */

  /* STATE BADGES (if you want blue for “delayed” etc, override here too) */
  --state-tentative:   #95a5a6;
  --state-delayed:     #3080b3;  /* delayed now blueish */
  --state-in-progress: #006b80;
  --state-overdue:     #3399cc;
  --state-complete:    #227a5b;
}

/* 1) Make calendar icons & date text black for visibility */
.light .task-meta span,
.light .task-meta span i.far.fa-calendar {
  color: #000 !important;
}

/* 2) Force stats card labels (“Active Projects”, etc.) to pure black */
.light .stat-label {
  color: #000 !important;
}

/* 3) Button text brighter—use white */
.light .btn-primary,
.light .btn-success,
.light button.btn-sm {
  color: #fff !important;
}

/* 4) Darken the ‘In Progress’ and “2 days left” badges */
.light .state-in-progress {
  /* darker-blue background, less neon */
  background: rgba(0, 107, 128, 0.2) !important; 
  color: #006b80 !important;
}

/* 5) (Optional) if you have other “priority” or “badge” classes still neon, tweak similarly */
.light .priority-high,
.light .priority-medium,
.light .priority-low {
  /* example: make all priorities the same dark tone */
  color: #003f54 !important;
}

/* 6) Make legend labels darker for contrast */
.light .state-legend span {
  color: #32414d;  /* darker slate than var(--text-secondary) */
}

.light .logo h1 {
  color: var(--accent);
}

.dark {
  --bg-base: var(--dark-base);
  --bg-section: var(--soft-grid);
  --text-primary: #ffffff;
  --text-secondary: rgba(255, 255, 255, 0.7);
  --border-color: var(--shadow-glow);
}

/* 1) Match dates, calendar icon & “X days left” to team‑member text colour */
.light .task-meta span,
.light .task-meta span i.far.fa-calendar,
.light .state-tentative { 
  color: var(--text-primary) !important; 
}

/* 2) Stat‑card labels same as team‑member text */
.light .stat-label {
  color: var(--text-primary) !important;
}

/* 3) Legend labels a bit darker for contrast */
.light .state-legend span {
  color: #32414d;  /* darker slate than var(--text-secondary) */
}

/* 4) Buttons keep white text */
.light .btn-primary,
.light .btn-success,
.light button.btn-sm {
  color: #fff !important;
}


* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

template, body {
  overflow: hidden;
}

.admin-dashboard {
  display: flex;
  height: 100vh;
  background-color: var(--bg-base);
  color: var(--text-primary);
  line-height: 1.6;
  top: 0;
}

.logo h1{
  font-weight: 600;
  color: var(--accent);
  font-size: 3rem;
}

.sidebar {
  width: 260px;
  background: linear-gradient(180deg, var(--shadow-glow), var(--sfinal))!important;
  color: white;
  padding: 20px 0;
  position: fixed;
  height: 100vh;
  overflow-y: auto;
  z-index: 100;
  box-shadow: var(--shadow);
}

.logo {
  display: flex;
  align-items: center;
  padding: 0 20px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 1rem;
  max-width: 100%;
}

.logo-img {
  width: 67px;
  height: 67px;
  align-items: center;
  object-fit: contain;
  margin-right: 12px;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: block;
}

.nav-links {
  padding: 20px 0;
}

.nav-item {
  padding: 12px 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: rgba(248, 247, 247, 0.9);
}

.nav-item:hover, .nav-item.active {
  background: rgba(255, 255, 255, 0.1);
  border-left: 4px solid var(--highlight);
  color: white;
}

.nav-item i {
  margin-right: 12px;
  font-size: 18px;
}

/* Main Content */
.main-content {
  flex: 1;
  margin-left: 260px;
  padding: 20px;
  overflow-y: auto;
  height: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border-color);
}

.header h2 {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: 15px;
}

.btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  background: var(--primary);
  color: var(--dark-base);
}

.btn-success {
  background: var(--success);
  color: var(--dark-base);
}

.btn-warning {
  background: var(--warning);
  color: var(--dark-base);
}

.btn:hover {
  opacity: 0.9;
  transform: translateY(-2px);
}

.card {
  background: var(--bg-section);
  border-radius: 10px;
  box-shadow: var(--shadow);
  margin-bottom: 25px;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.card-header {
  padding: 15px 20px;
  background: rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid var(--border-color);
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-primary);
}

.card-body {
  padding: 15px 20px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.state-badge {
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  display: inline-block;
}

.state-tentative {
  background: rgba(108, 117, 125, 0.2);
  color: var(--text-secondary);
}

.state-delayed {
  background: rgba(230, 57, 70, 0.2);
  color: var(--danger);
}

.state-in-progress {
  background: rgba(73, 80, 246, 0.2);
  color: var(--accent);
}

.state-overdue {
  background: rgba(247, 37, 133, 0.2);
  color: var(--warning);
}

.state-complete {
  background: rgba(76, 201, 240, 0.2);
  color: var(--success);
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

.theme-toggle {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.theme-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
}

@media (max-width: 992px) {
  .sidebar {
    width: 80px;
  }
  .sidebar .logo h1, .sidebar .nav-item span {
    display: none;
  }
  .sidebar .logo {
    justify-content: center;
    padding: 20px 0;
  }
  .sidebar .logo-img {
    margin-right: 0;
  }
  .sidebar .nav-item {
    justify-content: center;
  }
  .sidebar .nav-item i {
    margin-right: 0;
    font-size: 20px;
  }
  .main-content {
    margin-left: 80px;
  }
}

@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  .btn {
    flex: 1;
    min-width: 120px;
  }
}
</style>