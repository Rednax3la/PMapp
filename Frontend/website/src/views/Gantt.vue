//Frontend/website/src/views/Gantt.vue
<template>
  <div class="gantt-page" :class="{ dark: isDark, light: !isDark }">
    <!-- Sidebar -->
    <Sidebar :active-nav="activeNav" @nav-change="setActiveNav" />
    
    <!-- Main Content -->
    <div class="main-content">
      <AppHeader title="Gantt Chart">
        <template #actions>
          <ThemeToggle :is-dark="isDark" @toggle="toggleTheme" />
          <AppButton variant="primary" icon="fas fa-plus">
            Add Task
          </AppButton>
          <AppButton variant="secondary" icon="fas fa-download">
            Export Chart
          </AppButton>
        </template>
      </AppHeader>
      
      <!-- Chart Controls -->
      <div class="chart-controls">
        <div class="control-group">
          <select v-model="selectedProject" @change="loadGanttData" class="control-select">
            <option value="">Select Project</option>
            <option v-for="project in projects" :key="project.id" :value="project.name">
              {{ project.name }}
            </option>
          </select>
          
          <div class="view-toggle">
            <button 
              v-for="view in viewOptions" 
              :key="view" 
              :class="['toggle-btn', { active: currentView === view }]"
              @click="currentView = view"
            >
              {{ view }}
            </button>
          </div>
        </div>
        
        <div class="date-controls">
          <div class="date-inputs">
            <input 
              type="date" 
              v-model="startDate" 
              class="date-input"
              @change="updateDateRange"
            >
            <span class="date-separator">to</span>
            <input 
              type="date" 
              v-model="endDate" 
              class="date-input"
              @change="updateDateRange"
            >
          </div>
          <AppButton variant="outline" @click="resetToCurrentMonth" class="btn-sm">
            Current Month
          </AppButton>
        </div>
      </div>
      
      <!-- Loading State -->
      <div v-if="loading" class="state-card loading">
        <div class="state-content">
          <i class="fas fa-spinner fa-spin state-icon"></i>
          <p>Loading Gantt chart...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-if="error && !loading" class="state-card error">
        <div class="state-content">
          <i class="fas fa-exclamation-triangle state-icon"></i>
          <p>{{ error }}</p>
          <AppButton @click="loadGanttData" variant="primary" class="btn-sm">
            Retry
          </AppButton>
        </div>
      </div>

      <!-- Gantt Chart -->
      <div v-if="!loading && !error && selectedProject" class="gantt-container">
        <div class="gantt-header">
          <div class="task-column-header">
            <h4>Tasks</h4>
            <span class="task-count">{{ ganttTasks.length }} tasks</span>
          </div>
          <div class="timeline-header" ref="timelineHeader">
            <div 
              v-for="date in timelineHeaders" 
              :key="formatDateKey(date)" 
              class="date-header"
              :class="{ today: isToday(date) }"
            >
              <div class="date-label">{{ formatHeaderDate(date) }}</div>
              <div class="date-weekday">{{ formatWeekday(date) }}</div>
            </div>
          </div>
        </div>
        
        <div class="gantt-body" ref="ganttBody">
          <div 
            v-for="task in ganttTasks" 
            :key="task.id" 
            class="gantt-row"
            :class="{ selected: selectedTask?.id === task.id }"
            @click="selectTask(task)"
          >
            <div class="task-info">
              <div class="task-header">
                <h5 class="task-name">{{ task.name }}</h5>
                <div class="task-progress">{{ task.progress }}%</div>
              </div>
              <div class="task-meta">
                <span class="project-tag" :style="{ background: getProjectColor(task.project) }">
                  {{ task.project }}
                </span>
                <span class="assignee">
                  <i class="fas fa-user"></i>
                  {{ task.assignee }}
                </span>
                <span class="task-duration">
                  <i class="far fa-calendar"></i>
                  {{ formatDuration(task.startDate, task.endDate) }}
                </span>
              </div>
            </div>
            
            <div class="timeline-row">
              <div 
                class="task-bar"
                :style="getTaskBarStyle(task)"
                :class="getTaskStatusClass(task)"
                @mouseover="showTaskTooltip(task, $event)"
                @mouseleave="hideTaskTooltip"
              >
                <div class="bar-fill" :style="{ width: task.progress + '%' }"></div>
                <div class="bar-content">
                  <span class="bar-text">{{ task.name }}</span>
                </div>
              </div>
              
              <!-- Dependencies -->
              <div v-if="task.dependencies" class="dependencies">
                <div 
                  v-for="dep in task.dependencies" 
                  :key="dep" 
                  class="dependency-line"
                ></div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Today Indicator -->
        <div class="today-line" :style="getTodayLineStyle()" v-if="showTodayLine"></div>
      </div>

      <!-- No Project Selected -->
      <div v-if="!loading && !error && !selectedProject" class="state-card empty">
        <div class="state-content">
          <i class="fas fa-chart-gantt state-icon"></i>
          <h3>No Project Selected</h3>
          <p>Select a project from the dropdown to view its Gantt chart.</p>
        </div>
      </div>
      
      <!-- Chart Legend -->
      <div v-if="!loading && !error && selectedProject" class="chart-legend">
        <div class="legend-title">Status Legend</div>
        <div class="legend-items">
          <div class="legend-item">
            <div class="legend-color status-not-started"></div>
            <span>Not Started</span>
          </div>
          <div class="legend-item">
            <div class="legend-color status-in-progress"></div>
            <span>In Progress</span>
          </div>
          <div class="legend-item">
            <div class="legend-color status-completed"></div>
            <span>Completed</span>
          </div>
          <div class="legend-item">
            <div class="legend-color status-overdue"></div>
            <span>Overdue</span>
          </div>
          <div class="legend-item">
            <div class="legend-color status-delayed"></div>
            <span>Delayed</span>
          </div>
        </div>
      </div>
      
      <!-- Task Tooltip -->
      <div 
        v-if="tooltipTask" 
        class="task-tooltip" 
        :style="tooltipStyle"
        ref="tooltip"
      >
        <div class="tooltip-header">
          <h4>{{ tooltipTask.name }}</h4>
          <span class="tooltip-progress">{{ tooltipTask.progress }}%</span>
        </div>
        <div class="tooltip-body">
          <div class="tooltip-row">
            <span class="tooltip-label">Project:</span>
            <span>{{ tooltipTask.project }}</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">Assignee:</span>
            <span>{{ tooltipTask.assignee }}</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">Duration:</span>
            <span>{{ formatDuration(tooltipTask.startDate, tooltipTask.endDate) }}</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">Status:</span>
            <span class="tooltip-status" :class="getTaskStatusClass(tooltipTask)">
              {{ tooltipTask.status }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { format, addDays, differenceInDays, startOfDay, isToday as checkIsToday, differenceInCalendarDays } from 'date-fns';
import Sidebar from '@/components/layout/Sidebar.vue';
import AppHeader from '@/components/layout/AppHeader.vue';
import ThemeToggle from '@/components/layout/ThemeToggle.vue';
import AppButton from '@/components/ui/AppButton.vue';

export default {
  name: 'GanttPage',
  components: {
    Sidebar,
    AppHeader,
    ThemeToggle,
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
    const activeNav = ref('gantt');
    const setActiveNav = (target) => {
      activeNav.value = target;
    };

    // Chart Configuration
    const currentView = ref('Month');
    const viewOptions = ref(['Week', 'Month', 'Quarter']);
    const startDate = ref(format(new Date(), 'yyyy-MM-dd'));
    const endDate = ref(format(addDays(new Date(), 60), 'yyyy-MM-dd'));
    const selectedProject = ref('');
    const selectedTask = ref(null);
    const loading = ref(false);
    const error = ref(null);

    // Tooltip
    const tooltipTask = ref(null);
    const tooltipStyle = ref({});

    // Sample Projects
    const projects = ref([
      { id: 1, name: 'Website Redesign' },
      { id: 2, name: 'Mobile App Development' },
      { id: 3, name: 'Marketing Campaign' },
      { id: 4, name: 'Backend Infrastructure' }
    ]);

    // Task Data
    const ganttTasks = ref([
      {
        id: 1,
        name: 'Project Planning & Research',
        project: 'Website Redesign',
        assignee: 'Sarah Johnson',
        startDate: new Date(2024, 0, 15),
        endDate: new Date(2024, 1, 5),
        progress: 100,
        status: 'Completed',
        dependencies: []
      },
      {
        id: 2,
        name: 'UI/UX Design Phase',
        project: 'Website Redesign',
        assignee: 'Emma Rodriguez',
        startDate: new Date(2024, 1, 1),
        endDate: new Date(2024, 2, 15),
        progress: 75,
        status: 'In Progress',
        dependencies: [1]
      },
      {
        id: 3,
        name: 'Frontend Development',
        project: 'Website Redesign',
        assignee: 'David Kim',
        startDate: new Date(2024, 2, 10),
        endDate: new Date(2024, 4, 20),
        progress: 30,
        status: 'In Progress',
        dependencies: [2]
      },
      {
        id: 4,
        name: 'Backend API Development',
        project: 'Website Redesign',
        assignee: 'Michael Chen',
        startDate: new Date(2024, 1, 20),
        endDate: new Date(2024, 4, 15),
        progress: 45,
        status: 'In Progress',
        dependencies: [1]
      },
      {
        id: 5,
        name: 'Testing & QA',
        project: 'Website Redesign',
        assignee: 'Priya Patel',
        startDate: new Date(2024, 4, 10),
        endDate: new Date(2024, 5, 10),
        progress: 0,
        status: 'Not Started',
        dependencies: [3, 4]
      },
      {
        id: 6,
        name: 'Content Migration',
        project: 'Website Redesign',
        assignee: 'Sarah Johnson',
        startDate: new Date(2024, 3, 1),
        endDate: new Date(2024, 4, 30),
        progress: 15,
        status: 'Delayed',
        dependencies: [2]
      }
    ]);

    // Timeline Generation
    const timelineHeaders = computed(() => {
      const start = new Date(startDate.value);
      const end = new Date(endDate.value);
      const dates = [];
      
      let current = startOfDay(start);
      while (current <= end) {
        dates.push(new Date(current));
        if (currentView.value === 'Week') {
          current = addDays(current, 1);
        } else if (currentView.value === 'Month') {
          current = addDays(current, 7);
        } else {
          current = addDays(current, 14);
        }
      }
      
      return dates;
    });

    const showTodayLine = computed(() => {
      const today = new Date();
      const start = new Date(startDate.value);
      const end = new Date(endDate.value);
      return today >= start && today <= end;
    });

    // Helper Functions
    const formatHeaderDate = (date) => {
      if (currentView.value === 'Week') {
        return format(date, 'MMM d');
      } else if (currentView.value === 'Month') {
        return format(date, 'MMM d');
      } else {
        return format(date, 'MMM d');
      }
    };

    const formatWeekday = (date) => {
      return format(date, 'EEE');
    };

    const formatDateKey = (date) => {
      return format(date, 'yyyy-MM-dd');
    };

    const formatDuration = (start, end) => {
      const days = differenceInCalendarDays(end, start) + 1;
      if (days === 1) return '1 day';
      if (days < 7) return `${days} days`;
      const weeks = Math.floor(days / 7);
      const remainingDays = days % 7;
      if (weeks === 1 && remainingDays === 0) return '1 week';
      if (remainingDays === 0) return `${weeks} weeks`;
      return `${weeks}w ${remainingDays}d`;
    };

    const isToday = (date) => {
      return checkIsToday(date);
    };

    const getTaskBarStyle = (task) => {
      const chartStart = new Date(startDate.value);
      const chartEnd = new Date(endDate.value);
      const taskStart = task.startDate;
      const taskEnd = task.endDate;
      
      const totalDays = differenceInDays(chartEnd, chartStart);
      const daysFromStart = differenceInDays(taskStart, chartStart);
      const taskDuration = differenceInDays(taskEnd, taskStart);
      
      const leftPercent = Math.max(0, (daysFromStart / totalDays) * 100);
      const widthPercent = Math.min(100 - leftPercent, (taskDuration / totalDays) * 100);
      
      return {
        left: `${leftPercent}%`,
        width: `${widthPercent}%`,
      };
    };

    const getTaskStatusClass = (task) => {
      return `status-${task.status.toLowerCase().replace(' ', '-')}`;
    };

    const getProjectColor = (project) => {
      const colors = {
        'Website Redesign': '#00fff7',
        'Mobile App Development': '#00e0ff',
        'Marketing Campaign': '#00ffb3',
        'Backend Infrastructure': '#ffb300'
      };
      return colors[project] || '#6c757d';
    };

    const getTodayLineStyle = () => {
      const today = new Date();
      const chartStart = new Date(startDate.value);
      const chartEnd = new Date(endDate.value);
      const totalDays = differenceInDays(chartEnd, chartStart);
      const daysFromStart = differenceInDays(today, chartStart);
      const leftPercent = (daysFromStart / totalDays) * 100;
      
      return {
        left: `calc(300px + ${leftPercent}%)`
      };
    };

    // Event Handlers
    const loadGanttData = async () => {
      if (!selectedProject.value) return;
      
      loading.value = true;
      error.value = null;
      
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Filter tasks by selected project
        const filteredTasks = ganttTasks.value.filter(task => 
          task.project === selectedProject.value
        );
        
        if (filteredTasks.length === 0) {
          error.value = 'No tasks found for the selected project.';
        }
        
      } catch (err) {
        error.value = 'Failed to load Gantt chart data. Please try again.';
      } finally {
        loading.value = false;
      }
    };

    const updateDateRange = () => {
      // Validate date range
      if (new Date(startDate.value) >= new Date(endDate.value)) {
        endDate.value = format(addDays(new Date(startDate.value), 30), 'yyyy-MM-dd');
      }
    };

    const resetToCurrentMonth = () => {
      const today = new Date();
      startDate.value = format(new Date(today.getFullYear(), today.getMonth(), 1), 'yyyy-MM-dd');
      endDate.value = format(new Date(today.getFullYear(), today.getMonth() + 2, 0), 'yyyy-MM-dd');
    };

    const selectTask = (task) => {
      selectedTask.value = selectedTask.value?.id === task.id ? null : task;
    };

    const showTaskTooltip = (task, event) => {
      tooltipTask.value = task;
      const rect = event.target.getBoundingClientRect();
      tooltipStyle.value = {
        position: 'fixed',
        top: `${rect.top - 10}px`,
        left: `${rect.left + rect.width / 2}px`,
        transform: 'translateX(-50%) translateY(-100%)',
        zIndex: 1000
      };
    };

    const hideTaskTooltip = () => {
      tooltipTask.value = null;
    };

    onMounted(() => {
      const savedTheme = localStorage.getItem("zainpm-theme");
      if (savedTheme === "light") {
        isDark.value = false;
      }
      
      // Auto-select first project
      if (projects.value.length > 0) {
        selectedProject.value = projects.value[0].name;
        loadGanttData();
      }
    });

    return {
      isDark,
      toggleTheme,
      activeNav,
      setActiveNav,
      currentView,
      viewOptions,
      startDate,
      endDate,
      selectedProject,
      selectedTask,
      loading,
      error,
      projects,
      ganttTasks,
      timelineHeaders,
      showTodayLine,
      tooltipTask,
      tooltipStyle,
      formatHeaderDate,
      formatWeekday,
      formatDateKey,
      formatDuration,
      isToday,
      getTaskBarStyle,
      getTaskStatusClass,
      getProjectColor,
      getTodayLineStyle,
      loadGanttData,
      updateDateRange,
      resetToCurrentMonth,
      selectTask,
      showTaskTooltip,
      hideTaskTooltip
    };
  }
};
</script>

