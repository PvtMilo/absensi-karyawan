<template>
  <div style="padding:12px; border-bottom:1px solid #ddd; display:flex; gap:12px; align-items:center; flex-wrap:wrap;">
    <strong>Absensi</strong>

    <template v-if="auth.isAuthed.value">
      <a href="#" @click.prevent="go('/attendance')">Attendance</a>
      <a href="#" @click.prevent="go('/attendance/history')">History</a>

      <template v-if="auth.role.value === 'ADMIN'">
        <a href="#" @click.prevent="go('/admin/attendance')">Admin Attendance</a>
        <a href="#" @click.prevent="go('/admin/users')">Admin Users</a>
      </template>

      <span style="margin-left:auto; opacity:.8;">
        {{ auth.user.value?.email }} ({{ auth.role.value }})
      </span>

      <button @click="doLogout">Logout</button>
    </template>

    <template v-else>
      <span style="margin-left:auto;"></span>
      <a href="#" @click.prevent="go('/login')">Login</a>
    </template>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { useAuth } from "../stores/auth";

const router = useRouter();
const auth = useAuth();

function go(path) {
  router.push(path);
}

function doLogout() {
  auth.logout();
  router.push("/login");
}
</script>
