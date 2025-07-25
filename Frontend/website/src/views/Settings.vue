<template>
  <div class="settings-page" :class="{ dark: isDark, light: !isDark }">
    <!-- Sidebar -->
    <Sidebar :active-nav="activeNav" @nav-change="setActiveNav" />

    <!-- Main Content -->
    <div class="main-content">
      <AppHeader title="Settings">
        <template #actions>
          <ThemeToggle :is-dark="isDark" @toggle="toggleTheme" />
        </template>
      </AppHeader>

      <!-- Settings Navigation -->
      <div class="settings-nav">
        <button
          v-for="tab in settingsTabs"
          :key="tab.id"
          :class="['nav-tab', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          <i :class="tab.icon"></i>
          {{ tab.label }}
        </button>
      </div>

      <!-- General Settings -->
      <div v-if="activeTab === 'general'" class="settings-section">
        <div class="section-header">
          <h3>General Settings</h3>
          <p>Manage your account and application preferences</p>
        </div>

        <div class="settings-grid">
          <div class="setting-card">
            <h4>Profile Information</h4>
            <div class="setting-group">
              <label>Full Name</label>
              <input type="text" v-model="settings.profile.name" class="setting-input">
            </div>
            <div class="setting-group">
              <label>Email Address</label>
              <input type="email" v-model="settings.profile.email" class="setting-input">
            </div>
            <div class="setting-group">
              <label>Job Title</label>
              <input type="text" v-model="settings.profile.jobTitle" class="setting-input">
            </div>
            <div class="setting-group">
              <label>Company</label>
              <input type="text" v-model="settings.profile.company" class="setting-input">
            </div>
          </div>

          <div class="setting-card">
            <h4>Application Preferences</h4>
            <div class="setting-group">
              <label>Default View</label>
              <select v-model="settings.preferences.defaultView" class="setting-select">
                <option value="dashboard">Dashboard</option>
                <option value="projects">Projects</option>
                <option value="tasks">Tasks</option>
                <option value="gantt">Gantt Chart</option>
              </select>
            </div>
            <div class="setting-group">
              <label>Items Per Page</label>
              <select v-model="settings.preferences.itemsPerPage" class="setting-select">
                <option value="10">10</option>
                <option value="25">25</option>
                <option value="50">50</option>
                <option value="100">100</option>
              </select>
            </div>
            <div class="setting-group">
              <label>Date Format</label>
              <select v-model="settings.preferences.dateFormat" class="setting-select">
                <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                <option value="YYYY-MM-DD">YYYY-MM-DD</option>
              </select>
            </div>
            <div class="setting-group">
              <label>Time Zone</label>
              <select v-model="settings.preferences.timeZone" class="setting-select">
                <option value="UTC-8">Pacific Time (UTC-8)</option>
                <option value="UTC-7">Mountain Time (UTC-7)</option>
                <option value="UTC-6">Central Time (UTC-6)</option>
                <option value="UTC-5">Eastern Time (UTC-5)</option>
                <option value="UTC+0">UTC</option>
                <option value="UTC+1">Central European Time (UTC+1)</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Notifications Settings -->
      <div v-if="activeTab === 'notifications'" class="settings-section">
        <div class="section-header">
          <h3>Notification Settings</h3>
          <p>Configure how and when you receive notifications</p>
        </div>

        <div class="settings-grid">
          <div class="setting-card">
            <h4>Email Notifications</h4>
            <div class="toggle-group">
              <div class="toggle-item">
                <div class="toggle-info">
                  <span class="toggle-label">Task Assignments</span>
                  <span class="toggle-description">Get notified when tasks are assigned to you</span>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settings.notifications.email.taskAssignments">
                  <span class="slider"></span>
                </label>
              </div>
              
              <div class="toggle-item">
                <div class="toggle-info">
                  <span class="toggle-label">Project Updates</span>
                  <span class="toggle-description">Receive updates about project progress</span>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settings.notifications.email.projectUpdates">
                  <span class="slider"></span>
                </label>
              </div>
              
              <div class="toggle-item">
                <div class="toggle-info">
                  <span class="toggle-label">Deadline Reminders</span>
                  <span class="toggle-description">Get reminded about upcoming deadlines</span>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settings.notifications.email.deadlineReminders">
                  <span class="slider"></span>
                </label>
              </div>
              
              <div class="toggle-item">
                <div class="toggle-info">
                  <span class="toggle-label">Weekly Summary</span>
                  <span class="toggle-description">Receive weekly project summaries</span>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settings.notifications.email.weeklySummary">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
          </div>


          <div class="setting-card">
            <h4>Push Notifications</h4>
            <div class="toggle-group">
              <div class="toggle-item">
                <div class="toggle-info">
                  <span class="toggle-label">Browser Notifications</span>
                  <span class="toggle-description">Show notifications in your browser</span>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settings.notifications.push.browser">
                  <span class="slider"></span>
                </label>
              </div>
              
              <div class="toggle-item">
                <div class="toggle-info">
                  <span class="toggle-label">Mobile Notifications</span>
                  <span class="toggle-description">Send notifications to mobile app</span>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settings.notifications.push.mobile">
                  <span class="slider"></span>
                </label>
              </div>
              
              <div class="toggle-item">
                <div class="toggle-info">
                  <span class="toggle-label">Sound Alerts</span>
                  <span class="toggle-description">Play sound for important notifications</span>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settings.notifications.push.sound">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>


      <!-- Security Settings -->
      <div v-if="activeTab === 'security'" class="settings-section">
        <div class="section-header">
          <h3>Security Settings</h3>
          <p>Manage your account security and privacy</p>
        </div>

        <div class="settings-grid">
          <div class="setting-card">
            <h4>Password Settings</h4>
            <div class="setting-group">
              <label>Current Password</label>
              <input type="password" v-model="passwordForm.current" class="setting-input">
            </div>
            <div class="setting-group">
              <label>New Password</label>
              <input type="password" v-model="passwordForm.new" class="setting-input">
            </div>
            <div class="setting-group">
              <label>Confirm New Password</label>
              <input type="password" v-model="passwordForm.confirm" class="setting-input">
            </div>
            <AppButton variant="primary" @click="changePassword">
              Change Password
            </AppButton>
          </div>

          <div class="setting-card">
            <h4>Two-Factor Authentication</h4>
            <div class="security-status">
              <div class="status-indicator" :class="{ enabled: settings.security.twoFactorEnabled }">
                <i :class="settings.security.twoFactorEnabled ? 'fas fa-shield-alt' : 'fas fa-shield'"></i>
              </div>
              <div class="status-info">
                <span class="status-label">
                  {{ settings.security.twoFactorEnabled ? 'Enabled' : 'Disabled' }}
                </span>
                <span class="status-description">
                  {{ settings.security.twoFactorEnabled ? 
                      'Your account is protected with 2FA' : 
                      'Add an extra layer of security to your account' }}
                </span>
              </div>
              <AppButton 
                :variant="settings.security.twoFactorEnabled ? 'danger' : 'success'"
                @click="toggleTwoFactor"
              >
                {{ settings.security.twoFactorEnabled ? 'Disable' : 'Enable' }}
              </AppButton>
            </div>
          </div>
          
          <div class="setting-card">
            <h4>Session Management</h4>
            <div class="session-list">
              <div v-for="session in activeSessions" :key="session.id" class="session-item">
                <div class="session-info">
                  <div class="session-device">
                    <i :class="session.deviceIcon"></i>
                    {{ session.device }}
                  </div>
                  <div class="session-details">
                    <span>{{ session.location }}</span>
                    <span>{{ session.lastActive }}</span>
                  </div>
                </div>
                <AppButton 
                  v-if="!session.current" 
                  variant="danger" 
                  @click="terminateSession(session.id)"
                >
                  Terminate
                </AppButton>
                <span v-else class="current-session">Current</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Team Settings -->
      <div v-if="activeTab === 'team'" class="settings-section">
        <div class="section-header">
          <h3>Team Settings</h3>
          <p>Manage team preferences and project defaults</p>
        </div>
        
        <div class="settings-grid">
          <div class="setting-card">
            <h4>Project Defaults</h4>
            <div class="setting-group">
              <label>Default Project Status</label>
              <select v-model="settings.team.defaultProjectStatus" class="setting-select">
                <option value="planning">Planning</option>
                <option value="in-progress">In Progress</option>
                <option value="on-hold">On Hold</option>
              </select>
            </div>
            <div class="setting-group">
              <label>Default Task Priority</label>
              <select v-model="settings.team.defaultTaskPriority" class="setting-select">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div class="setting-group">
              <label>Working Hours (Start)</label>
              <input type="time" v-model="settings.team.workingHours.start" class="setting-input">
            </div>
            <div class="setting-group">
              <label>Working Hours (End)</label>
              <input type="time" v-model="settings.team.workingHours.end" class="setting-input">
            </div>
          </div>
          
          <div class="setting-card">
            <h4>Team Permissions</h4>
            <div class="toggle-group">
              <div class="toggle-item">
                <div class="toggle-info">
                  <span class="toggle-label">Allow Task Creation</span>
                  <span class="toggle-description">Team members can create new tasks</span>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settings.team.permissions.createTasks">
                  <span class="slider"></span>
                </label>
              </div>
              
              <div class="toggle-item">
                <div class="toggle-info">
                  <span class="toggle-label">Allow Project Creation</span>
                  <span class="toggle-description">Team members can create new projects</span>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settings.team.permissions.createProjects">
                  <span class="slider"></span>
                </label>
              </div>
              
              <div class="toggle-item">
                <div class="toggle-info">
                  <span class="toggle-label">Allow User Invites</span>
                  <span class="toggle-description">Team members can invite new users</span>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settings.team.permissions.inviteUsers">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Help Settings -->
      <div v-if="activeTab === 'help'" class="settings-section">
        <div class="section-header">
          <h3>Help & Support</h3>
          <p>Get help and manage support preferences</p>
        </div>
        
        <div class="settings-grid">
          <div class="setting-card">
            <h4>Documentation</h4>
            <div class="help-links">
              <a href="#" class="help-link">
                <i class="fas fa-book"></i>
                <div>
                  <span class="link-title">User Guide</span>
                  <span class="link-description">Complete guide to using ZainPM</span>
                </div>
                <i class="fas fa-external-link-alt"></i>
              </a>
              
              <a href="#" class="help-link">
                <i class="fas fa-video"></i>
                <div>
                  <span class="link-title">Video Tutorials</span>
                  <span class="link-description">Step-by-step video guides</span>
                </div>
                <i class="fas fa-external-link-alt"></i>
              </a>
              
              <a href="#" class="help-link">
                <i class="fas fa-question-circle"></i>
                <div>
                  <span class="link-title">FAQ</span>
                  <span class="link-description">Frequently asked questions</span>
                </div>
                <i class="fas fa-external-link-alt"></i>
              </a>
            </div>
          </div>
          
          <div class="setting-card">
            <h4>Contact Support</h4>
            <div class="support-options">
              <div class="support-option">
                <i class="fas fa-envelope"></i>
                <div>
                  <span class="option-title">Email Support</span>
                  <span class="option-description">support@zainpm.com</span>
                </div>
              </div>
              
              <div class="support-option">
                <i class="fas fa-comments"></i>
                <div>
                  <span class="option-title">Live Chat</span>
                  <span class="option-description">Available 9 AM - 5 PM EST</span>
                </div>
              </div>
              
              <div class="support-option">
                <i class="fas fa-phone"></i>
                <div>
                  <span class="option-title">Phone Support</span>
                  <span class="option-description">+1 (555) 123-4567</span>
                </div>
              </div>
            </div>
            
            <AppButton variant="primary" @click="contactSupport">
              Contact Support
            </AppButton>
          </div>
          
          <div class="setting-card">
            <h4>System Information</h4>
            <div class="system-info">
              <div class="info-item">
                <span class="info-label">Version</span>
                <span class="info-value">ZainPM v2.1.0</span>
              </div>
              <div class="info-item">
                <span class="info-label">Last Updated</span>
                <span class="info-value">June 15, 2023</span>
              </div>
              <div class="info-item">
                <span class="info-label">Browser</span>
                <span class="info-value">{{ browserInfo }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Account Type</span>
                <span class="info-value">Professional</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Save Button -->
      <div class="settings-footer">
        <AppButton variant="success" @click="saveSettings">
          <i class="fas fa-save"></i>
          Save Settings
        </AppButton>
        <AppButton variant="secondary" @click="resetSettings">
          Reset to Defaults
        </AppButton>
      </div>
    </div>
  </div>
</template>


<script>
import { ref, onMounted } from 'vue';
import Sidebar from '@/components/layout/Sidebar.vue';
import AppHeader from '@/components/layout/AppHeader.vue';
import ThemeToggle from '@/components/layout/ThemeToggle.vue';
import AppButton from '@/components/ui/AppButton.vue';

export default {
  name: 'SettingsPage',
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
    const activeNav = ref('settings');
    const setActiveNav = (target) => {
      activeNav.value = target;
    };

    // Settings State
    const activeTab = ref('general');
    const settingsTabs = ref([
      { id: 'general', label: 'General', icon: 'fas fa-cog' },
      { id: 'notifications', label: 'Notifications', icon: 'fas fa-bell' },
      { id: 'security', label: 'Security', icon: 'fas fa-shield-alt' },
      { id: 'team', label: 'Team', icon: 'fas fa-users' },
      { id: 'help', label: 'Help', icon: 'fas fa-question-circle' }
    ]);

    // Settings Data
    const settings = ref({
      profile: {
        name: 'John Doe',
        email: 'john.doe@company.com',
        jobTitle: 'Project Manager',
        company: 'Tech Solutions Inc.'
      },
      preferences: {
        defaultView: 'dashboard',
        itemsPerPage: '25',
        dateFormat: 'MM/DD/YYYY',
        timeZone: 'UTC-5'
      },
      notifications: {
        email: {
          taskAssignments: true,
          projectUpdates: true,
          deadlineReminders: true,
          weeklySummary: false
        },
        push: {
          browser: true,
          mobile: false,
          sound: true
        }
      },
      security: {
        twoFactorEnabled: false
      },
      team: {
        defaultProjectStatus: 'planning',
        defaultTaskPriority: 'medium',
        workingHours: {
          start: '09:00',
          end: '17:00'
        },
        permissions: {
          createTasks: true,
          createProjects: false,
          inviteUsers: false
        }
      }
    });

    // Forms
    const passwordForm = ref({ current: '', new: '', confirm: '' });

    // Session Data
    const activeSessions = ref([
      { id: 1, device: 'Chrome on Windows', deviceIcon: 'fas fa-desktop', location: 'New York, NY', lastActive: '2 minutes ago', current: true },
      { id: 2, device: 'Safari on iPhone', deviceIcon: 'fas fa-mobile-alt', location: 'New York, NY', lastActive: '1 hour ago', current: false },
      { id: 3, device: 'Firefox on MacOS', deviceIcon: 'fas fa-laptop', location: 'Boston, MA', lastActive: '3 days ago', current: false }
    ]);

    const browserInfo = ref('');

        // Methods
    const changePassword = () => {
      if (passwordForm.value.new !== passwordForm.value.confirm) {
        alert('New passwords do not match');
        return;
      }
      console.log('Changing password...');
      passwordForm.value = { current: '', new: '', confirm: '' };
    };

    const toggleTwoFactor = () => {
      settings.value.security.twoFactorEnabled = !settings.value.security.twoFactorEnabled;
      console.log('2FA toggled:', settings.value.security.twoFactorEnabled);
    };

    const terminateSession = (sessionId) => {
      const index = activeSessions.value.findIndex(s => s.id === sessionId);
      if (index > -1) {
        activeSessions.value.splice(index, 1);
      }
      console.log('Session terminated:', sessionId);
    };

    const contactSupport = () => {
      console.log('Opening support contact form...');
    };

    const saveSettings = () => {
      console.log('Saving settings...', settings.value);
      // Save to localStorage or API
      localStorage.setItem('zainpm-settings', JSON.stringify(settings.value));
    };

    const resetSettings = () => {
      if (confirm('Are you sure you want to reset all settings to defaults?')) {
        // Reset logic here
        console.log('Settings reset to defaults');
      }
    };

    const getBrowserInfo = () => {
      const ua = navigator.userAgent;
      if (ua.includes('Chrome')) return 'Chrome ' + ua.match(/Chrome\/(\d+)/)[1];
      if (ua.includes('Firefox')) return 'Firefox ' + ua.match(/Firefox\/(\d+)/)[1];
      if (ua.includes('Safari')) return 'Safari ' + ua.match(/Version\/(\d+)/)[1];
      return 'Unknown Browser';
    };

    onMounted(() => {
      const savedTheme = localStorage.getItem("zainpm-theme");
      if (savedTheme === "light") {
        isDark.value = false;
      }

      // Load saved settings
      const savedSettings = localStorage.getItem('zainpm-settings');
      if (savedSettings) {
        settings.value = { ...settings.value, ...JSON.parse(savedSettings) };
      }

      browserInfo.value = getBrowserInfo();
    });

    return {
      isDark, toggleTheme,
      activeNav, setActiveNav,
      activeTab, settingsTabs,
      settings, passwordForm,
      activeSessions, browserInfo,
      changePassword, toggleTwoFactor,
      terminateSession, contactSupport,
      saveSettings, resetSettings
    };
  }
};
</script>

