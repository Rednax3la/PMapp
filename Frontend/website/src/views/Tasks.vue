<template>
  <div class="tasks-page" :class="{ dark: isDark, light: !isDark }">
    <!-- Sidebar -->
    <Sidebar :active-nav="activeNav" @nav-change="setActiveNav" />
    
    <!-- Main Content -->
    <div class="main-content">
      <AppHeader title="Tasks">
        <template #actions>
          <ThemeToggle :is-dark="isDark" @toggle="toggleTheme" />
          <AppButton variant="success" icon="fas fa-plus">
            Add Task
          </AppButton>
        </template>
      </AppHeader>
      
      <!-- Task Filters -->
      <div class="filters-section">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search tasks..."
          >
        </div>
        
        <div class="filter-controls">
          <select v-model="statusFilter" class="filter-select">
            <option value="">All Statuses</option>
            <option v-for="status in statusOptions" :key="status" :value="status">
              {{ status }}
            </option>
          </select>
          
          <select v-model="priorityFilter" class="filter-select">
            <option value="">All Priorities</option>
            <option value="High">High Priority</option>
            <option value="Medium">Medium Priority</option>
            <option value="Low">Low Priority</option>
          </select>
        </div>
      </div>
      
      <!-- Tasks Grid -->
      <div class="tasks-grid">
        <div 
          v-for="task in filteredTasks" 
          :key="task.id" 
          class="task-card"
          @click="selectTask(task)"
        >
          <div class="task-header">
            <h3 class="task-title">{{ task.title }}</h3>
            <StateBadge :status="task.status" />
          </div>
          
          <div class="task-meta">
            <div class="meta-item">
              <i class="far fa-calendar"></i>
              <span>{{ formatDate(task.dueDate) }}</span>
            </div>
            <div class="meta-item">
              <i class="fas fa-project-diagram"></i>
              <span>{{ task.project }}</span>
            </div>
            <div class="meta-item">
              <i class="fas fa-user"></i>
              <span>{{ task.assignee }}</span>
            </div>
            <div class="meta-item" :class="task.priorityClass">
              <i class="fas fa-flag"></i>
              <span>{{ task.priority }}</span>
            </div>
          </div>
          
          <div class="task-description">
            {{ task.description }}
          </div>
          
          <div class="task-actions">
            <AppButton variant="icon" icon="fas fa-eye" tooltip="View Details" />
            <AppButton variant="icon" icon="fas fa-edit" tooltip="Edit Task" />
            <AppButton variant="icon" icon="fas fa-check" tooltip="Mark Complete" />
            <AppButton variant="icon" icon="fas fa-trash" tooltip="Delete Task" />
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-if="filteredTasks.length === 0" class="empty-state">
        <i class="fas fa-tasks fa-3x"></i>
        <h3>No tasks found</h3>
        <p>Try adjusting your search filters or create a new task</p>
        <AppButton variant="success" icon="fas fa-plus">
          Create New Task
        </AppButton>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { format } from 'date-fns';
import Sidebar from '@/components/layout/Sidebar.vue';
import AppHeader from '@/components/layout/AppHeader.vue';
import ThemeToggle from '@/components/layout/ThemeToggle.vue';
import StateBadge from '@/components/ui/StateBadge.vue';
import AppButton from '@/components/ui/AppButton.vue';

