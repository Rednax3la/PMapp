// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import AdminDashboard from '../views/AdminDashboard.vue'
import Projects from '../views/Projects.vue'
import Tasks from '@/views/Tasks.vue'
import Gantt from '@/views/Gantt.vue'
import Timetable from '@/views/Timetable.vue'
import Reports from '@/views/Reports.vue'
import Members from '@/views/Members.vue'
import Settings from '@/views/Settings.vue'
import Help from '@/views/Help.vue'


const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: AdminDashboard
  },
  {
    path: '/projects',
    name: 'Projects',
    component: Projects
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: Tasks
  },
  {
    path: '/gantt',
    name: 'Gantt',
    component: Gantt
  },
  {
    path: '/timetable',
    name: 'Timetable',
    component: Timetable
  },
  {
    path: '/reports',
    name: 'Reports',
    component: Reports
  },
  {
    path: '/members',
    name: 'Members',
    component: Members
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  },
  {
    path: '/help',
    name: 'Help',
    component: Help
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router