<template>
  <div class="projects-page" :class="{ dark: isDark, light: !isDark }">
    <!-- Sidebar -->
    <Sidebar />
    
    <!-- Main Content -->
    <div class="main-content">
      <AppHeader title="Projects">
        <template #actions>
          <ThemeToggle :is-dark="isDark" @toggle="toggleTheme" />
          <AppButton variant="primary" icon="fas fa-plus">
            New Project
          </AppButton>
        </template>
      </AppHeader>
      
      <!-- Projects Filter and Search -->
      <div class="filters-section">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search projects..."
          >
        </div>
        
        <div class="filter-controls">
          <select v-model="statusFilter" class="filter-select">
            <option value="">All Statuses</option>
            <option v-for="status in statusOptions" :key="status" :value="status">
              {{ status }}
            </option>
          </select>
          
          <select v-model="sortBy" class="filter-select">
            <option value="name">Sort by Name</option>
            <option value="startDate">Sort by Start Date</option>
            <option value="endDate">Sort by End Date</option>
          </select>
        </div>
      </div>
      
      <!-- Projects Grid -->
      <div class="projects-grid">
        <div 
          v-for="project in filteredProjects" 
          :key="project.id" 
          class="project-card"
          @click="selectProject(project)"
        >
          <div class="project-header">
            <h3 class="project-title">{{ project.name }}</h3>
            <StateBadge :status="project.status" />
          </div>
          
          <div class="project-meta">
            <div class="meta-item">
              <i class="far fa-calendar"></i>
              <span>{{ formatDateRange(project.startDate, project.endDate) }}</span>
            </div>
            <div class="meta-item">
              <i class="fas fa-tasks"></i>
              <span>{{ project.tasks }} tasks</span>
            </div>
            <div class="meta-item">
              <i class="fas fa-users"></i>
              <span>{{ project.team.length }} members</span>
            </div>
          </div>
          
          <div class="progress-section">
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: project.progress + '%', background: project.progressColor }"
              ></div>
            </div>
            <span class="progress-value">{{ project.progress }}%</span>
          </div>
          
          <div class="project-actions">
            <AppButton variant="icon" icon="fas fa-eye" tooltip="View Details" />
            <AppButton variant="icon" icon="fas fa-edit" tooltip="Edit Project" />
            <AppButton variant="icon" icon="fas fa-chart-bar" tooltip="View Reports" />
            <AppButton variant="icon" icon="fas fa-trash" tooltip="Delete Project" />
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div v-if="filteredProjects.length === 0" class="empty-state">
        <i class="fas fa-project-diagram fa-3x"></i>
        <h3>No projects found</h3>
        <p>Try adjusting your search filters or create a new project</p>
        <AppButton variant="primary" icon="fas fa-plus">
          Create New Project
        </AppButton>
      </div>
      
      <!-- Project Details Modal -->
      <ProjectModal 
        v-if="selectedProject" 
        :project="selectedProject" 
        @close="selectedProject = null"
      />
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
import ProjectModal from '@/components/projects/ProjectModal.vue';

