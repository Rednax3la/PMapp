import api from './api'

export const membersService = {
  async getTeamMembers(projectName) {
    const res = await api.get(`/projects/team/${encodeURIComponent(projectName)}`)
    return res.data
  },

  async addMember(projectName, email, role = 'member') {
    const res = await api.post(`/projects/team/${encodeURIComponent(projectName)}/add`, { email, role })
    return res.data
  },

  async removeMember(projectName, email) {
    const res = await api.delete(`/projects/team/${encodeURIComponent(projectName)}/remove/${encodeURIComponent(email)}`)
    return res.data
  }
}
