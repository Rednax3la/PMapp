//Frontend/website/src/views/Tasks.vue
<template>
  <div class="tasks-page" :class="{ dark: isDark, light: !isDark }">
    <!-- Sidebar -->
    <Sidebar />
    
    <!-- Main Content -->
    <div class="main-content">
      <AppHeader title="Tasks">
        <template #actions>
          <ThemeToggle :is-dark="isDark" @toggle="toggleTheme" />
          <AppButton variant="primary" icon="fas fa-plus" @click="showCreateModal = true">
            New Task
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
          <select v-model="filters.project" class="filter-select">
            <option value="">All Projects</option>
            <option v-for="project in projects" :key="project.id" :value="project.name">
              {{ project.name }}
            </option>
          </select>
          
          <select v-model="filters.status" class="filter-select">
            <option value="">All Statuses</option>
            <option value="not-started">Not Started</option>
            <option value="in-progress">In Progress</option>
            <option value="complete">Complete</option>
            <option value="overdue">Overdue</option>
          </select>
          
          <select v-model="filters.priority" class="filter-select">
            <option value="">All Priorities</option>
            <option value="low">Low Priority</option>
            <option value="medium">Medium Priority</option>
            <option value="high">High Priority</option>
            <option value="urgent">Urgent Priority</option>
          </select>

          <select v-model="filters.assignee" class="filter-select">
            <option value="">All Assignees</option>
            <option v-for="member in allMembers" :key="member" :value="member">
              {{ member }}
            </option>
          </select>
        </div>
      </div>

      <!-- Loading & Error States -->
      <div v-if="loading" class="loading">
        <p>Loading tasks...</p>
      </div>
      <div v-if="error" class="error">
        <p>{{ error }}</p>
        <AppButton @click="loadTasks" variant="primary">Retry</AppButton>
      </div>
      
      <!-- Tasks Grid -->
      <div v-if="!loading && !error" class="tasks-grid">
        <div 
          v-for="task in filteredTasks" 
          :key="task.id" 
          class="task-card"
          @click="selectTask(task)"
        >
          <div class="task-header">
            <h3 class="task-title">{{ task.name || task.title }}</h3>
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
              <span>
                <div class="assignees" v-if="task.members && task.members.length">
                  <span v-for="member in task.members" :key="member" class="assignee-tag">
                    {{ member }}
                  </span>
                </div>
                <span v-else>{{ task.assignee || 'Unassigned' }}</span>
              </span>
            </div>
            <div class="meta-item" :class="getPriorityClass(task.priority)">
              <i class="fas fa-flag"></i>
              <span>{{ task.priority || 'Medium' }}</span>
            </div>
          </div>
          
          <div class="task-description">
            {{ task.description || 'No description available' }}
          </div>

          <div class="progress-section">
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: (task.progress || 0) + '%' }"
              ></div>
            </div>
            <span class="progress-value">{{ task.progress || 0 }}%</span>
          </div>
          
          <div class="task-actions">
            <AppButton 
              variant="icon" 
              icon="fas fa-play" 
              tooltip="Start Task"
              @click.stop="markTaskAs(task, 'started')"
            />
            <AppButton 
              variant="icon" 
              icon="fas fa-check" 
              tooltip="Mark Complete"
              @click.stop="markTaskAs(task, 'complete')"
            />
            <AppButton 
              variant="icon" 
              icon="fas fa-edit" 
              tooltip="Update Task"
              @click.stop="showUpdateModal(task)"
            />
            <AppButton 
              variant="icon" 
              icon="fas fa-eye" 
              tooltip="View Details"
              @click.stop="selectTask(task)"
            />
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-if="!loading && !error && filteredTasks.length === 0" class="empty-state">
        <i class="fas fa-tasks fa-3x"></i>
        <h3>No tasks found</h3>
        <p>Try adjusting your search filters or create a new task</p>
        <AppButton variant="primary" icon="fas fa-plus" @click="showCreateModal = true">
          Create New Task
        </AppButton>
      </div>

      <!-- Create Task Modal -->
      <CreateTaskModal 
        v-if="showCreateModal"
        :projects="projects"
        @close="showCreateModal = false"
        @task-created="onTaskCreated"
      />

      <!-- Task Update Modal -->
      <TaskUpdateModal 
        v-if="showTaskUpdateModal && selectedTask"
        :task="selectedTask"
        @close="showTaskUpdateModal = false"
        @update-created="onUpdateCreated"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import Sidebar from '@/components/layout/Sidebar.vue';
