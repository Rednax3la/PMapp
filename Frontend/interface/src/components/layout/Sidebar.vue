<template>
  <aside class="sidebar">
    <div class="logo">
      <img class="logo-img" src="@/assets/Zain-clear2.png" alt="ZainPM Logo" />
      <h1>ZainPM</h1>
    </div>
    <nav class="nav-links">
      <router-link
        v-for="item in items"
        :key="item.target"
        :to="item.path"
        class="nav-item"
        :class="{ active: activeNav === item.target }"
        @click="changeNav(item.target)"
      >
        <i :class="item.icon"></i>
        <span>{{ item.label }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<script>
import { ref } from 'vue';

export default {
  name: 'AppSidebar',
  props: {
    activeNav: { type: String, required: true }
  },
  emits: ['nav-change'],
  setup(props, { emit }) {
    const items = ref([
      { target: 'dashboard', path: '/', icon: 'fas fa-home', label: 'Dashboard' },
      { target: 'projects', path: '/projects', icon: 'fas fa-project-diagram', label: 'Projects' },
      { target: 'tasks', icon: 'fas fa-tasks', label: 'Tasks' },
      { target: 'gantt', icon: 'fas fa-chart-bar', label: 'Gantt Chart' },
      { target: 'timetable', icon: 'fas fa-calendar-day', label: 'Timetable' },
      { target: 'reports', icon: 'fas fa-chart-pie', label: 'Reports' },
      { target: 'members', icon: 'fas fa-users', label: 'Team Members' },
      { target: 'settings', icon: 'fas fa-cog', label: 'Settings' },
      { target: 'help', icon: 'fas fa-question-circle', label: 'Help' },
      { target: 'logout', path: '/logout', icon: 'fas fa-sign-out-alt', label: 'Logout' }
    ]);

    const changeNav = (target) => {
      emit('nav-change', target);
    };

    return { items, changeNav };
  }
};
</script>

<style scoped>
/* Sidebar styles reused from AdminDashboard */
.sidebar {
  width: 260px;
  background: linear-gradient(180deg, var(--shadow-glow), var(--accent));
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
}

.logo-img {
  width: 67px;
  height: 67px;
  object-fit: contain;
  margin-right: 12px;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
  color: rgba(255, 255, 255, 0.9);
}

.nav-item:hover,
.nav-item.active {
  background: rgba(255, 255, 255, 0.1);
  border-left: 4px solid var(--highlight);
  color: white;
}

.nav-item i {
  margin-right: 12px;
  font-size: 18px;
}
</style>