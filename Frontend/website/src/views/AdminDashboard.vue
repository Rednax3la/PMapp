//Frontend/website/src/views/AdminDashboard.vue
<template>
  <div class="admin-dashboard" :class="{ dark: isDark, light: !isDark }">
    <Sidebar />

    <div class="main-content">
      <AppHeader :title="dashboardTitle">
        <template #actions>
          <ThemeToggle :is-dark="isDark" @toggle="toggleTheme" />
        </template>
      </AppHeader>

      <!-- Stats Overview -->
      <div class="stats-grid">
        <template v-if="loading">
          <div v-for="n in 4" :key="n" class="stat-card glass-card skeleton" style="height:90px"></div>
        </template>
        <template v-else>
          <div
            class="stat-card glass-card fade-in"
            v-for="stat in displayStats"
            :key="stat.label"
          >
            <div class="stat-label">{{ stat.label }}</div>
            <div class="stat-value" :style="{ color: stat.color }">
              {{ stat.value ?? '0' }}
            </div>
          </div>
        </template>
      </div>

      <!-- State Legend (keeps page-wide legend consistent) -->
      <div class="state-legend">
        <div class="legend-item" v-for="item in legendItems" :key="item.label">
          <div class="legend-color" :style="{ background: item.color }"></div>
          <span>{{ item.label }}</span>
        </div>
      </div>

      <div class="grid">
        <!-- Active Projects -->
        <div class="card glass-card">
          <div class="card-header">
            <span>Active Projects</span>
            <router-link to="/projects" class="btn btn-primary btn-sm">View All</router-link>
          </div>
          <div class="card-body">
            <div
              class="task-item"
              v-for="project in projects"
              :key="project.id || project.project_name || project.name"
            >
              <div class="task-info">
                <div class="task-title">
                  <span class="state-dot" :style="{ background: statusToColor(project.state || project.status) }"></span>
                  {{ project.project_name || project.name || project.title }}
                </div>
                <div class="task-meta">
                  <span class="task-date">
                    <i class="far fa-calendar"></i>
                    <span v-if="project.start_date || project.startDate">{{ formatDate(project.start_date || project.startDate) }}</span>
                    <span v-if="project.end_date || project.endDate"> - {{ formatDate(project.end_date || project.endDate) }}</span>
                  </span>
                  <span><i class="fas fa-tasks"></i> {{ (Array.isArray(project.tasks) && project.tasks.length) || (!Array.isArray(project.tasks) && project.tasks) || '—' }}</span>
                </div>
              </div>
              <StateBadge :status="project.state || project.status" />
            </div>
          </div>
        </div>

        <!-- Recent Tasks -->
        <div class="card glass-card">
          <div class="card-header">
            <span>Recent Tasks</span>
            <router-link to="/tasks" class="btn btn-primary btn-sm">View All</router-link>
          </div>
          <div class="card-body">
            <div
              class="task-item"
              v-for="task in tasks"
              :key="task.id || task.task_name || task.title"
            >
              <div class="task-info">
                <div class="task-title">
                  <span class="state-dot" :style="{ background: statusToColor(task.state || task.status) }"></span>
                  {{ task.title || task.task_name }}
                </div>
                <div class="task-meta">
                  <span class="task-date">
                    <i class="far fa-calendar"></i>
                    <span v-if="task.start_time">{{ formatDate(task.start_time) }}</span>
                    <span v-else>—</span>
                  </span>
                  <span :class="priorityClass(task.priority)">{{ priorityLabel(task.priority) || '—' }}</span>
                </div>
              </div>
              <StateBadge :status="task.state || task.status" />
            </div>
          </div>
        </div>

        <!-- Task Status Distribution (canvas stretches, labels below) -->
        <div class="card">
          <div class="card-header">
            <span>Task Status Distribution</span>
          </div>
          <div class="card-body chart-full-width">
            <div class="chart-container-full">
              <canvas ref="chartCanvas"></canvas>
            </div>

            <!-- labels / key below the chart (colors come from legendItems so everything matches) -->
            <div class="chart-legend-grid">
              <div class="legend-cell" v-for="item in chartLegendBelow" :key="item.label">
                <div class="legend-color" :style="{ background: item.color }"></div>
                <div class="legend-line">
                  <div class="legend-label">{{ item.label }}</div>
                  <div class="legend-count">{{ item.count }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Team Members -->
        <div class="card">
          <div class="card-header">
            <span>Team Members</span>
          </div>
          <div class="card-body">
            <div class="member-list">
              <div class="member-tag" v-for="member in uniqueTeamMembers" :key="member">
                <i class="fas fa-user"></i> {{ member }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Upcoming Deadlines -->
      <div class="card" style="margin-top: 16px;">
        <div class="card-header">
          <span>Upcoming Deadlines</span>
        </div>
        <div class="card-body">
          <div class="grid">
            <div
              class="task-item"
              v-for="deadline in deadlines"
              :key="deadline.title + (deadline.dueDate || '')"
            >
              <div class="task-info">
                <div class="task-title">{{ deadline.title }}</div>
                <div class="task-meta">
                  <span><i class="far fa-calendar"></i> Due: {{ deadline.dueDate }}</span>
                  <span>Project: {{ deadline.project }}</span>
                </div>
              </div>
              <StateBadge :status="deadline.status" />
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch, computed } from 'vue';
import Chart from 'chart.js/auto';
import Sidebar from '@/components/layout/Sidebar.vue';
import AppHeader from '@/components/layout/AppHeader.vue';
import ThemeToggle from '@/components/layout/ThemeToggle.vue';
import StateBadge from '@/components/ui/StateBadge.vue';

import { projectService } from '@/services/projects';
import { authService } from '@/services/auth';

export default {
  name: 'AdminDashboard',
  components: {
    Sidebar,
    AppHeader,
    ThemeToggle,
    StateBadge
  },
  setup() {
    const isDark = ref(true);
    const toggleTheme = () => {
      isDark.value = !isDark.value;
      localStorage.setItem("zainpm-theme", isDark.value ? "dark" : "light");
    };

    // stats container
    const companyName = ref('');
    const stats = reactive({
      activeProjects: 0,
      totalTasks: 0,
      teamMembers: 0,
      completionRate: '0%'
    });

    // shared status labels (order matters)
    const statusLabels = ['Tentative','Delayed','In Progress','Overdue','Complete'];

    // legendItems -> drives both chart color palette and small page legend
    const legendItems = computed(() => {
      const a = isDark.value ? 0.72 : 0.72;
      return [
        { label: 'Tentative', color: `rgba(108, 117, 125, ${a})` },
        { label: 'Delayed',   color: `rgba(230, 57, 70, ${a})` },
        { label: 'In Progress', color:`rgba(73, 80, 246, ${a})` },
        { label: 'Overdue',   color: `rgba(247, 37, 133, ${a})` },
        { label: 'Complete',  color: `rgba(76, 201, 240, ${a})` }
      ];
    });

    // statusColors are derived from legendItems to keep EXACT color sync
    const statusColors = computed(() => legendItems.value.map(i => i.color));
    const statusBorderColors = computed(() => [
      'rgba(108,117,125,1)',
      'rgba(230,57,70,1)',
      'rgba(73,80,246,1)',
      'rgba(247,37,133,1)',
      'rgba(76,201,240,1)'
    ]);

    // internal lists
    const loading = ref(false);
    const projects = ref([]);
    const tasks = ref([]);
    const teamMembers = ref([]);
    const deadlines = ref([]);

    // chart helpers
    const chartCanvas = ref(null);
    let chartInstance = null;
    const statusCountsRef = ref([0,0,0,0,0]);

    // chart legend used below canvas
    const chartLegendBelow = computed(() => {
      return statusLabels.map((label, idx) => ({
        label,
        count: statusCountsRef.value[idx] ?? 0,
        color: statusColors.value[idx]
      }));
    });

    // page-wide legend uses legendItems (keeps existing UI)
    // (legendItems computed above)

    // dashboard title
    const dashboardTitle = computed(() => companyName.value ? `Dashboard - ${companyName.value}` : 'Dashboard');

    // helpers
    const calculateCompletionRate = (allTasks) => {
      if (!Array.isArray(allTasks) || allTasks.length === 0) return 0;
      const completed = allTasks.filter(t => {
        const st = (t.state || t.status || '').toString().toLowerCase();
        return st === 'complete' || st === 'completed' || (t.raw && Number(t.raw?.progress) >= 100);
      }).length;
      return Math.round((completed / allTasks.length) * 100);
    };

    const priorityClass = (p) => {
      if (!p) return 'priority-medium';
      const s = p.toString().toLowerCase();
      if (s.includes('high') || s.includes('urgent')) return 'priority-high';
      if (s.includes('low')) return 'priority-low';
      return 'priority-medium';
    };

    const priorityLabel = (p) => {
      if (!p) return '';
      const s = p.toString().toLowerCase();
      if (s.includes('high') || s.includes('urgent')) return 'High Priority';
      if (s.includes('low')) return 'Low Priority';
      return 'Medium Priority';
    };

    const formatDate = (value) => {
      if (!value) return '';
      const d = (value instanceof Date) ? value : new Date(value);
      if (isNaN(d.getTime())) return String(value);
      return d.toLocaleDateString();
    };

    // convert status string to color (synchronized with legendItems/statusColors)
    const statusToColor = (rawStatus) => {
      if (!rawStatus) return 'transparent';
      const s = rawStatus.toString().toLowerCase();
      for (let i = 0; i < statusLabels.length; i++) {
        const lab = statusLabels[i].toString().toLowerCase();
        if (s.includes(lab.split(' ')[0])) return statusColors.value[i];
      }
      // fallback if no exact match; try matching words like 'overdue', 'delay', 'complete', etc.
      if (s.includes('overdue')) return statusColors.value[3];
      if (s.includes('delay')) return statusColors.value[1];
      if (s.includes('complete')) return statusColors.value[4];
      if (s.includes('progress') || s.includes('in progress')) return statusColors.value[2];
      return 'transparent';
    };

    // Stats array shape expected by template
    const statsList = computed(() => [
      { label: 'Active Projects', value: stats.activeProjects ?? 0, color: 'var(--primary)' },
      { label: 'Live Tasks',    value: stats.totalTasks ?? 0,    color: 'var(--primary)' },
      { label: 'Team Members',   value: stats.teamMembers ?? 0,   color: 'var(--success)' },
      { label: 'Completion Rate',value: stats.completionRate ?? '0%', color: 'var(--warning)' }
    ]);
    const displayStats = computed(() => statsList.value);
    const uniqueTeamMembers = computed(() => Array.isArray(teamMembers.value) ? teamMembers.value : []);

    // Build doughnut and init chart (cutout reduced to 40% making inner hole smaller)
    const initChart = (statusCounts = [0,0,0,0,0]) => {
      if (!chartCanvas.value) return;
      if (chartInstance) chartInstance.destroy();

      const ctx = chartCanvas.value.getContext('2d');

      chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: statusLabels,
          datasets: [{
            data: statusCounts,
            backgroundColor: statusColors.value,
            borderColor: statusBorderColors.value,
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '50%',
          layout: { padding: { top: 4, right: 4, bottom: 4, left: 4 } },
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label(ctx) {
                  const label = ctx.label || '';
                  const val = ctx.parsed ?? ctx.raw ?? 0;
                  return `${label}: ${val}`;
                }
              }
            }
          }
        }
      });
    };

    // Fetch & populate data
    const fetchDashboardData = async () => {
      loading.value = true;
      try {
        let user = authService.getCurrentUser() || {};
        if (!user?.company_name) {
          const stored = localStorage.getItem('user');
          if (stored) {
            try {
              const parsed = JSON.parse(stored);
              if (parsed.company_name) user.company_name = parsed.company_name;
            } catch (error) {
              console.error('Error parsing stored user data:', error);
            }
          }
        }
        if (!user?.company_name) throw new Error('Missing company info (please login again)');

        companyName.value = user.company_name;

        // projects
        const projResp = await projectService.getProjects(user.company_name);
        const projList = (projResp && projResp.projects) ? projResp.projects : (Array.isArray(projResp) ? projResp : []);
        projects.value = (projList || []).map(p => {
          const start =
            p.start_date || p.startDate || p.start_time || p.startTime || p.expected_start || p.expected_start_date || p.begin || null;
          const end =
            p.end_date || p.endDate || p.end_time || p.endTime || p.due_date || p.expected_completion || p.expected_end || null;
          const tasksField = Array.isArray(p.tasks) ? p.tasks : (typeof p.tasks === 'number' ? [] : (p.tasks || []));
          return {
            ...p,
            project_name: p.project_name || p.name || p.title || p.project_name,
            title: p.title || p.name || p.project_name,
            state: p.state || p.status || p.state || '',
            status: p.state || p.status || '',
            tasks: tasksField,
            team: p.team || p.members || p.teams || [],
            start_date: start,
            startDate: start,
            end_date: end,
            endDate: end
          };
        });

        // flatten tasks
        const flattened = [];
        projects.value.forEach(proj => {
          (proj.tasks || []).forEach(t => {
            flattened.push({
              id: t.id || t._id || t.task_id || null,
              title: t.name || t.task_name || t.title || 'Untitled Task',
              start_time: t.start_time || t.startTime || t.startDate || t.start_date || null,
              due_date: t.due_date || t.deadline || t.dueDate || null,
              dates: t.start_time ? `${formatDate(t.start_time)} — ${t.expected_duration || ''}` : '',
              priority: t.priority || t.priority_level || (t.priority_label ? t.priority_label : 'medium'),
              priorityClass: priorityClass(t.priority || t.priority_level),
              state: t.state || t.status || '',
              status: t.state || t.status || '',
              project: proj.title || proj.project_name || proj.name,
              raw: t
            });
          });
        });

        flattened.sort((a,b) => {
          const da = new Date(a.start_time || a.raw?.timestamp || 0).getTime();
          const db = new Date(b.start_time || b.raw?.timestamp || 0).getTime();
          return db - da;
        });

        tasks.value = flattened;

        // team members deduped
        const members = projects.value.flatMap(p => p.team || []);
        const normalizedMembers = members.map(m => {
          if (!m) return null;
          if (typeof m === 'string') return m;
          return m.username || m.email || m.name || (m.fullName || m.full_name) || JSON.stringify(m);
        }).filter(Boolean);
        const unique = Array.from(new Set(normalizedMembers));
        teamMembers.value = unique;

        // upcoming deadlines
        deadlines.value = tasks.value
          .filter(t => t.due_date || t.raw?.due_date || t.raw?.deadline || t.start_time)
          .slice(0, 10)
          .map(t => {
            const rawDue = t.due_date || t.raw?.due_date || t.raw?.deadline || null;
            const due = rawDue ? new Date(rawDue) : (t.start_time ? new Date(t.start_time) : null);
            return {
              title: t.title,
              dueDate: due ? formatDate(due) : 'N/A',
              project: t.project,
              status: t.status
            };
          });

        // stats
        const activeProjectsCount = projects.value.filter(p => {
          const st = (p.state || p.status || '').toString().toLowerCase();
          return st !== 'complete' && st !== 'completed';
        }).length;

        const nonCompleteTasks = flattened.filter(t => {
          const st = (t.state || t.status || '').toString().toLowerCase();
          return st !== 'complete' && st !== 'completed';
        });

        stats.activeProjects = activeProjectsCount;
        stats.totalTasks = nonCompleteTasks.length;
        stats.teamMembers = teamMembers.value.length;
        const completionRate = calculateCompletionRate(flattened);
        stats.completionRate = `${completionRate}%`;

        // chart counts & render
        const counts = { 'tentative':0, 'delayed':0, 'in progress':0, 'overdue':0, 'complete':0 };
        flattened.forEach(t => {
          const s = (t.state || t.status || '').toString().toLowerCase();
          if (s.includes('tentat')) counts['tentative']++;
          else if (s.includes('delay')) counts['delayed']++;
          else if (s.includes('overdue')) counts['overdue']++;
          else if (s.includes('complete') || (t.raw && Number(t.raw?.progress) >= 100)) counts['complete']++;
          else counts['in progress']++;
        });

        const countsArr = [
          counts['tentative'],
          counts['delayed'],
          counts['in progress'],
          counts['overdue'],
          counts['complete']
        ];
        statusCountsRef.value = countsArr;
        initChart(countsArr);

      } catch (err) {
        console.error('Dashboard load error:', err);
      } finally {
        loading.value = false;
      }
    };

    // rerender chart on theme change (reads statusCountsRef for data)
    watch(isDark, () => {
      if (chartInstance && chartInstance.data) {
        const data = chartInstance.data.datasets?.[0]?.data || statusCountsRef.value || [0,0,0,0,0];
        initChart(data);
      }
    });

    onMounted(() => {
      const savedTheme = localStorage.getItem("zainpm-theme");
      if (savedTheme === "light") isDark.value = false;
      fetchDashboardData();
    });

    return {
      isDark,
      loading,
      toggleTheme,
      dashboardTitle,
      stats: statsList,
      displayStats,
      legendItems,
      projects,
      tasks,
      teamMembers,
      uniqueTeamMembers,
      deadlines,
      chartCanvas,
      formatDate,
      priorityClass,
      priorityLabel,
      chartLegendBelow,
      statusCountsRef,
      statusColors,
      statusToColor
    };
  }
};
</script>

