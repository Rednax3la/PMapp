<template>
  <div class="timetable-page" :class="{ dark: isDark, light: !isDark }">
    <!-- Sidebar -->
    <Sidebar :active-nav="activeNav" @nav-change="setActiveNav" />
    
    <!-- Main Content -->
    <div class="main-content">
      <AppHeader title="Timetable">
        <template #actions>
          <ThemeToggle :is-dark="isDark" @toggle="toggleTheme" />
          <AppButton variant="primary" icon="fas fa-calendar-plus">
            Add Event
          </AppButton>
        </template>
      </AppHeader>
      
      <!-- Calendar Controls -->
      <div class="calendar-controls">
        <div class="view-switcher">
          <button 
            v-for="view in viewTypes" 
            :key="view" 
            :class="['view-btn', { active: currentView === view }]"
            @click="currentView = view"
          >
            {{ view }}
          </button>
        </div>
        
        <div class="navigation">
          <button class="nav-btn" @click="previousPeriod">
            <i class="fas fa-chevron-left"></i>
          </button>
          <h3 class="current-period">{{ currentPeriodLabel }}</h3>
          <button class="nav-btn" @click="nextPeriod">
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
        
        <button class="today-btn" @click="goToToday">
          Today
        </button>
      </div>
      
      <!-- Calendar Grid -->
      <div class="calendar-container">
        <!-- Week View -->
        <div v-if="currentView === 'Week'" class="week-view">
          <div class="week-header">
            <div class="time-column">Time</div>
            <div 
              v-for="day in weekDays" 
              :key="day.date" 
              class="day-header"
              :class="{ today: isToday(day.date) }"
            >
              <div class="day-name">{{ day.name }}</div>
              <div class="day-number">{{ day.number }}</div>
            </div>
          </div>
          
          <div class="week-grid">
            <div class="time-slots">
              <div 
                v-for="hour in timeSlots" 
                :key="hour" 
                class="time-slot"
              >
                {{ formatHour(hour) }}
              </div>
            </div>
            
            <div class="days-grid">
              <div 
                v-for="day in weekDays" 
                :key="day.date" 
                class="day-column"
              >
                <div 
                  v-for="hour in timeSlots" 
                  :key="hour" 
                  class="hour-slot"
                  @click="createEvent(day.date, hour)"
                >
                  <div 
                    v-for="event in getEventsForSlot(day.date, hour)" 
                    :key="event.id" 
                    class="event-block"
                    :style="{ background: event.color }"
                    @click.stop="selectEvent(event)"
                  >
                    <div class="event-title">{{ event.title }}</div>
                    <div class="event-time">{{ event.time }}</div>
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
                'selected': selectedDate && date.dateKey === formatDateKey(selectedDate)
              }"
              @click="selectDate(date.date)"
            >
              <div class="cell-date">{{ date.day }}</div>
              <div class="cell-events">
                <div 
                  v-for="event in getEventsForDate(date.date)" 
                  :key="event.id" 
                  class="month-event"
                  :style="{ background: event.color }"
                  @click.stop="selectEvent(event)"
                >
                  {{ event.title }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Event Details Modal -->
      <div v-if="selectedEvent" class="modal-overlay" @click.self="selectedEvent = null">
        <div class="event-modal">
          <div class="modal-header">
            <h3>{{ selectedEvent.title }}</h3>
            <button class="close-btn" @click="selectedEvent = null">&times;</button>
          </div>
          <div class="modal-body">
            <div class="event-details">
              <div class="detail-item">
                <i class="fas fa-clock"></i>
                <span>{{ selectedEvent.time }} - {{ selectedEvent.endTime }}</span>
              </div>
              <div class="detail-item">
                <i class="fas fa-calendar"></i>
                <span>{{ formatEventDate(selectedEvent.date) }}</span>
              </div>
              <div class="detail-item">
                <i class="fas fa-project-diagram"></i>
                <span>{{ selectedEvent.project }}</span>
              </div>
              <div class="detail-item">
                <i class="fas fa-users"></i>
                <span>{{ selectedEvent.attendees.join(', ') }}</span>
              </div>
            </div>
            <div class="event-description">
              {{ selectedEvent.description }}
            </div>
          </div>
          <div class="modal-footer">
            <AppButton variant="primary" @click="editEvent">Edit</AppButton>
            <AppButton variant="danger" @click="deleteEvent">Delete</AppButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
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
  isToday as isDateToday
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

    // Calendar State
    const currentView = ref('Week');
    const viewTypes = ref(['Week', 'Month']);
    const currentDate = ref(new Date());
    const selectedDate = ref(null);
    const selectedEvent = ref(null);

    // Events Data
    const events = ref([
      {
        id: 1,
        title: 'Team Standup',
        description: 'Daily team synchronization meeting',
        date: new Date(2023, 5, 12),
        time: '09:00',
        endTime: '09:30',
        hour: 9,
        project: 'General',
        attendees: ['Sarah Johnson', 'Michael Chen', 'David Kim'],
        color: 'var(--primary)'
      },
      {
        id: 2,
        title: 'Design Review',
        description: 'Review mockups for homepage redesign',
        date: new Date(2023, 5, 12),
        time: '14:00',
        endTime: '15:30',
        hour: 14,
        project: 'Website Redesign',
        attendees: ['Sarah Johnson', 'Emma Rodriguez'],
        color: 'var(--success)'
      },
      {
        id: 3,
        title: 'Client Meeting',
        description: 'Project status update with stakeholders',
        date: new Date(2023, 5, 13),
        time: '10:00',
        endTime: '11:00',
        hour: 10,
        project: 'Mobile App',
        attendees: ['David Kim', 'Priya Patel'],
        color: 'var(--warning)'
      },
      {
        id: 4,
        title: 'Code Review',
        description: 'Review API integration implementation',
        date: new Date(2023, 5, 14),
        time: '16:00',
        endTime: '17:00',
        hour: 16,
        project: 'Backend',
        attendees: ['Michael Chen', 'David Kim'],
        color: 'var(--info)'
      },
      {
        id: 5,
        title: 'Sprint Planning',
        description: 'Plan tasks for upcoming sprint',
        date: new Date(2023, 5, 15),
        time: '13:00',
        endTime: '15:00',
        hour: 13,
        project: 'General',
        attendees: ['All Team'],
        color: 'var(--accent)'
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

    const weekDays = computed(() => {
      const start = startOfWeek(currentDate.value);
      const days = [];
      for (let i = 0; i < 7; i++) {
        const day = addDays(start, i);
        days.push({
          date: day,
          name: format(day, 'EEE'),
          number: format(day, 'd')
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
      for (let hour = 8; hour <= 18; hour++) {
        slots.push(hour);
      }
      return slots;
    });

    const dayNames = ref(['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']);

    // Helper Functions
    const isToday = (date) => {
      return isDateToday(date);
    };

    const formatHour = (hour) => {
      return `${hour}:00`;
    };

    const formatDateKey = (date) => {
      return format(date, 'yyyy-MM-dd');
    };

    const formatEventDate = (date) => {
      return format(date, 'EEEE, MMMM d, yyyy');
    };

    const getEventsForSlot = (date, hour) => {
      return events.value.filter(event => 
        isSameDay(event.date, date) && event.hour === hour
      );
    };

    const getEventsForDate = (date) => {
      return events.value.filter(event => 
        isSameDay(event.date, date)
      );
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
      selectedDate.value = date;
    };

    const selectEvent = (event) => {
      selectedEvent.value = event;
    };

    const createEvent = (date, hour) => {
      console.log('Creating event for:', date, hour);
      // Implementation for creating new event
    };

    const editEvent = () => {
      console.log('Editing event:', selectedEvent.value);
      selectedEvent.value = null;
    };

    const deleteEvent = () => {
      console.log('Deleting event:', selectedEvent.value);
      selectedEvent.value = null;
    };

    onMounted(() => {
      const savedTheme = localStorage.getItem("zainpm-theme");
      if (savedTheme === "light") {
        isDark.value = false;
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
      events,
      currentPeriodLabel,
      weekDays,
      monthDates,
      timeSlots,
      dayNames,
      isToday,
      formatHour,
      formatDateKey,
      formatEventDate,
      getEventsForSlot,
      getEventsForDate,
      previousPeriod,
      nextPeriod,
      goToToday,
      selectDate,
      selectEvent,
      createEvent,
      editEvent,
      deleteEvent
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

.calendar-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding: 15px 20px;
  background: var(--bg-section);
  border-radius: 10px;
  border: 1px solid var(--border-color);
}

.view-switcher {
  display: flex;
  gap: 5px;
}

.view-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-btn:hover,
.view-btn.active {
  background: var(--primary);
  color: var(--dark-base);
  border-color: var(--primary);
}

.navigation {
  display: flex;
  align-items: center;
  gap: 15px;
}

.nav-btn {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-btn:hover {
  background: var(--accent);
  color: var(--dark-base);
}

.current-period {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  min-width: 200px;
  text-align: center;
}

.today-btn {
  background: var(--success);
  color: var(--dark-base);
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.today-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.calendar-container {
  background: var(--bg-section);
  border-radius: 10px;
  border: 1px solid var(--border-color);
  overflow: hidden;
}

/* Week View Styles */
.week-header {
  display: flex;
  background: rgba(0, 0, 0, 0.1);
  border-bottom: 2px solid var(--border-color);
}

.time-column {
  width: 80px;
  padding: 15px 10px;
  font-weight: 600;
  border-right: 1px solid var(--border-color);
  text-align: center;
}

.day-header {
  flex: 1;
  padding: 15px 10px;
  text-align: center;
  border-right: 1px solid var(--border-color);
}

.day-header.today {
  background: var(--primary);
  color: var(--dark-base);
}

.day-name {
  font-weight: 600;
  margin-bottom: 5px;
}

.day-number {
  font-size: 18px;
  font-weight: 700;
}

.week-grid {
  display: flex;
  max-height: 600px;
  overflow-y: auto;
}

.time-slots {
  width: 80px;
  border-right: 1px solid var(--border-color);
}

.time-slot {
  height: 60px;
  padding: 5px;
  border-bottom: 1px solid var(--border-color);
  font-size: 12px;
  text-align: center;
  display: flex;
  align-items: flex-start;
  justify-content: center;
}

.days-grid {
  flex: 1;
  display: flex;
}

.day-column {
  flex: 1;
  border-right: 1px solid var(--border-color);
}

.hour-slot {
  height: 60px;
  border-bottom: 1px solid var(--border-color);
  position: relative;
  cursor: pointer;
  transition: background 0.2s ease;
}

.hour-slot:hover {
  background: rgba(0, 0, 0, 0.05);
}

.event-block {
  position: absolute;
  left: 2px;
  right: 2px;
  top: 2px;
  bottom: 2px;
  border-radius: 4px;
  padding: 4px 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 1;
}

.event-block:hover {
  transform: scale(1.02);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.event-title {
  font-size: 11px;
  font-weight: 600;
  color: white;
  margin-bottom: 2px;
}

.event-time {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.8);
}

/* Month View Styles */
.month-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: rgba(0, 0, 0, 0.1);
  border-bottom: 2px solid var(--border-color);
}

.month-day-header {
  padding: 15px 10px;
  text-align: center;
  font-weight: 600;
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
  transition: background 0.2s ease;
  position: relative;
}

.month-cell:hover {
  background: rgba(0, 0, 0, 0.05);
}

.month-cell.other-month {
  color: var(--text-secondary);
  background: rgba(0, 0, 0, 0.02);
}

.month-cell.today {
  background: rgba(0, 255, 247, 0.1);
}

.month-cell.selected {
  background: rgba(0, 255, 247, 0.2);
}

.cell-date {
  font-weight: 600;
  margin-bottom: 5px;
}

.cell-events {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.month-event {
  font-size: 10px;
  padding: 2px 4px;
  border-radius: 3px;
  color: white;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Modal Styles */
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
  border-radius: 10px;
  width: 90%;
  max-width: 500px;
  box-shadow: var(--shadow);
  overflow: hidden;
}

.modal-header {
  padding: 20px;
  background: rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  transition: color 0.2s ease;
}

.close-btn:hover {
  color: var(--danger);
}

.modal-body {
  padding: 20px;
}

.event-details {
  margin-bottom: 20px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  color: var(--text-secondary);
}

.detail-item i {
  width: 16px;
  color: var(--accent);
}

.event-description {
  color: var(--text-secondary);
  line-height: 1.6;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  background: rgba(0, 0, 0, 0.05);
}

@media (max-width: 992px) {
  .calendar-controls {
    flex-direction: column;
    gap: 15px;
  }
  
  .navigation {
    order: -1;
  }
}

@media (max-width: 768px) {
  .week-grid {
    min-width: 600px;
  }
  
  .calendar-container {
    overflow-x: auto;
  }
  
  .month-grid {
    grid-auto-rows: 80px;
  }
}
</style>