import AppHeader from '@/components/layout/AppHeader.vue';
import ThemeToggle from '@/components/layout/ThemeToggle.vue';
import StateBadge from '@/components/ui/StateBadge.vue';
import AppButton from '@/components/ui/AppButton.vue';
import CreateTaskModal from '@/components/tasks/CreateTaskModal.vue';
import TaskUpdateModal from '@/components/tasks/TaskUpdateModal.vue';
import { taskService } from '@/services/tasks';
import { projectService } from '@/services/projects';
import { authService } from '@/services/auth';

export default {
  name: 'TasksPage',
  components: {
    Sidebar,
    AppHeader,
    ThemeToggle,
    StateBadge,
    AppButton,
    CreateTaskModal,
    TaskUpdateModal
  },
  setup() {
    // Theme Management
    const isDark = ref(true);
    const toggleTheme = () => {
      isDark.value = !isDark.value;
      localStorage.setItem("zainpm-theme", isDark.value ? "dark" : "light");
    };

    // Data & State
    const tasks = ref([]);
    const projects = ref([]);
    const loading = ref(false);
    const error = ref(null);
    const showCreateModal = ref(false);
    const showTaskUpdateModal = ref(false);
    const selectedTask = ref(null);

    // Filtering
    const searchQuery = ref('');
    const filters = ref({
      project: '',
      status: '',
      priority: '',
      assignee: ''
    });

    // Computed properties
    const filteredTasks = computed(() => {
      let result = [...tasks.value];
      
      // Apply search
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        result = result.filter(task => 
          (task.name || task.title || '').toLowerCase().includes(query) || 
          (task.description || '').toLowerCase().includes(query) ||
          (task.project || '').toLowerCase().includes(query)
        );
      }
      
      // Apply filters
      if (filters.value.project) {
        result = result.filter(task => task.project === filters.value.project);
      }
      
      if (filters.value.status) {
        result = result.filter(task => task.status === filters.value.status);
      }
      
      if (filters.value.priority) {
        result = result.filter(task => task.priority === filters.value.priority);
      }
      
      if (filters.value.assignee) {
        result = result.filter(task => 
          task.members && task.members.includes(filters.value.assignee)
        );
      }
      
      return result;
    });
    
    const allMembers = computed(() => {
      const members = new Set();
      tasks.value.forEach(task => {
        if (task.members) {
          task.members.forEach(member => members.add(member));
        }
      });
      return Array.from(members).sort();
    });

    // Methods
    const loadProjects = async () => {
      try {
        const user = authService.getCurrentUser();
        if (!user) return;
        
        const data = await projectService.getProjects(user.company_name);
        projects.value = data.projects || [];
      } catch (error) {
        console.error('Failed to load projects:', error);
      }
    };

    const loadTasks = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const user = authService.getCurrentUser();
        if (!user) {
          // Handle redirect to login if needed
          return;
        }
        
        // Load tasks from all projects
        const allTasks = [];
        for (const project of projects.value) {
          try {
            const projectData = await projectService.getProjects(user.company_name);
            const proj = projectData.projects.find(p => p.name === project.name);
            if (proj && proj.tasks) {
              proj.tasks.forEach(task => {
                allTasks.push({
                  ...task,
                  project: project.name,
                  dueDate: calculateDueDate(task.start_time, task.expected_duration),
                  progress: getTaskProgress(task.id)
                });
              });
            }
          } catch (error) {
            console.error(`Failed to load tasks for project ${project.name}:`, error);
          }
        }
        
        tasks.value = allTasks;
      } catch (e) {
        error.value = e.message || 'Failed to load tasks';
      } finally {
        loading.value = false;
      }
    };

    const getTaskStatus = (taskId) => {
      // This function would call your backend's get_task_state function
      // For now, return a mock status based on progress
      const task = tasks.value.find(t => t.id === taskId);
      if (task) {
        const progress = task.progress || 0;
        if (progress === 100) return 'complete';
        if (progress > 0) return 'in-progress';
        if (new Date() > new Date(task.dueDate)) return 'overdue';
        return 'tentative';
      }
      return 'tentative';
    };

    const markTaskAs = async (task, state) => {
      try {
        const user = authService.getCurrentUser();
        await taskService.markTaskAs(user.company_name, task.project, task.name, state);
        
        // Update task status locally using the task ID
        const taskIndex = tasks.value.findIndex(t => t.id === task.id);
        if (taskIndex !== -1) {
          tasks.value[taskIndex].status = state === 'started' ? 'in-progress' : state;
          if (state === 'complete') {
            tasks.value[taskIndex].progress = 100;
            // Call backend to create task update with 100% completion
            await createTaskUpdate(task.id, 100, `Task marked as ${state}`);
          } else if (state === 'started') {
            // Create task update for starting the task
            await createTaskUpdate(task.id, 10, `Task started`);
          }
        }
        
      } catch (error) {
        alert('Failed to update task: ' + error);
      }
    };

    const createTaskUpdate = async (taskId, statusPercentage, description) => {
      try {
        const updateData = {
          task_id: taskId,
          status_percentage: statusPercentage,
          description: description,
          timestamp: new Date().toISOString()
        };
        
        // Call your backend API to create the update
        // await taskService.createTaskUpdate(updateData);
        console.log('Task update created:', updateData);
        
      } catch (error) {
        console.error('Failed to create task update:', error);
      }
    };

    const selectTask = (task) => {
      selectedTask.value = task;
      // You can add task details modal here if needed
    };

    const showUpdateModal = (task) => {
      selectedTask.value = task;
      showTaskUpdateModal.value = true;
    };

    const onTaskCreated = () => {
      loadTasks();
    };

    const onUpdateCreated = () => {
      loadTasks();
    };

    const calculateDueDate = (startTime, duration) => {
      if (!startTime || !duration) return null;
      const start = new Date(startTime);
      const due = new Date(start.getTime() + (duration * 60 * 60 * 1000));
      return due.toISOString();
    };

    const getTaskProgress = (taskId) => {
      // This would typically come from the backend
      // For now, return a default value based on task updates
      const task = tasks.value.find(t => t.id === taskId);
      if (task && task.updates && task.updates.length > 0) {
        // Get the latest update's status_percentage
        return task.latest_progress || 0;
      }
      return Math.floor(Math.random() * 100);
    };

    const formatDate = (dateStr) => {
      if (!dateStr) return 'N/A';
      return new Date(dateStr).toLocaleDateString();
    };

    const getPriorityClass = (priority) => {
      switch (priority?.toLowerCase()) {
        case 'high':
        case 'urgent':
          return 'priority-high';
        case 'medium':
          return 'priority-medium';
        case 'low':
          return 'priority-low';
        default:
          return 'priority-medium';
      }
    };

    onMounted(async () => {
      const savedTheme = localStorage.getItem("zainpm-theme");
      if (savedTheme === "light") {
        isDark.value = false;
      }
      
      await loadProjects();
      await loadTasks();
    });

    return {
      isDark,
      toggleTheme,
      tasks,
      projects,
      loading,
      error,
      showCreateModal,
      showTaskUpdateModal,
      selectedTask,
      searchQuery,
      filters,
      filteredTasks,
      allMembers,
      loadTasks,
      markTaskAs,
      selectTask,
      showUpdateModal,
      onTaskCreated,
      onUpdateCreated,
      formatDate,
      getPriorityClass,
      getTaskStatus,
      createTaskUpdate
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

.main-content {
  flex: 1;
  margin-left: 260px;
  padding: 20px;
  overflow-y: auto;
  height: 100%;
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

.loading, .error {
  text-align: center;
  padding: 2rem;
  background: var(--bg-section);
  border-radius: 8px;
  margin: 1rem 0;
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

.assignees {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.assignee-tag {
  background: var(--primary);
  color: var(--dark-base);
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 500;
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

.progress-section {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
  background: var(--accent);
}

.progress-value {
  font-weight: 600;
  font-size: 14px;
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
  .main-content { margin-left: 80px; }
  .filters-section { flex-direction: column; }
  .search-box { max-width: 100%; }
}

@media (max-width: 768px) {
  .tasks-grid { grid-template-columns: 1fr; }
  .filter-controls { flex-direction: column; width: 100%; }
  .filter-select { width: 100%; }
}
</style>