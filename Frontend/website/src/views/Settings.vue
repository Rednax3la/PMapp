<!-- src/views/Settings.vue -->
<template>
  <div class="settings-page" :class="{ dark: isDark, light: !isDark }">
    <Sidebar :active-nav="activeNav" @nav-change="setActiveNav" />

    <div class="main-content">
      <AppHeader title="Settings">
        <template #actions>
          <ThemeToggle :is-dark="isDark" @toggle="toggleTheme" />
        </template>
      </AppHeader>

      <!-- Tabs -->
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

      <!-- General -->
      <section v-show="activeTab === 'general'" class="settings-section">
        <div class="section-header">
          <h3>General Settings</h3>
          <p>Manage your account and application preferences</p>
        </div>
        <div class="settings-grid">
          <!-- Profile -->
          <div class="setting-card">
            <h4>Profile Information</h4>
            <div class="setting-group" v-for="(field,label) in profileFields" :key="field">
              <label>{{ label }}</label>
              <input
                :type="field==='email'?'email':'text'"
                v-model="settings.profile[field]"
                class="setting-input"
              />
            </div>
          </div>
          <!-- Preferences -->
          <div class="setting-card">
            <h4>Application Preferences</h4>
            <div class="setting-group">
              <label>Default View</label>
              <select v-model="settings.preferences.defaultView" class="setting-select">
                <option value="dashboard">Dashboard</option>
                <option value="projects">Projects</option>
                <option value="tasks">Tasks</option>
                <option value="gantt">Gantt Chart</option>
                <option value="timetable">Timetable</option>
                <option value="reports">Reports</option>
              </select>
            </div>
            <div class="setting-group">
              <label>Items Per Page</label>
              <select v-model="settings.preferences.itemsPerPage" class="setting-select">
                <option v-for="n in [10,25,50,100]" :key="n" :value="n">{{ n }}</option>
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
      </section>

      <!-- Notifications -->
      <section v-show="activeTab === 'notifications'" class="settings-section">
        <div class="section-header">
          <h3>Notification Settings</h3>
          <p>Configure how and when you receive notifications</p>
        </div>
        <div class="settings-grid">
          <!-- Email -->
          <div class="setting-card">
            <h4>Email Notifications</h4>
            <div class="toggle-group">
              <div class="toggle-item" v-for="opt in notificationEmailOpts" :key="opt.key">
                <div class="toggle-info">
                  <span class="toggle-label">{{ opt.label }}</span>
                  <span class="toggle-description">{{ opt.desc }}</span>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settings.notifications.email[opt.key]" />
                  <span class="slider"></span>
                </label>
              </div>
            </div>
          </div>
          <!-- Push -->
          <div class="setting-card">
            <h4>Push Notifications</h4>
            <div class="toggle-group">
              <div class="toggle-item" v-for="opt in notificationPushOpts" :key="opt.key">
                <div class="toggle-info">
                  <span class="toggle-label">{{ opt.label }}</span>
                  <span class="toggle-description">{{ opt.desc }}</span>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settings.notifications.push[opt.key]" />
                  <span class="slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Security -->
      <section v-show="activeTab === 'security'" class="settings-section">
        <div class="section-header">
          <h3>Security Settings</h3>
          <p>Manage your account security and privacy</p>
        </div>
        <div class="settings-grid">
          <!-- Password -->
          <div class="setting-card">
            <h4>Password Settings</h4>
            <div class="setting-group" v-for="field in ['current','new','confirm']" :key="field">
              <label>{{ field === 'current' ? 'Current Password' : field==='new' ? 'New Password' : 'Confirm New Password' }}</label>
              <input
                type="password"
                v-model="passwordForm[field]"
                class="setting-input"
              />
            </div>
            <AppButton variant="primary" @click="changePassword">
              Change Password
            </AppButton>
          </div>
          <!-- 2FA -->
          <div class="setting-card">
            <h4>Two‑Factor Authentication</h4>
            <div class="security-status">
              <div
                class="status-indicator"
                :class="{ enabled: settings.security.twoFactorEnabled }"
              >
                <i :class="settings.security.twoFactorEnabled ? 'fas fa-shield-alt' : 'fas fa-shield'"></i>
              </div>
              <div class="status-info">
                <span class="status-label">
                  {{ settings.security.twoFactorEnabled ? 'Enabled' : 'Disabled' }}
                </span>
                <span class="status-description">
                  {{
                    settings.security.twoFactorEnabled
                      ? 'Your account is protected with 2FA'
                      : 'Add an extra layer of security to your account'
                  }}
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
        </div>
      </section>

      <!-- Team -->
      <section v-show="activeTab === 'team'" class="settings-section">
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
              <input type="time" v-model="settings.team.workingHours.start" class="setting-input" />
            </div>
            <div class="setting-group">
              <label>Working Hours (End)</label>
              <input type="time" v-model="settings.team.workingHours.end" class="setting-input" />
            </div>
          </div>
          <div class="setting-card">
            <h4>Team Permissions</h4>
            <div class="toggle-group">
              <div class="toggle-item" v-for="opt in teamPermOpts" :key="opt.key">
                <div class="toggle-info">
                  <span class="toggle-label">{{ opt.label }}</span>
                  <span class="toggle-description">{{ opt.desc }}</span>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="settings.team.permissions[opt.key]" />
                  <span class="slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Help -->
      <section v-show="activeTab === 'help'" class="settings-section">
        <div class="section-header">
          <h3>Help & Support</h3>
          <p>Get help and manage support preferences</p>
        </div>
        <div class="settings-grid">
          <!-- Documentation Links -->
          <div class="setting-card">
            <h4>Documentation</h4>
            <div class="help-links">
              <a v-for="link in docLinks" :key="link.title" :href="link.href" class="help-link" target="_blank">
                <i :class="link.icon"></i>
                <div>
                  <span class="link-title">{{ link.title }}</span>
                  <span class="link-description">{{ link.desc }}</span>
                </div>
                <i class="fas fa-external-link-alt"></i>
              </a>
            </div>
          </div>
          <!-- Contact Support -->
          <div class="setting-card">
            <h4>Contact Support</h4>
            <div class="support-options">
              <div class="support-option" v-for="opt in supportOpts" :key="opt.type">
                <i :class="opt.icon"></i>
                <div>
                  <span class="option-title">{{ opt.title }}</span>
                  <span class="option-description">{{ opt.desc }}</span>
                </div>
              </div>
            </div>
            <AppButton variant="primary" @click="contactSupport">
              Contact Support
            </AppButton>
          </div>
          <!-- System Info -->
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
      </section>

      <!-- Footer Actions -->
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
import { ref, reactive, onMounted } from 'vue';
import Sidebar from '@/components/layout/Sidebar.vue';
import AppHeader from '@/components/layout/AppHeader.vue';
import ThemeToggle from '@/components/layout/ThemeToggle.vue';
import AppButton from '@/components/ui/AppButton.vue';

