import api from './api'

export const reportsService = {
  async getSummary() {
    const res = await api.get('/reports/summary')
    return res.data
  },

  async getProjectReport(projectName) {
    const res = await api.get(`/reports/project/${encodeURIComponent(projectName)}`)
    return res.data
  },

  async exportCsv(projectName = '') {
    const params = projectName ? { project: projectName } : {}
    const res = await api.get('/reports/export', {
      params,
      responseType: 'blob'
    })
    // Trigger browser download
    const url = window.URL.createObjectURL(new Blob([res.data], { type: 'text/csv' }))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'zainpm_report.csv')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  }
}
