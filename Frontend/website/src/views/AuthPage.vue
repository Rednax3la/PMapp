<template>
  <div class="auth-container">
    <div class="auth-card">
      <!-- Logo and Title -->
      <div class="auth-header">
        <img src="@/assets/Zain-clear2.png" alt="ZainPM" class="logo" />
        <h1>ZainPM</h1>
        <p>Project Management Made Simple</p>
      </div>

      <!-- Tab Navigation -->
      <div class="auth-tabs">
        <button 
          :class="['tab-button', { active: activeTab === 'login' }]"
          @click="activeTab = 'login'"
        >
          Login
        </button>
        <button 
          :class="['tab-button', { active: activeTab === 'register' }]"
          @click="activeTab = 'register'"
        >
          Register
        </button>
      </div>

      <!-- Login Form -->
      <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="auth-form">
        <h2>Welcome Back</h2>
        <p class="form-subtitle">Sign in to your account</p>

        <div class="form-group">
          <label for="login-username">Username</label>
          <input 
            id="login-username"
            v-model="loginForm.username" 
            type="text" 
            required 
            placeholder="Enter your username"
            :disabled="loading"
          />
        </div>
        
        <div class="form-group">
          <label for="login-password">Password</label>
          <div class="password-input">
            <input 
              id="login-password"
              v-model="loginForm.password" 
              :type="showLoginPassword ? 'text' : 'password'"
              required 
              placeholder="Enter your password"
              :disabled="loading"
            />
            <button 
              type="button" 
              class="password-toggle"
              @click="showLoginPassword = !showLoginPassword"
            >
              <i :class="showLoginPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
        </div>
        
        <button type="submit" class="auth-button" :disabled="loading">
          <i v-if="loading" class="fas fa-spinner fa-spin"></i>
          {{ loading ? 'Signing In...' : 'Sign In' }}
        </button>
      </form>

      <!-- Register Form -->
      <form v-if="activeTab === 'register'" @submit.prevent="handleRegister" class="auth-form">
        <h2>Create Account</h2>
        <p class="form-subtitle">Join ZainPM today</p>

        <div class="form-group">
          <label for="register-company">Company Name</label>
          <input 
            id="register-company"
            v-model="registerForm.company_name" 
            type="text" 
            required 
            placeholder="Enter your company name"
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="register-username">Username</label>
          <input 
            id="register-username"
            v-model="registerForm.username" 
            type="text" 
            required 
            placeholder="Choose a username"
            :disabled="loading"
          />
        </div>
        
        <div class="form-group">
          <label for="register-password">Password</label>
          <div class="password-input">
            <input 
              id="register-password"
              v-model="registerForm.password" 
              :type="showRegisterPassword ? 'text' : 'password'"
              required 
              placeholder="Create a password"
              :disabled="loading"
              minlength="6"
            />
            <button 
              type="button" 
              class="password-toggle"
              @click="showRegisterPassword = !showRegisterPassword"
            >
              <i :class="showRegisterPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
          <small class="form-hint">Password must be at least 6 characters long</small>
        </div>

        <div class="form-group">
          <label for="register-confirm-password">Confirm Password</label>
          <div class="password-input">
            <input 
              id="register-confirm-password"
              v-model="confirmPassword" 
              :type="showConfirmPassword ? 'text' : 'password'"
              required 
              placeholder="Confirm your password"
              :disabled="loading"
            />
            <button 
              type="button" 
              class="password-toggle"
              @click="showConfirmPassword = !showConfirmPassword"
            >
              <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
          <small v-if="confirmPassword && registerForm.password !== confirmPassword" class="error-hint">
            Passwords do not match
          </small>
        </div>

        <div class="form-group">
          <label for="register-role">Role</label>
          <select 
            id="register-role"
            v-model="registerForm.role" 
            required
            :disabled="loading"
          >
            <option value="">Select your role</option>
            <option value="admin">Admin</option>
            <option value="manager">Manager</option>
            <option value="member">Team Member</option>
          </select>
        </div>
        
        <button 
          type="submit" 
          class="auth-button" 
          :disabled="loading || registerForm.password !== confirmPassword"
        >
          <i v-if="loading" class="fas fa-spinner fa-spin"></i>
          {{ loading ? 'Creating Account...' : 'Create Account' }}
        </button>
      </form>
      
      <!-- Error Message -->
      <div v-if="error" class="error-message">
        <i class="fas fa-exclamation-triangle"></i>
        {{ error }}
      </div>

      <!-- Success Message -->
      <div v-if="success" class="success-message">
        <i class="fas fa-check-circle"></i>
        {{ success }}
      </div>
    </div>

    <!-- Footer -->
    <div class="auth-footer">
      <p>&copy; 2025 ZainPM. All rights reserved.</p>
    </div>
  </div>
