import { request } from './base.js'

export const adminAPI = {
  summary() {
    return request('/api/admin/summary')
  },
  departments() {
    return request('/api/admin/departments')
  },
  createDepartment(payload) {
    return request('/api/admin/departments', { method: 'POST', body: JSON.stringify(payload) })
  },
  doctors(params = '') {
    return request(`/api/admin/doctors${params}`)
  },
  createDoctor(payload) {
    return request('/api/admin/doctors', { method: 'POST', body: JSON.stringify(payload) })
  },
  updateDoctor(id, payload) {
    return request(`/api/admin/doctors/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
  },
  blacklistDoctor(id) {
    return request(`/api/admin/doctors/${id}`, { method: 'DELETE' })
  },
  patients(params = '') {
    return request(`/api/admin/patients${params}`)
  },
  blacklistPatient(id) {
    return request(`/api/admin/patients/${id}/blacklist`, { method: 'PATCH' })
  },
  appointments(params = '') {
    return request(`/api/admin/appointments${params}`)
  },
  updateAppointment(id, payload) {
    return request(`/api/admin/appointments/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
  }
}
