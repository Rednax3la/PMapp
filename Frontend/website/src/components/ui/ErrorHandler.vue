<!-- src/components/ui/ErrorHandler.vue -->
<template>
  <div v-if="error" class="error-container">
    <div class="error-card">
      <div class="error-icon">
        <i class="fas fa-exclamation-triangle"></i>
      </div>
      
      <div class="error-content">
        <h3>{{ errorTitle }}</h3>
        <p>{{ errorMessage }}</p>
        
        <div v-if="showDetails" class="error-details">
          <h4>Technical Details:</h4>
          <pre>{{ errorDetails }}</pre>
        </div>
      </div>
      
      <div class="error-actions">
        <button @click="toggleDetails" class="details-btn">
          {{ showDetails ? 'Hide' : 'Show' }} Details
        </button>
        <button @click="retry" v-if="canRetry" class="retry-btn">
          <i class="fas fa-redo"></i>
          Retry
        </button>
        <button @click="dismiss" class="dismiss-btn">
          Dismiss
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ErrorHandler',
  props: {
    error: {
      type: [String, Object, Error],
      default: null
    },
    canRetry: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: 'Something went wrong'
    }
  },
  emits: ['retry', 'dismiss'],
  data() {
    return {
      showDetails: false
    }
  },
  computed: {
    errorTitle() {
      if (typeof this.error === 'object' && this.error?.response?.status) {
        const status = this.error.response.status
        switch (status) {
          case 401:
            return 'Authentication Required'
          case 403:
            return 'Access Denied'
          case 404:
            return 'Not Found'
          case 500:
            return 'Server Error'
          default:
            return this.title
        }
      }
      return this.title
    },
    
    errorMessage() {
      if (typeof this.error === 'string') {
        return this.error
      }
      
      if (this.error?.response?.data?.message) {
        return this.error.response.data.message
      }
      
      if (this.error?.message) {
        return this.error.message
      }
      
      return 'An unexpected error occurred. Please try again.'
    },
    
    errorDetails() {
      if (typeof this.error === 'object') {
        return JSON.stringify(this.error, null, 2)
      }
      return this.error
    }
  },
  methods: {
    toggleDetails() {
      this.showDetails = !this.showDetails
    },
    
    retry() {
      this.$emit('retry')
    },
    
    dismiss() {
      this.$emit('dismiss')
    }
  }
}
</script>

<style scoped>
.error-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.error-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.error-icon {
  text-align: center;
  margin-bottom: 1rem;
}

.error-icon i {
  font-size: 3rem;
  color: #dc3545;
}

.error-content h3 {
  margin: 0 0 1rem 0;
  text-align: center;
  color: #333;
  font-size: 1.5rem;
}

.error-content p {
  margin: 0 0 1.5rem 0;
  text-align: center;
  color: #666;
  line-height: 1.5;
}

.error-details {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.error-details h4 {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
  color: #495057;
}

.error-details pre {
  margin: 0;
  font-size: 0.8rem;
  color: #6c757d;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 200px;
  overflow-y: auto;
}

.error-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  flex-wrap: wrap;
}

.error-actions button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.details-btn {
  background: #6c757d;
  color: white;
}

.details-btn:hover {
  background: #5a6268;
}

.retry-btn {
  background: #007bff;
  color: white;
}

.retry-btn:hover {
  background: #0056b3;
}

.dismiss-btn {
  background: #28a745;
  color: white;
}

.dismiss-btn:hover {
  background: #1e7e34;
}

@media (max-width: 480px) {
  .error-card {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  .error-actions {
    flex-direction: column;
  }
  
  .error-actions button {
    width: 100%;
  }
}
</style>