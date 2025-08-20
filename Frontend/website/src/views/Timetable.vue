// Frontend/website/src/views/Timetable.vue
<template>
  <div class="timetable-page" :class="{ dark: isDark, light: !isDark }">
    <!-- Sidebar -->
    <Sidebar :active-nav="'timetable'" />

    <!-- Main Content -->
    <div class="main-content">
      <AppHeader title="Timetable">
        <template #actions>
          <ThemeToggle :is-dark="isDark" @toggle="toggleTheme" />
          <AppButton @click="goToToday">Today</AppButton>
          <AppButton @click="prevPeriod">Prev</AppButton>
          <AppButton @click="nextPeriod">Next</AppButton>
          <AppButton @click="setView('Week')">Week</AppButton>
          <AppButton @click="setView('Month')">Month</AppButton>
          <select v-model="selectedProject" @change="onProjectChange" class="ml-2 p-1 border rounded">
            <option value="">All Projects</option>
            <option v-for="p in projects" :key="p.id" :value="p.name">{{ p.name }}</option>
          </select>
        </template>
      </AppHeader>

      <div class="timetable-container">
        <!-- Week view -->
        <div v-if="currentView === 'Week'" class="week-grid">
          <!-- Time column -->
          <div class="time-slots">
            <div v-for="h in hours()" :key="'time-' + h" class="time-slot">
              <div class="time-display">
                <span class="hour">{{ h === 0 ? 12 : h > 12 ? h - 12 : h }}</span>
                <span class="period">{{ h < 12 ? 'AM' : 'PM' }}</span>
              </div>
            </div>
          </div>

          <!-- Day columns -->
          <div class="days-grid">
            <div
              v-for="day in visibleDays"
              :key="'week-' + day"
              class="day-column"
              :class="{ today: isSameDay(day, now) }"
            >
              <div
                v-for="h in hours()"
                :key="day + '-' + h"
                class="hour-slot"
              >
                <div
                  v-for="ev in getEventsForSlot(day, h)"
                  :key="ev.id"
                  class="event-block"
                  :class="['event-' + (ev.type || 'task')]"
                  :style="{ height: (ev.duration/60) * 80 + 'px' }"
                  @mouseenter="showTooltip(ev, $event)"
                  @mouseleave="hideTooltip"
                  @click="selectedEvent = ev"
                >
                  <div class="event-content">
                    <div class="event-title">{{ ev.title }}</div>
                    <div class="event-time">{{ formatTimeRange(ev) }}</div>
                    <div class="event-attendees" v-if="ev.members?.length">
                      <span v-for="m in ev.members" :key="m" class="attendee-chip">{{ m }}</span>
                    </div>
                    <div class="event-progress">
                      <div
                        class="event-priority"
                        :class="{
                          'priority-high': ev.priority === 'high',
                          'priority-medium': ev.priority === 'medium',
                          'priority-low': ev.priority === 'low'
                        }"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Month view -->
        <div v-else class="month-grid">
          <div
            v-for="day in visibleDays"
            :key="'month-' + day"
            class="month-cell"
            :class="{
              today: isSameDay(day, now),
              weekend: [0,6].includes(day.getDay()),
              'has-events': eventsForDate(day).length
            }"
          >
            <div class="cell-header">
              <span class="cell-date">{{ format(day, 'd') }}</span>
              <span v-if="eventsForDate(day).length" class="cell-event-count">{{ eventsForDate(day).length }}</span>
            </div>
            <div class="cell-events">
              <div
                v-for="ev in eventsForDate(day).slice(0,3)"
                :key="ev.id"
                class="month-event"
                @mouseenter="showTooltip(ev, $event)"
                @mouseleave="hideTooltip"
                @click="selectedEvent = ev"
              >
                <span class="event-dot" :class="'priority-' + (ev.priority || 'low')"></span>
                <span class="event-text">{{ ev.title }}</span>
              </div>
              <div v-if="eventsForDate(day).length > 3" class="more-events">
                +{{ eventsForDate(day).length - 3 }} more
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tooltip -->
      <div
        v-if="tooltipEvent"
        class="event-tooltip"
        :style="tooltipStyle"
      >
        <div class="tooltip-title">{{ tooltipEvent.title }}</div>
        <div class="tooltip-time">{{ formatTimeRange(tooltipEvent) }}</div>
        <div v-if="tooltipEvent.members?.length" class="tooltip-members">
          <span v-for="m in tooltipEvent.members" :key="m" class="attendee-chip">{{ m }}</span>
        </div>
        <StateBadge :state="tooltipEvent.state" />
      </div>

      <!-- Event Modal -->
      <div v-if="selectedEvent" class="modal-overlay" @click.self="selectedEvent = null">
        <div class="event-modal">
          <h3 class="modal-title">{{ selectedEvent.title }}</h3>
          <p><strong>Project:</strong> {{ selectedEvent.project }}</p>
          <p><strong>Time:</strong> {{ formatTimeRange(selectedEvent) }}</p>
          <p><strong>Status:</strong> <StateBadge :state="selectedEvent.state" /></p>
          <p v-if="selectedEvent.members?.length"><strong>Members:</strong>
            <span v-for="m in selectedEvent.members" :key="m" class="attendee-chip">{{ m }}</span>
          </p>
          <div class="modal-actions">
            <AppButton @click="markTaskAs(selectedEvent, 'complete')">Mark Complete</AppButton>
            <AppButton @click="selectedEvent = null">Close</AppButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  format,
  startOfWeek,
  endOfWeek,
  startOfMonth,
  endOfMonth,
  addDays,
  addWeeks,
  addMonths,
  parseISO,
  isSameDay,
  addMinutes,
  addHours,
  startOfDay,
  isWithinInterval,
  differenceInMinutes
} from 'date-fns'

