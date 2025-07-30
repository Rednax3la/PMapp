//Frontend/website/src/views/Members.vue
<template>
  <div class="members-page" :class="{ dark: isDark, light: !isDark }">
    <!-- Sidebar -->
    <Sidebar :active-nav="activeNav" @nav-change="setActiveNav" />
    
    <!-- Main Content -->
    <div class="main-content">
      <AppHeader title="Team Members">
        <template #actions>
          <ThemeToggle :is-dark="isDark" @toggle="toggleTheme" />
          <AppButton variant="success" icon="fas fa-user-plus">
            Add Member
          </AppButton>
        </template>
      </AppHeader>
      
      <!-- Team Stats -->
      <div class="team-stats">
        <div class="stat-item">
          <div class="stat-number">{{ teamMembers.length }}</div>
          <div class="stat-label">Total Members</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ activeMembers }}</div>
          <div class="stat-label">Active</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ onlineMembers }}</div>
          <div class="stat-label">Online</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ avgTasksPerMember }}</div>
          <div class="stat-label">Avg Tasks</div>
        </div>
      </div>
      
      <!-- Search and Filters -->
      <div class="filters-section">
        <div class="search-box">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search team members..."
          >
        </div>
        
        <div class="filter-controls">
          <select v-model="roleFilter" class="filter-select">
            <option value="">All Roles</option>
            <option v-for="role in uniqueRoles" :key="role" :value="role">
              {{ role }}
            </option>
          </select>
          
          <select v-model="statusFilter" class="filter-select">
            <option value="">All Status</option>
            <option value="Active">Active</option>
            <option value="Away">Away</option>
            <option value="Busy">Busy</option>
          </select>
          
          <div class="view-toggle">
            <button 
              :class="['view-btn', { active: viewMode === 'grid' }]"
              @click="viewMode = 'grid'"
            >
              <i class="fas fa-th"></i>
            </button>
            <button 
              :class="['view-btn', { active: viewMode === 'list' }]"
              @click="viewMode = 'list'"
            >
              <i class="fas fa-list"></i>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Members Grid View -->
      <div v-if="viewMode === 'grid'" class="members-grid">
        <div 
          v-for="member in filteredMembers" 
          :key="member.id" 
          class="member-card"
          @click="selectMember(member)"
        >
          <div class="member-avatar">
            <img :src="member.avatar" :alt="member.name" />
            <div class="status-indicator" :class="member.status.toLowerCase()"></div>
          </div>
          
          <div class="member-info">
            <h3 class="member-name">{{ member.name }}</h3>
            <div class="member-role">{{ member.role }}</div>
            <div class="member-email">{{ member.email }}</div>
          </div>
          
          <div class="member-stats">
            <div class="stat">
              <span class="stat-label">Projects</span>
              <span class="stat-value">{{ member.projects }}</span>
            </div>
            <div class="stat">
              <span class="stat-label">Tasks</span>
              <span class="stat-value">{{ member.activeTasks }}</span>
            </div>
            <div class="stat">
              <span class="stat-label">Completed</span>
              <span class="stat-value">{{ member.completedTasks }}</span>
            </div>
          </div>
          
          <div class="member-actions">
            <AppButton variant="icon" icon="fas fa-message" tooltip="Message" />
            <AppButton variant="icon" icon="fas fa-eye" tooltip="View Profile" />
            <AppButton variant="icon" icon="fas fa-edit" tooltip="Edit" />
          </div>
        </div>
      </div>
      
      <!-- Members List View -->
      <div v-if="viewMode === 'list'" class="members-list">
        <div class="list-header">
          <div class="col-member">Member</div>
          <div class="col-role">Role</div>
          <div class="col-status">Status</div>
          <div class="col-projects">Projects</div>
          <div class="col-tasks">Tasks</div>
          <div class="col-performance">Performance</div>
          <div class="col-actions">Actions</div>
        </div>
        
        <div 
          v-for="member in filteredMembers" 
          :key="member.id" 
          class="list-item"
          @click="selectMember(member)"
        >
          <div class="col-member">
            <div class="member-basic">
              <img :src="member.avatar" :alt="member.name" class="avatar-small" />
              <div class="member-details">
                <div class="name">{{ member.name }}</div>
                <div class="email">{{ member.email }}</div>
              </div>
            </div>
          </div>
          
          <div class="col-role">
            <span class="role-badge">{{ member.role }}</span>
          </div>
          
          <div class="col-status">
            <div class="status-badge" :class="member.status.toLowerCase()">
              <div class="status-dot"></div>
              {{ member.status }}
            </div>
          </div>
          
          <div class="col-projects">{{ member.projects }}</div>
          <div class="col-tasks">{{ member.activeTasks }}/{{ member.totalTasks }}</div>
          
          <div class="col-performance">
            <div class="performance-bar">
              <div 
                class="performance-fill" 
                :style="{ width: member.performance + '%' }"
              ></div>
            </div>
            <span class="performance-text">{{ member.performance }}%</span>
          </div>
          
          <div class="col-actions">
            <AppButton variant="icon" icon="fas fa-message" tooltip="Message" />
            <AppButton variant="icon" icon="fas fa-eye" tooltip="View Profile" />
            <AppButton variant="icon" icon="fas fa-edit" tooltip="Edit" />
          </div>
        </div>
      </div>
      
      <!-- Member Detail Modal -->
      <div v-if="selectedMember" class="modal-overlay" @click.self="selectedMember = null">
        <div class="member-modal">
          <div class="modal-header">
            <div class="member-header-info">
              <img :src="selectedMember.avatar" :alt="selectedMember.name" />
              <div>
                <h3>{{ selectedMember.name }}</h3>
                <p>{{ selectedMember.role }}</p>
              </div>
            </div>
            <button class="close-btn" @click="selectedMember = null">&times;</button>
          </div>
          
          <div class="modal-body">
            <div class="member-details-grid">
              <div class="detail-section">
                <h4>Contact Information</h4>
                <div class="detail-item">
                  <i class="fas fa-envelope"></i>
                  <span>{{ selectedMember.email }}</span>
                </div>
                <div class="detail-item">
                  <i class="fas fa-phone"></i>
                  <span>{{ selectedMember.phone }}</span>
                </div>
                <div class="detail-item">
                  <i class="fas fa-map-marker-alt"></i>
                  <span>{{ selectedMember.location }}</span>
                </div>
              </div>
              
              <div class="detail-section">
                <h4>Performance Metrics</h4>
                <div class="metric-item">
                  <span>Overall Performance</span>
                  <div class="metric-bar">
                    <div 
                      class="metric-fill" 
                      :style="{ width: selectedMember.performance + '%' }"
                    ></div>
                  </div>
                  <span>{{ selectedMember.performance }}%</span>
                </div>
                <div class="metric-item">
                  <span>Task Completion Rate</span>
                  <div class="metric-bar">
                    <div 
                      class="metric-fill" 
                      :style="{ width: selectedMember.completionRate + '%' }"
                    ></div>
                  </div>
                  <span>{{ selectedMember.completionRate }}%</span>
                </div>
              </div>
              
              <div class="detail-section">
                <h4>Current Projects</h4>
                <div class="project-list">
                  <div 
                    v-for="project in selectedMember.currentProjects" 
                    :key="project.name"
                    class="project-item"
                  >
                    <div class="project-name">{{ project.name }}</div>
                    <div class="project-role">{{ project.role }}</div>
                  </div>
                </div>
              </div>
              
              <div class="detail-section">
                <h4>Skills</h4>
                <div class="skills-list">
                  <span 
                    v-for="skill in selectedMember.skills" 
                    :key="skill"
                    class="skill-tag"
                  >
                    {{ skill }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="modal-footer">
            <AppButton variant="primary" @click="editMember">Edit Member</AppButton>
            <AppButton variant="success" @click="assignTask">Assign Task</AppButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import Sidebar from '@/components/layout/Sidebar.vue';
import AppHeader from '@/components/layout/AppHeader.vue';
import ThemeToggle from '@/components/layout/ThemeToggle.vue';
import AppButton from '@/components/ui/AppButton.vue';

export default {
  name: 'MembersPage',
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
    const activeNav = ref('members');
    const setActiveNav = (target) => {
      activeNav.value = target;
    };

    // State
    const searchQuery = ref('');
    const roleFilter = ref('');
    const statusFilter = ref('');
    const viewMode = ref('grid');
    const selectedMember = ref(null);

    // Team Members Data
    const teamMembers = ref([
      {
        id: 1,
        name: 'Sarah Johnson',
        email: 'sarah.johnson@company.com',
        phone: '+1 (555) 123-4567',
        location: 'New York, NY',
        role: 'Senior Designer',
        status: 'Active',
        avatar: 'https://ix-marketing.imgix.net/focalpoint.png?auto=format,compress&w=1446',
        projects: 3,
        activeTasks: 8,
        totalTasks: 12,
        completedTasks: 42,
        performance: 92,
        completionRate: 88,
        currentProjects: [
          { name: 'Website Redesign', role: 'Lead Designer' },
          { name: 'Mobile App', role: 'UI Designer' },
          { name: 'Brand Guidelines', role: 'Designer' }
        ],
        skills: ['UI Design', 'Figma', 'Adobe Creative Suite', 'Prototyping']
      },
      {
        id: 2,
        name: 'Michael Chen',
        email: 'michael.chen@company.com',
        phone: '+1 (555) 234-5678',
        location: 'San Francisco, CA',
        role: 'Full Stack Developer',
        status: 'Busy',
        avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
        projects: 4,
        activeTasks: 12,
        totalTasks: 15,
        completedTasks: 38,
        performance: 85,
        completionRate: 79,
        currentProjects: [
          { name: 'API Integration', role: 'Backend Developer' },
          { name: 'Database Migration', role: 'Lead Developer' },
          { name: 'Mobile App', role: 'Frontend Developer' }
        ],
        skills: ['React', 'Node.js', 'Python', 'MongoDB', 'AWS']
      },
      {
        id: 3,
        name: 'Emma Rodriguez',
        email: 'emma.rodriguez@company.com',
        phone: '+1 (555) 345-6789',
        location: 'Austin, TX',
        role: 'Marketing Manager',
        status: 'Active',
        avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face',
        projects: 2,
        activeTasks: 6,
        totalTasks: 10,
        completedTasks: 28,
        performance: 94,
        completionRate: 91,
        currentProjects: [
          { name: 'Marketing Campaign', role: 'Campaign Manager' },
          { name: 'Brand Strategy', role: 'Marketing Lead' }
        ],
        skills: ['Digital Marketing', 'Content Strategy', 'Analytics', 'Social Media']
      },
      {
        id: 4,
        name: 'David Kim',
        email: 'david.kim@company.com',
        phone: '+1 (555) 456-7890',
        location: 'Seattle, WA',
        role: 'DevOps Engineer',
        status: 'Away',
        avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
        projects: 5,
        activeTasks: 10,
        totalTasks: 14,
        completedTasks: 35,
        performance: 78,
        completionRate: 82,
        currentProjects: [
          { name: 'Infrastructure Setup', role: 'DevOps Lead' },
          { name: 'CI/CD Pipeline', role: 'Engineer' },
          { name: 'Security Audit', role: 'Security Engineer' }
        ],
        skills: ['Docker', 'Kubernetes', 'AWS', 'Jenkins', 'Terraform']
      },
      {
        id: 5,
        name: 'Priya Patel',
        email: 'priya.patel@company.com',
        phone: '+1 (555) 567-8901',
        location: 'Boston, MA',
        role: 'Product Manager',
        status: 'Active',
        avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=face',
        projects: 3,
        activeTasks: 9,
        totalTasks: 11,
        completedTasks: 31,
        performance: 89,
        completionRate: 87,
        currentProjects: [
          { name: 'Product Roadmap', role: 'Product Owner' },
          { name: 'User Research', role: 'PM' },
          { name: 'Feature Planning', role: 'Lead PM' }
        ],
        skills: ['Product Strategy', 'User Research', 'Agile', 'Data Analysis']
      },
      {
        id: 6,
        name: 'James Wilson',
        email: 'james.wilson@company.com',
        phone: '+1 (555) 678-9012',
        location: 'Chicago, IL',
        role: 'QA Engineer',
        status: 'Active',
        avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face',
        projects: 2,
        activeTasks: 7,
        totalTasks: 9,
        completedTasks: 26,
        performance: 91,
        completionRate: 85,
        currentProjects: [
          { name: 'Testing Framework', role: 'QA Lead' },
          { name: 'Automation Suite', role: 'Test Engineer' }
        ],
        skills: ['Test Automation', 'Selenium', 'Jest', 'Cypress', 'Performance Testing']
      }
    ]);

    // Computed Properties
    const filteredMembers = computed(() => {
      let result = [...teamMembers.value];
      
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase();
        result = result.filter(m => 
          m.name.toLowerCase().includes(query) || 
          m.email.toLowerCase().includes(query) ||
          m.role.toLowerCase().includes(query)
        );
      }
      
      if (roleFilter.value) {
        result = result.filter(m => m.role === roleFilter.value);
      }
      
      if (statusFilter.value) {
        result = result.filter(m => m.status === statusFilter.value);
      }
      
      return result;
    });

    const uniqueRoles = computed(() => {
      return [...new Set(teamMembers.value.map(m => m.role))];
    });

    const activeMembers = computed(() => {
      return teamMembers.value.filter(m => m.status === 'Active').length;
    });

    const onlineMembers = computed(() => {
      return teamMembers.value.filter(m => m.status === 'Active' || m.status === 'Busy').length;
    });

    const avgTasksPerMember = computed(() => {
      const total = teamMembers.value.reduce((sum, m) => sum + m.activeTasks, 0);
      return Math.round(total / teamMembers.value.length);
    });

    // Methods
    const selectMember = (member) => {
      selectedMember.value = member;
    };

    const editMember = () => {
      console.log('Editing member:', selectedMember.value);
      selectedMember.value = null;
    };

    const assignTask = () => {
      console.log('Assigning task to:', selectedMember.value);
      selectedMember.value = null;
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
      searchQuery,
      roleFilter,
      statusFilter,
      viewMode,
      selectedMember,
      teamMembers,
      filteredMembers,
      uniqueRoles,
      activeMembers,
      onlineMembers,
      avgTasksPerMember,
      selectMember,
      editMember,
      assignTask
    };
  }
};
</script>

