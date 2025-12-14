import { createRouter, createWebHistory } from 'vue-router'
import AdminAttendance from '../views/AdminAttendance.vue'
import Login from '../views/Login.vue'
import StaffAttendance from "../views/StaffAttendance.vue";
import AttendanceHistory from "../views/AttendanceHistory.vue";
import AdminUsers from '../views/AdminUsers.vue';
import { useAuth } from "../stores/auth";

const routes = [
  {
    path: "/attendance",
    component: StaffAttendance,
    meta: { requiresAuth: true, roles: ["STAFF","ADMIN"] }
  },
  {
    path: "/attendance/history",
    component: AttendanceHistory,
    meta: { requiresAuth: true, roles: ["STAFF","ADMIN"] }
  },
  {
    path: "/admin/users",
    component: AdminUsers,
    meta: { requiresAuth: true, roles: ["ADMIN"] }
  },
  {
    path: "/admin/attendance",
    component: AdminAttendance,
    meta: { requiresAuth: true, roles: ["ADMIN"] }
  },
  {
    path: "/login",
    component: Login,
    meta: { requiresAuth: false }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem("token");
  const isAdminRoute = to.path.startsWith("/admin");
  if (isAdminRoute && !token) {
    return "/login";
  }
});

router.beforeEach((to) => {
  const token = localStorage.getItem("token");
  const needLogin = to.path.startsWith("/admin") || to.path.startsWith("/attendance");
  if (needLogin && !token) return "/login";
});

router.beforeEach((to, from, next) => {
  const auth = useAuth();

  const needAuth = to.meta?.requiresAuth;
  const roles = to.meta?.roles;

  if (needAuth && !auth.isAuthed.value) {
    return next("/login");
  }

  if (needAuth && roles && roles.length > 0) {
    const r = auth.role.value;
    if (!roles.includes(r)) {
      // kalau staff maksa buka admin
      return next("/attendance");
    }
  }

  next();
});

export default router