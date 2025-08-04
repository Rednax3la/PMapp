// Frontend/website/src/views/Timetable.vue
<template>
  <div class="timetable-page" :class="{ dark: isDark, light: !isDark }">
    <!-- Sidebar -->
    <Sidebar :active-nav="activeNav" @nav-change="setActiveNav" />
    
    <!-- Main Content -->
    <div class="main-content">
      <AppHeader title="Timetable">
        <template #actions>
          <ThemeToggle :is-dark="isDark" @toggle="toggleTheme" />
          <AppButton variant="primary" icon="fas fa-plus">
            Add Event
          </AppButton>
          <AppButton variant="secondary" icon="fas fa-calendar-alt">
            View Calendar
          </AppButton>
        </template>
      </AppHeader>
      
      <!-- Timetable Controls -->
      <div class="timetable-controls">
        <div class="control-group">
          <select v-model="selectedProject" @change="loadTimetableData" class="control-select">
            <option value="">Select Project</option>
            <option v-for="project in projects" :key="project.id" :value="project.name">
              {{ project.name }}
            </option>
          </select>
          
          <div class="view-toggle">
            <button 
              v-for="view in viewTypes" 
              :key="view" 
              :class="['toggle-btn', { active: currentView === view }]"
              @click="currentView = view"
            >
              {{ view }}
            </button>
          </div>
        </div>
        
        <div class="navigation-controls">
          <div class="week-navigation">
            <AppButton @click="previousPeriod" variant="outline" class="nav-btn">
              <i class="fas fa-chevron-left"></i>
            </AppButton>
            <div class="current-period">
              <h3>{{ currentPeriodLabel }}</h3>
              <span class="period-subtitle">{{ periodSubtitle }}</span>
            </div>
            <AppButton @click="nextPeriod" variant="outline" class="nav-btn">
              <i class="fas fa-chevron-right"></i>
            </AppButton>
          </div>
          
          <AppButton @click="goToToday" variant="primary" class="today-btn">
            <i class="fas fa-calendar-day"></i>
            Today
          </AppButton>
        </div>
      </div>
      
      <!-- Loading State -->
      <div v-if="loading" class="state-card loading">
        <div class="state-content">
          <i class="fas fa-spinner fa-spin state-icon"></i>
          <p>Loading timetable...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-if="error && !loading" class="state-card error">
        <div class="state-content">
          <i class="fas fa-exclamation-triangle state-icon"></i>
          <p>{{ error }}</p>
          <AppButton @click="loadTimetableData" variant="primary" class="btn-sm">
            Retry
          </AppButton>
        </div>
      </div>

      <!-- Timetable Grid -->
      <div v-if="!loading && !error && selectedProject" class="timetable-container">
        <!-- Week View -->
        <div v-if="currentView === 'Week'" class="week-view">
          <div class="week-header">
            <div class="time-column">
              <div class="time-label">Time</div>
            </div>
            <div 
              v-for="day in weekDays" 
              :key="day.dateKey" 
              class="day-header"
              :class="{ 
                today: isToday(day.date),
                weekend: isWeekend(day.date)
              }"
            >
              <div class="day-info">
                <div class="day-name">{{ day.name }}</div>
                <div class="day-number">{{ day.number }}</div>
                <div class="day-date">{{ day.month }}</div>
              </div>
              <div class="day-stats">
                <span class="event-count">{{ getEventsForDate(day.date).length }} events</span>
              </div>
            </div>
          </div>
          
          <div class="week-grid" ref="weekGrid">
            <div class="time-slots">
              <div 
                v-for="hour in timeSlots" 
                :key="hour" 
                class="time-slot"
                :class="{ current: isCurrentHour(hour) }"
              >
                <div class="time-display">
                  <span class="hour">{{ formatHour(hour) }}</span>
                  <span class="period">{{ formatPeriod(hour) }}</span>
                </div>
              </div>
            </div>
            
            <div class="days-grid">
              <div 
                v-for="day in weekDays" 
                :key="day.dateKey" 
                class="day-column"
                :class="{ 
                  today: isToday(day.date),
                  weekend: isWeekend(day.date)
                }"
              >
                <div 
                  v-for="hour in timeSlots" 
                  :key="`${day.dateKey}-${hour}`" 
                  class="hour-slot"
                  :class="{ current: isToday(day.date) && isCurrentHour(hour) }"
                  @click="createEvent(day.date, hour)"
                >
                  <div 
                    v-for="event in getEventsForSlot(day.date, hour)" 
                    :key="event.id" 
                    class="event-block"
                    :class="[getEventTypeClass(event), { selected: selectedEvent?.id === event.id }]"
                    :style="getEventStyle(event)"
                    @click.stop="selectEvent(event)"
                    @mouseover="showEventTooltip(event, $event)"
                    @mouseleave="hideEventTooltip"
                  >
                    <div class="event-content">
                      <div class="event-title">{{ event.title }}</div>
                      <div class="event-time">{{ event.time }}</div>
                      <div class="event-attendees" v-if="event.attendees?.length">
                        <i class="fas fa-users"></i>
                        {{ event.attendees.length }}
                      </div>
                    </div>
                    <div class="event-priority" :class="`priority-${event.priority}`"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Month View -->
        <div v-if="currentView === 'Month'" class="month-view">
          <div class="month-header">
            <div v-for="day in dayNames" :key="day" class="month-day-header">
              {{ day }}
            </div>
          </div>
          
          <div class="month-grid">
            <div 
              v-for="date in monthDates" 
              :key="date.dateKey" 
              class="month-cell"
              :class="{ 
                'other-month': !date.currentMonth,
                'today': isToday(date.date),
                'weekend': isWeekend(date.date),
                'selected': selectedDate && date.dateKey === formatDateKey(selectedDate),
                'has-events': getEventsForDate(date.date).length > 0
              }"
              @click="selectDate(date.date)"
            >
              <div class="cell-header">
                <span class="cell-date">{{ date.day }}</span>
                <span class="cell-event-count" v-if="getEventsForDate(date.date).length > 0">
                  {{ getEventsForDate(date.date).length }}
                </span>
              </div>
              <div class="cell-events">
                <div 
                  v-for="(event) in getEventsForDate(date.date).slice(0, 3)" 
                  :key="event.id" 
                  class="month-event"
                  :class="getEventTypeClass(event)"
                  @click.stop="selectEvent(event)"
                >
                  <div class="event-dot" :style="{ background: getEventColor(event) }"></div>
                  <span class="event-text">{{ event.title }}</span>
                </div>
                <div 
                  v-if="getEventsForDate(date.date).length > 3" 
                  class="more-events"
                  @click.stop="showMoreEvents(date.date)"
                >
                  +{{ getEventsForDate(date.date).length - 3 }} more
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Current Time Indicator -->
        <div 
          v-if="currentView === 'Week' && showCurrentTimeIndicator" 
          class="current-time-line" 
          :style="getCurrentTimeStyle()"
        ></div>
      </div>

      <!-- No Project Selected -->
      <div v-if="!loading && !error && !selectedProject" class="state-card empty">
        <div class="state-content">
          <i class="fas fa-calendar-alt state-icon"></i>
          <h3>No Project Selected</h3>
          <p>Select a project from the dropdown to view its timetable and events.</p>
        </div>
      </div>
      
      <!-- Event Details Modal -->
      <div v-if="selectedEvent" class="modal-overlay" @click.self="selectedEvent = null">
        <div class="event-modal">
          <div class="modal-header">
            <div class="event-header-info">
              <h3>{{ selectedEvent.title }}</h3>
              <div class="event-type-badge" :class="getEventTypeClass(selectedEvent)">
                {{ selectedEvent.type }}
              </div>
            </div>
            <button class="close-btn" @click="selectedEvent = null">
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <div class="modal-body">
            <div class="event-details-grid">
              <div class="detail-card">
                <div class="detail-icon">
                  <i class="fas fa-clock"></i>
                </div>
                <div class="detail-content">
                  <span class="detail-label">Time</span>
                  <span class="detail-value">{{ selectedEvent.time }} - {{ selectedEvent.endTime }}</span>
                </div>
              </div>
              
              <div class="detail-card">
                <div class="detail-icon">
                  <i class="fas fa-calendar"></i>
                </div>
                <div class="detail-content">
                  <span class="detail-label">Date</span>
                  <span class="detail-value">{{ formatEventDate(selectedEvent.date) }}</span>
                </div>
              </div>
              
              <div class="detail-card">
                <div class="detail-icon">
                  <i class="fas fa-project-diagram"></i>
                </div>
                <div class="detail-content">
                  <span class="detail-label">Project</span>
                  <span class="detail-value">{{ selectedEvent.project }}</span>
                </div>
              </div>
              
              <div class="detail-card" v-if="selectedEvent.location">
                <div class="detail-icon">
                  <i class="fas fa-map-marker-alt"></i>
                </div>
                <div class="detail-content">
                  <span class="detail-label">Location</span>
                  <span class="detail-value">{{ selectedEvent.location }}</span>
                </div>
              </div>
            </div>
            
            <div class="event-description" v-if="selectedEvent.description">
              <h4>Description</h4>
              <p>{{ selectedEvent.description }}</p>
            </div>
            
            <div class="event-attendees" v-if="selectedEvent.attendees?.length">
              <h4>Attendees ({{ selectedEvent.attendees.length }})</h4>
              <div class="attendees-list">
                <div 
                  v-for="attendee in selectedEvent.attendees" 
                  :key="attendee" 
                  class="attendee-chip"
                >
                  <i class="fas fa-user"></i>
                  {{ attendee }}
                </div>
              </div>
            </div>
          </div>
          
          <div class="modal-footer">
            <AppButton variant="outline" @click="selectedEvent = null">
              Close
            </AppButton>
            <div class="action-buttons">
              <AppButton variant="secondary" @click="editEvent">
                <i class="fas fa-edit"></i>
                Edit
              </AppButton>
              <AppButton variant="danger" @click="deleteEvent">
                <i class="fas fa-trash"></i>
                Delete
              </AppButton>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Event Tooltip -->
      <div 
        v-if="tooltipEvent" 
        class="event-tooltip" 
        :style="tooltipStyle"
        ref="tooltip"
      >
        <div class="tooltip-header">
          <h4>{{ tooltipEvent.title }}</h4>
          <span class="tooltip-time">{{ tooltipEvent.time }}</span>
        </div>
        <div class="tooltip-body">
          <div class="tooltip-row" v-if="tooltipEvent.location">
            <i class="fas fa-map-marker-alt"></i>
            <span>{{ tooltipEvent.location }}</span>
          </div>
          <div class="tooltip-row" v-if="tooltipEvent.attendees?.length">
            <i class="fas fa-users"></i>
            <span>{{ tooltipEvent.attendees.length }} attendees</span>
          </div>
          <div class="tooltip-row">
            <i class="fas fa-tag"></i>
            <span>{{ tooltipEvent.type }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { 
  format, 
  startOfWeek, 
  endOfWeek, 
  addDays, 
  addWeeks, 
  addMonths,
  startOfMonth,
  endOfMonth,
  isSameDay,
  isToday as checkIsToday,
  isWeekend as checkIsWeekend,
  getHours,
  getMinutes
} from 'date-fns';
import Sidebar from '@/components/layout/Sidebar.vue';
import AppHeader from '@/components/layout/AppHeader.vue';
import ThemeToggle from '@/components/layout/ThemeToggle.vue';
import AppButton from '@/components/ui/AppButton.vue';

export default {
  name: 'TimetablePage',
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
    const activeNav = ref('timetable');
    const setActiveNav = (target) => {
      activeNav.value = target;
    };

    // Timetable State
    const currentView = ref('Week');
    const viewTypes = ref(['Week', 'Month']);
    const currentDate = ref(new Date());
    const selectedDate = ref(null);
    const selectedEvent = ref(null);
    const selectedProject = ref('');
    const loading = ref(false);
    const error = ref(null);

    // Tooltip
    const tooltipEvent = ref(null);
    const tooltipStyle = ref({});

    // Current time tracking
    const currentTime = ref(new Date());
    let timeInterval = null;

    // Sample Projects
    const projects = ref([
      { id: 1, name: 'Website Redesign' },
      { id: 2, name: 'Mobile App Development' },
      { id: 3, name: 'Marketing Campaign' },
      { id: 4, name: 'Backend Infrastructure' }
    ]);

    // Events Data
    const events = ref([
      {
        id: 1,
        title: 'Daily Standup',
        description: 'Daily team synchronization meeting to discuss progress and blockers',
        date: new Date(),
        time: '09:00',
        endTime: '09:30',
        hour: 9,
        project: 'Website Redesign',
        type: 'Meeting',
        priority: 'high',
        location: 'Conference Room A',
        attendees: ['Sarah Johnson', 'Michael Chen', 'David Kim', 'Emma Rodriguez'],
        color: '#00fff7'
      },
      {
        id: 2,
        title: 'Design Review Session',
        description: 'Review latest UI/UX designs and provide feedback',
        date: new Date(),
        time: '14:00',
        endTime: '15:30',
        hour: 14,
        project: 'Website Redesign',
        type: 'Review',
        priority: 'medium',
        location: 'Design Studio',
        attendees: ['Sarah Johnson', 'Emma Rodriguez'],
        color: '#00ffb3'
      },
      {
        id: 3,
        title: 'Client Presentation',
        description: 'Present project progress and milestones to stakeholders',
        date: addDays(new Date(), 1),
        time: '10:00',
        endTime: '11:30',
        hour: 10,
        project: 'Website Redesign',
        type: 'Presentation',
        priority: 'high',
        location: 'Main Conference Room',
        attendees: ['David Kim', 'Priya Patel', 'Client Team'],
        color: '#ffb300'
      },
      {
        id: 4,
        title: 'Code Review',
        description: 'Review backend API implementation and discuss improvements',
        date: addDays(new Date(), 2),
        time: '16:00',
        endTime: '17:00',
        hour: 16,
        project: 'Website Redesign',
        type: 'Review',
        priority: 'medium',
        location: 'Development Room',
        attendees: ['Michael Chen', 'David Kim'],
        color: '#00e0ff'
      },
      {
        id: 5,
        title: 'Sprint Planning',
        description: 'Plan tasks and user stories for the upcoming development sprint',
        date: addDays(new Date(), 3),
        time: '13:00',
        endTime: '15:00',
        hour: 13,
        project: 'Website Redesign',
        type: 'Planning',
        priority: 'high',
        location: 'Team Room',
        attendees: ['All Team Members'],
        color: '#ff0066'
      }
    ]);

    // Computed Properties
    const currentPeriodLabel = computed(() => {
      if (currentView.value === 'Week') {
        const start = startOfWeek(currentDate.value);
        const end = endOfWeek(currentDate.value);
        return `${format(start, 'MMM d')} - ${format(end, 'MMM d, yyyy')}`;
      } else {
        return format(currentDate.value, 'MMMM yyyy');
      }
    });

    const periodSubtitle = computed(() => {
      if (currentView.value === 'Week') {
        return 'Weekly Schedule';
      } else {
        return 'Monthly Overview';
      }
    });

    const weekDays = computed(() => {
      const start = startOfWeek(currentDate.value);
      const days = [];
      for (let i = 0; i < 7; i++) {
        const day = addDays(start, i);
        days.push({
          date: day,
          name: format(day, 'EEE'),
          number: format(day, 'd'),
          month: format(day, 'MMM'),
          dateKey: format(day, 'yyyy-MM-dd')
        });
      }
      return days;
    });

    const monthDates = computed(() => {
      const start = startOfMonth(currentDate.value);
      const end = endOfMonth(currentDate.value);
      const firstWeekStart = startOfWeek(start);
      const lastWeekEnd = endOfWeek(end);
      
      const dates = [];
      let current = firstWeekStart;
      
      while (current <= lastWeekEnd) {
        dates.push({
          date: current,
          day: format(current, 'd'),
          dateKey: format(current, 'yyyy-MM-dd'),
          currentMonth: current.getMonth() === currentDate.value.getMonth()
        });
        current = addDays(current, 1);
      }
      
      return dates;
    });

    const timeSlots = computed(() => {
      const slots = [];
      for (let hour = 6; hour <= 22; hour++) {
        slots.push(hour);
      }
      return slots;
    });

    const dayNames = ref(['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']);

    const showCurrentTimeIndicator = computed(() => {
      const today = new Date();
      return weekDays.value.some(day => isSameDay(day.date, today));
    });

    // Helper Functions
    const isToday = (date) => {
      return checkIsToday(date);
    };

    const isWeekend = (date) => {
      return checkIsWeekend(date);
    };

    const isCurrentHour = (hour) => {
      const now = new Date();
      return isToday(now) && getHours(now) === hour;
    };

    const formatHour = (hour) => {
      return format(new Date().setHours(hour, 0, 0, 0), 'h');
    };

    const formatPeriod = (hour) => {
      return format(new Date().setHours(hour, 0, 0, 0), 'a');
    };

    const formatDateKey = (date) => {
      return format(date, 'yyyy-MM-dd');
    };

    const formatEventDate = (date) => {
      return format(date, 'EEEE, MMMM d, yyyy');
    };

    const getEventsForSlot = (date, hour) => {
      if (!selectedProject.value) return [];
      return events.value.filter(event => 
        event.project === selectedProject.value &&
        isSameDay(event.date, date) && 
        event.hour === hour
      );
    };

    const getEventsForDate = (date) => {
      if (!selectedProject.value) return [];
      return events.value.filter(event => 
        event.project === selectedProject.value &&
        isSameDay(event.date, date)
      );
    };

    const getEventTypeClass = (event) => {
      return `event-${event.type.toLowerCase()}`;
    };

    const getEventStyle = (event) => {
      return {
        background: `linear-gradient(135deg, ${event.color}, ${event.color}CC)`
      };
    };

    const getEventColor = (event) => {
      return event.color;
    };

    const getCurrentTimeStyle = () => {
      const now = new Date();
      const currentHour = getHours(now);
      const currentMinutes = getMinutes(now);
      
      // Find the current hour in timeSlots
      const hourIndex = timeSlots.value.indexOf(currentHour);
      if (hourIndex === -1) return { display: 'none' };
      
      // Calculate position
      const slotHeight = 80; // Height of each hour slot
      const headerHeight = 100; // Height of the header
      const minuteOffset = (currentMinutes / 60) * slotHeight;
      const topPosition = headerHeight + (hourIndex * slotHeight) + minuteOffset;
      
      return {
        top: `${topPosition}px`,
        left: '80px', // Width of time column
        right: '0',
        position: 'absolute',
        height: '2px',
        background: '#ff0066',
        zIndex: 100,
        boxShadow: '0 0 10px rgba(255, 0, 102, 0.5)'
      };
    };

    // Navigation Functions
    const previousPeriod = () => {
      if (currentView.value === 'Week') {
        currentDate.value = addWeeks(currentDate.value, -1);
      } else {
        currentDate.value = addMonths(currentDate.value, -1);
      }
    };

    const nextPeriod = () => {
      if (currentView.value === 'Week') {
        currentDate.value = addWeeks(currentDate.value, 1);
      } else {
        currentDate.value = addMonths(currentDate.value, 1);
      }
    };

    const goToToday = () => {
      currentDate.value = new Date();
    };

    // Event Functions
    const selectDate = (date) => {
      selectedDate.value = selectedDate.value && isSameDay(selectedDate.value, date) ? null : date;
    };

    const selectEvent = (event) => {
      selectedEvent.value = event;
    };

    const createEvent = (date, hour) => {
      console.log('Creating event for:', format(date, 'yyyy-MM-dd'), hour);
      // Implementation for creating new event
    };

    const editEvent = () => {
      console.log('Editing event:', selectedEvent.value);
      selectedEvent.value = null;
    };

    const deleteEvent = () => {
      if (confirm('Are you sure you want to delete this event?')) {
        const eventIndex = events.value.findIndex(e => e.id === selectedEvent.value.id);
        if (eventIndex > -1) {
          events.value.splice(eventIndex, 1);
        }
        selectedEvent.value = null;
      }
    };

    const showMoreEvents = (date) => {
      console.log('Showing more events for:', format(date, 'yyyy-MM-dd'));
      // Implementation for showing more events modal
    };

    const showEventTooltip = (event, mouseEvent) => {
      tooltipEvent.value = event;
      const rect = mouseEvent.target.getBoundingClientRect();
      tooltipStyle.value = {
        position: 'fixed',
        top: `${rect.top - 10}px`,
        left: `${rect.left + rect.width / 2}px`,
        transform: 'translateX(-50%) translateY(-100%)',
        zIndex: 1000
      };
    };

    const hideEventTooltip = () => {
      tooltipEvent.value = null;
    };

    const loadTimetableData = async () => {
      if (!selectedProject.value) return;
      
      loading.value = true;
      error.value = null;
      
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Filter events by selected project
        const projectEvents = events.value.filter(event => 
          event.project === selectedProject.value
        );
        
        if (projectEvents.length === 0) {
          error.value = 'No events found for the selected project.';
        }
        
      } catch (err) {
        error.value = 'Failed to load timetable data. Please try again.';
      } finally {
        loading.value = false;
      }
    };

    // Time tracking
    const updateCurrentTime = () => {
      currentTime.value = new Date();
    };

    onMounted(() => {
      const savedTheme = localStorage.getItem("zainpm-theme");
      if (savedTheme === "light") {
        isDark.value = false;
      }
      
      // Auto-select first project
      if (projects.value.length > 0) {
        selectedProject.value = projects.value[0].name;
        loadTimetableData();
      }
      
      // Update time every minute
      timeInterval = setInterval(updateCurrentTime, 60000);
      updateCurrentTime();
    });

    onUnmounted(() => {
      if (timeInterval) {
        clearInterval(timeInterval);
      }
    });

    return {
      isDark,
      toggleTheme,
      activeNav,
      setActiveNav,
      currentView,
      viewTypes,
      currentDate,
      selectedDate,
      selectedEvent,
      selectedProject,
      loading,
      error,
      projects,
      events,
      currentPeriodLabel,
      periodSubtitle,
      weekDays,
      monthDates,
      timeSlots,
      dayNames,
      showCurrentTimeIndicator,
      tooltipEvent,
      tooltipStyle,
      isToday,
      isWeekend,
      isCurrentHour,
      formatHour,
      formatPeriod,
      formatDateKey,
      formatEventDate,
      getEventsForSlot,
      getEventsForDate,
      getEventTypeClass,
      getEventStyle,
      getEventColor,
      getCurrentTimeStyle,
      previousPeriod,
      nextPeriod,
      goToToday,
      selectDate,
      selectEvent,
      createEvent,
      editEvent,
      deleteEvent,
      showMoreEvents,
      showEventTooltip,
      hideEventTooltip,
      loadTimetableData
    };
  }
};
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