<style scoped>
.admin-dashboard {
  display: flex;
  height: 100vh;
  background-color: var(--bg-base);
  color: var(--text-primary);
  line-height: 1.6;
  top: 0;
}

.main-content {
  flex: 1;
  margin-left: 260px;
  padding: 20px;
  overflow-y: auto;
  height: 100%;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
}

.stat-card {
  background: var(--bg-section);
  border-radius: 10px;
  box-shadow: var(--shadow);
  padding: 20px;
  text-align: center;
  border: 1px solid var(--border-color);
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  margin: 10px 0;
  color: var(--primary);
}

.stat-label {
  color: var(--text-primary);
  font-size: 20px;
}

.state-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin: 20px 0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.task-item {
  padding: 15px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-primary);
}

.task-item:last-child {
  border-bottom: none;
}

.task-info {
  flex: 1;
}

.task-title {
  font-weight: 600;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.task-meta {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: var(--text-secondary);
}

.task-date i.far.fa-calendar,
.task-meta i.far.fa-calendar {
  margin-right: 8px;
}

.task-date-value {
  display: inline-block;
  margin-right: 4px;
}

/* small color dot used next to titles to visually sync with chart */
.state-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 0 1px rgba(0,0,0,0.06) inset;
}

/* Chart: full-width canvas and legend below it */
.chart-full-width {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
}

/* allow canvas to stretch horizontally; keep a fixed height */
.chart-container-full {
  width: 100%;
  height: 220px;
  position: relative;
}

/* Chart canvas should fill the container */
.chart-container-full canvas {
  width: 100% !important;
  height: 100% !important;
}

/* legend grid below canvas */
.chart-legend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
  width: 100%;
  max-width: 720px;
  justify-items: start;
  align-items: center;
}

.legend-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.legend-line {
  display: flex;
  flex-direction: column;
  line-height: 1;
}

.legend-label {
  font-weight: 600;
  font-size: 14px;
}

.legend-count {
  font-size: 13px;
  color: var(--text-secondary);
}

.priority-high {
  color: var(--danger);
  font-weight: 600;
}

.priority-medium {
  color: var(--warning);
  font-weight: 600;
}

.priority-low {
  color: var(--success);
  font-weight: 600;
}

.member-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.member-tag {
  background: rgba(0, 0, 0, 0.1);
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--text-primary);
}

@media (max-width: 992px) {
  .main-content {
    margin-left: 80px;
  }
}

@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
  .chart-container-full { height: 200px; }
}
</style>
