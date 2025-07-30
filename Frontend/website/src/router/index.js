//Frontend/website/src/router/index.js

import { createRouter, createWebHistory } from 'vue-router'
import { authService } from '@/services/auth'

// Import components
import AuthPage from '@/views/AuthPage.vue'
import AdminDashboard from '@/views/AdminDashboard.vue'
import Projects from '@/views/Projects.vue'
import Tasks from '@/views/Tasks.vue'
import Gantt from '@/views/Gantt.vue'
import Timetable from '@/views/Timetable.vue'
import Reports from '@/views/Reports.vue'
import Members from '@/views/Members.vue'
import Settings from '@/views/Settings.vue'
import Help from '@/views/Help.vue'

const routes = [
  {
    path: '/auth',
    name: 'Auth',
    component: AuthPage,
    meta: { 
      requiresGuest: true // Only accessible when not authenticated
    }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: AdminDashboard,
    meta: { 
      requiresAuth: true,
      title: 'Dashboard'
    }
  },
  {
    path: '/projects',
    name: 'Projects',
    component: Projects,
    meta: { 
      requiresAuth: true,
      title: 'Projects'
    }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: Tasks,
    meta: { 
      requiresAuth: true,
      title: 'Tasks'
    }
  },
  {
    path: '/gantt',
    name: 'Gantt',
    component: Gantt,
    meta: { 
      requiresAuth: true,
      title: 'Gantt Chart'
    }
  },
  {
    path: '/timetable',
    name: 'Timetable',
    component: Timetable,
    meta: { 
      requiresAuth: true,
      title: 'Timetable'
    }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: Reports,
    meta: { 
      requiresAuth: true,
      title: 'Reports'
    }
  },
  {
    path: '/members',
    name: 'Members',
    component: Members,
    meta: { 
      requiresAuth: true,
      title: 'Members'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { 
      requiresAuth: true,
      title: 'Settings'
    }
  },
  {
    path: '/help',
    name: 'Help',
    component: Help,
    meta: { 
      requiresAuth: true,
      title: 'Help'
    }
  },
  {
    path: '/login',
    redirect: () =>
      authService.isAuthenticated() ? '/' : '/auth'
  },
  {
    path: '/logout',
    name: 'Logout',
    // as soon as we enter this route, clear auth and bounce to /auth
    beforeEnter: (to, from, next) => {
    authService.logout()          // clear tokens / state
    next('/auth')                 // send them to the login page
    }  
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: () =>
      authService.isAuthenticated() ? '/' : '/auth'
  }

]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Global navigation guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = authService.isAuthenticated()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Redirect to auth page if not authenticated
    next('/auth')
    return
  }
  
  // Check if route requires guest (not authenticated)
  if (to.meta.requiresGuest && isAuthenticated) {
    // Redirect to dashboard if already authenticated
    next('/')
    return
  }
  
  // If no authentication required or user is properly authenticated
  next()
})

// Set page title based on route meta
router.afterEach((to) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - ZainPM`
  } else {
    document.title = 'ZainPM'
  }
})

export default router