</template>

<script>
import { authService } from '@/services/auth'

export default {
  name: 'AuthPage',
  data() {
    return {
      activeTab: 'login',
      loading: false,
      error: null,
      success: null,
      showLoginPassword: false,
      showRegisterPassword: false,
      showConfirmPassword: false,
      confirmPassword: '',
      loginForm: {
        username: '',
        password: ''
      },
      registerForm: {
        company_name: '',
        username: '',
        password: '',  
        role: ''
      }
    }
  },
  mounted() {
    // Check if user is already authenticated
    if (authService.isAuthenticated()) {
      this.$router.push('/')
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = null
      this.success = null
      
      try {
        await authService.login(this.loginForm.username, this.loginForm.password)
        
        this.success = 'Login successful! Redirecting to dashboard...'
        
        // Redirect after a short delay to show success message
        setTimeout(() => {
          this.$router.push('/')
        }, 1500)
        
      } catch (error) {
        this.error = error
      } finally {
        this.loading = false
      }
    },

    async handleRegister() {
      this.loading = true
      this.error = null
      this.success = null
      
      // Validate passwords match
      if (this.registerForm.password !== this.confirmPassword) {
        this.error = 'Passwords do not match'
        this.loading = false
        return
      }
      
      try {
        await authService.register(this.registerForm)
        
        this.success = 'Account created successfully! You can now log in.'
        
        // Reset form and switch to login
        this.registerForm = {
          company_name: '',
          username: '',
          password: '',
          role: ''
        }
        this.confirmPassword = ''
        
        // Switch to login tab after successful registration
        setTimeout(() => {
          this.activeTab = 'login'
          this.success = null
        }, 2000)
        
      } catch (error) {
        this.error = error
      } finally {
        this.loading = false
      }
    }
  },
  watch: {
    // Clear messages when switching tabs
    activeTab() {
      this.error = null
      this.success = null
    }
  }
}
</script>

<style scoped>
/* Import ZainPM color variables */
:root {
  --primary: #00fff7;
  --accent: #00e0ff;
  --highlight: #00ffb3;
  --dark-base: #0a0f1c;
  --soft-grid: #1e2f3a;
  --shadow-glow: #006b80;
  --success: #00ffb3;
  --warning: #ffb300;
  --danger: #ff0066;
  --info: #00e0ff;
  --light-gray: #e9ecef;
  --border: #1e2f3a;
  --shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  --sfinal: #03bde2;
}