export default {
  name: 'TasksPage',
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
    const activeNav = ref('tasks');
    const setActiveNav = (target) => {
      activeNav.value = target;
    };

    // Task Data
    const tasks = ref([
      {
        id: 1,
        title: 'Design Homepage',
        description: 'Create modern homepage design with responsive layout',
        project: 'Website Redesign',
        assignee: 'Sarah Johnson',
        dueDate: new Date(2023, 5, 15),
        status: 'In Progress',
        priority: 'High',
        priorityClass: 'priority-high'
      },
      {
        id: 2,
        title: 'API Integration',
        description: 'Implement REST API endpoints for user management',
        project: 'Mobile App',
        assignee: 'David Kim',
        dueDate: new Date(2023, 5, 20),
        status: 'Delayed',
        priority: 'Medium',
        priorityClass: 'priority-medium'
      },
      {
        id: 3,
        title: 'User Testing',
        description: 'Conduct usability testing with target users',
        project: 'Website Redesign',
        assignee: 'Emma Rodriguez',
        dueDate: new Date(2023, 5, 18),
        status: 'Complete',
        priority: 'Low',
        priorityClass: 'priority-low'
      },
      {
        id: 4,
        title: 'Database Migration',
        description: 'Migrate legacy data to new database structure',
        project: 'Backend Upgrade',
        assignee: 'Michael Chen',
        dueDate: new Date(2023, 5, 25),
        status: 'Tentative',
        priority: 'High',
        priorityClass: 'priority-high'
      },
      {
        id: 5,
        title: 'Content Creation',
        description: 'Write blog posts and marketing copy',
        project: 'Marketing Campaign',
        assignee: 'James Wilson',
        dueDate: new Date(2023, 5, 12),
        status: 'Overdue',
        priority: 'Medium',
        priorityClass: 'priority-medium'
      }
    ]);

    // Filtering
    const searchQuery = ref('');
    const statusFilter = ref('');
    const priorityFilter = ref('');
    const selectedTask = ref(null);
    
    const statusOptions = ref([
      'Tentative', 'In Progress', 'Delayed', 'Overdue', 'Complete'
    ]);

    const filteredTasks = computed(() => {
      let result = [...tasks.value];
      
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        result = result.filter(t => 
          t.title.toLowerCase().includes(query) || 
          t.description.toLowerCase().includes(query) ||
          t.project.toLowerCase().includes(query)
        );
      }
      
      if (statusFilter.value) {
        result = result.filter(t => t.status === statusFilter.value);
      }
      
      if (priorityFilter.value) {
        result = result.filter(t => t.priority === priorityFilter.value);
      }
      
      return result;
    });

    // Helper functions
    const formatDate = (date) => {
      return format(date, 'MMM d, yyyy');
    };
    
    const selectTask = (task) => {
      selectedTask.value = task;
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
      tasks,
      searchQuery,
      statusFilter,
      priorityFilter,
      statusOptions,
      filteredTasks,
      selectedTask,
      formatDate,
      selectTask
    };
  }
};
</script>

<style scoped>
@import '@/assets/css/main.css';

.tasks-page {
  display: flex;
  height: 100vh;
  background-color: var(--bg-base);
  color: var(--text-primary);
  line-height: 1.6;
}

.filters-section {
  display: flex;
  justify-content: space-between;
  margin-bottom: 25px;
  gap: 20px;
}

.search-box {
  flex: 1;
  max-width: 400px;
  position: relative;
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
  padding: 12px 20px 12px 40px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: var(--bg-section);
  color: var(--text-primary);
  font-size: 16px;
}

.filter-controls {
  display: flex;
  gap: 15px;
}

.filter-select {
  padding: 12px 20px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: var(--bg-section);
  color: var(--text-primary);
  font-size: 14px;
  min-width: 180px;
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.task-card {
  background: var(--bg-section);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 20px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
  cursor: pointer;
}

.task-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  border-color: var(--accent);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.task-title {
  font-size: 18px;
  font-weight: 600;
  margin-right: 15px;
}

.task-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 15px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: var(--text-secondary);
}

.priority-high {
  color: var(--danger) !important;
  font-weight: 600;
}

.priority-medium {
  color: var(--warning) !important;
  font-weight: 600;
}

.priority-low {
  color: var(--success) !important;
  font-weight: 600;
}

.task-description {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 20px;
  line-height: 1.5;
}

.task-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.empty-state {
  text-align: center;
  padding: 50px 20px;
  background: var(--bg-section);
  border-radius: 12px;
  border: 1px dashed var(--border-color);
}

.empty-state i {
  color: var(--accent);
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 22px;
  margin-bottom: 10px;
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 20px;
}

@media (max-width: 992px) {
  .filters-section {
    flex-direction: column;
  }
  
  .search-box {
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .tasks-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-controls {
    flex-direction: column;
    width: 100%;
  }
  
  .filter-select {
    width: 100%;
  }
}
</style>