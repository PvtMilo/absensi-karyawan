<script setup>
import { ref, onMounted } from "vue";
import { adminGetAttendance } from "../services/attendance.service";
import { adminGetUsers } from "../services/users.service";

const BACKEND = "http://127.0.0.1:8000";

const day = ref(new Date().toISOString().slice(0, 10)); // default hari ini
const selectedUserId = ref("");

const users = ref([]);
const attendance = ref([]);

const loading = ref(false);
const error = ref("");

function backendUrl(path) {
  // path dari backend contoh: "/uploads/selfies/xxx.png"
  return `${BACKEND}${path}`;
}

function formatDateTime(s) {
  // string iso -> tampil simpel
  if (!s) return "-";
  return s.replace("T", " ").split(".")[0];
}

function toMeter(v) {
  if (v === null || v === undefined) return "-";
  return `${Number(v).toFixed(0)}m`;
}

function getUserName(userId) {
  const u = users.value.find(x => x.id === userId);
  return u ? u.name : "Unknown";
}

function getUserEmail(userId) {
  const u = users.value.find(x => x.id === userId);
  return u ? u.email : "-";
}

async function loadData() {
  error.value = "";
  loading.value = true;

  try {
    // load users sekali kalau belum ada
    if (users.value.length === 0) {
      users.value = await adminGetUsers();
    }

    const payload = {
      day: day.value || undefined,
      user_id: selectedUserId.value ? Number(selectedUserId.value) : undefined,
      limit: 100,
      offset: 0,
    };

    attendance.value = await adminGetAttendance(payload);
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || "Error";
  } finally {
    loading.value = false;
  }
}

onMounted(loadData);
</script>

<template>
  <div style="padding:16px; max-width:1100px; margin:0 auto;">
    <h2 style="margin-bottom:12px;">Admin — Attendance</h2>

    <!-- Filters -->
    <div style="display:flex; gap:12px; flex-wrap:wrap; align-items:end; margin-bottom:16px;">
      <div>
        <label style="display:block; font-size:12px; opacity:.8;">Tanggal</label>
        <input type="date" v-model="day" />
      </div>

      <div>
        <label style="display:block; font-size:12px; opacity:.8;">User</label>
        <select v-model="selectedUserId">
          <option value="">Semua</option>
          <option v-for="u in users" :key="u.id" :value="String(u.id)">
            {{ u.name }} ({{ u.email }})
          </option>
        </select>
      </div>

      <button @click="loadData" :disabled="loading">
        {{ loading ? "Loading..." : "Load" }}
      </button>
    </div>

    <p v-if="error" style="color:#c00; margin-bottom:12px;">
      {{ error }}
    </p>

    <!-- Table -->
    <div style="overflow:auto; border:1px solid #ddd; border-radius:8px;">
      <table style="width:100%; border-collapse:collapse; min-width:980px;">
        <thead>
          <tr style="background:#f6f6f6;">
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">User</th>
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">Check-in</th>
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">Check-out</th>
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">Status</th>
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">Jarak</th>
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">Selfie</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="a in attendance" :key="a.id">
            <td style="padding:10px; border-bottom:1px solid #eee;">
              <div style="font-weight:600;">{{ getUserName(a.user_id) }}</div>
              <div style="font-size:12px; opacity:.75;">{{ getUserEmail(a.user_id) }}</div>
              <div style="font-size:12px; opacity:.75;">ID: {{ a.user_id }}</div>
            </td>

            <td style="padding:10px; border-bottom:1px solid #eee;">
              <div>{{ formatDateTime(a.check_in_at) }}</div>
              <div style="font-size:12px; opacity:.75;">
                valid: {{ a.is_valid_location ? "yes" : "no" }},
                acc: {{ a.accuracy_m ?? "-" }}m
              </div>
            </td>

            <td style="padding:10px; border-bottom:1px solid #eee;">
              <div>{{ a.check_out_at ? formatDateTime(a.check_out_at) : "-" }}</div>
              <div style="font-size:12px; opacity:.75;">
                valid: {{ a.check_out_is_valid_location ? "yes" : "no" }},
                acc: {{ a.check_out_accuracy_m ?? "-" }}m
              </div>
            </td>

            <td style="padding:10px; border-bottom:1px solid #eee;">
              {{ a.status }}
            </td>

            <td style="padding:10px; border-bottom:1px solid #eee;">
              <div>IN: {{ toMeter(a.distance_m) }}</div>
              <div>OUT: {{ toMeter(a.check_out_distance_m) }}</div>
            </td>

            <td style="padding:10px; border-bottom:1px solid #eee;">
              <div style="display:flex; gap:8px; flex-wrap:wrap;">
                <a v-if="a.selfie_url" :href="backendUrl(a.selfie_url)" target="_blank">Selfie In</a>
                <span v-else style="opacity:.6;">No In</span>

                <a v-if="a.check_out_selfie_url" :href="backendUrl(a.check_out_selfie_url)" target="_blank">Selfie Out</a>
                <span v-else style="opacity:.6;">No Out</span>
              </div>
            </td>
          </tr>

          <tr v-if="!loading && attendance.length === 0">
            <td colspan="6" style="padding:14px; text-align:center; opacity:.7;">
              Tidak ada data.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>
<style>
  th{
    color: black;
  }
</style>

