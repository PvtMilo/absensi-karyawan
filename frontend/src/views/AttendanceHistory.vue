<template>
  <div style="padding:16px; max-width:1000px; margin:0 auto;">
    <h2>Riwayat Absensi Saya</h2>

    <div style="display:flex; gap:10px; margin:12px 0; flex-wrap:wrap;">
      <button @click="load" :disabled="loading">
        {{ loading ? "Loading..." : "Refresh" }}
      </button>
      <button @click="goAttendance">Ke Halaman Absensi</button>
    </div>

    <p v-if="error" style="color:#c00;">{{ error }}</p>

    <div style="overflow:auto; border:1px solid #ddd; border-radius:8px;">
      <table style="width:100%; border-collapse:collapse; min-width:980px;">
        <thead>
          <tr style="background:#f6f6f6;">
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">ID</th>
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">Check-in</th>
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">Check-out</th>
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">Status</th>
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">Lokasi</th>
            <th style="text-align:left; padding:10px; border-bottom:1px solid #ddd;">Selfie</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="a in rows" :key="a.id">
            <td style="padding:10px; border-bottom:1px solid #eee;">
              {{ a.id }}
            </td>

            <td style="padding:10px; border-bottom:1px solid #eee;">
              <div>{{ formatDateTime(a.check_in_at) }}</div>
              <div style="font-size:12px; opacity:.75;">
                valid: {{ a.is_valid_location ? "yes" : "no" }},
                jarak: {{ toMeter(a.distance_m) }},
                acc: {{ a.accuracy_m ?? "-" }}m
              </div>
            </td>

            <td style="padding:10px; border-bottom:1px solid #eee;">
              <div>{{ a.check_out_at ? formatDateTime(a.check_out_at) : "-" }}</div>
              <div style="font-size:12px; opacity:.75;">
                valid: {{ a.check_out_is_valid_location ? "yes" : "no" }},
                jarak: {{ toMeter(a.check_out_distance_m) }},
                acc: {{ a.check_out_accuracy_m ?? "-" }}m
              </div>
            </td>

            <td style="padding:10px; border-bottom:1px solid #eee;">
              {{ a.status }}
            </td>

            <td style="padding:10px; border-bottom:1px solid #eee;">
              <div style="font-size:12px; opacity:.85;">
                IN: {{ a.lat ?? "-" }}, {{ a.lng ?? "-" }}
              </div>
              <div style="font-size:12px; opacity:.85;">
                OUT: {{ a.check_out_lat ?? "-" }}, {{ a.check_out_lng ?? "-" }}
              </div>
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

          <tr v-if="!loading && rows.length === 0">
            <td colspan="6" style="padding:14px; text-align:center; opacity:.7;">
              Belum ada riwayat.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getMyAttendance } from "../services/attendance.service";

const router = useRouter();
const BACKEND = "http://127.0.0.1:8000";

const rows = ref([]);
const loading = ref(false);
const error = ref("");

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

function goAttendance() {
  router.push("/attendance");
}

async function load() {
  error.value = "";
  loading.value = true;
  try {
    rows.value = await getMyAttendance();
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || "Gagal load data";
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>
