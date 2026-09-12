import { createRouter, createWebHistory } from 'vue-router'
import AuthForm from '../components/AuthForm.vue'
import Home from '../views/Home.vue'
import Logout from '../views/Logout.vue'

// Thin wrapper views — each just passes a role prop to AuthForm
// This keeps routes separate (patient/login, doctor/login, admin/login)
// while sharing a single component

const routes = [
  // ── Home ──
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: 'MediCare HMS · Home', guest: true }
  },

  // ── Patient routes ──
  {
    path: '/patient/login',
    name: 'PatientLogin',
    component: AuthForm,
    props: { role: 'patient' },
    meta: { title: 'Patient Login · MediCare HMS', guest: true }
  },
  {
    path: '/patient/register',
    name: 'PatientRegister',
    component: AuthForm,
    props: { role: 'patient' },
    meta: { title: 'Patient Register · MediCare HMS', guest: true }
  },

  // ── Doctor routes ──
  {
    path: '/doctor/login',
    name: 'DoctorLogin',
    component: AuthForm,
    props: { role: 'doctor' },
    meta: { title: 'Doctor Login · MediCare HMS', guest: true }
  },

  // ── Admin routes ──
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: AuthForm,
    props: { role: 'admin' },
    meta: { title: 'Admin Login · MediCare HMS', guest: true }
  },

  // ── Dashboards (placeholder — replace with real dashboard components) ──
  {
    path: '/patient/dashboard',
    name: 'PatientDashboard',
    component: () => import('../views/PatientDashboard.vue'),
    meta: { requiresAuth: true, role: 'patient' }
  },
  {
    path: '/doctor/dashboard',
    name: 'DoctorDashboard',
    component: () => import('../views/DoctorDashboard.vue'),
    meta: { requiresAuth: true, role: 'doctor' }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('../views/AdminDashboard.vue'),
    meta: { requiresAuth: true, role: 'admin' }
  },

  // ── Logout (always accessible) ──
  {
    path: '/logout',
    name: 'Logout',
    component: Logout,
    meta: { title: 'Signing out…' }
  },

  // ── Fallback ──
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() { return { top: 0 } }
})

// ── Navigation Guard ──
router.beforeEach((to, from, next) => {
  // Update page title
  document.title = to.meta.title || 'MediCare HMS'

  const token = localStorage.getItem('hms_token')
  const userRole = localStorage.getItem('hms_role')

  // Always allow logout route
  if (to.path === '/logout') return next()

  // Redirect logged-in users away from guest pages
  if (to.meta.guest && token) {
    const dashboardMap = { admin: '/admin/dashboard', doctor: '/doctor/dashboard', patient: '/patient/dashboard' }
    return next(dashboardMap[userRole] || '/patient/login')
  }

  // Redirect unauthenticated users away from protected pages
  if (to.meta.requiresAuth && !token) {
    const loginMap = { admin: '/admin/login', doctor: '/doctor/login', patient: '/patient/login' }
    return next(loginMap[to.meta.role] || '/patient/login')
  }

  // Prevent role mismatch (doctor trying to access admin dashboard etc.)
  if (to.meta.requiresAuth && to.meta.role && userRole !== to.meta.role) {
    const loginMap = { admin: '/admin/login', doctor: '/doctor/login', patient: '/patient/login' }
    localStorage.clear()
    return next(loginMap[to.meta.role] || '/patient/login')
  }

  next()
})

export default router
