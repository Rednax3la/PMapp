<template>
  <aside class="sidebar">
    <div class="logo">
      <img class="logo-img" src="@/assets/Zain-clear2.png" alt="ZainPM Logo" />
      <h1>ZainPM</h1>
    </div>

    <!-- Subscription tier badge (admins only) -->
    <div v-if="userStore.isAdmin || userStore.isManager" class="tier-badge" :class="userStore.subscriptionTier">
      <span class="tier-dot"></span>
      <span class="tier-label">{{ tierLabel }}</span>
    </div>

    <nav class="nav-links">
      <router-link
        v-for="item in navItems"
        :key="item.target"
        :to="item.path"
        class="nav-item"
        :class="{ active: $route.path === item.path }"
      >
        <i :class="item.icon"></i>
        <span>{{ item.label }}</span>
        <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<script>
import { computed } from 'vue'
import { useUserStore } from '@/store/user'

export default {
  name: 'AppSidebar',

  setup() {
    const userStore = useUserStore()

    const adminItems = [
      { target: 'dashboard',    path: '/',            icon: 'fas fa-home',            label: 'Dashboard' },
      { target: 'projects',     path: '/projects',    icon: 'fas fa-project-diagram', label: 'Projects' },
      { target: 'tasks',        path: '/tasks',       icon: 'fas fa-tasks',           label: 'Tasks' },
      { target: 'gantt',        path: '/gantt',       icon: 'fas fa-chart-bar',       label: 'Gantt Chart' },
      { target: 'timetable',    path: '/timetable',   icon: 'fas fa-calendar-day',    label: 'Timetable' },
      { target: 'reports',      path: '/reports',     icon: 'fas fa-chart-pie',       label: 'Reports' },
      { target: 'members',      path: '/members',     icon: 'fas fa-users',           label: 'Team Members' },
      { target: 'subscription', path: '/subscription',icon: 'fas fa-crown',           label: 'Subscription' },
      { target: 'settings',     path: '/settings',    icon: 'fas fa-cog',             label: 'Settings' },
      { target: 'help',         path: '/help',        icon: 'fas fa-question-circle', label: 'Help' },
      { target: 'logout',       path: '/logout',      icon: 'fas fa-sign-out-alt',    label: 'Logout' }
    ]

    const memberItems = [
      { target: 'member-dashboard', path: '/member-dashboard', icon: 'fas fa-home',         label: 'My Dashboard' },
      { target: 'tasks',            path: '/tasks',            icon: 'fas fa-tasks',         label: 'My Tasks' },
      { target: 'projects',         path: '/projects',         icon: 'fas fa-project-diagram',label: 'Projects' },
      { target: 'gantt',            path: '/gantt',            icon: 'fas fa-chart-bar',     label: 'Gantt' },
      { target: 'timetable',        path: '/timetable',        icon: 'fas fa-calendar-day',  label: 'Timetable' },
      { target: 'settings',         path: '/settings',         icon: 'fas fa-cog',           label: 'Settings' },
      { target: 'help',             path: '/help',             icon: 'fas fa-question-circle',label: 'Help' },
      { target: 'logout',           path: '/logout',           icon: 'fas fa-sign-out-alt',  label: 'Logout' }
    ]

    const navItems = computed(() =>
      userStore.isMember ? memberItems : adminItems
    )

    const tierLabel = computed(() => {
      const map = { free: 'Free Plan', pro: 'Pro', enterprise: 'Enterprise' }
      return map[userStore.subscriptionTier] || 'Free Plan'
    })

    return { userStore, navItems, tierLabel }
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
  display: flex;
  flex-direction: column;
}

.logo {
  display: flex;
  align-items: center;
  padding: 0 20px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 0.5rem;
  max-width: 100%;
}

.logo h1 {
  font-weight: 600;
  color: var(--accent);
  font-size: 2.6rem;
}

.logo-img {
  width: 60px;
  height: 60px;
  object-fit: contain;
  margin-right: 12px;
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 255, 247, 0.2);
  display: block;
}

/* Tier badge */
.tier-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 8px 20px;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(0,0,0,0.2);
}

.tier-badge.free   { color: rgba(255,255,255,0.5); }
.tier-badge.pro    { color: var(--primary); border-color: rgba(0,255,247,0.3); background: rgba(0,255,247,0.08); }
.tier-badge.enterprise { color: #ffb300; border-color: rgba(255,179,0,0.3); background: rgba(255,179,0,0.08); }

.tier-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: currentColor;
}

.tier-label { flex: 1; }

.nav-links {
  padding: 12px 0;
  flex: 1;
  overflow-y: auto;
}

.nav-item {
  padding: 11px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.25s ease;
  color: rgba(248, 247, 247, 0.85);
  text-decoration: none;
  font-size: 0.9rem;
  position: relative;
}

.nav-item:hover,
.nav-item.active,
.nav-item.router-link-active {
  background: rgba(0, 255, 247, 0.08);
  border-left: 3px solid var(--highlight);
  color: white;
  padding-left: 17px;
}

.nav-item i {
  font-size: 16px;
  width: 18px;
  text-align: center;
  flex-shrink: 0;
}

.nav-badge {
  margin-left: auto;
  background: rgba(0,255,247,0.2);
  color: var(--primary);
  border-radius: 10px;
  padding: 1px 7px;
  font-size: 0.7rem;
  font-weight: 700;
}

@media (max-width: 992px) {
  .sidebar { width: 70px; }
  .logo h1,
  .nav-item span,
  .tier-badge .tier-label,
  .nav-badge { display: none; }
  .logo { justify-content: center; padding: 16px 0; }
  .logo-img { margin-right: 0; width: 42px; height: 42px; }
  .tier-badge { justify-content: center; margin: 6px 10px; padding: 5px; }
  .nav-item { justify-content: center; padding: 12px; }
  .nav-item:hover,
  .nav-item.active,
  .nav-item.router-link-active { padding-left: 12px; border-left: 3px solid var(--highlight); }
  .nav-item i { margin-right: 0; font-size: 18px; }
}
</style>
