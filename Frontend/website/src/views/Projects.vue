<template>
  <div class="projects-page" :class="{ dark: isDark, light: !isDark }">
    <!-- Sidebar -->
    <Sidebar />
    
    <!-- Main Content -->
    <div class="main-content">
      <AppHeader title="Projects">
        <template #actions>
          <ThemeToggle :is-dark="isDark" @toggle="toggleTheme" />
          <AppButton variant="primary" icon="fas fa-plus" @click="showCreateModal = true">
            New Project
          </AppButton>
        </template>
      </AppHeader>
      
      <!-- Filters and Search -->
      <div class="filters-section">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search projects..."
          />
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

      <!-- Loading & Error States -->
      <div v-if="loading" class="loading">
        <p>Loading projects...</p>
      </div>
      <div v-if="error" class="error">
        <p>{{ error }}</p>
        <AppButton @click="loadProjects" variant="primary">Retry</AppButton>
      </div>

      <!-- Projects Grid -->
      <div v-if="!loading && !error" class="projects-grid">
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
              <span>{{ formatDate(project.startDate) }} <span v-if="project.endDate">- {{ formatDate(project.endDate) }}</span></span>
            </div>
            <div class="meta-item">
              <i class="fas fa-tasks"></i>
              <span>{{ project.tasks?.length || project.tasks }} tasks</span>
            </div>
            <div class="meta-item">
              <i class="fas fa-users"></i>
              <span>{{ project.team?.length || project.team }} members</span>
            </div>
          </div>
          <div class="progress-section">
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: project.progress + '%' }"
              ></div>
            </div>
            <span class="progress-value">{{ project.progress }}%</span>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!loading && !error && filteredProjects.length === 0" class="empty-state">
        <i class="fas fa-project-diagram fa-3x"></i>
        <h3>No projects found</h3>
        <p>Try adjusting your search filters or create a new project</p>
        <AppButton variant="primary" icon="fas fa-plus" @click="showCreateModal = true">
          Create New Project
        </AppButton>
      </div>

      <!-- Create Project Modal -->
      <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
        <div class="modal" @click.stop>
          <h3>Create New Project</h3>
          <form @submit.prevent="createProject">
            <div class="form-group">
              <label>Project Name *</label>
              <input v-model="newProject.project_name" type="text" required />
            </div>
            <div class="form-group">
              <label>Start Date</label>
              <input v-model="newProject.start_date" type="date" />
            </div>
            <div class="form-group">
              <label>Timezone</label>
              <select v-model="newProject.timezone">
                <option value="Africa/Addis_Ababa">Africa/Addis_Ababa</option>
                <option value="UTC">UTC</option>
                <option value="America/New_York">America/New_York</option>
                <option value="Europe/London">Europe/London</option>
              </select>
            </div>
            <div class="modal-actions">
              <AppButton type="button" @click="showCreateModal = false">Cancel</AppButton>
              <AppButton type="submit" :disabled="createLoading" variant="primary">
                {{ createLoading ? 'Creating...' : 'Create Project' }}
              </AppButton>
            </div>
          </form>
        </div>
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
import Sidebar from '@/components/layout/Sidebar.vue';
import AppHeader from '@/components/layout/AppHeader.vue';
import ThemeToggle from '@/components/layout/ThemeToggle.vue';
import StateBadge from '@/components/ui/StateBadge.vue';
import AppButton from '@/components/ui/AppButton.vue';
import ProjectModal from '@/components/projects/ProjectModal.vue';
import { projectService } from '@/services/projects';

export default {
  name: 'ProjectsPage',
  components: {
    Sidebar,
    AppHeader,
    ThemeToggle,
    StateBadge,
    AppButton,
    ProjectModal,
  },
  setup() {
    // Theme
    const isDark = ref(true);
    const toggleTheme = () => {
      isDark.value = !isDark.value;
      localStorage.setItem('zainpm-theme', isDark.value ? 'dark' : 'light');
    };

    // Data & State
    const projects = ref([]);
    const loading = ref(false);
    const error = ref(null);
    const showCreateModal = ref(false);
    const createLoading = ref(false);
    const selectedProject = ref(null);

    // Filters
    const searchQuery = ref('');
    const statusFilter = ref('');
    const sortBy = ref('name');
    const statusOptions = [
      'Planning', 'Tentative', 'In Progress', 'Delayed', 'Overdue', 'Complete', 'Not Started'
    ];

    // New Project form
    const newProject = ref({ project_name: '', start_date: '', timezone: 'Africa/Addis_Ababa' });

    // Fetch projects
    const loadProjects = async () => {
      loading.value = true;
      error.value = null;
      try {
        const resp = await projectService.getProjects();
        projects.value = resp.projects || [];
      } catch (e) {
        error.value = e.message || 'Failed to load';
      } finally {
        loading.value = false;
      }
    };

    // Create project
    const createProject = async () => {
      createLoading.value = true;
      try {
        await projectService.createProject(newProject.value);
        showCreateModal.value = false;
        newProject.value = { project_name: '', start_date: '', timezone: 'Africa/Addis_Ababa' };
        await loadProjects();
      } catch (e) {
        alert('Failed to create project: ' + (e.message || e));
      } finally {
        createLoading.value = false;
      }
    };

    // Select for detail view
    const selectProject = (p) => selectedProject.value = p;

    // Computed filtered and sorted
    const filteredProjects = computed(() => {
      let res = projects.value.slice();
      if (searchQuery.value) {
        const q = searchQuery.value.toLowerCase();
        res = res.filter(p => p.name.toLowerCase().includes(q));
      }
      if (statusFilter.value) res = res.filter(p => p.status === statusFilter.value);
      if (sortBy.value === 'name') res.sort((a,b)=>a.name.localeCompare(b.name));
      else if (sortBy.value === 'startDate') res.sort((a,b)=>new Date(a.startDate)-new Date(b.startDate));
      else if (sortBy.value === 'endDate') res.sort((a,b)=>new Date(a.endDate)-new Date(b.endDate));
      return res;
    });

    // Date formatting
    const formatDate = d => d ? new Date(d).toLocaleDateString() : 'N/A';

    onMounted(() => {
      // theme pref
      const saved = localStorage.getItem('zainpm-theme');
      if (saved === 'light') isDark.value = false;
      loadProjects();
    });

    return {
      isDark, toggleTheme,
      projects, loading, error,
      showCreateModal, createLoading,
      selectedProject,
      searchQuery, statusFilter, sortBy, statusOptions,
      newProject,
      filteredProjects,
      loadProjects, createProject, selectProject,
      formatDate,
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

.loading, .error {
  text-align: center;
  padding: 2rem;
  background: var(--bg-section);
  border-radius: 8px;
  margin: 1rem 0;
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
  background: var(--accent);
}
.progress-value {
  font-weight: 600;
  font-size: 14px;
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

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal {
  background: var(--bg-section);
  border-radius: 8px;
  padding: 2rem;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}
.form-group {
  margin-bottom: 1rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}
.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}
.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

/* Responsive */
@media (max-width: 992px) {
  .main-content { margin-left: 80px; }
  .filters-section { flex-direction: column; }
  .search-box { max-width: 100%; }
}
@media (max-width: 768px) {
  .projects-grid { grid-template-columns: 1fr; }
  .filter-controls { flex-direction: column; width: 100%; }
  .filter-select { width: 100%; }
}
</style>
