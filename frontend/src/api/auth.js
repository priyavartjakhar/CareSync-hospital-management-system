// src/api/auth.js
// Centralised API calls for authentication
// All routes hit Flask backend at /api/auth/...

import { request } from './base.js'

export const authAPI = {
  /**
   * Login for any role
   * @param {string} role - 'admin' | 'doctor' | 'patient'
   * @param {object} payload - { email/username, password }
   */
  login(role, payload) {
    return request(`/api/auth/${role}/login`, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  },

  /**
   * Patient self-registration
   * @param {object} payload - patient registration fields
   */
  register(payload) {
    return request('/api/auth/patient/register', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  },

  /**
   * Check if email / phone already exists in the database (no auth required)
   * @param {{ email?: string, phone?: string }} params
   * @returns {{ email_taken?: boolean, phone_taken?: boolean }}
   */
  check({ email, phone } = {}) {
    const qs = new URLSearchParams()
    if (email) qs.set('email', email)
    if (phone) qs.set('phone', phone)
    return request(`/api/auth/check?${qs.toString()}`)
  },

  /**
   * Logout (clears server-side session if using flask-security)
   */
  logout() {
    const token = localStorage.getItem('hms_token')
    return request('/api/auth/logout', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    }).finally(() => localStorage.clear())
  },

  /**
   * Get current user info from token
   */
  me() {
    const token = localStorage.getItem('hms_token')
    return request('/api/auth/me', {
      headers: { Authorization: `Bearer ${token}` }
    })
  }
}
