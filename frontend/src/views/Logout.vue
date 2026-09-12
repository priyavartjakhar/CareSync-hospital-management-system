<template>
  <div style="min-height: 60vh; display: grid; place-items: center; padding: 2rem;">
    <div style="text-align: center; max-width: 520px;">
      <h1 style="font-size: 1.25rem; margin: 0 0 0.5rem;">Signing you out…</h1>
      <p style="color: #6b7280; margin: 0;">Please wait.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '../api/auth.js'

const router = useRouter()

onMounted(async () => {
  const role = localStorage.getItem('hms_role')
  const loginMap = { admin: '/admin/login', doctor: '/doctor/login', patient: '/patient/login' }

  try {
    await authAPI.logout()
  } catch {
    localStorage.clear()
  } finally {
    await router.replace(loginMap[role] || '/patient/login')
  }
})
</script>