import Sidebar from '@/components/layout/Sidebar.vue'
import AppHeader from '@/components/layout/AppHeader.vue'
import ThemeToggle from '@/components/layout/ThemeToggle.vue'
import AppButton from '@/components/ui/AppButton.vue'
import StateBadge from '@/components/ui/StateBadge.vue'

import { visualizationService } from '@/services/visualizations'
import { projectService } from '@/services/projects'
import { taskService } from '@/services/tasks'
import { authService } from '@/services/auth'
import { useUserStore } from '@/store/user'

export default {
  name: 'TimetablePage',
  components: { Sidebar, AppHeader, ThemeToggle, AppButton, StateBadge },

  data() {
    return {
      // theme / nav
      isDark: true,
      activeNav: 'timetable',

      // view
      currentView: 'Week', // 'Week' | 'Month'
      currentDate: new Date(),

      // ui
      loading: false,
      error: null,

      // projects & filter
      projects: [],
      selectedProject: '',

      // hour grid bounds (keeps original behaviour)
      hourStart: 6,
      hourEnd: 22,

      // events loaded from API
      events: [],

      // tooltip & selection
      selectedEvent: null,
      tooltipEvent: null,
      tooltipStyle: { top: '0px', left: '0px' },

      // store + live time
      userStore: null,
      now: new Date()
    }
  },

  computed: {
    // expose period bounds depending on view
    periodStart() {
      return this.currentView === 'Month'
        ? startOfMonth(this.currentDate)
        : startOfWeek(this.currentDate, { weekStartsOn: 1 })
    },
    periodEnd() {
      return this.currentView === 'Month'
        ? endOfMonth(this.currentDate)
        : endOfWeek(this.currentDate, { weekStartsOn: 1 })
    },

    periodLabel() {
      if (this.currentView === 'Month') return format(this.currentDate, 'MMMM yyyy')
      const s = startOfWeek(this.currentDate, { weekStartsOn: 1 })
      const e = endOfWeek(this.currentDate, { weekStartsOn: 1 })
      return `${format(s, 'MMM d')} — ${format(e, 'MMM d, yyyy')}`
    },

    visibleDays() {
      const days = []
      let cur = this.periodStart
      while (cur <= this.periodEnd) {
        days.push(new Date(cur))
        cur = addDays(cur, 1)
      }
      return days
    },

    // used by template to decide whether to show current-time line
    showCurrentTimeIndicator() {
      return this.visibleDays.some(d => isSameDay(d, new Date()))
    }
  },

  methods: {
    // expose date-fns functions that the template calls directly (template can't access imports)
    format,     // allows calling `format(...)` in template
    isSameDay,  // allows calling `isSameDay(...)` in template

    // theme
    toggleTheme() {
      this.isDark = !this.isDark
      localStorage.setItem('zainpm-theme', this.isDark ? 'dark' : 'light')
    },

    // Projects
    async loadProjects() {
      this.loading = true
      this.error = null
      try {
        const user = authService.getCurrentUser()
        const companyName = (user && user.company_name) || (this.userStore && this.userStore.companyName)
        if (!companyName) {
          this.error = 'company name not found; cannot load projects'
          return
        }
        const resp = await projectService.getProjects(companyName)
        this.projects = (resp && resp.projects) ? resp.projects : []
        if (!this.selectedProject && this.projects.length) this.selectedProject = this.projects[0].name
      } catch (err) {
        this.error = err?.message || String(err)
      } finally {
        this.loading = false
      }
    },

    // Timetable loading (uses visualizationService, conservative parsing)
    async loadTimetable() {
      this.loading = true
      this.error = null
      try {
        const user = authService.getCurrentUser()
        const companyName = (user && user.company_name) || (this.userStore && this.userStore.companyName)
        if (!companyName) {
          this.error = 'company name not found; cannot load timetable'
          return
        }

        const payload = await visualizationService.getTimetable(companyName, this.selectedProject || null)
        const rawEvents = Array.isArray(payload) ? payload : (payload.events || [])

        this.events = rawEvents.map(ev => {
          const start = ev.start ? parseISO(ev.start)
                        : ev.start_time ? parseISO(ev.start_time)
                        : ev.start_time_iso ? parseISO(ev.start_time_iso)
                        : new Date()

          let end = null
          if (ev.end) end = parseISO(ev.end)
          else if (ev.end_time) end = parseISO(ev.end_time)
          else if (ev.expected_duration != null) end = addMinutes(start, Number(ev.expected_duration) || 0)
          else if (ev.duration_minutes != null) end = addMinutes(start, Number(ev.duration_minutes) || 0)
          else end = addMinutes(start, 60)

          const title = ev.title || ev.task_name || ev.name || ev.task || 'Untitled'
          const proj = ev.project_name || ev.project || ev.proj_name || ''
          const members = ev.members || ev.team || ev.assignees || []

          const priority = (ev.priority || ev.priority_level || ev.task_priority || '').toString().toLowerCase() || null
          const progress = ev.progress != null ? Number(ev.progress) : (ev.status_percentage ?? 0)
          const state = ev.state || ev.status || ev.task_state || 'unknown'

          return {
            id: ev.id ?? `${proj}:${title}:${start.toISOString()}`,
            title,
            project: proj,
            members,
            start,
            end,
            duration: differenceInMinutes(end, start),
            progress,
            state,
            priority,
            raw: ev
          }
        })
      } catch (err) {
        this.error = err?.message || String(err)
      } finally {
        this.loading = false
      }
    },

    // Interactive task updates (use taskService)
    async markTaskAs(task, state) {
      try {
        const user = authService.getCurrentUser()
        if (!user?.company_name) throw new Error('Not authenticated')
        const taskName = task.raw?.task_name || task.title || task.raw?.name || task.raw?.task
        await taskService.markTaskAs(user.company_name, task.project, taskName, state)
        await this.loadTimetable()
      } catch (e) {
        alert(`Failed to update task: ${e?.message || e}`)
      }
    },

    async postponeTask(task, newStartISO, newDurationMinutes) {
      try {
        const user = authService.getCurrentUser()
        if (!user?.company_name) throw new Error('Not authenticated')
        const taskName = task.raw?.task_name || task.title || task.raw?.name || task.raw?.task
        await taskService.postponeTask(user.company_name, task.project, taskName, newStartISO, newDurationMinutes)
        await this.loadTimetable()
      } catch (e) {
        alert(`Failed to postpone: ${e?.message || e}`)
      }
    },

    // navigation
    prevPeriod() {
      if (this.currentView === 'Month') this.currentDate = addMonths(this.currentDate, -1)
      else this.currentDate = addWeeks(this.currentDate, -1)
    },
    nextPeriod() {
      if (this.currentView === 'Month') this.currentDate = addMonths(this.currentDate, 1)
      else this.currentDate = addWeeks(this.currentDate, 1)
    },
    goToToday() {
      this.currentDate = new Date()
    },
    setView(v) {
      this.currentView = v
    },

    // helpers used by template
    hours() {
      const start = Number(this.hourStart) || 0
      const end = Number(this.hourEnd) || 23
      const arr = []
      for (let h = start; h <= end; h++) arr.push(h)
      return arr
    },

    eventsForDate(date) {
      return this.events.filter(e =>
        isSameDay(e.start, date) || isWithinInterval(date, { start: e.start, end: e.end })
      )
    },

    formatTimeRange(ev) {
      if (!ev || !ev.start) return ''
      return `${format(ev.start, 'HH:mm')} — ${format(ev.end, 'HH:mm')}`
    },

    getEventsForSlot(date, hour) {
      const slotStart = addHours(startOfDay(date), hour)
      const slotEnd = addHours(slotStart, 1)
      return this.events.filter(e =>
        isWithinInterval(e.start, { start: slotStart, end: slotEnd }) ||
        isWithinInterval(e.end, { start: slotStart, end: slotEnd }) ||
        (e.start <= slotStart && e.end >= slotEnd)
      )
    },

    // tooltip
    showTooltip(ev, mouseEvent) {
      this.tooltipEvent = ev
      this.tooltipStyle = { top: `${mouseEvent.clientY + 8}px`, left: `${mouseEvent.clientX + 8}px` }
    },
    hideTooltip() {
      this.tooltipEvent = null
    },

    // filters change
    async onProjectChange() {
      await this.loadTimetable()
    }
  },

  async mounted() {
    const saved = localStorage.getItem('zainpm-theme')
    if (saved === 'light') this.isDark = false

    this.userStore = useUserStore()
    await this.loadProjects()
    await this.loadTimetable()

    this._nowTimer = setInterval(() => { this.now = new Date() }, 60 * 1000)
  },

  beforeUnmount() {
    if (this._nowTimer) clearInterval(this._nowTimer)
  }
}
</script>


