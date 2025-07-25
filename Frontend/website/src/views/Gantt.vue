<template>
  <div class="gantt-page" :class="{ dark: isDark, light: !isDark }">
    <!-- Sidebar -->
    <Sidebar :active-nav="activeNav" @nav-change="setActiveNav" />
    
    <!-- Main Content -->
    <div class="main-content">
      <AppHeader title="Gantt Chart">
        <template #actions>
          <ThemeToggle :is-dark="isDark" @toggle="toggleTheme" />
          <AppButton variant="primary" icon="fas fa-download">
            Export Chart
          </AppButton>
        </template>
      </AppHeader>
      
      <!-- Chart Controls -->
      <div class="chart-controls">
        <div class="view-controls">
          <button 
            v-for="view in viewOptions" 
            :key="view" 
            :class="['view-btn', { active: currentView === view }]"
            @click="currentView = view"
          >
            {{ view }}
          </button>
        </div>
        
        <div class="date-range">
          <input 
            type="date" 
            v-model="startDate" 
            class="date-input"
          >
          <span>to</span>
          <input 
            type="date" 
            v-model="endDate" 
            class="date-input"
          >
        </div>
      </div>
      
      <!-- Gantt Chart Container -->
      <div class="gantt-container">
        <div class="gantt-header">
          <div class="task-column">Tasks</div>
          <div class="timeline-header">
            <div 
              v-for="date in timelineHeaders" 
              :key="date" 
              class="date-header"
            >
              {{ formatHeaderDate(date) }}
            </div>
          </div>
        </div>
        
        <div class="gantt-body">
          <div 
            v-for="task in ganttTasks" 
            :key="task.id" 
            class="gantt-row"
          >
            <div class="task-info">
              <div class="task-name">{{ task.name }}</div>
              <div class="task-details">
                <span class="project-tag">{{ task.project }}</span>
                <span class="assignee">{{ task.assignee }}</span>
              </div>
            </div>
            
            <div class="timeline-row">
              <div 
                class="task-bar"
                :style="getTaskBarStyle(task)"
              >
                <div class="bar-content">
                  <span class="bar-text">{{ task.progress }}%</span>
                </div>
                <div 
                  class="progress-overlay" 
                  :style="{ width: task.progress + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Legend -->
      <div class="gantt-legend">
        <div class="legend-item">
          <div class="legend-color" style="background: var(--primary)"></div>
          <span>In Progress</span>
        </div>
        <div class="legend-item">
          <div class="legend-color" style="background: var(--success)"></div>
          <span>Completed</span>
        </div>
        <div class="legend-item">
          <div class="legend-color" style="background: var(--warning)"></div>
          <span>Delayed</span>
        </div>
        <div class="legend-item">
          <div class="legend-color" style="background: var(--danger)"></div>
          <span>Overdue</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { format, addDays, differenceInDays, startOfDay } from 'date-fns';
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
    const startDate = ref(format(new Date(2023, 5, 1), 'yyyy-MM-dd'));
    const endDate = ref(format(new Date(2023, 7, 31), 'yyyy-MM-dd'));

    // Task Data
    const ganttTasks = ref([
      {
        id: 1,
        name: 'Website Redesign',
        project: 'Web Dev',
        assignee: 'Sarah J.',
        startDate: new Date(2023, 5, 1),
        endDate: new Date(2023, 6, 15),
        progress: 65,
        status: 'In Progress',
        color: 'var(--primary)'
      },
      {
        id: 2,
        name: 'Mobile App Development',
        project: 'Mobile',
        assignee: 'David K.',
        startDate: new Date(2023, 5, 10),
        endDate: new Date(2023, 7, 5),
        progress: 25,
        status: 'In Progress',
        color: 'var(--primary)'
      },
      {
        id: 3,
        name: 'Marketing Campaign',
        project: 'Marketing',
        assignee: 'Emma R.',
        startDate: new Date(2023, 4, 15),
        endDate: new Date(2023, 5, 30),
        progress: 85,
        status: 'Overdue',
        color: 'var(--danger)'
      },
      {
        id: 4,
        name: 'API Integration',
        project: 'Backend',
        assignee: 'Michael C.',
        startDate: new Date(2023, 6, 1),
        endDate: new Date(2023, 7, 20),
        progress: 0,
        status: 'Not Started',
        color: 'var(--text-secondary)'
      },
      {
        id: 5,
        name: 'Database Migration',
        project: 'Backend',
        assignee: 'Priya P.',
        startDate: new Date(2023, 5, 20),
        endDate: new Date(2023, 7, 10),
        progress: 40,
        status: 'In Progress',
        color: 'var(--primary)'
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
          current = addDays(current, 30);
        }
      }
      
      return dates;
    });

    // Helper Functions
    const formatHeaderDate = (date) => {
      if (currentView.value === 'Week') {
        return format(date, 'MMM d');
      } else if (currentView.value === 'Month') {
        return format(date, 'MMM d');
      } else {
        return format(date, 'MMM yyyy');
      }
    };

    const getTaskBarStyle = (task) => {
      const chartStart = new Date(startDate.value);
      const chartEnd = new Date(endDate.value);
      const taskStart = task.startDate;
      const taskEnd = task.endDate;
      
      const totalDays = differenceInDays(chartEnd, chartStart);
      const daysFromStart = differenceInDays(taskStart, chartStart);
      const taskDuration = differenceInDays(taskEnd, taskStart);
      
      const leftPercent = (daysFromStart / totalDays) * 100;
      const widthPercent = (taskDuration / totalDays) * 100;
      
      return {
        left: `${Math.max(0, leftPercent)}%`,
        width: `${Math.min(100, widthPercent)}%`,
        background: task.color,
        position: 'relative'
      };
    };

    onMounted(() => {
      const savedTheme = localStorage.getItem("zainpm-theme");
      if (savedTheme === "light") {
        isDark.value = false;
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
      ganttTasks,
      timelineHeaders,
      formatHeaderDate,
      getTaskBarStyle
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

.chart-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding: 15px 20px;
  background: var(--bg-section);
  border-radius: 10px;
  border: 1px solid var(--border-color);
}

.view-controls {
  display: flex;
  gap: 5px;
}

.view-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-btn:hover,
.view-btn.active {
  background: var(--primary);
  color: var(--dark-base);
  border-color: var(--primary);
}

.date-range {
  display: flex;
  align-items: center;
  gap: 10px;
}

.date-input {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--bg-base);
  color: var(--text-primary);
}

.gantt-container {
  background: var(--bg-section);
  border-radius: 10px;
  border: 1px solid var(--border-color);
  overflow: hidden;
  margin-bottom: 25px;
}

.gantt-header {
  display: flex;
  background: rgba(0, 0, 0, 0.1);
  border-bottom: 2px solid var(--border-color);
}

.task-column {
  width: 300px;
  padding: 15px 20px;
  font-weight: 600;
  border-right: 1px solid var(--border-color);
}

.timeline-header {
  flex: 1;
  display: flex;
  overflow-x: auto;
}

.date-header {
  min-width: 80px;
  padding: 15px 10px;
  text-align: center;
  font-weight: 500;
  border-right: 1px solid var(--border-color);
  font-size: 14px;
}

.gantt-body {
  max-height: 500px;
  overflow-y: auto;
}

.gantt-row {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  min-height: 60px;
}

.gantt-row:hover {
  background: rgba(0, 0, 0, 0.05);
}

.task-info {
  width: 300px;
  padding: 15px 20px;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.task-name {
  font-weight: 600;
  margin-bottom: 5px;
}

.task-details {
  display: flex;
  gap: 10px;
  font-size: 12px;
}

.project-tag {
  background: var(--primary);
  color: var(--dark-base);
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.assignee {
  color: var(--text-secondary);
}

.timeline-row {
  flex: 1;
  position: relative;
  padding: 20px 10px;
}

.task-bar {
  height: 20px;
  border-radius: 10px;
  position: relative;
  cursor: pointer;
  transition: all 0.2s ease;
}

.task-bar:hover {
  opacity: 0.8;
  transform: scaleY(1.1);
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
  font-size: 11px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.progress-overlay {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  z-index: 1;
}

.gantt-legend {
  display: flex;
  justify-content: center;
  gap: 30px;
  padding: 20px;
  background: var(--bg-section);
  border-radius: 10px;
  border: 1px solid var(--border-color);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

@media (max-width: 992px) {
  .chart-controls {
    flex-direction: column;
    gap: 15px;
  }
  
  .task-column,
  .task-info {
    width: 250px;
  }
}

@media (max-width: 768px) {
  .gantt-legend {
    flex-direction: column;
    gap: 15px;
  }
  
  .timeline-header {
    min-width: 500px;
  }
}
</style>