<style scoped>
@import '@/assets/css/main.css';

.members-page {
  display: flex;
  height: 100vh;
  background-color: var(--bg-base);
  color: var(--text-primary);
  line-height: 1.6;
}

.team-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 25px;
  padding: 20px;
  background: var(--bg-section);
  border-radius: 10px;
  border: 1px solid var(--border-color);
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

.filters-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  align-items: center;
  gap: 15px;
}

.filter-select {
  padding: 12px 20px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: var(--bg-section);
  color: var(--text-primary);
  font-size: 14px;
  min-width: 150px;
}

.view-toggle {
  display: flex;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  overflow: hidden;
}

.view-btn {
  padding: 10px 12px;
  background: transparent;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-btn:hover,
.view-btn.active {
  background: var(--primary);
  color: var(--dark-base);
}

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.member-card {
  background: var(--bg-section);
  border-radius: 12px;
  box-shadow: var(--shadow);
  padding: 25px;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
  cursor: pointer;
  text-align: center;
}

.member-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
  border-color: var(--accent);
}

.member-avatar {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 15px;
}

.member-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.status-indicator {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid var(--bg-section);
}

.status-indicator.active {
  background: var(--success);
}

.status-indicator.busy {
  background: var(--warning);
}

.status-indicator.away {
  background: var(--text-secondary);
}