<style scoped>
@import '@/assets/css/main.css';

.settings-page {
  display: flex;
  height: 100vh;
  background-color: var(--bg-base);
  color: var(--text-primary);
  line-height: 1.6;
}

.settings-nav {
  display: flex;
  gap: 5px;
  margin-bottom: 30px;
  padding: 10px;
  background: var(--bg-section);
  border-radius: 10px;
  border: 1px solid var(--border-color);
  overflow-x: auto;
}

.nav-tab {
  padding: 12px 20px;
  border: none;
  background: transparent;
  color: var(--text-primary);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  white-space: nowrap;
  font-size: 14px;
}

.nav-tab:hover,
.nav-tab.active {
  background: var(--primary);
  color: var(--dark-base);
}

.settings-section {
  margin-bottom: 30px;
}

.section-header {
  margin-bottom: 25px;
}

.section-header h3 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 5px;
}

.section-header p {
  color: var(--text-secondary);
  font-size: 16px;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 25px;
}

.setting-card {
  background: var(--bg-section);
  border-radius: 12px;
  padding: 25px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow);
}

.setting-card h4 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--primary);
}

.setting-group {
  margin-bottom: 20px;
}

.setting-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.setting-input,
.setting-select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-base);
  color: var(--text-primary);
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.setting-input:focus,
.setting-select:focus {
  outline: none;
  border-color: var(--primary);
}

