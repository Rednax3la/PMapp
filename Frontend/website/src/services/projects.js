// Frontend/website/src/services/projects.js
import api from './api'

export const projectService = {
  async createProject(projectData) {
    try {
      console.log('Sending project data to backend:', projectData)
      const response = await api.post('/projects', projectData)
      console.log('Backend response:', response.data)
      return response.data
    } catch (error) {
      console.error('Project creation error details:', error)
      console.error('Error response:', error.response)
      
      // Extract the actual error message from backend
      let errorMessage = 'Failed to create project'
      
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

  async getProjects(companyName) {
    try {
      const response = await api.post('/projects/view', {
        company_name: companyName
      })
      return response.data
    } catch (error) {
      console.error('Get projects error:', error)
      let errorMessage = 'Failed to fetch projects'
      
      if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      }
      
      throw new Error(errorMessage)
    }
  },

  async getLatestUpdates(companyName, projectName = null) {
    try {
      const payload = { company_name: companyName }
      if (projectName) payload.project_name = projectName
      
      const response = await api.post('/projects/latest_updates', payload)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to fetch updates')
    }
  },

  async splitProject(companyName, originalProject, splits) {
    try {
      const response = await api.post('/projects/split', {
        company_name: companyName,
        original: originalProject,
        splits: splits
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to split project')
    }
  },

  async mergeProjects(companyName, projectNames, newName = null) {
    try {
      const payload = {
        company_name: companyName,
        project_names: projectNames
      }
      if (newName) payload.new_name = newName
      
      const response = await api.post('/projects/merge', payload)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to merge projects')
    }
  },

  async cloneProject(companyName, originalProject, newName = null) {
    try {
      const payload = {
        company_name: companyName,
        original: originalProject
      }
      if (newName) payload.new_name = newName
      
      const response = await api.post('/projects/clone', payload)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to clone project')
    }
  },

  async createTeam(companyName, projectName, members) {
    try {
      const response = await api.post('/projects/create_team', {
        company_name: companyName,
        proj_name: projectName,
        members: members
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to create team')
    }
  },

  async addUsers(companyName, projectName, users) {
    try {
      const response = await api.post('/projects/add_users', {
        company_name: companyName,
        proj_name: projectName,
        users: users
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to add users')
    }
  },

  async allocateRole(companyName, projectName, taskName, member, duty) {
    try {
      const response = await api.post('/projects/allocate_roles', {
        company_name: companyName,
        proj_name: projectName,
        task_name: taskName,
        member: member,
        duty: duty
      })
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to allocate role')
    }
  },

  async allocateFunds(companyName, projectName, amount, member = null, taskName = null) {
    try {
      const payload = {
        company_name: companyName,
        proj_name: projectName,
        amount: amount
      }
      if (member) payload.member = member
      if (taskName) payload.task_name = taskName
      
      const response = await api.post('/projects/allocate_funds', payload)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to allocate funds')
    }
  }
}