import { createRouter, createWebHistory } from 'vue-router'
import { authService } from '@/services/auth'

import AuthPage from '@/views/AuthPage.vue'
import AdminDashboard from '@/views/AdminDashboard.vue'
import MemberDashboard from '@/views/MemberDashboard.vue'
import Projects from '@/views/Projects.vue'
import Tasks from '@/views/Tasks.vue'
import Gantt from '@/views/Gantt.vue'
import Timetable from '@/views/Timetable.vue'
import Reports from '@/views/Reports.vue'
import Members from '@/views/Members.vue'
import Settings from '@/views/Settings.vue'
import Help from '@/views/Help.vue'
import Subscription from '@/views/Subscription.vue'

const routes = [
  {
    path: '/auth',
    name: 'Auth',
    component: AuthPage,
    meta: { requiresGuest: true }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, requiresAdmin: true, title: 'Dashboard' }
  },
  {
    path: '/member-dashboard',
    name: 'MemberDashboard',
    component: MemberDashboard,
    meta: { requiresAuth: true, requiresMember: true, title: 'My Dashboard' }
  },
  {
    path: '/projects',
    name: 'Projects',
    component: Projects,
    meta: { requiresAuth: true, title: 'Projects' }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: Tasks,
    meta: { requiresAuth: true, title: 'Tasks' }
  },
  {
    path: '/gantt',
    name: 'Gantt',
    component: Gantt,
    meta: { requiresAuth: true, title: 'Gantt Chart' }
  },
  {
    path: '/timetable',
    name: 'Timetable',
    component: Timetable,
    meta: { requiresAuth: true, title: 'Timetable' }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: Reports,
    meta: { requiresAuth: true, requiresAdmin: true, title: 'Reports' }
  },
  {
    path: '/members',
    name: 'Members',
    component: Members,
    meta: { requiresAuth: true, requiresAdmin: true, title: 'Members' }
  },
  {
    path: '/subscription',
    name: 'Subscription',
    component: Subscription,
    meta: { requiresAuth: true, requiresAdmin: true, title: 'Subscription' }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { requiresAuth: true, title: 'Settings' }
  },
  {
    path: '/help',
    name: 'Help',
    component: Help,
    meta: { requiresAuth: true, title: 'Help' }
  },
  {
    path: '/login',
    redirect: () => {
      if (!authService.isAuthenticated()) return '/auth'
      const user = authService.getCurrentUser()
      return user?.role === 'member' ? '/member-dashboard' : '/'
    }
  },
  {
    path: '/logout',
    name: 'Logout',
    beforeEnter: async (to, from, next) => {
      await authService.logout()
      next('/auth')
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: () => {
      if (!authService.isAuthenticated()) return '/auth'
      const user = authService.getCurrentUser()
      return user?.role === 'member' ? '/member-dashboard' : '/'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Global navigation guard with role-based routing
router.beforeEach((to, from, next) => {
  const isAuthenticated = authService.isAuthenticated()
  const user = authService.getCurrentUser()
  const role = user?.role || null

  // Unauthenticated trying to access protected route
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/auth')
    return
  }

  // Already authenticated trying to access guest-only page
  if (to.meta.requiresGuest && isAuthenticated) {
    next(role === 'member' ? '/member-dashboard' : '/')
    return
  }

  // Admin-only route accessed by a member
  if (to.meta.requiresAdmin && role === 'member') {
    next('/member-dashboard')
    return
  }

  // Member-only route accessed by admin/manager
  if (to.meta.requiresMember && role && role !== 'member') {
    next('/')
    return
  }

  next()
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} - ZainPM` : 'ZainPM'
})

export default router