<style scoped>
@import '@/assets/css/main.css';

.gantt-page {
  display: flex;
  height: 100vh;
  background-color: var(--bg-base);
  color: var(--text-primary);
  line-height: 1.6;
}

/* Chart Controls */
.chart-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: var(--bg-section);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.control-group {
  display: flex;
  align-items: center;
  gap: 16px;
}

.control-select {
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-base);
  color: var(--text-primary);
  font-size: 14px;
  min-width: 200px;
  transition: all 0.2s ease;
}

.control-select:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(0, 255, 247, 0.1);
}

.view-toggle {
  display: flex;
  background: var(--bg-base);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.toggle-btn {
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
}

.toggle-btn:hover,
.toggle-btn.active {
  background: var(--primary);
  color: var(--dark-base);
}

.date-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.date-inputs {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date-input {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-base);
  color: var(--text-primary);
  font-size: 14px;
}

.date-separator {
  color: var(--text-secondary);
  font-weight: 500;
}

/* State Cards */
.state-card {
  background: var(--bg-section);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  padding: 60px 40px;
  text-align: center;
  margin-bottom: 20px;
}

.state-content {
  max-width: 400px;
  margin: 0 auto;
}

.state-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.loading .state-icon {
  color: var(--primary);
}

.error .state-icon {
  color: var(--danger);
}

.empty .state-icon {
  color: var(--text-secondary);
}

.state-card h3 {
  margin-bottom: 8px;
  font-size: 20px;
}

.state-card p {
  color: var(--text-secondary);
  margin-bottom: 20px;
  line-height: 1.6;
}

/* Gantt Chart */
.gantt-container {
  background: var(--bg-section);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  overflow: hidden;
  margin-bottom: 20px;
  position: relative;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.gantt-header {
  display: flex;
  background: rgba(0, 0, 0, 0.05);
  border-bottom: 2px solid var(--border-color);
}

.task-column-header {
  width: 300px;
  padding: 20px;
  border-right: 1px solid var(--border-color);
}

.task-column-header h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
}

.task-count {
  font-size: 12px;
  color: var(--text-secondary);
}

.timeline-header {
  flex: 1;
  display: flex;
  overflow-x: auto;
}

.date-header {
  min-width: 100px;
  padding: 16px 12px;
  text-align: center;
  border-right: 1px solid var(--border-color);
  transition: background 0.2s ease;
}

.date-header.today {
  background: rgba(0, 255, 247, 0.1);
  border-color: var(--primary);
}

.date-label {
  font-weight: 600;
  margin-bottom: 4px;
  font-size: 14px;
}

.date-weekday {
  font-size: 12px;
  color: var(--text-secondary);
}

.gantt-body {
  max-height: 600px;
  overflow-y: auto;
}

.gantt-row {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  min-height: 80px;
  transition: background 0.2s ease;
  cursor: pointer;
}

.gantt-row:hover {
  background: rgba(0, 0, 0, 0.02);
}

.gantt-row.selected {
  background: rgba(0, 255, 247, 0.05);
  border-color: var(--primary);
}

.task-info {
  width: 300px;
  padding: 16px 20px;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.task-name {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.3;
  flex: 1;
}

.task-progress {
  background: var(--primary);
  color: var(--dark-base);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  margin-left: 8px;
}

.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
}

.project-tag {
  color: var(--dark-base);
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 500;
  font-size: 11px;
}

.assignee,
.task-duration {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-secondary);
}

