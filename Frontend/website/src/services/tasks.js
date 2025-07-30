// Frontend/website/src/services/tasks.js
import api from './api'

export const taskService = {
  /**
   * Create a new task update entry (e.g., progress update or status change)
   * @param {string|number} taskId
   * @param {number} statusPercentage
   * @param {string} description
   * @returns {Promise<object>}
   */
  async createTaskUpdate(taskId, statusPercentage, description) {
    const response = await api.post('/tasks/update', {
      task_id: taskId,
      status_percentage: statusPercentage,
      description: description
    })
    return response.data
  },

  /**
   * Mark a task with a new state (e.g., started, complete, postponed)
   * @param {string} companyName
   * @param {string} projectName
   * @param {string} taskName
   * @param {string} state
   * @returns {Promise<object>}
   */
  async markTaskAs(companyName, projectName, taskName, state) {
    const response = await api.post('/tasks/mark', {
      company_name: companyName,
      project_name: projectName,
      task_name: taskName,
      state: state
    })
    return response.data
  },

  /**
   * Fetch all tasks for a company (optionally scoped by project)
   * @param {string} companyName
   * @param {string|null} [projectName]
   * @returns {Promise<object>}
   */
  async getTasks(companyName, projectName = null) {
    const payload = { company_name: companyName }
    if (projectName) payload.project_name = projectName
    const response = await api.post('/tasks/view', payload)
    return response.data
  }
}
