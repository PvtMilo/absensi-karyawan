import { createRouter, createWebHistory } from 'vue-router'
import AdminAttendance from '../views/AdminAttendance.vue'

const routes = [
  { path: '/admin-attendance', 
    name: 'adminAttendance', 
    component: AdminAttendance },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router