export default {
  name: 'SettingsPage',
  components: { Sidebar, AppHeader, ThemeToggle, AppButton },
  setup() {
    // theme & nav
    const isDark = ref(true);
    const toggleTheme = () => {
      isDark.value = !isDark.value;
      localStorage.setItem('zainpm-theme', isDark.value ? 'dark' : 'light');
    };
    const activeNav = ref('settings');
    const setActiveNav = (t) => (activeNav.value = t);

    // tabs
    const activeTab = ref('general');
    const settingsTabs = [
      { id: 'general', label: 'General', icon: 'fas fa-cog' },
      { id: 'notifications', label: 'Notifications', icon: 'fas fa-bell' },
      { id: 'security', label: 'Security', icon: 'fas fa-shield-alt' },
      { id: 'team', label: 'Team', icon: 'fas fa-users' },
      { id: 'help', label: 'Help', icon: 'fas fa-question-circle' },
    ];

    // data
    const settings = reactive({
      profile: {
        name: 'John Doe',
        email: 'john.doe@company.com',
        jobTitle: 'Project Manager',
        company: 'Tech Solutions Inc.'
      },
      preferences: {
        defaultView: 'dashboard',
        itemsPerPage: 25,
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
        workingHours: { start: '09:00', end: '17:00' },
        permissions: { createTasks: true, createProjects: false, inviteUsers: false }
      }
    });

    const passwordForm = reactive({ current: '', new: '', confirm: '' });

    // helpers for loops
    const profileFields = {
      name: 'Full Name',
      email: 'Email Address',
      jobTitle: 'Job Title',
      company: 'Company'
    };
    const notificationEmailOpts = [
      { key: 'taskAssignments', label: 'Task Assignments', desc: 'Get notified when tasks are assigned to you' },
      { key: 'projectUpdates',    label: 'Project Updates',    desc: 'Receive updates about project progress' },
      { key: 'deadlineReminders',  label: 'Deadline Reminders',  desc: 'Get reminded about upcoming deadlines' },
      { key: 'weeklySummary',      label: 'Weekly Summary',      desc: 'Receive weekly project summaries' }
    ];
    const notificationPushOpts = [
      { key: 'browser', label: 'Browser Notifications', desc: 'Show notifications in your browser' },
      { key: 'mobile',  label: 'Mobile Notifications',  desc: 'Send notifications to mobile app' },
      { key: 'sound',   label: 'Sound Alerts',         desc: 'Play sound for important notifications' }
    ];
    const teamPermOpts = [
      { key: 'createTasks',    label: 'Allow Task Creation',    desc: 'Team members can create new tasks' },
      { key: 'createProjects', label: 'Allow Project Creation', desc: 'Team members can create new projects' },
      { key: 'inviteUsers',    label: 'Allow User Invites',     desc: 'Team members can invite new users' }
    ];
    const docLinks = [
      { title: 'User Guide',     desc: 'Complete guide to using ZainPM',     icon: 'fas fa-book', href: '#' },
      { title: 'Video Tutorials', desc: 'Step-by-step video guides',         icon: 'fas fa-video', href: '#' },
      { title: 'FAQ',            desc: 'Frequently asked questions',        icon: 'fas fa-question-circle', href: '#' }
    ];
    const supportOpts = [
      { type: 'email',   title: 'Email Support', desc: 'support@zainpm.com', icon: 'fas fa-envelope' },
      { type: 'chat',    title: 'Live Chat',     desc: 'Available 9 AM - 5 PM EST', icon: 'fas fa-comments' },
      { type: 'phone',   title: 'Phone Support', desc: '+1 (555) 123-4567', icon: 'fas fa-phone' }
    ];

    // browser & lifecycle
    const browserInfo = ref('');
    const getBrowserInfo = () => {
      const ua = navigator.userAgent;
      if (/Chrome\/(\d+)/.test(ua))   return 'Chrome ' + ua.match(/Chrome\/(\d+)/)[1];
      if (/Firefox\/(\d+)/.test(ua))  return 'Firefox ' + ua.match(/Firefox\/(\d+)/)[1];
      if (/Version\/(\d+)/.test(ua)) return 'Safari ' + ua.match(/Version\/(\d+)/)[1];
      return 'Unknown Browser';
    };

    onMounted(() => {
      const savedTheme = localStorage.getItem('zainpm-theme');
      if (savedTheme === 'light') isDark.value = false;

      const saved = localStorage.getItem('zainpm-settings');
      if (saved) Object.assign(settings, JSON.parse(saved));

      browserInfo.value = getBrowserInfo();
    });

    // actions
    const changePassword = () => {
      if (passwordForm.new !== passwordForm.confirm) {
        alert('New passwords do not match');
        return;
      }
      console.log('Password Changed');
      Object.assign(passwordForm, { current: '', new: '', confirm: '' });
    };
    const toggleTwoFactor  = () => settings.security.twoFactorEnabled = !settings.security.twoFactorEnabled;
    const contactSupport    = () => console.log('Contact Support');
    const saveSettings      = () => localStorage.setItem('zainpm-settings', JSON.stringify(settings));
    const resetSettings     = () => {
      if (confirm('Reset all settings to defaults?')) {
        localStorage.removeItem('zainpm-settings');
        window.location.reload();
      }
    };

    return {
      isDark, toggleTheme, activeNav, setActiveNav,
      activeTab, settingsTabs, settings, passwordForm,
      profileFields, notificationEmailOpts, notificationPushOpts, teamPermOpts,
      docLinks, supportOpts, browserInfo,
      changePassword, toggleTwoFactor, contactSupport, saveSettings, resetSettings
    };
  }
};
</script>

<style scoped>
@import '@/assets/css/main.css';

/* you already have all the layout & component styles in main.css */
</style>