.auth-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--dark-base) 0%, var(--soft-grid) 50%, var(--shadow-glow) 100%);
  padding: 1rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.auth-card {
  background: var(--soft-grid);
  border: 1px solid var(--shadow-glow);
  border-radius: 16px;
  padding: 2rem;
  width: 100%;
  max-width: 420px;
  box-shadow: 
    0 10px 30px rgba(0, 0, 0, 0.3),
    0 0 20px rgba(0, 255, 247, 0.1);
  animation: slideUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo {
  width: 60px;
  height: 60px;
  margin-bottom: 1rem;
  filter: drop-shadow(0 0 10px var(--primary));
}

.auth-header h1 {
  margin: 0 0 0.5rem 0;
  color: var(--primary);
  font-size: 2.2rem;
  font-weight: 700;
  text-shadow: 0 0 20px var(--primary);
}

.auth-header p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.auth-tabs {
  display: flex;
  margin-bottom: 2rem;
  border-radius: 10px;
  overflow: hidden;
  background: var(--dark-base);
  border: 1px solid var(--shadow-glow);
}

.tab-button {
  flex: 1;
  padding: 0.875rem 1rem;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.tab-button.active {
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: var(--dark-base);
  box-shadow: 0 0 15px rgba(0, 255, 247, 0.4);
}

.tab-button:hover:not(.active) {
  background: rgba(0, 255, 247, 0.1);
  color: var(--primary);
}

.auth-form {
  animation: fadeIn 0.4s ease-in-out;
}

@keyframes fadeIn {
  from { 
    opacity: 0;
    transform: translateY(10px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

.auth-form h2 {
  margin: 0 0 0.5rem 0;
  color: var(--accent);
  font-size: 1.6rem;
  font-weight: 600;
}

.form-subtitle {
  margin: 0 0 1.5rem 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--highlight);
  font-size: 0.9rem;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 2px solid var(--shadow-glow);
  border-radius: 10px;
  font-size: 1rem;
  background: var(--dark-base);
  color: #ffffff;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-sizing: border-box;
}

.form-group input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 15px rgba(0, 255, 247, 0.3);
  transform: translateY(-2px);
}

.form-group input:disabled,
.form-group select:disabled {
  background-color: rgba(30, 47, 58, 0.5);
  cursor: not-allowed;
  opacity: 0.6;
}

.form-group select {
  cursor: pointer;
}

.form-group select option {
  background: var(--dark-base);
  color: #ffffff;
}

.password-input {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--accent);
  cursor: pointer;
  padding: 0.25rem;
  font-size: 1rem;
  transition: color 0.3s ease;
}

.password-toggle:hover {
  color: var(--primary);
}

.form-hint {
  display: block;
  margin-top: 0.4rem;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8rem;
}

.error-hint {
  color: var(--danger);
}

.auth-button {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
  color: var(--dark-base);
  border: none;
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  margin-top: 1rem;
  box-shadow: 0 4px 15px rgba(0, 255, 247, 0.3);
}

.auth-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 255, 247, 0.4);
}

.auth-button:active:not(:disabled) {
  transform: translateY(-1px);
}

.auth-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.error-message,
.success-message {
  margin-top: 1.5rem;
  padding: 1rem;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.9rem;
  font-weight: 500;
  animation: messageSlide 0.4s ease-out;
}

@keyframes messageSlide {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.error-message {
  background: rgba(255, 0, 102, 0.1);
  color: var(--danger);
  border: 1px solid rgba(255, 0, 102, 0.3);
}

.success-message {
  background: rgba(0, 255, 179, 0.1);
  color: var(--success);
  border: 1px solid rgba(0, 255, 179, 0.3);
}

.auth-footer {
  margin-top: 2rem;
  text-align: center;
}

.auth-footer p {
  margin: 0;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8rem;
}

/* Font Awesome icon fixes */
.fas, .far, .fab {
  font-family: "Font Awesome 5 Free" !important;
}

.fas {
  font-weight: 900 !important;
}

.far, .fab {
  font-weight: 400 !important;
}

/* Responsive Design */
@media (max-width: 480px) {
  .auth-container {
    padding: 0.5rem;
  }
  
  .auth-card {
    padding: 1.5rem;
    max-width: 100%;
  }
  
  .auth-header h1 {
    font-size: 1.8rem;
  }
  
  .tab-button {
    padding: 0.75rem 0.5rem;
    font-size: 0.9rem;
  }
  
  .auth-form h2 {
    font-size: 1.4rem;
  }
  
  .form-group input,
  .form-group select {
    padding: 0.75rem;
  }
  
  .auth-button {
    padding: 0.875rem;
    font-size: 1rem;
  }
}

@media (max-width: 320px) {
  .auth-header h1 {
    font-size: 1.6rem;
  }
  
  .tab-button {
    padding: 0.625rem 0.25rem;
    font-size: 0.85rem;
  }
}
</style>