<style scoped>
@import '@/assets/css/main.css';

.timetable-page {
  display: flex;
  height: 100vh;
  background-color: var(--bg-base);
  color: var(--text-primary);
  line-height: 1.6;
}

/* Timetable Controls */
.timetable-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: var(--bg-section);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.control-group {
  display: flex;
  align-items: center;
  gap: 16px;
}

.control-select {
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-base);
  color: var(--text-primary);
  font-size: 14px;
  min-width: 200px;
  transition: all 0.2s ease;
}

.control-select:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(0, 255, 247, 0.1);
}

.view-toggle {
  display: flex;
  background: var(--bg-base);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.toggle-btn {
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  font-weight: 500;
}

.toggle-btn:hover,
.toggle-btn.active {
  background: var(--primary);
  color: var(--dark-base);
}

.navigation-controls {
  display: flex;
  align-items: center;
  gap: 20px;
}

.week-navigation {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-btn {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.current-period {
  text-align: center;
  min-width: 220px;
}

.current-period h3 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
}

.period-subtitle {
  font-size: 12px;
  color: var(--text-secondary);
}

.today-btn {
  gap: 8px;
}

/* State Cards */
.state-card {
  background: var(--bg-section);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  padding: 60px 40px;
  text-align: center;
  margin-bottom: 20px;
}

.state-content {
  max-width: 400px;
  margin: 0 auto;
}

.state-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.loading .state-icon {
  color: var(--primary);
}

.error .state-icon {
  color: var(--danger);
}

.empty .state-icon {
  color: var(--text-secondary);
}

.state-card h3 {
  margin-bottom: 8px;
  font-size: 20px;
}

.state-card p {
  color: var(--text-secondary);
  margin-bottom: 20px;
  line-height: 1.6;
}

/* Timetable Container */
.timetable-container {
  background: var(--bg-section);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  overflow: hidden;
  position: relative;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* Week View */
.week-header {
  display: flex;
  background: rgba(0, 0, 0, 0.05);
  border-bottom: 2px solid var(--border-color);
}

.time-column {
  width: 80px;
  padding: 20px 16px;
  border-right: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
}

.time-label {
  font-weight: 600;
  font-size: 14px;
}

.day-header {
  flex: 1;
  padding: 16px 12px;
  text-align: center;
  border-right: 1px solid var(--border-color);
  transition: all 0.2s ease;
}

.day-header.today {
  background: rgba(0, 255, 247, 0.1);
  border-color: var(--primary);
}

.day-header.weekend {
  background: rgba(0, 0, 0, 0.02);
}

.day-info {
  margin-bottom: 8px;
}

.day-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
}

.day-number {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 2px;
}

.day-date {
  font-size: 12px;
  color: var(--text-secondary);
}

.day-stats {
  font-size: 11px;
  color: var(--text-secondary);
}

.event-count {
  background: rgba(0, 255, 247, 0.1);
  color: var(--primary);
  padding: 2px 6px;
  border-radius: 10px;
}

.week-grid {
  display: flex;
  max-height: 70vh;
  overflow-y: auto;
  position: relative;
}

.time-slots {
  width: 80px;
  border-right: 1px solid var(--border-color);
}

.time-slot {
  height: 80px;
  padding: 8px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  transition: background 0.2s ease;
}

.time-slot.current {
  background: rgba(0, 255, 247, 0.05);
}

.time-display {
  text-align: center;
}

.hour {
  display: block;
  font-size: 14px;
  font-weight: 600;
  line-height: 1;
}

.period {
  display: block;
  font-size: 10px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.days-grid {
  flex: 1;
  display: flex;
}

.day-column {
  flex: 1;
  border-right: 1px solid var(--border-color);
}

.day-column.weekend {
  background: rgba(0, 0, 0, 0.01);
}

.day-column.today {
  background: rgba(0, 255, 247, 0.02);
}

.hour-slot {
  height: 80px;
  border-bottom: 1px solid var(--border-color);
  position: relative;
  cursor: pointer;
  transition: background 0.2s ease;
}

.hour-slot:hover {
  background: rgba(0, 0, 0, 0.02);
}

.hour-slot.current {
  background: rgba(0, 255, 247, 0.05);
}

.event-block {
  position: absolute;
  left: 4px;
  right: 4px;
  top: 4px;
  bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 1;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.event-block:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.event-block.selected {
  transform: scale(1.02);
  box-shadow: 0 4px 20px rgba(0, 255, 247, 0.3);
  z-index: 2;
}

.event-content {
  padding: 8px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
}

.event-title {
  font-size: 11px;
  font-weight: 600;
  color: white;
  margin-bottom: 2px;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-time {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px;
}

.event-attendees {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  gap: 4px;
}

.event-priority {
  position: absolute;
  top: 0;
  right: 0;
  width: 4px;
  height: 100%;
  border-radius: 0 8px 8px 0;
}

.priority-high {
  background: #ff0066;
}

.priority-medium {
  background: #ffb300;
}

.priority-low {
  background: #00ffb3;
}

/* Event Type Classes */
.event-meeting {
  border-left: 4px solid #ff0066;
}

.event-review {
  border-left: 4px solid #00ffb3;
}

.event-presentation {
  border-left: 4px solid #ffb300;
}

.event-planning {
  border-left: 4px solid #00e0ff;
}

/* Month View */
.month-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: rgba(0, 0, 0, 0.05);
  border-bottom: 2px solid var(--border-color);
}

.month-day-header {
  padding: 16px 12px;
  text-align: center;
  font-weight: 600;
  font-size: 14px;
  border-right: 1px solid var(--border-color);
}

.month-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-auto-rows: 120px;
}

.month-cell {
  border-right: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
  padding: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.month-cell:hover {
  background: rgba(0, 0, 0, 0.02);
}

.month-cell.other-month {
  color: var(--text-secondary);
  background: rgba(0, 0, 0, 0.01);
}

.month-cell.today {
  background: rgba(0, 255, 247, 0.1);
}

.month-cell.weekend {
  background: rgba(0, 0, 0, 0.02);
}

.month-cell.selected {
  background: rgba(0, 255, 247, 0.15);
  border-color: var(--primary);
}

.month-cell.has-events {
  border-left: 3px solid var(--primary);
}

.cell-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.cell-date {
  font-weight: 600;
  font-size: 14px;
}

.cell-event-count {
  background: var(--primary);
  color: var(--dark-base);
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 9px;
  font-weight: 600;
}

.cell-events {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.month-event {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  padding: 2px 4px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: rgba(0, 0, 0, 0.05);
}

.month-event:hover {
  background: rgba(0, 0, 0, 0.1);
}

.event-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.event-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.more-events {
  font-size: 9px;
  color: var(--text-secondary);
  padding: 2px 4px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.more-events:hover {
  background: rgba(0, 0, 0, 0.1);
  color: var(--text-primary);
}

/* Current Time Line */
.current-time-line {
  background: #ff0066;
  height: 2px;
  position: absolute;
  z-index: 100;
  box-shadow: 0 0 10px rgba(255, 0, 102, 0.5);
}

.current-time-line::before {
  content: '';
  position: absolute;
  left: -4px;
  top: -4px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ff0066;
  box-shadow: 0 0 8px rgba(255, 0, 102, 0.5);
}

/* Event Modal */
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

.event-modal {
  background: var(--bg-section);
  color: var(--text-primary);
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.modal-header {
  padding: 24px;
  background: rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.event-header-info {
  flex: 1;
}

.modal-header h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
}

.event-type-badge {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(0, 255, 247, 0.1);
  color: var(--primary);
  display: inline-block;
}

.close-btn {
  background: transparent;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 0, 102, 0.1);
  color: var(--danger);
}

.modal-body {
  padding: 24px;
}

.event-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.detail-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.detail-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: rgba(0, 255, 247, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
  flex-shrink: 0;
}

.detail-content {
  flex: 1;
}

.detail-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
  font-weight: 500;
}

.detail-value {
  display: block;
  font-size: 14px;
  font-weight: 600;
}

.event-description {
  margin-bottom: 24px;
}

.event-description h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
}

.event-description p {
  line-height: 1.6;
  color: var(--text-secondary);
}

.event-attendees h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
}

.attendees-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.attendee-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(0, 255, 247, 0.1);
  color: var(--primary);
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

.modal-footer {
  padding: 24px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.02);
}

.action-buttons {
  display: flex;
  gap: 12px;
}

/* Event Tooltip */
.event-tooltip {
  background: var(--bg-section);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  max-width: 280px;
  z-index: 1000;
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.tooltip-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  flex: 1;
  line-height: 1.3;
}

.tooltip-time {
  font-size: 11px;
  color: var(--text-secondary);
  margin-left: 8px;
}

.tooltip-body {
  font-size: 12px;
}

.tooltip-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  color: var(--text-secondary);
}

.tooltip-row i {
  width: 12px;
  font-size: 10px;
  color: var(--primary);
}

/* Responsive Design */
@media (max-width: 1200px) {
  .timetable-controls {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .control-group,
  .navigation-controls {
    justify-content: space-between;
  }
}

@media (max-width: 992px) {
  .time-column {
    width: 60px;
  }
  
  .time-slots {
    width: 60px;
  }
  
  .event-details-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .timetable-controls {
    padding: 16px;
  }
  
  .control-group {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .control-select {
    min-width: auto;
  }
  
  .navigation-controls {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .week-navigation {
    justify-content: space-between;
  }
  
  .current-period {
    min-width: auto;
  }
  
  .week-grid {
    min-width: 600px;
  }
  
  .timetable-container {
    overflow-x: auto;
  }
  
  .month-grid {
    grid-auto-rows: 100px;
  }
  
  .state-card {
    padding: 40px 20px;
  }
  
  .state-icon {
    font-size: 36px;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 16px;
  }
  
  .modal-footer {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .action-buttons {
    justify-content: space-between;
  }
}

@media (max-width: 480px) {
  .time-column {
    width: 50px;
  }
  
  .time-slots {
    width: 50px;
  }
  
  .hour {
    font-size: 12px;
  }
  
  .period {
    font-size: 9px;
  }
  
  .day-header {
    padding: 12px 8px;
  }
  
  .day-name {
    font-size: 12px;
  }
  
  .day-number {
    font-size: 16px;
  }
  
  .event-title {
    font-size: 10px;
  }
  
  .event-time {
    font-size: 9px;
  }
  
  .month-grid {
    grid-auto-rows: 80px;
  }
  
  .cell-date {
    font-size: 12px;
  }
  
  .month-event {
    font-size: 9px;
  }
}

/* Dark mode adjustments */
.dark .timetable-container {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.dark .event-modal {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.dark .event-tooltip {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.dark .event-block {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.dark .event-block:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
}

.dark .detail-card {
  background: rgba(255, 255, 255, 0.05);
}

/* Light mode specific adjustments */
.light .week-header,
.light .month-header {
  background: rgba(0, 0, 0, 0.02);
}

.light .day-header.today {
  background: rgba(0, 107, 128, 0.1);
  border-color: var(--primary);
}

.light .month-cell.today {
  background: rgba(0, 107, 128, 0.1);
}

.light .month-cell.selected {
  background: rgba(0, 107, 128, 0.15);
}

.light .hour-slot.current,
.light .time-slot.current {
  background: rgba(0, 107, 128, 0.05);
}

.light .day-column.today {
  background: rgba(0, 107, 128, 0.02);
}

.light .event-type-badge {
  background: rgba(0, 107, 128, 0.1);
  color: var(--primary);
}

.light .attendee-chip {
  background: rgba(0, 107, 128, 0.1);
  color: var(--primary);
}

.light .detail-icon {
  background: rgba(0, 107, 128, 0.1);
  color: var(--primary);
}

.light .event-count {
  background: rgba(0, 107, 128, 0.1);
  color: var(--primary);
}

.light .cell-event-count {
  background: var(--primary);
  color: white;
}

/* Scrollbar styling */
.week-grid::-webkit-scrollbar,
.timetable-container::-webkit-scrollbar,
.event-modal::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.week-grid::-webkit-scrollbar-track,
.timetable-container::-webkit-scrollbar-track,
.event-modal::-webkit-scrollbar-track {
  background: var(--bg-base);
  border-radius: 4px;
}

.week-grid::-webkit-scrollbar-thumb,
.timetable-container::-webkit-scrollbar-thumb,
.event-modal::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}

.week-grid::-webkit-scrollbar-thumb:hover,
.timetable-container::-webkit-scrollbar-thumb:hover,
.event-modal::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

/* Animation for event creation */
@keyframes eventCreate {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.event-block.new {
  animation: eventCreate 0.3s ease-out;
}

/* Loading animation */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.fa-spinner {
  animation: spin 1s linear infinite;
}

/* Hover effects for interactive elements */
.hour-slot::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 255, 247, 0.05);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.hour-slot:hover::before {
  opacity: 1;
}

.month-cell::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 255, 247, 0.03);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.month-cell:hover::before {
  opacity: 1;
}

/* Focus styles for accessibility */
.control-select:focus,
.toggle-btn:focus,
.nav-btn:focus,
.today-btn:focus {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

.event-block:focus {
  outline: 2px solid var(--primary);
  outline-offset: 1px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .event-block {
    border: 2px solid currentColor;
  }
  
  .day-header.today,
  .month-cell.today {
    border: 2px solid var(--primary);
  }
  
  .current-time-line {
    height: 3px;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .event-block,
  .hour-slot,
  .month-cell,
  .toggle-btn,
  .close-btn {
    transition: none;
  }
  
  .fa-spinner {
    animation: none;
  }
  
  .event-block.new {
    animation: none;
  }
}

/* Print styles */
@media print {
  .timetable-controls,
  .modal-overlay,
  .event-tooltip {
    display: none !important;
  }
  
  .timetable-container {
    box-shadow: none;
    border: 1px solid #000;
  }
  
  .event-block {
    box-shadow: none;
    border: 1px solid #000;
  }
  
  .week-grid {
    max-height: none;
    overflow: visible;
  }
}
</style>