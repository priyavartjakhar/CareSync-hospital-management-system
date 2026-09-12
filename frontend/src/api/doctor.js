import { request } from './base.js'

export const doctorAPI = {
  profile() {
    return request('/api/doctor/profile')
  },
  updateProfile(payload) {
    return request('/api/doctor/profile', { method: 'PUT', body: JSON.stringify(payload) })
  },
  summary() {
    return request('/api/doctor/summary')
  },
  appointments(params = '') {
    return request(`/api/doctor/appointments${params}`)
  },
  updateAppointment(id, payload) {
    return request(`/api/doctor/appointments/${id}`, { method: 'PATCH', body: JSON.stringify(payload) })
  },
  availability() {
    return request('/api/doctor/availability')
  },
  addAvailability(payload) {
    return request('/api/doctor/availability', { method: 'POST', body: JSON.stringify(payload) })
  },
  patients() {
    return request('/api/doctor/patients')
  },
  treatments(params = '') {
    return request(`/api/doctor/treatments${params}`)
  }
}