.toggle-group {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.toggle-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
}

.toggle-info {
  flex: 1;
}

.toggle-label {
  display: block;
  font-weight: 500;
  margin-bottom: 5px;
}

.toggle-description {
  font-size: 14px;
  color: var(--text-secondary);
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--border-color);
  transition: 0.3s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: var(--primary);
}

input:checked + .slider:before {
  transform: translateX(26px);
}

.security-status {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
}

.status-indicator {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  background: var(--text-secondary);
  color: white;
}

.status-indicator.enabled {
  background: var(--success);
}

.status-info {
  flex: 1;
}

.status-label {
  display: block;
  font-weight: 600;
  margin-bottom: 5px;
}

.status-description {
  font-size: 14px;
  color: var(--text-secondary);
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.session-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
}

.session-info {
  flex: 1;
}

.session-device {
  font-weight: 600;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.session-details {
  font-size: 14px;
  color: var(--text-secondary);
  display: flex;
  gap: 15px;
}

.current-session {
  color: var(--success);
  font-weight: 600;
  font-size: 14px;
}

.help-links {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.help-link {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  text-decoration: none;
  color: var(--text-primary);
  transition: all 0.2s ease;
}

.help-link:hover {
  background: rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.help-link i:first-child {
  color: var(--primary);
  font-size: 20px;
}

.help-link div {
  flex: 1;
}

.link-title {
  display: block;
  font-weight: 600;
  margin-bottom: 5px;
}

.link-description {
  font-size: 14px;
  color: var(--text-secondary);
}

.help-link i:last-child {
  color: var(--text-secondary);
  font-size: 14px;
}

.support-options {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.support-option {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
}

.support-option i {
  color: var(--primary);
  font-size: 20px;
}

.option-title {
  display: block;
  font-weight: 600;
  margin-bottom: 5px;
}

.option-description {
  font-size: 14px;
  color: var(--text-secondary);
}

.system-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-weight: 500;
}

.info-value {
  color: var(--text-secondary);
  font-family: monospace;
}

.settings-footer {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  padding-top: 30px;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 992px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  .settings-nav {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .toggle-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .session-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .settings-footer {
    flex-direction: column;
  }
}

</style>