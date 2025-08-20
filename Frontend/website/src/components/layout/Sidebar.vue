//Frontend/website/src/components/layout/Sidebar.vue
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
        :class="{ active: $route.path === item.path }"
      >
        <i :class="item.icon"></i>
        <span>{{ item.label }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<script>
export default {
  name: 'AppSidebar',
  data() {
    return {
      items: [
        { target: 'dashboard', path: '/', icon: 'fas fa-home', label: 'Dashboard' },
        { target: 'projects', path: '/projects', icon: 'fas fa-project-diagram', label: 'Projects' },
        { target: 'tasks', path: '/tasks', icon: 'fas fa-tasks', label: 'Tasks' },
        { target: 'gantt', path: '/gantt', icon: 'fas fa-chart-bar', label: 'Gantt Chart' },
        { target: 'timetable', path: '/timetable', icon: 'fas fa-calendar-day', label: 'Timetable' },
        { target: 'reports', path: '/reports', icon: 'fas fa-chart-pie', label: 'Reports' },
        { target: 'members', path: '/members', icon: 'fas fa-users', label: 'Team Members' },
        { target: 'settings', path: '/settings', icon: 'fas fa-cog', label: 'Settings' },
        { target: 'help', path: '/help', icon: 'fas fa-question-circle', label: 'Help' },
        { target: 'logout', path: '/logout', icon: 'fas fa-sign-out-alt', label: 'Logout' }
      ]
    }
  }
}
</script>


<style scoped>
.sidebar {
  width: 260px;
  background: linear-gradient(180deg, var(--shadow-glow), var(--sfinal)) !important;
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
  max-width: 100%;
}

.logo h1 {
  font-weight: 600;
  color: var(--accent);
  font-size: 3rem;
}

.logo-img {
  width: 67px;
  height: 67px;
  align-items: center;
  object-fit: contain;
  margin-right: 12px;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: block;
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
  color: rgba(248, 247, 247, 0.9);
  text-decoration: none;
}

.nav-item:hover, 
.nav-item.active,
.nav-item.router-link-active {
  background: rgba(255, 255, 255, 0.1);
  border-left: 4px solid var(--highlight);
  color: white;
}

.nav-item i {
  margin-right: 12px;
  font-size: 18px;
}

/* Responsive Design */
@media (max-width: 992px) {
  .sidebar {
    width: 80px;
  }
  .sidebar .logo h1, 
  .sidebar .nav-item span {
    display: none;
  }
  .sidebar .logo {
    justify-content: center;
    padding: 20px 0;
  }
  .sidebar .logo-img {
    margin-right: 0;
  }
  .sidebar .nav-item {
    justify-content: center;
  }
  .sidebar .nav-item i {
    margin-right: 0;
    font-size: 20px;
  }
}
</style>