// Frontend/website/src/services/visualizations.js
import api from './api'

export const visualizationService = {
  async getTimetable(companyName, projectName) {
    try {
      const response = await api.post('/views/timetable', {
        company_name: companyName,
        project_name: projectName
      })
      return response.data
    } catch (error) {
      throw error.response?.data?.message || 'Failed to generate timetable'
    }
  },

  async getGanttChart(companyName, projectName) {
    try {
      const response = await api.post('/views/gantt', {
        company_name: companyName,
        project_name: projectName
      })
      return response.data
    } catch (error) {
      throw error.response?.data?.message || 'Failed to generate Gantt chart'
    }
  }
}