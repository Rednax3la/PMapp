<!-- src/views/Help.vue -->
<template>
  <div class="help-page" :class="{ dark: isDark, light: !isDark }">
    <Sidebar :active-nav="activeNav" @nav-change="setActiveNav" />

    <div class="main-content">
      <AppHeader title="Help & Support">
        <template #actions>
          <ThemeToggle :is-dark="isDark" @toggle="toggleTheme" />
          <AppButton variant="primary" icon="fas fa-headset">
            Contact Support
          </AppButton>
        </template>
      </AppHeader>

      <!-- Search -->
      <div class="help-search">
        <div class="search-container">
          <i class="fas fa-search"></i>
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Search help articles, tutorials, and FAQs..."
            class="search-input"
          />
        </div>
      </div>

      <!-- Quick Access -->
      <div class="quick-access">
        <div
          v-for="item in quickAccessItems"
          :key="item.id"
          class="access-card"
          @click="selectSection(item.section)"
        >
          <div class="card-icon"><i :class="item.icon"></i></div>
          <div class="card-content">
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
          </div>
          <i class="fas fa-arrow-right card-arrow"></i>
        </div>
      </div>

      <!-- Categories -->
      <div class="help-categories">
        <div class="category-nav">
          <button
            v-for="cat in categories"
            :key="cat.id"
            :class="['category-btn', { active: activeCategory === cat.id }]"
            @click="activeCategory = cat.id"
          >
            <i :class="cat.icon"></i>
            {{ cat.name }}
          </button>
        </div>

        <!-- Getting Started -->
        <div v-show="activeCategory==='getting-started'" class="help-content">
          <h2>Getting Started</h2>
          <div class="content-grid">
            <div class="help-section">
              <h3>Quick Setup Guide</h3>
              <div class="step-list">
                <div
                  class="step-item"
                  v-for="(step, i) in setupSteps"
                  :key="i"
                >
                  <div class="step-number">{{ i+1 }}</div>
                  <div class="step-content">
                    <h4>{{ step.title }}</h4>
                    <p>{{ step.description }}</p>
                  </div>
                </div>
              </div>
            </div>
            <div class="help-section">
              <h3>Video Tutorials</h3>
              <div class="video-list">
                <div
                  class="video-item"
                  v-for="vid in tutorialVideos"
                  :key="vid.id"
                >
                  <div class="video-thumbnail"><i class="fas fa-play-circle"></i></div>
                  <div class="video-info">
                    <h4>{{ vid.title }}</h4>
                    <p>{{ vid.duration }} • {{ vid.views }} views</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Features -->
        <div v-show="activeCategory==='features'" class="help-content">
          <h2>Features & Functionality</h2>
          <div class="feature-accordion">
            <div
              v-for="feat in features"
              :key="feat.id"
              class="accordion-item"
              :class="{ active: expandedFeature === feat.id }"
            >
              <div class="accordion-header" @click="toggleFeature(feat.id)">
                <div class="header-content"><i :class="feat.icon"></i> {{ feat.title }}</div>
                <i class="fas fa-chevron-down accordion-arrow"></i>
              </div>
              <div class="accordion-content">
                <p>{{ feat.description }}</p>
                <div class="feature-details">
                  <div v-for="d in feat.details" :key="d" class="detail-item">
                    <i class="fas fa-check"></i> {{ d }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- FAQ -->
        <div v-show="activeCategory==='faq'" class="help-content">
          <h2>Frequently Asked Questions</h2>
          <div class="faq-section">
            <div
              v-for="q in filteredFAQs"
              :key="q.id"
              class="faq-item"
              :class="{ active: expandedFAQ === q.id }"
            >
              <div class="faq-question" @click="toggleFAQ(q.id)">
                <span>{{ q.question }}</span>
                <i class="fas fa-chevron-down faq-arrow"></i>
              </div>
              <div class="faq-answer"><p>{{ q.answer }}</p></div>
            </div>
          </div>
        </div>

        <!-- Troubleshooting -->
        <div v-show="activeCategory==='troubleshooting'" class="help-content">
          <h2>Troubleshooting</h2>
          <div class="troubleshoot-grid">
            <div
              class="trouble-category"
              v-for="cat in troubleshootCategories"
              :key="cat.id"
            >
              <div class="category-header">
                <i :class="cat.icon"></i><h3>{{ cat.title }}</h3>
              </div>
              <div class="issue-list">
                <div v-for="iss in cat.issues" :key="iss.id" class="issue-item">
                  <div class="issue-title">{{ iss.problem }}</div>
                  <div class="issue-solution">{{ iss.solution }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Contact -->
        <div v-show="activeCategory==='contact'" class="help-content">
          <h2>Contact Support</h2>
          <div class="contact-options">
            <div
              class="contact-card"
              v-for="opt in contactOptions"
              :key="opt.id"
            >
              <div class="contact-icon"><i :class="opt.icon"></i></div>
              <div class="contact-info">
                <h3>{{ opt.title }}</h3>
                <p>{{ opt.description }}</p>
                <div class="contact-details">
                  <span class="availability">{{ opt.availability }}</span>
                  <span class="response-time">{{ opt.responseTime }}</span>
                </div>
              </div>
              <AppButton :variant="opt.buttonVariant" @click="initiateContact(opt.type)">
                {{ opt.buttonText }}
              </AppButton>
            </div>
          </div>
          <!-- Optional: inline form -->
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import Sidebar from '@/components/layout/Sidebar.vue';
import AppHeader from '@/components/layout/AppHeader.vue';
import ThemeToggle from '@/components/layout/ThemeToggle.vue';
import AppButton from '@/components/ui/AppButton.vue';

export default {
  name: 'HelpPage',
  components: { Sidebar, AppHeader, ThemeToggle, AppButton },
  setup() {
    const isDark = ref(true);
    const toggleTheme = () => {
      isDark.value = !isDark.value;
      localStorage.setItem('zainpm-theme', isDark.value ? 'dark' : 'light');
    };
    const activeNav = ref('help');
    const setActiveNav = (t) => (activeNav.value = t);

    const searchQuery = ref('');
    const activeCategory = ref('getting-started');
    const expandedFeature = ref(null);
    const expandedFAQ = ref(null);

    const quickAccessItems = [
      { id: 1, title: 'Getting Started', description: 'Learn the basics of ZainPM', icon: 'fas fa-rocket', section: 'getting-started' },
      { id: 2, title: 'Feature Guide',    description: 'Explore all available features', icon: 'fas fa-tools',   section: 'features' },
      { id: 3, title: 'Common Issues',     description: 'Quick solutions to common problems', icon: 'fas fa-wrench', section: 'troubleshooting' },
      { id: 4, title: 'Contact Support',   description: 'Get help from our team', icon: 'fas fa-headset', section: 'contact' }
    ];
    const categories = [
      { id: 'getting-started', name: 'Getting Started', icon: 'fas fa-play' },
      { id: 'features',        name: 'Features',        icon: 'fas fa-star' },
      { id: 'faq',             name: 'FAQ',             icon: 'fas fa-question-circle' },
      { id: 'troubleshooting', name: 'Troubleshooting', icon: 'fas fa-tools' },
      { id: 'contact',         name: 'Contact',         icon: 'fas fa-envelope' }
    ];
    const setupSteps = [
      { title: 'Create Your Account',     description: 'Sign up for ZainPM and verify your email.' },
      { title: 'Set Up Your Profile',     description: 'Add personal info and workspace prefs.' },
      { title: 'Create Your First Project', description: 'Add a project and invite team members.' },
      { title: 'Add Tasks and Deadlines', description: 'Break down work into clear tasks.' },
      { title: 'Invite Team Members',     description: 'Share projects with colleagues.' }
    ];
    const tutorialVideos = [
      { id:1, title:'ZainPM Overview - Getting Started', duration:'5:42', views:'1.2K' },
      { id:2, title:'Creating and Managing Projects',   duration:'8:15', views:'890' },
      { id:3, title:'Task Management Best Practices',   duration:'6:30', views:'756' },
      { id:4, title:'Using the Gantt Chart View',       duration:'4:22', views:'624' }
    ];
    const features = [
      { id:1, title:'Project Management',    icon:'fas fa-project-diagram', description:'Create and track projects end‑to‑end.', details:['Unlimited projects','Deadlines & milestones','Real‑time tracking','Assign team members'] },
      { id:2, title:'Task Management',       icon:'fas fa-tasks',            description:'Organize tasks by priority and due date.', details:['Assignable tasks','Priority levels','Attachments','Status tracking'] },
      { id:3, title:'Team Collaboration',    icon:'fas fa-users',            description:'Collaborate in real time.', details:['Invite members','Task comments','File sharing','Notifications'] },
      { id:4, title:'Reporting & Analytics', icon:'fas fa-chart-bar',        description:'Visualize team performance.', details:['Custom reports','Export data','Dashboard views','Metrics tracking'] }
    ];
    const faqData = [
      { id:1, question:'How do I create a new project?', answer:'Click "New Project" or go to Projects → Add Project, fill details and submit.' },
      { id:2, question:'Can I invite team members?', answer:'Yes—visit Team Members, click "Add Member", enter email & role.' },
      { id:3, question:'How do I track progress?', answer:'Progress auto‑calculates from completed tasks; view in Dashboard or Reports.' },
      { id:4, question:'Is there a mobile app?', answer:'Not yet. ZainPM is mobile‑optimized in your browser; a native app is coming soon.' },
      { id:5, question:'How to export data?', answer:'On Reports, select project & date range, then Export.' },
      { id:6, question:'Forgot password?', answer:'Use "Forgot Password" on login page; follow the emailed reset link.' }
    ];
    const troubleshootCategories = [
      { id:1, title:'Login Issues',       icon:'fas fa-sign-in-alt', issues:[{ id:1, problem:'Cannot log in', solution:'Check credentials or reset password.' },{ id:2, problem:'Account locked', solution:'Wait 15 min or contact support.' }] },
      { id:2, title:'Performance Issues', icon:'fas fa-tachometer-alt', issues:[{ id:1, problem:'Slow app', solution:'Clear cache or switch browser.' },{ id:2, problem:'Pages not loading', solution:'Check connection & refresh.' }] },
      { id:3, title:'Feature Problems',   icon:'fas fa-cogs', issues:[{ id:1, problem:'Cannot create tasks', solution:'Check permissions or ask admin.' },{ id:2, problem:'Notifications broken', solution:'Verify settings & browser permissions.' }] }
    ];
    const contactOptions = [
      { id:1, title:'Live Chat',   description:'Instant support from our team', icon:'fas fa-comments',    availability:'Mon–Fri 9–5 EST', responseTime:'~2 min', buttonText:'Start Chat',   buttonVariant:'primary', type:'chat' },
      { id:2, title:'Email Support', description:'Send us a message anytime', icon:'fas fa-envelope', availability:'24/7',       responseTime:'~4 hrs', buttonText:'Send Email', buttonVariant:'success', type:'email' },
      { id:3, title:'Phone Support', description:'Speak with a rep directly', icon:'fas fa-phone',   availability:'Mon–Fri 9–5 EST', responseTime:'Immediate', buttonText:'Call Now',   buttonVariant:'warning', type:'phone' }
    ];

    const filteredFAQs = computed(() => {
      if (!searchQuery.value) return faqData;
      const q=searchQuery.value.toLowerCase();
      return faqData.filter(f=>f.question.toLowerCase().includes(q) || f.answer.toLowerCase().includes(q));
    });

    const selectSection = (sec) => (activeCategory.value = sec);
    const toggleFeature = (id) => (expandedFeature.value = expandedFeature.value===id?null:id);
    const toggleFAQ     = (id) => (expandedFAQ.value     = expandedFAQ.value===id?null:id);
    const initiateContact = (type) => console.log('Contact via', type);

    onMounted(() => {
      const saved = localStorage.getItem('zainpm-theme');
      if (saved==='light') isDark.value = false;
    });

    return {
      isDark, toggleTheme, activeNav, setActiveNav,
      searchQuery, activeCategory, expandedFeature, expandedFAQ,
      quickAccessItems, categories, setupSteps, tutorialVideos,
      features, faqData, troubleshootCategories, contactOptions,
      filteredFAQs, selectSection, toggleFeature, toggleFAQ, initiateContact
    };
  }
};
</script>

<style scoped>
@import '@/assets/css/main.css';
/* all layout & components come from main.css */
</style>
