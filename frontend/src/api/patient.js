import { request, requestFile } from './base.js'

export const patientAPI = {
  summary() {
    return request('/api/patient/summary')
  },
  profile() {
    return request('/api/patient/profile')
  },
  updateProfile(payload) {
    return request('/api/patient/profile', { method: 'PUT', body: JSON.stringify(payload) })
  },
  departments() {
    return request('/api/patient/departments')
  },
  doctors(params = '') {
    return request(`/api/patient/doctors${params}`)
  },
  availability(doctorId) {
    return request(`/api/patient/availability?doctor_id=${doctorId}`)
  },
  availableSlots(doctorId, date) {
    return request(`/api/patient/available-slots?doctor_id=${doctorId}&date=${date}`)
  },
  bookingDoctorsOnDate(date, specialization = '') {
    const q = new URLSearchParams({ date })
    if (specialization) q.set('specialization', specialization)
    return request(`/api/patient/booking/doctors-on-date?${q}`)
  },
  bookingDoctorsWithDates(specialization = '') {
    const q = specialization ? `?specialization=${encodeURIComponent(specialization)}` : ''
    return request(`/api/patient/booking/doctors-with-dates${q}`)
  },
  appointments() {
    return request('/api/patient/appointments')
  },
  bookAppointment(payload) {
    return request('/api/patient/appointments', { method: 'POST', body: JSON.stringify(payload) })
  },
  updateAppointment(id, payload) {
    return request(`/api/patient/appointments/${id}`, { method: 'PUT', body: JSON.stringify(payload) })
  },
  treatments() {
    return request('/api/patient/treatments')
  },
  prescriptions() {
    return request('/api/patient/prescriptions')
  },
  followUps() {
    return request('/api/patient/follow-ups')
  },
  exportCsv() {
    return requestFile('/api/patient/export')
  }
}
