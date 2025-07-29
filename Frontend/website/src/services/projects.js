import api from './api'

export const projectService = {
  async createProject(projectData) {
    try {
      const response = await api.post('/projects', projectData)
      return response.data
    } catch (error) {
      throw error.response?.data?.message || 'Failed to create project'
    }
  },

  async getProjects(companyName) {
    try {
      const response = await api.post('/projects/view', {
        company_name: companyName
      })
      return response.data
    } catch (error) {
      throw error.response?.data?.message || 'Failed to fetch projects'
    }
  },

  async getLatestUpdates(companyName, projectName = null) {
    try {
      const payload = { company_name: companyName }
      if (projectName) payload.project_name = projectName
      
      const response = await api.post('/projects/latest_updates', payload)
      return response.data
    } catch (error) {
      throw error.response?.data?.message || 'Failed to fetch updates'
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
      throw error.response?.data?.message || 'Failed to split project'
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
      throw error.response?.data?.message || 'Failed to merge projects'
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
      throw error.response?.data?.message || 'Failed to clone project'
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
      throw error.response?.data?.message || 'Failed to create team'
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
      throw error.response?.data?.message || 'Failed to add users'
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
      throw error.response?.data?.message || 'Failed to allocate role'
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
      throw error.response?.data?.message || 'Failed to allocate funds'
    }
  }
}