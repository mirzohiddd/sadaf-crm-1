import { download, http, tokenStore } from './client.js'
export { ApiError, onUnauthorized, tokenStore, download } from './client.js'
export const authApi = {
  login: async (login, password) => {
    const data = await http.post('/auth/login', { login, password })
    tokenStore.set(data.access_token)
    return data.user
  },
  me: () => http.get('/auth/me'),
  logout: () => http.post('/auth/logout').catch(() => null),
  updateProfile: (patch) => http.put('/auth/profile', patch),
  changePassword: (current, next) => http.put('/auth/password', { current, next })
}
export const employeesApi = {
  list: () => http.get('/employees'),
  roles: () => http.get('/employees/roles'),
  directory: () => http.get('/employees/directory'),
  create: (payload) => http.post('/employees', payload),
  update: (id, payload) => http.put(`/employees/${id}`, payload),
  remove: (id) => http.del(`/employees/${id}`)
}
export const leadsApi = {
  list: () => http.get('/leads'),
  stages: () => http.get('/leads/stages'),
  newCount: () => http.get('/leads/new-count'),
  create: (payload) => http.post('/leads', payload),
  update: (id, payload) => http.put(`/leads/${id}`, payload),
  moveStage: (id, stage) => http.patch(`/leads/${id}/stage`, { stage }),
  markSeen: (id) => http.patch(`/leads/${id}/seen`),
  remove: (id) => http.del(`/leads/${id}`)
}
export const clientsApi = {
  list: () => http.get('/clients'),
  create: (payload) => http.post('/clients', payload),
  update: (id, payload) => http.put(`/clients/${id}`, payload),
  remove: (id) => http.del(`/clients/${id}`)
}
export const toursApi = {
  list: () => http.get('/tours'),
  create: (payload) => http.post('/tours', payload),
  update: (id, payload) => http.put(`/tours/${id}`, payload),
  remove: (id) => http.del(`/tours/${id}`)
}
export const salesApi = {
  list: () => http.get('/sales'),
  create: (payload) => http.post('/sales', payload),
  update: (id, payload) => http.put(`/sales/${id}`, payload),
  remove: (id) => http.del(`/sales/${id}`)
}
export const tasksApi = {
  list: () => http.get('/tasks'),
  create: (payload) => http.post('/tasks', payload),
  update: (id, payload) => http.put(`/tasks/${id}`, payload),
  toggle: (id) => http.patch(`/tasks/${id}/toggle`),
  remove: (id) => http.del(`/tasks/${id}`)
}
export const notificationsApi = {
  list: () => http.get('/notifications'),
  unreadCount: () => http.get('/notifications/unread-count'),
  markRead: (id) => http.patch(`/notifications/${id}/read`),
  markAllRead: () => http.patch('/notifications/read-all'),
  remove: (id) => http.del(`/notifications/${id}`)
}
export const remindersApi = {
  listForLead: (leadId) => http.get(`/leads/${leadId}/reminders`),
  create: (leadId, payload) => http.post(`/leads/${leadId}/reminders`, payload),
  toggleDone: (id) => http.patch(`/reminders/${id}/done`),
  remove: (id) => http.del(`/reminders/${id}`)
}
export const attendanceApi = {
  today: () => http.get('/attendance/today'),
  history: () => http.get('/attendance'),
  summary: () => http.get('/attendance/summary'),
  checkIn: () => http.post('/attendance/check-in'),
  checkOut: () => http.post('/attendance/check-out')
}
export const dashboardApi = {
  get: (period = 'month') => http.get('/dashboard', { period }),
  myStats: (name) => http.get('/dashboard/me', { name })
}
export const analyticsApi = {
  get: () => http.get('/analytics')
}
export const activityApi = {
  list: (limit = 60) => http.get('/activity', { limit })
}
export const reportsApi = {
  list: () => http.get('/reports'),
  exportExcel: (kind = 'leads') =>
    download('/reports/excel', { kind }, `sadaf-${kind}.xlsx`)
}
export const settingsApi = {
  get: () => http.get('/settings'),
  save: (patch) => http.put('/settings', patch),
  reset: () => http.post('/settings/reset')
}
export const aiApi = {
  status: () => http.get('/ai/status'),
  chat: (message, history = []) => http.post('/ai/chat', { message, history }),
  history: (limit = 30) => http.get('/ai/history', { limit }),
  clear: () => http.del('/ai/history')
}