.member-info {
  margin-bottom: 20px;
}

.member-name {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 5px;
}

.member-role {
  color: var(--primary);
  font-weight: 500;
  margin-bottom: 5px;
}

.member-email {
  color: var(--text-secondary);
  font-size: 14px;
}

.member-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
  padding: 15px 0;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.stat {
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  display: block;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.member-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.members-list {
  background: var(--bg-section);
  border-radius: 10px;
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.list-header,
.list-item {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 0.8fr 1fr 1.2fr 1fr;
  gap: 15px;
  align-items: center;
  padding: 15px 20px;
}

.list-header {
  background: rgba(0, 0, 0, 0.1);
  border-bottom: 2px solid var(--border-color);
  font-weight: 600;
}

.list-item {
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background 0.2s ease;
}

.list-item:hover {
  background: rgba(0, 0, 0, 0.05);
}

.member-basic {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-small {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.name {
  font-weight: 600;
  margin-bottom: 2px;
}

.email {
  font-size: 12px;
  color: var(--text-secondary);
}

.role-badge {
  background: var(--primary);
  color: var(--dark-base);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-badge.active .status-dot {
  background: var(--success);
}

.status-badge.busy .status-dot {
  background: var(--warning);
}

.status-badge.away .status-dot {
  background: var(--text-secondary);
}

.performance-bar {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  margin-right: 10px;
}

.performance-fill {
  height: 100%;
  background: var(--success);
  border-radius: 3px;
}

.performance-text {
  font-size: 12px;
  font-weight: 600;
}

.col-performance {
  display: flex;
  align-items: center;
}

.col-actions {
  display: flex;
  gap: 5px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.member-modal {
  background: var(--bg-section);
  color: var(--text-primary);
  border-radius: 10px;
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: var(--shadow);
}

.modal-header {
  padding: 20px;
  background: rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.member-header-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.member-header-info img {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
}

.member-header-info h3 {
  margin: 0;
  font-size: 1.5rem;
}

.member-header-info p {
  margin: 0;
  color: var(--primary);
  font-weight: 500;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  transition: color 0.2s ease;
}

.close-btn:hover {
  color: var(--danger);
}

.modal-body {
  padding: 20px;
}

.member-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.detail-section h4 {
  margin-bottom: 15px;
  color: var(--primary);
  font-size: 16px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  color: var(--text-secondary);
}

.detail-item i {
  width: 16px;
  color: var(--accent);
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.metric-bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  background: var(--success);
  border-radius: 4px;
}

.project-item {
  padding: 10px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 6px;
  margin-bottom: 8px;
}

.project-name {
  font-weight: 600;
}

.project-role {
  font-size: 12px;
  color: var(--text-secondary);
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-tag {
  background: var(--primary);
  color: var(--dark-base);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  background: rgba(0, 0, 0, 0.05);
}

@media (max-width: 992px) {
  .filters-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    max-width: 100%;
  }
  
  .filter-controls {
    justify-content: space-between;
  }
  
  .list-header,
  .list-item {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .member-basic {
    justify-content: space-between;
  }
}

@media (max-width: 768px) {
  .members-grid {
    grid-template-columns: 1fr;
  }
  
  .team-stats {
    flex-direction: column;
    gap: 15px;
  }
  
  .member-details-grid {
    grid-template-columns: 1fr;
  }
}
</style>