//Frontend/website/src/views/Help.vue
<template>
  <div class="help-page" :class="{ dark: isDark, light: !isDark }">
    <!-- Sidebar -->
    <Sidebar :active-nav="activeNav" @nav-change="setActiveNav" />
    
    <!-- Main Content -->
    <div class="main-content">
      <AppHeader title="Help & Support">
        <template #actions>
          <ThemeToggle :is-dark="isDark" @toggle="toggleTheme" />
          <AppButton variant="primary" icon="fas fa-headset">
            Contact Support
          </AppButton>
        </template>
      </AppHeader>
      
      <!-- Search Bar -->
      <div class="help-search">
        <div class="search-container">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search help articles, tutorials, and FAQs..."
            class="search-input"
          >
        </div>
      </div>
      
      <!-- Quick Access Cards -->
      <div class="quick-access">
        <div 
          v-for="item in quickAccessItems" 
          :key="item.id"
          class="access-card"
          @click="selectSection(item.section)"
        >
          <div class="card-icon">
            <i :class="item.icon"></i>
          </div>
          <div class="card-content">
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
          </div>
          <i class="fas fa-arrow-right card-arrow"></i>
        </div>
      </div>
      
      <!-- Help Categories -->
      <div class="help-categories">
        <div class="category-nav">
          <button 
            v-for="category in categories" 
            :key="category.id"
            :class="['category-btn', { active: activeCategory === category.id }]"
            @click="activeCategory = category.id"
          >
            <i :class="category.icon"></i>
            {{ category.name }}
          </button>
        </div>
        
        <!-- Getting Started -->
        <div v-if="activeCategory === 'getting-started'" class="help-content">
          <h2>Getting Started</h2>
          <div class="content-grid">
            <div class="help-section">
              <h3>Quick Setup Guide</h3>
              <div class="step-list">
                <div class="step-item" v-for="(step, index) in setupSteps" :key="index">
                  <div class="step-number">{{ index + 1 }}</div>
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
                <div v-for="video in tutorialVideos" :key="video.id" class="video-item">
                  <div class="video-thumbnail">
                    <i class="fas fa-play-circle"></i>
                  </div>
                  <div class="video-info">
                    <h4>{{ video.title }}</h4>
                    <p>{{ video.duration }} • {{ video.views }} views</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Features -->
        <div v-if="activeCategory === 'features'" class="help-content">
          <h2>Features & Functionality</h2>
          <div class="feature-accordion">
            <div 
              v-for="feature in features" 
              :key="feature.id"
              class="accordion-item"
              :class="{ active: expandedFeature === feature.id }"
            >
              <div class="accordion-header" @click="toggleFeature(feature.id)">
                <div class="header-content">
                  <i :class="feature.icon"></i>
                  <span>{{ feature.title }}</span>
                </div>
                <i class="fas fa-chevron-down accordion-arrow"></i>
              </div>
              <div class="accordion-content">
                <p>{{ feature.description }}</p>
                <div class="feature-details">
                  <div v-for="detail in feature.details" :key="detail" class="detail-item">
                    <i class="fas fa-check"></i>
                    {{ detail }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- FAQ -->
        <div v-if="activeCategory === 'faq'" class="help-content">
          <h2>Frequently Asked Questions</h2>
          <div class="faq-section">
            <div 
              v-for="faq in filteredFAQs" 
              :key="faq.id"
              class="faq-item"
              :class="{ active: expandedFAQ === faq.id }"
            >
              <div class="faq-question" @click="toggleFAQ(faq.id)">
                <span>{{ faq.question }}</span>
                <i class="fas fa-chevron-down faq-arrow"></i>
              </div>
              <div class="faq-answer">
                <p>{{ faq.answer }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Troubleshooting -->
        <div v-if="activeCategory === 'troubleshooting'" class="help-content">
          <h2>Troubleshooting</h2>
          <div class="troubleshoot-grid">
            <div class="trouble-category" v-for="category in troubleshootCategories" :key="category.id">
              <div class="category-header">
                <i :class="category.icon"></i>
                <h3>{{ category.title }}</h3>
              </div>
              <div class="issue-list">
                <div v-for="issue in category.issues" :key="issue.id" class="issue-item">
                  <div class="issue-title">{{ issue.problem }}</div>
                  <div class="issue-solution">{{ issue.solution }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Contact -->
        <div v-if="activeCategory === 'contact'" class="help-content">
          <h2>Contact Support</h2>
          <div class="contact-options">
            <div class="contact-card" v-for="option in contactOptions" :key="option.id">
              <div class="contact-icon">
                <i :class="option.icon"></i>
              </div>
              <div class="contact-info">
                <h3>{{ option.title }}</h3>
                <p>{{ option.description }}</p>
                <div class="contact-details">
                  <span class="availability">{{ option.availability }}</span>
                  <span class="response-time">{{ option.responseTime }}</span>
                </div>
              </div>
              <AppButton :variant="option.buttonVariant" @click="initiateContact(option.type)">
                {{ option.buttonText }}
              </AppButton>
            </div>
          </div>
          
          <!-- Contact Form -->
          <div class="contact-form">
            <h3>Send us a message</h3>
            <form @submit.prevent="submitContactForm">
              <div class="form-group">
                <label>Subject</label>
                <select v-model="contactForm.subject" class="form-input">
                  <option value="">Select a topic</option>
                  <option value="technical">Technical Issue</option>
                  <option value="billing">Billing Question</option>
                  <option value="feature">Feature Request</option>
                  <option value="other">Other</option>
                </select>
              </div>
              
              <div class="form-group">
                <label>Priority</label>
                <select v-model="contactForm.priority" class="form-input">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
              
              <div class="form-group">
                <label>Message</label>
                <textarea 
                  v-model="contactForm.message" 
                  class="form-textarea"
                  rows="5"
                  placeholder="Describe your issue or question in detail..."
                ></textarea>
              </div>
              
              <div class="form-group">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="contactForm.attachLogs">
                  <span class="checkmark"></span>
                  Attach system logs (helps with troubleshooting)
                </label>
              </div>
              
              <AppButton type="submit" variant="primary">
                Send Message
              </AppButton>
            </form>
          </div>
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
    const activeNav = ref('help');
    const setActiveNav = (target) => {
      activeNav.value = target;
    };

    // State
    const searchQuery = ref('');
    const activeCategory = ref('getting-started');
    const expandedFeature = ref(null);
    const expandedFAQ = ref(null);

    // Quick Access Items
    const quickAccessItems = ref([
      {
        id: 1,
        title: 'Getting Started',
        description: 'Learn the basics of ZainPM',
        icon: 'fas fa-rocket',
        section: 'getting-started'
      },
      {
        id: 2,
        title: 'Feature Guide',
        description: 'Explore all available features',
        icon: 'fas fa-tools',
        section: 'features'
      },
      {
        id: 3,
        title: 'Common Issues',
        description: 'Quick solutions to common problems',
        icon: 'fas fa-wrench',
        section: 'troubleshooting'
      },
      {
        id: 4,
        title: 'Contact Support',
        description: 'Get help from our team',
        icon: 'fas fa-headset',
        section: 'contact'
      }
    ]);

    // Categories
    const categories = ref([
      { id: 'getting-started', name: 'Getting Started', icon: 'fas fa-play' },
      { id: 'features', name: 'Features', icon: 'fas fa-star' },
      { id: 'faq', name: 'FAQ', icon: 'fas fa-question-circle' },
      { id: 'troubleshooting', name: 'Troubleshooting', icon: 'fas fa-tools' },
      { id: 'contact', name: 'Contact', icon: 'fas fa-envelope' }
    ]);

    // Setup Steps
    const setupSteps = ref([
      {
        title: 'Create Your Account',
        description: 'Sign up for ZainPM and verify your email address to get started.'
      },
      {
        title: 'Set Up Your Profile',
        description: 'Add your personal information and customize your workspace preferences.'
      },
      {
        title: 'Create Your First Project',
        description: 'Start by creating a project and adding team members to collaborate.'
      },
      {
        title: 'Add Tasks and Deadlines',
        description: 'Break down your project into manageable tasks with clear deadlines.'
      },
      {
        title: 'Invite Team Members',
        description: 'Invite colleagues to join your projects and assign them specific roles.'
      }
    ]);

    // Tutorial Videos
    const tutorialVideos = ref([
      {
        id: 1,
        title: 'ZainPM Overview - Getting Started',
        duration: '5:42',
        views: '1.2K'
      },
      {
        id: 2,
        title: 'Creating and Managing Projects',
        duration: '8:15',
        views: '890'
      },
      {
        id: 3,
        title: 'Task Management Best Practices',
        duration: '6:30',
        views: '756'
      },
      {
        id: 4,
        title: 'Using the Gantt Chart View',
        duration: '4:22',
        views: '624'
      }
    ]);

    // Features
    const features = ref([
      {
        id: 1,
        title: 'Project Management',
        icon: 'fas fa-project-diagram',
        description: 'Create, organize, and track projects from start to finish.',
        details: [
          'Create unlimited projects',
          'Set project deadlines and milestones',
          'Track project progress in real-time',
          'Assign team members to projects'
        ]
      },
      {
        id: 2,
        title: 'Task Management',
        icon: 'fas fa-tasks',
        description: 'Break down projects into manageable tasks and track completion.',
        details: [
          'Create and assign tasks',
          'Set priority levels and due dates',
          'Add task descriptions and attachments',
          'Track task completion status'
        ]
      },
      {
        id: 3,
        title: 'Team Collaboration',
        icon: 'fas fa-users',
        description: 'Work together seamlessly with your team members.',
        details: [
          'Invite team members to projects',
          'Real-time collaboration features',
          'Comment and discuss on tasks',
          'Share files and documents'
        ]
      },
      {
        id: 4,
        title: 'Reporting & Analytics',
        icon: 'fas fa-chart-bar',
        description: 'Get insights into project performance and team productivity.',
        details: [
          'Generate detailed project reports',
          'Track team performance metrics',
          'Export data to various formats',
          'Customizable dashboard views'
        ]
      }
    ]);

    // FAQ Data
    const faqData = ref([
      {
        id: 1,
        question: 'How do I create a new project?',
        answer: 'To create a new project, click the "New Project" button in the header or go to the Projects page and click "Add Project". Fill in the project details and click "Create Project".'
      },
      {
        id: 2,
        question: 'Can I invite team members to my projects?',
        answer: 'Yes! You can invite team members by going to the Team Members section and clicking "Add Member". Enter their email address and select their role in the project.'
      },
      {
        id: 3,
        question: 'How do I track project progress?',
        answer: 'Project progress is automatically calculated based on completed tasks. You can view progress on the Dashboard, Projects page, or in detailed project reports.'
      },
      {
        id: 4,
        question: 'Is there a mobile app available?',
        answer: 'Currently, ZainPM is a web-based application optimized for desktop and mobile browsers. A dedicated mobile app is in development and will be available soon.'
      },
      {
        id: 5,
        question: 'How do I export project data?',
        answer: 'You can export project data from the Reports page. Select the project and date range, then click "Export Reports" to download data in various formats.'
      },
      {
        id: 6,
        question: 'What happens if I forget my password?',
        answer: 'Click "Forgot Password" on the login page, enter your email address, and you\'ll receive a password reset link. Follow the instructions in the email to create a new password.'
      }
    ]);

    // Troubleshooting Categories
    const troubleshootCategories = ref([
      {
        id: 1,
        title: 'Login Issues',
        icon: 'fas fa-sign-in-alt',
        issues: [
          {
            id: 1,
            problem: 'Cannot log in to my account',
            solution: 'Check your email and password. If you forgot your password, use the "Forgot Password" link.'
          },
          {
            id: 2,
            problem: 'Account is locked',
            solution: 'Wait 15 minutes after multiple failed attempts, or contact support to unlock your account.'
          }
        ]
      },
      {
        id: 2,
        title: 'Performance Issues',
        icon: 'fas fa-tachometer-alt',
        issues: [
          {
            id: 1,
            problem: 'Application is running slowly',
            solution: 'Clear your browser cache and cookies, or try using a different browser.'
          },
          {
            id: 2,
            problem: 'Pages are not loading',
            solution: 'Check your internet connection and refresh the page. If the problem persists, contact support.'
          }
        ]
      },
      {
        id: 3,
        title: 'Feature Problems',
        icon: 'fas fa-cogs',
        issues: [
          {
            id: 1,
            problem: 'Cannot create new tasks',
            solution: 'Ensure you have the necessary permissions. Contact your project administrator if needed.'
          },
          {
            id: 2,
            problem: 'Notifications not working',
            solution: 'Check your notification settings in the Settings page and ensure browser notifications are enabled.'
          }
        ]
      }
    ]);

    // Contact Options
    const contactOptions = ref([
      {
        id: 1,
        title: 'Live Chat',
        description: 'Get instant help from our support team',
        icon: 'fas fa-comments',
        availability: 'Mon-Fri, 9 AM - 5 PM EST',
        responseTime: 'Avg response: 2 minutes',
        buttonText: 'Start Chat',
        buttonVariant: 'primary',
        type: 'chat'
      },
      {
        id: 2,
        title: 'Email Support',
        description: 'Send us a detailed message about your issue',
        icon: 'fas fa-envelope',
        availability: '24/7',
        responseTime: 'Avg response: 4 hours',
        buttonText: 'Send Email',
        buttonVariant: 'success',
        type: 'email'
      },
      {
        id: 3,
        title: 'Phone Support',
        description: 'Speak directly with a support representative',
        icon: 'fas fa-phone',
        availability: 'Mon-Fri, 9 AM - 5 PM EST',
        responseTime: 'Immediate',
        buttonText: 'Call Now',
        buttonVariant: 'warning',
        type: 'phone'
      }
    ]);

    // Contact Form
    const contactForm = ref({
      subject: '',
      priority: 'medium',
      message: '',
      attachLogs: false
    });

    // Computed Properties
    const filteredFAQs = computed(() => {
      if (!searchQuery.value) return faqData.value;
      
      const query = searchQuery.value.toLowerCase();
      return faqData.value.filter(faq => 
        faq.question.toLowerCase().includes(query) || 
        faq.answer.toLowerCase().includes(query)
      );
    });

    // Methods
    const selectSection = (section) => {
      activeCategory.value = section;
    };

    const toggleFeature = (featureId) => {
      expandedFeature.value = expandedFeature.value === featureId ? null : featureId;
    };

    const toggleFAQ = (faqId) => {
      expandedFAQ.value = expandedFAQ.value === faqId ? null : faqId;
    };

    const initiateContact = (type) => {
      console.log('Initiating contact:', type);
      // Implementation for different contact methods
    };

    const submitContactForm = () => {
      console.log('Submitting contact form:', contactForm.value);
      // Form submission logic
      alert('Message sent successfully! We\'ll get back to you soon.');
      contactForm.value = {
        subject: '',
        priority: 'medium',
        message: '',
        attachLogs: false
      };
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
      searchQuery,
      activeCategory,
      expandedFeature,
      expandedFAQ,
      quickAccessItems,
      categories,
      setupSteps,
      tutorialVideos,
      features,
      faqData,
      troubleshootCategories,
      contactOptions,
      contactForm,
      filteredFAQs,
      selectSection,
      toggleFeature,
      toggleFAQ,
      initiateContact,
      submitContactForm
    };
  }
};
</script>

<style scoped>
@import '@/assets/css/main.css';

.help-page {
  display: flex;
  height: 100vh;
  background-color: var(--bg-base);
  color: var(--text-primary);
  line-height: 1.6;
}

.help-search {
  margin-bottom: 30px;
}

.search-container {
  position: relative;
  max-width: 600px;
  margin: 0 auto;
}

.search-container i {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 18px;
}

.search-input {
  width: 100%;
  padding: 16px 20px 16px 55px;
  border: 2px solid var(--border-color);
  border-radius: 50px;
  background: var(--bg-section);
  color: var(--text-primary);
  font-size: 16px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(0, 255, 247, 0.1);
}

.quick-access {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.access-card {
  background: var(--bg-section);
  border-radius: 12px;
  padding: 25px;
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.access-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  border-color: var(--primary);
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  background: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: var(--dark-base);
}

.card-content {
  flex: 1;
}

.card-content h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.card-content p {
  color: var(--text-secondary);
  font-size: 14px;
}

.card-arrow {
  color: var(--text-secondary);
  font-size: 18px;
}

.help-categories {
  background: var(--bg-section);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.category-nav {
  display: flex;
  background: rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid var(--border-color);
  overflow-x: auto;
}

.category-btn {
  padding: 15px 25px;
  border: none;
  background: transparent;
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  white-space: nowrap;
  font-weight: 500;
}

.category-btn:hover,
.category-btn.active {
  background: var(--primary);
  color: var(--dark-base);
}

.help-content {
  padding: 30px;
}

.help-content h2 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 25px;
  color: var(--primary);
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 30px;
}

.help-section h3 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
}

.step-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.step-item {
  display: flex;
  gap: 15px;
}

.step-number {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--primary);
  color: var(--dark-base);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.step-content h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 5px;
}