export default {
  name: 'ProjectsPage',
  components: {
    Sidebar,
    AppHeader,
    ThemeToggle,
    StateBadge,
    AppButton,
    ProjectModal
  },
  setup() {
    // Theme Management
    const isDark = ref(true);
    const toggleTheme = () => {
      isDark.value = !isDark.value;
      localStorage.setItem("zainpm-theme", isDark.value ? "dark" : "light");
    };

    // Project Data
    const projects = ref([
      {
        id: 1,
        name: 'Website Redesign',
        description: 'Complete overhaul of company website with modern design and improved user experience',
        startDate: new Date(2023, 5, 1),
        endDate: new Date(2023, 6, 15),
        status: 'In Progress',
        progress: 65,
        progressColor: '#00e0ff',
        tasks: 18,
        team: ['Sarah Johnson', 'Michael Chen', 'Emma Rodriguez'],
        budget: 15000,
        spent: 9800
      },
      {
        id: 2,
        name: 'Mobile App Development',
        description: 'Development of cross-platform mobile application for iOS and Android',
        startDate: new Date(2023, 5, 10),
        endDate: new Date(2023, 7, 5),
        status: 'Tentative',
        progress: 15,
        progressColor: '#6c757d',
        tasks: 24,
        team: ['David Kim', 'Priya Patel'],
        budget: 25000,
        spent: 4200
      },
      {
        id: 3,
        name: 'Marketing Campaign',
        description: 'Q3 marketing campaign for new product launch with social media integration',
        startDate: new Date(2023, 4, 15),
        endDate: new Date(2023, 5, 30),
        status: 'Overdue',
        progress: 85,
        progressColor: '#f72585',
        tasks: 12,
        team: ['James Wilson', 'Emma Rodriguez', 'Michael Chen'],
        budget: 8000,
        spent: 7800
      },
      {
        id: 4,
        name: 'API Integration',
        description: 'Integration with third-party services and external APIs',
        startDate: new Date(2023, 6, 1),
        endDate: new Date(2023, 7, 20),
        status: 'Not Started',
        progress: 0,
        progressColor: '#6c757d',
        tasks: 8,
        team: ['David Kim'],
        budget: 5000,
        spent: 0
      },
      {
        id: 5,
        name: 'Database Migration',
        description: 'Migration to cloud-based database solution with improved performance',
        startDate: new Date(2023, 5, 20),
        endDate: new Date(2023, 7, 10),
        status: 'In Progress',
        progress: 40,
        progressColor: '#00e0ff',
        tasks: 14,
        team: ['Priya Patel', 'Michael Chen'],
        budget: 12000,
        spent: 5200
      },
      {
        id: 6,
        name: 'UI/UX Overhaul',
        description: 'User interface and experience improvements across all platforms',
        startDate: new Date(2023, 6, 5),
        endDate: new Date(2023, 8, 1),
        status: 'Planning',
        progress: 10,
        progressColor: '#6c757d',
        tasks: 16,
        team: ['Sarah Johnson', 'Emma Rodriguez'],
        budget: 9000,
        spent: 900
      }
    ]);

    // Filtering and Sorting
    const searchQuery = ref('');
    const statusFilter = ref('');
    const sortBy = ref('name');
    const selectedProject = ref(null);
    
    const statusOptions = ref([
      'Planning', 'Tentative', 'In Progress', 
      'Delayed', 'Overdue', 'Complete', 'Not Started'
    ]);

    const filteredProjects = computed(() => {
      let result = [...projects.value];
      
      // Apply search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        result = result.filter(p => 
          p.name.toLowerCase().includes(query) || 
          p.description.toLowerCase().includes(query)
        );
      }
      
      // Apply status filter
      if (statusFilter.value) {
        result = result.filter(p => p.status === statusFilter.value);
      }
      
      // Apply sorting
      if (sortBy.value === 'name') {
        result.sort((a, b) => a.name.localeCompare(b.name));
      } else if (sortBy.value === 'startDate') {
        result.sort((a, b) => a.startDate - b.startDate);
      } else if (sortBy.value === 'endDate') {
        result.sort((a, b) => a.endDate - b.endDate);
      }
      
      return result;
    });

    // Helper functions
    const formatDateRange = (start, end) => {
      return `${format(start, 'MMM d')} - ${format(end, 'MMM d, yyyy')}`;
    };
    
    const selectProject = (project) => {
      selectedProject.value = project;
    };

    onMounted(() => {
      // Load theme preference
      const savedTheme = localStorage.getItem("zainpm-theme");
      if (savedTheme === "light") {
        isDark.value = false;
      }
    });

    return {
      isDark,
      toggleTheme,
      projects,
      searchQuery,
      statusFilter,
      sortBy,
      statusOptions,
      filteredProjects,
      selectedProject,
      formatDateRange,
      selectProject
    };
  }
};
</script>

<style scoped>
.projects-page {
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

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.project-card {
  background: var(--bg-section);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 20px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
  cursor: pointer;
}

.project-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
  border-color: var(--accent);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.project-title {
  font-size: 18px;
  font-weight: 600;
  margin-right: 15px;
  color: var(--text-primary);
}

.project-meta {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: var(--text-secondary);
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
}

.progress-value {
  font-weight: 600;
  font-size: 14px;
  min-width: 40px;
  color: var(--text-primary);
}

.project-actions {
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
  color: var(--text-primary);
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 20px;
}

/* Light mode specific adjustments */
.light .search-box input {
  background: var(--bg-section);
  color: var(--text-primary);
}

.light .filter-select {
  background: var(--bg-section);
  color: var(--text-primary);
}

.light .meta-item {
  color: var(--text-primary);
}

@media (max-width: 992px) {
  .main-content {
    margin-left: 80px;
  }
  
  .filters-section {
    flex-direction: column;
  }
  
  .search-box {
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .projects-grid {
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