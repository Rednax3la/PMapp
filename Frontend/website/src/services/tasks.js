// Frontend/website/src/services/tasks.js
import api from './api'

export const taskService = {
  async createTask(taskData) {
    try {
      console.log('Sending task data to backend:', taskData)
      const response = await api.post('/tasks', taskData)
      console.log('Backend response:', response.data)
      return response.data
    } catch (error) {
      console.error('Task creation error details:', error)
      console.error('Error response:', error.response)
      
      // Extract the actual error message from backend
      let errorMessage = 'Failed to create task'
      
      if (error.response) {
        console.error('Backend error status:', error.response.status)
        console.error('Backend error data:', error.response.data)
        
        // Try different ways to extract the error message
        if (error.response.data?.error) {
          errorMessage = error.response.data.error
        } else if (error.response.data?.message) {
          errorMessage = error.response.data.message
        } else if (typeof error.response.data === 'string') {
          errorMessage = error.response.data
        } else {
          errorMessage = `Server error (${error.response.status}): ${error.response.statusText}`
        }
      } else if (error.request) {
        errorMessage = 'No response from server. Please check your connection.'
      } else {
        errorMessage = error.message || 'Unknown error occurred'
      }
      
      console.error('Final error message:', errorMessage)
      throw new Error(errorMessage)
    }
  },

  async createBatchTasks(tasksData) {
    try {
      console.log('Sending batch task data to backend:', tasksData)
      const response = await api.post('/tasks', tasksData) // Same endpoint, but with array
      console.log('Backend batch response:', response.data)
      return response.data
    } catch (error) {
      console.error('Batch task creation error:', error)
      
      let errorMessage = 'Failed to create batch tasks'
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      }
      
      throw new Error(errorMessage)
    }
  },

  async getTasks(companyName, projectName) {
    try {
      const response = await api.post('/tasks/view', {
        company_name: companyName,
        project_name: projectName
      })
      return response.data
    } catch (error) {
      console.error('Get tasks error:', error)
      let errorMessage = 'Failed to fetch tasks'
      
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      }
      
      throw new Error(errorMessage)
    }
  },

  async updateTask(taskData) {
    try {
      const formData = new FormData()
      
      // Add text fields
      formData.append('company_name', taskData.company_name)
      formData.append('project_name', taskData.project_name)
      formData.append('task_name', taskData.task_name)
      formData.append('status_percentage', taskData.status_percentage.toString())
      formData.append('description', taskData.description || '')
      
      // Add expenditure if provided
      if (taskData.expenditure !== undefined && taskData.expenditure !== null) {
        formData.append('expenditure', taskData.expenditure.toString())
      }
      
      // Add images if provided
      if (taskData.images && taskData.images.length > 0) {
        taskData.images.forEach((image) => {
          formData.append('images', image)
        })
      }
      
      console.log('Sending task update:', taskData)
      const response = await api.post('/tasks/updates', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      return response.data
    } catch (error) {
      console.error('Task update error:', error)
      
      let errorMessage = 'Failed to update task'
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      }
      
      throw new Error(errorMessage)
    }
  },

  async markTaskAs(companyName, projectName, taskName, state) {
    try {
      const response = await api.post('/tasks/mark-as', {
        company_name: companyName,
        project_name: projectName,
        task_name: taskName,
        state: state
      })
      return response.data
    } catch (error) {
      console.error('Mark task error:', error)
      
      let errorMessage = `Failed to mark task as ${state}`
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      }
      
      throw new Error(errorMessage)
    }
  },

  async postponeTask(companyName, projectName, taskName, newStartTime, newDuration = null) {
    try {
      const payload = {
        company_name: companyName,
        project_name: projectName,
        task_name: taskName,
        new_start_time: newStartTime
      }
      
      if (newDuration) {
        payload.new_duration = newDuration
      }
      
      const response = await api.post('/tasks/postpone-to', payload)
      return response.data
    } catch (error) {
      console.error('Postpone task error:', error)
      
      let errorMessage = 'Failed to postpone task'
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      }
      
      throw new Error(errorMessage)
    }
  },

  async getTasksByPriority(companyName, projectName, priority) {
    try {
      const response = await api.post('/tasks/priority', {
        company_name: companyName,
        project_name: projectName,
        priority: priority
      })
      return response.data
    } catch (error) {
      console.error('Get tasks by priority error:', error)
      
      let errorMessage = 'Failed to fetch tasks by priority'
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      }
      
      throw new Error(errorMessage)
    }
  },

  async getMemberTasks(companyName, projectName, member) {
    try {
      const response = await api.post('/tasks/member', {
        company_name: companyName,
        project_name: projectName,
        member: member
      })
      return response.data
    } catch (error) {
      console.error('Get member tasks error:', error)
      
      let errorMessage = 'Failed to fetch member tasks'
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      }
      
      throw new Error(errorMessage)
    }
  },

  async getTaskMembers(companyName, projectName, taskName) {
    try {
      const response = await api.post('/tasks/members', {
        company_name: companyName,
        project_name: projectName,
        task_name: taskName
      })
      return response.data
    } catch (error) {
      console.error('Get task members error:', error)
      
      let errorMessage = 'Failed to fetch task members'
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      }
      
      throw new Error(errorMessage)
    }
  },

  async getTaskImages(companyName, projectName, taskName) {
    try {
      const response = await api.post('/views/images', {
        company_name: companyName,
        project_name: projectName,
        task_name: taskName
      })
      return response.data
    } catch (error) {
      console.error('Get task images error:', error)
      
      let errorMessage = 'Failed to fetch task images'
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      }
      
      throw new Error(errorMessage)
    }
  },

  async getTaskState(companyName, projectName, taskName, time = null) {
    try {
      const payload = {
        company_name: companyName,
        project_name: projectName,
        task_name: taskName,
        type: 'task'
      }
      
      if (time) {
        payload.time = time
      }
      
      const response = await api.post('/states', payload)
      return response.data
    } catch (error) {
      console.error('Get task state error:', error)
      
      let errorMessage = 'Failed to fetch task state'
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      }
      
      throw new Error(errorMessage)
    }
  }
}