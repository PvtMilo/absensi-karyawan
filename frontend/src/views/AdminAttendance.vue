<template>
  <div style="padding:16px; max-width:1100px; margin:0 auto;">
    <h2>Admin — Attendance</h2>

    <div style="border:1px solid #ddd; border-radius:8px; padding:12px; margin:12px 0;">
      <h3 style="margin:0 0 10px;">Filter</h3>

      <div style="display:grid; gap:10px; grid-template-columns:1fr 1fr 1fr;">
        <div>
          <label style="display:block; font-size:12px; opacity:.8;">User ID (opsional)</label>
          <input v-model="filters.user_id" style="width:100%; padding:10px;" placeholder="1" />
        </div>

        <div>
          <label style="display:block; font-size:12px; opacity:.8;">Date From (YYYY-MM-DD)</label>
          <input v-model="filters.date_from" style="width:100%; padding:10px;" placeholder="2025-12-01" />
        </div>

        <div>
          <label style="display:block; font-size:12px; opacity:.8;">Date To (YYYY-MM-DD)</label>
          <input v-model="filters.date_to" style="width:100%; padding:10px;" placeholder="2025-12-31" />
        </div>
      </div>

      <div style="margin-top:10px; display:flex; gap:10px; flex-wrap:wrap;">
        <button @click="load" :disabled="loading">
          {{ loading ? "Loading..." : "Apply Filter" }}
        </button>
        <button @click="reset" :disabled="loading">Reset</button>
      </div>

      <p v-if="error" style="color:#c00; margin-top:10px;">{{ error }}</p>
    </div>

    <div style="overflow:auto; border:1px solid #ddd; border-radius:8px;">
      <table style="width:100%; border-collapse:collapse; min-width:1050px;">
        <thead>
          <tr style="background:#f6f6f6;">
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">ID</th>
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">User</th>
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">Check-in</th>
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">Check-out</th>
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">Valid</th>
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">Distance</th>
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">Selfie</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="a in rows" :key="a.id">
            <td style="padding:10px; border-bottom:1px solid #eee;">{{ a.id }}</td>
            <td style="padding:10px; border-bottom:1px solid #eee;">{{ a.user_id }}</td>
            <td style="padding:10px; border-bottom:1px solid #eee;">{{ formatDateTime(a.check_in_at) }}</td>
            <td style="padding:10px; border-bottom:1px solid #eee;">{{ a.check_out_at ? formatDateTime(a.check_out_at) : "-" }}</td>
            <td style="padding:10px; border-bottom:1px solid #eee;">
              IN: {{ a.is_valid_location ? "yes" : "no" }} /
              OUT: {{ a.check_out_is_valid_location ? "yes" : "no" }}
            </td>
            <td style="padding:10px; border-bottom:1px solid #eee;">
              IN: {{ toMeter(a.distance_m) }} /
              OUT: {{ toMeter(a.check_out_distance_m) }}
            </td>
            <td style="padding:10px; border-bottom:1px solid #eee;">
              <a v-if="a.selfie_url" :href="backendUrl(a.selfie_url)" target="_blank">In</a>
              <span v-else style="opacity:.6;">-</span>
              <span> | </span>
              <a v-if="a.check_out_selfie_url" :href="backendUrl(a.check_out_selfie_url)" target="_blank">Out</a>
              <span v-else style="opacity:.6;">-</span>
            </td>
          </tr>

          <tr v-if="!loading && rows.length === 0">
            <td colspan="7" style="padding:14px; text-align:center; opacity:.7;">
              Tidak ada data.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script setup>
import { ref } from "vue";
import { adminGetAttendance } from "../services/adminAttendance.service";

const BACKEND = "http://127.0.0.1:8000";

const rows = ref([]);
const loading = ref(false);
const error = ref("");

const filters = ref({
  user_id: "",
  date_from: "",
  date_to: "",
});

function backendUrl(path) {
  return `${BACKEND}${path}`;
}

function formatDateTime(s) {
  if (!s) return "-";
  return s.replace("T", " ").split(".")[0];
}

function toMeter(v) {
  if (v === null || v === undefined) return "-";
  return `${Number(v).toFixed(0)}m`;
}

function reset() {
  filters.value = { user_id: "", date_from: "", date_to: "" };
  load();
}

async function load() {
  error.value = "";
  loading.value = true;
  try {
    const params = {};
    if (filters.value.user_id) params.user_id = Number(filters.value.user_id);
    if (filters.value.date_from) params.date_from = filters.value.date_from;
    if (filters.value.date_to) params.date_to = filters.value.date_to;

    rows.value = await adminGetAttendance(params);
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || "Gagal load attendance";
  } finally {
    loading.value = false;
  }
}

load();
</script>