.assignee i,
.task-duration i {
  font-size: 10px;
}

.timeline-row {
  flex: 1;
  position: relative;
  padding: 24px 12px;
  min-height: 80px;
}

.task-bar {
  height: 32px;
  border-radius: 16px;
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.task-bar:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.bar-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 16px;
  transition: width 0.3s ease;
}

.bar-content {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.bar-text {
  color: white;
  font-size: 12px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0 12px;
}

/* Task Status Colors */
.status-not-started {
  background: #6c757d;
}

.status-in-progress {
  background: var(--primary);
}

.status-completed {
  background: var(--success);
}

.status-overdue {
  background: var(--danger);
}

.status-delayed {
  background: var(--warning);
}

/* Today Line */
.today-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--primary);
  z-index: 10;
  pointer-events: none;
  box-shadow: 0 0 8px rgba(0, 255, 247, 0.3);
}

.today-line::before {
  content: '';
  position: absolute;
  top: 0;
  left: -4px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--primary);
  box-shadow: 0 0 8px rgba(0, 255, 247, 0.5);
}

/* Chart Legend */
.chart-legend {
  background: var(--bg-section);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  padding: 20px;
  margin-bottom: 20px;
}

.legend-title {
  font-weight: 600;
  margin-bottom: 12px;
  font-size: 14px;
}