.step-content p {
  color: var(--text-secondary);
  font-size: 14px;
}

.video-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.video-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.video-item:hover {
  background: rgba(0, 0, 0, 0.1);
}

.video-thumbnail {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  background: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--dark-base);
  font-size: 20px;
}

.video-info h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 5px;
}

.video-info p {
  color: var(--text-secondary);
  font-size: 14px;
}

.feature-accordion {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.accordion-item {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

.accordion-header {
  padding: 20px;
  background: rgba(0, 0, 0, 0.05);
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.2s ease;
}

.accordion-header:hover {
  background: rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-content i {
  color: var(--primary);
  font-size: 18px;
}

.accordion-arrow {
  transition: transform 0.2s ease;
}

.accordion-item.active .accordion-arrow {
  transform: rotate(180deg);
}

.accordion-content {
  padding: 0 20px;
  max-height: 0;
  overflow: hidden;
  transition: all 0.3s ease;
}

.accordion-item.active .accordion-content {
  padding: 20px;
  max-height: 500px;
}

.feature-details {
  margin-top: 15px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-secondary);
}

.detail-item i {
  color: var(--success);
  font-size: 12px;
}

.faq-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.faq-item {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

.faq-question {
  padding: 20px;
  background: rgba(0, 0, 0, 0.05);
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
  transition: all 0.2s ease;
}

.faq-question:hover {
  background: rgba(0, 0, 0, 0.1);
}

.faq-arrow {
  transition: transform 0.2s ease;
}

.faq-item.active .faq-arrow {
  transform: rotate(180deg);
}

.faq-answer {
  padding: 0 20px;
  max-height: 0;
  overflow: hidden;
  transition: all 0.3s ease;
  color: var(--text-secondary);
}

.faq-item.active .faq-answer {
  padding: 20px;
  max-height: 200px;
}

.troubleshoot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 25px;
}

.trouble-category {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  padding: 20px;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.category-header i {
  color: var(--primary);
  font-size: 20px;
}

.category-header h3 {
  font-size: 18px;
  font-weight: 600;
}

.issue-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.issue-item {
  padding: 15px;
  background: var(--bg-base);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.issue-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.issue-solution {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.contact-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.contact-card {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  padding: 25px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 15px;
}

.contact-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: var(--dark-base);
}

.contact-info h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.contact-info p {
  color: var(--text-secondary);
  margin-bottom: 15px;
}

.contact-details {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.availability,
.response-time {
  font-size: 12px;
  color: var(--text-secondary);
}

.contact-form {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  padding: 30px;
  max-width: 600px;
  margin: 0 auto;
}

.contact-form h3 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 25px;
  text-align: center;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-base);
  color: var(--text-primary);
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  display: none;
}

.checkmark {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color);
  border-radius: 4px;
  position: relative;
  transition: all 0.2s ease;
}

.checkbox-label input[type="checkbox"]:checked + .checkmark {
  background: var(--primary);
  border-color: var(--primary);
}

.checkbox-label input[type="checkbox"]:checked + .checkmark::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: var(--dark-base);
  font-weight: bold;
  font-size: 12px;
}

@media (max-width: 992px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .contact-options {
    grid-template-columns: 1fr;
  }
  
  .troubleshoot-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .quick-access {
    grid-template-columns: 1fr;
  }
  
  .access-card {
    flex-direction: column;
    text-align: center;
  }
  
  .category-nav {
    flex-direction: column;
  }
  
  .help-content {
    padding: 20px;
  }
}
</style>