.legend-items {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 8px;
  flex-shrink: 0;
}

/* Task Tooltip */
.task-tooltip {
  background: var(--bg-section);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  max-width: 300px;
  z-index: 1000;
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.tooltip-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  flex: 1;
  line-height: 1.3;
}

.tooltip-progress {
  background: var(--primary);
  color: var(--dark-base);
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 600;
  margin-left: 8px;
}

.tooltip-body {
  font-size: 12px;
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.tooltip-label {
  color: var(--text-secondary);
  font-weight: 500;
}

.tooltip-status {
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 600;
}

.tooltip-status.status-not-started {
  background: rgba(108, 117, 125, 0.2);
  color: #6c757d;
}

.tooltip-status.status-in-progress {
  background: rgba(0, 255, 247, 0.2);
  color: var(--primary);
}

.tooltip-status.status-completed {
  background: rgba(0, 255, 179, 0.2);
  color: var(--success);
}

.tooltip-status.status-overdue {
  background: rgba(255, 0, 102, 0.2);
  color: var(--danger);
}

.tooltip-status.status-delayed {
  background: rgba(255, 179, 0, 0.2);
  color: var(--warning);
}

/* Responsive Design */
@media (max-width: 1200px) {
  .chart-controls {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .control-group,
  .date-controls {
    justify-content: space-between;
  }
}

@media (max-width: 992px) {
  .task-info {
    width: 250px;
  }
  
  .task-column-header {
    width: 250px;
  }
  
  .legend-items {
    gap: 16px;
  }
}

@media (max-width: 768px) {
  .chart-controls {
    padding: 16px;
  }
  
  .control-group {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .control-select {
    min-width: auto;
  }
  
  .date-controls {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .date-inputs {
    justify-content: space-between;
  }
  
  .task-info {
    width: 200px;
  }
  
  .task-column-header {
    width: 200px;
    padding: 16px;
  }
  
  .task-name {
    font-size: 13px;
  }
  
  .task-meta {
    flex-direction: column;
    gap: 4px;
  }
  
  .timeline-header {
    min-width: 500px;
  }
  
  .gantt-container {
    overflow-x: auto;
  }
  
  .legend-items {
    flex-direction: column;
    gap: 12px;
  }
  
  .state-card {
    padding: 40px 20px;
  }
  
  .state-icon {
    font-size: 36px;
  }
}

@media (max-width: 480px) {
  .task-info {
    width: 180px;
  }
  
  .task-column-header {
    width: 180px;
  }
  
  .task-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .task-progress {
    margin-left: 0;
  }
}

/* Dark mode adjustments */
.dark .gantt-container {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.dark .task-tooltip {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.dark .task-bar {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.dark .task-bar:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
}

/* Light mode specific adjustments */
.light .gantt-header {
  background: rgba(0, 0, 0, 0.02);
}

.light .gantt-row:hover {
  background: rgba(0, 0, 0, 0.01);
}

.light .gantt-row.selected {
  background: rgba(0, 107, 128, 0.05);
}

.light .date-header.today {
  background: rgba(0, 107, 128, 0.1);
  border-color: var(--primary);
}

/* Scrollbar styling */
.timeline-header::-webkit-scrollbar,
.gantt-body::-webkit-scrollbar {
  height: 8px;
  width: 8px;
}

.timeline-header::-webkit-scrollbar-track,
.gantt-body::-webkit-scrollbar-track {
  background: var(--bg-base);
  border-radius: 4px;
}

.timeline-header::-webkit-scrollbar-thumb,
.gantt-body::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}

.timeline-header::-webkit-scrollbar-thumb:hover,
.gantt-body::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}
</style>